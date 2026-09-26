#!/usr/bin/env python3
"""Audit configured GPT reader sensitivity on historical policy-disagreement B."""
import hashlib
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'gold_aligned_development'


def read(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interval(values):
    ordered = sorted(values)
    return [ordered[round(.025 * (len(ordered) - 1))], ordered[round(.975 * (len(ordered) - 1))]]


def main():
    plan = json.loads((OUT / 'gold_plan_development_only.json').read_text())
    packet = {x['id']: x for x in read(OUT / 'B_disagreement_packet.jsonl')}
    responses = read(OUT / 'gpt56_B_gold_bare.jsonl')
    by_response = {(x['id'], x['condition']): x for x in responses}
    if len(responses) != 2 * len(packet) or len(by_response) != len(responses):
        raise ValueError('Incomplete or duplicate configured GPT reader responses')
    if any(x['returned_model'] != 'gpt-5.6-terra' or not x['provider_response_id'] or x.get('usage') is None
           for x in responses):
        raise ValueError('Model/usage/response provenance incomplete')
    checked = {x['id']: x for x in read(OUT / 'source_decisions.jsonl')}
    if set(checked) != set(packet):
        raise ValueError('Incomplete outcome-blind source checks')
    f = {x['id']: x['post_count'] for x in read(OUT / 'historical_frequency.jsonl')}
    catalog = {x['id']: x for x in read(OUT / 'gold_catalog.jsonl')}
    base = set(plan['policies']['frequency_per_cost']['root_definition_ids'])
    method = set(plan['policies']['frequency_delta_p_per_cost']['root_definition_ids'])
    disagreement = base ^ method
    if disagreement != {x['term_id'] for x in packet.values()}:
        raise ValueError('Reader packet does not cover precisely all strategy-disagreement terms')
    term_gain = defaultdict(list)
    accepted_gain = defaultdict(list)
    repairs = harms = 0
    for qid, item in packet.items():
        bare = by_response[qid, 'bare']['answer'] == item['gold_option']
        gold = by_response[qid, 'gold']['answer'] == item['gold_option']
        gain = int(gold) - int(bare)
        term_gain[item['term_id']].append(gain)
        repairs += not bare and gold
        harms += bare and not gold
        if checked[qid]['accepted_by_outcome_blind_model']:
            accepted_gain[item['term_id']].append(gain)
    if set(term_gain) != disagreement:
        raise ValueError('At least one disagreement term is missing a reader result')
    sign = lambda i: 1 if i in method - base else -1
    term_value = {i: sign(i) * f[i] * statistics.mean(gains) for i, gains in term_gain.items()}
    total_freq = sum(f.values())
    point = sum(term_value.values()) / total_freq
    by_community_num = Counter()
    by_community_den = Counter()
    for i, n in f.items():
        by_community_den[catalog[i]['scope']] += n
        by_community_num[catalog[i]['scope']] += term_value.get(i, 0)
    communities = sorted(by_community_den)
    rng = random.Random(260925)
    draws = []
    for _ in range(5000):
        sampled = rng.choices(communities, k=len(communities))
        draws.append(sum(by_community_num[c] for c in sampled) / sum(by_community_den[c] for c in sampled))
    base_only = base - method
    method_only = method - base
    values = {'baseline_only': sum(f[i] * statistics.mean(term_gain[i]) for i in base_only),
              'method_only': sum(f[i] * statistics.mean(term_gain[i]) for i in method_only)}
    accepted_terms = set(accepted_gain)
    missing = disagreement - accepted_terms
    accepted_known = sum(sign(i) * f[i] * statistics.mean(gains) for i, gains in accepted_gain.items())
    worst_abs = sum(f[i] for i in missing)
    reasons = Counter()
    for row in checked.values():
        if row['accepted_by_outcome_blind_model']:
            continue
        v = row['verdict']
        if v.get('answer') != row['historical_key']:
            reasons['checker_disagreed_with_historical_key'] += 1
        if v.get('definition_sufficient') is not True:
            reasons['definition_insufficient'] += 1
        if v.get('no_answer_leakage') is not True:
            reasons['answer_leakage'] += 1
    output = {'status': 'DEVELOPMENT_ONLY_OLD_SIBLING_B_NOT_FORMAL',
              'n_terms_catalog': len(catalog), 'n_communities': len(communities),
              'n_policy_disagreement_terms': len(disagreement), 'n_B_questions': len(packet),
              'n_configured_reader_calls': len(responses), 'reader_model': 'gpt-5.6-terra',
              'reader_returned_models': dict(Counter(x['returned_model'] for x in responses)),
              'reader_total_tokens': sum(x['usage'].get('total_tokens', 0) for x in responses),
              'overall_repairs': repairs, 'overall_harms': harms,
              'baseline_only_terms': len(base_only), 'method_only_terms': len(method_only),
              'baseline_only_words': sum(len(catalog[i]['definition'].split()) for i in base_only),
              'method_only_words': sum(len(catalog[i]['definition'].split()) for i in method_only),
              'weighted_gain_values': values,
              'policy_difference_weighted_value': sum(term_value.values()),
              'historical_frequency_total': total_freq,
              'policy_difference_per_matched_occurrence': point,
              'fixed_policy_community_cluster_bootstrap_95_interval': interval(draws),
              'source_check': {'n_checked': len(checked),
                               'n_accepted': sum(x['accepted_by_outcome_blind_model'] for x in checked.values()),
                               'n_terms_with_accepted_B': len(accepted_terms),
                               'n_disagreement_terms_without_accepted_B': len(missing),
                               'known_contribution_value': accepted_known,
                               'known_contribution_per_total_frequency': accepted_known / total_freq,
                               'missing_contribution_absolute_bound': worst_abs / total_freq,
                               'partial_identification_interval': [(accepted_known - worst_abs) / total_freq,
                                                                   (accepted_known + worst_abs) / total_freq],
                               'rejection_reason_counts_nonexclusive': dict(reasons)},
              'input_sha256': {name: sha(OUT / name) for name in
                               ('gold_plan_development_only.json', 'B_disagreement_packet.jsonl',
                                'gpt56_B_gold_bare.jsonl', 'source_decisions.jsonl',
                                'historical_frequency.jsonl', 'gold_catalog.jsonl')}}
    (OUT / 'configured_reader_analysis.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print('policy diff pp', round(100 * point, 2), 'CI pp',
          [round(100 * x, 2) for x in output['fixed_policy_community_cluster_bootstrap_95_interval']])
    print('source accepted', output['source_check']['n_accepted'], '/', len(checked),
          'missing term gold', len(missing), 'partial range pp',
          [round(100 * x, 2) for x in output['source_check']['partial_identification_interval']])


if __name__ == '__main__':
    main()
