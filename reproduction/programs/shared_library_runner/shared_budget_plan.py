#!/usr/bin/env python3
"""Freeze two shared definition-library selections before reading future B.

Usage: python shared_budget_plan.py --config study_config.json
This program never reads test questions, answers, or model API keys.
"""
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def definition_hash(row):
    return hashlib.sha256(row['definition'].encode('utf-8')).hexdigest()


def timestamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def check_inputs(config, base):
    paths = {key: (base / config[key]).resolve() for key in ('catalog', 'a_scores', 'frequency')}
    catalog_rows = read_rows(paths['catalog'])
    if not catalog_rows:
        raise ValueError('Empty definition catalog')
    catalog = {x['id']: x for x in catalog_rows}
    if len(catalog) != len(catalog_rows):
        raise ValueError('Duplicate catalog ID')
    development = config.get('development_only') is True
    for row in catalog_rows:
        for key in ('id', 'scope', 'term', 'definition', 'source_ref'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f'Missing catalog {key}')
        if row.get('unit_type') != 'local_definition':
            raise ValueError('All units must be local definitions')
        if not development and row.get('validation_status') != 'source_checked':
            raise ValueError('Formal catalog contains a definition without source_check')
        if row.get('definition_sha256') and row['definition_sha256'] != definition_hash(row):
            raise ValueError('Catalog definition hash mismatch: ' + row['id'])
    selectable = {i for i, row in catalog.items() if row.get('selectable', True)}
    if not selectable:
        raise ValueError('No selectable definitions')
    a_rows, f_rows = read_rows(paths['a_scores']), read_rows(paths['frequency'])
    if {x['id'] for x in a_rows} != selectable or len(a_rows) != len(selectable):
        raise ValueError('A IDs must cover each selectable definition exactly once')
    if {x['id'] for x in f_rows} != selectable or len(f_rows) != len(selectable):
        raise ValueError('Frequency IDs must cover each selectable definition exactly once')
    a = {x['id']: x for x in a_rows}
    frequency = {x['id']: x for x in f_rows}
    question_ids = []
    for i in selectable:
        row = a[i]
        if row.get('definition_sha256') != definition_hash(catalog[i]):
            raise ValueError('A uses a different definition version: ' + i)
        if not math.isfinite(float(row['mean_delta_p'])):
            raise ValueError('Non-finite A score')
        if not development and int(row.get('n_A', 0)) < 4:
            raise ValueError('Fewer than four verified A questions: ' + i)
        if not development and not row.get('proxy_model'):
            raise ValueError('Missing proxy model identity: ' + i)
        question_ids.extend(row.get('question_ids') or [])
        count = frequency[i].get('post_count')
        if not isinstance(count, int) or count < 0:
            raise ValueError('Frequency must be a nonnegative integer post count: ' + i)
    if len(question_ids) != len(set(question_ids)):
        raise ValueError('An A question ID appears under multiple definitions')
    frame = config.get('frequency_frame') or {}
    if not development:
        if frame.get('type') != 'complete_community_stream':
            raise ValueError('Formal frequency requires a complete stream or a separately audited weighted sampler')
        if not frame.get('sha256') or not frame.get('communities_sha256') or not frame.get('matches_sha256'):
            raise ValueError('Missing frequency frame provenance')
        if not config.get('frequency_matches'):
            raise ValueError('Formal plan must verify original source-only frequency matches')
        paths['frequency_matches'] = (base / config['frequency_matches']).resolve()
        if file_hash(paths['frequency_matches']) != frame['matches_sha256']:
            raise ValueError('Frequency match frame hash differs from manifest')
        frame_counts = {i: 0 for i in selectable}
        seen_posts = set()
        with paths['frequency_matches'].open() as stream:
            for line in stream:
                if not line.strip():
                    continue
                matched = json.loads(line)
                post_id = matched['post_id']
                if post_id in seen_posts:
                    raise ValueError('Duplicate post in frequency match frame')
                seen_posts.add(post_id)
                if not timestamp(frame['start_utc']) <= timestamp(matched['created_utc']) < timestamp(frame['end_utc']):
                    raise ValueError('Frequency match outside frozen frame')
                ids = matched['matched_definition_ids']
                if len(ids) != len(set(ids)):
                    raise ValueError('Duplicate matched term in frequency post')
                for i in ids:
                    if i in frame_counts:
                        if matched['scope'] != catalog[i]['scope']:
                            raise ValueError('Cross-scope frequency match')
                        frame_counts[i] += 1
        if any(frame_counts[i] != frequency[i]['post_count'] for i in selectable):
            raise ValueError('Frequency counts differ from frozen post-match frame')
        if frame.get('overlap_check_passed') is not True:
            raise ValueError('A/F disjointness not confirmed')
        if timestamp(frame['end_utc']) > timestamp(config['b_start_utc']):
            raise ValueError('Frequency frame must end no later than B starts')
    fraction = float(config.get('budget_fraction', .25))
    if not 0 < fraction < 1:
        raise ValueError('Budget fraction must be between zero and one')
    return paths, catalog, selectable, a, frequency, fraction, development


def closure(root, catalog):
    seen = set()
    stack = [root]
    while stack:
        i = stack.pop()
        if i in seen:
            continue
        if i not in catalog:
            raise ValueError('Missing definition dependency: ' + i)
        if catalog[i]['scope'] != catalog[root]['scope']:
            raise ValueError('Cross-scope dependency requires separate adjudication: ' + i)
        seen.add(i)
        stack.extend(catalog[i].get('dependencies') or [])
    return seen


def select(catalog, roots, a, frequency, budget, combined):
    words = {i: len(x['definition'].split()) for i, x in catalog.items()}
    deps = {i: closure(i, catalog) for i in roots}
    scored = []
    for i in roots:
        f = frequency[i]['post_count']
        delta = float(a[i]['mean_delta_p'])
        standalone_cost = sum(words[j] for j in deps[i])
        score = (f * delta if combined else f) / standalone_cost
        if score > 0:
            scored.append((i, score))
    scored.sort(key=lambda x: (-x[1], x[0]))
    selected = []
    installed = set()
    for i, score in scored:
        candidate = installed | deps[i]
        if sum(words[j] for j in candidate) <= budget:
            selected.append(i)
            installed = candidate
    return {'root_definition_ids': selected, 'installed_definition_ids': sorted(installed),
            'spent_words': sum(words[j] for j in installed),
            'n_root_definitions': len(selected), 'n_installed_definitions': len(installed)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text())
    paths, catalog, roots, a, frequency, fraction, development = check_inputs(config, config_path.parent)
    total_words = sum(len(x['definition'].split()) for x in catalog.values())
    budget = math.floor(fraction * total_words)
    if budget <= 0:
        raise ValueError('Budget cannot fit any words')
    result = {'status': 'DEVELOPMENT_ONLY' if development else 'FROZEN_BEFORE_B',
              'question': 'which local definitions to build for a future batch of requests',
              'cost_unit': 'whitespace_separated_definition_words',
              'scope': 'global_budget_across_frozen_community_catalog',
              'budget_fraction': fraction, 'total_catalog_words': total_words,
              'budget_words': budget, 'n_catalog_definitions': len(catalog),
              'n_selectable_definitions': len(roots),
              'frequency_frame': config.get('frequency_frame'),
              'b_start_utc': config.get('b_start_utc'),
              'input_sha256': {key: file_hash(path) for key, path in paths.items()},
              'config_sha256': file_hash(config_path),
              'policies': {'frequency_per_cost': select(catalog, roots, a, frequency, budget, False),
                           'frequency_delta_p_per_cost': select(catalog, roots, a, frequency, budget, True)},
              'selection_rule': 'positive-score greedy descending, stable ID ties, full dependency closure, skip non-fitting term'}
    output = (config_path.parent / config['out']).resolve()
    if output.exists():
        if json.loads(output.read_text()) != result:
            raise RuntimeError('Existing frozen plan differs; use a new output path/version')
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'budget_words': budget,
                      'frequency_selected': result['policies']['frequency_per_cost']['n_root_definitions'],
                      'delta_selected': result['policies']['frequency_delta_p_per_cost']['n_root_definitions'],
                      'plan': str(output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
