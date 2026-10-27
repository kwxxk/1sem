# 구현 소스코드

실행 방법·전체 기능·데이터 준비·색인·출처는 [산출물 README](../README.md)를 참고한다.

| 구분 | 구현 위치 |
|---|---|
| Python 실행 진입점 | app.py, serve.py |
| 수집·색인 스크립트 | manage.py의 fetch-pdfs, index-movies, index-pdfs, reindex-docs 명령 |
| 영화 데이터 준비·위키/PDF 수집 | movielab/preparation/ |
| Vector DB·검색 | movielab/store.py, retrieval.py |
| RAG·인용 | movielab/pipeline.py, citations.py |
| 서비스·조건 탐색 | movielab/service.py, explore.py |
| 심화 웹/API | web/, movielab/webapi/ |
| 심화 답변 비교·성능 기록 | movielab/evaluation.py, operations.py |
| 설정·출처·배포 데이터 | config.json, data/, data_assets/ |
| 자동 검사 | tests/ |
