#!/usr/bin/env python3
"""Run a frozen shared-definition plan on independently authored B tasks.

Requires the same role-based private config.json used by previous experiments.
The API key is read in memory and never stored. Tasks/plan/source validation
are checked before the first model call.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

from shared_budget_plan import closure, file_hash, read_rows

ROOT = Path(__file__).resolve().parent
from api_client import config_role, parse_json_object, request_one

BASE = 'frequency_per_cost'
METHOD = 'frequency_delta_p_per_cost'
SYSTEM = """Answer the following independently written question using the supplied common context and any local definitions. If the available information does not support one option, answer ABSTAIN. Do not invent a missing local definition. Return JSON only: {"answer":"A|B|C|D|ABSTAIN","reason":"brief explanation"}."""


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def timestamp(value):
    from datetime import datetime
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def expected_definitions(matched, policy, catalog):
    selected = set(policy['root_definition_ids'])
    ids = set()
    for term_id in matched:
        if term_id in selected:
            ids |= closure(term_id, catalog)
    return sorted(ids)


def validate_tasks(tasks, plan, catalog):
    if plan['status'] != 'FROZEN_BEFORE_B':
        raise ValueError('Formal B calls require a formal plan frozen before B')
    ids = set()
    for task in tasks:
        qid = task['request_id']
        if qid in ids:
            raise ValueError('Duplicate B request ID')
        ids.add(qid)
        if timestamp(task['created_utc']) < timestamp(plan['b_start_utc']):
            raise ValueError('B request predates frozen B boundary')
        if task.get('quality_status') != 'source_checked' or task.get('gold_source_checked') is not True:
            raise ValueError('B request was not source checked: ' + qid)
        if task.get('definition_leakage_checked') is not True:
            raise ValueError('B question leakage not reviewed: ' + qid)
        if not task.get('source_evidence_ref') or not task.get('independent_author'):
            raise ValueError('Missing B question provenance: ' + qid)
        options = task['options']
        if not isinstance(options, list) or len(options) not in {2, 3, 4} or not all(isinstance(x, str) and x for x in options):
            raise ValueError('B must have two to four nonempty options: ' + qid)
        gold = task.get('gold_option')
        if not isinstance(gold, str) or gold not in 'ABCD'[:len(options)]:
            raise ValueError('B has no unique gold option: ' + qid)
        matched = task['matched_definition_ids']
        if len(set(matched)) != len(matched):
            raise ValueError('Duplicate matched definition ID')
        for term_id in matched:
            if term_id not in catalog or catalog[term_id]['scope'] != task['scope']:
                raise ValueError('Missing or cross-scope matched definition: ' + qid)
        if float(task['sampling_weight']) <= 0 or not task.get('cluster'):
            raise ValueError('Missing sampling weight or cluster: ' + qid)
    if not tasks:
        raise ValueError('Empty B task file')


def make_prompt(task, ids, catalog):
    definitions = [{'term': catalog[i]['term'], 'definition': catalog[i]['definition']} for i in ids]
    public_question = {'common_context': task.get('common_context', ''), 'post_context': task.get('post_context', ''),
                       'question': task['question'], 'options': {letter: option for letter, option in zip('ABCD', task['options'])},
                       'local_definitions': definitions, 'abstain_allowed': True}
    return public_question


def call(spec, task, prompt):
    payload = {'model': spec['model'], 'messages': [{'role': 'system', 'content': SYSTEM},
                                                   {'role': 'user', 'content': canonical(prompt)}],
               'temperature': 0, 'max_tokens': 700,
               'reasoning_effort': 'none', 'response_format': {'type': 'json_object'}}
    start = time.monotonic()
    output = request_one(spec, payload)
    result = parse_json_object(output['content'])
    if not isinstance(result, dict) or result.get('answer') not in set('ABCD'[:len(task['options'])]) | {'ABSTAIN'}:
        raise ValueError('Unparsed B answer; no silent scoring')
    return {'answer': result['answer'], 'reason': result.get('reason'),
            'raw_content': output['content'], 'provider_response_id': output['provider_response_id'],
            'requested_model': spec['model'], 'returned_model': output['returned_model'],
            'usage': output['usage'], 'finish_reason': output['finish_reason'],
            'seconds': time.monotonic() - start,
            'prompt_sha256': sha_text(canonical(payload))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--tasks', type=Path, required=True)
    parser.add_argument('--config', type=Path, default=ROOT / 'config.json')
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    plan_path, catalog_path, task_path = [x.resolve() for x in (args.plan, args.catalog, args.tasks)]
    plan = json.loads(plan_path.read_text())
    if file_hash(catalog_path) != plan['input_sha256']['catalog']:
        raise ValueError('Catalog differs from frozen selection')
    catalog_rows = read_rows(catalog_path)
    catalog = {x['id']: x for x in catalog_rows}
    tasks = read_rows(task_path)
    validate_tasks(tasks, plan, catalog)
    spec = config_role(args.config.resolve(), 'reader')
    if spec['model'] != 'gpt-5.6-terra':
        raise ValueError('Primary reader model differs from frozen protocol')
    if any(task['independent_author'] == spec['model'] for task in tasks):
        raise ValueError('B question author must differ from the primary reader')
    settings = {'model': spec['model'], 'temperature': 0, 'max_tokens': 700,
                'reasoning_effort': 'none', 'system_sha256': sha_text(SYSTEM)}
    settings_hash = sha_text(canonical(settings))
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    freeze_path = out / 'B_run_freeze.json'
    freeze = {'plan_sha256': file_hash(plan_path), 'catalog_sha256': file_hash(catalog_path),
              'tasks_sha256': file_hash(task_path), 'settings_sha256': settings_hash,
              'runner_sha256': file_hash(Path(__file__)),
              'status': 'FROZEN_BEFORE_READER'}
    if freeze_path.exists():
        if json.loads(freeze_path.read_text()) != freeze:
            raise RuntimeError('Inputs/settings changed after first B call; use a new output directory')
    else:
        freeze_path.write_text(json.dumps(freeze, indent=2) + '\n')
    raw_path = out / 'B_raw_responses.jsonl'
    done = {(x['request_id'], x['policy']): x for x in read_rows(raw_path)} if raw_path.exists() else {}
    policies = (BASE, METHOD)
    for task in tasks:
        # Stable balanced ordering prevents one policy always occupying the first API slot.
        order = policies if int(sha_text(task['request_id']), 16) % 2 == 0 else policies[::-1]
        for policy_name in order:
            ids = expected_definitions(task['matched_definition_ids'], plan['policies'][policy_name], catalog)
            prompt = make_prompt(task, ids, catalog)
            if (task['request_id'], policy_name) in done:
                if done[(task['request_id'], policy_name)]['injected_definition_ids'] != ids:
                    raise RuntimeError('Resumed response uses different definitions')
                continue
            identical = next((done[(task['request_id'], other)] for other in policies
                              if (task['request_id'], other) in done
                              and done[(task['request_id'], other)]['injected_definition_ids'] == ids), None)
            if identical is not None:
                response = {k: v for k, v in identical.items() if k not in {'request_id', 'policy', 'injected_definition_ids'}}
                response['api_call_made'] = False
                response['reused_response_from_policy'] = identical['policy']
            else:
                print('B', task['request_id'], policy_name, flush=True)
                response = call(spec, task, prompt)
                response['api_call_made'] = True
            row = {'request_id': task['request_id'], 'policy': policy_name,
                   'injected_definition_ids': ids, **response}
            with raw_path.open('a') as f:
                f.write(canonical(row) + '\n')
            done[(task['request_id'], policy_name)] = row
    trials = []
    for task in tasks:
        question_hash = sha_text(canonical({k: task.get(k) for k in ('common_context', 'post_context', 'question', 'options')}))
        for policy_name in policies:
            response = done[(task['request_id'], policy_name)]
            answer = response['answer']
            trials.append({'request_id': task['request_id'], 'policy': policy_name,
                           'scope': task['scope'], 'cluster': task['cluster'],
                           'created_utc': task['created_utc'], 'matched_definition_ids': task['matched_definition_ids'],
                           'injected_definition_ids': response['injected_definition_ids'],
                           'sampling_weight': task['sampling_weight'], 'gold_source_checked': task['gold_source_checked'],
                           'judgment': 'abstain' if answer == 'ABSTAIN' else ('correct' if answer == task['gold_option'] else 'wrong'),
                           'reader_model': spec['model'], 'question_sha256': question_hash,
                           'prompt_sha256': response['prompt_sha256'], 'settings_sha256': settings_hash,
                           'provider_response_id': response['provider_response_id'],
                           'returned_model': response['returned_model'], 'usage': response['usage'],
                           'api_call_made': response.get('api_call_made', True)})
    (out / 'B_trials.jsonl').write_text(''.join(canonical(x) + '\n' for x in trials))
    print(json.dumps({'status': 'B_READER_COMPLETE', 'n_tasks': len(tasks), 'n_arms': len(trials),
                      'actual_api_calls': sum(x.get('api_call_made', True) for x in done.values()),
                      'trials': str(out / 'B_trials.jsonl')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
