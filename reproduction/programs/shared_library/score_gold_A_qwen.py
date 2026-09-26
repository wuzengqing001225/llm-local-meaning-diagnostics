#!/usr/bin/env python3
"""Score A's correct-option probability with the exact gold definition.

This uses the pinned local Qwen2.5-7B cache and the original prompt format.
It reads only A_gold_packet.jsonl, never B questions or reader outcomes.
"""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

ROOT = Path(__file__).resolve().parent
MODEL = 'Qwen/Qwen2.5-7B'
REVISION = 'd149729398750b98c0af14eb82c78cfe92750796'
SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only.\n\n"


def prompt(item, term, definition):
    head = f'Term note: {term}: {definition}\n\n' if definition else ''
    options = '\n'.join(f'{chr(65+i)}. {x}' for i, x in enumerate(item['options']))
    return SYSTEM + head + item['q'] + '\n' + options + '\nANSWER_LETTER:'


@torch.no_grad()
def p_correct(tokenizer, model, text, gold, n_options, device):
    inputs = tokenizer(text, return_tensors='pt').to(device)
    logits = model(**inputs).logits[0, -1].float()
    lp = torch.log_softmax(logits, -1)
    answer_scores = []
    for i in range(n_options):
        letter = chr(65 + i)
        variants = [tokenizer.encode(' ' + letter, add_special_tokens=False),
                    tokenizer.encode(letter, add_special_tokens=False)]
        answer_scores.append(max(lp[seq[0]].item() for seq in variants if seq))
    z = math.log(sum(math.exp(value) for value in answer_scores))
    return math.exp(answer_scores[ord(gold) - 65] - z)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--packet', type=Path, default=ROOT / 'gold_aligned_development/A_gold_packet.jsonl')
    parser.add_argument('--out', type=Path, default=ROOT / 'gold_aligned_development/qwen_A_gold.jsonl')
    parser.add_argument('--limit', type=int, default=0, help='Only score this many pending terms; rerun to resume')
    args = parser.parse_args()
    packet_hash = hashlib.sha256(args.packet.read_bytes()).hexdigest()
    entries = [json.loads(line) for line in args.packet.open()]
    done = {x['id']: x for x in (json.loads(line) for line in args.out.open())} if args.out.exists() else {}
    if any(x['A_packet_sha256'] != packet_hash for x in done.values()):
        raise ValueError('A packet changed after scoring began')
    pending = [x for x in entries if x['id'] not in done]
    if args.limit:
        pending = pending[:args.limit]
    if not pending:
        print('All requested A terms already scored')
        return
    if not torch.backends.mps.is_available():
        raise RuntimeError('Apple GPU unavailable here; do not silently launch a many-hour CPU run')
    device = 'mps'
    dtype = torch.float16
    print('Loading cached', MODEL, REVISION, 'on', device, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL, revision=REVISION,
                                                torch_dtype=dtype, local_files_only=True,
                                                low_cpu_mem_usage=True).to(device).eval()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('a') as output:
        for n, entry in enumerate(pending, 1):
            started = time.monotonic()
            results = []
            for q in entry['questions_A']:
                if q['answer'] not in 'ABCD'[:len(q['options'])]:
                    raise ValueError('Invalid A answer key')
                bare_prompt = prompt(q, entry['term'], None)
                gold_prompt = prompt(q, entry['term'], entry['definition'])
                bare = p_correct(tokenizer, model, bare_prompt, q['answer'], len(q['options']), device)
                with_gold = p_correct(tokenizer, model, gold_prompt, q['answer'], len(q['options']), device)
                results.append({'question_id': q['id'], 'p_bare': bare, 'p_gold_definition': with_gold,
                                'delta_p': with_gold - bare,
                                'bare_prompt_sha256': hashlib.sha256(bare_prompt.encode()).hexdigest(),
                                'gold_prompt_sha256': hashlib.sha256(gold_prompt.encode()).hexdigest()})
            row = {'id': entry['id'], 'scope': entry['scope'], 'definition_sha256': entry['definition_sha256'],
                   'A_packet_sha256': packet_hash, 'proxy_model': MODEL, 'proxy_revision': REVISION,
                   'device': device, 'dtype': str(dtype), 'n_A': len(results),
                   'mean_delta_p': sum(x['delta_p'] for x in results) / len(results),
                   'per_question': results, 'seconds': time.monotonic() - started,
                   'status': 'development_only_gold_definition_A'}
            output.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
            output.flush()
            if n % 10 == 0 or n == len(pending):
                print(f'Scored {n}/{len(pending)} pending terms', flush=True)


if __name__ == '__main__':
    main()
