#!/usr/bin/env python3
"""Freeze note-allocation plans without loading B gold or reader outcomes."""

import argparse
import collections
import hashlib
import json
import random
import statistics
from pathlib import Path


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def sha_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def random_key(value):
    return hashlib.sha256(value.encode()).hexdigest()


def select(sorted_ids, costs, budget):
    result, spent = [], 0
    for task_id in sorted_ids:
        cost = costs[task_id]
        if spent + cost <= budget:
            result.append(task_id)
            spent += cost
    return result, spent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--public-tasks', type=Path, required=True,
                   help='B tasks without answers or oracle traces')
    p.add_argument('--cards', type=Path, required=True)
    p.add_argument('--scores-a', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    tasks = read_jsonl(args.public_tasks)
    cards = {x['definition_id']: x for x in read_jsonl(args.cards)}
    scores = collections.defaultdict(list)
    for row in read_jsonl(args.scores_a):
        did = row.get('definition_id') or row['id'].split(':a_')[0].split('A:')[1]
        scores[did].append(row)
    if not tasks or len({x['id'] for x in tasks}) != len(tasks):
        raise ValueError('Public B tasks must be nonempty and unique')
    if any(x.get('status') not in {'unreviewed_development_item', 'accepted_formal_B'} for x in tasks):
        raise ValueError('Budget planning received B drafts before the quality gate')
    for task in tasks:
        if {'answer', 'oracle_membership', 'oracle_trace'} & task.keys():
            raise ValueError('Planner received gold or oracle fields')
        if task['definition_id'] not in cards or len(scores[task['definition_id']]) < 4:
            raise ValueError('Missing source rule or at least four A scores for ' + task['id'])
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B',
        revision='d149729398750b98c0af14eb82c78cfe92750796',
        local_files_only=True, trust_remote_code=False)
    costs = {}
    for task in tasks:
        card = cards[task['definition_id']]
        quote = card.get('rule_quote') or (card.get('proposal') or {}).get('full_rule_quote')
        if not isinstance(quote, str) or not quote:
            raise ValueError('Missing source rule quote')
        note = f'Local definition for this contract only:\n{task["term"]}: {quote}\n\n'
        costs[task['id']] = len(tok.encode(note, add_special_tokens=False))
    full_cost = sum(costs.values())
    if full_cost <= 0:
        raise ValueError('No definition cost')
    term_stats = {
        did: {'mean_dp': statistics.mean(x['dp'] for x in rows),
              'mean_R': statistics.mean(x['R'] for x in rows), 'A_count': len(rows)}
        for did, rows in scores.items()
    }
    by_id = {x['id']: x for x in tasks}
    ids = list(by_id)
    orderings = {
        'matched_fixed': sorted(ids, key=lambda x: random_key('matched-fixed:' + x)),
        'dp': sorted(ids, key=lambda x: (-term_stats[by_id[x]['definition_id']]['mean_dp'], x)),
        'R': sorted(ids, key=lambda x: (-term_stats[by_id[x]['definition_id']]['mean_R'], x)),
        'dp_per_token': sorted(ids, key=lambda x: (-term_stats[by_id[x]['definition_id']]['mean_dp'] / costs[x], x)),
    }
    for seed in range(20):
        shuffled = sorted(ids)
        random.Random(20260925 + seed).shuffle(shuffled)
        orderings[f'random_{seed:02d}'] = shuffled
    allocations = []
    for fraction in (0.25, 0.5, 0.75):
        budget = int(full_cost * fraction)
        for policy, order in orderings.items():
            selected, spent = select(order, costs, budget)
            allocations.append({
                'budget_fraction': fraction, 'budget_tokens': budget,
                'policy': policy, 'selected_task_ids': selected,
                'spent_tokens': spent, 'selected_count': len(selected),
            })
    result = {
        'status': 'frozen_development_allocation_plan_no_B_gold_read',
        'inputs': {
            'public_tasks': str(args.public_tasks), 'public_tasks_sha256': sha_file(args.public_tasks),
            'cards': str(args.cards), 'cards_sha256': sha_file(args.cards),
            'scores_a': str(args.scores_a), 'scores_a_sha256': sha_file(args.scores_a),
        },
        'n_tasks': len(tasks), 'full_matched_cost_tokens': full_cost,
        'token_counter': 'Qwen/Qwen2.5-7B d149729398750b98c0af14eb82c78cfe92750796',
        'term_stats': term_stats, 'costs_by_task': costs,
        'allocation_rules': {'atomic_notes': True, 'greedy_skip_nonfitting': True,
                             'tie_break': 'task_id', 'matched_order': 'fixed SHA256 of task ID'},
        'allocations': allocations,
        'caveat': 'Development sample only; fixed-order matching is a feasible all-matched scheduling baseline, not full-cost all-matched.',
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'Frozen {len(allocations)} allocations for {len(tasks)} B tasks; full note cost {full_cost} proxy tokens.')


if __name__ == '__main__':
    main()
