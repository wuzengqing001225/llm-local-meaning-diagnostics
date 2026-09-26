#!/usr/bin/env python3
"""Check generated development items for structural leakage and split errors."""

import argparse
import collections
import json
from pathlib import Path


def load(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('pilot', type=Path)
    args = p.parse_args()
    a = load(args.pilot / 'diagnostics_A.jsonl')
    b = load(args.pilot / 'tasks_B.jsonl')
    blind = load(args.pilot / 'tasks_B_blind.jsonl')
    assert len(a) == 20 and len(b) == len(blind) == 30
    assert len({x['id'] for x in a + b}) == 50
    assert not ({x['fact_text'] for x in a} & {x['fact_text'] for x in b})
    assert not ({x['fact_id'] for x in a} & {x['fact_id'] for x in b})
    for group, expected in ((a, 4), (b, 6)):
        by_rule = collections.defaultdict(list)
        for x in group:
            assert x['answer'] in 'AB' and len(x['options']) == 2
            assert x['status'] == 'unreviewed_development_item'
            option = x['options']['AB'.index(x['answer'])]
            assert option.startswith('Yes') == x['oracle_membership']
            assert 'means ' not in x['question'].lower()
            by_rule[x['definition_id']].append(x)
        assert len(by_rule) == 5
        for rule, xs in by_rule.items():
            assert len(xs) == expected, (rule, len(xs))
            assert sum(x['oracle_membership'] for x in xs) == expected // 2
            assert collections.Counter(x['answer'] for x in xs) == {'A': expected // 2, 'B': expected // 2}
    for keyed, hidden in zip(b, blind):
        assert keyed['id'] == hidden['id']
        assert not ({'answer', 'oracle_membership', 'oracle_trace'} & hidden.keys())
    print('Development QA passed: 5 rules, 20 A, 30 B; split, labels, balance and blind copy checked.')


if __name__ == '__main__':
    main()
