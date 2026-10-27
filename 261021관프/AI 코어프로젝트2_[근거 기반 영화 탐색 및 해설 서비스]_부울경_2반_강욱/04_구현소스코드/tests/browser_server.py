"""브라우저 회귀 테스트 전용 서버. 제품 실행은 serve.py를 사용한다. 실제 GMS를 호출하지 않는다."""
from dataclasses import replace
from pathlib import Path
import json
import os
import sys

sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
import test_project as fixtures
from movielab.preparation.documents import write_json
from movielab.service import Service
from movielab.webapi.app import create_app


def build_test_app():
    fixture=fixtures.ProjectTests('test_metadata_idempotent')
    fixture.setUp()
    fixture.movies[0].update(movie_id='157336',title='인터스텔라',year=2014,runtime=169,genres=['SF','드라마'],
                             overview='브라우저 회귀 테스트용 영화 데이터입니다. 실제 모델의 답변 품질 검증과 구분합니다.')
    fixture.movies[1].update(title='테스트 영화 B')
    write_json(fixture.settings.movies_path,fixture.movies)
    write_json(fixture.settings.wiki_bundle_path/'157336_인터스텔라.json',{
        **fixture.doc,'movie_id':'157336','title':'인터스텔라','source':'테스트 문서'})
    fixture.models.text=lambda *_:'테스트용 응답입니다. 실제 GMS의 답변이 아닙니다. [근거 1]'
    fixture.store.index_items(fixture.movies)
    local=object.__new__(Service)
    local.settings,local.models,local.store,local.domain=fixture.settings,fixture.models,fixture.store,fixture.domain
    local.collector=fixture.domain.create_collector(local.settings,local.models,local.store)
    def factory(settings):
        local.settings=settings
        local.store.settings=settings
        return local
    os.environ['GMS_KEY']='TEST-ONLY-BROWSER-FIXTURE'
    return create_app(fixture.settings,factory),fixture


if __name__=='__main__':
    import uvicorn
    app,fixture=build_test_app()
    try:
        uvicorn.run(app,host='127.0.0.1',port=8766,log_level='warning',access_log=False)
    finally:
        fixture.tearDown()
