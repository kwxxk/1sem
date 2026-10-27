"""조건 탐색 흐름. 도메인별 필드·조건 규칙은 데이터 준비 영역에서 주입한다."""
from .config import UserError


def explore(query, items, models, store, settings, domain):
    filters = models.json(domain.filter_prompt(), domain.filter_payload(query, items), dict)
    domain.validate_filters(filters)
    if filters["unsupported"]:
        return {"filters": filters, "results": [], "notice": "확인할 수 없는 조건이 있습니다: " + filters["unsupported"]}
    eligible = {domain.item_id(item): item for item in items if domain.matches(item, filters)}
    if not eligible:
        return {"filters": filters, "results": [], "notice": "명시한 조건에 맞는 항목이 없습니다."}
    candidates = store.explore_candidates(query, list(eligible), settings.explore_candidate_limit)
    decisions = models.json(domain.verification_prompt(),
        {"query": query, "filters": filters, "candidates": candidates}, list) if candidates else []
    allowed = {c["id"] for c in candidates}
    results, seen = [], set()
    for decision in decisions:
        if not isinstance(decision, dict) or not isinstance(decision.get("reason"), str):
            raise UserError("탐색 결과를 읽지 못했습니다. 다시 검색하세요.")
        item_id = domain.decision_item_id(decision)
        if item_id in allowed and item_id not in seen and domain.matches(eligible[item_id], filters):
            seen.add(item_id)
            results.append({"item": eligible[item_id], "reason": decision["reason"]})
    return {"filters": filters, "results": results[:10],
            "notice": "전체 목록 중 조건을 먼저 검증한 뒤 의미 검색 상위 후보를 선별합니다. 모든 일치 항목을 나열하는 결과는 아닙니다."}
