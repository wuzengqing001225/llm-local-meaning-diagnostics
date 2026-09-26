#!/usr/bin/env python3
"""Blinded source-grounded pilot: budgeted membership definitions in group approvals."""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT / 'local_meaning_v7_allocation'))
from api import config_role, parse_json_object, request_one  # noqa: E402

MEMBERS = PARENT / 'gitlab_definition_choice_pilot_20260925/source_policy_pages/members.txt'
APPROVALS = PARENT / 'gitlab_definition_choice_pilot_20260925/source_policy_pages/approvals.txt'

DEFINITIONS = [
    {'id': 'direct', 'term': 'Direct member', 'definition': 'The user is added directly to the current group or project.'},
    {'id': 'inherited', 'term': 'Inherited member', 'definition': 'The user is a member of a parent group that contains the current group or project.'},
    {'id': 'shared', 'term': 'Shared member', 'definition': 'The user is a member of a group invited to the current group or project.'},
    {'id': 'inherited_shared', 'term': 'Inherited shared member', 'definition': 'The user is a member of a group invited to an ancestor of the current group or project.'},
]
RULE = 'For group-based approvals, only direct members of the group can approve merge requests. Inherited members of the eligible groups cannot provide approvals.'

AUTHOR = """You independently author a development set of six realistic requests about group-based merge-request approval in GitLab. You see only public source definitions and the public rule. You do not see A diagnostic questions, A scores, allocation policies, or target reader outcomes. In every request, a named group G is already configured as the sole group approver for a merge request requiring TWO distinct approvals. Name 4 to 6 possible approvers and state their exact membership paths in natural organizational language, without using the labels Direct, Inherited, Shared, or Inherited shared. Include at least one possible approver representing each of the four membership paths, so each source definition is relevant to the decision. The participants have no other membership paths or individual approver assignments; none is the author or committer. Ask ONE decision: can the group supply the two required eligible approvals from these people? Arrange exactly three yes and three no answers across six requests by varying the number of people actually added to G itself. Do not paraphrase the local definitions into a predicate checklist and do not disclose the conclusion in the reader-facing scenario. Use different realistic organizational hierarchies and invited groups, not just name changes. Return JSON only: {"items":[{"scenario":"self-contained scenario and single yes/no question","answer":"yes|no","private_mapping":"source-based membership mapping for every person","source_evidence":"exact relevant source wording"},...]}."""

CHECK = """Independently review each proposed request using the supplied full public source; proposed answers and private mappings are hidden. For the named approval group G, identify which people were added to G itself versus inherited membership from a parent, shared from an invited group, or inherited shared from an invitation to an ancestor. Count only those who independently qualify under the group approver rule. Reject any request if a path is missing, a person may have another access path, a rule outside the supplied source is needed, there is no unique yes/no answer, the source rule or answer is restated in the scenario, or fewer than four membership path types are substantively present. Return JSON only: {"items":[{"id":"...","valid":true or false,"answer":"yes|no|undetermined","all_four_paths_present":true or false,"facts_sufficient":true or false,"no_answer_leakage":true or false,"reason":"..."},...]}."""

READER = """Apply the supplied GitLab group approval rule to the request. No local definitions are supplied. If you cannot determine a unique yes/no answer from the rule and facts, say ABSTAIN. Return JSON only: {"answer":"YES|NO|ABSTAIN","reason":"one short sentence"}."""


def norm(s):
    return re.sub(r'\s+', ' ', s).strip().casefold()


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def write_rows(path, rows):
    path.write_text(''.join(canonical(x) + '\n' for x in rows))


def append(path, row):
    with path.open('a') as f:
        f.write(canonical(row) + '\n')


def source_card():
    members = norm(MEMBERS.read_text())
    approvals = norm(APPROVALS.read_text())
    for row in DEFINITIONS:
        if norm(row['definition']) not in members:
            raise RuntimeError('Definition not found verbatim in source snapshot: ' + row['id'])
    if norm(RULE) not in approvals:
        raise RuntimeError('Approval rule not found verbatim in source snapshot')
    return {'scope': 'gitlab_group_approval_current_docs_snapshot',
            'definition_source_url': 'https://docs.gitlab.com/user/project/members/',
            'rule_source_url': 'https://docs.gitlab.com/user/project/merge_requests/approvals/rules/',
            'definition_source_sha256': digest_file(MEMBERS),
            'rule_source_sha256': digest_file(APPROVALS),
            'definitions': DEFINITIONS, 'common_rule': RULE,
            'status': 'development_source_candidate_not_formal_gold'}


def call(config, role, system, data, max_tokens):
    spec = config_role(config, role)
    payload = {'model': spec['model'],
               'messages': [{'role': 'system', 'content': system},
                            {'role': 'user', 'content': canonical(data)}],
               'temperature': 0, 'max_tokens': max_tokens,
               'response_format': {'type': 'json_object'}}
    if 'deepseek' in spec['model'].lower():
        payload['thinking'] = {'type': 'disabled'}
    else:
        payload['reasoning_effort'] = 'none'
    t = time.monotonic()
    raw = request_one(spec, payload)
    parsed = parse_json_object(raw['content'])
    if not isinstance(parsed, dict):
        raise ValueError('Non-JSON model response')
    return {'requested_model': spec['model'], 'returned_model': raw['returned_model'],
            'provider_response_id': raw['provider_response_id'], 'usage': raw['usage'],
            'finish_reason': raw['finish_reason'], 'seconds': time.monotonic() - t,
            'input_sha256': hashlib.sha256(canonical(payload).encode()).hexdigest(),
            'result': parsed, 'raw_content': raw['content']}


def draft(config, source):
    p = HERE / 'B_drafts.jsonl'
    for batch in (1, 2):
        if any(x['batch'] == batch for x in records(p)):
            continue
        print('Draft B batch', batch, flush=True)
        out = call(config, 'draft', AUTHOR, {**source, 'batch': batch, 'randomized_seed_label': f'group-approval-{batch}'}, 6500)
        append(p, {'batch': batch, **out})
    rows = []
    for result in records(p):
        items = result['result'].get('items', [])
        if len(items) != 6:
            raise ValueError(f'Expected six items in batch {result["batch"]}, got {len(items)}')
        if sorted(x.get('answer') for x in items) != ['no'] * 3 + ['yes'] * 3:
            raise ValueError(f'Expected balanced yes/no answers in batch {result["batch"]}')
        for i, item in enumerate(items, 1):
            rows.append({'id': f'group_approval:{result["batch"]}:B{i}', **item,
                         'scope': source['scope'], 'definition_ids': [x['id'] for x in DEFINITIONS]})
    write_rows(HERE / 'B_candidates_private.jsonl', rows)
    return rows


def check(config, source, candidates):
    p = HERE / 'B_checks.jsonl'
    for batch in (1, 2):
        if any(x['batch'] == batch for x in records(p)):
            continue
        items = [{'id': x['id'], 'scenario': x['scenario']} for x in candidates
                 if x['id'].startswith(f'group_approval:{batch}:')]
        print('Check B batch', batch, flush=True)
        out = call(config, 'judge', CHECK, {'definitions': DEFINITIONS, 'rule': RULE, 'items': items}, 5500)
        append(p, {'batch': batch, **out})
    verdicts = {y.get('id'): y for x in records(p) for y in x['result'].get('items', [])}
    audit = []
    accepted = []
    for x in candidates:
        v = verdicts.get(x['id'], {})
        okay = all(v.get(k) is True for k in ('valid', 'all_four_paths_present', 'facts_sufficient', 'no_answer_leakage'))
        okay = okay and v.get('answer') == x['answer']
        audit.append({'id': x['id'], 'model_check_accept': okay, 'verdict': v, 'draft_answer': x['answer']})
        if okay:
            accepted.append(x)
    write_rows(HERE / 'B_quality_audit.jsonl', audit)
    write_rows(HERE / 'B_source_checked_provisional.jsonl', accepted)
    print('B candidates', len(candidates), 'model-check accepted', len(accepted), flush=True)


def bare(config, source):
    inputs = ['source_card.json', 'B_candidates_private.jsonl', 'B_quality_audit.jsonl', 'B_source_checked_provisional.jsonl']
    manifest = {x: digest_file(HERE / x) for x in inputs}
    lock = HERE / 'B_freeze.json'
    if lock.exists():
        if json.loads(lock.read_text())['sha256'] != manifest:
            raise RuntimeError('B changed after reader freeze')
    else:
        save(lock, {'status': 'development_B_frozen_before_bare_reader', 'sha256': manifest})
    accepted = records(HERE / 'B_source_checked_provisional.jsonl')
    output = HERE / 'bare_reader.jsonl'
    done = {(x['id'], x['role']) for x in records(output)}
    for item in accepted:
        prompt = {'common_rule': RULE, 'scenario': item['scenario'], 'abstain_allowed': True}
        for role in ('reader', 'second_judge'):
            if (item['id'], role) in done:
                continue
            print('Bare', item['id'], role, flush=True)
            out = call(config, role, READER, prompt, 650)
            if out['result'].get('answer') not in {'YES', 'NO', 'ABSTAIN'}:
                raise ValueError('Unparsed bare reader answer')
            append(output, {'id': item['id'], 'role': role, **out})
    trials = records(output)
    report = {'status': 'development_only_not_formal', 'n_model_checked': len(accepted), 'roles': {}, 'items': []}
    for role in ('reader', 'second_judge'):
        rs = []
        for item in accepted:
            x = next(x for x in trials if x['id'] == item['id'] and x['role'] == role)
            answer = x['result']['answer']
            gold = item['answer'].upper()
            rs.append({'id': item['id'], 'gold': gold, 'answer': answer,
                       'correct': answer == gold, 'abstain': answer == 'ABSTAIN'})
        report['roles'][role] = {'n': len(rs), 'correct': sum(x['correct'] for x in rs),
                                 'abstain': sum(x['abstain'] for x in rs),
                                 'substantive_wrong': sum(not x['correct'] and not x['abstain'] for x in rs)}
        report['items'].extend({'role': role, **x} for x in rs)
    save(HERE / 'bare_reader_analysis.json', report)
    print('Development bare reader', report['roles'], flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, default=PARENT / 'local_meaning_v4_config/config.json')
    p.add_argument('--stage', choices=['draft', 'check', 'bare', 'all'], default='all')
    a = p.parse_args()
    source = source_card()
    card_path = HERE / 'source_card.json'
    if card_path.exists():
        if json.loads(card_path.read_text()) != source:
            raise RuntimeError('Source card changed; start a new pilot version')
    else:
        save(card_path, source)
    if a.stage in {'draft', 'all'}:
        candidates = draft(a.config, source)
    elif a.stage == 'check':
        candidates = records(HERE / 'B_candidates_private.jsonl')
    else:
        candidates = []
    if a.stage in {'check', 'all'}:
        gate = json.loads((HERE / 'B_source_quality_gate.json').read_text())
        if gate.get('status') != 'APPROVED_BEFORE_SOURCE_CHECK':
            raise RuntimeError('B candidates failed source-only quality gate; do not run checker or readers')
        check(a.config, source, candidates)
    if a.stage in {'bare', 'all'}:
        gate = json.loads((HERE / 'B_source_quality_gate.json').read_text())
        if gate.get('status') != 'APPROVED_BEFORE_SOURCE_CHECK':
            raise RuntimeError('B candidates failed source-only quality gate; do not run checker or readers')
        bare(a.config, source)


if __name__ == '__main__':
    main()
