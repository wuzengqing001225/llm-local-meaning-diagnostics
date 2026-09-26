#!/usr/bin/env python3
"""Deterministic source-only reserve frame when primary screening yield is low.

The top-up rule is fixed before formal A scores, B items, or reader outcomes.
"""

import argparse
import collections
import hashlib
import json
from pathlib import Path


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent-frame', type=Path, required=True)
    p.add_argument('--parent-manifest', type=Path, required=True)
    p.add_argument('--source-audit', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    selected = read_jsonl(args.parent_frame)
    used = {x['definition_id'] for x in selected}
    manifest = json.loads(args.parent_manifest.read_text())
    docs = set(manifest['contract_split']['challenge_pool'])
    groups = collections.defaultdict(list)
    for x in read_jsonl(args.source_audit):
        if (x['contract_index'] in docs and x['id'] not in used and not x['review_flags']
                and 6 <= len(x['definition'].split()) <= 160):
            groups[x['contract_index']].append(x)
    rows = []
    for ci in sorted(docs):
        order = sorted(groups[ci], key=lambda x: hashlib.sha256(('v5-source-topup:' + x['id']).encode()).hexdigest())
        for rank, x in enumerate(order[:2], 1):
            rows.append({
                'definition_id': x['id'], 'term': x['term'],
                'contract_index': ci, 'contract_title': x['contract'],
                'cohort': 'challenge_topup_candidate',
                'reserve_rank_within_contract': rank,
                'source_only_priority': x['source_only_priority'],
                'extracted_definition': x['definition'],
                'source_hit': x['first_source_hit'],
                'source_review_flags': x['review_flags'],
                'status': 'unreviewed_source_candidate',
            })
    if set(x['definition_id'] for x in rows) & used:
        raise ValueError('Top-up overlaps parent frame')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows))
    result = {
        'status': 'source_only_challenge_reserve_frozen_before_formal_A_or_B_outcomes',
        'reason': 'Plan two additional clean candidates per challenge contract if initial source-only eligibility yield is insufficient for planned rule count.',
        'parent_frame_sha256': filehash(args.parent_frame),
        'parent_manifest_sha256': filehash(args.parent_manifest),
        'source_audit_sha256': filehash(args.source_audit),
        'n_candidates': len(rows),
        'n_contracts': len({x['contract_index'] for x in rows}),
        'priority_counts': dict(collections.Counter(x['source_only_priority'] for x in rows)),
        'caveat': 'This is a reserve source frame, not accepted source rules or B tasks.',
    }
    args.out.with_suffix('.manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'Frozen {len(rows)} reserve candidates in {result["n_contracts"]} challenge contracts.')


if __name__ == '__main__':
    main()
