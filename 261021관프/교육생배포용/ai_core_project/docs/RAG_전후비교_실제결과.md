# RAG 사용 전후 비교

실행 모드: live / 모델: gpt-5.4-nano

질문 수: 5 / 응답 상태: responses_collected / 사람 검토 완료: False

자동 인용 표식은 사실 정확성을 증명하지 않습니다.


## interstellar-runtime

제공된 영화 데이터에서 인터스텔라의 상영 시간은 몇 분이며 감독은 누구인가?


### RAG 미사용

```text
제가 가진 정보(일반적으로 알려진 제작 정보) 기준으로 **『인터스텔라』(Interstellar)**의 상영 시간은 **약 169분**이고, **감독은 크리스토퍼 놀란(Christopher Nolan)**입니다.
```


### RAG 사용

```text
인터스텔라의 상영시간은 **169분**이며, 감독은 **크리스토퍼 놀란**입니다. [근거 1]
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

시간: 미사용 0.963초 / RAG 1.5172초


## interstellar-countries

인터스텔라의 제작 국가와 개봉 연도는 무엇인가? 제공된 데이터 기준으로 답해줘.


### RAG 미사용

```text
제공된 데이터(검색 문서 등) 없이, 제가 알고 있는 일반 정보에 따르면 **《인터스텔라(Interstellar)》의 제작 국가는 미국과 영국(미국-영국 합작)**이고, **개봉 연도는 2014년**입니다.
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

시간: 미사용 1.236초 / RAG 1.1372초


## blackhole-horizon

블랙홀의 사건의 지평선은 무엇이며 빛이 빠져나올 수 있는가?


### RAG 미사용

```text
《인터스텔라》에서(그리고 물리적으로도) **사건의 지평선(event horizon)** 은 **블랙홀의 중력 때문에 어떤 것도(심지어 빛도) 바깥으로 빠져나올 수 없게 되는 경계**를 뜻합니다. 즉, 그 안쪽에서는 모든 경로가 블랙홀의 중심(특이점) 쪽으로 “빨려 들어가게” 되어 탈출이 불가능합니다.

### 빛이 빠져나올 수 있는가?
- **사건의 지평선 ‘바깥’에서는** 빛은 탈출할 수 있습니다.  
- **사건의 지평선 ‘안’으로 들어간 빛은** 다시 밖으로 나오지 못합니다.  
- 사건의 지평선은 빛의 탈출 가능 여부를 갈라놓는 “경계”라고 이해하면 됩니다.

원하시면, 《인터스텔라》에서 등장하는 설정(예: 웜홀, 블랙홀 근처의 시간 지연/조석력 등)과 사건의 지평선이 장면 전개에 어떻게 연결되는지도 설명해 드릴게요.
```


### RAG 사용

```text
블랙홀의 **사건의 지평선(event horizon)**은 **물질과 빛이 블랙홀의 질량(방향)으로는 안으로 들어갈 수는 있지만, 밖으로는 나올 수 없는 시공간상의 경계**입니다. [근거 2] 또한 “그 무엇도(심지어 빛마저) 사건의 지평선 안쪽에서 바깥쪽으로 탈출할 수 없다”고 설명됩니다. [근거 2]

따라서 **빛은 사건의 지평선을 빠져나올 수 없습니다.** 사건의 지평선에서는 “블랙홀 바깥으로 향하는 경로가 존재할 수 없게 된다”는 방식으로 탈출 불가능성이 묘사됩니다. [근거 2]
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

시간: 미사용 1.999초 / RAG 1.817초


## blackhole-types

관측된 블랙홀의 주요 두 질량 범주와 각각의 대략적 질량 범위는?


### RAG 미사용

```text
영화 **〈인터스텔라〉** 안에서 “관측된 블랙홀”이라고 단정해 특정 장면의 블랙홀을 콕 집어 설명하진 않지만, 작품에서 언급되는 블랙홀은 대체로 **슈퍼매시브 블랙홀**과 **항성 질량(또는 중간 질량) 블랙홀** 계열로 나뉘어 설명됩니다. (다만 영화가 “관측된 블랙홀의 두 가지 질량 범주”를 교과서처럼 정확히 구분해 수치로 제시하는 방식은 아닙니다.)

그래도 일반적으로(그리고 영화에서 통용되는 통념대로) 주요 두 범주와 대략적 질량 범위는 다음처럼 정리할 수 있습니다:

1) **항성 질량(또는 항성 붕괴로 생기는) 블랙홀**
- 대략적 질량 범위: **약 3~수십 태양질량**(보통 수~수십 M☉ 범위를 많이 말함)

2) **슈퍼매시브 블랙홀**
- 대략적 질량 범위: **수백만~수십억 태양질량**(예: 10⁶~10⁹ M☉)

※ 정확히 “인터스텔라에서 관측된 블랙홀”을 말하는지, 혹은 “현실 천문학에서 관측되는 블랙홀의 대표적인 두 범주”를 묻는지에 따라 답의 표현이 달라질 수 있어요.  
원하시면 **어느 장면/대사(예: ‘밀러의 행성’, ‘가르강튀아’ 관련 맥락 등)**을 기준으로 한 질문인지 알려주시면 그 맥락에 맞춰 더 정확히 답해드릴게요.
```


### RAG 사용

```text
관측된(문서에서 “관측된”을 명시적으로 한정하지는 않음) 블랙홀은 “두 가지 큰 질량 범주”로 분류된다고 제시됩니다. [근거 6]

1) **항성질량( Stellar-mass ) 블랙홀**: **5~dozens(‘수십’)** 배 태양질량 [근거 6]  
2) **초대질량( Supermassive ) 블랙홀**: **hundreds of thousands(‘수십만’)** ~ **billions(‘수십억’)** 배 태양질량 [근거 6]

※ 문서에는 “관측된 블랙홀”의 주요 두 질량 범주가 위와 같이 제시되지만, “각각의 대략적 질량 범위”를 더 구체적인 숫자(예: 10^x 단위의 정확한 범위)로 환산해 확정하라는 정보는 제공되지 않습니다(‘dozens’, ‘hundreds of thousands’, ‘billions’는 원문 표기 그대로만 확인됨). [근거 6]
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

시간: 미사용 3.06초 / RAG 2.5783초


## unknown-prop-number

쿠퍼가 착용한 우주복 소품의 제조 일련번호 전체를 알려줘.


### RAG 미사용

```text
죄송하지만, 영화 **〈인터스텔라〉**에서 **쿠퍼가 착용한 우주복의 “제조 일련번호 전체”**가 정확히 무엇인지(그리고 그 번호가 전편에서 어떤 장면/소품에 어떤 형태로 표기되는지)를 **확인 가능한 범위의 정보로 확정해 드릴 수 없습니다.**  

원하시면,
- 우주복이 나온 **장면(예: 어떤 행성/어느 시점/캡처 여부)**, 또는  
- 우주복 소품에 표기된 번호가 **보이는 화면을 캡처**해서  
주시면, 그 텍스트가 무엇인지 **읽어서** 정리해 드릴게요.
```


### RAG 사용

```text
문서에서 확인되지 않습니다.  

쿠퍼가 착용한 우주복의 **소품(부품) 제조 일련번호 전체**에 대한 정보는 제공된 근거 문서(인터스텔라 줄거리/관련 설명)들에 포함되어 있지 않습니다.
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

시간: 미사용 1.603초 / RAG 1.2036초