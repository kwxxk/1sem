"""서비스 기능 영역. UI는 요청과 표시만 담당한다."""
from .llm import Models
from .store import Store
from .pipeline import build_graph
from .explore import explore
from .operations import record_metrics, public_value
import time


class Service:
    def __init__(self, settings, domain=None):
        if domain is None:
            # 기본 도메인 선택은 이 연결 지점 한 곳에서 수행한다.
            from .preparation.domain import MovieDomain
            domain = MovieDomain()
        self.settings, self.domain = settings, domain
        self.models = Models(settings)
        self.store = Store(settings, self.models.embeddings, domain)
        self.collector = domain.create_collector(settings, self.models, self.store)

    def index_items(self, items, notice=lambda message: None):
        return self.store.index_items(items, notice)

    def ask(self, item, question, history, notice=lambda message: None, *, task="question"):
        started = time.perf_counter()
        report = self.collector.collect(item, question, history, notice)
        from .preparation.pdf_documents import index_for_item
        pdf = index_for_item(self.settings, item, self.store, self.domain, notice)
        report["pdf"] = pdf
        report["warnings"].extend(pdf["warnings"])
        prepared = time.perf_counter()
        result = build_graph(self.store, self.models, self.settings.top_k,
                             self.domain.answer_prompt(task), notice).invoke({
            "item_id": self.domain.item_id(item), "question": question, "history": history})
        finished = time.perf_counter()
        timings = {"preparation": round(prepared-started, 4),
                   "rag": round(finished-prepared, 4), "total": round(finished-started, 4)}
        metrics = record_metrics(self.settings, self.domain.item_id(item), question, timings, report, self.models)
        return public_value({**result, "collection": report, "timings": timings, "metrics": metrics})

    def guide(self, item, history, notice=lambda message: None):
        return self.ask(item, self.domain.guide_question(), history, notice, task="guide")

    def find_items(self, query, items):
        return explore(query, items, self.models, self.store, self.settings, self.domain)

    def compare_search(self, item, question, notice=lambda message: None):
        self.collector.collect(item, question, [], notice)
        from .preparation.pdf_documents import index_for_item
        index_for_item(self.settings, item, self.store, self.domain, notice)
        results = {method: self.store.retrieve(self.domain.item_id(item), question, self.settings.top_k, method)
                   for method in ("similarity", "mmr")}
        a, b = ({s["id"] for s in results[method]} for method in ("similarity", "mmr"))
        return {**results, "same_ids": a == b, "shared_ids": sorted(a & b),
                "fetch_k": self.settings.mmr_fetch_k, "lambda": self.settings.mmr_lambda,
                "note": "후보가 적거나 비슷하면 두 결과가 같을 수 있습니다. 차이를 임의로 만들지 않습니다."}
