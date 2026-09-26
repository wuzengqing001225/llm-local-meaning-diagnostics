#!/usr/bin/env python3
"""Score paired future-use outcomes against a frozen shared definition plan."""
import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from shared_budget_plan import closure, file_hash, read_rows


BASE = 'frequency_per_cost'
METHOD = 'frequency_delta_p_per_cost'
JUDGMENTS = {'correct', 'wrong', 'abstain'}


def timestamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def expected_injection(matched, roots, catalog):
    installed = set()
    for term_id in set(matched) & set(roots):
        installed |= closure(term_id, catalog)
    return installed


def weighted_rate(pairs, policy, field):
    den = sum(x['weight'] for x in pairs)
    return sum(x['weight'] * (x[policy]['judgment'] == field) for x in pairs) / den


def paired_stats(pairs):
    return {'n_requests': len(pairs), 'weighted_n': sum(x['weight'] for x in pairs),
            'accuracy_frequency': weighted_rate(pairs, BASE, 'correct'),
            'accuracy_frequency_delta_p': weighted_rate(pairs, METHOD, 'correct'),
            'correct_rate_difference': weighted_rate(pairs, METHOD, 'correct') - weighted_rate(pairs, BASE, 'correct'),
            'wrong_frequency': weighted_rate(pairs, BASE, 'wrong'),
            'wrong_frequency_delta_p': weighted_rate(pairs, METHOD, 'wrong'),
            'abstain_frequency': weighted_rate(pairs, BASE, 'abstain'),
            'abstain_frequency_delta_p': weighted_rate(pairs, METHOD, 'abstain')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--trials', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--development', action='store_true')
    args = parser.parse_args()
    plan_path, catalog_path, trials_path = [x.resolve() for x in (args.plan, args.catalog, args.trials)]
    plan = json.loads(plan_path.read_text())
    if not args.development and plan['status'] != 'FROZEN_BEFORE_B':
        raise ValueError('Formal evaluation requires a formal plan frozen before B')
    if file_hash(catalog_path) != plan['input_sha256']['catalog']:
        raise ValueError('Definition catalog changed after planning')
    catalog_rows = read_rows(catalog_path)
    catalog = {x['id']: x for x in catalog_rows}
    if len(catalog_rows) != len(catalog):
        raise ValueError('Duplicate definition ID')
    trials = read_rows(trials_path)
    by_request = defaultdict(dict)
    for row in trials:
        request_id = row['request_id']
        policy = row['policy']
        if policy not in {BASE, METHOD}:
            raise ValueError('Unexpected policy arm')
        if policy in by_request[request_id]:
            raise ValueError('Duplicate request/policy arm')
        if row.get('judgment') not in JUDGMENTS:
            raise ValueError('Every trial needs correct/wrong/abstain source-adjudicated judgment')
        if not args.development and row.get('gold_source_checked') is not True:
            raise ValueError('Unreviewed B answer')
        if not args.development:
            for key in ('question_sha256', 'prompt_sha256', 'settings_sha256',
                        'provider_response_id', 'returned_model'):
                if not isinstance(row.get(key), str) or not row[key].strip():
                    raise ValueError(f'Missing formal response provenance: {key}')
        if not args.development and timestamp(row['created_utc']) < timestamp(plan['b_start_utc']):
            raise ValueError('B use predates frozen B start')
        roots = plan['policies'][policy]['root_definition_ids']
        matched = row['matched_definition_ids']
        if len(set(matched)) != len(matched) or any(i not in catalog for i in matched):
            raise ValueError('Invalid matched definition IDs')
        expected = expected_injection(matched, roots, catalog)
        if set(row['injected_definition_ids']) != expected:
            raise ValueError(f'Actual injected definitions differ from frozen policy: {request_id} {policy}')
        if float(row['sampling_weight']) <= 0:
            raise ValueError('Sampling weight must be positive')
        by_request[request_id][policy] = row
    pairs = []
    models = set()
    usage_missing = 0
    total_tokens = Counter()
    actual_api_tokens = Counter()
    for request_id, arms in by_request.items():
        if set(arms) != {BASE, METHOD}:
            raise ValueError('Unpaired request: ' + request_id)
        left, right = arms[BASE], arms[METHOD]
        shared_fields = ['cluster', 'scope', 'created_utc', 'matched_definition_ids', 'sampling_weight']
        if not args.development:
            shared_fields.extend(['question_sha256', 'settings_sha256'])
        for field in shared_fields:
            if left[field] != right[field]:
                raise ValueError(f'Pair metadata mismatch for {request_id}: {field}')
        if left['reader_model'] != right['reader_model']:
            raise ValueError('Main paired arms must use the same reader model')
        models.add(left['reader_model'])
        if not args.development and left['reader_model'] != 'gpt-5.6-terra':
            raise ValueError('Primary reader model changed')
        for arm in (left, right):
            usage = arm.get('usage') or {}
            if usage.get('prompt_tokens') is None or usage.get('completion_tokens') is None:
                usage_missing += 1
            else:
                total_tokens[arm['policy'] + ':prompt'] += usage['prompt_tokens']
                total_tokens[arm['policy'] + ':completion'] += usage['completion_tokens']
                if arm.get('api_call_made', True):
                    actual_api_tokens['prompt'] += usage['prompt_tokens']
                    actual_api_tokens['completion'] += usage['completion_tokens']
        pairs.append({'request_id': request_id, 'cluster': left['cluster'],
                      'weight': float(left['sampling_weight']), BASE: left, METHOD: right})
    if not pairs:
        raise ValueError('No paired B trials')
    stats = paired_stats(pairs)
    by_cluster = defaultdict(list)
    for pair in pairs:
        by_cluster[pair['cluster']].append(pair)
    cluster_ids = sorted(by_cluster)
    rng = random.Random(260925)
    bootstrap = []
    for _ in range(2000):
        sample = [p for cluster in rng.choices(cluster_ids, k=len(cluster_ids)) for p in by_cluster[cluster]]
        bootstrap.append(paired_stats(sample)['correct_rate_difference'])
    bootstrap.sort()
    ci = [bootstrap[round(.025 * (len(bootstrap) - 1))], bootstrap[round(.975 * (len(bootstrap) - 1))]]
    transitions = Counter((p[BASE]['judgment'], p[METHOD]['judgment']) for p in pairs)
    result = {'status': 'DEVELOPMENT_ONLY' if args.development else 'FORMAL_EVALUATION',
              'n_community_clusters': len(cluster_ids), 'reader_models': sorted(models),
              'primary': stats, 'cluster_bootstrap_95_interval': ci,
              'primary_superiority_supported': not args.development and len(cluster_ids) >= 20 and ci[0] > 0,
              'practical_one_percent_point_estimate_met': stats['correct_rate_difference'] >= .01,
              'transition_counts': {f'{a}->{b}': n for (a, b), n in sorted(transitions.items())},
              'usage_missing_arms': usage_missing,
              'logical_deployment_tokens_by_policy': dict(total_tokens),
              'actual_deduplicated_experiment_tokens': dict(actual_api_tokens),
              'input_sha256': {'plan': file_hash(plan_path), 'catalog': file_hash(catalog_path),
                               'trials': file_hash(trials_path)},
              'caveat': 'Cluster bootstrap captures within-community dependence conditional on this frozen candidate frame; source review, sample inclusion probabilities, and policy prompts require independent audit.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'n': len(pairs), 'clusters': len(cluster_ids),
                      'correct_rate_difference': stats['correct_rate_difference'], 'CI': ci}, ensure_ascii=False))


if __name__ == '__main__':
    main()
