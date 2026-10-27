# 데이터·문서 출처와 이용 조건

| 자료 | 원문·제공처 | 이용 조건 기록 | 처리 |
|---|---|---|---|
| 영화 메타데이터 964편 | 교육용 제공 TMDB 기반 movies.json, 각 tmdb_url | 제공처 및 https://www.themoviedb.org/terms-of-use 의 허용 범위를 확인. 별도 자유 재배포 허가를 받은 것으로 간주하지 않음. | 영화당 1텍스트. 원본 데이터는 이 저장소 밖의 배포 폴더를 참조. |
| 한국어 위키백과 | https://ko.wikipedia.org/ 및 배포 문서별 url | 제공 안내의 CC BY-SA 4.0. https://creativecommons.org/licenses/by-sa/4.0/ | 제목·원문·검색어·수집일 보존. 영화별 청킹·색인. |
| A Field Guide to Black Holes | NASA Goddard, https://science.nasa.gov/resource/a-field-guide-to-black-holes-booklet/ | https://www.nasa.gov/nasa-brand-center/images-and-media/ 및 PDF 안의 제3자 크레딧을 보존. NASA가 제품을 승인했다는 표현을 쓰지 않음. | 원본은 .local/source_pdfs에 저장해 Git 제외. 이미지 재배포 없이 교육용 본문 검색. |

PDF 원문: https://science.nasa.gov/wp-content/uploads/2023/09/black_hole_field_guide_booklet.pdf

2026-10-21 수집한 원본 SHA256:
`e2ca1e01b1ec8426e8e9dd99d1a56db1edb7e526aa148230d3911f761c0988f4`

인터스텔라(157336)의 블랙홀 배경 자료로 연결했다. 이 문서가 영화 제작상의 모든 주장을 확인해 주는 것은 아니다.
영문 PDF의 2~4쪽을 각각 추출한다. 1쪽은 표지·가상 서평·크레딧이어서 검색 본문에서 제외한다.
각 쪽 안에서는 기본 1000/200자 청킹을 사용한다. 위키와 다른 점은 쪽 경계를 넘어 청킹하지 않는 것으로,
파일·쪽 번호를 정확하게 제시하기 위한 선택이다. 원문 링크 #page=N과 source_kind=pdf를 청크마다 저장한다.

추가 PDF는 pdf_manifest.json에 ID·프로젝트 내부 경로·제목·HTTPS 원문·출처·이용 조건·연결 영화 ID를 등록한다.
실제 원문이 없으면 성공으로 꾸미지 않고 fetch-pdfs 안내를 표시한다. 출처·이용 조건이 누락된 등록은 거부한다.
