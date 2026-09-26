#!/usr/bin/env python3
"""Second deterministic source-only reserve, if first reviewable yield is low."""

import argparse
import collections
import hashlib
import json
from pathlib import Path


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent-frame', type=Path, required=True)
    p.add_argument('--first-topup', type=Path, required=True)
    p.add_argument('--parent-manifest', type=Path, required=True)
    p.add_argument('--source-audit', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    used = {x['definition_id'] for path in (a.parent_frame, a.first_topup) for x in read(path)}
    docs = set(json.loads(a.parent_manifest.read_text())['contract_split']['challenge_pool'])
    groups = collections.defaultdict(list)
    for row in read(a.source_audit):
        if (row['contract_index'] in docs and row['id'] not in used and not row['review_flags']
                and 6 <= len(row['definition'].split()) <= 160):
            groups[row['contract_index']].append(row)
    rows = []
    for ci in sorted(docs):
        candidates = sorted(groups[ci], key=lambda x: hashlib.sha256(('v5-source-topup2:' + x['id']).encode()).hexdigest())
        for rank, row in enumerate(candidates[:2], 1):
            rows.append({
                'definition_id': row['id'], 'term': row['term'],
                'contract_index': ci, 'contract_title': row['contract'],
                'cohort': 'challenge_topup2_candidate',
                'reserve_rank_within_contract': rank,
                'source_only_priority': row['source_only_priority'],
                'extracted_definition': row['definition'],
                'source_hit': row['first_source_hit'],
                'source_review_flags': row['review_flags'],
                'status': 'unreviewed_source_candidate',
            })
    if set(x['definition_id'] for x in rows) & used:
        raise ValueError('Reserve overlaps earlier candidate frames')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows))
    meta = {'status': 'second_source_only_reserve_before_formal_A_or_B_outcomes',
            'reason': 'Only 83 challenge programs were accept/revise after two automated source checks; reserve candidates before any formal A/B reader result.',
            'parent_frame_sha256': sha(a.parent_frame), 'first_topup_sha256': sha(a.first_topup),
            'source_audit_sha256': sha(a.source_audit),
            'n_candidates': len(rows), 'n_contracts': len({x['contract_index'] for x in rows}),
            'caveat': 'Source-only candidates; model triage, rule-program checks and human review remain.'}
    a.out.with_suffix('.manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(f'Frozen {len(rows)} second-reserve candidates across {meta["n_contracts"]} contracts.')


if __name__ == '__main__':
    main()
