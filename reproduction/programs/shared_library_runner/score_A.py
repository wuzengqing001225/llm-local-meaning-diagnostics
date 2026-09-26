#!/usr/bin/env python3
"""Score source-checked A questions with one frozen local definition text.

No B file or API key is read. Requires local torch + transformers and the
pinned Qwen model cache; see README for the optional dependency install.
"""
import argparse
import hashlib
import json
import math
import os
import time
from collections import defaultdict
from pathlib import Path

from shared_budget_plan import file_hash, read_rows

SYSTEM = "You answer multiple-choice questions about a company's internal operations. Answer with the letter only.\n\n"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def prompt(row, term, definition):
    note = f'Term note: {term}: {definition}\n\n' if definition else ''
    options = '\n'.join(f'{chr(65+i)}. {text}' for i, text in enumerate(row['options']))
    return SYSTEM + note + row['q'] + '\n' + options + '\nANSWER_LETTER:'


def validate(catalog_path, question_path, development):
    definitions = read_rows(catalog_path)
    catalog = {x['id']: x for x in definitions}
    if len(catalog) != len(definitions) or not definitions:
        raise ValueError('Catalog is empty or has duplicate IDs')
    if not development and any(x.get('validation_status') != 'source_checked' for x in definitions):
        raise ValueError('Formal A requires source-checked definitions')
    questions = read_rows(question_path)
    if not questions:
        raise ValueError('A question file is empty')
    ids = set()
    by_term = defaultdict(list)
    for row in questions:
        qid = row['id']
        if qid in ids:
            raise ValueError('Duplicate A question ID')
        ids.add(qid)
        term_id = row['term_id']
        if term_id not in catalog or not catalog[term_id].get('selectable', True):
            raise ValueError('A question uses an unselectable or unknown definition')
        options = row['options']
        if not isinstance(options, list) or len(options) not in {2, 3, 4} or not all(isinstance(x, str) and x for x in options):
            raise ValueError('A must have two to four nonempty options')
        if not isinstance(row.get('answer'), str) or row['answer'] not in 'ABCD'[:len(options)]:
            raise ValueError('A gold option is missing or invalid')
        if not development and (row.get('quality_status') != 'source_checked' or not row.get('source_post_id')):
            raise ValueError('Formal A requires a checked answer and source post ID')
        by_term[term_id].append(row)
    selectable = {i for i, item in catalog.items() if item.get('selectable', True)}
    if set(by_term) != selectable:
        raise ValueError('A must cover every selectable catalog definition')
    if not development and any(len(by_term[i]) < 4 for i in selectable):
        raise ValueError('Formal A requires at least four checked questions per definition')
    return catalog, questions, by_term


def model_device(torch, requested):
    if requested == 'auto':
        requested = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
    if requested == 'mps' and not torch.backends.mps.is_available():
        raise ValueError('Apple GPU unavailable; run outside a sandbox or specify cpu explicitly')
    if requested == 'cuda' and not torch.cuda.is_available():
        raise ValueError('CUDA GPU unavailable')
    return requested, torch.float16 if requested == 'mps' else (torch.bfloat16 if requested == 'cuda' else torch.float32)


def run(catalog_path, questions_path, out_dir, model_name, revision, requested_device,
        development=False, limit=0):
    catalog_path, questions_path, out_dir = catalog_path.resolve(), questions_path.resolve(), out_dir.resolve()
    catalog, questions, by_term = validate(catalog_path, questions_path, development)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device, dtype = model_device(torch, requested_device)
    if device == 'cpu' and not development:
        raise ValueError('Formal A needs an explicit GPU; CPU scoring would be impractically slow')
    out_dir.mkdir(parents=True, exist_ok=True)
    freeze = {'catalog_sha256': file_hash(catalog_path), 'questions_sha256': file_hash(questions_path),
              'scorer_sha256': file_hash(Path(__file__)), 'model': model_name, 'revision': revision,
              'device': device, 'dtype': str(dtype), 'development_only': development}
    frozen_path = out_dir / 'A_freeze.json'
    if frozen_path.exists():
        if json.loads(frozen_path.read_text()) != freeze:
            raise RuntimeError('A inputs/scorer changed after scoring began')
    else:
        frozen_path.write_text(json.dumps(freeze, indent=2) + '\n')
    raw_path = out_dir / 'A_raw_scores.jsonl'
    done = {x['id']: x for x in read_rows(raw_path)} if raw_path.exists() else {}
    if len(done) != (sum(1 for _ in raw_path.open()) if raw_path.exists() else 0):
        raise ValueError('Duplicate cached A score')
    if set(done) - {x['id'] for x in questions}:
        raise ValueError('Cached A result not present in frozen A input')
    pending = [x for x in questions if x['id'] not in done]
    if limit:
        pending = pending[:limit]
    if pending:
        os.environ['HF_HUB_OFFLINE'] = '1'
        tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(model_name, revision=revision, dtype=dtype,
                                                    local_files_only=True, low_cpu_mem_usage=True).to(device).eval()

        @torch.no_grad()
        def p_correct(text, gold, count):
            inputs = tokenizer(text, return_tensors='pt').to(device)
            logits = model(**inputs).logits[0, -1].float()
            lp = torch.log_softmax(logits, -1)
            scores = []
            for index in range(count):
                letter = chr(65 + index)
                variants = [tokenizer.encode(' ' + letter, add_special_tokens=False),
                            tokenizer.encode(letter, add_special_tokens=False)]
                scores.append(max(lp[tokens[0]].item() for tokens in variants if tokens))
            denominator = math.log(sum(math.exp(value) for value in scores))
            return math.exp(scores[ord(gold) - 65] - denominator)

        with raw_path.open('a') as output:
            for n, row in enumerate(pending, 1):
                term = catalog[row['term_id']]
                bare_text = prompt(row, term['term'], None)
                definition_text = prompt(row, term['term'], term['definition'])
                started = time.monotonic()
                bare = p_correct(bare_text, row['answer'], len(row['options']))
                with_definition = p_correct(definition_text, row['answer'], len(row['options']))
                result = {'id': row['id'], 'term_id': row['term_id'],
                          'source_post_id': row.get('source_post_id'),
                          'definition_sha256': digest(term['definition']),
                          'p_bare': bare, 'p_definition': with_definition,
                          'delta_p': with_definition - bare,
                          'bare_prompt_sha256': digest(bare_text),
                          'definition_prompt_sha256': digest(definition_text),
                          'proxy_model': model_name, 'proxy_revision': revision,
                          'seconds': time.monotonic() - started}
                output.write(canonical(result) + '\n')
                output.flush()
                done[row['id']] = result
                if n % 20 == 0 or n == len(pending):
                    print('A scored', n, '/', len(pending), flush=True)
    if len(done) == len(questions):
        aggregated = []
        for term_id in sorted(by_term):
            qids = [x['id'] for x in by_term[term_id]]
            term = catalog[term_id]
            aggregated.append({'id': term_id, 'definition_sha256': digest(term['definition']),
                               'mean_delta_p': sum(done[qid]['delta_p'] for qid in qids) / len(qids),
                               'n_A': len(qids), 'question_ids': qids,
                               'source_post_ids': sorted({x['source_post_id'] for x in by_term[term_id] if x.get('source_post_id')}),
                               'proxy_model': model_name, 'proxy_revision': revision})
        (out_dir / 'a_scores.jsonl').write_text(''.join(canonical(x) + '\n' for x in aggregated))
        print('A complete:', len(questions), 'questions across', len(aggregated), 'terms')
    else:
        print('A partial:', len(done), '/', len(questions), 'questions; planning remains disabled')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--questions', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--model', default='Qwen/Qwen2.5-7B')
    parser.add_argument('--revision', default='d149729398750b98c0af14eb82c78cfe92750796')
    parser.add_argument('--device', choices=['auto', 'mps', 'cuda', 'cpu'], default='auto')
    parser.add_argument('--development', action='store_true')
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    run(args.catalog, args.questions, args.out_dir, args.model, args.revision,
        args.device, args.development, args.limit)


if __name__ == '__main__':
    main()
