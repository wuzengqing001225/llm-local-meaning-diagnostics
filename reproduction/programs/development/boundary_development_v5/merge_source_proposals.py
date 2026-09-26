#!/usr/bin/env python3
"""Merge completed base and source-only reserve triage without changing votes."""

import argparse
import hashlib
import json
from pathlib import Path


def load(path):
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    by = {}
    for row in rows:
        by[row['candidate_id']] = row  # latest retry wins
    return by


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--topup', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    base = load(a.base)
    topup = load(a.topup)
    if set(base) & set(topup):
        raise ValueError('Base and reserve candidate overlap')
    if len(base) != 323 or len(topup) != 225:
        raise ValueError('Source triage incomplete')
    rows = [base[k] for k in sorted(base)] + [topup[k] for k in sorted(topup)]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows))
    meta = {'status': 'merged_unreviewed_source_only_triage',
            'base_sha256': sha(a.base), 'topup_sha256': sha(a.topup),
            'n_base': len(base), 'n_topup': len(topup), 'n_eligible': sum(x['eligible_auto'] for x in rows),
            'n_challenge_eligible': sum(x['eligible_auto'] and x['cohort'] != 'source_sample_candidate' for x in rows),
            'n_source_sample_eligible': sum(x['eligible_auto'] and x['cohort'] == 'source_sample_candidate' for x in rows)}
    a.out.with_suffix('.manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(meta)


if __name__ == '__main__':
    main()
