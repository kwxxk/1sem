"""step7_skeleton의 항목 선택/채팅/진행 상태/실제 인용 표시를 확장한 실행 진입점."""
import os
import time

import streamlit as st

from movielab.config import UserError, load_settings
from movielab.preparation.movies import read_movies
from movielab.citations import cited_sources
from movielab.operations import public_error

st.set_page_config(page_title="Movie Lab", page_icon="🎬", layout="wide")
st.title("🎬 Movie Lab")
st.caption("영화 데이터와 외부 문서를 근거로 답하는 영화 지식 서비스")


def safe_error(exc):
    # traceback/전체 프롬프트/요청 헤더는 사용자 화면에 출력하지 않는다.
    st.error(public_error(exc))


@st.cache_data
def get_movies(path, modified):
    return read_movies(path)


@st.cache_resource
def get_service(settings, key_fingerprint):
    from movielab.service import Service
    return Service(settings)


def choose_movie(movie_id):
    st.session_state.selected_movie = movie_id


def render_sources(answer, sources):
    used = cited_sources(answer, sources)
    if not used:
        st.caption("ⓘ 답변에 인용된 근거가 없습니다.")
        return
    with st.expander(f"답변에 사용한 근거 {len(used)}건"):
        for number, source in used:
            st.markdown(f"**[근거 {number}] {source['title']}** · {source['source_type']}")
            st.markdown(f"출처: {source.get('source', '')}")
            st.caption(f"종류: {source.get('source_kind', '메타데이터')}" +
                       (f" · {source['page']}쪽" if source.get('page') else ""))
            if source.get("url", "").startswith("https://"):
                st.link_button("원문 보기", source["url"])
            st.caption(source["text"][:450])


try:
    base_settings = load_settings()
    movies = get_movies(base_settings.movies_path, base_settings.movies_path.stat().st_mtime_ns)
except Exception as exc:
    safe_error(exc)
    st.stop()

by_id = {str(m["movie_id"]): m for m in movies}
with st.sidebar:
    st.header("영화 선택")
    st.selectbox("질문할 영화", list(by_id), key="selected_movie",
                 format_func=lambda mid: f"{by_id[mid]['title']} ({by_id[mid].get('year', '')})")
    with st.expander("검색 설정"):
        size = st.number_input("청크 크기(자)", 100, 8000, base_settings.chunk_size, 100)
        overlap = st.number_input("중복 길이(자)", 0, 7900, base_settings.chunk_overlap, 50)
        top_k = st.slider("전체 근거 수(Top-k)", 2, 20, base_settings.top_k)
        st.caption("Top-k는 선택 영화 메타데이터 1건을 포함한 최대 근거 수입니다. 청크 설정 변경 시 저장된 원문을 재색인합니다.")
    st.caption(f"로드된 영화 {len(movies):,}편")

try:
    settings = base_settings.search_options(size, overlap, top_k)
except UserError as exc:
    safe_error(exc)
    st.stop()

key = os.getenv("GMS_KEY", "").strip()
service = None
if not key:
    st.info("GMS 키가 아직 설정되지 않았습니다. .env에 GMS_KEY를 넣은 뒤 다시 실행하세요. 영화 목록은 미리 볼 수 있습니다.")
else:
    import hashlib
    try:
        service = get_service(settings, hashlib.sha256(key.encode()).hexdigest())
    except Exception as exc:
        safe_error(exc)

with st.sidebar:
    if service:
        st.metric("메타데이터 색인", service.store.meta.count())
        st.metric("외부 문서 청크", service.store.external.count())
    else:
        st.caption("색인 건수는 키 설정 후 확인할 수 있습니다.")
    if st.button("메타데이터 색인 / 갱신", disabled=service is None):
        try:
            with st.status("영화 메타데이터를 색인합니다.", expanded=True) as status:
                summary = service.index_items(movies, status.write)
                status.update(label=f"로드 {summary['loaded']}건 / 색인 {summary['indexed']}건 / 갱신 {summary['updated']}건", state="complete")
            st.session_state.index_summary = summary
            st.rerun()
        except Exception as exc:
            safe_error(exc)
    if "index_summary" in st.session_state:
        st.caption(f"최근 색인 결과: {st.session_state.index_summary}")

movie_id = st.session_state.selected_movie
movie = by_id[movie_id]
histories = st.session_state.setdefault("movie_histories", {})
messages = histories.setdefault(movie_id, [])
ready = service is not None and service.store.meta.count() > 0
if service and not ready:
    st.warning("색인이 없습니다. 사이드바에서 ‘메타데이터 색인 / 갱신’을 먼저 실행하세요.")

chat_tab, explore_tab, info_tab = st.tabs(["영화 질문 · 관람 가이드", "조건으로 영화 찾기", "영화 정보"])
with explore_tab:
    with st.form("explore_form"):
        condition = st.text_input("원하는 영화 조건", placeholder="2010년 이후 한국 영화 중 120분 이하 스릴러")
        submitted = st.form_submit_button("조건 검색", disabled=not ready)
    if submitted and condition.strip():
        try:
            with st.spinner("자연어 조건을 해석하고 영화 후보를 검증합니다..."):
                st.session_state.exploration = service.find_items(condition, movies)
        except Exception as exc:
            st.session_state.pop("exploration", None)
            safe_error(exc)
    if "exploration" in st.session_state:
        found = st.session_state.exploration
        st.caption(found["notice"])
        with st.expander("해석된 조건 확인"):
            st.json(found["filters"])
        if not found["results"]:
            st.info("모든 조건을 확인할 수 있는 영화가 없습니다. 조건을 바꿔 보세요.")
        for entry in found["results"]:
            item = entry["item"]
            with st.container(border=True):
                st.markdown(f"**{item['title']} ({item.get('year', '')})**")
                st.write(entry["reason"])
                st.caption(f"{', '.join(item['genres'])} · {item.get('runtime')}분 · 평점 {item.get('vote_average')}")
                if item.get("tmdb_url", "").startswith("https://"):
                    st.link_button("데이터 출처", item["tmdb_url"])
                st.button("이 영화 선택", key=f"choose_{item['movie_id']}",
                          on_click=choose_movie, args=(str(item["movie_id"]),))
    st.caption("영화를 선택한 뒤 첫 번째 탭에서 질문을 이어가세요.")

with info_tab:
    st.subheader(movie["title"])
    st.write(movie.get("overview", "줄거리 없음"))
    st.json({k: movie[k] for k in ("year", "genres", "director", "cast", "runtime", "original_language")})
    st.caption("메타데이터: 배포된 TMDB 영화 데이터 / 외부 문서: 한국어 위키백과, CC BY-SA 4.0")

with chat_tab:
    st.subheader(f"{movie['title']} ({movie.get('year', '')})")
    c1, c2 = st.columns(2)
    guide = c1.button("근거 기반 관람 가이드 만들기", disabled=not ready)
    if c2.button("이 영화 대화 지우기"):
        histories[movie_id] = []
        st.rerun()
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_sources(message["content"], message.get("sources", []))
                st.caption(f"처리 시간 {message.get('elapsed', 0):.1f}초")
                with st.expander("문서 수집 결과 확인"):
                    st.json(message.get("collection", {}))
    question = st.chat_input("이 영화에 대해 질문하세요", disabled=not ready)
    if question or guide:
        history = [{"role": m["role"], "content": m["content"]} for m in messages[-6:]]
        with st.chat_message("user"):
            st.markdown("관람 가이드 요청" if guide else question)
        start = time.perf_counter()
        with st.chat_message("assistant"):
            try:
                with st.status("문서를 준비합니다...", expanded=True) as status:
                    result = (service.guide(movie, history, status.write) if guide else
                              service.ask(movie, question, history, status.write))
                    status.update(label="답변 준비 완료", state="complete")
                elapsed = time.perf_counter() - start
                messages.extend([
                    {"role": "user", "content": result["question"]},
                    {"role": "assistant", "content": result["answer"], "sources": result["sources"],
                     "collection": result["collection"], "elapsed": elapsed}])
                st.markdown(result["answer"])
                render_sources(result["answer"], result["sources"])
                st.caption(f"처리 시간 {elapsed:.1f}초")
                for warning in result["collection"]["warnings"]:
                    st.info(warning)
                with st.expander("문서 수집 결과 확인"):
                    st.json(result["collection"])
            except Exception as exc:
                safe_error(exc)
