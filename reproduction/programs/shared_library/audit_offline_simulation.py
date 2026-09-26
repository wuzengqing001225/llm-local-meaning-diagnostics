#!/usr/bin/env python3
"""Reproduce the four inspectable cells of the supplied shared-budget simulation.

No API calls. Terms are ranked using odd/even A proxy probabilities, and
evaluated against the other half's observed reader correct-answer changes.
The original simulation script was not supplied, so this file records every
choice needed to reconstruct the numbers and a definition-cost sensitivity.
"""
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'release_20260923/llm-idf-reproduce/data'
CASES = [
    ('synthetic_DeepSeek', 'synthetic_v1', 'lpmc_v1.jsonl', 'v1_weights.jsonl', 'eqa_v1_deepseek_robust.jsonl'),
    ('synthetic_GPT6', 'synthetic_v1', 'lpmc_v1.jsonl', 'v1_weights.jsonl', 'astra6_v1_eqa.jsonl'),
    ('reddit_DeepSeek', 'reddit', 'lpmc_reddit_v2.jsonl', 'reddit_v2_weights.jsonl', 'reddit_v2_eqa.jsonl'),
    ('reddit_GPT6', 'reddit', 'lpmc_reddit_v2.jsonl', 'reddit_v2_weights.jsonl', 'astra6_reddit_eqa.jsonl'),
]
EXCLUDED_SYNTHETIC = {('v1:desk:interest', 1)}


def load(path):
    return {x['id']: x for x in (json.loads(line) for line in path.open())}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(case, split, cost_source, exclude_interest):
    name, corpus, proxy_file, weights_file, reader_file = case
    folder = DATA / corpus / 'raw_outputs'
    paths = [folder / x for x in (proxy_file, weights_file, reader_file)]
    proxy, weights, reader = map(load, paths)
    out = []
    for term_id in sorted(proxy.keys() & weights.keys() & reader.keys()):
        w = weights[term_id]
        if corpus == 'reddit' and not w['labels'].get('is_target'):
            continue
        probs = proxy[term_id]['per_question']
        items = reader[term_id]['questions']
        if len(probs) < 2:
            continue
        if len(probs) != len(items) or not all(q['q'].startswith(p['q']) for p, q in zip(probs, items)):
            raise ValueError(f'Question order mismatch: {name} {term_id}')
        valid = [i for i in range(len(items)) if not (exclude_interest and corpus == 'synthetic_v1'
                                                      and (term_id, i) in EXCLUDED_SYNTHETIC)]
        a_idx = [i for i in valid if i % 2 == split]
        b_idx = [i for i in valid if i % 2 != split]
        if not a_idx or not b_idx:
            continue
        definition = w['gloss_gold'] if cost_source == 'gold_gloss' else w['gloss_used']
        if not definition:
            continue
        cost = len(definition.split())
        delta_p = statistics.mean(probs[i]['glossC']['p_correct'] - probs[i]['bare']['p_correct'] for i in a_idx)
        gain = statistics.mean(items[i]['correct']['glossC'] - items[i]['correct']['bare'] for i in b_idx)
        freq = w['labels']['tf']
        out.append({'id': term_id, 'cost': cost, 'frequency': freq, 'delta_p_A': delta_p,
                    'reader_gain_B': gain, 'realized_value': freq * gain,
                    'n_A': len(a_idx), 'n_B': len(b_idx)})
    return out, {str(p): sha(p) for p in paths}


def select(rows, budget, score):
    ordered = sorted(rows, key=lambda x: (-score(x), x['id']))
    used = 0
    selected = []
    for row in ordered:
        if used + row['cost'] <= budget:
            selected.append(row['id'])
            used += row['cost']
    by_id = {x['id']: x for x in rows}
    value = sum(by_id[i]['realized_value'] for i in selected)
    return {'value': value, 'spent': used, 'n_selected': len(selected), 'selected_ids': selected}


def exact_oracle(rows, budget):
    # Signed negative realized values can always be skipped.
    dp = [float('-inf')] * (budget + 1)
    dp[0] = 0.0
    for row in rows:
        cost, value = row['cost'], row['realized_value']
        if value <= 0:
            continue
        for j in range(budget, cost - 1, -1):
            dp[j] = max(dp[j], dp[j - cost] + value)
    return max(dp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'simulation_audit.json')
    args = parser.parse_args()
    cells = []
    source_hashes = {}
    for case in CASES:
        for cost_source in ('gold_gloss', 'actual_injected_gloss'):
            for split in (0, 1):
                for exclude_interest in (False, True):
                    # The correction only changes synthetic rows; avoid duplicate Reddit cells.
                    if exclude_interest and case[1] != 'synthetic_v1':
                        continue
                    rows, hashes = build(case, split, cost_source, exclude_interest)
                    source_hashes.update(hashes)
                    for fraction in (.10, .25, .50):
                        budget = math.floor(fraction * sum(x['cost'] for x in rows))
                        frequency = select(rows, budget, lambda x: x['frequency'] / x['cost'])
                        combined = select(rows, budget,
                                          lambda x: x['frequency'] * x['delta_p_A'] / x['cost'])
                        greedy_oracle = select(rows, budget, lambda x: x['realized_value'] / x['cost'])
                        oracle = exact_oracle(rows, budget)
                        cells.append({'setting': case[0], 'n_terms': len(rows), 'A_parity': split,
                                      'budget_fraction': fraction, 'budget_words': budget,
                                      'cost_source': cost_source, 'excluded_interest_inconsistent_question': exclude_interest,
                                      'frequency': frequency, 'frequency_delta_p': combined,
                                      'greedy_oracle_value': greedy_oracle['value'],
                                      'exact_oracle_value': oracle,
                                      'frequency_over_exact_oracle': frequency['value'] / oracle if oracle > 0 else None,
                                      'frequency_delta_p_over_exact_oracle': combined['value'] / oracle if oracle > 0 else None,
                                      'combined_minus_frequency_value': combined['value'] - frequency['value']})
    result = {'status': 'development_reproduction_no_API', 'source_hashes': source_hashes,
              'assumptions': ['Reddit target glossary terms only; >=2 aligned questions per term',
                              'A uses per-question p_correct(glossC)-p_correct(bare)',
                              'B uses per-question reader correct(glossC)-correct(bare)',
                              'frequency is labels.tf; cost is split-on-whitespace word count',
                              'greedy strategies fill capacity even if the final score is negative',
                              'exact oracle is 0-1 knapsack on positive realized values'],
              'cells': cells}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for name in [x[0] for x in CASES]:
        for source in ('gold_gloss', 'actual_injected_gloss'):
            row = next(x for x in cells if x['setting'] == name and x['cost_source'] == source
                       and x['A_parity'] == 0 and x['budget_fraction'] == .25
                       and not x['excluded_interest_inconsistent_question'])
            print(name, source, row['n_terms'],
                  round(row['frequency_over_exact_oracle'], 3),
                  round(row['frequency_delta_p_over_exact_oracle'], 3),
                  round(row['combined_minus_frequency_value'], 3))


if __name__ == '__main__':
    main()
