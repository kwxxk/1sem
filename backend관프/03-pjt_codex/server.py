"""python server.py → http://127.0.0.1:8000"""
import argparse
import json
import mimetypes
import re
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import community
from loan_client import libraries

from nl_isbn_client import LibraryError, find_by_isbn, normalize_book, search_books

ROOT = Path(__file__).resolve().parent
CACHE = {}
CACHE_LOCK = threading.Lock()


def query_books(field, query, page):
    cache_key = (field, query, page)
    with CACHE_LOCK:
        cached = CACHE.get(cache_key)
        if cached and time.monotonic() - cached[0] < 300:
            return cached[1]
    if field == 'isbn':
        doc = find_by_isbn(query)
        books = [normalize_book(doc)] if doc else []
        total = len(books)
    else:
        data = search_books(page_no=page, page_size=12, **{field:query})
        books = [normalize_book(doc) for doc in data['docs'] if isinstance(doc, dict)]
        try:
            total = max(0, int(str(data.get('TOTAL_COUNT', 0)).replace(',', '')))
        except ValueError:
            raise LibraryError('도서 API의 검색 건수를 읽지 못했습니다.') from None
    result = dict(books=books, total=total, page=page, page_size=12,
                  source='국립중앙도서관 ISBN 서지정보')
    with CACHE_LOCK:
        if len(CACHE) >= 128:
            CACHE.pop(next(iter(CACHE)))
        CACHE[cache_key] = (time.monotonic(), result)
    return result


class Handler(SimpleHTTPRequestHandler):
    def json_response(self, status, data, headers=None):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        for name,value in (headers or {}).items():self.send_header(name,value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if community.dispatch(self):return
        url = urlsplit(self.path)
        if url.path == '/api/libraries':
            q=parse_qs(url.query)
            try:
                page=int(q.get('page',['1'])[0])
                if not 1<=page<=10000:raise ValueError('페이지를 확인해 주세요.')
                return self.json_response(200,libraries(q.get('isbn',[''])[0],q.get('region',[''])[0],page))
            except ValueError as error:return self.json_response(400,{'error':str(error)})
            except Exception:return self.json_response(502,{'error':'도서관 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.'})
        if url.path == '/api/books':
            params = parse_qs(url.query)
            field = params.get('field', ['title'])[0]
            query = params.get('q', [''])[0].strip()
            try:
                page = int(params.get('page', ['1'])[0])
            except ValueError:
                return self.json_response(400, {'error':'페이지 번호가 올바르지 않습니다.'})
            if field not in ('title', 'author', 'isbn') or not 1 <= page <= 10000 or not 1 <= len(query) <= 100:
                return self.json_response(400, {'error':'검색 조건을 확인해 주세요.'})
            if field == 'isbn':
                query = re.sub(r'[\s-]', '', query).upper()
                if not re.fullmatch(r'(?:\d{13}|\d{9}[\dX])', query):
                    return self.json_response(400, {'error':'ISBN은 하이픈을 제외한 10자리 또는 13자리로 입력해 주세요.'})
            try:
                return self.json_response(200, query_books(field, query, page))
            except LibraryError as error:
                return self.json_response(502, {'error':str(error)})
        if url.path.startswith('/api/'):
            return self.json_response(404, {'error':'지원하지 않는 요청입니다.'})
        return super().do_GET()

    def do_POST(self):
        if not community.dispatch(self):self.json_response(404,{'error':'지원하지 않는 요청입니다.'})

    do_PATCH=do_POST
    do_DELETE=do_POST

    def send_head(self):
        # .env / 소스코드 / Git / 테스트는 정적 파일 서버에서 공개하지 않습니다.
        path = unquote(urlsplit(self.path).path)
        parts = Path(path.replace('\\', '/')).parts
        target = Path(self.translate_path(self.path)).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            self.send_error(404)
            return None
        if any(part.startswith('.') for part in parts) or target.suffix.lower() not in {'.html','.css','.js','.jpeg','.jpg','.png','.webp','.svg','.ico','.ttf','.woff','.woff2'}:
            if path == '/':
                self.path = '/index.html'
            else:
                self.send_error(404)
                return None
        if target.is_dir() and path != '/':
            self.send_error(404)
            return None
        return super().send_head()

    def log_message(self, format, *args):
        pass  # API 쿼리와 키를 로그에 출력하지 않습니다.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--open', action='store_true', help='브라우저 열기')
    args = parser.parse_args()
    mimetypes.add_type('text/javascript', '.js')
    community.initialize()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(ROOT)))
    print(f'ThRead: http://127.0.0.1:{args.port}/06-main.html', flush=True)
    print('종료하려면 Ctrl+C를 누르세요.', flush=True)
    if args.open:
        import webbrowser
        threading.Timer(0.7, lambda: webbrowser.open(f'http://127.0.0.1:{args.port}/06-main.html')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
