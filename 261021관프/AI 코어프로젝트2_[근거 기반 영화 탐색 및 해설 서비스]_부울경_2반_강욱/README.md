# 근거 기반 영화 탐색 및 해설 서비스

## 1. 프로젝트 개요 및 실행 방법

Movie Lab은 영화 메타데이터와 위키백과·NASA PDF를 검색해, 답변에 사용한 근거와 원문 링크를 함께 제공하는 영화 RAG 서비스다. 영화별 질문과 대화, 근거 기반 관람 가이드, 자연어 조건 탐색을 제공한다. Python 3.12, LangChain, LangGraph, Chroma를 사용하며 Streamlit 화면과 HTML/CSS/JavaScript·FastAPI 화면을 지원한다.

### 환경 준비

산출물 폴더에서 Windows Git Bash를 열고 실행한다.

```bash
cd "04_구현소스코드"
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; fi
```

`.env`의 `GMS_KEY`에 본인의 GMS 키를 입력한다. 위키백과 실시간 API를 사용하려면 `WIKI_CONTACT`에 본인의 영문 이메일 또는 연락 가능한 URL을 설정한다. 연락처가 없으면 기본 `auto` 모드에서 제공 위키 문서 묶음을 사용한다. 실제 키와 가상환경은 산출물에 포함하지 않는다.

### 데이터 준비와 실행

```bash
./.venv/Scripts/python.exe manage.py fetch-pdfs
./.venv/Scripts/python.exe manage.py inspect
./.venv/Scripts/python.exe manage.py index-movies
./.venv/Scripts/python.exe serve.py
```

브라우저에서 http://127.0.0.1:8000 을 연다. 다른 포트는 `serve.py --port 8001`처럼 지정한다.

기본 Streamlit 화면은 다음 명령으로 실행한다.

```bash
./.venv/Scripts/python.exe -m streamlit run app.py
```

PowerShell에서는 Python 실행 경로를 `.\.venv\Scripts\python.exe`로 바꿔 사용한다. 이후 명령의 인자는 같다.

## 2. 전체 기능 설명

### 필수 기능

| ID | 기능 | 설명 |
|---|---|---|
| F2001 | 영화 데이터 준비 | 영화 964편을 로드하고 제목·연도·장르·감독·출연·줄거리 등을 항목별 텍스트로 구성한다. |
| F2002 | 메타데이터 색인 | 영화별 고정 ID와 내용 해시로 임베딩을 저장하고 변경 없는 항목은 다시 색인하지 않는다. |
| F2003 | 검색어 추출 | 영화 큐레이터 프롬프트로 검색어를 JSON 배열로 추출하고 영화 자체 검색어를 포함한다. |
| F2004 | 외부 문서 수집 | 후보 제목·요약을 LLM으로 선별한 뒤 본문과 URL을 수집하고 영화·검색어별 결과를 재사용한다. |
| F2005 | 외부 문서 색인 | 수집 문서를 설정된 크기와 중복 길이로 나누어 메타데이터와 별도 컬렉션에 저장한다. |
| F2006 | 근거 검색 | 선택 영화의 메타데이터를 포함하고 같은 영화의 외부 문서를 검색해 병합·중복 제거한다. |
| F2007 | RAG 답변 생성 | LangGraph의 retrieve·generate 두 노드로 답변을 생성하며 문서에 없는 내용은 확인 불가로 안내한다. |
| F2008 | 인용 및 출처 표시 | 본문의 근거 번호와 실제 인용한 문서의 제목·원문 링크·출처 유형을 함께 표시한다. |
| F2009 | 영화별 대화 | 선택한 영화별로 대화를 구분하고 영화 전환 후 이전 대화를 다시 표시한다. |
| F2010 | 관람 가이드 | 작품 소개와 관람 전 배경 지식을 근거와 함께 제공한다. |
| F2011 | 조건 탐색 | 자연어 조건을 구조화해 명시 조건 검사·의미 검색·후보 검증 후 영화 카드를 제공한다. |
| F2012 | 상태 및 오류 안내 | 처리 진행, 키 없음, 색인 없음, 검색 결과 없음, 확인 불가와 오류 상태를 안내한다. |

### 선택한 심화 기능

| ID | 기능 |
|---|---|
| F2013 | HTML/CSS/JavaScript 프론트엔드와 FastAPI 서버 분리 |
| F2014 | 유사도 검색과 MMR 검색 선택 및 근거 목록 비교 |
| F2015 | 대표 질문 5개에 대한 RAG 사용 전후 답변 비교·평가·보고서 저장 |
| F2016 | 위키백과와 PDF를 결합한 검색 및 출처 유형·PDF 쪽 번호 표시 |

## 3. 데이터 준비 및 색인 절차 요약

1. `04_구현소스코드/data_assets/movies.json`의 영화 964편과 `data_assets/movielab_wiki/wikipedia/`의 위키 문서 3,725파일을 사용한다. `config.json`은 프로젝트 내부 상대 경로를 참조한다.
2. `manage.py fetch-pdfs`로 등록된 NASA PDF를 내려받는다. 등록 정보와 체크섬은 `data/pdf_manifest.json`에 있으며 원본은 `.local/`에 저장한다.
3. `manage.py inspect`로 영화 데이터 건수와 색인할 텍스트 예시를 확인한다.
4. `manage.py index-movies`로 영화당 하나의 텍스트를 임베딩해 메타데이터 컬렉션에 저장한다. 같은 명령을 다시 실행하면 변경된 항목만 갱신한다.
5. 질문 시 검색어 추출 → 외부 문서 후보 선별 → 본문 수집 → 청킹 → 외부 컬렉션 색인 순서로 처리한다. 연결된 PDF도 페이지별로 준비한다.
6. 선택 영화의 메타데이터와 외부 근거를 검색·병합한 뒤 답변을 생성한다. 완료된 검색어와 원문은 재사용한다.

기본 설정은 청크 크기 1,000자, 중복 길이 200자, 전체 근거 상한 Top-k 6건이다. 메타데이터 1건을 포함하고 외부 근거는 최대 5건을 사용한다. 값은 `config.json` 또는 화면의 검색 설정에서 조정한다.

메타데이터와 외부 문서는 별도 Chroma 컬렉션에 저장한다. 색인·캐시·실행 기록은 `.local/`에서 관리하며 산출물에는 기존 벡터 DB를 포함하지 않는다. 새 환경의 최초 색인과 질문에는 실제 GMS API 사용량이 발생한다.

## 4. 사용한 데이터·문서의 출처와 이용 조건

| 자료 | 출처 | 이용 조건 및 사용 범위 |
|---|---|---|
| 영화 메타데이터 | 교육용 TMDB 기반 배포 JSON, 각 항목의 `tmdb_url` | 제공처 안내와 [TMDB 이용 조건](https://www.themoviedb.org/terms-of-use)을 따른다. 교육용 제공이 별도의 공개 재배포 허가를 뜻하지 않는다. |
| 한국어 위키백과 문서 | [한국어 위키백과](https://ko.wikipedia.org/)와 제공 문서 묶음의 개별 원문 URL | 제공 안내의 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)에 따라 출처와 이용 조건을 보존한다. |
| A Field Guide to Black Holes | [NASA Goddard 원문 안내](https://science.nasa.gov/resource/a-field-guide-to-black-holes-booklet/) | [NASA 미디어 이용 지침](https://www.nasa.gov/nasa-brand-center/images-and-media/)과 원문의 제3자 크레딧을 보존한다. 인터스텔라의 과학 배경 자료로 2~4쪽 텍스트를 검색하며 이미지를 재배포하지 않는다. |

세부 원문 URL·PDF 체크섬·처리 방식은 [출처 기록](04_구현소스코드/data/SOURCES.md)과 [배포 데이터 안내](04_구현소스코드/data_assets/README.md)에 정리했다.

## 5. 심화 기능 적용 요약

- **F2013 — 웹 UI/API 분리:** 기본 Streamlit 서비스와 동일한 수집·검색·생성 서비스를 HTML/CSS/JavaScript 및 FastAPI로 연결했다. 긴 작업은 백그라운드 작업으로 실행하고 진행 상태를 표시한다.
- **F2014 — MMR:** 기본 유사도 검색에 근거 간 다양성을 반영하는 MMR을 추가했다. 기본 관련성 가중치는 λ=0.5이며, 같은 질문·색인·Top-k로 두 검색 방식의 근거를 나란히 비교한다.
- **F2015 — RAG 전후 비교:** 같은 모델에 대표 질문 5개를 문서 없이/문서를 붙여 각각 답하게 하고 사실 정확성·근거 제시·확인 불가 응답을 비교한다. [실제 비교 기록](03_검증결과/RAG_전후비교_실제결과.md)을 포함하며 사람의 검토 상태는 별도로 관리한다.
- **F2016 — 여러 외부 출처 결합:** 위키백과와 NASA PDF를 같은 외부 컬렉션에 저장하고 출처 유형과 PDF 쪽 번호를 보존한다. 문서 유형별 검색 후보를 확보해 긴 위키 문서에 PDF가 밀리는 문제를 보완했다.
