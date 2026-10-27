import os

import requests

BASE_URL = 'https://www.nl.go.kr/seoji/SearchApi.do'
CERT_KEY = os.environ.get('NL_CERT_KEY')  # 발급받은 인증키


def search_books(page_no=1, page_size=10, **filters):
    params = {
        'cert_key': CERT_KEY,  # 필수
        'result_style': 'json',  # 필수: json 또는 xml
        'page_no': page_no,  # 필수: 1부터 시작
        'page_size': page_size,  # 필수: 쪽당 출력건수
        **filters,  # 선택: isbn, title, author, publisher, sort, order_by 등
    }
    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def find_by_isbn(isbn):
    isbn = isbn.replace('-', '')
    data = search_books(isbn=isbn)
    # isbn은 앞부분 일치(우절단) 검색이라 완전히 같은 ISBN만 고른다
    for doc in data.get('docs', []):
        if doc.get('EA_ISBN') == isbn:
            return doc
    return None


if __name__ == '__main__':
    # 1) ISBN으로 조회
    book = find_by_isbn('978-89-7199-855-7')
    if book:
        print(book['TITLE'], book['AUTHOR'], book['PUBLISHER'])

    # 2) 제목 검색 + 출판예정일 최신순
    data = search_books(title='파이썬', sort='PUBLISH_PREDATE', order_by='DESC')
    print('전체 건수:', data.get('TOTAL_COUNT'))
    # [주의] 응답에서 도서 목록이 담긴 키 이름이 docs가 아닐 수 있으니 확인 필요
    for doc in data.get('docs', []):
        print('-', doc['TITLE'], doc['EA_ISBN'])
