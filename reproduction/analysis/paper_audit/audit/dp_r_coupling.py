#!/usr/bin/env python3
"""Offline analysis of the algebraic relationship between R and delta p."""
import json
import math
import statistics
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'historical_blind_audit_20260926'))
from sensitivity_exclude_screened import SETTINGS,pair,auc

def mean(xs):return sum(xs)/len(xs) if xs else None

def rank_within_r_deciles(rows,score):
    ordered=sorted(rows,key=lambda r:r['risk'])
    buckets=[[] for _ in range(10)]
    for i,r in enumerate(ordered):buckets[min(9,(i*10)//len(ordered))].append(r)
    numerator=denominator=0.0;valid=0
    for bucket in buckets:
        positives=sum(r['bare_error'] for r in bucket)
        pairs=positives*(len(bucket)-positives)
        if not pairs:continue
        a=auc(bucket,'bare_error',score)
        numerator+=pairs*a;denominator+=pairs;valid+=1
    return {'auc':numerator/denominator if denominator else None,
            'cross_class_pairs':int(denominator),'informative_deciles':valid}

def main():
    report={'status':'DESCRIPTIVE_OFFLINE_CONTROL_NOT_CAUSAL_SIGNAL_SEPARATION',
            'identity':'delta_p = R + p_definition - 1; hence R-1 <= delta_p <= R for option probabilities in [0,1]',
            'settings':[]}
    for name,corpus,proxy,reader,ctx in SETTINGS:
        rows,_=pair(corpus,proxy,reader,ctx)
        for r in rows:
            r['p0']=1-r['risk'];r['p_definition']=r['p0']+r['pd']
            if not -1e-8<=r['p_definition']<=1+1e-8 or not r['risk']-1-1e-8<=r['pd']<=r['risk']+1e-8:
                raise ValueError('Probability identity/bounds failed: '+name)
        bad=[r for r in rows if r['bare_error']]
        good=[r for r in rows if not r['bare_error']]
        group=lambda rr:{'n':len(rr),'mean_R':mean([r['risk'] for r in rr]),
           'mean_p_definition':mean([r['p_definition'] for r in rr]),
           'mean_delta_p':mean([r['pd'] for r in rr]),
           'delta_p_positive_fraction':mean([r['pd']>0 for r in rr])}
        out={'setting':name,'corpus':corpus,'n':len(rows),
             'R_error_auroc':auc(rows,'bare_error','risk'),
             'delta_p_error_auroc':auc(rows,'bare_error','pd'),
             'p_definition_error_auroc':auc(rows,'bare_error','p_definition'),
             'spearman_R_delta_p':None,
             'bare_error_items':group(bad),'bare_correct_items':group(good),
             'R_decile_matched_delta_p':rank_within_r_deciles(rows,'pd'),
             'R_decile_matched_p_definition':rank_within_r_deciles(rows,'p_definition')}
        from scipy.stats import spearmanr
        out['spearman_R_delta_p']=float(spearmanr([r['risk'] for r in rows],[r['pd'] for r in rows]).statistic)
        report['settings'].append(out)
    report['interpretation']=[
       'The two AUCs in the manuscript use the same items and target; a paired interval describes a predictive ranking contrast, not two independent signals.',
       'A raw delta_p AUC below 0.5 means that, in this observed setting, low delta_p tends to accompany bare reader errors; it is not a sign error in the formula.',
       'Within-R-decile AUC conditions approximately on proxy bare-answer risk. It remains a descriptive check because binning does not remove all difficulty or selection confounding.',
       'The identity decomposes the mean delta_p contrast into mean R and post-definition support contrasts. No causal mechanism is established by this decomposition.']
    dest=HERE/'dp_r_coupling.json'
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    for row in report['settings']:
        b=row['bare_error_items'];g=row['bare_correct_items'];m=row['R_decile_matched_delta_p']
        print(row['setting'], 'AUC',round(row['delta_p_error_auroc'],3),
              'delta-means',round(b['mean_delta_p'],3),round(g['mean_delta_p'],3),
              'pdef-means',round(b['mean_p_definition'],3),round(g['mean_p_definition'],3),
              'R-bin AUC',round(m['auc'],3) if m['auc'] is not None else None)
    print(dest)

if __name__=='__main__':main()
