"""심화·비기능 자동 검증. 실제 GMS 호출과 실제 품질 평가를 대신하지 않는다."""
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
import os
import shutil
import sys
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_project as base_tests
from movielab.config import UserError, ROOT
from movielab.service import Service
from movielab.retrieval import mmr_indices
from movielab.operations import CachedEmbeddings, public_error, register_prompt, redact
from movielab.preparation.documents import write_json, WikiAPI
from movielab.preparation.pdf_documents import pages_for_item, index_for_item
from movielab.evaluation import run_evaluation, review_evaluation, markdown_report, evaluation_path
from movielab.webapi.app import create_app
from movielab.webapi.jobs import Jobs
from fastapi.testclient import TestClient


class AdvancedTests(unittest.TestCase):
    setUp = base_tests.ProjectTests.setUp
    tearDown = base_tests.ProjectTests.tearDown

    def service(self):
        local = object.__new__(Service)
        local.settings, local.store, local.models, local.domain = self.settings, self.store, self.models, self.domain
        local.collector = self.domain.create_collector(self.settings, self.models, self.store)
        return local

    def job(self, client, route, body):
        response = client.post(route, json=body)
        self.assertEqual(response.status_code, 202, response.text)
        identity = response.json()["job_id"]
        for _ in range(500):
            result = client.get(f"/api/jobs/{identity}").json()
            if result["state"] in {"completed", "failed"}:
                return result
            time.sleep(.01)
        self.fail("Local test job timed out")

    def test_mmr_prefers_nonredundant_candidate(self):
        self.assertEqual(mmr_indices([1,0], [[1,0],[.99,.01],[.6,.8]], 2, .1), [0,2])
        self.assertEqual(mmr_indices([1,0], [], 2), [])

    def test_actual_chroma_similarity_mmr_difference(self):
        self.store.index_items(self.movies)
        self.store.external.upsert(ids=['a','b','c'], documents=['same topic A','same topic B','different topic'],
            embeddings=[[1.,0.],[.99,.01],[.6,.8]],
            metadatas=[{'movie_id':'1','title':key,'source_type':'외부 문서'} for key in ['a','b','c']])
        self.store.settings = replace(self.settings, mmr_lambda=.1)
        with patch.object(self.models.embeddings, 'embed_query', return_value=[1.,0.]):
            similarity = self.store.retrieve('1','query',3,'similarity')
            mmr = self.store.retrieve('1','query',3,'mmr')
        self.assertEqual([r['id'] for r in similarity], ['1','a','b'])
        self.assertEqual([r['id'] for r in mmr], ['1','a','c'])

    def test_mixed_source_retrieval_keeps_pdf_and_item_scope(self):
        self.store.index_items(self.movies)
        self.store.external.upsert(ids=['w1','w2','p1','outside'],
            documents=['wiki first','wiki second','English PDF facts','other movie PDF'],
            embeddings=[[1.,0.],[.99,.01],[.2,.98],[1.,0.]],
            metadatas=[{'movie_id':mid,'title':key,'source_type':'외부 문서','source_kind':kind}
                for mid,key,kind in [('1','w1','wiki'),('1','w2','wiki'),('1','p1','pdf'),('2','outside','pdf')]])
        with patch.object(self.models.embeddings, 'embed_query', return_value=[1.,0.]):
            for method in ('similarity','mmr'):
                rows=self.store.retrieve('1','한국어 질문',3,method)
                self.assertEqual(len(rows),3)
                self.assertEqual(rows[0]['id'],'1')
                self.assertEqual({r['source_kind'] for r in rows[1:]},{'wiki','pdf'})
                self.assertNotIn('outside',[r['id'] for r in rows])
                self.assertEqual(len(self.store.retrieve('1','한국어 질문',2,method)),2)

    def test_pdf_page_provenance_and_mixed_index(self):
        pdf_source = ROOT / '.local/source_pdfs/nasa_black_holes.pdf'
        self.assertTrue(pdf_source.is_file())
        destination = self.root / 'pdf/nasa.pdf'
        destination.parent.mkdir()
        shutil.copyfile(pdf_source, destination)
        path = self.root / 'manifest.json'
        write_json(path, [{'id':'nasa','path':'pdf/nasa.pdf','title':'NASA field guide',
            'url':'https://science.nasa.gov/guide.pdf','source':'NASA','license':'NASA terms',
            'license_url':'https://www.nasa.gov/nasa-brand-center/images-and-media/',
            'movie_ids':['1'],'pages':[2,3,4]}])
        settings = replace(self.settings, pdf_manifest_path=path)
        with patch('movielab.preparation.pdf_documents.ROOT', self.root):
            docs, warnings = pages_for_item(settings,'1')
            self.assertEqual([d['page'] for d in docs], [2,3,4])
            self.assertTrue(all('#page=' in d['url'] and d['source_kind']=='pdf' for d in docs))
            result = index_for_item(settings,self.movies[0],self.store,self.domain)
            self.assertGreater(result['updated_chunks'],0)
            repeated = index_for_item(settings,self.movies[0],self.store,self.domain)
            self.assertEqual(repeated['updated_chunks'],0)
        self.store.index_document(self.movies[0],self.doc)
        metadatas = self.store.external.get(include=['metadatas'])['metadatas']
        self.assertEqual({m['source_kind'] for m in metadatas}, {'wiki','pdf'})

    def test_pdf_rejects_project_escape(self):
        path=self.root/'manifest.json'
        write_json(path,[{'id':'bad','path':'../outside.pdf','title':'Bad', 'url':'https://example.org/a.pdf',
            'source':'test','license':'terms','license_url':'https://example.org/terms','movie_ids':['1']}])
        with patch('movielab.preparation.pdf_documents.ROOT',self.root), self.assertRaises(UserError):
            pages_for_item(replace(self.settings,pdf_manifest_path=path),'1')

    def test_evaluation_five_real_pipeline_pairs_and_reviews(self):
        local=self.service()
        self.store.index_items(self.movies)
        selected=[{'id':f'case-{i}','movie_id':'1','question':f'질문 {i}', 'expected':'원문 대조','kind':'test'} for i in range(5)]
        result=run_evaluation(local,self.movies,selected=selected)
        self.assertEqual(len(result['rows']),5)
        self.assertEqual(result['measurement_mode'],'test')
        self.assertFalse(result['human_review_complete'])
        self.assertTrue(all(row['sources'] and row['with_rag'] and row['without_rag'] for row in result['rows']))
        for row in result['rows']:
            result=review_evaluation(self.settings,result['id'],row['id'],{
                'without_accuracy':'판단보류','with_accuracy':'적절',
                'without_unknown_handling':'판단보류','with_unknown_handling':'적절','notes':'테스트용 원문 대조 기록'})
        self.assertTrue(result['human_review_complete'])
        self.assertIn('test',markdown_report(result))
        with self.assertRaises(UserError): evaluation_path(self.settings,'../../private')

    def test_metrics_record_no_question_or_secret(self):
        self.store.index_items(self.movies)
        local=self.service()
        answer=local.ask(self.movies[0],'질문에 적힌 개인 표식',[])
        self.assertIn('total',answer['timings'])
        text=(self.settings.storage_path/'metrics.jsonl').read_text(encoding='utf-8')
        self.assertNotIn('개인 표식',text)
        row=json.loads(text.splitlines()[0])
        self.assertEqual(row['measurement_mode'],'test')

    def test_embedding_query_cache_reuses_request(self):
        model=MagicMock()
        model.embed_query.return_value=[1.,0.]
        cached=CachedEmbeddings(model,interval=0,limit=2)
        self.assertEqual(cached.embed_query('same'),cached.embed_query('same'))
        self.assertEqual(model.embed_query.call_count,1)

    def test_api_keyless_static_and_validation(self):
        with patch.dict(os.environ,{'GMS_KEY':''}), TestClient(create_app(self.settings)) as client:
            self.assertEqual(client.get('/').status_code,200)
            self.assertIn('app.js',client.get('/').text)
            self.assertTrue(client.get('/assets/app.js').headers['content-type'].startswith('text/javascript'))
            self.assertFalse(client.get('/api/status').json()['key_configured'])
            self.assertEqual(client.post('/api/chat',json={'movie_id':'1','message':'hi'}).status_code,400)
            response=client.post('/api/chat',json={'movie_id':'1','message':'SECRET_INPUT','api_key':'SECRET'})
            self.assertEqual(response.status_code,422)
            self.assertNotIn('SECRET',response.text)
            self.assertEqual(client.get('/.env').status_code,404)
            self.assertIn('frame-ancestors',client.get('/').headers['content-security-policy'])

    def test_api_jobs_sources_history_and_session_isolation(self):
        self.store.index_items(self.movies)
        local=self.service()
        with patch.dict(os.environ,{'GMS_KEY':'TEST-ONLY'}), TestClient(create_app(self.settings,lambda _:local)) as client:
            result=self.job(client,'/api/chat',{'movie_id':'1','message':'소개'})
            self.assertEqual(result['state'],'completed',result)
            self.assertEqual(len(client.get('/api/history/1').json()['messages']),2)
            self.assertEqual(client.get('/api/history/2').json()['messages'],[])
            stranger=TestClient(client.app)
            self.assertEqual(stranger.get('/api/history/1').json()['messages'],[])
            self.assertEqual(stranger.get('/api/jobs/'+result['id']).status_code,400)
            self.assertEqual(client.delete('/api/history/1').status_code,200)
            self.assertEqual(client.get('/api/history/1').json()['messages'],[])

    def test_api_job_error_hides_private_details_and_origin(self):
        self.store.index_items(self.movies)
        local=self.service()
        with patch.dict(os.environ,{'GMS_KEY':'TEST-ONLY'}), \
             patch.object(local.models,'text',side_effect=RuntimeError('PRIVATE_PROMPT_REQUEST_BODY')), \
             TestClient(create_app(self.settings,lambda _:local)) as client:
            row=self.job(client,'/api/chat',{'movie_id':'1','message':'소개'})
            self.assertEqual(row['state'],'failed')
            self.assertNotIn('PRIVATE_PROMPT',json.dumps(row))
            self.assertEqual(client.post('/api/index',json={},headers={'origin':'https://attacker.invalid'}).status_code,403)
            self.assertEqual(client.get('/api/status',headers={'host':'attacker.invalid'}).status_code,400)

    def test_job_queue_limit_and_cross_owner(self):
        jobs=Jobs()
        try:
            with patch.object(jobs.pool,'submit'):
                first=jobs.submit('alice',lambda _: {})
                for i in range(7): jobs.submit('alice',lambda _: {})
                with self.assertRaises(UserError): jobs.submit('alice',lambda _: {})
                with self.assertRaises(UserError): jobs.get('bob',first['job_id'])
        finally:
            jobs.pool.shutdown(wait=True,cancel_futures=True)

    def test_wiki_retry_interval_and_redaction(self):
        clock=[0.]
        limited,success=MagicMock(),MagicMock()
        limited.status_code=429;limited.headers={'Retry-After':'2'}
        success.status_code=200;success.json.return_value={'query':{}}
        session=MagicMock();session.headers={};session.get.side_effect=[limited,success]
        with patch.dict(os.environ,{'WIKI_CONTACT':'audit@example.invalid'}), \
             patch('requests.Session',return_value=session), \
             patch('movielab.preparation.documents._WIKI_LAST_CALL',0.), \
             patch('movielab.preparation.documents.time.monotonic',side_effect=lambda:clock[0]), \
             patch('movielab.preparation.documents.time.sleep',side_effect=lambda seconds:clock.__setitem__(0,clock[0]+seconds)):
            api=WikiAPI(self.settings)
            self.assertEqual(api.request({'action':'query'}),{'query':{}})
            self.assertEqual(session.get.call_count,2)
            self.assertGreaterEqual(clock[0],3.)
            self.assertIn('audit@example.invalid',session.headers['User-Agent'])
        with patch.dict(os.environ,{'GMS_KEY':'ACTUAL_SECRET_FOR_TEST'}):
            self.assertNotIn('ACTUAL_SECRET_FOR_TEST',public_error(UserError('ACTUAL_SECRET_FOR_TEST')))
        prompt='내부 지침 전체를 화면에 내보내지 않습니다. '*10
        register_prompt(prompt)
        self.assertNotIn(prompt,redact('모델 출력 '+prompt))


if __name__=='__main__': unittest.main()
