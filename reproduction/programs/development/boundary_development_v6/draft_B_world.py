#!/usr/bin/env python3
"""Independent B wording from concrete facts only: no rule, gold, A or scores."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'local_meaning_v5_development'))
from draft_source_rules import parse_json_object
from run_reader_dev import canonical, config_role, request_one


SYSTEM = (
    'You are a different author of independent research requests. Write a realistic, concise question '
    'asking whether a concrete situation falls within a contract term. You receive ONLY the term name '
    'and observable situation. You do not receive the local definition, a gold answer, any diagnostic A '
    'question or score, or target reader outcome. Preserve every stated fact and named entity; do not '
    'invent a fact, assume a hidden clause, explain the term, or tell the reader which answer is correct. '
    'Use natural request wording, not a checklist of conditions. Return JSON only: {"question":"..."}.'
)


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--public-seeds', type=Path, required=True)
    p.add_argument('--public-terms', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--limit', type=int, default=None)
    p.add_argument('--workers', type=int, default=4)
    a = p.parse_args()
    if not 1 <= a.workers <= 4:
        raise ValueError('--workers must be 1-4')
    spec = config_role(a.config, 'draft')
    terms = {x['definition_id']: x['term'] for x in read(a.public_terms)}
    seeds = [x for x in read(a.public_seeds) if x['case_type'] == 'membership']
    if a.limit is not None:
        if a.limit <= 0:
            raise ValueError('--limit must be positive')
        seeds = seeds[:a.limit]
    done = {x['id']: x for x in read(a.out)} if a.out.exists() else {}
    jobs = []
    for seed in seeds:
        did = seed['definition_id']
        user = canonical({'term': terms[did], 'observable_situation': seed['world_fact']})
        input_hash = hashlib.sha256((SYSTEM + user + spec['model']).encode()).hexdigest()
        if seed['id'] in done:
            if done[seed['id']]['input_sha256'] != input_hash:
                raise RuntimeError('Stale B draft; use a new output file')
            continue
        payload = {'model': spec['model'],
                   'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}],
                   'temperature': 0, 'max_tokens': 1024,
                   'thinking': {'type': 'disabled'}, 'response_format': {'type': 'json_object'}}
        jobs.append((seed, input_hash, payload))

    def execute(job):
        seed, input_hash, payload = job
        start = time.monotonic()
        response = request_one(spec, payload)
        parsed = parse_json_object(response['content'])
        question = parsed.get('question') if isinstance(parsed, dict) else None
        valid = isinstance(question, str) and 40 <= len(question) <= 650 and terms[seed['definition_id']].lower() in question.lower()
        return {'id': seed['id'], 'definition_id': seed['definition_id'],
                'world_seed_sha256': hashlib.sha256(seed['world_fact'].encode()).hexdigest(),
                'input_sha256': input_hash, 'question': question,
                'draft_structure_valid': valid, 'requested_model': spec['model'],
                'returned_model': response['returned_model'],
                'provider_response_id': response['provider_response_id'],
                'usage': response['usage'], 'elapsed_seconds': time.monotonic()-start,
                'status': 'new_B_wording_no_rule_or_key_seen'}

    a.out.parent.mkdir(parents=True, exist_ok=True)
    failed = []
    with ThreadPoolExecutor(max_workers=a.workers) as pool, a.out.open('a') as file:
        futures = {pool.submit(execute, job): job[0]['id'] for job in jobs}
        for future in as_completed(futures):
            did = futures[future]
            try:
                row = future.result()
            except Exception as exc:
                failed.append(did)
                print('FAILED',did,type(exc).__name__,'rerun to retry',flush=True)
                continue
            file.write(canonical(row)+'\n');file.flush()
            print(did,'valid',row['draft_structure_valid'],flush=True)
    if failed:
        raise RuntimeError(f'{len(failed)} B drafts failed; completed rows saved')


if __name__=='__main__':
    main()
