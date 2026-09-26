#!/usr/bin/env python3
"""Read gold-free frozen tasks only, run both arms with resumable requests."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
from pathlib import Path
import random
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'local_meaning_v5_development'))
from run_reader_dev import config_role,request_one,prompt,canonical,sha,read_jsonl

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    if not 1<=a.workers<=4:raise ValueError('workers must be 1..4')
    manifest=json.loads((a.root/'freeze_manifest.json').read_text())
    for file,digest in manifest['sha256'].items():
        if hashlib.sha256((a.root/file).read_bytes()).hexdigest()!=digest:raise ValueError('Frozen input changed: '+file)
    tasks=read_jsonl(a.root/'tasks_public.jsonl')
    rules={x['definition_id']:x for x in read_jsonl(a.root/'rules_with_dependencies.jsonl')}
    specs={'gpt_reader':config_role(a.config,'reader'),'deepseek_reader':config_role(a.config,'draft')}
    out=a.root/'reader_results.jsonl'
    existing={x['request_id'] for x in read_jsonl(out)} if out.exists() else set()
    jobs=[]
    for role,spec in specs.items():
        for item in tasks:
            for arm in ['bare','definition']:
                text=prompt(item,rules[item['definition_id']]['rule_quote'] if arm=='definition' else None)
                payload={'model':spec['model'],'messages':[{'role':'system','content':'You answer multiple-choice research questions about a contract. Choose one option letter.'},{'role':'user','content':text}],**manifest['reader_inference'][role]}
                rid=sha({'role':role,'endpoint':spec['base_url'],'task':item['id'],'arm':arm,'payload':payload})
                if rid not in existing:jobs.append((rid,role,item['id'],arm,spec,payload))
    random.Random(20260925).shuffle(jobs)
    def execute(job):
        rid,role,sid,arm,spec,payload=job;start=time.monotonic()
        response=request_one(spec,payload)
        return {'request_id':rid,'role':role,'task_id':sid,'arm':arm,'requested_model':spec['model'],
                'prompt_sha256':sha(payload),'inference':manifest['reader_inference'][role],
                'elapsed_seconds':time.monotonic()-start,'status':'development_only',**response}
    failed=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool,out.open('a') as f:
        fs={pool.submit(execute,j):j[0] for j in jobs}
        for i,future in enumerate(as_completed(fs),1):
            try:row=future.result()
            except Exception as e:failed.append(fs[future]);print('FAILED',type(e).__name__,flush=True);continue
            f.write(canonical(row)+'\n');f.flush()
            print(i,'/',len(jobs),row['role'],row['arm'],row['task_id'],row['prediction'],flush=True)
    if failed:raise RuntimeError(f'{len(failed)} calls failed; rerun the same command to resume')

if __name__=='__main__':main()
