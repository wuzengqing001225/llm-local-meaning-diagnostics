#!/usr/bin/env python3
"""Materialize independent B drafts into public tasks and sealed gold keys.

No B reader outcomes are loaded. Cases remain pending quality review.
"""

import argparse
import collections
import hashlib
import json
from pathlib import Path

from draft_B_independent import check_B
from rule_logic import check_card, evaluate


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vector(facts):
    return tuple((key, str(value)) for key, value in sorted(facts.items()))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--drafts', type=Path, required=True)
    p.add_argument('--programs', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--human-decisions', type=Path, required=True)
    p.add_argument('--A-items', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    programs = {x['definition_id']: x for x in read(a.programs)}
    source = {x['candidate_id']: x for x in read(a.source)}
    reviews = {x['definition_id']: x for x in read(a.human_decisions)}
    a_vectors = collections.defaultdict(set)
    for row in read(a.A_items):
        a_vectors[row['definition_id']].add(vector(row['facts']))
    drafts = {x['definition_id']: x for x in read(a.drafts)}
    public, private, overlap = [], [], []
    for did, row in sorted(drafts.items()):
        if not row.get('draft_structure_valid'):
            continue
        if did not in programs or did not in source or did not in reviews:
            raise ValueError('Missing reviewed source program for B: ' + did)
        program = programs[did]['program']
        review = reviews[did]
        if review.get('decision') != 'accepted' or review.get('program_sha256') != sha(program):
            raise ValueError('B source rule not approved: ' + did)
        if review.get('source_complete') is not True or review.get('rule_faithful') is not True:
            raise ValueError('Incomplete human source approval: ' + did)
        if review.get('dependency_closed') is not True:
            raise ValueError('Unresolved source dependency: ' + did)
        labels = check_B(program, row['draft'])
        fields = check_card(program)['field_domains']
        for i, (case, inside) in enumerate(zip(row['draft']['cases'], labels)):
            if inside != evaluate(program['predicate'], case['facts'], fields):
                raise ValueError('Mechanical key mismatch')
            correct = 'AB'[i % 2]
            yes_first = inside == (correct == 'A')
            options = ['Yes, the contract-defined term applies.', 'No, the contract-defined term does not apply.']
            if not yes_first:
                options.reverse()
            task_id = f'B:{did}:{case["id"]}'
            task = {
                'id': task_id, 'definition_id': did,
                'term': source[did]['term'], 'contract_index': source[did]['contract_index'],
                'cohort': source[did]['cohort'],
                'question': case['question'], 'options': options,
                'source_rule_sha256': hashlib.sha256(source[did]['proposal']['full_rule_quote'].encode()).hexdigest(),
                'B_author_model': row['requested_model'],
                'B_author_request_sha256': row['input_sha256'],
                'status': 'independent_B_draft_pending_quality_review',
            }
            if task_id in {x['id'] for x in public}:
                raise ValueError('Duplicate B id')
            public.append(task)
            same_vector = vector(case['facts']) in a_vectors[did]
            private.append({
                'id': task_id, 'definition_id': did, 'case_id': case['id'],
                'answer': correct, 'oracle_membership': inside,
                'fact_fields': case['facts'], 'same_fact_vector_as_A': same_vector,
                'program_sha256': sha(program), 'source_reviewer_id': review['reviewer_id'],
                'quality_review_status': 'pending',
            })
            if same_vector:
                overlap.append(task_id)
    if len({x['id'] for x in public}) != len(public):
        raise ValueError('Duplicate B task')
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / 'tasks_B_public.jsonl').write_text(''.join(canonical(x) + '\n' for x in public))
    (a.out / 'gold_B_private.jsonl').write_text(''.join(canonical(x) + '\n' for x in private))
    meta = {
        'status': 'B_materialized_before_reader_outcomes_pending_quality_review',
        'n_B': len(public), 'n_rules': len({x['definition_id'] for x in public}),
        'same_fact_vector_as_A_count': len(overlap), 'same_fact_vector_ids': overlap,
        'input_hashes': {k: filehash(v) for k, v in {'drafts': a.drafts, 'programs': a.programs,
            'source': a.source, 'human_decisions': a.human_decisions, 'A_items': a.A_items}.items()},
        'caveat': 'Public B facts were authored without A scores/items. Mechanical labels depend on source-reviewed programs; every B still needs quality checks before reader runs.',
    }
    (a.out / 'manifest.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(f'Materialized {len(public)} B drafts across {meta["n_rules"]} rules; {len(overlap)} share an A fact vector.')


if __name__ == '__main__':
    main()
