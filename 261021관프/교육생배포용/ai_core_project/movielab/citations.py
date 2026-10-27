"""도메인에 독립적인 인용 번호 검사."""
import re

def cited_sources(answer, sources):
    ids = {int(n) for group in re.findall(r"\[근거\s*([\d,\s]+)\]", answer)
           for n in group.split(",") if n.strip().isdigit()}
    return [(i, source) for i, source in enumerate(sources, 1) if i in ids]


def validate_citations(answer, sources):
    used = {int(n) for group in re.findall(r"\[근거\s*([\d,\s]+)\]", answer)
            for n in group.split(",") if n.strip().isdigit()}
    if any(n < 1 or n > len(sources) for n in used):
        return "문서에서 확인되지 않습니다. 유효한 근거 번호를 확인하지 못했습니다."
    # 인용 없는 생성 결과를 사실처럼 내보내지 않는다.
    if not used and "확인되지" not in answer:
        return "문서에서 확인되지 않습니다. 답변을 뒷받침하는 인용 근거가 없습니다."
    return answer
