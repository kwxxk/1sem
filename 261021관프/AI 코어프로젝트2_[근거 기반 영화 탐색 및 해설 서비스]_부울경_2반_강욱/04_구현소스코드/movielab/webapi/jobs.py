from concurrent.futures import ThreadPoolExecutor
from collections import OrderedDict
import secrets
import threading
import time
import uuid

from ..config import UserError
from ..operations import public_error, public_value, redact


class Sessions:
    def __init__(self):
        self.data = OrderedDict()
        self.lock = threading.RLock()

    def ensure(self, token):
        now = time.monotonic()
        with self.lock:
            expired = [key for key, value in self.data.items() if now-value["seen"] > 3600]
            for key in expired:
                self.data.pop(key, None)
            if token not in self.data:
                token = secrets.token_urlsafe(32)
                self.data[token] = {"seen": now, "histories": {}, "evaluations": set(), "lock": threading.RLock()}
            self.data[token]["seen"] = now
            self.data.move_to_end(token)
            while len(self.data) > 128:
                self.data.popitem(last=False)
            return token, self.data[token]


class Jobs:
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="movielab")
        self.data = OrderedDict()
        self.lock = threading.RLock()

    def submit(self, owner, action):
        with self.lock:
            if sum(row["state"] in {"queued", "running"} for row in self.data.values()) >= 8:
                raise UserError("대기 중인 작업이 많습니다. 진행 중인 작업이 끝난 뒤 다시 시도하세요.")
            while len(self.data) >= 128:
                done = next((key for key,row in self.data.items() if row["state"] in {"completed", "failed"}), None)
                if done is None:
                    raise UserError("작업 공간이 가득 찼습니다.")
                self.data.pop(done)
            identity = str(uuid.uuid4())
            self.data[identity] = {"id": identity, "owner": owner, "state": "queued", "progress": [], "result": None}
        def notice(message):
            with self.lock:
                row = self.data[identity]
                row["progress"] = [*row["progress"], redact(message)][-30:]
        def run():
            with self.lock:
                self.data[identity]["state"] = "running"
            try:
                result = action(notice)
                with self.lock:
                    self.data[identity].update(state="completed", result=public_value(result))
            except Exception as exc:
                with self.lock:
                    self.data[identity].update(state="failed", error=public_error(exc))
        self.pool.submit(run)
        return {"job_id": identity}

    def get(self, owner, identity):
        with self.lock:
            row = self.data.get(identity)
            if row is None or row["owner"] != owner:
                raise UserError("작업을 찾지 못했습니다.")
            return {key: value for key,value in row.items() if key != "owner"}
