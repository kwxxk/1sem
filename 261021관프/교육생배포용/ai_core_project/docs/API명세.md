# 로컬 웹 API

실행: `python serve.py` → http://127.0.0.1:8000

UI: web/index.html + styles.css + app.js. API: movielab/webapi/. Streamlit app.py와 같은 Service를 사용한다.
Content-Type은 application/json이다. 키·프롬프트·환경 파일 경로를 요청/응답에 넣지 않는다.

## 요청과 응답

| 메서드·경로 | 입력 | 결과 |
|---|---|---|
| GET /api/status | 없음 | 키 설정 여부, 색인 건수, 안전한 검색 설정, 실행 모드 |
| GET /api/movies | 없음 | 선택용 영화 목록 |
| GET /api/movies/{id} | 영화 ID | 영화 정보 |
| GET /api/history/{id} | 세션 쿠키 | 해당 세션·영화의 대화 |
| DELETE /api/history/{id} | 세션 쿠키 | 해당 영화 대화 삭제 |
| POST /api/index | options 선택 | 색인 작업 ID |
| POST /api/chat | movie_id, message 또는 mode=guide, options | 답변 작업 ID |
| POST /api/explore | query, options | 조건 탐색 작업 ID |
| POST /api/search-comparison | movie_id, message, options | 동일 질문의 유사도/MMR 검색 작업 ID |
| GET /api/sources | 없음 | PDF·위키 원문·이용 조건·연결 영화 |
| POST /api/pdf/index | movie_id, options | 등록된 해당 영화 PDF 색인 작업 ID |
| GET /api/evaluation-cases | 없음 | 대표 질문 5개와 검토 기준 |
| POST /api/evaluations | options 선택 | 5쌍 비교 작업 ID |
| POST /api/evaluations/{uuid}/review | case_id, without_accuracy, with_accuracy, without_unknown_handling, with_unknown_handling, notes | 검토 저장 결과 |
| GET /api/evaluations/{uuid}/report | 세션 쿠키 | Markdown 첨부 보고서 |
| POST /api/benchmarks | options 선택 | 5개 질문을 두 번씩 측정하는 작업 ID |
| GET /api/jobs/{uuid} | 소유 세션 쿠키 | state, progress, result 또는 안전한 error |

선택적 options:

```json
{"search_method":"mmr","top_k":6,"chunk_size":1000,"chunk_overlap":200}
```

질문 요청 예:

```json
{"movie_id":"157336","message":"블랙홀의 사건의 지평선이란?","options":{"search_method":"mmr","top_k":6,"chunk_size":1000,"chunk_overlap":200}}
```

긴 작업의 최초 HTTP 상태는 202, 본문은 `{"job_id":"UUID"}`다. 이후 해당 작업을 폴링한다.
state는 queued/running/completed/failed. completed이면 result에 해당 작업 결과를 반환한다.
채팅 result는 question, answer, sources, collection, timings, metrics를 포함한다.
sources의 source_type은 메타데이터/외부 문서를 구분하고 source_kind는 metadata/wiki/pdf를 구분한다.
PDF에는 page·file_id·원문 URL #page=N이 있다. 실제 답변 근거 UI는 인용 번호에 해당하는 sources만 표시한다.

평가 값은 적절/부적절/판단보류 중 선택하고 원문과 대조한 이유를 notes에 기록한다.
자동 인용 표식 관찰과 사람의 정확성 평가를 구분한다. 모델을 실행하기 전에는 비교가 완료되지 않는다.

잘못된 입력은 422, 안전한 도메인/설정 안내는 400, 잘못된 Origin은 403이다.
오류 본문은 `{"error":"안내"}`이며 입력 원문·프롬프트·인증 헤더·traceback을 포함하지 않는다.
GMS 키가 없을 때 목록·출처를 볼 수 있지만 색인/생성 작업은 거부한다.
