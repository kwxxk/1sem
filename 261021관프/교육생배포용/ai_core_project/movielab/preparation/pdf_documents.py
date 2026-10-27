"""F2016: 등록된 외부 PDF만 읽고 쪽 경계를 보존해 같은 외부 컬렉션에 넣는다."""
from functools import lru_cache
from pathlib import Path
import hashlib
import json

from ..config import ROOT, UserError


def manifest(settings):
    path = Path(settings.pdf_manifest_path)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        return []
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise UserError("PDF 목록은 배열이어야 합니다.")
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(entries) or len(set(ids)) != len(ids):
        raise UserError("PDF 목록에 중복되거나 올바르지 않은 문서 ID가 있습니다.")
    for entry in entries:
        if not all(entry.get(k) for k in ("id", "path", "title", "url", "source", "license", "license_url", "movie_ids")):
            raise UserError("PDF 목록의 출처·이용 조건·연결 영화 정보가 빠져 있습니다.")
        if not isinstance(entry["movie_ids"], list):
            raise UserError("PDF 연결 영화 ID는 목록으로 지정하세요.")
    return entries


@lru_cache(maxsize=32)
def extract_pages(filename, modified, file_size):
    from pypdf import PdfReader
    if file_size > 10_000_000:
        raise UserError("PDF는 10MB 이하 파일만 사용할 수 있습니다.")
    reader = PdfReader(filename)
    if reader.is_encrypted or len(reader.pages) > 150:
        raise UserError("암호화되지 않은 150쪽 이하 PDF를 등록하세요.")
    return [(i, page.extract_text() or "") for i, page in enumerate(reader.pages, 1)]


def pages_for_item(settings, item_id):
    documents, warnings = [], []
    for entry in manifest(settings):
        if str(item_id) not in [str(mid) for mid in entry["movie_ids"]]:
            continue
        path = (ROOT / entry["path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise UserError("PDF 파일은 프로젝트 내부에 등록해야 합니다.")
        if not path.is_file():
            warnings.append(f"PDF 원문이 없습니다: {entry['title']}. manage.py fetch-pdfs를 실행하세요.")
            continue
        if entry.get("sha256") and hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise UserError("PDF 원문의 체크섬이 등록 정보와 다릅니다. 출처를 다시 확인하세요.")
        stat = path.stat()
        for number, text in extract_pages(str(path), stat.st_mtime_ns, stat.st_size):
            if entry.get("pages") and number not in entry["pages"]:
                continue
            if text.strip():
                documents.append({"page_id": f"pdf:{entry['id']}:p{number}", "file_id": entry["id"],
                    "movie_id": str(item_id), "title": f"{entry['title']} · {number}쪽", "text": text,
                    "url": entry["url"] + f"#page={number}", "source": entry["source"],
                    "source_kind": "pdf", "page": number, "license": entry["license"],
                    "license_url": entry["license_url"], "collected_at": entry.get("retrieved_at", ""),
                    "search_query": "등록된 영화 배경 PDF"})
    return documents, warnings


def index_for_item(settings, item, store, domain, notice=lambda message: None):
    documents, warnings = pages_for_item(settings, domain.item_id(item))
    updated = 0
    for document in documents:
        notice(f"PDF 근거 준비: {document['title']}")
        updated += store.index_document(item, document)
    return {"pages": len(documents), "updated_chunks": updated, "warnings": warnings}


def fetch_registered(settings):
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from urllib.parse import urlsplit
    import time
    session = requests.Session()
    session.headers["User-Agent"] = "MovieLab-EducationalResearch/1.0"
    session.mount("https://", HTTPAdapter(max_retries=Retry(
        total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], respect_retry_after_header=True)))
    outcomes = []
    for entry in manifest(settings):
        path = (ROOT / entry["path"]).resolve()
        if not path.is_relative_to(ROOT.resolve()) or urlsplit(entry["url"]).scheme != "https":
            raise UserError("PDF 등록 경로와 HTTPS 출처를 확인하세요.")
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == entry.get("sha256"):
            outcomes.append({"title":entry["title"], "cached":True})
            continue
        time.sleep(settings.request_interval)
        with session.get(entry["url"], timeout=settings.request_timeout, stream=True) as response:
            response.raise_for_status()
            if urlsplit(response.url).scheme != "https":
                raise UserError("PDF 출처가 안전한 연결을 유지하지 않았습니다.")
            content = bytearray()
            for block in response.iter_content(65536):
                content.extend(block)
                if len(content) > 10_000_000:
                    raise UserError("PDF 원문이 10MB를 초과합니다.")
        if not content.startswith(b"%PDF") or (entry.get("sha256") and
                hashlib.sha256(content).hexdigest() != entry["sha256"]):
            raise UserError("PDF 원문 형식 또는 체크섬이 등록 정보와 다릅니다.")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".download")
        temporary.write_bytes(content)
        temporary.replace(path)
        outcomes.append({"title":entry["title"], "cached":False})
    return outcomes
