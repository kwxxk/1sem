from dataclasses import dataclass, replace
from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[1]


class UserError(Exception):
    """사용자에게 표시할 수 있는, 비밀 정보가 없는 오류."""


@dataclass(frozen=True)
class Settings:
    movies_path: Path
    wiki_bundle_path: Path
    storage_path: Path
    chat_model: str
    embedding_model: str
    base_url: str
    document_mode: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    keyword_limit: int
    candidate_limit: int
    selected_limit: int
    request_interval: float
    request_retries: int
    request_timeout: int
    embedding_batch_size: int
    explore_candidate_limit: int
    search_method: str = "similarity"
    mmr_fetch_k: int = 30
    mmr_lambda: float = 0.5
    pdf_manifest_path: Path = Path("data/pdf_manifest.json")
    gms_request_interval: float = 0.2
    first_question_budget: float = 120.0
    repeat_question_budget: float = 30.0

    def validate(self):
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise UserError("청크 중복 길이는 0 이상이며 청크 크기보다 작아야 합니다.")
        if self.top_k < 2:
            raise UserError("Top-k는 메타데이터와 외부 문서를 포함하도록 2 이상으로 설정하세요.")
        if self.document_mode not in {"auto", "wiki", "bundle"}:
            raise UserError("문서 모드는 auto, wiki, bundle 중 하나여야 합니다.")
        if self.search_method not in {"similarity", "mmr"} or self.mmr_fetch_k < self.top_k:
            raise UserError("검색 방식은 similarity/mmr이며 MMR 후보 수는 Top-k 이상이어야 합니다.")
        if not 0 <= self.mmr_lambda <= 1 or self.gms_request_interval < 0:
            raise UserError("MMR 가중치와 외부 호출 간격을 확인하세요.")
        if min(self.first_question_budget, self.repeat_question_budget) <= 0:
            raise UserError("성능 목표 시간은 0보다 커야 합니다.")
        if min(self.keyword_limit, self.candidate_limit, self.selected_limit,
               self.request_retries, self.request_timeout, self.embedding_batch_size,
               self.explore_candidate_limit) < 1 or self.request_interval < 0.5:
            raise UserError("호출·검색 설정을 확인하세요. 호출 간격은 최소 0.5초입니다.")
        return self

    def search_options(self, size, overlap, top_k):
        return replace(self, chunk_size=size, chunk_overlap=overlap, top_k=top_k).validate()


def load_settings():
    # 환경변수 파일은 현재 터미널 위치가 아닌 프로젝트 위치에서 읽는다.
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)
    os.environ["LANGSMITH_TRACING"] = "false"
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"
    values = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    for field in ("movies_path", "wiki_bundle_path", "storage_path", "pdf_manifest_path"):
        if field not in values:
            continue
        values[field] = (ROOT / values[field]).resolve()
    for field in ("chat_model", "embedding_model"):
        values[field] = os.getenv(field.upper()) or values[field]
    return Settings(**values).validate()
