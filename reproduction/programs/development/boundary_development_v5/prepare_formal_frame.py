#!/usr/bin/env python3
"""Freeze a source-only candidate frame before any new A/B reader outcomes.

This is a screening frame, not a set of accepted rule cards or tasks.
"""

import argparse
import collections
import hashlib
import json
from pathlib import Path


DEV_CONTRACTS = {38, 108, 170, 171, 250}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def order_key(prefix, value):
    return hashlib.sha256(f'{prefix}:{value}'.encode()).hexdigest()


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-audit', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    rows = [json.loads(x) for x in a.source_audit.read_text().splitlines() if x.strip()]
    docs = sorted({r['contract_index'] for r in rows} - DEV_CONTRACTS,
                  key=lambda d: order_key('v5-split', d))
    if len(docs) < 220:
        raise ValueError('Insufficient source documents for the frozen split')
    challenge_docs = set(docs[:180])
    source_docs = set(docs[180:])
    eligible = [r for r in rows if r['contract_index'] not in DEV_CONTRACTS
                and not r['review_flags'] and 6 <= len(r['definition'].split()) <= 160]
    clean_by_doc = collections.defaultdict(list)
    all_by_doc = collections.defaultdict(list)
    for r in rows:
        if r['contract_index'] not in DEV_CONTRACTS:
            all_by_doc[r['contract_index']].append(r)
    for r in eligible:
        clean_by_doc[r['contract_index']].append(r)
    chosen = []
    for ci in docs:
        if ci in challenge_docs:
            for group in ('boundary_possible', 'ordinary'):
                candidates = [r for r in clean_by_doc[ci] if r['source_only_priority'] == group]
                if candidates:
                    r = min(candidates, key=lambda x: order_key('v5-challenge-rule', x['id']))
                    chosen.append((r, 'challenge_candidate'))
        else:
            candidates = all_by_doc[ci]
            if candidates:
                r = min(candidates, key=lambda x: order_key('v5-source-rule', x['id']))
                chosen.append((r, 'source_sample_candidate'))
    frame = []
    for r, cohort in chosen:
        hit = r['first_source_hit']
        frame.append({
            'definition_id': r['id'], 'term': r['term'],
            'contract_index': r['contract_index'], 'contract_title': r['contract'],
            'cohort': cohort, 'source_only_priority': r['source_only_priority'],
            'extracted_definition': r['definition'],
            'source_hit': hit,
            'source_review_flags': r['review_flags'],
            'status': 'unreviewed_source_candidate',
        })
    if len({x['definition_id'] for x in frame}) != len(frame):
        raise ValueError('Duplicate source candidate')
    if {x['contract_index'] for x in frame if x['cohort'] == 'challenge_candidate'} & source_docs:
        raise ValueError('Cohort document overlap')
    a.out.mkdir(parents=True, exist_ok=True)
    write_jsonl(a.out / 'candidate_frame.jsonl', frame)
    summary = {
        'status': 'source_only_candidate_frame_frozen_before_new_A_or_B_outcomes',
        'source_audit_path': str(a.source_audit), 'source_audit_sha256': digest(a.source_audit),
        'source_records': len(rows), 'dev_contract_indices': sorted(DEV_CONTRACTS),
        'contract_split': {'challenge_pool': sorted(challenge_docs), 'source_sample_pool': sorted(source_docs)},
        'selection': {
            'challenge': 'up to one clean boundary-keyword and one clean other definition per contract, SHA256 tie-break',
            'source_sample': 'one definition from all records per contract by SHA256, including flagged records',
            'clean_filter': 'no automatic review flags and 6-160 definition words',
        },
        'candidate_counts': dict(collections.Counter(x['cohort'] for x in frame)),
        'candidate_contract_counts': {group: len({x['contract_index'] for x in frame if x['cohort'] == group})
                                      for group in ('challenge_candidate', 'source_sample_candidate')},
        'source_sample_review_flags': dict(collections.Counter(
            flag for x in frame if x['cohort'] == 'source_sample_candidate' for flag in x['source_review_flags'])),
        'caveats': ['Challenge and source-sampled candidate cohorts are different selection frames.',
                    'No item is yet an accepted rule or answer key.',
                    'Source-sampled questions are generated, not natural user traffic.'],
    }
    (a.out / 'frame_manifest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(f"Frozen {len(frame)} source candidates: {summary['candidate_counts']}")


if __name__ == '__main__':
    main()
