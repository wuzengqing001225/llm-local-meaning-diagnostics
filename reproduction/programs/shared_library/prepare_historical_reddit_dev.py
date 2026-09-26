#!/usr/bin/env python3
"""Make a clearly non-confirmatory planner fixture from historical Reddit records."""
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'release_20260923/llm-idf-reproduce/data/reddit/raw_outputs'
OUT = ROOT / 'historical_reddit_development_only'


def load(filename):
    return {x['id']: x for x in (json.loads(line) for line in (DATA / filename).open())}


def jsonl(path, rows):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows))


def main():
    OUT.mkdir(exist_ok=True)
    proxy = load('lpmc_reddit_v2.jsonl')
    reader = load('reddit_v2_eqa.jsonl')
    weights = load('reddit_v2_weights.jsonl')
    catalog, a_scores, frequencies = [], [], []
    for term_id in sorted(proxy.keys() & reader.keys() & weights.keys()):
        w = weights[term_id]
        if not w['labels'].get('is_target') or len(proxy[term_id]['per_question']) < 2:
            continue
        pp = proxy[term_id]['per_question']
        rr = reader[term_id]['questions']
        if len(pp) != len(rr) or not all(q['q'].startswith(p['q']) for p, q in zip(pp, rr)):
            raise ValueError('Question alignment failed: ' + term_id)
        definition = w['gloss_used']
        digest = hashlib.sha256(definition.encode()).hexdigest()
        catalog.append({'id': term_id, 'scope': w['labels']['subreddit'], 'term': w['term'],
                        'definition': definition, 'definition_sha256': digest,
                        'unit_type': 'local_definition', 'source_ref': 'historical auto gloss in reddit_v2_weights.jsonl',
                        'validation_status': 'provisional', 'dependencies': [], 'selectable': True})
        a_idx = list(range(0, len(pp), 2))
        a_scores.append({'id': term_id, 'definition_sha256': digest,
                         'mean_delta_p': statistics.mean(pp[i]['glossC']['p_correct'] - pp[i]['bare']['p_correct'] for i in a_idx),
                         'n_A': len(a_idx), 'question_ids': [f'{term_id}:A{i}' for i in a_idx],
                         'proxy_model': proxy[term_id]['model']})
        frequencies.append({'id': term_id, 'post_count': w['labels']['tf']})
    jsonl(OUT / 'catalog.jsonl', catalog)
    jsonl(OUT / 'a_scores.jsonl', a_scores)
    jsonl(OUT / 'frequency.jsonl', frequencies)
    config = {'catalog': 'catalog.jsonl', 'a_scores': 'a_scores.jsonl',
              'frequency': 'frequency.jsonl', 'budget_fraction': .25,
              'frequency_frame': {'type': 'historical_overlapping_development',
                                  'sha256': hashlib.sha256((DATA / 'reddit_v2_weights.jsonl').read_bytes()).hexdigest(),
                                  'overlap_check_passed': False},
              'b_start_utc': None, 'development_only': True,
              'out': 'plan_development_only.json'}
    (OUT / 'study_config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n')
    print('prepared', len(catalog), 'provisional historical terms at', OUT)


if __name__ == '__main__':
    main()
