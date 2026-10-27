"""국립중앙도서관 ISBN 서지정보 클라이언트. 키는 서버에서만 읽습니다."""
import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen

BASE_URL = 'https://www.nl.go.kr/seoji/SearchApi.do'


class LibraryError(Exception):
    pass


def load_key():
    key = os.environ.get('NL_CERT_KEY', '').strip()
    if key:
        return key
    env = Path(__file__).resolve().with_name('.env')
    if env.exists():
        for line in env.read_text(encoding='utf-8-sig').splitlines():
            name, separator, value = line.partition('=')
            if separator and name.strip() == 'NL_CERT_KEY':
                return value.strip().strip('\"\'')
    raise LibraryError('서버에 국립중앙도서관 API 키를 설정해 주세요.')


def search_books(page_no=1, page_size=12, **filters):
    # 브라우저에서 전달한 임의의 파라미터로 인증키나 접속 주소를 바꿀 수 없습니다.
    allowed = {'title', 'author', 'isbn', 'sort', 'order_by'}
    params = {name: value for name, value in filters.items() if name in allowed}
    params.update(cert_key=load_key(), result_style='json', page_no=page_no, page_size=page_size)
    try:
        with urlopen(BASE_URL + '?' + urlencode(params), timeout=15) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError):
        # HTTP 예외 문자열에는 인증키가 포함된 URL이 들어갈 수 있습니다.
        raise LibraryError('국립중앙도서관에 연결하지 못했습니다. 잠시 후 다시 검색해 주세요.') from None
    except (ValueError, UnicodeError):
        raise LibraryError('국립중앙도서관 응답을 읽지 못했습니다.') from None
    if not isinstance(data, dict) or not isinstance(data.get('docs'), list):
        raise LibraryError('도서 API가 정상적인 목록을 반환하지 않았습니다. 인증키의 ISBN 서지정보 이용 승인을 확인해 주세요.')
    return data


def clean(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def normalize_book(doc):
    """사용하는 필드만 반환하고 HTML을 실행하거나 임의 URL을 프록시하지 않습니다."""
    fields = {'title':'TITLE', 'author':'AUTHOR', 'publisher':'PUBLISHER',
              'isbn':'EA_ISBN', 'publish_date':'PUBLISH_PREDATE', 'price':'PRE_PRICE',
              'pages':'PAGE', 'form':'FORM', 'subject':'SUBJECT', 'edition':'EDITION_STMT'}
    book = {name: clean(doc.get(api_name)) for name, api_name in fields.items()}
    cover = clean(doc.get('TITLE_URL'))
    book['cover'] = cover if urlsplit(cover).scheme in ('http', 'https') else ''
    return book


def find_by_isbn(isbn):
    isbn = re.sub(r'[\s-]', '', isbn).upper()
    data = search_books(page_size=100, isbn=isbn)
    for doc in data['docs']:
        if re.sub(r'[\s-]', '', clean(doc.get('EA_ISBN'))).upper() == isbn:
            return doc
    return None
