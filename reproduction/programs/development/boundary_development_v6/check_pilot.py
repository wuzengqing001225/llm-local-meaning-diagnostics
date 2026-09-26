#!/usr/bin/env python3
"""Pre-reader usual-meaning labels and independent source checks. No outcomes read."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'local_meaning_v5_development'))
from run_reader_dev import canonical, config_role, request_one
from draft_source_rules import parse_json_object

USUAL = '''Classify a concrete situation using the ordinary English meaning of the named term only. You have no local contract definition. Do not invent one. Ignore the request's reference to a contract when judging the ordinary meaning. Return yes if the situation falls under the ordinary meaning, no if it does not, or undetermined if the term requires an unspecified scope, relationship, or other missing information. In particular an arbitrary named territory or covered region need not have a determinate ordinary extension. Do not guess to force a binary classification. Return JSON: {"ordinary_answer":"yes|no|undetermined","reason":"brief reason"}.'''
QUALITY = '''Audit a research question against supplied source text, without access to a proposed answer or target model outcomes. Determine its answer under the local source definition. All facts not stated must remain unknown. Check that the question preserves the seed's facts and adds no material premise, the situation is possible, the object being classified is unambiguous, and the supplied source is sufficient. A missing exhibit or unresolved defined term matters if it could change the answer. Check semantic leakage: concrete observations may instantiate a rule, but reject questions that directly assert membership in the target term, reveal the local answer, or simply list abstract definition predicates as given facts. Mere overlap or mentioning a concrete excluded thing is not by itself leakage. Return JSON with booleans facts_preserved, world_consistent, object_clear, source_sufficient, no_answer_leakage, and local_answer (yes|no|undetermined), reason (brief).'''

def read(p):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--config',type=Path,required=True)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--stage',choices=['usual','quality'],required=True)
    p.add_argument('--workers',type=int,default=4)
    a=p.parse_args()
    if not 1<=a.workers<=4: raise ValueError('workers must be 1..4')
    rules={x['definition_id']:x for x in read(a.root/'rules_with_dependencies.jsonl')}
    seeds={x['id']:x for x in read(a.root/'seed_frame/world_seeds_private.jsonl')}
    drafts=read(a.root/'drafts_B.jsonl')
    if a.stage=='quality':
        # Freeze usual labels before any source-aware judge call.
        if len(read(a.root/'usual_labels.jsonl'))!=len(drafts):
            raise ValueError('Complete source-blind usual labels first')
    spec=config_role(a.config,'reader')
    if a.stage=='usual': spec['model']='gpt-6-astra'
    system=USUAL if a.stage=='usual' else QUALITY
    out=a.root/('usual_labels.jsonl' if a.stage=='usual' else 'source_checks.jsonl')
    done={x['id']:x for x in read(out)} if out.exists() else {}
    jobs=[]
    for d in drafts:
        r=rules[d['definition_id']]
        data={'term':r['term'],'question':d['question']}
        if a.stage=='quality':
            data.update(observable_seed=seeds[d['id']]['world_fact'],local_source=r['rule_quote'])
        payload={'model':spec['model'],'messages':[{'role':'system','content':system},{'role':'user','content':canonical(data)}],
                 'temperature':0,'max_tokens':1500,'response_format':{'type':'json_object'}}
        digest=hashlib.sha256(canonical(payload).encode()).hexdigest()
        if d['id'] in done:
            if done[d['id']]['input_sha256']!=digest: raise ValueError('Stale checks; use a new output directory')
            continue
        jobs.append((d,payload,digest))
    def execute(job):
        d,payload,digest=job
        response=request_one(spec,payload)
        parsed=parse_json_object(response['content'])
        field='ordinary_answer' if a.stage=='usual' else 'local_answer'
        if parsed.get(field) not in ['yes','no','undetermined']: raise ValueError('Invalid answer schema')
        if a.stage=='quality' and any(type(parsed.get(k)) is not bool for k in ['facts_preserved','world_consistent','object_clear','source_sufficient','no_answer_leakage']):
            raise ValueError('Invalid boolean schema')
        return {'id':d['id'],'definition_id':d['definition_id'],'input_sha256':digest,'check':parsed,
                'requested_model':spec['model'],'returned_model':response['returned_model'],
                'provider_response_id':response['provider_response_id'],'usage':response['usage'],
                'stage':a.stage,'target_outcomes_seen':False}
    failed=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool,out.open('a') as f:
        fs={pool.submit(execute,j):j[0]['id'] for j in jobs}
        for future in as_completed(fs):
            try: row=future.result()
            except Exception as e:
                failed.append(fs[future]);print('FAILED',fs[future],type(e).__name__,flush=True);continue
            f.write(canonical(row)+'\n');f.flush()
            print(a.stage,row['id'],row['check'],flush=True)
    if failed: raise RuntimeError(f'{len(failed)} checks failed; rerun to resume')

if __name__=='__main__': main()
