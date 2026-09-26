#!/usr/bin/env python3
"""Small answer-blind development pilot for allocating public local definitions.

Run from any directory with `python run_pilot.py --config /path/to/config.json`.
Credentials are read in memory only and are never saved to result files.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
sys.path.insert(0, str(PARENT / 'local_meaning_v7_allocation'))
from api import config_role, parse_json_object, request_one  # noqa: E402

SOURCE = PARENT / 'definition_allocation_scope_audit_20260925' / 'gitlab_auth_definitions_provisional.jsonl'
GROUPS = {
    'token_scope': ['auth_018', 'auth_019', 'auth_020', 'auth_021'],
    'access_construct': ['auth_032', 'auth_033', 'auth_034', 'auth_037'],
    'account_kind': ['auth_026', 'auth_027', 'auth_028'],
}

B_SYSTEM = """You are an independent author of applied questions about a public organization's glossary. You do not see A diagnostic questions, A scores, budget policies, or target reader results. Create exactly FOUR realistic, concrete requests for the supplied group. Each asks which ONE of the listed local terms best names the described object or arrangement. Describe ordinary facts, not a glossary paraphrase or a checklist of defining predicates. Never put a local definition, answer, or option-specific hint in the scenario. The options are the given terms in the given order. Make at least two different terms correct across the four requests. All necessary facts must be in the scenario, and the full provided glossary must imply one uniquely best answer. If a term is a subtype or could overlap another option, avoid such an ambiguous scenario. Do not invent GitLab behavior beyond the supplied definitions. Return JSON only: {"items":[{"scenario":"...","question":"Which listed local term best fits this situation?","answer_id":"one supplied ID","source_evidence":"exact phrase in the supplied definition","mapping_private":"why the concrete facts entail this answer and rule out each distractor"},...]}."""

CHECK_SYSTEM = """You independently check public-glossary classification questions before any target reader test. The candidate author's answers are hidden. From the supplied definitions and scenario alone, identify whether exactly ONE listed term is the best label. Reject a request if two options can both fit, a fact is missing, a required rule is outside the definitions, the scenario paraphrases the winning definition too closely, or a term's name alone makes the answer trivial. Return JSON only: {"items":[{"id":"...","valid":true or false,"answer_id":"one supplied ID or undetermined","unique_answer":true or false,"definition_needed":true or false,"no_definition_leakage":true or false,"reason":"..."},...]}."""

READER_SYSTEM = """Answer from the scenario and the listed term names only. No glossary is supplied. If the information is insufficient to identify a single best local term, abstain. Return JSON only: {"choice":"A|B|C|D|ABSTAIN","reason":"one brief sentence"}."""


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def save_rows(path, items):
    path.write_text(''.join(canonical(x) + '\n' for x in items))


def source_cards():
    defs = {x['id']: x for x in rows(SOURCE)}
    cards = []
    for group, ids in GROUPS.items():
        cards.append({'group': group, 'scope': 'gitlab_auth_glossary_current_snapshot',
                      'source_url': 'https://docs.gitlab.com/auth/auth_glossary/',
                      'definitions': [{k: defs[i][k] for k in ('id', 'term', 'definition')} for i in ids],
                      'source_catalog_sha256': sha(SOURCE),
                      'status': 'development_source_candidate_not_formal_gold'})
    return cards


def call(config, role, system, data, max_tokens):
    spec = config_role(config, role)
    payload = {'model': spec['model'],
               'messages': [{'role': 'system', 'content': system},
                            {'role': 'user', 'content': canonical(data)}],
               'temperature': 0,
               'max_tokens': max_tokens,
               'response_format': {'type': 'json_object'}}
    if 'deepseek' in spec['model'].lower():
        payload['thinking'] = {'type': 'disabled'}
    else:
        payload['reasoning_effort'] = 'none'
    started = time.monotonic()
    result = request_one(spec, payload)
    parsed = parse_json_object(result['content'])
    if not isinstance(parsed, dict):
        raise ValueError('Model did not return a JSON object')
    return {'input_sha256': hashlib.sha256(canonical(payload).encode()).hexdigest(),
            'requested_model': spec['model'], 'returned_model': result['returned_model'],
            'provider_response_id': result['provider_response_id'], 'usage': result['usage'],
            'finish_reason': result['finish_reason'], 'seconds': time.monotonic() - started,
            'result': parsed, 'raw_content': result['content']}


def append(path, item):
    with path.open('a') as f:
        f.write(canonical(item) + '\n')


def draft_b(config, cards):
    path = HERE / 'B_drafts.jsonl'
    completed = {x['group']: x for x in rows(path)} if path.exists() else {}
    for card in cards:
        group = card['group']
        if group in completed:
            continue
        print('Drafting B', group, flush=True)
        response = call(config, 'draft', B_SYSTEM, card, 4000)
        append(path, {'group': group, **response})
    drafts = rows(path)
    candidates = []
    for card in cards:
        group = card['group']
        record = next((x for x in drafts if x['group'] == group), None)
        if record is None:
            raise RuntimeError(f'Missing B draft for {group}')
        items = record['result'].get('items')
        if not isinstance(items, list) or len(items) != 4:
            raise ValueError(f'B author produced invalid item count for {group}')
        ids = {x['id'] for x in card['definitions']}
        if len({x.get('answer_id') for x in items}) < 2:
            raise ValueError(f'B author used only one answer in {group}')
        for i, item in enumerate(items, 1):
            if item.get('answer_id') not in ids or not isinstance(item.get('scenario'), str):
                raise ValueError(f'Invalid B answer or scenario in {group}:{i}')
            candidates.append({'id': f'{group}:B{i}', 'group': group, **item,
                               'options': [{k: x[k] for k in ('id', 'term')} for x in card['definitions']],
                               'source_catalog_sha256': card['source_catalog_sha256']})
    save_rows(HERE / 'B_candidates_private.jsonl', candidates)
    return candidates


def check_b(config, cards, candidates):
    path = HERE / 'B_checks.jsonl'
    completed = {x['group']: x for x in rows(path)} if path.exists() else {}
    for card in cards:
        group = card['group']
        if group in completed:
            continue
        items = [{k: x[k] for k in ('id', 'scenario', 'question', 'options')}
                 for x in candidates if x['group'] == group]
        data = {'source_url': card['source_url'], 'definitions': card['definitions'], 'items': items}
        print('Checking B', group, flush=True)
        response = call(config, 'judge', CHECK_SYSTEM, data, 4500)
        append(path, {'group': group, **response})
    verdicts = {}
    for record in rows(path):
        for item in record['result'].get('items', []):
            verdicts[item.get('id')] = item
    audit = []
    accepted = []
    for item in candidates:
        v = verdicts.get(item['id'], {})
        okay = all(v.get(k) is True for k in ('valid', 'unique_answer', 'definition_needed', 'no_definition_leakage'))
        okay = okay and v.get('answer_id') == item['answer_id']
        audit.append({'id': item['id'], 'accepted_by_model_checks': okay, 'source_checker': v,
                      'draft_answer_id': item['answer_id']})
        if okay:
            accepted.append(item)
    save_rows(HERE / 'B_quality_audit.jsonl', audit)
    save_rows(HERE / 'B_source_checked_provisional.jsonl', accepted)
    print(f'B candidates {len(candidates)}; model-check accepted {len(accepted)}. Human/source audit still required.', flush=True)


def bare_reader(config):
    frozen = ['source_cards.jsonl', 'B_candidates_private.jsonl', 'B_quality_audit.jsonl',
              'B_source_checked_provisional.jsonl']
    manifest_path = HERE / 'pilot_B_freeze.json'
    current = {name: sha(HERE / name) for name in frozen}
    if manifest_path.exists():
        if json.loads(manifest_path.read_text())['sha256'] != current:
            raise RuntimeError('B pilot inputs changed after reader start; use a new output directory')
    else:
        manifest_path.write_text(json.dumps({'status': 'development_B_frozen_before_bare_reader',
                                             'source_validation': 'model_checked_provisional_not_human_gold',
                                             'sha256': current}, indent=2) + '\n')
    accepted = rows(HERE / 'B_source_checked_provisional.jsonl')
    outputs = HERE / 'bare_reader.jsonl'
    completed = {(x['id'], x['role']) for x in rows(outputs)} if outputs.exists() else set()
    for item in accepted:
        options = [{'label': 'ABCD'[i], 'term': x['term']} for i, x in enumerate(item['options'])]
        prompt = {'scenario': item['scenario'], 'question': item['question'],
                  'options': options, 'abstain_allowed': True}
        for role in ('reader', 'second_judge'):
            if (item['id'], role) in completed:
                continue
            print('Bare reader', item['id'], role, flush=True)
            response = call(config, role, READER_SYSTEM, prompt, 600)
            choice = response['result'].get('choice')
            if choice not in {'A', 'B', 'C', 'D', 'ABSTAIN'}:
                raise ValueError(f'Unparsed reader choice for {item["id"]} {role}')
            append(outputs, {'id': item['id'], 'role': role, **response})
    records = rows(outputs)
    report = {'status': 'development_only_not_formal', 'n_source_checked_provisional': len(accepted),
              'roles': {}, 'item_results': []}
    for role in ('reader', 'second_judge'):
        trials = []
        for item in accepted:
            record = next(x for x in records if x['id'] == item['id'] and x['role'] == role)
            gold = 'ABCD'[next(i for i, option in enumerate(item['options'])
                               if option['id'] == item['answer_id'])]
            choice = record['result']['choice']
            trials.append({'id': item['id'], 'gold': gold, 'choice': choice,
                           'correct': choice == gold, 'abstain': choice == 'ABSTAIN'})
        report['roles'][role] = {'n': len(trials), 'correct': sum(x['correct'] for x in trials),
                                 'abstain': sum(x['abstain'] for x in trials),
                                 'substantive_wrong': sum(not x['correct'] and not x['abstain'] for x in trials)}
        report['item_results'].extend({'role': role, **x} for x in trials)
    (HERE / 'bare_reader_analysis.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Bare-reader development check', report['roles'], flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, default=PARENT / 'local_meaning_v4_config' / 'config.json')
    p.add_argument('--stage', choices=['draft-b', 'check-b', 'bare-reader', 'all'], default='all')
    args = p.parse_args()
    cards = source_cards()
    card_path = HERE / 'source_cards.jsonl'
    if card_path.exists():
        if rows(card_path) != cards:
            raise RuntimeError('Source cards changed; use a new pilot directory')
    else:
        save_rows(card_path, cards)
    if args.stage in {'draft-b', 'all'}:
        candidates = draft_b(args.config, cards)
    elif args.stage == 'check-b':
        candidates = rows(HERE / 'B_candidates_private.jsonl')
    else:
        candidates = []
    if args.stage in {'check-b', 'all'}:
        check_b(args.config, cards, candidates)
    if args.stage in {'bare-reader', 'all'}:
        bare_reader(args.config)


if __name__ == '__main__':
    main()
