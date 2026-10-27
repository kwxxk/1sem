"""호출 간격, 안전한 사용자 오류, 제한된 임베딩 캐시, 성능 기록."""
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import threading
import time

_GATE = threading.Lock()
_LAST_REQUEST = 0.0
_METRICS_LOCK = threading.Lock()
_PROMPTS = OrderedDict()
_PROMPTS_LOCK = threading.Lock()


def register_prompt(prompt):
    if len(prompt) < 80:
        return
    with _PROMPTS_LOCK:
        _PROMPTS[prompt] = True
        _PROMPTS.move_to_end(prompt)
        while len(_PROMPTS) > 64:
            _PROMPTS.popitem(last=False)


def call_with_interval(call, interval):
    global _LAST_REQUEST
    with _GATE:
        time.sleep(max(0, interval - (time.monotonic() - _LAST_REQUEST)))
        _LAST_REQUEST = time.monotonic()
        return call()


def redact(value):
    text = str(value)
    with _PROMPTS_LOCK:
        for prompt in _PROMPTS:
            text = text.replace(prompt, "[내부 지침 비공개]")
    for field in ("GMS_KEY", "OPENAI_API_KEY"):
        secret = os.getenv(field, "")
        if secret and len(secret) >= 6:
            text = text.replace(secret, "[비공개]")
    return re.sub(r"\bsk-[A-Za-z0-9_-]{16,}", "[비공개]", text)


def public_error(exc):
    from .config import UserError
    if isinstance(exc, UserError):
        return redact(exc)
    return "처리하지 못했습니다. 키 권한, 모델 설정, 데이터와 네트워크를 확인한 뒤 다시 시도하세요."


def public_value(value):
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return {str(key): public_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [public_value(item) for item in value]
    return value


class CachedEmbeddings:
    def __init__(self, model, interval=0.2, limit=256):
        self.model, self.interval, self.limit = model, interval, limit
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def embed_documents(self, texts):
        return call_with_interval(lambda: self.model.embed_documents(texts), self.interval)

    def embed_query(self, text):
        key = hashlib.sha256(text.encode()).hexdigest()
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
        vector = call_with_interval(lambda: self.model.embed_query(text), self.interval)
        with self.lock:
            self.cache[key] = vector
            while len(self.cache) > self.limit:
                self.cache.popitem(last=False)
        return vector


def record_metrics(settings, item_id, question, timings, collection, model):
    cached = bool(collection.get("queries")) and all(q.get("cached") for q in collection["queries"])
    budget = settings.repeat_question_budget if cached else settings.first_question_budget
    row = {"at": datetime.now(timezone.utc).isoformat(), "item_id": str(item_id),
           "question_hash": hashlib.sha256(question.encode()).hexdigest(),
           "timings": timings, "collection_cached": cached, "budget_seconds": budget,
           "within_budget": timings["total"] <= budget,
           "measurement_mode": getattr(model, "measurement_mode", "test"),
           "method": settings.search_method}
    path = settings.storage_path / "metrics.jsonl"
    with _METRICS_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
