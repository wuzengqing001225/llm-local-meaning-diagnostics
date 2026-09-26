#!/usr/bin/env python3
"""Evaluate a frozen allocation plan against B gold and paired reader outputs."""

import argparse
import collections
import json
import statistics
from pathlib import Path


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--gold-tasks', type=Path, required=True)
    p.add_argument('--gold-file', type=Path,
                   help='Formal private gold JSONL; all rows must have accepted quality review.')
    p.add_argument('--predictions', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text())
    if plan['status'] != 'frozen_development_allocation_plan_no_B_gold_read':
        raise ValueError('Wrong plan status')
    gold = {x['id']: x for x in read_jsonl(a.gold_tasks)}
    if a.gold_file:
        private = {x['id']: x for x in read_jsonl(a.gold_file)}
        if set(private) != set(gold):
            raise ValueError('Public task and private gold coverage differs')
        if any(x.get('quality_review_status') != 'accepted' for x in private.values()):
            raise ValueError('Formal B gold has pending or rejected quality review')
        gold = {tid: {**task, 'answer': private[tid]['answer']} for tid, task in gold.items()}
    if set(gold) != set(plan['costs_by_task']):
        raise ValueError('Plan/gold task coverage differs')
    predictions = collections.defaultdict(dict)
    for row in read_jsonl(a.predictions):
        key = (row['role'], row['task_id'])
        if row['arm'] in predictions[key]:
            raise ValueError('Duplicate role/task/arm prediction')
        predictions[key][row['arm']] = row['prediction']
    roles = sorted({x[0] for x in predictions})
    for role in roles:
        for task_id in gold:
            if set(predictions.get((role, task_id), {})) != {'bare', 'definition'}:
                raise ValueError(f'Incomplete predictions: {role}, {task_id}')
            if not all(x in {'A', 'B'} for x in predictions[(role, task_id)].values()):
                raise ValueError(f'Unparsed prediction: {role}, {task_id}')
    results = []
    for role in roles:
        bare_correct = {tid: predictions[(role, tid)]['bare'] == task['answer'] for tid, task in gold.items()}
        full_correct = {tid: predictions[(role, tid)]['definition'] == task['answer'] for tid, task in gold.items()}
        base_accuracy = sum(bare_correct.values()) / len(gold)
        full_accuracy = sum(full_correct.values()) / len(gold)
        for allocation in plan['allocations']:
            selected = set(allocation['selected_task_ids'])
            if len(selected) != allocation['selected_count'] or not selected <= set(gold):
                raise ValueError('Invalid allocation coverage')
            if sum(plan['costs_by_task'][x] for x in selected) != allocation['spent_tokens']:
                raise ValueError('Allocation cost mismatch')
            if allocation['spent_tokens'] > allocation['budget_tokens']:
                raise ValueError('Over-budget policy')
            outcome = {tid: (full_correct[tid] if tid in selected else bare_correct[tid]) for tid in gold}
            repairs = sum(not bare_correct[tid] and outcome[tid] for tid in gold)
            harms = sum(bare_correct[tid] and not outcome[tid] for tid in gold)
            results.append({
                'role': role, 'fraction': allocation['budget_fraction'],
                'policy': allocation['policy'], 'n': len(gold),
                'accuracy': sum(outcome.values()) / len(gold),
                'bare_accuracy': base_accuracy, 'full_accuracy': full_accuracy,
                'repairs': repairs, 'harms': harms,
                'net_gain_pp': 100 * (repairs - harms) / len(gold),
                'selected_count': allocation['selected_count'],
                'spent_tokens': allocation['spent_tokens'],
                'budget_tokens': allocation['budget_tokens'],
            })
    result = {
        'status': ('formal_budget_result_from_quality_accepted_B' if a.gold_file
                   else 'development_only_not_confirmatory'),
        'plan_path': str(a.plan), 'gold_tasks_path': str(a.gold_tasks),
        'predictions_path': str(a.predictions),
        'n_tasks': len(gold), 'roles': roles, 'results': results,
        'caveats': (['Random policy is averaged over 20 prespecified shuffles.',
                     'The full-cost all-matched arm is a reference, not an equal-budget comparator.']
                    if a.gold_file else
                    ['Only five rules and two bare errors per reader.',
                     'A and B are controlled examples from one generator.',
                     'No contract-cluster interval is meaningful at five contracts.',
                     'Random policy is averaged over 20 prespecified shuffles.',
                     'The full-cost all-matched arm is a reference, not an equal-budget comparator.']),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    lines = ['# V5 ' + ('formal' if a.gold_file else 'development') + ' budget check', '',
             ('The plan was frozen without loading B gold or reader outcomes. '
              'Formal interpretation still requires prespecified cluster intervals and full cost accounting.'
              if a.gold_file else
              '**Exploratory only.** The plan was frozen without loading B gold or reader outcomes. '
              'The same five-rule pilot and paired outputs are evaluated here.'), '',
             '| Reader | Budget | Policy | Accuracy | Repairs | Harms | Notes |',
             '| --- | ---: | --- | ---: | ---: | ---: | ---: |']
    for role in roles:
        for frac in (0.25, 0.5, 0.75):
            rows = [x for x in results if x['role'] == role and x['fraction'] == frac]
            for policy in ('matched_fixed', 'dp', 'R', 'dp_per_token'):
                row = next(x for x in rows if x['policy'] == policy)
                lines.append(f"| {role} | {frac:.0%} | {policy} | {row['accuracy']:.3f} | {row['repairs']} | {row['harms']} | {row['spent_tokens']} |")
            random_rows = [x for x in rows if x['policy'].startswith('random_')]
            lines.append(f"| {role} | {frac:.0%} | random mean (20) | {statistics.mean(x['accuracy'] for x in random_rows):.3f} | {statistics.mean(x['repairs'] for x in random_rows):.2f} | {statistics.mean(x['harms'] for x in random_rows):.2f} | {statistics.mean(x['spent_tokens'] for x in random_rows):.1f} |")
    if not a.gold_file:
        lines.extend(['', 'The development set is too small and too easy to establish a policy advantage. '
                      'Use this output to verify accounting and choose the formal source-quality gate, not to make a paper claim.', ''])
    a.out.with_suffix('.md').write_text('\n'.join(lines))
    print(f'Evaluated {len(results)} policy-reader-budget rows across {len(roles)} readers.')


if __name__ == '__main__':
    main()
