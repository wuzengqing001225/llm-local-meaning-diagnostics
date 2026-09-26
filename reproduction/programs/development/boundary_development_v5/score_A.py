#!/usr/bin/env python3
"""Score V5 development diagnostics with a locally cached small proxy.

The output is exploratory until source rules and every item are accepted.
No API key, reader outcome, or B task is loaded.
"""

import argparse
import hashlib
import json
import os
import time
from pathlib import Path


MODEL = 'Qwen/Qwen2.5-7B'
REVISION = 'd149729398750b98c0af14eb82c78cfe92750796'


def stable_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(stable_json(value).encode()).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def source_rule_quote(card):
    if isinstance(card.get('rule_quote'), str):
        return card['rule_quote']
    proposal = card.get('proposal') or {}
    if isinstance(proposal.get('full_rule_quote'), str):
        return proposal['full_rule_quote']
    raise ValueError('Missing source rule quote')


def prompt(item, definition=None):
    note = '' if definition is None else (
        f'Local definition for this contract only:\n{item["term"]}: {definition}\n\n'
    )
    opts = '\n'.join(f'{letter}. {option}' for letter, option in zip('AB', item['options']))
    return ('You answer a multiple-choice question about a contract. '
            'Answer with one option letter only.\n\n'
            + note + item['question'] + '\n' + opts + '\nAnswer:')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--items', type=Path, required=True)
    p.add_argument('--cards', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--model', default=MODEL)
    p.add_argument('--revision', default=REVISION)
    p.add_argument('--device', choices=['auto', 'cpu', 'mps'], default='auto')
    p.add_argument('--limit', type=int, default=None, help='Development smoke limit; omit for all items.')
    a = p.parse_args()
    items = read_jsonl(a.items)
    cards = {x['definition_id']: x for x in read_jsonl(a.cards)}
    assert items and all(x['study_split'] == 'A' for x in items)
    assert all(x['definition_id'] in cards for x in items)
    if a.limit is not None:
        assert a.limit > 0
        items = items[:a.limit]

    os.environ.setdefault('HF_HUB_OFFLINE', '1')
    os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    device = ('mps' if torch.backends.mps.is_available() else 'cpu') if a.device == 'auto' else a.device
    if device == 'mps' and not torch.backends.mps.is_available():
        raise RuntimeError('MPS is unavailable in this process; rerun with --device cpu or a GPU-enabled environment.')
    dtype = torch.float16 if device == 'mps' else torch.float32
    tok = AutoTokenizer.from_pretrained(a.model, revision=a.revision, local_files_only=True, trust_remote_code=False)
    label_ids = [tok.encode(' A', add_special_tokens=False), tok.encode(' B', add_special_tokens=False)]
    if any(len(x) != 1 for x in label_ids) or label_ids[0] == label_ids[1]:
        raise RuntimeError('This scorer needs distinct single-token spaced A/B labels; inspect tokenizer first.')
    print(f'Loading {a.model} at {a.revision} on {device}, {dtype}; {len(items)} items planned.', flush=True)
    start = time.monotonic()
    net = AutoModelForCausalLM.from_pretrained(
        a.model, revision=a.revision, dtype=dtype, local_files_only=True,
        trust_remote_code=False,
    ).to(device).eval()
    print(f'Model loaded in {time.monotonic()-start:.1f}s.', flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    existing = {x['id']: x for x in read_jsonl(a.out)} if a.out.exists() else {}
    def score(text):
        encoded = tok(text, return_tensors='pt', add_special_tokens=True)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        with torch.inference_mode():
            logits = net(**encoded).logits[0, -1, [label_ids[0][0], label_ids[1][0]]].float()
            probs = torch.softmax(logits, dim=0).cpu().tolist()
        return probs
    for i, item in enumerate(items, 1):
        card = cards[item['definition_id']]
        rule_quote = source_rule_quote(card)
        token = digest({'item': item, 'rule_quote': rule_quote, 'prompt_version': 1})
        if item['id'] in existing:
            row = existing[item['id']]
            if row['input_digest'] != token or row['proxy_revision'] != a.revision or row['proxy_model'] != a.model:
                raise RuntimeError(f'Stale prior score for {item["id"]}; use a fresh output path.')
            continue
        before = time.monotonic()
        bare_prompt = prompt(item)
        def_prompt = prompt(item, rule_quote)
        pb = score(bare_prompt)
        pd = score(def_prompt)
        answer_idx = 'AB'.index(item['answer'])
        row = {
            'id': item['id'], 'definition_id': item['definition_id'],
            'contract_index': item.get('contract_index'), 'cohort': item.get('cohort'),
            'input_digest': token, 'proxy_model': a.model,
            'proxy_revision': a.revision, 'device': device, 'dtype': str(dtype),
            'backend': 'local_single_token_label_softmax', 'label_token_ids': label_ids,
            'scorer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'prompt_version': 1,
            'p_bare': pb[answer_idx], 'p_definition': pd[answer_idx],
            'R': 1 - pb[answer_idx], 'dp': pd[answer_idx] - pb[answer_idx],
            'probabilities_bare': pb, 'probabilities_definition': pd,
            'bare_prompt_sha256': hashlib.sha256(bare_prompt.encode()).hexdigest(),
            'definition_prompt_sha256': hashlib.sha256(def_prompt.encode()).hexdigest(),
            'score_seconds': time.monotonic() - before,
            'status': ('source_reviewed_A_scored' if item.get('status') == 'source_reviewed_A_not_scored'
                       else 'development_only_unreviewed_items'),
        }
        with a.out.open('a') as f:
            f.write(stable_json(row) + '\n')
            f.flush()
        print(f'Scored {i}/{len(items)} {item["id"]}: R={row["R"]:.3f}, dp={row["dp"]:.3f}, seconds={row["score_seconds"]:.1f}', flush=True)


if __name__ == '__main__':
    main()
