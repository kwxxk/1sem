from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path
import os
import threading
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from ..config import ROOT, UserError, load_settings
from ..operations import public_error, public_value
from ..preparation.movies import read_movies
from ..preparation.pdf_documents import manifest, index_for_item
from ..service import Service
from ..evaluation import cases, run_evaluation, benchmark, load_evaluation, review_evaluation, markdown_report
from .schemas import OptionsRequest, QuestionRequest, ExploreRequest, ReviewRequest
from .jobs import Sessions, Jobs


def create_app(settings=None, service_factory=Service):
    settings = settings or load_settings()
    items = read_movies(settings.movies_path)
    by_id = {str(item["movie_id"]): item for item in items}
    sessions, jobs = Sessions(), Jobs()
    services, service_lock = {}, threading.RLock()

    @asynccontextmanager
    async def lifespan(app):
        yield
        jobs.pool.shutdown(wait=True, cancel_futures=True)

    app = FastAPI(title="Movie Lab API", version="2.0", debug=False, lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "testserver"])

    @app.middleware("http")
    async def security_and_session(request, call_next):
        if request.method in {"POST", "DELETE", "PUT", "PATCH"}:
            origin = request.headers.get("origin")
            if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
                return JSONResponse({"error": "다른 출처의 요청은 허용하지 않습니다."}, status_code=403)
            if request.headers.get("content-length", "").isdigit() and int(request.headers["content-length"]) > 100_000:
                return JSONResponse({"error": "요청이 너무 큽니다."}, status_code=413)
        token, session = sessions.ensure(request.cookies.get("ml_session"))
        request.state.owner, request.state.session = token, session
        response = await call_next(request)
        response.set_cookie("ml_session", token, httponly=True, samesite="strict", max_age=3600,
                            secure=request.url.scheme == "https")
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        return response

    @app.exception_handler(UserError)
    async def known_error(request, exc):
        return JSONResponse({"error": public_error(exc)}, status_code=400)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse({"error": "입력 길이·영화 ID·검색 설정을 확인하세요."}, status_code=422)

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        return JSONResponse({"error": public_error(exc)}, status_code=500)

    def service(options=None):
        if not os.getenv("GMS_KEY", "").strip():
            raise UserError("GMS_KEY가 없습니다. 프로젝트의 .env에 키를 넣고 서버를 재시작하세요.")
        chosen = (replace(settings, **options.model_dump()) if options else settings).validate()
        with service_lock:
            if chosen not in services:
                if len(services) >= 8:
                    services.pop(next(iter(services)))
                services[chosen] = service_factory(chosen)
            return services[chosen]

    def item_for(identity):
        if identity not in by_id:
            raise UserError("목록에 없는 영화입니다.")
        return by_id[identity]

    def ready(options):
        instance = service(options)
        if instance.store.meta.count() == 0:
            raise UserError("색인이 없습니다. 메타데이터 색인을 먼저 실행하세요.")
        return instance

    def authorized_evaluation(request, identity):
        if identity not in request.state.session["evaluations"]:
            raise UserError("이 세션의 비교 기록을 찾지 못했습니다.")
        return load_evaluation(settings, identity)

    @app.get("/api/status")
    def status():
        key_ready = bool(os.getenv("GMS_KEY", "").strip())
        counts, issue, execution_mode = {"metadata": 0, "external": 0}, None, "not_configured"
        if key_ready:
            try:
                instance = service()
                counts = {"metadata": instance.store.meta.count(), "external": instance.store.external.count()}
                execution_mode = getattr(instance.models, "measurement_mode", "test")
            except Exception as exc:
                issue = public_error(exc)
        return {"key_configured": key_ready, "execution_mode": execution_mode,
                "counts": counts, "issue": issue, "loaded_items": len(items),
                "settings": {key: getattr(settings, key) for key in
                             ("chunk_size", "chunk_overlap", "top_k", "search_method", "mmr_fetch_k", "mmr_lambda")}}

    @app.get("/api/movies")
    def movie_list():
        return {"items": [{key:item.get(key) for key in ("movie_id", "title", "year", "genres", "runtime")}
                          for item in items]}

    @app.get("/api/movies/{identity}")
    def movie_detail(identity: str):
        return item_for(identity)

    @app.get("/api/history/{identity}")
    def history(identity: str, request: Request):
        item_for(identity)
        with request.state.session["lock"]:
            return public_value({"messages": request.state.session["histories"].get(identity, [])})

    @app.delete("/api/history/{identity}")
    def clear_history(identity: str, request: Request):
        with request.state.session["lock"]:
            request.state.session["histories"].pop(identity, None)
        return {"cleared": True}

    @app.get("/api/jobs/{identity}")
    def get_job(identity: str, request: Request):
        return jobs.get(request.state.owner, identity)

    @app.post("/api/index", status_code=202)
    def index(body: OptionsRequest, request: Request):
        instance = service(body.options)
        return jobs.submit(request.state.owner, lambda notice: instance.index_items(items, notice))

    @app.post("/api/chat", status_code=202)
    def chat(body: QuestionRequest, request: Request):
        item, instance = item_for(body.movie_id), ready(body.options)
        if body.mode == "question" and not body.message.strip():
            raise UserError("질문을 입력하세요.")
        session = request.state.session
        def action(notice):
            with session["lock"]:
                messages = session["histories"].setdefault(body.movie_id, [])
                recent = [{"role":m["role"], "content":m["content"]} for m in messages[-6:]]
                result = (instance.guide(item, recent, notice) if body.mode == "guide" else
                          instance.ask(item, body.message, recent, notice))
                messages.extend([{"role":"user", "content": result["question"]},
                    {"role":"assistant", "content": result["answer"], "sources": result["sources"],
                     "timings": result.get("timings", {}), "collection": result["collection"]}])
                del messages[:-40]
                return result
        return jobs.submit(request.state.owner, action)

    @app.post("/api/explore", status_code=202)
    def explore(body: ExploreRequest, request: Request):
        instance = ready(body.options)
        return jobs.submit(request.state.owner, lambda notice: instance.find_items(body.query, items))

    @app.post("/api/search-comparison", status_code=202)
    def compare_search(body: QuestionRequest, request: Request):
        instance, item = ready(body.options), item_for(body.movie_id)
        if not body.message.strip():
            raise UserError("비교할 질문을 입력하세요.")
        return jobs.submit(request.state.owner, lambda notice: instance.compare_search(item, body.message, notice))

    @app.get("/api/sources")
    def sources():
        return {"pdf": [{key:entry.get(key) for key in
                          ("id", "title", "url", "source", "license", "license_url", "movie_ids")}
                         for entry in manifest(settings)],
                "wiki": {"source":"한국어 위키백과", "license":"CC BY-SA 4.0",
                         "url":"https://ko.wikipedia.org/", "license_url":"https://creativecommons.org/licenses/by-sa/4.0/"}}

    @app.post("/api/pdf/index", status_code=202)
    def index_pdf(body: QuestionRequest, request: Request):
        instance, item = ready(body.options), item_for(body.movie_id)
        return jobs.submit(request.state.owner, lambda notice:
            index_for_item(instance.settings, item, instance.store, instance.domain, notice))

    @app.get("/api/evaluation-cases")
    def evaluation_cases():
        return {"cases": cases()}

    @app.post("/api/evaluations", status_code=202)
    def evaluate(body: OptionsRequest, request: Request):
        instance = ready(body.options)
        def action(notice):
            result = run_evaluation(instance, items, notice)
            with request.state.session["lock"]:
                request.state.session["evaluations"].add(result["id"])
            return result
        return jobs.submit(request.state.owner, action)

    @app.post("/api/benchmarks", status_code=202)
    def benchmark_route(body: OptionsRequest, request: Request):
        instance = ready(body.options)
        return jobs.submit(request.state.owner, lambda notice: benchmark(instance, items, notice))

    @app.post("/api/evaluations/{identity}/review")
    def review(identity: str, body: ReviewRequest, request: Request):
        authorized_evaluation(request, identity)
        values = body.model_dump()
        case_id = values.pop("case_id")
        return review_evaluation(settings, identity, case_id, values)

    @app.get("/api/evaluations/{identity}/report")
    def download_report(identity: str, request: Request):
        result = authorized_evaluation(request, identity)
        return Response(markdown_report(result), media_type="text/markdown; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="rag-comparison-{identity}.md"'})

    @app.get("/")
    def home():
        return FileResponse(ROOT / "web/index.html")

    @app.get("/assets/app.js")
    def javascript():
        # Windows 레지스트리의 .js MIME 연결이 text/plain인 환경에서도 모듈을 실행한다.
        return FileResponse(ROOT / "web/app.js", media_type="text/javascript")

    app.mount("/assets", StaticFiles(directory=ROOT / "web"), name="assets")
    return app
