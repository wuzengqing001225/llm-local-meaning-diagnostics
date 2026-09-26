import unittest,tempfile,json,os,copy
from pathlib import Path
from unittest.mock import patch
from localrisk.study import BlindConsensus,balance_positions,candidate_frame,stratified_selection,run_study
from localrisk.common import *
from localrisk.easy import parser
from localrisk.smoke import fixture

class Solver:
    def __init__(self,name,answer='A'):self.config={'model':name};self.answer=answer;self.prompts=[]
    def complete(self,system,prompt):
        self.prompts.append(json.loads(prompt))
        return json.dumps({'correct_answer':self.answer,'source_sufficient':True,'definition_dependence':'required','reason':'fixture'})

class StudyTests(unittest.TestCase):
    def test_checker_does_not_receive_proposed_answer_or_dependence(self):
        a,b=Solver('gpt'),Solver('deepseek');j=BlindConsensus(a,b)
        out=json.loads(j.complete('',json.dumps({'source':{'source_passage':'facts'},'item':{'question':'Q','options':['right','wrong'],'answer':'A','definition_dependence':'required','evidence_quotes':['biased evidence']}})))
        self.assertTrue(out['key_valid'])
        for c in [a,b]:self.assertEqual(set(c.prompts[0]),{'source','question','options'});self.assertNotIn('answer',c.prompts[0])
    def test_checker_disagreement_is_not_accepted_truth(self):
        j=BlindConsensus(Solver('gpt'),Solver('deepseek','B'))
        out=json.loads(j.complete('',json.dumps({'source':{},'item':{'question':'Q','options':['a','b'],'answer':'A'}})));self.assertFalse(out['key_valid'])
    def test_same_checker_identifier_rejected(self):
        with self.assertRaises(InvalidExperiment):BlindConsensus(Solver('same'),Solver('same'))
    def test_B_not_filtered_by_final_reader_full_source_verdict(self):
        from localrisk.study import strict_item
        row={'answer':'A','review':{'status':'accepted','key_valid':False,'source_sufficient':True,'independent_checker_votes':[{'model':'gpt','correct_answer':'B','source_sufficient':True},{'model':'deepseek','correct_answer':'A','source_sufficient':True}]}}
        with patch('localrisk.study.make_item',return_value=copy.deepcopy(row)):
            r=strict_item({},'p',Solver('deepseek'),None)
        self.assertEqual(r['review']['status'],'accepted');self.assertFalse(r['review']['final_reader_audit_agrees'])
    def test_B_non_reader_source_disagreement_is_rejected(self):
        from localrisk.study import strict_item
        row={'answer':'A','review':{'status':'accepted','key_valid':False,'source_sufficient':True,'independent_checker_votes':[{'model':'gpt','correct_answer':'A','source_sufficient':True},{'model':'deepseek','correct_answer':'B','source_sufficient':True}]}}
        with patch('localrisk.study.make_item',return_value=copy.deepcopy(row)):
            r=strict_item({},'p',Solver('deepseek'),None)
        self.assertEqual(r['review']['status'],'rejected')
    def test_balance_preserves_answer_content_and_updates_checker_mapping(self):
        rows=[{'question':f'q{i}','options':['correct','other','another'],'answer':'A','review':{'status':'accepted','checker_advisory':{'correct_answer':'A'},'independent_checker_votes':[{'correct_answer':'A'}]}} for i in range(12)]
        result=balance_positions(rows,7);counts={k:sum(r['answer']==k for r in result) for k in 'ABC'};self.assertEqual(counts,{'A':4,'B':4,'C':4})
        for r in result:
            self.assertEqual(r['options'][ord(r['answer'])-65],'correct');self.assertEqual(r['review']['checker_advisory']['correct_answer'],r['answer'])
        self.assertTrue(all(r['answer']=='A' for r in rows))
    def test_sampling_preserves_absolute_low_risk_status(self):
        rows=[{'passage_id':str(i),'doc_id':str(i),'R':.01} for i in range(100)]
        selected,status=stratified_selection(rows,5,.2,.6,1);self.assertEqual(selected,[]);self.assertEqual(status['status'],'insufficient_A_risk_coverage')
    def test_each_stratum_sampled_without_duplicates(self):
        rows=[{'passage_id':str(i),'doc_id':str(i),'R':[.1,.4,.8][i%3]} for i in range(30)]
        selected,status=stratified_selection(rows,4,.2,.6,1);self.assertEqual(len(selected),12);self.assertEqual(len({r['passage_id'] for r in selected}),12)
        self.assertTrue(all(r['selection_probability']==.4 for r in selected));self.assertEqual(stratified_selection(rows,4,.2,.6,1)[0],selected)
    def test_A_score_provenance_must_match(self):
        c,p,t,s,cfg=fixture()
        for r in p:r['source_type']='model_generated'
        for r in s:r['backend']='fixture_scores';r['probe_digest']=digest(next(a for a in p if a['probe_id']==r['probe_id']))
        frame,missing=candidate_frame(c,p,s);self.assertEqual(len(frame),4)
        s[0]['probe_digest']='wrong'
        with self.assertRaises(InvalidExperiment):candidate_frame(c,p,s)

if __name__=='__main__':unittest.main()

class StudyFlowTests(unittest.TestCase):
    def test_A_scored_before_B_and_reused_on_resume(self):
        from test_easy import FakeClient,fake_reader,ENV
        from localrisk.tokens import Counter as TokenCounter
        from localrisk.easy import parser as ep
        class Client(FakeClient):
            lock=None
            def complete(self,system,prompt):
                if system.startswith('Independently solve'):
                    self.calls.append((system,prompt));packet=json.loads(prompt)
                    return json.dumps({'correct_answer':'A','source_sufficient':True,'definition_dependence':'required','reason':'fixture independent solve'})
                if prompt.startswith('Write a NEW scenario'):
                    assert self.lock.exists(), 'B started before A was scored and locked'
                return super().complete(system,prompt)
        c,_,_,_,_=fixture()
        for d in c['documents']:d['corpus']='cuad'
        def scorer(cp,pp,model,revision,out,device):
            cc=read_json(cp);probes=read_rows(pp);rows=[]
            for q in probes:
                if q['review']['status']!='accepted':continue
                r=[.1,.4,.8,.1][int(q['doc_id'].split(':')[1])]
                rows.append({'probe_id':q['probe_id'],'corpus_digest':digest(cc),'probe_digest':digest(q),'p_bare':1-r,'p_definition':.95,'risk':r,'pd':.95-(1-r),'proxy_model':model,'proxy_revision':revision,'backend':'fixture-only'})
            write_rows(out,rows)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);terms=root/'terms.jsonl';terms.write_text('{}\n')
            a=ep().parse_args(['--out',str(root/'run'),'--limit','0']);a.budgets=[16,32,64]
            a.pool_size=4;a.per_band=1;a.minimum_per_band=1;a.risk_low=.2;a.risk_high=.6;a.study_seed=7;a.cuad_terms=str(terms)
            Client.lock=root/'run/_study/A_index_lock.json';Client.calls=[]
            with patch.dict(os.environ,{**ENV,'JUDGE_MODEL':ENV['LLM_MODEL']},clear=True),patch('localrisk.study.build_pool',return_value=c),patch('localrisk.study.DraftClient',Client),patch('localrisk.easy.DraftClient',Client),patch('localrisk.study.pin_revision',return_value='fixed'),patch('localrisk.easy.pin_revision',return_value='fixed'),patch('localrisk.study.choose_device',return_value='cpu'),patch('localrisk.study.score_probes',side_effect=scorer) as score,patch('localrisk.easy.score_probes') as redundant,patch('localrisk.easy.run_http',side_effect=fake_reader),patch('localrisk.experiment.TokenCounter',side_effect=lambda _:TokenCounter({'kind':'utf8_smoke'})),patch('localrisk.mechanism.TokenCounter',side_effect=lambda _:TokenCounter({'kind':'utf8_smoke'})):
                first=run_study(a);ncalls=len(Client.calls);second=run_study(a)
                self.assertEqual(first['status'],'complete');self.assertEqual(second['status'],'complete');self.assertEqual(score.call_count,1);redundant.assert_not_called();self.assertEqual(len(Client.calls),ncalls)
            report=read_json(root/'run/selection_report.json');self.assertEqual(report['B_generated'],3)
            self.assertNotIn('unit-test-secret',(root/'run/_study/protocol.json').read_text())
