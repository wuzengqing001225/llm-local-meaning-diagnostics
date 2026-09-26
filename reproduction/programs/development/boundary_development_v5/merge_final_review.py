#!/usr/bin/env python3
"""Combine complete source-only review candidates and their automated votes."""

import argparse
import collections
import hashlib
import json
from pathlib import Path


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, rows):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in rows))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-files', type=Path, nargs='+', required=True)
    p.add_argument('--base-programs', type=Path, required=True)
    p.add_argument('--base-judgements', type=Path, required=True)
    p.add_argument('--reserve-programs', type=Path, required=True)
    p.add_argument('--reserve-judgements', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    sources = {}
    for path in a.source_files:
        for row in read(path):
            did = row['candidate_id']
            if did in sources:
                raise ValueError('Source record overlap: ' + did)
            sources[did] = row
    base = {x['definition_id']: x for x in read(a.base_programs)}
    base_j = {x['definition_id']: x for x in read(a.base_judgements)}
    reserve_all = {x['definition_id']: x for x in read(a.reserve_programs)}
    reserve_j = {x['definition_id']: x for x in read(a.reserve_judgements)}
    if set(base) != set(base_j) or not set(reserve_j) <= set(reserve_all):
        raise ValueError('Program/judgement coverage mismatch')
    reserve = {k: reserve_all[k] for k in reserve_j}
    if set(base) & set(reserve):
        raise ValueError('Base/reserve program overlap')
    programs = {**base, **reserve}
    judgements = {**base_j, **reserve_j}
    if not set(programs) <= set(sources):
        raise ValueError('Program missing original source proposal')
    a.out.mkdir(parents=True, exist_ok=True)
    write(a.out / 'all_source_proposals.jsonl', [sources[k] for k in sorted(sources)])
    write(a.out / 'all_review_programs.jsonl', [programs[k] for k in sorted(programs)])
    write(a.out / 'all_review_judgements.jsonl', [judgements[k] for k in sorted(judgements)])
    votes = collections.Counter((judgements[k].get('proposal') or {}).get('recommendation','unparsed') for k in programs)
    cohort_votes = collections.Counter((sources[k]['cohort'], (judgements[k].get('proposal') or {}).get('recommendation','unparsed'))
                                      for k in programs)
    result = {
        'status': 'source_only_automated_review_complete_before_formal_A_or_B_outcomes',
        'n_source_candidates': len(sources), 'n_schema_valid_programs_with_judgements': len(programs),
        'votes': dict(votes),
        'cohort_votes': {f'{cohort}|{vote}': n for (cohort,vote),n in cohort_votes.items()},
        'reviewable_challenge_contracts': len({sources[k]['contract_index'] for k in programs
            if sources[k]['cohort'] != 'source_sample_candidate' and (judgements[k].get('proposal') or {}).get('recommendation') in {'accept','revise'}}),
        'inputs': {name: {'path': str(path), 'sha256': sha(path)} for name,path in {
            'base_programs':a.base_programs,'base_judgements':a.base_judgements,
            'reserve_programs':a.reserve_programs,'reserve_judgements':a.reserve_judgements}.items()},
        'source_inputs': [{'path': str(path), 'sha256': sha(path)} for path in a.source_files],
        'caveat': 'These are model-reviewed source programs, not human-approved rules or valid B gold.',
    }
    (a.out / 'all_review_manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f"Merged {len(sources)} source candidates and {len(programs)} reviewed programs: {dict(votes)}")


if __name__ == '__main__':
    main()
