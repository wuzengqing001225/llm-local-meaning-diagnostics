#!/usr/bin/env python3
"""Paired contract-cluster analysis of a frozen formal V5 budget plan."""

import argparse
import collections
import hashlib
import json
import random
import statistics
from pathlib import Path

import numpy as np
from scipy.stats import rankdata


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def auc(rows, target, score):
    y = np.array([x[target] for x in rows])
    s = np.array([x[score] for x in rows])
    pos = int(y.sum())
    if pos == 0 or pos == len(y):
        return None
    return float((rankdata(s)[y == 1].sum() - pos * (pos + 1) / 2) / (pos * (len(y) - pos)))


def cluster_interval(rows, statistic, replicates=2000, seed=20260925):
    groups = collections.defaultdict(list)
    for x in rows:
        groups[x['contract_index']].append(x)
    keys = sorted(groups)
    if len(keys) < 2:
        return None
    rng = random.Random(seed)
    values = []
    for _ in range(replicates):
        sample = [x for key in rng.choices(keys, k=len(keys)) for x in groups[key]]
        value = statistic(sample)
        if value is not None:
            values.append(value)
    return [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))] if values else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--public', type=Path, required=True)
    p.add_argument('--private-gold', type=Path, required=True)
    p.add_argument('--predictions', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--replicates', type=int, default=2000)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text())
    public = {x['id']: x for x in read(a.public)}
    gold = {x['id']: x for x in read(a.private_gold)}
    if set(public) != set(gold) or set(public) != set(plan['costs_by_task']):
        raise ValueError('Plan/public/gold task coverage mismatch')
    if plan['inputs']['public_tasks_sha256'] != hashlib.sha256(a.public.read_bytes()).hexdigest():
        raise ValueError('Budget plan was made from a different public B file')
    if any(x.get('status') != 'accepted_formal_B' for x in public.values()):
        raise ValueError('Public B contains unaccepted tasks')
    if any(x.get('quality_review_status') != 'accepted' for x in gold.values()):
        raise ValueError('Private B gold contains unaccepted tasks')
    preds = collections.defaultdict(dict)
    models = collections.defaultdict(set)
    for row in read(a.predictions):
        if row['task_id'] not in public:
            continue
        if row.get('status') != 'formal_reader_condition' or row['prediction'] not in {'A', 'B'}:
            raise ValueError('Incomplete or nonformal reader result')
        key = (row['role'], row['task_id'])
        if row['arm'] in preds[key]:
            raise ValueError('Duplicate formal reader condition')
        preds[key][row['arm']] = row
        models[row['role']].add(row['returned_model'])
    if len(models) < 2 or any(len(v) != 1 for v in models.values()):
        raise ValueError('Need two distinct stable reader roles')
    if len({next(iter(v)) for v in models.values()}) != len(models):
        raise ValueError('Reader roles did not return distinct models')
    alloc = {(x['budget_fraction'], x['policy']): x for x in plan['allocations']}
    primary_dp = set(alloc[(0.5, 'dp')]['selected_task_ids'])
    primary_match = set(alloc[(0.5, 'matched_fixed')]['selected_task_ids'])
    result = {'status': 'formal_paired_analysis_from_frozen_plan',
              'n_tasks': len(public), 'n_contracts': len({x['contract_index'] for x in public.values()}),
              'cohorts': dict(collections.Counter(x['cohort'] for x in public.values())),
              'reader_models': {k: next(iter(v)) for k,v in models.items()},
              'primary_budget_fraction': 0.5,
              'primary_comparison': 'dp_A versus feasible fixed-order matched notes',
              'contract_bootstrap_replicates': a.replicates,
              'readers': {},
              'limitations': ['Generated source-sampled requests do not estimate natural user traffic.',
                              'Conditional repair AUROC concerns only known bare failures.',
                              'A construction/review costs must be added to a deployment cost analysis.']}
    for role in sorted(models):
        rows = []
        for task_id, task in public.items():
            arms = preds.get((role, task_id), {})
            if set(arms) != {'bare', 'definition'}:
                raise ValueError('Missing paired formal reader result: ' + role + ':' + task_id)
            bare = arms['bare']['prediction'] == gold[task_id]['answer']
            defined = arms['definition']['prediction'] == gold[task_id]['answer']
            dp_correct = defined if task_id in primary_dp else bare
            matched_correct = defined if task_id in primary_match else bare
            u0 = (arms['bare'].get('usage') or {}).get('prompt_tokens')
            u1 = (arms['definition'].get('usage') or {}).get('prompt_tokens')
            rows.append({'task_id': task_id, 'definition_id': task['definition_id'],
                         'contract_index': task['contract_index'], 'cohort': task['cohort'],
                         'bare_correct': int(bare), 'defined_correct': int(defined),
                         'repair': int(not bare and defined), 'harm': int(bare and not defined),
                         'dp_correct': int(dp_correct), 'matched_correct': int(matched_correct),
                         'policy_delta': int(dp_correct) - int(matched_correct),
                         'dp_A': plan['term_stats'][task['definition_id']]['mean_dp'],
                         'actual_note_prompt_tokens': u1 - u0 if isinstance(u0,int) and isinstance(u1,int) else None})
        estimate = statistics.mean(x['policy_delta'] for x in rows)
        ci = cluster_interval(rows, lambda rs: statistics.mean(x['policy_delta'] for x in rs), a.replicates)
        bare_wrong = [x for x in rows if not x['bare_correct']]
        conditional_auc = auc(bare_wrong, 'repair', 'dp_A') if bare_wrong else None
        conditional_ci = cluster_interval(bare_wrong, lambda rs: auc(rs,'repair','dp_A'), a.replicates)
        unconditional_auc = auc(rows, 'repair', 'dp_A')
        result['readers'][role] = {
            'n': len(rows), 'contracts': len({x['contract_index'] for x in rows}),
            'bare_accuracy': statistics.mean(x['bare_correct'] for x in rows),
            'all_matched_full_cost_accuracy': statistics.mean(x['defined_correct'] for x in rows),
            'dp_50_accuracy': statistics.mean(x['dp_correct'] for x in rows),
            'matched_50_accuracy': statistics.mean(x['matched_correct'] for x in rows),
            'dp_minus_matched_accuracy': estimate,
            'dp_minus_matched_contract_ci': ci,
            'practical_5pp_threshold_met': estimate >= 0.05,
            'statistical_ci_above_zero': bool(ci and ci[0] > 0),
            'all_matched_repairs': sum(x['repair'] for x in rows),
            'all_matched_harms': sum(x['harm'] for x in rows),
            'dp_selected_notes': len(primary_dp),
            'matched_selected_notes': len(primary_match),
            'dp_proxy_tokens': alloc[(0.5,'dp')]['spent_tokens'],
            'matched_proxy_tokens': alloc[(0.5,'matched_fixed')]['spent_tokens'],
            'full_proxy_tokens': plan['full_matched_cost_tokens'],
            'mean_actual_note_prompt_tokens': statistics.mean(x['actual_note_prompt_tokens'] for x in rows if x['actual_note_prompt_tokens'] is not None)
                                              if any(x['actual_note_prompt_tokens'] is not None for x in rows) else None,
            'conditional_repair_n_bare_wrong': len(bare_wrong),
            'conditional_repair_AUC_dp_A': conditional_auc,
            'conditional_repair_contract_ci': conditional_ci,
            'unconditional_repair_AUC_dp_A': unconditional_auc,
            'rows': rows,
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    lines = ['# V5 formal paired result', '',
             'The primary comparison uses a frozen 50% shared note budget and contract-cluster bootstrap. '
             'The 5 percentage-point practical threshold and CI-above-zero are reported separately.', '',
             '| Reader | n | Bare | Full matched | Δp 50% | Matched 50% | Δp−matched [95% contract CI] |',
             '| --- | ---: | ---: | ---: | ---: | ---: | --- |']
    for role, x in result['readers'].items():
        bounds = x['dp_minus_matched_contract_ci']
        ci_text = f"[{bounds[0]:+.3f},{bounds[1]:+.3f}]" if bounds else 'unavailable'
        lines.append(f"| {role} | {x['n']} | {x['bare_accuracy']:.3f} | {x['all_matched_full_cost_accuracy']:.3f} | "
                     f"{x['dp_50_accuracy']:.3f} | {x['matched_50_accuracy']:.3f} | "
                     f"{x['dp_minus_matched_accuracy']:+.3f} {ci_text} |")
    lines.extend(['', 'Conditional repair AUC uses only bare failures; the budget outcome uses all B tasks. '
                  'Before writing broad claims, inspect task/source audit failures, actual costs, and the source-sampled cohort separately.', ''])
    a.out.with_suffix('.md').write_text('\n'.join(lines))
    print('Formal paired analysis complete for',len(result['readers']),'readers.')


if __name__ == '__main__':
    main()
