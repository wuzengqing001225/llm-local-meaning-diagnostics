#!/usr/bin/env python3
"""Exploratory deletion sensitivity on historical matched questions.

Only the audited sample IDs are removed. Unreviewed questions remain under
their historical keys, so stability here cannot validate the full dataset.
"""
import json
import math
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
DATA=ROOT/'outputs/release_20260923/llm-idf-reproduce/data'
PRIVATE=HERE.parent/'historical_blind_audit_20260926_private'
SETTINGS=[
 ('Synthetic / DeepSeek','synthetic','synthetic_v1/raw_outputs/lpmc_v1.jsonl','synthetic_v1/raw_outputs/v1_eqa.jsonl',False),
 ('Synthetic / GPT6','synthetic','synthetic_v1/raw_outputs/lpmc_v1.jsonl','synthetic_v1/raw_outputs/astra6_v1_eqa.jsonl',False),
 ('Reddit / DeepSeek','reddit','reddit/raw_outputs/lpmc_reddit.jsonl','reddit/raw_outputs/reddit_eqa.jsonl',False),
 ('Reddit / GPT6','reddit','reddit/raw_outputs/lpmc_reddit.jsonl','reddit/raw_outputs/astra6_reddit_eqa.jsonl',False),
 ('DeFi / DeepSeek','defi','defi/raw_outputs/defi_strict_lpmc.jsonl','defi/raw_outputs/defi_strict_eqa.jsonl',False),
 ('DeFi / GPT5.6','defi','defi/raw_outputs/defi_strict_lpmc.jsonl','defi/raw_outputs/defi_strict_eqa_gpt.jsonl',False),
 ('DeFi / GPT6','defi','defi/raw_outputs/defi_strict_lpmc.jsonl','defi/raw_outputs/astra6_defi_strict_eqa.jsonl',False),
 ('CUAD / GPT5.6','cuad','cuad/raw_outputs/lpmc_full.jsonl','cuad/raw_outputs/t2_answers.jsonl',True)]

def read(path):return [json.loads(s) for s in path.read_text().splitlines() if s.strip()]

def auc(rows,label,score,weight=None):
    pairs=sorted((r[score],r[label],r.get(weight,1.0) if weight else 1.0) for r in rows)
    pos=neg=total=0.0;i=0
    while i<len(pairs):
        j=i;wp=wn=0.0
        while j<len(pairs) and pairs[j][0]==pairs[i][0]:
            _,y,w=pairs[j];wp+=w*y;wn+=w*(1-y);j+=1
        total+=wp*(neg+wn/2);pos+=wp;neg+=wn;i=j
    return total/(pos*neg) if pos*neg else None

def pair(corpus,proxy_path,reader_path,context_match):
    proxy=read(DATA/proxy_path);reader={x['id']:x for x in read(DATA/reader_path)}
    rows=[]
    for term in proxy:
        tid=term['id'];e=reader.get(tid)
        if e is None:continue
        eq=e.get('questions') or []
        all_scored=term.get('per_question') or []
        all_pd=[v['glossC']['p_correct']-v['bare']['p_correct'] for v in all_scored]
        for j,p in enumerate(all_scored):
            if corpus=='synthetic' and (tid,j)==('v1:desk:interest',1):
                continue
            matches=[q for q in eq if str(q.get('ctx_idx'))==str(p.get('ctx_idx'))] if context_match else eq[j:j+1]
            if len(matches)!=1:continue
            q=matches[0]
            if not (q.get('q','').startswith(p.get('q','')) or p.get('q','').startswith(q.get('q',''))):
                continue
            c=q.get('correct') or {}
            if c.get('bare') is None or c.get('glossC') is None:continue
            qi=str(q.get('ctx_idx')) if context_match else str(j)
            sibling=[value for k,value in enumerate(all_pd)
                     if k!=j and (not context_match or
                                  str(all_scored[k].get('ctx_idx'))!=str(p.get('ctx_idx')))]
            rows.append({'source_qid':corpus+':'+tid+':'+qi,
                         'term_id':tid,'ctx_idx':qi,
                         'cluster':':'.join(tid.split(':')[:2]) if corpus in ('reddit','cuad') else tid,
                         'risk':1-p['bare']['p_correct'],
                         'pd':p['glossC']['p_correct']-p['bare']['p_correct'],
                         'sibling_pd':sum(sibling)/len(sibling) if sibling else None,
                         'bare_error':1-int(c['bare']),
                         'definition_error':1-int(c['glossC']),
                         'repair':int(c['bare']==0 and c['glossC']==1)})
    if context_match:
        # The reported CUAD other-item column keeps only evaluated items with
        # another matched validation question from the term, while averaging
        # scores over all proxy-scored occurrences in that term record.
        matched_contexts={}
        for r in rows:matched_contexts.setdefault(r['term_id'],set()).add(r['ctx_idx'])
        for r in rows:
            if len(matched_contexts[r['term_id']]-{r['ctx_idx']})==0:
                r['sibling_pd']=None
    return rows,proxy

def metrics(rows,weighted=False):
    failed=[r for r in rows if r['bare_error']]
    siblings=[r for r in failed if r['sibling_pd'] is not None]
    w='weight' if weighted else None
    sw=sum(r.get(w,1) if w else 1 for r in rows)
    return {'n':len(rows),'bare_failures':len(failed),
            'bare_error_rate':sum(r['bare_error']*(r.get(w,1) if w else 1) for r in rows)/sw,
            'definition_error_rate':sum(r['definition_error']*(r.get(w,1) if w else 1) for r in rows)/sw,
            'risk_error_auroc':auc(rows,'bare_error','risk',w),
            'pd_error_auroc':auc(rows,'bare_error','pd',w),
            'conditional_repair_risk_auroc':auc(failed,'repair','risk',w),
            'conditional_repair_pd_auroc':auc(failed,'repair','pd',w),
            'conditional_repair_sibling_pd_n':len(siblings),
            'conditional_repair_sibling_pd_auroc':auc(siblings,'repair','sibling_pd',w)}

def synthetic_stability(exclude_qids):
    u=read(DATA/'synthetic_v1/raw_outputs/unc_v1.jsonl')
    e={r['id']:r for r in read(DATA/'synthetic_v1/raw_outputs/v1_eqa.jsonl')}
    direct_conflicts={('v1:desk:interest',1),('v1:desk:interest@mix0.7',0)}
    n=errors=stable_wrong=0
    for term in u:
        tid=term['id']
        for j,p in enumerate(term.get('per_question') or []):
            if (tid,j) in direct_conflicts or 'synthetic:'+tid+':'+str(j) in exclude_qids:
                continue
            q=e[tid]['questions'][j]
            failed=int(q['correct']['bare']==0);n+=1;errors+=failed
            votes=p['votes']
            if failed and len(votes)==1 and next(iter(votes.values()))==10 and next(iter(votes))!=q['answer']:
                stable_wrong+=1
    return {'n':n,'greedy_errors':errors,'ten_identical_wrong':stable_wrong,
            'fraction_of_greedy_errors':stable_wrong/errors}

def main():
    audit=read(PRIVATE/'sonnet5_deepseek_cross_private.jsonl')
    sets={
      'priority_17':{r['source_qid'] for r in audit if r['human_priority']},
      'all_model_not_confirmed_41':{r['source_qid'] for r in audit if r['category']!='both_support_stored_key'},
      'both_insufficient_24':{r['source_qid'] for r in audit if r['category']=='both_insufficient_or_ambiguous'}}
    report={'status':'EXPLORATORY_SAMPLE_ONLY_EXCLUSION_NOT_SOURCE_ADJUDICATION',
            'exclusion_counts':{k:len(v) for k,v in sets.items()},'settings':[],
            'synthetic_stable_wrong':{'original':synthetic_stability(set()),
                                      **{k:synthetic_stability(v) for k,v in sets.items()}}}
    for name,corpus,proxy_path,reader_path,ctx in SETTINGS:
        rows,proxy=pair(corpus,proxy_path,reader_path,ctx)
        # CUAD uses the same original 300-per-risk-bin sample weights.
        if corpus=='cuad':
            frame=Counter(min(4,int((1-p['bare']['p_correct'])*5))
                          for term in proxy for p in term.get('per_question') or [])
            for r in rows:r['weight']=frame[min(4,int(r['risk']*5))]/300
        out={'setting':name,'corpus':corpus,'original':metrics(rows),
             'deletions':{}}
        if corpus=='cuad':out['original_weighted_cuad']=metrics(rows,True)
        for label,ids in sets.items():
            left=[r for r in rows if r['source_qid'] not in ids]
            dropped=len(rows)-len(left)
            result={'audited_sample_items_removed':dropped,'retained':metrics(left)}
            if corpus=='cuad':result['retained_weighted_cuad']=metrics(left,True)
            out['deletions'][label]=result
        report['settings'].append(out)
    report['limits']=[
      'Only 80 sampled historical questions were source screened; excluding their flags from 3,726+ questions cannot validate unreviewed keys.',
      'Screening judgments are model-generated, not independent human corrections.',
      'All proxy p_correct values refer to the old key. Flagged items are removed, never relabeled using old probabilities.',
      'The CUAD weighted rows retain original design weights only as deletion sensitivity, not a population estimate for source-valid items.',
      'The stable-wrong calculation uses the corrected 761-item uncertainty frame, which differs from the 456-item directly matched prediction frame.']
    out=HERE/'sonnet5_deepseek_sample_exclusion_sensitivity.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for row in report['settings']:
        ori=row['original'];r=row['deletions']['all_model_not_confirmed_41']['retained']
        print(row['setting'],f"n {ori['n']} -> {r['n']}",
              f"R {ori['risk_error_auroc']:.3f} -> {r['risk_error_auroc']:.3f}",
              f"conditional Δp {ori['conditional_repair_pd_auroc']:.3f} -> {r['conditional_repair_pd_auroc']:.3f}",
              f"sibling Δp {ori['conditional_repair_sibling_pd_auroc']:.3f} -> {r['conditional_repair_sibling_pd_auroc']:.3f}")
    print(out)

if __name__=='__main__':main()
