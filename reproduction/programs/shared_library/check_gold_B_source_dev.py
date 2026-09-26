#!/usr/bin/env python3
"""Outcome-blind model review of historical gold-gloss B questions.

The checker never sees the historical answer key, reader results, A scores,
or which policy selected a term. Acceptance criteria are fixed in this file.
"""
import argparse
import hashlib
import json
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from api_client import config_role, parse_json_object, request_one
from shared_budget_plan import file_hash

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'gold_aligned_development'
PACKET = OUT / 'B_disagreement_packet.jsonl'
SYSTEM = """Review historical multiple-choice items from a community-specific glossary. For every item, read only the term, exact community definition, question and options. Proposed keys and model outcomes are hidden. Decide whether the definition and the question facts support exactly one option without inventing missing local rules. Mark a question invalid if several options remain plausible, if the question directly paraphrases the correct option, or if the definition does not determine the action/fact asked. Return JSON only: {"items":[{"id":"...","answer":"A|B|C|D|UNDETERMINED","valid":true or false,"definition_sufficient":true or false,"no_answer_leakage":true or false,"reason":"..."},...]}."""


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def source_jobs():
    by_term = defaultdict(list)
    for item in (json.loads(line) for line in PACKET.open()):
        by_term[item['term_id']].append(item)
    jobs = []
    for term_id, items in sorted(by_term.items()):
        first = items[0]
        request = {'term_id': term_id, 'term': first['term'], 'definition': first['definition'],
                   'items': [{'id': x['id'], 'question': x['question'], 'options': x['options']} for x in items]}
        jobs.append((term_id, request))
    return jobs


def one(spec, job):
    term_id, request = job
    payload = {'model': spec['model'], 'messages': [{'role': 'system', 'content': SYSTEM},
                                                   {'role': 'user', 'content': canonical(request)}],
               'temperature': 0, 'max_tokens': 1800,
               'response_format': {'type': 'json_object'}, 'thinking': {'type': 'disabled'}}
    started = time.monotonic()
    result = request_one(spec, payload)
    parsed = parse_json_object(result['content'])
    if not isinstance(parsed, dict) or not isinstance(parsed.get('items'), list):
        raise ValueError('Invalid source-check JSON')
    expected = {x['id'] for x in request['items']}
    received = {x.get('id') for x in parsed['items']}
    if expected != received:
        raise ValueError('Source checker omitted or duplicated question IDs')
    return {'term_id': term_id, 'input_sha256': hashlib.sha256(canonical(payload).encode()).hexdigest(),
            'requested_model': spec['model'], 'returned_model': result['returned_model'],
            'provider_response_id': result['provider_response_id'], 'usage': result['usage'],
            'finish_reason': result['finish_reason'], 'seconds': time.monotonic() - started,
            'result': parsed, 'raw_content': result['content']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=ROOT.parent / 'local_meaning_v4_config/config.json')
    args = parser.parse_args()
    spec = config_role(args.config.resolve(), 'second_judge')
    if 'deepseek' not in spec['model'].lower():
        raise ValueError('Expected independent DeepSeek source checker')
    freeze = {'packet_sha256': file_hash(PACKET), 'system_sha256': hashlib.sha256(SYSTEM.encode()).hexdigest(),
              'model': spec['model'], 'script_sha256': file_hash(Path(__file__)),
              'status': 'OUTCOME_BLIND_DEVELOPMENT_SOURCE_CHECK'}
    freeze_path = OUT / 'source_check_freeze.json'
    if freeze_path.exists():
        if json.loads(freeze_path.read_text()) != freeze:
            raise RuntimeError('Source-check input changed after calls began')
    else:
        freeze_path.write_text(json.dumps(freeze, indent=2) + '\n')
    output = OUT / 'source_checks.jsonl'
    done = {x['term_id']: x for x in (json.loads(line) for line in output.open())} if output.exists() else {}
    jobs = [x for x in source_jobs() if x[0] not in done]
    print('Pending outcome-blind source checks', len(jobs), flush=True)
    errors = []
    with ThreadPoolExecutor(max_workers=4) as pool, output.open('a') as file:
        futures = {pool.submit(one, spec, x): x[0] for x in jobs}
        for n, future in enumerate(as_completed(futures), 1):
            try:
                row = future.result()
            except Exception as exc:
                errors.append((futures[future], type(exc).__name__, str(exc)[:140]))
                continue
            file.write(canonical(row) + '\n')
            file.flush()
            if n % 10 == 0 or n == len(jobs):
                print('Checked', n, '/', len(jobs), flush=True)
    if errors:
        print('Failures', errors[:5], flush=True)
        raise RuntimeError(f'{len(errors)} incomplete checks; rerun to resume')
    packet = {x['id']: x for x in (json.loads(line) for line in PACKET.open())}
    decisions = []
    for result in (json.loads(line) for line in output.open()):
        for verdict in result['result']['items']:
            item = packet[verdict['id']]
            accepted = all(verdict.get(k) is True for k in
                           ('valid', 'definition_sufficient', 'no_answer_leakage'))
            accepted = accepted and verdict.get('answer') == item['gold_option']
            decisions.append({'id': item['id'], 'accepted_by_outcome_blind_model': accepted,
                              'checker_answer': verdict.get('answer'),
                              'historical_key': item['gold_option'], 'verdict': verdict})
    decisions.sort(key=lambda x: x['id'])
    (OUT / 'source_decisions.jsonl').write_text(''.join(canonical(x) + '\n' for x in decisions))
    print('Accepted', sum(x['accepted_by_outcome_blind_model'] for x in decisions), '/', len(decisions), flush=True)


if __name__ == '__main__':
    main()
