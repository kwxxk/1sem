from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import hashlib
import html
import json
import os
import re
import time
import threading
from functools import lru_cache

from ..config import UserError
from .movies import is_item_document, normalize
from .prompts import keyword_prompt, selection_prompt

_WIKI_GATE = threading.Lock()
_WIKI_LAST_CALL = 0.0


@lru_cache(maxsize=256)
def bundle_documents(path, movie_id):
    return tuple(read_json(p, {}) for p in sorted(Path(path).glob(f"{movie_id}_*.json")))


def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


class WikiAPI:
    def __init__(self, settings):
        import requests
        self.session = requests.Session()
        self.settings = settings
        contact = os.getenv("WIKI_CONTACT", "").strip()
        if not contact or not contact.isascii():
            raise UserError("위키백과 API를 사용하려면 .env에 영문 WIKI_CONTACT를 설정하세요.")
        self.session.headers["User-Agent"] = f"MovieLab/1.0 ({contact}) python-requests"
        self.last_call = 0.0

    def request(self, params):
        global _WIKI_LAST_CALL
        with _WIKI_GATE:
            self.last_call = max(self.last_call, _WIKI_LAST_CALL)
            try:
                return self._request(params)
            finally:
                _WIKI_LAST_CALL = self.last_call

    def _request(self, params):
        import requests
        for attempt in range(self.settings.request_retries):
            time.sleep(max(0, self.settings.request_interval - (time.monotonic() - self.last_call)))
            self.last_call = time.monotonic()
            try:
                response = self.session.get("https://ko.wikipedia.org/w/api.php", params={
                    **params, "format": "json", "formatversion": 2, "maxlag": 5},
                    timeout=self.settings.request_timeout)
                if response.status_code == 429 or response.status_code >= 500:
                    retry = response.headers.get("Retry-After", str(2 ** attempt))
                    try:
                        wait = float(retry)
                    except ValueError:
                        try:
                            date = parsedate_to_datetime(retry)
                            date = date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date
                            wait = (date - datetime.now(timezone.utc)).total_seconds()
                        except (ValueError, TypeError, OverflowError):
                            wait = 2 ** attempt
                    time.sleep(max(0, wait))
                    continue
                response.raise_for_status()
                value = response.json()
                if "error" in value:
                    if value["error"].get("code") in {"maxlag", "ratelimited"}:
                        time.sleep(2 ** attempt)
                        continue
                    raise UserError("위키백과에서 요청을 처리하지 못했습니다.")
                return value
            except (requests.RequestException, ValueError):
                if attempt + 1 < self.settings.request_retries:
                    time.sleep(2 ** attempt)
        raise UserError("위키백과 호출에 실패했습니다. 제공 문서 모드로 전환할 수 있습니다.")

    def search(self, query, movie):
        value = self.request({"action": "query", "list": "search", "srsearch": query,
                              "srlimit": self.settings.candidate_limit})
        return [{"page_id": str(p["pageid"]), "title": p["title"],
                 "snippet": html.unescape(re.sub(r"<[^>]+>", "", p.get("snippet", ""))),
                 "mode": "wiki"} for p in value.get("query", {}).get("search", [])]

    def fetch(self, candidate, query, movie):
        value = self.request({"action": "query", "prop": "extracts|info",
                              "pageids": candidate["page_id"], "explaintext": 1, "inprop": "url"})
        pages = value.get("query", {}).get("pages", [])
        if not pages or "missing" in pages[0]:
            raise UserError("선택한 위키 문서가 없어졌습니다. 다시 수집하세요.")
        p = pages[0]
        return {"page_id": str(p["pageid"]), "title": p["title"], "url": p["fullurl"],
                "text": p.get("extract", ""), "movie_id": str(movie["movie_id"]),
                "source": "한국어 위키백과", "search_query": query,
                "collected_at": datetime.now(timezone.utc).isoformat()}


class Bundle:
    def __init__(self, settings):
        self.path = settings.wiki_bundle_path
        self.limit = settings.candidate_limit

    def documents(self, movie):
        return bundle_documents(str(self.path), str(movie["movie_id"]))

    def search(self, query, movie):
        # 배포 묶음 내 제목/수집 검색어/짧은 요약을 대상으로 후보를 만든다.
        docs = self.documents(movie)
        terms = normalize(query).split()
        def score(doc):
            haystack = normalize(doc["title"] + " " + doc.get("search_query", "") + " " + doc["text"][:600])
            return sum(term in haystack for term in terms)
        ranked = sorted(docs, key=score, reverse=True)
        return [{"page_id": str(d["page_id"]), "title": d["title"], "snippet": d["text"][:500],
                 "mode": "bundle"} for d in ranked if score(d) > 0][:self.limit]

    def own_document(self, movie):
        matches = [d for d in self.documents(movie) if is_item_document(d["title"], movie)]
        return max(matches, key=lambda d: (str(movie.get("year")) in d["title"], len(d["text"])), default=None)

    def fetch(self, candidate, query, movie):
        for doc in self.documents(movie):
            if str(doc["page_id"]) == str(candidate["page_id"]):
                return {**doc, "page_id": str(doc["page_id"]), "search_query": query}
        raise UserError("제공 문서가 없습니다. wiki 모드 또는 데이터 경로를 확인하세요.")


class Collector:
    def __init__(self, settings, models, store):
        self.settings, self.models, self.store = settings, models, store
        self.root = settings.storage_path / "collection"
        self.bundle = Bundle(settings)
        self.api = None

    def raw_path(self, mid, pid):
        safe = hashlib.sha256(f"{mid}:{pid}".encode()).hexdigest()
        return self.root / "documents" / f"{safe}.json"

    def provider(self, notice):
        if self.settings.document_mode == "bundle":
            return self.bundle
        try:
            self.api = self.api or WikiAPI(self.settings)
            return self.api
        except UserError:
            if self.settings.document_mode == "wiki":
                raise
            notice("위키백과 설정이 없어 제공된 문서 묶음으로 수집합니다.")
            return self.bundle

    def collect(self, movie, question, history, notice=lambda message: None):
        # Store와 같은 잠금으로 수집 캐시의 read-modify-write와 색인 완료를 보호한다.
        with self.store.lock:
            return self._collect(movie, question, history, notice)

    def _collect(self, movie, question, history, notice):
        mid = str(movie["movie_id"])
        cache_path = self.root / f"{mid}.json"
        cache = read_json(cache_path, {"questions": {}, "queries": {}})
        # 이전 질문에서 수집한 문서도 현재 청크 설정에 맞춰 유지한다.
        for pid in {pid for entry in cache["queries"].values() for pid in entry["page_ids"]}:
            doc = read_json(self.raw_path(mid, pid), None)
            if doc is not None:
                self.store.index_document(movie, doc)
        question_key = hashlib.sha256(normalize(question).encode()).hexdigest()
        keyword_hit = question_key in cache["questions"]
        if keyword_hit:
            keywords = cache["questions"][question_key]
        else:
            keywords = self.models.json(
                keyword_prompt(self.settings.keyword_limit),
                {"movie": movie, "question": question, "history": history[-6:]}, list)
            if not all(isinstance(k, str) and 0 < len(k.strip()) <= 120 for k in keywords):
                raise UserError("검색어 형식이 올바르지 않습니다. 질문을 다시 입력하세요.")
            keywords = keywords[:self.settings.keyword_limit]
            cache["questions"][question_key] = keywords
        # 항목 자체 검색은 모든 질문에서 최우선이며, 새 검색어만 수집한다.
        own_query = f"{movie['title']} {movie.get('year', '')} 영화"
        keywords = list(dict.fromkeys([own_query, *keywords]))
        provider = None
        report = {"keywords": keywords, "queries": [], "warnings": [], "keyword_cache": keyword_hit}
        for query in keywords:
            query_key = normalize(query)
            prior = cache["queries"].get(query_key)
            if prior:
                for pid in prior["page_ids"]:
                    doc = read_json(self.raw_path(mid, pid), None)
                    if doc is None:
                        raise UserError("수집 캐시의 원문이 없습니다. 수집 캐시를 확인하세요.")
                    self.store.index_document(movie, doc)  # 설정 변경 시 원문에서 재청킹
                report["queries"].append({**prior, "query": query, "cached": True})
                notice(f"기존 수집 결과 재사용: {query}")
                continue
            provider = provider or self.provider(lambda msg: report["warnings"].append(msg))
            notice(f"문서 검색·선별: {query}")
            try:
                candidates = provider.search(query, movie)
            except UserError:
                if self.settings.document_mode != "auto":
                    raise
                provider = self.bundle
                report["warnings"].append("위키백과 호출 제한으로 제공 문서 묶음을 사용했습니다.")
                candidates = provider.search(query, movie)
            # 검색 결과에 항목 문서가 없더라도 제공 묶음에서 반드시 확보한다.
            own = self.bundle.own_document(movie) if query == own_query else None
            if own and not any(str(c["page_id"]) == str(own["page_id"]) for c in candidates):
                candidates.insert(0, {"page_id": str(own["page_id"]), "title": own["title"],
                                      "snippet": own["text"][:500], "mode": "bundle"})
            mandatory = {str(c["page_id"]) for c in candidates
                         if is_item_document(c["title"], movie)} if query == own_query else set()
            if query == own_query and not mandatory:
                raise UserError("선택한 영화 자체의 문서를 찾지 못했습니다. 위키 모드·검색 결과를 확인하세요.")
            selected = self.models.json(
                selection_prompt(self.settings.selected_limit),
                {"movie": movie["title"], "question": question, "query": query, "candidates": candidates}, list) if candidates else []
            selected_ids = {str(pid) for pid in selected} | mandatory
            accepted, rejected, page_ids = [], [], []
            for candidate in candidates:
                pid = str(candidate["page_id"])
                if pid not in selected_ids:
                    rejected.append(candidate["title"])
                    continue
                path = self.raw_path(mid, pid)
                doc = read_json(path, None)
                if doc is None:
                    source = self.bundle if candidate["mode"] == "bundle" else provider
                    try:
                        doc = source.fetch(candidate, query, movie)
                    except UserError:
                        if self.settings.document_mode != "auto":
                            raise
                        doc = self.bundle.fetch(candidate, query, movie)
                    write_json(path, doc)
                self.store.index_document(movie, doc)
                page_ids.append(pid)
                accepted.append(candidate["title"])
            entry = {"page_ids": page_ids, "accepted": accepted, "rejected": rejected,
                     "mandatory": [c["title"] for c in candidates if str(c["page_id"]) in mandatory],
                     "mode": "bundle" if isinstance(provider, Bundle) else "wiki"}
            # 수집 및 색인이 모두 끝난 검색어만 완료로 기록한다.
            cache["queries"][query_key] = entry
            write_json(cache_path, cache)
            report["queries"].append({**entry, "query": query, "cached": False})
        write_json(cache_path, cache)
        return report
