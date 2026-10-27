"""네트워크/실제 GMS 키 없이 실제 Chroma·LangGraph·Streamlit을 검증한다."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import hashlib
import json
import math
import os
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from movielab.config import Settings, UserError
from movielab.preparation.movies import movie_text, is_item_document
from movielab.citations import cited_sources, validate_citations
from movielab.preparation.domain import MovieDomain
from movielab.preparation.documents import Bundle, Collector, write_json
from movielab.explore import explore
from movielab.preparation.movie_filters import FILTER_FIELDS, matches, validate_filters
from movielab.pipeline import build_graph
from movielab.store import Store


class LocalEmbeddings:
    """테스트 전용 결정적 벡터. 제품 임베딩으로는 사용하지 않는다."""
    def embed_documents(self, texts):
        result = []
        for text in texts:
            raw = hashlib.sha256(text.encode()).digest()
            vector = [v / 255 for v in raw[:16]]
            norm = math.sqrt(sum(v * v for v in vector))
            result.append([v / norm for v in vector])
        return result

    def embed_query(self, text):
        return self.embed_documents([text])[0]


class LocalModels:
    def __init__(self):
        self.embeddings = LocalEmbeddings()
        self.calls = 0

    def json(self, system, payload, expected_type):
        self.calls += 1
        if "available_genres" in payload:
            return {**{k: None for k in ("min_year", "max_year", "min_runtime", "max_runtime", "min_rating", "max_rating")},
                    "language": "ko", "genres": ["스릴러"], "directors": [], "cast": [], "countries": [],
                    "semantic": "", "unsupported": ""}
        if expected_type is list and "filters" in payload:
            return [{"movie_id": c["id"], "reason": "한국어 스릴러"} for c in payload["candidates"]]
        return []  # 선별 LLM이 전부 버려도 항목 문서는 반드시 색인해야 함

    def text(self, system, payload):
        return "영화 소개입니다. [근거 1]"


class ProjectTests(unittest.TestCase):
    def setUp(self):
        test_root = Path(__file__).resolve().parents[1] / ".test-work"
        test_root.mkdir(exist_ok=True)
        self.temp = TemporaryDirectory(dir=test_root)
        self.root = Path(self.temp.name)
        raw = json.loads((Path(__file__).resolve().parents[1] / "config.json").read_text(encoding="utf-8"))
        raw.update(movies_path=self.root / "movies.json", wiki_bundle_path=self.root / "wiki",
                   storage_path=self.root / "storage", document_mode="bundle")
        self.settings = Settings(**raw).validate()
        self.models = LocalModels()
        self.domain = MovieDomain()
        self.store = Store(self.settings, self.models.embeddings, self.domain)
        self.movies = [
            {"movie_id": "1", "title": "테스트 영화", "original_title": "Test Movie", "year": 2020,
             "genres": ["스릴러"], "director": ["감독 A"], "cast": ["배우 A"], "runtime": 110,
             "original_language": "ko", "production_countries": ["South Korea"], "vote_average": 8.0,
             "overview": "가족의 비밀을 찾는 이야기", "tmdb_url": "https://www.themoviedb.org/movie/1"},
            {"movie_id": "2", "title": "다른 영화", "year": 2000, "genres": ["SF"], "director": [], "cast": [],
             "runtime": 150, "original_language": "en", "vote_average": 7.0, "overview": "우주 이야기"}]
        write_json(self.settings.movies_path, self.movies)
        self.doc = {"page_id": "10", "title": "테스트 영화", "url": "https://ko.wikipedia.org/wiki/Test",
                    "text": "영화의 배경은 우주이다. " * 180, "movie_id": "1", "source": "한국어 위키백과"}
        write_json(self.settings.wiki_bundle_path / "1_테스트.json", self.doc)
        write_json(self.settings.wiki_bundle_path / "1_우주.json", {**self.doc, "page_id": "11", "title": "우주"})

    def tearDown(self):
        # Chroma의 Windows SQLite 핸들이 프로세스 수명 동안 열려 있을 수 있다.
        import chromadb
        self.store.client._system.stop()
        chromadb.api.client.SharedSystemClient.clear_system_cache()
        assert self.root.resolve().is_relative_to(Path(__file__).resolve().parents[1] / ".test-work")
        self.temp.cleanup()

    def test_metadata_idempotent(self):
        first = self.store.index_items(self.movies)
        second = self.store.index_items(self.movies)
        self.assertEqual(first["indexed"], 2)
        self.assertEqual(second["indexed"], 2)
        self.assertEqual(second["updated"], 0)
        self.assertIn("감독 A", movie_text(self.movies[0]))

    def test_shared_page_does_not_overwrite_other_movie(self):
        self.store.index_document(self.movies[0], self.doc)
        self.store.index_document(self.movies[1], self.doc)
        ids = self.store.external.get(include=[])["ids"]
        self.assertTrue(any(x.startswith("1:10:") for x in ids))
        self.assertTrue(any(x.startswith("2:10:") for x in ids))

    def test_rechunk_removes_old_trailing_chunks(self):
        small = Store(replace(self.settings, chunk_size=120, chunk_overlap=20), self.models.embeddings, self.domain)
        small.index_document(self.movies[0], self.doc)
        old_count = small.external.count()
        self.store.index_document(self.movies[0], self.doc)
        self.assertLess(self.store.external.count(), old_count)
        count = self.store.external.count()
        self.assertEqual(self.store.index_document(self.movies[0], self.doc), 0)
        self.assertEqual(self.store.external.count(), count)

    def test_retrieve_always_meta_and_movie_filter(self):
        self.store.index_items(self.movies)
        for movie in self.movies:
            self.store.index_document(movie, self.doc)
        sources = self.store.retrieve("1", "우주", 3)
        self.assertEqual(sources[0]["source_type"], "항목 메타데이터")
        self.assertTrue(all(s["movie_id"] == "1" for s in sources))
        self.assertLessEqual(len(sources), 3)
        self.assertGreater(len(self.store.retrieve("1", "우주", 4)), len(self.store.retrieve("1", "우주", 2)))

    def test_collection_mandatory_and_cache(self):
        collector = Collector(self.settings, self.models, self.store)
        with patch.object(collector.bundle, "search", wraps=collector.bundle.search) as search:
            first = collector.collect(self.movies[0], "내용 알려줘", [])
            initial_count = self.store.external.count()
            second = collector.collect(self.movies[0], "내용 알려줘", [{"role": "user", "content": "다른 기록"}])
            self.assertEqual(search.call_count, 1)
        self.assertIn("테스트 영화", first["queries"][0]["accepted"])
        self.assertTrue(second["queries"][0]["cached"])
        self.assertEqual(self.store.external.count(), initial_count)

    def test_pipeline_real_graph_and_citations(self):
        self.store.index_items(self.movies)
        graph = build_graph(self.store, self.models, 3, self.domain.answer_prompt())
        self.assertEqual(set(graph.get_graph().nodes) - {"__start__", "__end__"}, {"retrieve", "generate"})
        result = graph.invoke({"item_id": "1", "question": "소개", "history": []})
        self.assertEqual(len(cited_sources(result["answer"], result["sources"])), 1)

    def test_invalid_and_absent_citations_fail_closed(self):
        self.assertIn("확인되지", validate_citations("주장 [근거 99]", [{}]))
        self.assertIn("확인되지", validate_citations("근거 없는 주장", [{}]))
        self.assertEqual(cited_sources("주장 [근거 1, 3]", [{}, {}, {}]), [(1, {}), (3, {})])

    def test_item_document_identity(self):
        movie = self.movies[0]
        self.assertTrue(is_item_document("테스트 영화 (2020년 영화)", movie))
        self.assertFalse(is_item_document("테스트 영화 (1990년 영화)", movie))
        self.assertFalse(is_item_document("테스트 영화 (드라마)", movie))
        self.assertTrue(is_item_document("테 스트 영화 (2020년 영화)", movie))
        self.assertTrue(is_item_document("육사오(6/45)", {"movie_id": "821153", "title": "육사오（6/45）", "year": 2022}))

    def test_explore_strict_filters_and_selection(self):
        self.store.index_items(self.movies)
        result = explore("한국 스릴러", self.movies, self.models, self.store, self.settings, self.domain)
        self.assertEqual([r["item"]["movie_id"] for r in result["results"]], ["1"])
        filters = result["filters"]
        filters["max_runtime"] = 100
        self.assertFalse(matches(self.movies[0], filters))
        filters["min_runtime"] = 120
        with self.assertRaises(UserError):
            validate_filters(filters)

    def test_ui_without_key_and_movie_history(self):
        from streamlit.testing.v1 import AppTest
        with patch.dict(os.environ, {"GMS_KEY": ""}), patch("movielab.config.load_settings", return_value=self.settings):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("GMS" in info.value for info in app.info))
            self.assertTrue(app.chat_input[0].disabled)
            app.session_state["movie_histories"]["1"] = [{"role": "user", "content": "첫 영화의 대화"}]
            app.selectbox[0].set_value("2").run()
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(app.session_state["movie_histories"]["2"], [])
            self.assertEqual(app.session_state["movie_histories"]["1"][0]["content"], "첫 영화의 대화")

    def test_ui_without_index(self):
        from streamlit.testing.v1 import AppTest
        from types import SimpleNamespace
        fake = SimpleNamespace(store=self.store, models=self.models)
        with patch.dict(os.environ, {"GMS_KEY": "TEST-ONLY-NOT-A-REAL-KEY"}), \
             patch("movielab.config.load_settings", return_value=self.settings), \
             patch("movielab.service.Service", return_value=fake):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("색인이 없습니다" in warning.value for warning in app.warning))
            self.assertTrue(app.chat_input[0].disabled)

    def test_ui_full_question_guide_and_explore_without_network(self):
        from streamlit.testing.v1 import AppTest
        from types import SimpleNamespace
        from movielab.service import Service
        self.store.index_items(self.movies)
        collector = Collector(self.settings, self.models, self.store)
        fake = object.__new__(Service)
        fake.settings, fake.store, fake.models = self.settings, self.store, self.models
        fake.collector, fake.domain = collector, self.domain
        with patch.dict(os.environ, {"GMS_KEY": "TEST-ONLY-NOT-A-REAL-KEY"}), \
             patch("movielab.config.load_settings", return_value=self.settings), \
             patch("movielab.service.Service", return_value=fake):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            app.chat_input[0].set_value("영화 소개해줘").run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertTrue(any("근거 1" in m.value for m in app.markdown))
            self.assertEqual(len(app.session_state["movie_histories"]["1"]), 2)
            next(b for b in app.button if b.label == "근거 기반 관람 가이드 만들기").click().run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.session_state["movie_histories"]["1"]), 4)
            app.text_input[0].set_value("한국 스릴러")
            next(b for b in app.button if b.label == "조건 검색").click().run(timeout=20)
            self.assertEqual(len(app.exception), 0)
            self.assertEqual(len(app.session_state["exploration"]["results"]), 1)

    def test_store_and_graph_accept_non_movie_domain(self):
        class BookDomain:
            metadata_collection = "book_meta"
            external_collection = "book_external"
            item_id_field = "book_id"
            document_id_field = "doc_id"

            @staticmethod
            def item_id(item):
                return item["book_id"]

            @staticmethod
            def item_record(item):
                return {"id": item["book_id"], "text": item["title"], "metadata": {
                    "book_id": item["book_id"], "title": item["title"],
                    "source_type": "항목 메타데이터", "url": "https://example.org/book"}}

            @staticmethod
            def document_metadata(item, doc):
                return {"book_id": item["book_id"], "doc_id": doc["doc_id"],
                        "title": doc["title"], "url": doc["url"], "source_type": "외부 문서"}

        book_store = Store(self.settings, self.models.embeddings, BookDomain())
        book = {"book_id": "book1", "title": "테스트 도서"}
        book_store.index_items([book])
        book_store.index_document(book, {"doc_id": "doc1", "title": "도서 설명",
            "url": "https://example.org/doc", "text": "테스트 도서의 배경 설명"})
        graph = build_graph(book_store, self.models, 3, "도서의 근거만 사용해 답하라.")
        result = graph.invoke({"item_id": "book1", "question": "도서 소개", "history": []})
        self.assertEqual(len(result["sources"]), 2)
        self.assertTrue(all(s["book_id"] == "book1" for s in result["sources"]))
        self.assertFalse(any("movie_id" in s for s in result["sources"]))

    def test_service_guide_uses_domain_question_and_prompt(self):
        from movielab.service import Service
        self.store.index_items(self.movies)
        local = object.__new__(Service)
        local.settings, local.store, local.domain = self.settings, self.store, self.domain
        local.models = self.models
        local.collector = self.domain.create_collector(self.settings, self.models, self.store)
        with patch.object(self.models, "text", wraps=self.models.text) as generation:
            result = local.guide(self.movies[0], [])
        self.assertEqual(result["question"], self.domain.guide_question())
        self.assertEqual(generation.call_args.args[0], self.domain.answer_prompt("guide"))
        self.assertNotEqual(self.domain.answer_prompt("guide"), self.domain.answer_prompt("question"))
        self.assertTrue(cited_sources(result["answer"], result["sources"]))


if __name__ == "__main__":
    unittest.main()
