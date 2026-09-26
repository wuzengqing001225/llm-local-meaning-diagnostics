#!/usr/bin/env python3
"""Create A diagnostics only from source-reviewed Boolean rule programs."""

import argparse
import collections
import hashlib
import json
from pathlib import Path

from rule_logic import check_card, evaluate


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def take(rows, definition_id, n):
    return sorted(rows, key=lambda x: sha({'definition_id': definition_id, 'case_id': x['id'], 'purpose': 'formal_A'}))[:n]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--programs', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--human-decisions', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    programs = {x['definition_id']: x for x in read_jsonl(a.programs)}
    sources = {x['candidate_id']: x for x in read_jsonl(a.source)}
    decisions = {x['definition_id']: x for x in read_jsonl(a.human_decisions)}
    accepted = [did for did, x in decisions.items() if x.get('decision') == 'accepted']
    if not accepted:
        raise ValueError('No accepted human-reviewed source rules')
    items, coverage = [], []
    for did in sorted(accepted):
        if did not in programs or did not in sources:
            raise ValueError('Decision references unknown source program: ' + did)
        row = programs[did]
        program = row['program']
        review = decisions[did]
        if review.get('program_sha256') != sha(program):
            raise ValueError('Program changed after human source review: ' + did)
        if review.get('source_complete') is not True or review.get('rule_faithful') is not True:
            raise ValueError('Incomplete source/logic approval: ' + did)
        if review.get('dependency_closed') is not True:
            raise ValueError('Unresolved source dependency: ' + did)
        if not isinstance(review.get('reviewer_id'), str) or not review['reviewer_id'].strip():
            raise ValueError('Missing reviewer id: ' + did)
        validation = check_card(program)
        facts = validation['field_domains']
        positive = [x for x in program['cases'] if evaluate(program['predicate'], x['facts'], facts)]
        negative = [x for x in program['cases'] if not evaluate(program['predicate'], x['facts'], facts)]
        chosen = take(positive, did, 2) + take(negative, did, 2)
        chosen.sort(key=lambda x: sha({'definition_id': did, 'case_id': x['id'], 'purpose': 'A_order'}))
        verdicts = review.get('case_verdicts')
        if not isinstance(verdicts, dict) or set(verdicts) != {x['id'] for x in chosen}:
            raise ValueError('Missing four independent source case verdicts: ' + did)
        labels = []
        for j, case in enumerate(chosen):
            inside = evaluate(program['predicate'], case['facts'], facts)
            if type(verdicts[case['id']]) is not bool or verdicts[case['id']] != inside:
                raise ValueError('Human source verdict differs from mechanical key: ' + did + ':' + case['id'])
            correct_letter = 'AB'[j % 2]
            yes_first = inside == (correct_letter == 'A')
            options = ['Yes, it falls within this contract-defined term.',
                       'No, it falls outside this contract-defined term.']
            if not yes_first:
                options.reverse()
            question = (f'Under this contract, does the following case fall within '
                        f'the term "{sources[did]["term"]}"? {case["fact_text"]}')
            items.append({
                'id': f'A:{did}:{case["id"]}',
                'study_split': 'A',
                'definition_id': did, 'contract_index': sources[did]['contract_index'],
                'cohort': sources[did]['cohort'], 'term': sources[did]['term'],
                'case_id': case['id'], 'question': question, 'options': options,
                'answer': correct_letter, 'facts': case['facts'],
                'source_rule_sha256': hashlib.sha256(sources[did]['proposal']['full_rule_quote'].encode()).hexdigest(),
                'human_review_id': review['reviewer_id'],
                'status': 'source_reviewed_A_not_scored',
            })
            labels.append(inside)
        if len(chosen) != 4 or sum(labels) != 2:
            raise ValueError('A balance failure: ' + did)
        coverage.append({'definition_id': did, 'A_case_ids': [x['id'] for x in chosen],
                         'program_sha256': review['program_sha256']})
    by_rule = collections.Counter(x['definition_id'] for x in items)
    if any(n != 4 for n in by_rule.values()):
        raise ValueError('A coverage failure')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(''.join(canonical(x) + '\n' for x in items))
    meta = {'status': 'source_reviewed_A_materialized_before_B_drafting',
            'n_rules': len(by_rule), 'n_A': len(items),
            'programs_sha256': hashlib.sha256(a.programs.read_bytes()).hexdigest(),
            'source_sha256': hashlib.sha256(a.source.read_bytes()).hexdigest(),
            'decisions_sha256': hashlib.sha256(a.human_decisions.read_bytes()).hexdigest(),
            'coverage': coverage}
    a.out.with_suffix('.manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(f'Materialized {len(items)} reviewed A questions across {len(by_rule)} rules.')


if __name__ == '__main__':
    main()
