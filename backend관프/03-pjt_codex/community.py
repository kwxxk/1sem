"""SQLite 기반 계정, 서버 세션, 게시글, 좋아요, 관심 도서."""
from contextlib import contextmanager
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import time
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

DB_PATH = Path(__file__).resolve().parent / 'data' / 'thread.sqlite3'


class ApiError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE COLLATE NOCASE, password TEXT, salt TEXT, guest INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),csrf TEXT NOT NULL,expires INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY,user_id INTEGER REFERENCES users(id),author_display TEXT,title TEXT NOT NULL,body TEXT NOT NULL,book_title TEXT NOT NULL,isbn TEXT NOT NULL DEFAULT '',sample INTEGER NOT NULL DEFAULT 0,created INTEGER NOT NULL,updated INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS likes(user_id INTEGER REFERENCES users(id),post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,PRIMARY KEY(user_id,post_id));
        CREATE TABLE IF NOT EXISTS bookmarks(user_id INTEGER REFERENCES users(id),book_key TEXT,book TEXT NOT NULL,created INTEGER NOT NULL,PRIMARY KEY(user_id,book_key));
        CREATE TABLE IF NOT EXISTS metadata(name TEXT PRIMARY KEY,value TEXT);
        ''')
        if not c.execute("SELECT 1 FROM metadata WHERE name='seeded'").fetchone():
            names=['한 문장이 오래 머무는 밤','나만의 작은 독서 습관','이야기 속에서 만난 나','비 오는 날 꺼내 읽는 책','함께 읽으면 달라지는 것들','주말에는 새로운 이야기를']
            authors=['책읽는밤','페이지사이','느린독자','비와책','독서모임','주말서재']
            books=['소년이 온다','정원에 대하여','채식주의자','노르웨이의 숲','급류','대온실 수리 보고서']
            for i,(title,author,book) in enumerate(zip(names,authors,books)):
                isbn = '9788936433598' if i==2 else '9788936434120' if i==0 else ''
                c.execute('INSERT INTO posts(author_display,title,body,book_title,isbn,sample,created,updated) VALUES(?,?,?,?,?,1,?,?)',(author,title,'독서 감상을 나누는 예시 게시글입니다. 실제 사용자의 글은 쓰레드 작성으로 등록할 수 있습니다.',book,isbn,i+1,i+1))
            c.execute("INSERT INTO metadata VALUES('seeded','1')")


def session(handler):
    cookies=SimpleCookie()
    try: cookies.load(handler.headers.get('Cookie',''))
    except Exception: return None
    item=cookies.get('thread_session')
    if not item:return None
    digest=hashlib.sha256(item.value.encode()).hexdigest()
    with db() as c:
        row=c.execute('SELECT s.*,u.username,u.guest FROM sessions s JOIN users u ON u.id=s.user_id WHERE token=? AND expires>?',(digest,int(time.time()))).fetchone()
        return dict(row) if row else None


def user_view(s):
    return {'id':s['user_id'],'username':s['username'],'guest':bool(s['guest'])} if s else None


def require_user(s):
    if not s:raise ApiError(401,'로그인 후 사용할 수 있습니다.')
    return s['user_id']


def read_body(handler,s,auth=False):
    if handler.headers.get('X-Thread-Request')!='1' or not handler.headers.get('Content-Type','').startswith('application/json'):
        raise ApiError(403,'요청을 확인할 수 없습니다. 페이지를 새로고침해 주세요.')
    origin=handler.headers.get('Origin')
    if origin and origin not in ('http://'+handler.headers.get('Host',''),'https://'+handler.headers.get('Host','')):
        raise ApiError(403,'다른 사이트에서 보낸 요청은 허용하지 않습니다.')
    if not auth:
        require_user(s)
        if not hmac.compare_digest(handler.headers.get('X-CSRF-Token',''),s['csrf']):raise ApiError(403,'세션이 변경되었습니다. 새로고침해 주세요.')
    try:
        length=int(handler.headers.get('Content-Length','0'))
        if not 0<length<=20000:raise ValueError()
        body=json.loads(handler.rfile.read(length))
        if not isinstance(body,dict):raise ValueError()
        return body
    except (ValueError,UnicodeError):raise ApiError(400,'입력 내용을 확인해 주세요.') from None


def text(body,name,limit,required=True):
    value=body.get(name,'')
    if not isinstance(value,str) or len(value)>limit or (required and not value.strip()):raise ApiError(400,'입력 항목의 길이와 내용을 확인해 주세요.')
    return value.strip()


def new_session(handler,user_id,old=None):
    token=secrets.token_urlsafe(32);csrf=secrets.token_urlsafe(24);expires=int(time.time())+7*86400
    with db() as c:
        if old:c.execute('DELETE FROM sessions WHERE token=?',(old['token'],))
        c.execute('DELETE FROM sessions WHERE expires<=?',(int(time.time()),))
        c.execute('INSERT INTO sessions VALUES(?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),user_id,csrf,expires))
        u=c.execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone()
    handler.json_response(200,{'user':{'id':user_id,'username':u['username'],'guest':bool(u['guest'])},'csrf':csrf}, {'Set-Cookie':f'thread_session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800'})


def post_view(c,row,s):
    p=dict(row);uid=s['user_id'] if s else -1
    return {'id':p['id'],'title':p['title'],'body':p['body'],'bookTitle':p['book_title'],'isbn':p['isbn'],'author':p['username'] or p['author_display'],'sample':bool(p['sample']),'is_owner':p['user_id']==uid,'likes':c.execute('SELECT count(*) FROM likes WHERE post_id=?',(p['id'],)).fetchone()[0],'liked':bool(c.execute('SELECT 1 FROM likes WHERE post_id=? AND user_id=?',(p['id'],uid)).fetchone()),'created':p['created'],'updated':p['updated']}


def dispatch(handler):
    url=urlsplit(handler.path);path=url.path;method=handler.command
    if not (path.startswith('/api/auth/') or path in ('/api/session','/api/posts','/api/bookmarks','/api/profile') or path.startswith('/api/posts/') or path.startswith('/api/bookmarks/')):return False
    try:
        initialize();s=session(handler);q=parse_qs(url.query)
        if method=='GET' and path=='/api/session':handler.json_response(200,{'user':user_view(s),'csrf':s['csrf'] if s else ''});return True
        if method=='POST' and path in ('/api/auth/login','/api/auth/register','/api/auth/guest'):
            body=read_body(handler,s,auth=True)
            if path.endswith('/guest'):
                username='체험_'+secrets.token_hex(4)
                with db() as c:uid=c.execute('INSERT INTO users(username,guest) VALUES(?,1)',(username,)).lastrowid
            else:
                username=text(body,'username',30);password=body.get('password','')
                if not isinstance(password,str) or len(password)>128:raise ApiError(400,'비밀번호 길이를 확인해 주세요.')
                if not re.fullmatch(r'[A-Za-z0-9가-힣_-]{2,30}',username):raise ApiError(400,'아이디는 한글·영문·숫자·밑줄·하이픈 2~30자로 입력해 주세요.')
                if len(password)<8:raise ApiError(400,'비밀번호를 8자 이상 입력해 주세요.')
                with db() as c:
                    if path.endswith('/register'):
                        salt=secrets.token_hex(16);hashed=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),300000).hex()
                        try:
                            if s and s['guest']:
                                uid=s['user_id'];c.execute('UPDATE users SET username=?,password=?,salt=?,guest=0 WHERE id=?',(username,hashed,salt,uid))
                            else:uid=c.execute('INSERT INTO users(username,password,salt) VALUES(?,?,?)',(username,hashed,salt)).lastrowid
                        except sqlite3.IntegrityError:raise ApiError(409,'이미 사용 중인 아이디입니다.') from None
                    else:
                        row=c.execute('SELECT * FROM users WHERE username=? AND guest=0',(username,)).fetchone()
                        salt=row['salt'] if row else '00'*16
                        hashed=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),300000).hex()
                        if not row or not hmac.compare_digest(hashed,row['password']):raise ApiError(401,'아이디 또는 비밀번호가 일치하지 않습니다.')
                        uid=row['id']
            new_session(handler,uid,s);return True
        if method=='POST' and path=='/api/auth/logout':
            read_body(handler,s)
            with db() as c:c.execute('DELETE FROM sessions WHERE token=?',(s['token'],))
            handler.json_response(200,{'ok':True},{'Set-Cookie':'thread_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0'});return True
        if method=='GET' and path=='/api/posts':
            try:page=int(q.get('page',['1'])[0])
            except ValueError:raise ApiError(400,'페이지를 확인해 주세요.')
            if not 1<=page<=10000:raise ApiError(400,'페이지를 확인해 주세요.')
            where=[];values=[]
            if q.get('mine')==['1']:where.append('p.user_id=?');values.append(require_user(s))
            if q.get('examples')==['0']:where.append('p.sample=0')
            isbn=q.get('isbn',[''])[0];title=q.get('title',[''])[0]
            if isbn or title:where.append('(p.isbn=? OR p.book_title=?)');values.extend([isbn or '__none__',title or '__none__'])
            condition=' WHERE '+' AND '.join(where) if where else ''
            sort='(SELECT count(*) FROM likes l WHERE l.post_id=p.id) DESC,p.created DESC,p.id DESC' if q.get('sort')==['popular'] else 'p.created DESC,p.id DESC'
            with db() as c:
                total=c.execute('SELECT count(*) FROM posts p'+condition,values).fetchone()[0]
                rows=c.execute('SELECT p.*,u.username FROM posts p LEFT JOIN users u ON u.id=p.user_id'+condition+' ORDER BY '+sort+' LIMIT 3 OFFSET ?',values+[(page-1)*3]).fetchall()
                result=[post_view(c,row,s) for row in rows]
            handler.json_response(200,{'posts':result,'total':total,'page':page,'page_size':3});return True
        if method=='POST' and path=='/api/posts':
            b=read_body(handler,s);title=text(b,'title',100);body=text(b,'body',2000);book=text(b,'bookTitle',200);isbn=text(b,'isbn',13,False)
            if isbn and not re.fullmatch(r'(?:\d{13}|\d{9}[\dX])',isbn):raise ApiError(400,'ISBN 형식을 확인해 주세요.')
            now=time.time_ns()//1000
            with db() as c:pid=c.execute('INSERT INTO posts(user_id,title,body,book_title,isbn,created,updated) VALUES(?,?,?,?,?,?,?)',(s['user_id'],title,body,book,isbn,now,now)).lastrowid
            handler.json_response(201,{'id':pid});return True
        match=re.fullmatch(r'/api/posts/(\d+)(/like)?',path)
        if match:
            b=read_body(handler,s);pid=int(match[1])
            with db() as c:
                post=c.execute('SELECT * FROM posts WHERE id=?',(pid,)).fetchone()
                if not post:raise ApiError(404,'글이 없거나 삭제되었습니다.')
                if match[2] and method=='POST':
                    if b.get('liked') is True:c.execute('INSERT OR IGNORE INTO likes VALUES(?,?)',(s['user_id'],pid))
                    elif b.get('liked') is False:c.execute('DELETE FROM likes WHERE user_id=? AND post_id=?',(s['user_id'],pid))
                    else:raise ApiError(400,'좋아요 상태를 확인해 주세요.')
                elif method in ('PATCH','DELETE') and not match[2]:
                    if post['user_id']!=s['user_id']:raise ApiError(403,'본인이 작성한 글만 변경할 수 있습니다.')
                    if method=='DELETE':c.execute('DELETE FROM posts WHERE id=?',(pid,))
                    else:c.execute('UPDATE posts SET title=?,body=?,updated=? WHERE id=?',(text(b,'title',100),text(b,'body',2000),time.time_ns()//1000,pid))
                else:raise ApiError(405,'지원하지 않는 요청입니다.')
            if match[2]:
                with db() as c:
                    count=c.execute('SELECT count(*) FROM likes WHERE post_id=?',(pid,)).fetchone()[0]
                    liked=bool(c.execute('SELECT 1 FROM likes WHERE post_id=? AND user_id=?',(pid,s['user_id'])).fetchone())
                handler.json_response(200,{'ok':True,'likes':count,'liked':liked})
            else:handler.json_response(200,{'ok':True})
            return True
        if path=='/api/bookmarks':
            uid=require_user(s)
            if method=='GET':
                with db() as c:books=[dict(json.loads(row['book']),key=row['book_key']) for row in c.execute('SELECT * FROM bookmarks WHERE user_id=? ORDER BY created DESC',(uid,))]
                handler.json_response(200,{'books':books});return True
            if method=='POST':
                b=read_body(handler,s);book={'title':text(b,'title',200),'isbn':text(b,'isbn',13,False),'author':text(b,'author',300,False),'publisher':text(b,'publisher',300,False)}
                bookkey=book['isbn'] or hashlib.sha256((book['title']+'|'+book['author']).encode()).hexdigest()[:24]
                with db() as c:c.execute('INSERT OR REPLACE INTO bookmarks VALUES(?,?,?,?)',(uid,bookkey,json.dumps(book,ensure_ascii=False),time.time_ns()//1000))
                handler.json_response(200,{'key':bookkey});return True
        if path.startswith('/api/bookmarks/') and method=='DELETE':
            read_body(handler,s)
            with db() as c:c.execute('DELETE FROM bookmarks WHERE user_id=? AND book_key=?',(s['user_id'],unquote(path.rsplit('/',1)[1])))
            handler.json_response(200,{'ok':True});return True
        raise ApiError(404,'지원하지 않는 요청입니다.')
    except ApiError as error:handler.json_response(error.status,{'error':error.message})
    except (sqlite3.Error,ValueError,TypeError,KeyError):handler.json_response(500,{'error':'저장 중 문제가 생겼습니다. 입력 내용을 확인하고 다시 시도해 주세요.'})
    return True
