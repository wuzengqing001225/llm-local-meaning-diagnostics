#!/usr/bin/env python3
"""Select source-rule program version using only independent source judgements."""

import argparse
import collections
import hashlib
import json
from pathlib import Path


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def main():
    p = argparse.ArgumentParser()
    for name in ('first-programs', 'first-judgements', 'alternate-programs', 'alternate-judgements'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--out-programs', type=Path, required=True)
    p.add_argument('--out-judgements', type=Path, required=True)
    a = p.parse_args()
    first = {x['definition_id']: x for x in read(a.first_programs)}
    first_j = {x['definition_id']: x for x in read(a.first_judgements)}
    alternate = {x['definition_id']: x for x in read(a.alternate_programs)}
    alternate_j = {x['definition_id']: x for x in read(a.alternate_judgements)}
    if set(first) != set(first_j) or set(alternate) != set(alternate_j):
        raise ValueError('Missing source judgement')
    rank = {'accept': 0, 'revise': 1, 'reject': 2, 'unparsed': 3}
    programs, judgements = [], []
    provenance = []
    for did in sorted(first):
        options = [(first[did], first_j[did], 'first')]
        if did in alternate:
            options.append((alternate[did], alternate_j[did], 'alternate'))
        def key(option):
            program, judge, origin = option
            vote = (judge.get('proposal') or {}).get('recommendation', 'unparsed')
            return (rank.get(vote, 3), -program['current_schema_validation']['n_unique_fact_vectors'],
                    origin != 'first')
        chosen, judge, origin = min(options, key=key)
        vote = (judge.get('proposal') or {}).get('recommendation', 'unparsed')
        programs.append({**chosen, 'selection_stage': 'source_judgement_preferred',
                         'selected_judge_recommendation': vote})
        judgements.append(judge)
        provenance.append({'definition_id': did, 'chosen': origin, 'vote': vote,
                           'other_vote': ((options[1 if origin == 'first' else 0][1].get('proposal') or {}).get('recommendation')
                                          if len(options) == 2 else None)})
    a.out_programs.parent.mkdir(parents=True, exist_ok=True)
    a.out_programs.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in programs))
    a.out_judgements.write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in judgements))
    meta = {'status': 'source_only_version_selection_before_new_A_or_B_outcomes',
            'n_programs': len(programs), 'by_vote': dict(collections.Counter(x['selected_judge_recommendation'] for x in programs)),
            'by_cohort_vote': dict(collections.Counter((x['source_cohort'], x['selected_judge_recommendation']) for x in programs)),
            'provenance': provenance,
            'input_hashes': {name: hashlib.sha256(getattr(a, name.replace('-', '_')).read_bytes()).hexdigest()
                             for name in ('first-programs', 'first-judgements', 'alternate-programs', 'alternate-judgements')}}
    # JSON object keys must be strings; encode the cohort/vote counts compactly.
    meta['by_cohort_vote'] = {f'{cohort}|{vote}': count for (cohort, vote), count in
                              collections.Counter((x['source_cohort'], x['selected_judge_recommendation']) for x in programs).items()}
    a.out_programs.with_suffix('.manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(f"Selected {len(programs)} reviewed versions: {meta['by_vote']}")


if __name__ == '__main__':
    main()
