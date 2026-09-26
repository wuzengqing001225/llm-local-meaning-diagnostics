#!/usr/bin/env python3
"""Freeze a gold-definition historical plan without inspecting B reader outcomes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'gold_aligned_development'
WEIGHTS = ROOT.parent / 'release_20260923/llm-idf-reproduce/data/reddit/raw_outputs/reddit_v2_weights.jsonl'


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows))


def main():
    scores = {x['id']: x for x in (json.loads(line) for line in (OUT / 'qwen_A_gold.jsonl').open())}
    weights = {x['id']: x for x in (json.loads(line) for line in WEIGHTS.open())}
    if len(scores) != 215:
        raise ValueError('Expected all 215 historical target terms scored')
    catalog, a_rows, f_rows = [], [], []
    for i in sorted(scores):
        w, s = weights[i], scores[i]
        definition = w['gloss_gold']
        digest = hashlib.sha256(definition.encode()).hexdigest()
        if digest != s['definition_sha256']:
            raise ValueError('A definition mismatch: ' + i)
        catalog.append({'id': i, 'scope': w['labels']['subreddit'], 'term': w['term'],
                        'definition': definition, 'definition_sha256': digest,
                        'source_ref': 'Lucy-Bamman community glossary as stored in reddit_v2_weights.jsonl',
                        'validation_status': 'provisional', 'unit_type': 'local_definition',
                        'selectable': True, 'dependencies': []})
        a_rows.append({'id': i, 'definition_sha256': digest, 'mean_delta_p': s['mean_delta_p'],
                       'n_A': s['n_A'], 'question_ids': [x['question_id'] for x in s['per_question']],
                       'proxy_model': s['proxy_model'], 'proxy_revision': s['proxy_revision']})
        f_rows.append({'id': i, 'post_count': w['labels']['tf']})
    write_rows(OUT / 'gold_catalog.jsonl', catalog)
    write_rows(OUT / 'gold_a_scores.jsonl', a_rows)
    write_rows(OUT / 'historical_frequency.jsonl', f_rows)
    config = {'catalog': 'gold_catalog.jsonl', 'a_scores': 'gold_a_scores.jsonl',
              'frequency': 'historical_frequency.jsonl', 'budget_fraction': .25,
              'frequency_frame': {'type': 'overlapping_historical_development',
                                  'sha256': hashlib.sha256(WEIGHTS.read_bytes()).hexdigest(),
                                  'overlap_check_passed': False},
              'b_start_utc': None, 'development_only': True,
              'out': 'gold_plan_development_only.json'}
    (OUT / 'gold_study_config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n')
    print('Prepared gold-definition development plan inputs for', len(catalog), 'terms')


if __name__ == '__main__':
    main()
