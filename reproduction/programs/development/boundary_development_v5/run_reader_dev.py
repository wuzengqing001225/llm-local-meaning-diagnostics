#!/usr/bin/env python3
"""Run the V5 *development* B cases against two configured reader families.

This is a small diagnostic of task quality, not the confirmatory study.
Keys are read from config.json in memory and never written to output.
"""

import argparse
import hashlib
import json
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def config_role(config, role):
    raw = json.loads(config.read_text())
    roles = raw.get('roles') or {}
    fallback = {'judge': 'reader', 'second_judge': 'draft',
                'test_draft': 'draft', 'mechanism_judge': 'judge'}
    spec = dict(raw.get('defaults') or {})
    if role in fallback:
        spec.update(config_role(config, fallback[role]))
    spec.update(roles[role])
    for key in ('model', 'base_url', 'api_key'):
        if not isinstance(spec.get(key), str) or not spec[key].strip() or spec[key] in {'[key]', 'YOUR_API_KEY', 'PASTE_API_KEY_HERE'}:
            raise ValueError(f'Role {role} needs a real {key} in config.json')
    return spec


def prompt(item, rule=None):
    opts = '\n'.join(f'{c}. {x}' for c, x in zip('AB', item['options']))
    note = '' if rule is None else (
        f'Local definition for this contract only:\n{item["term"]}: {rule}\n\n'
    )
    return note + item['question'] + '\n' + opts + '\nAnswer with A or B only.'


def parse_answer(content):
    value = content.strip()
    try:
        obj = json.loads(value)
        if isinstance(obj, dict) and isinstance(obj.get('answer'), str):
            value = obj['answer'].strip()
    except ValueError:
        pass
    if value in {'A', 'B'}:
        return value
    match = re.fullmatch(r'(?:Answer\s*:\s*)?([AB])[.\s]*', value, re.I)
    return match.group(1).upper() if match else None


def request_one(spec, payload):
    url = spec['base_url'].rstrip('/') + '/chat/completions'
    request = urllib.request.Request(
        url, data=canonical(payload).encode(), method='POST',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + spec['api_key']},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = json.loads(response.read())
            choice = raw['choices'][0]
            content = choice['message'].get('content')
            finish = choice.get('finish_reason')
            if not isinstance(content, str) or not content.strip() or finish == 'length':
                raise RuntimeError(f'Empty/truncated response, finish_reason={finish}; rerun to resume')
            return {
                'content': content, 'prediction': parse_answer(content),
                'returned_model': raw.get('model'), 'provider_response_id': raw.get('id'),
                'usage': raw.get('usage'), 'finish_reason': finish,
            }
        except urllib.error.HTTPError as e:
            if e.code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'HTTP {e.code} for configured model {spec["model"]}; no key or response body logged') from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'Connection failed for configured model {spec["model"]}; no key logged') from None
    raise RuntimeError('Request failed after retries')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--tasks', type=Path, required=True)
    p.add_argument('--cards', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--limit', type=int, default=None, help='First N B tasks for a smoke run; omit for all.')
    p.add_argument('--study', choices=['development', 'formal'], default='development')
    p.add_argument('--approval-manifest', type=Path, help='Required for formal reader runs')
    a = p.parse_args()
    specs = {'gpt_reader': config_role(a.config, 'reader'),
             'deepseek_reader': config_role(a.config, 'draft')}
    if a.study == 'formal':
        # Predeclared second reader setting; thought-mode robustness is separate.
        specs['deepseek_reader']['extra_body'] = {'thinking': {'type': 'disabled'}, 'max_tokens': 64}
    if specs['gpt_reader']['model'] == specs['deepseek_reader']['model']:
        raise ValueError('Two reader roles must use distinct model families')
    tasks = read_jsonl(a.tasks)
    expected_status = 'accepted_formal_B' if a.study == 'formal' else 'unreviewed_development_item'
    if any(x.get('status') != expected_status for x in tasks):
        raise ValueError('B tasks have the wrong study status; finish the quality gate before formal reader calls')
    if a.study == 'formal':
        if a.limit is not None or a.approval_manifest is None:
            raise ValueError('Formal reader runs require the full accepted B file and its approval manifest')
        approval = json.loads(a.approval_manifest.read_text())
        if (approval.get('status') != 'B_quality_gate_before_target_reader_outcomes'
                or approval.get('n_accepted_B') != len(tasks)
                or approval.get('approved_public_sha256') != hashlib.sha256(a.tasks.read_bytes()).hexdigest()):
            raise ValueError('Formal B public file does not match the frozen approval manifest')
    if a.limit is not None:
        if a.limit <= 0:
            raise ValueError('--limit must be positive')
        tasks = tasks[:a.limit]
    cards = {x['definition_id']: x for x in read_jsonl(a.cards)}
    existing = {x['request_id']: x for x in read_jsonl(a.out)} if a.out.exists() else {}
    jobs = []
    for role, spec in specs.items():
        for item in tasks:
            if item['definition_id'] not in cards:
                raise ValueError('Missing source card for ' + item['id'])
            for arm in ('bare', 'definition'):
                card = cards[item['definition_id']]
                quote = card.get('rule_quote') or (card.get('proposal') or {}).get('full_rule_quote')
                if arm == 'definition' and not isinstance(quote, str):
                    raise ValueError('Missing source rule quote for ' + item['definition_id'])
                text = prompt(item, quote if arm == 'definition' else None)
                payload = {
                    'model': spec['model'],
                    'messages': [
                        {'role': 'system', 'content': 'You answer multiple-choice research questions about a contract. Choose one option letter.'},
                        {'role': 'user', 'content': text},
                    ],
                    'temperature': 0,
                    'max_tokens': 64,
                }
                payload.update(spec.get('extra_body') or {})
                request_id = sha({'role': role, 'endpoint': spec['base_url'], 'task': item['id'], 'arm': arm, 'payload': payload})
                jobs.append((request_id, role, item, arm, spec, payload))
    random.Random(20260925).shuffle(jobs)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    for i, (request_id, role, item, arm, spec, payload) in enumerate(jobs, 1):
        if request_id in existing:
            continue
        started = time.monotonic()
        response = request_one(spec, payload)
        row = {
            'request_id': request_id, 'task_id': item['id'], 'role': role, 'arm': arm,
            'requested_model': spec['model'], 'endpoint': spec['base_url'],
            'prompt_sha256': hashlib.sha256(payload['messages'][1]['content'].encode()).hexdigest(),
            'elapsed_seconds': time.monotonic() - started,
            'status': 'formal_reader_condition' if a.study == 'formal' else 'development_only',
            **response,
        }
        with a.out.open('a') as f:
            f.write(canonical(row) + '\n')
            f.flush()
        print(f'{i}/{len(jobs)} {role} {arm} {item["id"]}: {row["prediction"] or "unparsed"} ({row["elapsed_seconds"]:.1f}s)', flush=True)
    print(f'Complete: {len(jobs)} planned reader-arm requests; data in {a.out}')


if __name__ == '__main__':
    main()
