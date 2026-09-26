import unittest,tempfile,json,copy,zipfile,os
from pathlib import Path
from unittest.mock import patch
from localrisk.common import *
from localrisk.smoke import fixture
from localrisk.experiment import freeze,accept_tasks,load_plan
from localrisk.mechanism import *
from collect_results import collect

class TestMechanism(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.r=Path(self.tmp.name)
        c,p,t,s,cfg=fixture()
        for d in c['documents']:
            c['definitions'].append({'definition_id':d['doc_id']+':Noise','doc_id':d['doc_id'],'term':'Noise','text':'The extra term refers to equipment excluded from this example.','flags':[]})
            c['passages'].append({'passage_id':d['doc_id']+':extra','doc_id':d['doc_id'],'text':'The separate rule requires written approval before this sale.','definition_ids':[]})
        for row in s:row['corpus_digest']=digest(c)
        self.c,self.p,self.t,self.s,self.cfg=c,p,t,s,cfg
        write_json(self.r/'c.json',c);write_rows(self.r/'p.jsonl',p);write_rows(self.r/'t.jsonl',t);write_rows(self.r/'s.jsonl',s);write_json(self.r/'cfg.json',cfg)
        freeze(self.r/'c.json',self.r/'p.jsonl',self.r/'s.jsonl',self.r/'cfg.json',self.r/'snapshot',True)
        accept_tasks(self.r/'snapshot',self.r/'t.jsonl',self.r/'tasks')
        cats=['meaning_conflict','local_binding','other_gap','control'];a=[]
        for i,task in enumerate(t):
            a.append({'task_id':task['task_id'],'status':'ready','category':cats[i],'review_mode':'human','reviewer_ids':['fixture-1','fixture-2'],'focus_definition_id':task['doc_id']+':Region',
                      'usual_meaning':'a generally understood geographic area','usual_answer':'B' if i==0 else None,'definition_sufficient':i!=2,'reason':'artificial fixture','evidence_quotes':task['evidence_quotes'],
                      'extra_passage_ids':[task['doc_id']+':extra'] if i==2 else [],'irrelevant_definition_id':task['doc_id']+':Noise','irrelevant_verified':True})
        self.a=a;write_rows(self.r/'a.jsonl',a)
    def tearDown(self):self.tmp.cleanup()
    def build(self):
        return plan_mechanism(self.r/'snapshot',self.r/'tasks',self.r/'a.jsonl',self.r/'plan')
    def predict(self):
        pm,reqs,trials=load_plan(self.r/'plan');rows=[];gold={t['task_id']:t['answer'] for t in self.t}
        for trial in trials:
            i=int(trial['task_id'].split(':')[1]);arm=trial['arm'];answer=gold[trial['task_id']]
            if i==0 and arm in ['bare','usual_note','irrelevant_note']:answer='B'
            if i==1 and arm=='bare':answer='ABSTAIN'
            if i==2 and arm!='other_evidence':answer='B'
            rows.append({'plan_id':pm['plan_id'],'request_id':trial['request_id'],'status':'ok','mode':'smoke','returned_model':'fixture-model','content':json.dumps({'answer':answer,'confidence':.95})})
        # Shared identical request ids are one observation, not independent replicates.
        rows=list({r['request_id']:r for r in rows}.values());write_rows(self.r/'pred.jsonl',rows)
    def test_all_conditions_and_extra_rule(self):
        result=self.build();self.assertEqual(result['annotated_tasks'],4);self.assertEqual(result['conditions']['other_evidence'],1)
        self.assertEqual(result['conditions']['irrelevant_note'],4)
    def test_no_annotation_labels_in_reader_prompt(self):
        self.build();_,reqs,_=load_plan(self.r/'plan')
        for q in reqs:
            text=canonical(q['payload']);self.assertNotIn('meaning_conflict',text);self.assertNotIn('usual_answer',text);self.assertNotIn('focus_definition_id',text)
    def test_abstention_is_not_a_wrong_substantive_answer(self):
        self.build();self.predict();r=analyze_mechanism(self.r/'snapshot',self.r/'tasks',self.r/'plan',self.r/'pred.jsonl',self.r/'out')
        b=next(x for x in r['by_category'] if x['category']=='local_binding' and x['arm']=='bare')
        self.assertEqual(b['abstention_rate'],1);self.assertEqual(b['substantive_wrong_rate'],0);self.assertEqual(b['answer_coverage'],0)
    def test_joint_confident_usual_error_is_measured(self):
        self.build();self.predict();r=analyze_mechanism(self.r/'snapshot',self.r/'tasks',self.r/'plan',self.r/'pred.jsonl',self.r/'out')
        b=next(x for x in r['by_category'] if x['category']=='meaning_conflict' and x['arm']=='bare');self.assertEqual(b['high_confidence_usual_error_count'],1)
    def test_local_note_not_sufficient_for_rule_gap(self):
        self.build();self.predict();r=analyze_mechanism(self.r/'snapshot',self.r/'tasks',self.r/'plan',self.r/'pred.jsonl',self.r/'out')
        x=next(x for x in r['paired_contrasts'] if x['local_note_minus']=='other_evidence' and x['subset']=='other_gap');self.assertEqual(x['net_accuracy_difference'],-1)
    def test_pending_category_never_guessed_from_outcome(self):
        self.a[0]['status']='pending';write_rows(self.r/'a.jsonl',self.a);r=self.build();self.assertEqual(r['pending_tasks'],1);self.assertEqual(r['annotated_tasks'],3)
    def test_unannotated_empty_plan_is_valid_but_has_no_result(self):
        write_rows(self.r/'a.jsonl',[]);r=self.build();self.assertEqual(r['annotated_tasks'],0);self.predict()
        result=analyze_mechanism(self.r/'snapshot',self.r/'tasks',self.r/'plan',self.r/'pred.jsonl',self.r/'out');self.assertEqual(result['by_category'],[])
    def test_same_usual_and_gold_cannot_define_conflict(self):
        self.a[0]['usual_answer']='A';write_rows(self.r/'a.jsonl',self.a)
        with self.assertRaises(InvalidExperiment):self.build()
    def test_other_gap_needs_evidence_in_confirmatory_labels(self):
        _,public,gold=load_task_bundle(self.r/'tasks',load_snapshot(self.r/'snapshot')[0]['snapshot_id'],True)
        self.a[2]['extra_passage_ids']=[]
        with self.assertRaises(InvalidExperiment):validate_annotations(self.c,public,gold,self.a,True)
    def test_extra_evidence_cannot_come_from_other_document(self):
        self.a[2]['extra_passage_ids']=['fixture:0:extra'];write_rows(self.r/'a.jsonl',self.a)
        with self.assertRaises(InvalidExperiment):self.build()
    def test_missing_api_response_not_an_error_label(self):
        self.build();self.predict();rr=read_rows(self.r/'pred.jsonl');write_rows(self.r/'pred.jsonl',rr[:-1])
        with self.assertRaises(InvalidExperiment):analyze_mechanism(self.r/'snapshot',self.r/'tasks',self.r/'plan',self.r/'pred.jsonl',self.r/'out')
    def test_parse_confidence_and_abstain(self):
        r=parse_response('{"answer":"ABSTAIN","confidence":0.8}',4);self.assertTrue(r['abstain']);self.assertEqual(r['confidence'],.8)
        self.assertFalse(parse_response('Because A is wrong, B is right',4)['valid']);self.assertIsNone(parse_response('{"answer":"A","confidence":80}',4)['confidence'])
    def test_quote_match_preserves_critical_punctuation(self):
        self.assertTrue(quote_present('The  rule applies.', ['The rule applies.']))
        self.assertFalse(quote_present('The rule does not apply.', ['The rule does apply.']))
        self.assertFalse(quote_present('.', ['Any source.']))
        self.assertFalse(quote_present('rate 1 5 percent',['rate 1.5 percent']))

class TestCollection(unittest.TestCase):
    def test_keys_excluded_and_unchanged_bytes_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);code=root/'code';run=root/'run';code.mkdir();run.mkdir()
            (code/'run_main.py').write_text('print("ok")\n');(run/'.env').write_text('LLM_API_KEY=unit-secret-123456')
            (run/'safe.json').write_text('{ "value": 1 }\n');(run/'secret.json').write_text('{"api_key":"unit-secret-123456", "model":"reader"}')
            with patch.dict(os.environ,{'LLM_API_KEY':'unit-secret-123456'}):r=collect([run],root/'bundle.zip',code)
            with zipfile.ZipFile(root/'bundle.zip') as z:
                self.assertFalse(any(x.endswith('.env') for x in z.namelist()));self.assertEqual(z.read('runs/01-run/safe.json'),b'{ "value": 1 }\n')
                self.assertNotIn(b'unit-secret-123456',z.read('runs/01-run/secret.json'))
            self.assertGreater(r['redacted_files'],0)

if __name__=='__main__':unittest.main()
