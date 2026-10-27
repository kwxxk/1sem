# RAG 사용 전후 비교

실행 모드: live / 모델: gpt-5.4-nano

질문 수: 5 / 응답 상태: responses_collected / 사람 검토 완료: False

자동 인용 표식은 사실 정확성을 증명하지 않습니다.


## interstellar-runtime

제공된 영화 데이터에서 인터스텔라의 상영 시간은 몇 분이며 감독은 누구인가?


### RAG 미사용

```text
제가 가진 범위의 일반 지식으로는 **다음과 같습니다.**

- **상영 시간(러닝타임): 169분**
- **감독: 크리스토퍼 놀란(Christopher Nolan)**

다만 질문에 “제공된 영화 데이터”라고 되어 있는데, 실제로 그 데이터가 이 대화에 포함되어 있지는 않아서 **데이터를 근거로 한 답**은 아니고, **일반적으로 알려진 정보**로 답한 것입니다.
```


### RAG 사용

```text
인터스텔라의 **상영시간은 169분**이며 [근거 1], **감독은 크리스토퍼 놀란**입니다. [근거 1]
```


### 검토 기준

배포 데이터의 runtime과 director 대조


### 원문 근거

- 인터스텔라: https://www.themoviedb.org/movie/157336 (metadata)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- A Field Guide to Black Holes · 4쪽: https://science.nasa.gov/wp-content/uploads/2023/09/black_hole_field_guide_booklet.pdf#page=4 (pdf)


### 평가

{"without_accuracy": null, "with_accuracy": null, "without_unknown_handling": null, "with_unknown_handling": null, "notes": ""}

시간: 미사용 1.409초 / RAG 1.8257초


## interstellar-countries

인터스텔라의 제작 국가와 개봉 연도는 무엇인가? 제공된 데이터 기준으로 답해줘.


### RAG 미사용

```text
영화 **《인터스텔라(Interstellar)》**의 **제작 국가**는 **미국, 영국**이고, **개봉 연도는 2014년**입니다.
```


### RAG 사용

```text
인터스텔라의 **제작 국가**는 **United Kingdom, United States of America**입니다. [근거 1]

인터스텔라의 **개봉 연도**는 **2014**입니다. [근거 1]
```


### 검토 기준

배포 데이터의 production_countries와 year 대조


### 원문 근거

- 인터스텔라: https://www.themoviedb.org/movie/157336 (metadata)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- A Field Guide to Black Holes · 4쪽: https://science.nasa.gov/wp-content/uploads/2023/09/black_hole_field_guide_booklet.pdf#page=4 (pdf)


### 평가

{"without_accuracy": null, "with_accuracy": null, "without_unknown_handling": null, "with_unknown_handling": null, "notes": ""}

시간: 미사용 0.968초 / RAG 1.9268초


## blackhole-horizon

블랙홀의 사건의 지평선은 무엇이며 빛이 빠져나올 수 있는가?


### RAG 미사용

```text
영화 **〈인터스텔라〉**에서 말하는 **블랙홀의 “사건의 지평선(event horizon)”**은, 한마디로 **“바깥으로 나가려 해도 절대 탈출할 수 없는 경계”**입니다. 즉 그 경계를 넘어가면, 중력(시공간의 휘어짐) 때문에 **어떤 물질이나 신호도 바깥 우주로 전달되지 못합니다.**

- **사건의 지평선의 의미**: 사건의 지평선은 빛을 포함한 모든 신호가 바깥으로 도달할 수 있는지 여부를 가르는 “탈출 불가능의 경계”예요.
- **빛이 빠져나올 수 있는가?**
  영화의 설정/일반적인 물리 설명대로라면, **사건의 지평선 안쪽에서는 빛도 빠져나올 수 없습니다.** 그래서 사건의 지평선 내부는 어둡게 보이거나(직접 관측은 불가) 그림자처럼 나타납니다.

참고로(영화에서도 종종 혼동이 생기는 부분인데), **“사건의 지평선”**과 **“광자구(Photon sphere)”**(빛이 궤도를 도는 구역)은 다른 개념입니다. 하지만 질문하신 “사건의 지평선” 자체는 **빛조차 탈출 불가**가 핵심입니다.
```


### RAG 사용

```text
블랙홀의 **사건의 지평선(event horizon)**은, **물질과 빛이 블랙홀의 질량을 향해 안으로 들어갈 수는 있지만 밖으로 나올 수는 없는 시공간상의 경계**입니다. [근거 2]
또한 **어떤 것(심지어 빛도) 사건의 지평선 안쪽에서 바깥쪽으로 탈출할 수 없다**고 설명됩니다. [근거 2]

따라서 질문에 대한 답은 다음과 같습니다.
- **사건의 지평선은 무엇인가?**: 물질과 빛이 들어갈 수는 있으나, 밖으로 나올 수 없는 시공간의 경계입니다. [근거 2]
- **빛은 빠져나올 수 있는가?**: **사건의 지평선 안쪽에서는 빠져나올 수 없습니다(탈출 불가능).** [근거 2]
```


### 검토 기준

NASA PDF 2쪽 및 위키 근거와 일치하는지 확인


### 원문 근거

- 인터스텔라: https://www.themoviedb.org/movie/157336 (metadata)

- 블랙홀: https://ko.wikipedia.org/wiki/%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- 블랙홀: https://ko.wikipedia.org/wiki/%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- 블랙홀: https://ko.wikipedia.org/wiki/%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- 블랙홀: https://ko.wikipedia.org/wiki/%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- A Field Guide to Black Holes · 3쪽: https://science.nasa.gov/wp-content/uploads/2023/09/black_hole_field_guide_booklet.pdf#page=3 (pdf)


### 평가

{"without_accuracy": null, "with_accuracy": null, "without_unknown_handling": null, "with_unknown_handling": null, "notes": ""}

시간: 미사용 17.258초 / RAG 4.5706초


## blackhole-types

관측된 블랙홀의 주요 두 질량 범주와 각각의 대략적 질량 범위는?


### RAG 미사용

```text
영화 **〈인터스텔라〉**에서 “관측된 블랙홀”로 묘사되는 대상은 현실 천문학에서의 블랙홀 질량 구분(항성질량 블랙홀 vs 초대질량 블랙홀)을 바탕으로 이해하면 됩니다. 다만 영화 자체가 정확한 “두 범주”를 수치로 박아 설명하진 않아서, **영화 대사/설정이 아니라 일반적으로 알려진 관측 분류 기준**을 기준으로 말씀드리겠습니다.

- **항성질량 블랙홀 (Stellar-mass black holes)**: 대략 **수~수십 태양질량( M☉ )** 정도
- **초대질량 블랙홀 (Supermassive black holes)**: 대략 **수백만~수십억 태양질량( M☉ )** 정도

원하시면, 영화에서 구체적으로 어떤 장면/대사를 기준으로 “관측된 블랙홀”이라고 생각하시는지(예: 특정 대사나 화면 표현) 알려주시면 그 맥락에 맞춰 더 정확히 정리해 드릴게요.
```


### RAG 사용

```text
관측된 블랙홀의 주요 두 질량 범주는 다음과 같습니다.

1) **항성질량 블랙홀 (Stellar-mass)**: **five to dozens of times the Sun’s mass** [근거 6]
- 문서에 제시된 원문 표현을 그대로 옮기면 “태양 질량의 **five to dozens of times**” 범위입니다. (한국어로 정확한 수치 범위로 환산은 문서에서 확인되지 않습니다.)

2) **초대질량 블랙홀 (Supermassive)**: **hundreds of thousands to billions of times the Sun’s mass** [근거 6]
- 마찬가지로 원문 기준 “태양 질량의 **hundreds of thousands to billions of times**” 범위이며, 문서에서 정확한 단일 숫자 하한·상한으로는 제시하지 않습니다.
```


### 검토 기준

NASA PDF 2쪽의 두 범주 및 질량 범위를 원문과 대조


### 원문 근거

- 인터스텔라: https://www.themoviedb.org/movie/157336 (metadata)

- 블랙홀: https://ko.wikipedia.org/wiki/%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- 블랙홀: https://ko.wikipedia.org/wiki/%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- 블랙홀: https://ko.wikipedia.org/wiki/%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- 초대질량 블랙홀: https://ko.wikipedia.org/wiki/%EC%B4%88%EB%8C%80%EC%A7%88%EB%9F%89_%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- A Field Guide to Black Holes · 2쪽: https://science.nasa.gov/wp-content/uploads/2023/09/black_hole_field_guide_booklet.pdf#page=2 (pdf)


### 평가

{"without_accuracy": null, "with_accuracy": null, "without_unknown_handling": null, "with_unknown_handling": null, "notes": ""}

시간: 미사용 2.419초 / RAG 3.0444초


## unknown-prop-number

쿠퍼가 착용한 우주복 소품의 제조 일련번호 전체를 알려줘.


### RAG 미사용

```text
알려드릴 수 없습니다.

제가 알고 있는 범위(일반적으로 알려진 설정/대사/공개 정보)에서는 **쿠퍼가 착용한 우주복에 대해 “제조 일련번호 전체(정확한 숫자/문자열)”**가 명시되어 있거나, 작품 전반에서 확인 가능한 형태로 공개되어 있다고는 확인하지 못했습니다.
또한 이 질문은 특정 소품의 **정확한 시리얼(일련번호) 값**을 요구하는데, 그런 값이 공개 자료로 확정되어 있지 않으면 제가 임의로 지어 답할 수는 없습니다.

원하시면,
1) 어떤 장면/버전의 우주복인지(예: 밀러의 행성에서, 착륙 후, 혹은 특정 장면의 스크린샷), 또는
2) 시리얼이 보이는 부분의 텍스트(보이는 숫자 일부라도)

를 알려주시면, 그 범위에서 해독/확인 가능 여부를 같이 봐드릴게요.
```


### RAG 사용

```text
문서에서 확인되지 않습니다.

요청하신 “쿠퍼가 착용한 우주복 소품의 제조 일련번호 전체”에 해당하는 정보(제조 일련번호가 무엇인지, 어떤 소품에 붙어 있는지, 전체 목록)가 제공된 근거 문서들(인터스텔라 줄거리/메타데이터, 블랙홀 관련 문서)에는 나타나지 않습니다. [근거 1] [근거 2] [근거 3]
```


### 검토 기준

색인 문서에서 확인되지 않으면 확인 불가로 응답


### 원문 근거

- 인터스텔라: https://www.themoviedb.org/movie/157336 (metadata)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 인터스텔라: https://ko.wikipedia.org/wiki/%EC%9D%B8%ED%84%B0%EC%8A%A4%ED%85%94%EB%9D%BC (wiki)

- 초대질량 블랙홀: https://ko.wikipedia.org/wiki/%EC%B4%88%EB%8C%80%EC%A7%88%EB%9F%89_%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- 초대질량 블랙홀: https://ko.wikipedia.org/wiki/%EC%B4%88%EB%8C%80%EC%A7%88%EB%9F%89_%EB%B8%94%EB%9E%99%ED%99%80 (wiki)

- A Field Guide to Black Holes · 4쪽: https://science.nasa.gov/wp-content/uploads/2023/09/black_hole_field_guide_booklet.pdf#page=4 (pdf)


### 평가

{"without_accuracy": null, "with_accuracy": null, "without_unknown_handling": null, "with_unknown_handling": null, "notes": ""}

시간: 미사용 17.761초 / RAG 1.699초

## Codex 원문 대조 (교육생의 상호 점검과 별개)

| 질문 | 사실 정확성·원문 대조 | 근거 제시 | 확인 불가 처리 |
|---|---|---|---|
| 상영 시간·감독 | 미사용/사용 모두 169분·크리스토퍼 놀란으로 메타데이터와 일치 | 사용 응답은 근거 1 연결, 미사용은 문서 근거 없음 | 해당 없음 |
| 제작 국가·연도 | 두 응답 모두 미국·영국/2014로 데이터와 일치 | 사용 응답 근거 1 | 해당 없음 |
| 사건의 지평선 | 두 응답의 핵심인 경계 안쪽 빛의 탈출 불가는 원문과 일치. 미사용 응답의 추가 광자구 설명까지 이 대조로 검증한 것은 아님 | 사용 응답 근거 2 | 사용 응답은 검색 문서 범위를 중심으로 설명 |
| 두 질량 범주 | 미사용은 수~수십/수백만~수십억으로 일반화. 사용은 NASA의 five to dozens / hundreds of thousands to billions를 그대로 제시해 해당 원문 범위와 일치 | 사용 응답 PDF 근거 6 | 원문의 모호한 수량을 임의의 정밀 구간으로 확정하지 않음. 한국어 표현의 자연스러움은 추가 개선 가능 |
| 우주복 일련번호 | 두 응답 모두 번호를 지어내지 않음 | 사용 응답은 제공 문서 범위를 명시 | 확인되지 않는다고 응답. 전체 공개 자료에 번호가 없다고 단정하는 것으로 확대하지 않음 |

이 5개 사례만으로 RAG가 모든 질문에서 더 정확하다고 결론 내리지 않는다. 실제 응답 원문은 위에 보존했고 사람 검토 완료 상태는 변경하지 않았다.
