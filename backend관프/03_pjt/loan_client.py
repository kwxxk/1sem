"""정보나루 키가 설정된 경우에만 소장 도서관과 전일 대출 상태 조회."""
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


def setting(name):
    if os.environ.get(name):return os.environ[name].strip()
    p=Path(__file__).resolve().with_name('.env')
    if p.exists():
        for line in p.read_text(encoding='utf-8-sig').splitlines():
            k,sep,v=line.partition('=')
            if sep and k.strip()==name:return v.strip().strip('\"\'')
    return ''


class LibraryAccessError(Exception):
    pass


def libraries(isbn,region,page=1):
    key=setting('DATA4LIBRARY_KEY')
    if not key:return {'configured':False,'libraries':[],'total':0,'message':'대출 정보 서비스가 아직 연결되지 않았습니다. 공식 자료 검색에서 확인해 주세요.'}
    if not re.fullmatch(r'\d{13}',isbn) or not re.fullmatch(r'\d{2}',region):raise ValueError('13자리 ISBN과 지역을 선택해 주세요.')
    def call(endpoint,**params):
        params.update(authKey=key,format='json')
        with urlopen('https://data4library.kr/api/'+endpoint+'?'+urlencode(params),timeout=8) as response:data=json.load(response)
        result=data.get('response',{})
        if not isinstance(result,dict):raise ValueError('도서관 서비스 응답을 확인하지 못했습니다.')
        if result.get('error'):raise LibraryAccessError(str(result.get('errCode','')))
        return result
    try:data=call('libSrchByBook',isbn=isbn,region=region,pageNo=page,pageSize=5)
    except LibraryAccessError as error:
        pending=str(error)=='vitalizationErr'
        return {'configured':True,'approved':False,'status':'approval_pending' if pending else 'api_error','libraries':[],'total':0,'message':'정보나루 인증키가 아직 활성화되지 않았습니다. 승인 후 다시 조회해 주세요.' if pending else '도서관 서비스에서 요청을 처리하지 못했습니다. 인증 상태를 확인해 주세요.'}
    def normalize(item):
        lib=item.get('lib',{})
        result={name:str(lib.get(source,'') or '') for name,source in [('code','libCode'),('name','libName'),('address','address'),('tel','tel'),('homepage','homepage')]}
        result.update(has_book=None,available=None)
        try:
            status=call('bookExist',libCode=result['code'],isbn13=isbn).get('result',{})
            result['has_book']=status.get('hasBook')=='Y' if status.get('hasBook') in ('Y','N') else None
            result['available']=status.get('loanAvailable')=='Y' if status.get('loanAvailable') in ('Y','N') else None
        except Exception:pass
        return result
    with ThreadPoolExecutor(max_workers=5) as pool:items=list(pool.map(normalize,data.get('libs',[])))
    return {'configured':True,'libraries':items,'total':int(data.get('numFound',0)),'page':page,'page_size':5,'message':'정보나루 제공 대출 상태는 전일 기준입니다. 방문 전 도서관에 확인해 주세요.'}
