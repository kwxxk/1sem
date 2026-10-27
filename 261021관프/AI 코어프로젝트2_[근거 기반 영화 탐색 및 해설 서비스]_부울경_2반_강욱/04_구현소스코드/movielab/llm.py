import json
import os

from .config import UserError
from .operations import CachedEmbeddings, call_with_interval, register_prompt


class Models:
    measurement_mode = "live"
    def __init__(self, settings):
        key = os.getenv("GMS_KEY", "").strip()
        if not key:
            raise UserError("GMS_KEY가 없습니다. 프로젝트의 .env 파일에 키를 설정하세요.")
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        self.interval = settings.gms_request_interval
        self.chat = ChatOpenAI(model=settings.chat_model, api_key=key,
                               base_url=settings.base_url, timeout=60, max_retries=2)
        self.embeddings = CachedEmbeddings(OpenAIEmbeddings(
            model=settings.embedding_model, api_key=key, base_url=settings.base_url,
            request_timeout=60, max_retries=2, check_embedding_ctx_length=False,
            chunk_size=settings.embedding_batch_size), settings.gms_request_interval)

    def text(self, system, payload):
        register_prompt(system)
        result = call_with_interval(lambda: self.chat.invoke([
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ]), self.interval).content
        if not isinstance(result, str):
            raise UserError("모델 응답 형식을 읽지 못했습니다. 모델 설정을 확인하세요.")
        return result

    def json(self, system, payload, expected_type):
        for attempt in range(2):
            answer = self.text(system + "\nJSON만 출력하세요. 코드 블록이나 설명은 쓰지 마세요."
                               + ("\n이전 출력이 유효하지 않았습니다. 형식을 엄격하게 지키세요." if attempt else ""), payload)
            try:
                value = json.loads(answer)
                if isinstance(value, expected_type):
                    return value
            except (ValueError, TypeError):
                pass
        raise UserError("모델의 구조화 응답을 읽지 못했습니다. 다시 시도하세요.")
