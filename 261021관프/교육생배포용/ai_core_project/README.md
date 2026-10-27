# Movie Lab — 근거로 읽는 영화

AI 코어 프로젝트 2회차: 필수 F2001~F2012, 심화 F2013~F2016, 비기능 NF2001~NF2007의 실행 코드입니다.
2026-10-21 실제 GMS 연결·영화 964개 임베딩·대표 질문 5개 비교·반복 시간·웹 화면을 검증했습니다.
결과와 발견한 문제/수정, 남은 제약은 [실제 검증 결과](docs/GMS_실제검증결과.md)에 기록했습니다.

## 실행

이 README가 있는 `ai_core_project`에서 실행합니다.

Git Bash:

```bash
source .venv/Scripts/activate
python serve.py
```

가상환경을 활성화하지 않으려면 `./.venv/Scripts/python.exe serve.py`를 사용하세요.

PowerShell:

```powershell
.\.venv\Scripts\python.exe serve.py
```

브라우저에서 http://127.0.0.1:8000 을 엽니다. 다른 포트: `python serve.py --port 8001`.
기존 필수 Streamlit 화면도 유지합니다: `python -m streamlit run app.py`.
심화 기능은 새 웹 화면의 검색·답변 비교 / 문서와 출처에서 사용합니다.

환경을 새로 준비할 때:

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

명세서의 필수 14개 및 심화 FastAPI·Uvicorn·Pydantic 버전을 고정했습니다. PDF 추출은 pypdf를 추가했습니다.

## 키 설정과 첫 색인

기존 `.env`에 키를 넣고 서버를 재시작하세요. `.env`가 없다면 `.env.example`을 복사합니다.
이미 있는 파일은 덮어쓰지 마세요. 키를 웹 화면에 입력하거나 브라우저로 전달하지 않습니다.

```dotenv
GMS_KEY=발급받은키
WIKI_CONTACT=본인의영문이메일
```

모델은 config.json 또는 .env의 CHAT_MODEL·EMBEDDING_MODEL로 지정합니다.
GMS에서 해당 모델의 사용 권한이 있어야 합니다. 현재 설정의 채팅·임베딩 모델은 실제 호출을 확인했습니다.
임베딩 모델/주소가 바뀌면 다른 컬렉션을 사용하므로 메타데이터를 다시 색인하세요.

1. 키 없이 영화 목록과 출처를 볼 수 있습니다.
2. 키 설정 후 왼쪽의 **영화 데이터 색인 / 갱신**을 누릅니다.
3. 영화를 고르고 질문하거나 관람 가이드를 요청합니다.
4. 근거 번호를 펼쳐 실제 인용한 원문과 답변을 대조합니다.

CLI 명령:

```bash
python manage.py inspect
python manage.py index-movies
python manage.py graph
python manage.py reindex-docs
```

## 데이터와 저장

기존 배포 폴더를 참조합니다. 저장소를 옮기면 config.json의 경로를 수정하세요.

```text
260121관프/
  교육생배포용/
    streamlit_lab/       원래 실습 자료
    ai_core_project/     이 프로젝트
  영화도메인_데이터_배포용/
    movies.json
    movielab_wiki/wikipedia/
```

영화 964편(한국어 168편), 위키 파일 3,725개를 사용합니다.
메타데이터는 항목당 1텍스트, 외부 문서는 별도 컬렉션에 청킹·임베딩합니다.
ID는 영화 메타데이터의 movie_id, 외부 청크의 movie_id:page_id:순번으로 고정해 중복을 막습니다.
원문·검색어 캐시·색인·성능·비교 결과는 `.local/`에 저장하고 Git에서 제외합니다.

문서 모드: `auto`(기본: 위키 설정/호출 제한 시 배포 묶음 대체), `wiki`, `bundle`.
검색어 추출·후보 선별은 어느 모드에서도 직접 구현한 LLM 프롬프트를 사용합니다.
영화 자체 문서는 선별보다 우선합니다. **묶음 모드의 13편 자체 문서 식별 제약은 남아 있습니다.**
관련 없는 문서를 영화 자체 문서로 대신하지 않고 안내 후 중단합니다. 올바른 원문·작품 대응을 확보해야 합니다.

## 심화 기능

### F2013 — HTML/CSS/JavaScript와 API

web/의 프론트엔드와 movielab/webapi/의 FastAPI를 분리했습니다.
질문·근거·대화·조건 탐색·가이드는 기존 Service/RAG를 함께 사용합니다.
긴 작업은 background job으로 처리하고 현재 단계와 결과를 폴링합니다.
요청/응답 규격은 docs/API명세.md에 있습니다.

### F2014 — MMR

왼쪽 검색 방식을 MMR로 바꾸면 기본 질의도 MMR을 사용합니다.
검색·답변 비교의 근거 목록 비교에서는 같은 질문에 유사도와 MMR을 나란히 실행합니다.
유형별 기본 후보 최대 30건, λ=0.5, Top-k=6(메타데이터 1건 포함)입니다. 슬롯이 충분하면 위키/PDF 유형별 최상위 후보를 최소 한 개 유지합니다. 후보가 적으면 두 결과가 같을 수 있습니다.
설정의 청크 1000자/중복 200자는 문맥 보존과 입력량을 균형 있게 시작하기 위한 값이며, 실제 품질 비교가 필요합니다.

### F2015 — 대표 질문 5개의 RAG 전후 비교

검색·답변 비교에서 5개 질문 실행 → 원문 대조 → 정확성/모르는 내용 처리와 이유 저장 → 보고서 내려받기.
data/evaluation_cases.json에 메타데이터·외부 문서·확인 불가 질문을 정했습니다.
인용 표식은 자동 관찰하고, 사실 정확성과 확인 불가 응답 적절성은 사람이 평가합니다.
JSON은 `.local/evaluations/`에 보존합니다. 서버 재시작 후에는 CLI로 저장된 기록을 내보낼 수 있습니다.

```bash
python manage.py evaluate
python manage.py export-evaluation --id UUID --output docs/RAG_전후비교_실제결과.md
```

최종 실제 5쌍 응답은 docs/RAG_전후비교_실제결과.md에 저장했습니다. 사람의 평가 완료 상태는 아직 false입니다. docs/RAG_전후비교_실행대기.md는 이전 계획서입니다.
테스트 모델의 답변을 실제 결과로 제출하지 마세요.

### F2016 — 위키와 PDF

인터스텔라에 NASA의 A Field Guide to Black Holes PDF를 연결했습니다.
등록 정보는 data/pdf_manifest.json, 출처·이용 조건은 data/SOURCES.md에 있습니다.
원본은 `.local/source_pdfs/`에 두고 Git에서 제외합니다. 원본이 없으면:

```bash
python manage.py fetch-pdfs
python manage.py inspect-pdfs
python manage.py index-pdfs
```

웹에서도 선택 영화 PDF 색인을 실행할 수 있습니다. 질문 때 연결된 PDF를 자동 준비합니다.
PDF는 2~4쪽만 각각 추출하고 쪽 경계를 보존합니다. 위키와 같은 외부 컬렉션에서 검색하며
근거에 metadata/wiki/pdf 종류, 출처, 원문, PDF 쪽 번호를 표시합니다.
이 PDF가 모든 영화에 연결되는 것은 아닙니다. 추가 자료는 출처·이용 조건과 연결 영화를 등록하세요.

## 비기능과 성능 확인

- 검색어·원문·인덱스 캐시와 제한된 질문 임베딩 캐시를 사용합니다.
- 위키는 공통 호출 간격·재시도·Retry-After·연락처를 적용하고 GMS도 호출 간격/SDK 재시도를 사용합니다.
- API는 세션별 대화·작업 소유권을 구분하고 대기 작업 수를 제한합니다.
- 키·프롬프트·오류 추적 정보는 UI·성능 기록에 넣지 않습니다. 모델/사용자 문자열은 HTML로 해석하지 않습니다.
- `.env`, `.venv/`, `venv/`, `.local/`, `.test-work/`는 Git 제외, `.env.example`은 포함입니다.
- 원문·출처·이용 조건을 보존하고 자료 준비와 저장소·그래프·서비스·UI 책임을 분리합니다.

`python manage.py benchmark` 또는 웹의 실제 처리 시간 측정으로 대표 질문 5개를 두 번씩 실행합니다.
기존 캐시 여부와 단계별·전체 시간을 `.local/metrics.jsonl`과 benchmark.json에 기록합니다.
첫 120초/반복 30초는 내부 목표 설정이며 명세의 고정 기준이 아닙니다.
첫 요청이 이미 캐시된 경우 cold start 측정이 아닙니다. 실제 표본 측정값과 캐시 조건은 docs/GMS_실제검증결과.md를 참고하세요.

## 검증과 문서

```bash
python -m unittest discover -s tests -v
python -m pip check
```

기존 필수 14개 + 심화/비기능 13개 = **27개 자동 테스트 통과**.
실제 Edge에서도 데스크톱·모바일, 질문·대화 분리·MMR·5쌍 응답·평가 저장·PDF를 검증했습니다.
테스트는 실제 Chroma/LangGraph/Streamlit/FastAPI를 쓰고 GMS 응답·임베딩만 대체했습니다.
docs/screenshots의 test 이미지는 실제 GMS 품질 증빙이 아닙니다.

- docs/GMS_실제검증결과.md — 최신 실제 GMS 검증 상태
- docs/심화_비기능_구현검증.md — 키 적용 전 구현 검증 이력
- docs/API명세.md — 웹 API 규격
- docs/요구사항정의서.md, RAG파이프라인설계.md, 프로젝트구조.md — 설계
- docs/작업순서_진행현황.md — PDF 1.3 순서와 현재 상태
- docs/요구사항_체크리스트_점검결과.md — **심화 구현 전** 사전 점검 이력

실제 GMS 답변·성능·비교 결과는 확보했습니다. 사람의 셀프·상호 체크리스트는 작성 완료 상태가 아닙니다.

## 출처

- 메타데이터: 교육용 TMDB 배포 팩. 원문 tmdb_url 보존, 공개 재배포는 제공처 및 TMDB 조건 확인.
- 외부 문서: 한국어 위키백과, 배포 안내 기준 CC BY-SA 4.0.
- PDF: [NASA 원문 안내](https://science.nasa.gov/resource/a-field-guide-to-black-holes-booklet/) 및
  [이용 지침](https://www.nasa.gov/nasa-brand-center/images-and-media/). 원문 안의 제3자 크레딧 보존.

data/SOURCES.md에 원문·이용 조건·수집일·체크섬·처리 방식을 정리했습니다.
원본 실습 폴더는 유지했으며, 이 프로젝트 .env에만 사용자가 제공한 GMS 키를 설정했습니다.
