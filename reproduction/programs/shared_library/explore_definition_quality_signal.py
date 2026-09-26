#!/usr/bin/env python3
"""Exploratory within-term comparison of two definition texts on old sibling B.

This is NOT an independent quality benchmark: historical B questions were
drafted with access to the community source gloss, which favours that version.
"""
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr, pearsonr, rankdata

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'release_20260923/llm-idf-reproduce/data/reddit/raw_outputs'
A_GOLD = ROOT / 'gold_aligned_development/qwen_A_gold.jsonl'


def load(path):
    return {x['id']: x for x in (json.loads(line) for line in path.open())}


def rows():
    gold = load(A_GOLD)
    auto = load(DATA / 'lpmc_reddit_v2.jsonl')
    eqa = load(DATA / 'reddit_v2_eqa.jsonl')
    weights = load(DATA / 'reddit_v2_weights.jsonl')
    output = []
    for term_id in sorted(gold):
        w = weights[term_id]
        if hashlib.sha256(w['gloss_gold'].encode()).hexdigest() != gold[term_id]['definition_sha256']:
            raise ValueError('Definition A hash mismatch')
        A = range(0, len(eqa[term_id]['questions']), 2)
        B = range(1, len(eqa[term_id]['questions']), 2)
        if not B:
            continue
        auto_delta = statistics.mean(auto[term_id]['per_question'][j]['glossC']['p_correct'] -
                                     auto[term_id]['per_question'][j]['bare']['p_correct'] for j in A)
        questions = eqa[term_id]['questions']
        quality = statistics.mean(questions[j]['correct']['glossG'] - questions[j]['correct']['glossC'] for j in B)
        bare = statistics.mean(questions[j]['correct']['bare'] for j in B)
        output.append({'term_id': term_id, 'community': w['labels']['subreddit'],
                       'A_delta_p_gold_minus_auto': gold[term_id]['mean_delta_p'] - auto_delta,
                       'B_correct_gold_minus_auto': quality, 'B_bare_accuracy': bare,
                       'gold_minus_auto_words': len(w['gloss_gold'].split()) - len(w['gloss_used'].split()),
                       'frequency': w['labels']['tf'], 'n_B': len(B)})
    return output


def auc_binary(y,score):
    positive=sum(y)
    if not positive or positive==len(y):return None
    ranks=rankdata(score)
    return float((sum(r for r,t in zip(ranks,y) if t)-positive*(positive+1)/2)/(positive*(len(y)-positive)))


def main():
    values=rows()
    x=np.array([r['A_delta_p_gold_minus_auto'] for r in values])
    y=np.array([r['B_correct_gold_minus_auto'] for r in values])
    better=int(sum(y>0));worse=int(sum(y<0));ties=int(sum(y==0))
    non_tie=[i for i,v in enumerate(y) if v!=0]
    sign_agree=int(sum((x[i]>0)==(y[i]>0) for i in non_tie))
    raw_spearman=float(spearmanr(x,y).statistic)
    raw_pearson=float(pearsonr(x,y).statistic)
    # A descriptive residual correlation after three obvious shared covariates.
    Z=np.array([[1,r['gold_minus_auto_words'],r['B_bare_accuracy'],math.log1p(r['frequency'])]
                for r in values],dtype=float)
    residual_x=x-Z@np.linalg.lstsq(Z,x,rcond=None)[0]
    residual_y=y-Z@np.linalg.lstsq(Z,y,rcond=None)[0]
    residual_pearson=float(pearsonr(residual_x,residual_y).statistic)
    groups=defaultdict(list)
    for r in values:groups[r['community']].append(r)
    names=sorted(groups);rng=random.Random(260926);draws=[]
    for _ in range(3000):
        sample=[r for name in rng.choices(names,k=len(names)) for r in groups[name]]
        xx=[r['A_delta_p_gold_minus_auto'] for r in sample]
        yy=[r['B_correct_gold_minus_auto'] for r in sample]
        s=spearmanr(xx,yy).statistic
        if np.isfinite(s):draws.append(float(s))
    draws.sort()
    result={'status':'EXPLORATORY_OLD_B_DRAFTED_FROM_GOLD_GLOSS',
            'n_terms':len(values),'n_communities':len(names),'B_gold_better_terms':better,
            'B_auto_better_terms':worse,'B_tied_terms':ties,
            'mean_A_delta_p_gold_minus_auto':float(x.mean()),
            'mean_B_correct_gold_minus_auto':float(y.mean()),
            'spearman_all_terms':raw_spearman,
            'community_cluster_bootstrap_95_for_spearman':[draws[round(.025*(len(draws)-1))],draws[round(.975*(len(draws)-1))]],
            'pearson_all_terms':raw_pearson,'pearson_after_linear_residualization_of_length_bare_accuracy_log_frequency':residual_pearson,
            'non_tied_B_terms':len(non_tie),'sign_agreement_non_tied':sign_agree,
            'AUROC_gold_better_vs_auto_better_among_non_ties':auc_binary([int(y[i]>0) for i in non_tie],[x[i] for i in non_tie]),
            'limitation':'Question generation used the source gloss; 161/215 terms tie on 1-2 B questions. Association does not validate Δp as a causal or source-invariant quality metric.'}
    path=ROOT/'gold_aligned_development/definition_quality_signal.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['n_terms','B_gold_better_terms','B_auto_better_terms','B_tied_terms','spearman_all_terms','community_cluster_bootstrap_95_for_spearman','non_tied_B_terms','sign_agreement_non_tied','AUROC_gold_better_vs_auto_better_among_non_ties']},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
