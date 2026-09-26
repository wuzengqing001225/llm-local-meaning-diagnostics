#!/usr/bin/env python3
"""Choose source-only alternate programs for earlier revise/reject judgements."""

import argparse
import collections
import hashlib
import json
from pathlib import Path

from rule_logic import RuleError, check_card


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--selected', type=Path, required=True)
    p.add_argument('--judgements', type=Path, required=True)
    p.add_argument('--programs', type=Path, nargs='+', required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    selected = {x['definition_id']: x for x in read(a.selected)}
    judges = {x['definition_id']: x for x in read(a.judgements)}
    options = collections.defaultdict(list)
    for path in a.programs:
        for row in read(path):
            try:
                validation = check_card(row['program'])
            except (RuleError, KeyError, TypeError, ValueError):
                continue
            options[row['definition_id']].append((validation, row, path))
    output = []
    for did, chosen in sorted(selected.items()):
        if (judges[did].get('proposal') or {}).get('recommendation') not in {'revise', 'reject'}:
            continue
        remaining = [x for x in options[did] if x[1]['input_sha256'] != chosen['input_sha256']]
        if not remaining:
            continue
        remaining.sort(key=lambda x: (-x[0]['n_unique_fact_vectors'],
                                      x[0]['n_repeated_fact_vectors'],
                                      x[1].get('generation_mode') != 'non_thinking_json', str(x[2])))
        validation, row, path = remaining[0]
        output.append({**row,
                       'source_cohort': chosen['source_cohort'],
                       'source_contract_index': chosen['source_contract_index'],
                       'selected_from': str(path),
                       'current_schema_validation': validation,
                       'alternative_to_input_sha256': chosen['input_sha256'],
                       'status': 'unreviewed_alternative_source_only_program'})
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in output))
    meta = {'status': 'source_only_alternative_programs_before_new_A_or_B_outcomes',
            'n_alternatives': len(output),
            'by_cohort': dict(collections.Counter(x['source_cohort'] for x in output)),
            'selected_sha256': hashlib.sha256(a.selected.read_bytes()).hexdigest(),
            'judgements_sha256': hashlib.sha256(a.judgements.read_bytes()).hexdigest()}
    a.out.with_suffix('.manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(f"Selected {len(output)} alternative source-only programs.")


if __name__ == '__main__':
    main()
