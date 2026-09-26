#!/usr/bin/env python3
"""Historical B gold-gloss sensitivity using the configured GPT-5.6 reader.

Only terms where frozen frequency and F×gold-Δp libraries disagree are called.
This is a development comparison on old drafted questions, not independent B.
"""
import argparse
import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from api_client import config_role, request_one
from shared_budget_plan import file_hash

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'gold_aligned_development'
EQA = ROOT.parent / 'release_20260923/llm-idf-reproduce/data/reddit/raw_outputs/reddit_v2_eqa.jsonl'
PLAN = OUT / 'gold_plan_development_only.json'
SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only."


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def parse_letter(content):
    text = (content or '').strip().upper()
    match = re.search(r'ANSWER_LETTER\s*[:：]?\s*\(?([A-D])\b', text)
    if not match:
        match = re.match(r'\s*\(?([A-D])\)?(?:[\s.:,)]|$)', text)
    return match.group(1) if match else None


def prepare():
    plan = json.loads(PLAN.read_text())
    base = set(plan['policies']['frequency_per_cost']['root_definition_ids'])
    method = set(plan['policies']['frequency_delta_p_per_cost']['root_definition_ids'])
    disagreement = base ^ method
    catalog = {x['id']: x for x in (json.loads(line) for line in (OUT / 'gold_catalog.jsonl').open())}
    packet = []
    for row in (json.loads(line) for line in EQA.open()):
        if row['id'] not in disagreement:
            continue
        term_id = row['id']
        entry = catalog[term_id]
        for j in range(1, len(row['questions']), 2):
            item = row['questions'][j]
            packet.append({'id': f'{term_id}:B{j}', 'term_id': term_id, 'scope': entry['scope'],
                           'term': entry['term'], 'definition': entry['definition'],
                           'definition_sha256': entry['definition_sha256'],
                           'question': item['q'], 'options': item['options'], 'gold_option': item['answer'],
                           'selected_by_frequency': term_id in base,
                           'selected_by_frequency_delta_p': term_id in method,
                           'status': 'historical_drafted_sibling_question_not_formal_B'})
    packet.sort(key=lambda x: x['id'])
    path = OUT / 'B_disagreement_packet.jsonl'
    content = ''.join(canonical(row) + '\n' for row in packet)
    if path.exists() and path.read_text() != content:
        raise RuntimeError('B packet changed after preparation; use a new version')
    path.write_text(content)
    manifest = {'status': 'DEVELOPMENT_ONLY', 'n_disagreement_terms': len(disagreement),
                'n_B_questions': len(packet), 'plan_sha256': file_hash(PLAN),
                'packet_sha256': file_hash(path), 'eqa_source_sha256': file_hash(EQA),
                'reader_outcomes_in_packet': False}
    manifest_path = OUT / 'B_disagreement_manifest.json'
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != manifest:
        raise RuntimeError('B manifest changed')
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print('Prepared', len(packet), 'old B questions on', len(disagreement), 'policy-disagreement terms')


def prompt(item, condition):
    options = '\n'.join(f'{chr(65+i)}. {x}' for i, x in enumerate(item['options']))
    prefix = f'Term note: {item["term"]}: {item["definition"]}\n\n' if condition == 'gold' else ''
    return prefix + item['question'] + '\n' + options + '\nANSWER_LETTER:'


def one(spec, item, condition):
    user = prompt(item, condition)
    payload = {'model': spec['model'], 'messages': [{'role': 'system', 'content': SYSTEM},
                                                   {'role': 'user', 'content': user}],
               'temperature': 0, 'max_tokens': 16, 'reasoning_effort': 'none'}
    digest = hashlib.sha256(canonical(payload).encode()).hexdigest()
    start = time.monotonic()
    response = request_one(spec, payload)
    answer = parse_letter(response['content'])
    if answer is None:
        raise ValueError('Reader response did not contain one unambiguous option letter')
    return {'id': item['id'], 'condition': condition, 'answer': answer,
            'prompt_sha256': digest, 'raw_content': response['content'],
            'requested_model': spec['model'], 'returned_model': response['returned_model'],
            'provider_response_id': response['provider_response_id'], 'usage': response['usage'],
            'finish_reason': response['finish_reason'], 'seconds': time.monotonic() - start}


def run(config, limit):
    packet_path = OUT / 'B_disagreement_packet.jsonl'
    manifest = json.loads((OUT / 'B_disagreement_manifest.json').read_text())
    if file_hash(packet_path) != manifest['packet_sha256'] or file_hash(PLAN) != manifest['plan_sha256']:
        raise RuntimeError('Frozen B packet or selection plan changed')
    items = [json.loads(line) for line in packet_path.open()]
    spec = config_role(config.resolve(), 'reader')
    if spec['model'] != 'gpt-5.6-terra':
        raise ValueError('Unexpected configured reader model')
    settings = {'model': spec['model'], 'system': SYSTEM, 'temperature': 0,
                'max_tokens': 16, 'reasoning_effort': 'none', 'runner_sha256': file_hash(Path(__file__))}
    freeze = {'packet_sha256': manifest['packet_sha256'], 'plan_sha256': manifest['plan_sha256'],
              'settings_sha256': hashlib.sha256(canonical(settings).encode()).hexdigest(),
              'status': 'DEVELOPMENT_READER_FROZEN'}
    freeze_path = OUT / 'configured_reader_freeze.json'
    if freeze_path.exists():
        if json.loads(freeze_path.read_text()) != freeze:
            raise RuntimeError('Reader settings changed after calls began')
    else:
        freeze_path.write_text(json.dumps(freeze, indent=2) + '\n')
    output_path = OUT / 'gpt56_B_gold_bare.jsonl'
    completed = {(x['id'], x['condition']): x for x in (json.loads(line) for line in output_path.open())} if output_path.exists() else {}
    pending_questions = [item for item in items if any((item['id'], c) not in completed for c in ('bare', 'gold'))]
    if limit:
        pending_questions = pending_questions[:limit]
    jobs = [(item, condition) for item in pending_questions for condition in ('bare', 'gold')
            if (item['id'], condition) not in completed]
    if not jobs:
        print('No pending configured-reader calls')
        return
    print('Submitting', len(jobs), 'development reader calls for', len(pending_questions), 'questions', flush=True)
    errors = []
    with ThreadPoolExecutor(max_workers=4) as pool, output_path.open('a') as output:
        futures = {pool.submit(one, spec, item, condition): (item['id'], condition) for item, condition in jobs}
        for n, future in enumerate(as_completed(futures), 1):
            try:
                row = future.result()
            except Exception as exc:
                errors.append((futures[future], type(exc).__name__, str(exc)[:140]))
                continue
            output.write(canonical(row) + '\n')
            output.flush()
            if n % 20 == 0 or n == len(jobs):
                print('completed', n, '/', len(jobs), flush=True)
    if errors:
        print('Failures', errors[:5], flush=True)
        raise RuntimeError(f'{len(errors)} calls incomplete; rerun the same command to resume')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--config', type=Path, default=ROOT.parent / 'local_meaning_v4_config/config.json')
    parser.add_argument('--limit-questions', type=int, default=0)
    args = parser.parse_args()
    if not args.prepare and not args.run:
        args.prepare = args.run = True
    if args.prepare:
        prepare()
    if args.run:
        run(args.config, args.limit_questions)


if __name__ == '__main__':
    main()
