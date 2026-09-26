#!/usr/bin/env python3
"""Exploratory clustered bootstrap of the signed policy difference, no API."""
import json
import math
import random
from collections import defaultdict
from pathlib import Path

from audit_offline_simulation import CASES, ROOT, build


def policy_value(rows, combined):
    budget = math.floor(.25 * sum(x['cost'] for x in rows))
    ranked = sorted(rows, key=lambda x: (-(x['frequency'] * x['delta_p_A'] / x['cost']
                                          if combined else x['frequency'] / x['cost']), x['id']))
    spent = 0
    value = 0.0
    for item in ranked:
        if spent + item['cost'] <= budget:
            spent += item['cost']
            value += item['realized_value']
    return value


def pct(values, quantile):
    return sorted(values)[round(quantile * (len(values) - 1))]


def main():
    rng = random.Random(260925)
    output = []
    for case in CASES:
        items, _ = build(case, split=0, cost_source='actual_injected_gloss', exclude_interest=False)
        groups = defaultdict(list)
        for item in items:
            cluster = item['id'].split(':')[1] if case[1] == 'reddit' else item['id']
            groups[cluster].append(item)
        keys = sorted(groups)
        estimate = (policy_value(items, True) - policy_value(items, False)) / sum(x['frequency'] for x in items)
        draws = []
        for _ in range(1500):
            sample = [x for key in rng.choices(keys, k=len(keys)) for x in groups[key]]
            draws.append((policy_value(sample, True) - policy_value(sample, False)) /
                         sum(x['frequency'] for x in sample))
        output.append({'setting': case[0], 'n_terms': len(items), 'n_clusters': len(keys),
                       'point_fraction_of_matched_term_occurrences': estimate,
                       'percentile_95_interval': [pct(draws, .025), pct(draws, .975)],
                       'n_replicates': len(draws)})
    (ROOT / 'development_bootstrap.json').write_text(json.dumps({
        'status': 'exploratory_only_same_source_A_and_B_questions',
        'cluster_rule': 'Reddit subreddit; synthetic term',
        'cost_source': 'actual_injected_gloss', 'budget_fraction': .25,
        'estimand': 'frequency-weighted observed correct-answer gain difference divided by source frequency total',
        'results': output}, indent=2) + '\n')
    for row in output:
        print(row['setting'], row['n_clusters'],
              round(100 * row['point_fraction_of_matched_term_occurrences'], 2),
              [round(100 * x, 2) for x in row['percentile_95_interval']])


if __name__ == '__main__':
    main()
