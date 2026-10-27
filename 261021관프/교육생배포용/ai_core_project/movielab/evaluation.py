"""F2015: 실제 답변과 사람의 검토를 구분해 저장한다. 빈 결과를 완료로 표시하지 않는다."""
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import threading
import time
import uuid

from .config import ROOT, UserError
from .operations import public_value
from .preparation.documents import write_json

_REVIEW_LOCK = threading.RLock()


def cases():
    return json.loads((ROOT / "data/evaluation_cases.json").read_text(encoding="utf-8"))


def evaluation_path(settings, identity):
    try:
        if str(uuid.UUID(identity)) != identity:
            raise ValueError()
    except (ValueError, AttributeError):
        raise UserError("비교 기록 ID가 올바르지 않습니다.")
    return settings.storage_path / "evaluations" / f"{identity}.json"


def run_evaluation(service, items, notice=lambda message: None, selected=None):
    chosen = selected or cases()
    if len(chosen) < 5:
        raise UserError("RAG 전후 비교에는 대표 질문 5개 이상이 필요합니다.")
    by_id = {service.domain.item_id(item): item for item in items}
    result = {"id": str(uuid.uuid4()), "at": datetime.now(timezone.utc).isoformat(), "status": "running",
              "measurement_mode": getattr(service.models, "measurement_mode", "test"),
              "model": service.settings.chat_model, "method": service.settings.search_method,
              "rows": [], "human_review_complete": False}
    path = evaluation_path(service.settings, result["id"])
    for index, case in enumerate(chosen, 1):
        if case["movie_id"] not in by_id:
            raise UserError("비교 질문에 지정된 영화가 데이터에 없습니다.")
        notice(f"대표 질문 {index}/{len(chosen)}: RAG 미사용 응답")
        started = time.perf_counter()
        baseline = service.models.text(
            "너는 영화와 배경 지식에 답하는 도우미다. 제공된 검색 문서는 없다. "
            "알고 있는 범위에서 한국어로 답하고 불확실하면 모른다고 말하라. 출처를 꾸며내지 마라.",
            {"movie_title": by_id[case["movie_id"]]["title"], "question": case["question"]})
        baseline_seconds = time.perf_counter() - started
        notice(f"대표 질문 {index}/{len(chosen)}: 근거를 붙인 응답")
        rag = service.ask(by_id[case["movie_id"]], case["question"], [], notice)
        result["rows"].append(public_value({**case, "without_rag": baseline, "with_rag": rag["answer"],
            "sources": rag["sources"], "baseline_seconds": round(baseline_seconds, 3), "rag_timings": rag["timings"],
            "automatic_observations": {"without_citation_marker": bool(re.search(r"\[근거\s*\d", baseline)),
                "with_citation_marker": bool(re.search(r"\[근거\s*\d", rag["answer"])),
                "with_unknown_notice": "확인되지" in rag["answer"]},
            "review": {"without_accuracy": None, "with_accuracy": None,
                       "without_unknown_handling": None, "with_unknown_handling": None, "notes": ""}}))
        with _REVIEW_LOCK:
            write_json(path, result)
    result["status"] = "responses_collected"
    with _REVIEW_LOCK:
        write_json(path, result)
    return result


def load_evaluation(settings, identity):
    path = evaluation_path(settings, identity)
    if not path.is_file():
        raise UserError("비교 기록을 찾지 못했습니다.")
    return json.loads(path.read_text(encoding="utf-8"))


def review_evaluation(settings, identity, case_id, review):
    fields = {"without_accuracy", "with_accuracy", "without_unknown_handling", "with_unknown_handling", "notes"}
    if set(review) != fields or any(review[k] not in {"적절", "부적절", "판단보류"} for k in fields - {"notes"}):
        raise UserError("정확성과 확인 불가 응답의 평가를 모두 선택하세요.")
    if not isinstance(review["notes"], str) or not review["notes"].strip() or len(review["notes"]) > 2000:
        raise UserError("원문과 대조한 이유를 1~2000자로 기록하세요.")
    with _REVIEW_LOCK:
        result = load_evaluation(settings, identity)
        found = next((row for row in result["rows"] if row["id"] == case_id), None)
        if found is None:
            raise UserError("비교 질문을 찾지 못했습니다.")
        found["review"] = public_value(review)
        result["human_review_complete"] = (len(result["rows"]) >= 5 and all(
            all(row["review"].get(k) for k in fields) for row in result["rows"]))
        write_json(evaluation_path(settings, identity), result)
    return result


def markdown_report(result):
    def literal(text):
        # 모델 출력이 보고서의 제목·HTML·평가 상태를 위조하지 않도록 원문 텍스트로 둔다.
        longest = max([len(run) for run in re.findall(r"`+", text)] or [0])
        fence = "`" * max(3, longest+1)
        return f"{fence}text\n{text}\n{fence}"
    lines = ["# RAG 사용 전후 비교", f"실행 모드: {result['measurement_mode']} / 모델: {result['model']}",
             f"질문 수: {len(result['rows'])} / 응답 상태: {result['status']} / 사람 검토 완료: {result['human_review_complete']}",
             "자동 인용 표식은 사실 정확성을 증명하지 않습니다."]
    for row in result["rows"]:
        lines += [f"\n## {row['id']}", row["question"], "\n### RAG 미사용", literal(row["without_rag"]),
                  "\n### RAG 사용", literal(row["with_rag"]), "\n### 검토 기준", row["expected"],
                  "\n### 원문 근거"]
        lines += [f"- {source['title']}: {source.get('url','')} ({source.get('source_kind','metadata')})"
                  for source in row["sources"]]
        lines += ["\n### 평가", json.dumps(row["review"], ensure_ascii=False),
                  f"시간: 미사용 {row['baseline_seconds']}초 / RAG {row['rag_timings']['total']}초"]
    return "\n\n".join(lines)


def benchmark(service, items, notice=lambda message: None):
    by_id = {service.domain.item_id(item): item for item in items}
    results = []
    for case in cases():
        item = by_id[case["movie_id"]]
        notice(f"성능 측정: {case['id']} 첫 요청")
        first = service.ask(item, case["question"], [], notice)
        notice(f"성능 측정: {case['id']} 반복 요청")
        second = service.ask(item, case["question"], [], notice)
        results.append({"case_id": case["id"], "first": first["metrics"], "repeat": second["metrics"]})
    payload = {"measurement_mode": getattr(service.models, "measurement_mode", "test"), "rows": results,
               "note": "첫 요청이 이미 캐시된 경우 cold start 측정이 아닙니다. collection_cached를 확인하세요."}
    write_json(service.settings.storage_path / "benchmark.json", payload)
    return payload
