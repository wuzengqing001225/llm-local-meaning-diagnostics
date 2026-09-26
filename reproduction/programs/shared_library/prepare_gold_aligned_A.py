#!/usr/bin/env python3
"""Export historical Reddit A questions without any reader outcomes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'release_20260923/llm-idf-reproduce/data/reddit/raw_outputs'
OUT = ROOT / 'gold_aligned_development'


def load(filename):
    return {x['id']: x for x in (json.loads(line) for line in (SOURCE / filename).open())}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    proxy = load('lpmc_reddit_v2.jsonl')
    reader = load('reddit_v2_eqa.jsonl')
    weights = load('reddit_v2_weights.jsonl')
    packet = []
    for term_id in sorted(proxy.keys() & reader.keys() & weights.keys()):
        w = weights[term_id]
        if not w['labels'].get('is_target') or len(proxy[term_id]['per_question']) < 2:
            continue
        old = proxy[term_id]['per_question']
        all_q = reader[term_id]['questions']
        if len(old) != len(all_q) or not all(q['q'].startswith(p['q']) for p, q in zip(old, all_q)):
            raise ValueError('Historical A question alignment failed: ' + term_id)
        gloss = w['gloss_gold']
        if not gloss:
            raise ValueError('Missing historical glossary definition: ' + term_id)
        a_questions = [{'id': f'{term_id}:A{i}', 'q': all_q[i]['q'],
                        'options': all_q[i]['options'], 'answer': all_q[i]['answer']}
                       for i in range(0, len(all_q), 2)]
        packet.append({'id': term_id, 'scope': w['labels']['subreddit'], 'term': w['term'],
                       'definition': gloss, 'definition_sha256': hashlib.sha256(gloss.encode()).hexdigest(),
                       'questions_A': a_questions,
                       'status': 'development_existing_questions_not_independent_future_B'})
    OUT.mkdir(exist_ok=True)
    path = OUT / 'A_gold_packet.jsonl'
    path.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in packet))
    manifest = {'n_terms': len(packet), 'n_A_questions': sum(len(x['questions_A']) for x in packet),
                'A_packet_sha256': sha(path),
                'source_hashes': {name: sha(SOURCE / name) for name in
                                  ('lpmc_reddit_v2.jsonl', 'reddit_v2_eqa.jsonl', 'reddit_v2_weights.jsonl')},
                'reader_outcomes_in_A_packet': False,
                'development_only': True}
    (OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'n_terms': manifest['n_terms'], 'n_A_questions': manifest['n_A_questions'],
                      'packet': str(path)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
