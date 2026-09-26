#!/usr/bin/env python3
"""Select one schema-valid source-only program per term, without outcomes."""

import argparse
import collections
import hashlib
import json
from pathlib import Path

from rule_logic import RuleError, check_card


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--programs', type=Path, nargs='+', required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    source = {x['candidate_id']: x for x in read(a.source)}
    options = collections.defaultdict(list)
    for path in a.programs:
        for row in read(path):
            did = row['definition_id']
            if did not in source or not source[did]['eligible_auto']:
                raise ValueError('Program without eligible source proposal: ' + did)
            try:
                validation = check_card(row['program'])
            except (RuleError, KeyError, TypeError, ValueError):
                continue
            options[did].append((validation, row, path))
    selected = []
    for did, choices in sorted(options.items()):
        # Source-only diversity preference. Nothing here reads A or B outcomes.
        choices.sort(key=lambda x: (-x[0]['n_unique_fact_vectors'],
                                    x[0]['n_repeated_fact_vectors'],
                                    x[1].get('generation_mode') != 'non_thinking_json',
                                    str(x[2])))
        validation, row, path = choices[0]
        selected.append({
            **row,
            'source_cohort': source[did]['cohort'],
            'source_contract_index': source[did]['contract_index'],
            'selected_from': str(path),
            'current_schema_validation': validation,
            'status': 'selected_unreviewed_source_only_program_no_A_or_B_outcomes',
        })
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in selected))
    meta = {
        'status': 'source_only_program_selection_before_new_A_or_B_outcomes',
        'source_sha256': sha(a.source),
        'program_files': [{'path': str(path), 'sha256': sha(path)} for path in a.programs],
        'selection_rule': 'schema-valid; prefer greater unique fact-vector count, fewer repeats, then non-thinking mode',
        'n_selected': len(selected),
        'by_cohort': dict(collections.Counter(x['source_cohort'] for x in selected)),
        'challenge_contracts': len({x['source_contract_index'] for x in selected if x['source_cohort'] != 'source_sample_candidate'}),
        'caveat': 'Syntactic validity and a source quote do not establish semantic validity. Every selected program needs source review.',
    }
    a.out.with_suffix('.manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(f"Selected {len(selected)} unreviewed programs: {meta['by_cohort']}")


if __name__ == '__main__':
    main()
