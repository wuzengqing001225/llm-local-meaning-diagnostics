import unittest,tempfile,copy,json
from pathlib import Path
from unittest.mock import patch
from localrisk.common import *
from localrisk.smoke import fixture,smoke
from localrisk.validation import *
from localrisk.policy import *
from localrisk.tokens import Counter as TokenCounter
from localrisk.experiment import *
from localrisk.analysis import *
from localrisk.backends import label_sequences,run_http
from localrisk.prepare import prepare,author_packets

class TestScientificContract(unittest.TestCase):
    def setUp(self):self.c,self.p,self.t,self.s,self.cfg=fixture()
    def test_pending_review_cannot_pass(self):
        self.p[0]['review']=dict(self.p[0]['review'],status='pending')
        with self.assertRaises(InvalidExperiment):validate_probes(self.c,self.p,True)
    def test_empty_human_audit_cannot_pass(self):
        self.t[0]['review']=dict(self.t[0]['review'],reviewer_ids=[])
        with self.assertRaises(InvalidExperiment):validate_tasks(self.c,self.p,self.t,True)
    def test_two_reviewers_required_for_independent_task(self):
        self.t[0]['review']=dict(self.t[0]['review'],reviewer_ids=['one'])
        with self.assertRaises(InvalidExperiment):validate_tasks(self.c,self.p,self.t,True)
    def test_same_diagnostic_question_rejected(self):
        self.t[0]['question']=self.p[0]['question']
        with self.assertRaises(InvalidExperiment):validate_tasks(self.c,self.p,self.t,True)
    def test_same_author_rejected(self):
        self.t[0]['author_id']='fixture-A'
        with self.assertRaises(InvalidExperiment):validate_tasks(self.c,self.p,self.t,True)
    def test_evidence_must_exist(self):
        self.t[0]['evidence_quotes']=['invented evidence']
        with self.assertRaises(InvalidExperiment):validate_tasks(self.c,self.p,self.t,True)
    def test_smoke_forbidden_in_real_experiment(self):
        with self.assertRaises(InvalidExperiment):validate_probes(self.c,self.p)
    def test_gold_separated_from_policy(self):
        public,gold=split_tasks(self.c,self.p,self.t,True)
        self.assertNotIn('answer',public[0]);self.assertIn('answer',gold[0]);self.assertNotIn('definition_dependence',public[0])
        with self.assertRaises(InvalidExperiment):candidates(self.c,{**public[0],'answer':'B'})
    def test_target_definition_not_exposed_to_policy(self):
        public,gold=split_tasks(self.c,self.p,self.t,True)
        with self.assertRaises(InvalidExperiment):candidates(self.c,{**public[0],'target_definition_id':'fixture:0:Region'})
    def test_score_provenance_rejects_changed_key(self):
        self.p[0]=dict(self.p[0],answer='B')
        with self.assertRaises(InvalidExperiment):validate_scores(self.c,self.p,self.s,True)
    def test_PD_and_R_not_interchangeable(self):
        self.s[0]['pd']=self.s[0]['risk']
        with self.assertRaises(InvalidExperiment):validate_scores(self.c,self.p,self.s,True)
    def test_cross_document_context_rejected(self):
        self.t[0]['context_ids']=[self.t[1]['context_ids'][0]]
        with self.assertRaises(InvalidExperiment):validate_tasks(self.c,self.p,self.t,True)
    def test_duplicate_task_ids_rejected(self):
        with self.assertRaises(InvalidExperiment):validate_tasks(self.c,self.p,self.t+[self.t[0]],True)
    def test_strict_answer_parse(self):
        self.assertIsNone(parse_answer('Because A looks right, answer B.',2));self.assertEqual(parse_answer('{"answer":"B"}',2),'B');self.assertIsNone(parse_answer('C',2))
    def test_multitoken_labels_not_first_token(self):
        class Tok:
            def encode(self,s,**kw):return [99,ord(s[-1])]
        self.assertEqual(label_sequences(Tok(),2),[[99,65],[99,66]])
    def test_duplicate_token_sequences_rejected(self):
        class Tok:
            def encode(self,s,**kw):return [99]
        with self.assertRaises(InvalidExperiment):label_sequences(Tok(),2)
    def test_budget_includes_scope_wrapper(self):
        pub,_=split_tasks(self.c,self.p,self.t,True);occ,term=index_scores(self.c,self.p,self.s);counter=TokenCounter({'kind':'utf8_smoke'})
        picked,cost,_=select('occurrence_risk',self.c,pub[0],occ,term,corpus_idf(self.c),90,counter)
        self.assertEqual(picked,[]);self.assertEqual(cost,0)
        for budget in range(0,500,17):
            picked,cost,_=select('occurrence_risk',self.c,pub[0],occ,term,{},budget,counter);self.assertLessEqual(cost,budget);self.assertEqual(cost,counter.count(definition_block(picked)))
    def test_missing_occurrence_score_not_assumed_safe(self):
        pub,_=split_tasks(self.c,self.p,self.t,True);occ,term=index_scores(self.c,self.p,self.s);occ.pop(next(iter(occ)))
        with self.assertRaises(InvalidExperiment):select('occurrence_risk',self.c,pub[0],occ,term,{},256,TokenCounter({'kind':'utf8_smoke'}))
    def test_random_policy_reproducible(self):
        pub,_=split_tasks(self.c,self.p,self.t,True);args=('random',self.c,pub[0],*index_scores(self.c,self.p,self.s),{},256,TokenCounter({'kind':'utf8_smoke'}),27)
        self.assertEqual(select(*args),select(*args))
    def test_workload_budget_can_prioritize_single_note_tasks(self):
        pub,_=split_tasks(self.c,self.p,self.t,True);occ,term=index_scores(self.c,self.p,self.s);counter=TokenCounter({'kind':'utf8_smoke'})
        selected=select_workload('occurrence_risk',self.c,pub,occ,term,{},50,counter)
        self.assertLessEqual(sum(v[1] for v in selected.values()),50*len(pub))
        self.assertGreater(sum(bool(v[0]) for v in selected.values()),0)
        self.assertTrue(all(select('occurrence_risk',self.c,t,occ,term,{},50,counter)[0]==[] for t in pub))
    def test_workload_zero_budget_injects_nothing(self):
        pub,_=split_tasks(self.c,self.p,self.t,True);occ,term=index_scores(self.c,self.p,self.s)
        selected=select_workload('random',self.c,pub,occ,term,{},0,TokenCounter({'kind':'utf8_smoke'}),1)
        self.assertTrue(all(not v[0] and v[1]==0 for v in selected.values()))
    def test_workload_missing_scores_fail_before_allocation(self):
        pub,_=split_tasks(self.c,self.p,self.t,True);occ,term=index_scores(self.c,self.p,self.s);occ.clear()
        with self.assertRaises(InvalidExperiment):select_workload('occurrence_risk',self.c,pub,occ,term,{},50,TokenCounter({'kind':'utf8_smoke'}))
    def test_auc_ties_and_no_positive(self):
        self.assertEqual(auroc([0,1],[.5,.5]),.5);self.assertEqual(auroc([0,0,1,1],[0,1,2,3]),1);self.assertIsNone(auroc([0,0],[.2,.4]))
        self.assertEqual(average_precision([0,1],[.5,.5]),.5)
    def test_cluster_bootstrap_single_group_has_no_interval(self):self.assertIsNone(cluster_ci([1,0],['a','a']))

class TestEndToEnd(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'run';smoke(self.root)
    def tearDown(self):self.tmp.cleanup()
    def test_complete_pipeline_zero_fake_advantage(self):
        r=read_json(self.root/'analysis/summary.json');self.assertEqual(r['mode'],'smoke');self.assertEqual(r['primary_contrast']['difference'],0);self.assertEqual(r['primary_contrast']['n_tasks'],4)
        random_rows=[x for x in r['results'] if x['policy']=='random' and x['subset']=='all'];self.assertTrue(all(x['n_tasks']==4 for x in random_rows))
    def test_snapshot_change_detected(self):
        p=self.root/'snapshot/config.json';c=read_json(p);c['seed']=999;write_json(p,c)
        with self.assertRaises(InvalidExperiment):load_snapshot(self.root/'snapshot')
    def test_missing_request_blocks_effect_estimate(self):
        p=self.root/'predictions.jsonl';write_rows(p,read_rows(p)[:-1])
        with self.assertRaises(InvalidExperiment):analyze(self.root/'snapshot',self.root/'tasks',self.root/'plan',p,self.root/'analysis2')
    def test_gold_mutation_detected(self):
        p=self.root/'tasks/gold_private.jsonl';r=read_rows(p);r[0]['answer']='B';write_rows(p,r)
        with self.assertRaises(InvalidExperiment):analyze(self.root/'snapshot',self.root/'tasks',self.root/'plan',self.root/'predictions.jsonl',self.root/'analysis2')
    def test_mixed_model_versions_rejected(self):
        p=self.root/'predictions.jsonl';r=read_rows(p);r[0]['returned_model']='different';write_rows(p,r)
        with self.assertRaises(InvalidExperiment):analyze(self.root/'snapshot',self.root/'tasks',self.root/'plan',p,self.root/'analysis2')
    def test_frozen_outputs_not_overwritten(self):
        with self.assertRaises(InvalidExperiment):smoke(self.root)
    def test_http_never_runs_smoke(self):
        with self.assertRaises(InvalidExperiment):run_http(self.root/'plan',self.root/'network.jsonl')
    def test_requested_payload_contains_no_gold(self):
        m,reqs,trials=load_plan(self.root/'plan')
        for r in reqs:
            self.assertNotIn('gold',r['payload']);self.assertNotIn('review',canonical(r['payload']));self.assertNotIn('definition_dependence',canonical(r['payload']))
    def test_http_errors_are_not_scored_wrong(self):
        p=self.root/'predictions.jsonl';r=read_rows(p);r[0]['status']='error';write_rows(p,r)
        with self.assertRaises(InvalidExperiment):analyze(self.root/'snapshot',self.root/'tasks',self.root/'plan',p,self.root/'analysis2')
    def test_prepare_requires_only_original_sources(self):
        src=self.root/'terms.jsonl';write_rows(src,[{'id':'cuadfull:1:Region','term':'Region','def_raw':'means Canada excluding the United States.','labels':{'ci':1},'contexts':['The distributor may market its goods throughout the Region under the license.']}])
        c=prepare(src,groups_per_corpus=1,passages_per_group=1);self.assertEqual(len(c['passages']),1)
        author_packets(c,self.root/'packets');r=read_rows(self.root/'packets/tasks_B.template.jsonl');self.assertEqual(r[0]['review']['status'],'pending');self.assertEqual(r[0]['answer'],'')

class TestHTTPAdapter(unittest.TestCase):
    def make_plan(self):
        return ({'mode':'real','plan_id':'adapter-test','reader':{'model':'unit-reader','base_url':'http://localhost:9000/v1','allow_unauthenticated_local':True}},[{'request_id':'r1','payload':{'model':'unit-reader','messages':[]},'n_options':2}],[])
    def test_response_metadata_and_resume(self):
        from unittest.mock import MagicMock
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps({'id':'provider-id','model':'unit-reader-v1','usage':{'prompt_tokens':10},'choices':[{'message':{'content':'B'}}]}).encode()
        with tempfile.TemporaryDirectory() as tmp, patch('localrisk.backends.load_plan',return_value=self.make_plan()), patch('localrisk.backends.urllib.request.urlopen',return_value=response) as send:
            out=Path(tmp)/'pred.jsonl';run_http('unused',out);run_http('unused',out)
            self.assertEqual(send.call_count,1);row=read_rows(out)[0];self.assertEqual(row['prediction'],'B');self.assertEqual(row['returned_model'],'unit-reader-v1');self.assertEqual(row['usage']['prompt_tokens'],10)
    def test_bad_format_not_first_letter(self):
        from unittest.mock import MagicMock
        response=MagicMock();response.__enter__.return_value.read.return_value=json.dumps({'model':'unit-reader-v1','choices':[{'message':{'content':'A thought about B; answer B.'}}]}).encode()
        with tempfile.TemporaryDirectory() as tmp, patch('localrisk.backends.load_plan',return_value=self.make_plan()), patch('localrisk.backends.urllib.request.urlopen',return_value=response):
            out=Path(tmp)/'pred.jsonl';run_http('unused',out);r=read_rows(out)[0];self.assertEqual(r['status'],'ok');self.assertIsNone(r['prediction'])
    def test_http_failure_preserved_as_missing(self):
        import urllib.error
        err=urllib.error.HTTPError('http://localhost',503,'unavailable',None,None)
        with tempfile.TemporaryDirectory() as tmp, patch('localrisk.backends.load_plan',return_value=self.make_plan()), patch('localrisk.backends.urllib.request.urlopen',side_effect=err), patch('localrisk.backends.time.sleep'):
            out=Path(tmp)/'pred.jsonl';run_http('unused',out);r=read_rows(out)[0];self.assertEqual(r['status'],'error');self.assertEqual(r['http_status'],503);self.assertNotIn('prediction',r)
    def test_different_plan_cannot_reuse_output(self):
        with tempfile.TemporaryDirectory() as tmp, patch('localrisk.backends.load_plan',return_value=self.make_plan()):
            out=Path(tmp)/'pred.jsonl';write_rows(out,[{'plan_id':'other','request_id':'r1','status':'ok'}])
            with self.assertRaises(InvalidExperiment):run_http('unused',out)

if __name__=='__main__':unittest.main()
