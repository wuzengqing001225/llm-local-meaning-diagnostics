#!/usr/bin/env python3
"""Offline check: does R also rank errors on designed prior-consistent terms?"""
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'historical_blind_audit_20260926'))
from sensitivity_exclude_screened import SETTINGS,pair,auc

def cluster_interval(rows,seed=260926,B=3000):
    groups=defaultdict(list)
    for r in rows:groups[r['term_id']].append(r)
    clusters=list(groups.values());rng=random.Random(seed);values=[]
    for _ in range(B):
        sample=[r for _ in clusters for r in clusters[rng.randrange(len(clusters))]]
        a=auc(sample,'bare_error','risk')
        if a is not None:values.append(a)
    values.sort()
    return [values[int(.025*(len(values)-1))],values[int(.975*(len(values)-1))]] if values else None

def main():
    data=ROOT/'release_20260923/llm-idf-reproduce/data/synthetic_v1/inputs/v1_terms.jsonl'
    labels={r['id']:r['labels'].get('quadrant') for r in (json.loads(s) for s in data.read_text().splitlines())}
    report={'status':'DESIGNED_CLASS_CONTROL_NOT_HUMAN_MECHANISM_LABELS','readers':{}}
    for name,corpus,proxy,reader,ctx in SETTINGS:
        if corpus!='synthetic':continue
        rows,_=pair(corpus,proxy,reader,ctx)
        result={}
        for group in ('prior_conflict','prior_consistent','no_prior'):
            rr=[r for r in rows if labels[r['term_id']]==group]
            result[group]={'n':len(rr),'term_records':len({r['term_id'] for r in rr}),
                           'reader_bare_errors':sum(r['bare_error'] for r in rr),
                           'R_error_auroc':auc(rr,'bare_error','risk'),
                           'term_bootstrap_95':cluster_interval(rr)}
        report['readers'][name]=result
    report['interpretation']='R ranks errors even when the source meaning is designed to be prior-consistent. This is evidence against calling R a meaning-conflict-specific detector. It does not estimate the mixture of error mechanisms in real corpora.'
    (HERE/'synthetic_mechanism_control.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for name,groups in report['readers'].items():
        print(name,[(k,v['n'],v['reader_bare_errors'],round(v['R_error_auroc'],3),v['term_bootstrap_95']) for k,v in groups.items()])

if __name__=='__main__':main()
