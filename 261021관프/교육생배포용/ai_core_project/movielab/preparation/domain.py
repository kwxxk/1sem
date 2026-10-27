"""영화 전용 필드·컬렉션·프롬프트를 공통 모듈에 전달하는 데이터 어댑터."""
from .movies import movie_text
from .movie_filters import matches, validate_filters
from . import prompts


class MovieDomain:
    metadata_collection = "movie_meta"
    external_collection = "movie_wiki"
    item_id_field = "movie_id"
    document_id_field = "page_id"

    @staticmethod
    def item_id(item):
        return str(item["movie_id"])

    @staticmethod
    def item_record(item):
        return {"id": str(item["movie_id"]), "text": movie_text(item), "metadata": {
            "movie_id": str(item["movie_id"]), "title": item["title"],
            "url": item.get("tmdb_url", ""), "source_type": "항목 메타데이터",
            "source_kind": "metadata", "source": "TMDB 제공 데이터"}}

    @staticmethod
    def document_metadata(item, document):
        return {"movie_id": str(item["movie_id"]), "page_id": str(document["page_id"]),
                "title": document["title"], "url": document["url"],
                "source": document.get("source", "한국어 위키백과"), "source_type": "외부 문서",
                "source_kind": document.get("source_kind", "wiki"),
                "page": int(document.get("page", 0)), "file_id": document.get("file_id", ""),
                "license": document.get("license", "CC BY-SA 4.0"),
                "license_url": document.get("license_url", "https://creativecommons.org/licenses/by-sa/4.0/"),
                "related_movie": item["title"], "search_query": document.get("search_query", ""),
                "collected_at": document.get("collected_at", "")}

    @staticmethod
    def answer_prompt(task="question"):
        return prompts.ANSWER_PROMPT + (prompts.GUIDE_INSTRUCTIONS if task == "guide" else "")

    @staticmethod
    def guide_question():
        return prompts.GUIDE_QUESTION

    @staticmethod
    def create_collector(settings, models, store):
        from .documents import Collector
        return Collector(settings, models, store)

    @staticmethod
    def filter_prompt():
        return prompts.FILTER_PROMPT

    @staticmethod
    def filter_payload(query, items):
        return {"query": query, "available_genres": sorted({g for item in items for g in item.get("genres", [])})}

    validate_filters = staticmethod(validate_filters)
    matches = staticmethod(matches)

    @staticmethod
    def verification_prompt():
        return prompts.VERIFY_PROMPT

    @staticmethod
    def decision_item_id(decision):
        return str(decision.get("movie_id", ""))
