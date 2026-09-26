#!/usr/bin/env python3
"""Offline verification of frozen inputs and the complete paired response table."""
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parent
def read(name):return [json.loads(x) for x in (ROOT/name).read_text().splitlines() if x.strip()]

def main():
    m=json.loads((ROOT/'freeze_manifest.json').read_text())
    for name,digest in m['sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    public=read('tasks_public.jsonl');private=read('tasks_private.jsonl');rows=read('reader_results.jsonl')
    assert len({x['id'] for x in public})==len(public)==len(private)
    for pub,prv in zip(public,private):
        assert all(prv[k]==v for k,v in pub.items())
        assert not {'gold','source_membership','ordinary_answer','group','hidden_facts'} & pub.keys()
        assert prv['options']['AB'.index(prv['gold'])]==('Yes' if prv['source_membership'] else 'No')
    expected={(r,t['id'],arm) for r in ['gpt_reader','deepseek_reader'] for t in public for arm in ['bare','definition']}
    actual=[(x['role'],x['task_id'],x['arm']) for x in rows]
    assert len(actual)==len(set(actual)) and set(actual)==expected
    assert all(x['finish_reason']=='stop' and x['prediction'] in ['A','B'] for x in rows)
    assert all(x['inference']==m['reader_inference'][x['role']] for x in rows)
    assert all(x['all_quotes_found'] for x in json.loads((ROOT/'source_span_verification.json').read_text()))
    result={'frozen_hashes_verified':len(m['sha256']),'n_tasks':len(public),'paired_requests_verified':len(rows),
            'public_tasks_have_no_gold_or_group':True,'source_quotes_match_originals':True,
            'gold_position_counts':dict(Counter(x['gold'] for x in private)),
            'all_responses_parsed':True,'inference_settings_match_freeze':True}
    (ROOT/'integrity_verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
