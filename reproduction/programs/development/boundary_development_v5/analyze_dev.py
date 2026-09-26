#!/usr/bin/env python3
"""Summarize paired V5 development outcomes without inferential claims."""

import argparse
import collections
import json
import statistics
from pathlib import Path


def load(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tasks', type=Path, required=True)
    p.add_argument('--predictions', type=Path, required=True)
    p.add_argument('--scores-a', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    tasks = {x['id']: x for x in load(args.tasks)}
    preds = load(args.predictions)
    by = collections.defaultdict(dict)
    for row in preds:
        assert row['task_id'] in tasks
        key = (row['task_id'], row['role'])
        assert row['arm'] not in by[key]
        by[key][row['arm']] = row
    roles = sorted({row['role'] for row in preds})
    paired = {}
    for role in roles:
        items = []
        for task_id, task in tasks.items():
            x = by.get((task_id, role), {})
            if set(x) != {'bare', 'definition'}:
                continue
            if x['bare']['prediction'] not in {'A', 'B'} or x['definition']['prediction'] not in {'A', 'B'}:
                continue
            bare = x['bare']['prediction'] == task['answer']
            defined = x['definition']['prediction'] == task['answer']
            items.append({
                'task_id': task_id, 'definition_id': task['definition_id'],
                'bare_correct': bare, 'defined_correct': defined,
                'transition': ('correct' if bare else 'wrong') + '_to_' + ('correct' if defined else 'wrong'),
            })
        counts = collections.Counter(x['transition'] for x in items)
        per_rule = {}
        for did in sorted({x['definition_id'] for x in items}):
            group = [x for x in items if x['definition_id'] == did]
            per_rule[did] = {
                'n': len(group),
                'bare_correct': sum(x['bare_correct'] for x in group),
                'defined_correct': sum(x['defined_correct'] for x in group),
                'repairs': sum(x['transition'] == 'wrong_to_correct' for x in group),
                'harms': sum(x['transition'] == 'correct_to_wrong' for x in group),
            }
        usage = collections.Counter()
        for row in preds:
            if row['role'] != role:
                continue
            for k in ('prompt_tokens', 'completion_tokens', 'total_tokens'):
                value = (row.get('usage') or {}).get(k)
                if isinstance(value, int):
                    usage[k] += value
        paired[role] = {
            'n_pairs': len(items),
            'bare_accuracy': sum(x['bare_correct'] for x in items) / len(items) if items else None,
            'definition_accuracy': sum(x['defined_correct'] for x in items) / len(items) if items else None,
            'transition_counts': dict(counts),
            'per_rule': per_rule,
            'bare_wrong_task_ids': [x['task_id'] for x in items if not x['bare_correct']],
            'usage_reported': dict(usage),
            'items': items,
        }
    scores = collections.defaultdict(list)
    for row in load(args.scores_a):
        did = row.get('definition_id') or row['id'].split(':a_')[0].split('A:')[1]
        scores[did].append(row)
    a_summary = {
        did: {'n': len(rows), 'mean_R': statistics.mean(x['R'] for x in rows),
              'mean_dp': statistics.mean(x['dp'] for x in rows),
              'min_dp': min(x['dp'] for x in rows), 'max_dp': max(x['dp'] for x in rows)}
        for did, rows in sorted(scores.items())
    }
    result = {
        'status': 'development_only_not_confirmatory',
        'task_count': len(tasks), 'prediction_count': len(preds),
        'planned_prediction_count': len(tasks) * len(roles) * 2,
        'complete': len(preds) == len(tasks) * len(roles) * 2 and all(x['n_pairs'] == len(tasks) for x in paired.values()),
        'A': a_summary, 'B': paired,
        'limitations': ['Only five source rules, author-reviewed summaries and partial task review.',
                        'A and B came from one deterministic generator.',
                        'No token-budget policy comparison or independent-request evidence.'],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    lines = ['# V5 development pilot results', '',
             '**Exploratory only.** Five source rules, controlled hypothetical B facts, and shared A/B generator. '
             'This report is not a confirmatory independent-request result.', '',
             f"- B tasks: {len(tasks)}; paired predictions: {len(preds)} / {result['planned_prediction_count']}; complete: {result['complete']}.", '',
             '| Reader | Pairs | Bare accuracy | With definition | Repairs | Harms |',
             '| --- | ---: | ---: | ---: | ---: | ---: |']
    for role, r in paired.items():
        lines.append(f"| {role} | {r['n_pairs']} | {r['bare_accuracy']:.3f} | {r['definition_accuracy']:.3f} | {r['transition_counts'].get('wrong_to_correct', 0)} | {r['transition_counts'].get('correct_to_wrong', 0)} |" if r['n_pairs'] else f'| {role} | 0 | -- | -- | -- | -- |')
    lines.extend(['', 'Bare wrong cases (all paired with definition outcomes in the JSON report):', ''])
    for role, r in paired.items():
        lines.append(f"- {role}: " + (', '.join('`' + x + '`' for x in r['bare_wrong_task_ids']) or 'none'))
    lines.extend(['', '| Definition | A n | Mean R(A) | Mean Δp(A) |', '| --- | ---: | ---: | ---: |'])
    for did, r in a_summary.items():
        lines.append(f"| {did} | {r['n']} | {r['mean_R']:.3f} | {r['mean_dp']:.3f} |")
    lines.extend(['', 'The A means are not candidate population estimates; all five rules were source-picked for a development feasibility check. '
                  'Formal sampling must include low, middle and high Δp after scoring a broader eligible source frame.',
                  ''])
    args.out.with_suffix('.md').write_text('\n'.join(lines))
    print(f"Analyzed {len(preds)} predictions; complete={result['complete']}; wrote {args.out}")


if __name__ == '__main__':
    main()
