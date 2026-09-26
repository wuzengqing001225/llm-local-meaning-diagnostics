#!/usr/bin/env python3
"""Compare historical F×Δp and F using the same gold gloss in A, cost and B.

This is developmental. B questions remain siblings of A, and F is not a
separate frozen text stream. No new model/API call is made by this analysis.
"""
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'release_20260923/llm-idf-reproduce/data/reddit/raw_outputs'
GOLD_A = ROOT / 'gold_aligned_development/qwen_A_gold.jsonl'


def load(path):
    return {x['id']: x for x in (json.loads(line) for line in path.open())}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    scores = load(GOLD_A)
    old = load(DATA / 'lpmc_reddit_v2.jsonl')
    reader = load(DATA / 'reddit_v2_eqa.jsonl')
    weights = load(DATA / 'reddit_v2_weights.jsonl')
    rows = []
    for i in sorted(scores):
        w = weights[i]
        if not w['labels'].get('is_target'):
            raise ValueError('Non-target term in score file')
        definition_hash = hashlib.sha256(w['gloss_gold'].encode()).hexdigest()
        if scores[i]['definition_sha256'] != definition_hash:
            raise ValueError('A scored a different definition: ' + i)
        questions = reader[i]['questions']
        B = [j for j in range(1, len(questions), 2)]
        if not B or not all('glossG' in questions[j]['correct'] for j in B):
            raise ValueError('Missing gold-definition B reader arm: ' + i)
        gain_gold = statistics.mean(questions[j]['correct']['glossG'] - questions[j]['correct']['bare'] for j in B)
        gain_auto = statistics.mean(questions[j]['correct']['glossC'] - questions[j]['correct']['bare'] for j in B)
        A = list(range(0, len(old[i]['per_question']), 2))
        delta_auto = statistics.mean(old[i]['per_question'][j]['glossC']['p_correct'] -
                                     old[i]['per_question'][j]['bare']['p_correct'] for j in A)
        rows.append({'id': i, 'scope': w['labels']['subreddit'], 'frequency': w['labels']['tf'],
                     'cost_words': len(w['gloss_gold'].split()),
                     'delta_p_gold_A': scores[i]['mean_delta_p'], 'delta_p_auto_A': delta_auto,
                     'risk_gold_A': statistics.mean(1 - x['p_bare'] for x in scores[i]['per_question']),
                     'gain_gold_B': gain_gold, 'gain_auto_B': gain_auto,
                     'n_A': scores[i]['n_A'], 'n_B': len(B)})
    return rows


def select(rows, fraction, score_key, gain_key):
    budget = math.floor(fraction * sum(x['cost_words'] for x in rows))
    if score_key == 'frequency':
        key = lambda x: x['frequency'] / x['cost_words']
    else:
        key = lambda x: x['frequency'] * x[score_key] / x['cost_words']
    selected = []
    spent = 0
    for row in sorted(rows, key=lambda x: (-key(x), x['id'])):
        if key(row) <= 0:
            continue
        if spent + row['cost_words'] <= budget:
            selected.append(row)
            spent += row['cost_words']
    value = sum(x['frequency'] * x[gain_key] for x in selected)
    return {'budget_words': budget, 'spent_words': spent, 'n_selected': len(selected),
            'frequency_weighted_gain': value, 'selected_ids': [x['id'] for x in selected]}


def exact_oracle(rows, fraction, gain_key):
    budget = math.floor(fraction * sum(x['cost_words'] for x in rows))
    dp = [float('-inf')] * (budget + 1)
    dp[0] = 0
    for row in rows:
        cost = row['cost_words']
        value = row['frequency'] * row[gain_key]
        if value <= 0:
            continue
        for k in range(budget, cost - 1, -1):
            dp[k] = max(dp[k], dp[k - cost] + value)
    return max(dp)


def bootstrap(rows, gain_key, score_key, n=1500):
    by_scope = defaultdict(list)
    for row in rows:
        by_scope[row['scope']].append(row)
    scopes = sorted(by_scope)
    rng = random.Random(260925)
    draws = []
    for _ in range(n):
        sample = []
        for draw, scope in enumerate(rng.choices(scopes, k=len(scopes))):
            for row in by_scope[scope]:
                sample.append({**row, 'id': f'{draw}:{row["id"]}'})
        baseline = select(sample, .25, 'frequency', gain_key)['frequency_weighted_gain']
        method = select(sample, .25, score_key, gain_key)['frequency_weighted_gain']
        draws.append((method - baseline) / sum(x['frequency'] for x in sample))
    draws.sort()
    return [draws[round(.025 * (n - 1))], draws[round(.975 * (n - 1))]]


def main():
    rows = build()
    settings = []
    for gain, score, label in [
        ('gain_auto_B', 'delta_p_auto_A', 'original_mixed_definition'),
        ('gain_gold_B', 'delta_p_auto_A', 'auto_score_gold_intervention_mismatch'),
        ('gain_gold_B', 'delta_p_gold_A', 'fully_gold_aligned'),
        ('gain_gold_B', 'risk_gold_A', 'risk_R_secondary_gold_intervention')]:
        for fraction in (.10, .25, .50):
            baseline = select(rows, fraction, 'frequency', gain)
            method = select(rows, fraction, score, gain)
            oracle = exact_oracle(rows, fraction, gain)
            total_freq = sum(x['frequency'] for x in rows)
            result = {'setting': label, 'budget_fraction': fraction,
                      'baseline': baseline, 'method': method, 'exact_oracle_value': oracle,
                      'baseline_oracle_fraction': baseline['frequency_weighted_gain'] / oracle,
                      'method_oracle_fraction': method['frequency_weighted_gain'] / oracle,
                      'method_minus_baseline_value': method['frequency_weighted_gain'] - baseline['frequency_weighted_gain'],
                      'method_minus_baseline_per_matched_occurrence':
                          (method['frequency_weighted_gain'] - baseline['frequency_weighted_gain']) / total_freq}
            if fraction == .25:
                result['community_cluster_bootstrap_95_interval'] = bootstrap(rows, gain, score)
            settings.append(result)
    output = {'status': 'DEVELOPMENT_ONLY_NO_INDEPENDENT_B', 'n_terms': len(rows),
              'n_communities': len({x['scope'] for x in rows}),
              'A_questions': sum(x['n_A'] for x in rows), 'B_questions': sum(x['n_B'] for x in rows),
              'source_hashes': {str(path): sha(path) for path in
                                (GOLD_A, DATA / 'lpmc_reddit_v2.jsonl', DATA / 'reddit_v2_eqa.jsonl',
                                 DATA / 'reddit_v2_weights.jsonl')},
              'settings': settings}
    out = ROOT / 'gold_aligned_development/analysis.json'
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    for item in settings:
        if item['budget_fraction'] == .25:
            print(item['setting'],
                  round(item['baseline_oracle_fraction'], 3),
                  round(item['method_oracle_fraction'], 3),
                  'diff_pp', round(100 * item['method_minus_baseline_per_matched_occurrence'], 2),
                  'CI_pp', [round(100 * x, 2) for x in item['community_cluster_bootstrap_95_interval']])


if __name__ == '__main__':
    main()
