"""도메인에 독립적인 retrieve/generate 그래프."""
from typing import TypedDict
from .citations import validate_citations


class RAGState(TypedDict, total=False):
    item_id: str
    question: str
    history: list[dict]
    sources: list[dict]
    answer: str


def build_graph(store, models, top_k, system_prompt, notice=lambda message: None):
    from langgraph.graph import StateGraph, START, END

    def retrieve(state):
        notice("선택한 항목의 메타데이터와 외부 문서에서 근거를 검색합니다.")
        preceding = [m["content"] for m in state.get("history", []) if m["role"] == "user"][-2:]
        query = "\n".join([*preceding, state["question"]])
        return {"sources": store.retrieve(state["item_id"], query, top_k)}

    def generate(state):
        notice("검색된 근거로 답변을 생성합니다.")
        if not state["sources"]:
            return {"answer": "문서에서 확인되지 않습니다."}
        numbered = [{"number": i, "type": s["source_type"], "title": s["title"],
                     "text": s["text"]} for i, s in enumerate(state["sources"], 1)]
        answer = models.text(system_prompt,
            {"question": state["question"], "history": state.get("history", [])[-6:], "sources": numbered})
        return {"answer": validate_citations(answer, state["sources"])}

    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
