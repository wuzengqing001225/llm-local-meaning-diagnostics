#!/usr/bin/env python3
"""Check the old first-token assumption without loading model weights."""
import argparse,json
from pathlib import Path

def inspect(tok):
    rows=[]
    for letter in 'ABCD':
        variants=[]
        for spelling in [letter,' '+letter]:
            ids=tok.encode(spelling,add_special_tokens=False)
            variants.append({'spelling':spelling,'ids':ids,'single_token':len(ids)==1,'first_token_decoded':tok.decode(ids[:1]) if ids else None})
        rows.append({'letter':letter,'variants':variants})
    singles=all(v['single_token'] for r in rows for v in r['variants'])
    firsts=[set(v['ids'][0] for v in r['variants'] if v['ids']) for r in rows]
    collisions=[['ABCD'[i],'ABCD'[j]] for i in range(4) for j in range(i+1,4) if firsts[i]&firsts[j]]
    return {'labels':rows,'all_variants_single_token':singles,'cross_letter_first_token_collisions':collisions,
            'old_first_token_assumption_passes':singles and not collisions,
            'note':'Passing this check does not validate model identity, calibration, or equivalence of max-over-spellings versus full-sequence scoring.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',default='Qwen/Qwen2.5-7B');p.add_argument('--revision',default='main');p.add_argument('--out',default='tokenizer_check.json');a=p.parse_args()
    from transformers import AutoTokenizer
    from huggingface_hub import HfApi
    rev=a.revision
    if not Path(a.model).is_dir():rev=HfApi().model_info(a.model,revision=rev).sha
    tok=AutoTokenizer.from_pretrained(a.model,revision=rev,trust_remote_code=False)
    r={'model':a.model,'revision':rev,**inspect(tok)};Path(a.out).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps(r,ensure_ascii=False,indent=2))
