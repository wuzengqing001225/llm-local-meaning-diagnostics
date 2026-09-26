"""Artificial fixtures to test plumbing. Never evidence about any model."""
from pathlib import Path
from .common import *
from .experiment import freeze,accept_tasks,plan,load_plan
from .analysis import analyze

def fixture():
    docs=[];defs=[];passages=[];probes=[];tasks=[];scores=[]
    for n in range(4):
        did=f'fixture:{n}';pid=did+':p';doc={'doc_id':did,'cluster_id':did,'corpus':'fixture','split':'dev'};docs.append(doc)
        for term,text in [('Region','The Region includes Canada and excludes the United States.'),('Product','Product refers only to the blue device listed in this document.')]:
            defs.append({'definition_id':did+':'+term,'doc_id':did,'term':term,'text':text,'flags':[]})
        passage={'passage_id':pid,'doc_id':did,'text':f'Example {n}: the distributor may sell the Product within the Region.','definition_ids':[did+':Region',did+':Product']};passages.append(passage)
        review={'status':'accepted','reviewer_ids':['fixture-reviewer-A','fixture-reviewer-B'],'key_valid':True,'source_sufficient':True,'independent_of_probes':True}
        for term in ['Region','Product']:
            probes.append({'probe_id':did+':A:'+term,'doc_id':did,'passage_id':pid,'definition_id':did+':'+term,'question':f'Fixture diagnostic about the meaning of {term}: which statement follows?','options':['Local rule','Ordinary rule'],'answer':'A','source_type':'smoke_fixture','author_id':'fixture-A','review':review})
        tasks.append({'task_id':did+':B','doc_id':did,'context_ids':[pid],'question':f'Independent fixture {n}: is this specified sale permitted under the document?','options':['Yes','No'],'answer':'A' if n%2==0 else 'B','source_type':'smoke_fixture','author_id':'fixture-B','evidence_quotes':[passage['text']],'definition_dependence':'required' if n%2==0 else 'not_required','review':review})
    c={'schema_version':1,'documents':docs,'definitions':defs,'passages':passages,'status':'smoke_fixture'}
    for q in probes:
        pb=.2 if q['definition_id'].endswith('Region') else .8;pc=.9
        scores.append({'probe_id':q['probe_id'],'corpus_digest':digest(c),'probe_digest':digest(q),'p_bare':pb,'p_definition':pc,'risk':1-pb,'pd':pc-pb,'proxy_model':'smoke-proxy','proxy_revision':'fixture-v1','backend':'smoke_fixture'})
    cfg={'schema_version':1,'stage':'pilot','corpus':'fixture','budget_scope':'workload','seed':1,'analysis_split':'dev','reader':{'model':'smoke-reader','base_url':'http://localhost:0/v1','generation':{}},'proxy':{'model':'smoke-proxy','revision':'fixture-v1'},'tokenizer':{'kind':'utf8_smoke'},'policies':['none','matched','random','idf','term_mean','term_max','occurrence_risk','pd','repairability','all_matched','full_glossary'],'budgets':[256,512],'primary_budget':256,'primary_policy':'occurrence_risk','comparator':'matched','random_seeds':[1,2,3],'bootstrap_replicates':200,'max_requests':500}
    return c,probes,tasks,scores,cfg

def smoke(out):
    out=Path(out);require(not out.exists(),'Smoke directory already exists');out.mkdir(parents=True)
    c,p,t,s,cfg=fixture();write_json(out/'corpus.json',c);write_rows(out/'diagnostics.jsonl',p);write_rows(out/'independent_tasks.jsonl',t);write_rows(out/'scores.jsonl',s);write_json(out/'config.json',cfg)
    freeze(out/'corpus.json',out/'diagnostics.jsonl',out/'scores.jsonl',out/'config.json',out/'snapshot',True)
    accept_tasks(out/'snapshot',out/'independent_tasks.jsonl',out/'tasks')
    summary=plan(out/'snapshot',out/'tasks',out/'plan');pm,reqs,trials=load_plan(out/'plan')
    # Constant artificial reader; no fabricated demonstration of a treatment advantage.
    preds=[{'plan_id':pm['plan_id'],'request_id':r['request_id'],'status':'ok','content':'A','returned_model':'smoke-reader','mode':'smoke'} for r in reqs]
    write_rows(out/'predictions.jsonl',preds)
    report=analyze(out/'snapshot',out/'tasks',out/'plan',out/'predictions.jsonl',out/'analysis')
    from .mechanism import plan_mechanism,analyze_mechanism
    annotations=[{'task_id':q['task_id'],'status':'ready','category':'local_binding','focus_definition_id':q['doc_id']+':Region','usual_meaning':'a broad geographic area','usual_answer':None,'definition_sufficient':True,'evidence_quotes':q['evidence_quotes'],'reason':'software fixture only','extra_passage_ids':[],'review_mode':'human','reviewer_ids':['fixture-person-1','fixture-person-2']} for q in t]
    write_rows(out/'mechanism_annotations.jsonl',annotations)
    mechanism_plan=plan_mechanism(out/'snapshot',out/'tasks',out/'mechanism_annotations.jsonl',out/'mechanism_plan')
    mm,mreq,_=load_plan(out/'mechanism_plan')
    write_rows(out/'mechanism_predictions.jsonl',[{'plan_id':mm['plan_id'],'request_id':r['request_id'],'status':'ok','content':'{\"answer\":\"A\",\"confidence\":0.5}','returned_model':'smoke-reader','mode':'smoke'} for r in mreq])
    analyze_mechanism(out/'snapshot',out/'tasks',out/'mechanism_plan',out/'mechanism_predictions.jsonl',out/'mechanism_analysis')
    return {'mechanism_smoke':mechanism_plan,'status':'software_smoke_passed','warning':'Artificial fixture; zero real model calls. NOT research results.','plan':summary,'primary_contrast':report['primary_contrast']}
