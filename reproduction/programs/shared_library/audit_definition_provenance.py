#!/usr/bin/env python3
"""Record which definition version actually fed each archived experiment arm."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'release_20260923/llm-idf-reproduce/data'
RECOVERED = ROOT.parent / 'release_20260923/llm-idf-reproduce/audit/recovered/cuad_gold_deepseek_raw.jsonl'


def rows(path):
    return [json.loads(line) for line in path.open()]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    files = {
        'synthetic_diagnostic': DATA / 'synthetic_v1/raw_outputs/v1_weights.jsonl',
        'reddit_diagnostic': DATA / 'reddit/raw_outputs/reddit_v2_weights.jsonl',
        'defi_diagnostic': DATA / 'defi/raw_outputs/defi_strict_weights.jsonl',
        'cuad_small_diagnostic': DATA / 'cuad/raw_outputs/cuad_weights_deepseek.jsonl',
    }
    groups = {}
    for name, path in files.items():
        records = rows(path)
        groups[name] = {'n_records': len(records),
                        'n_auto_gloss_source': sum(x.get('gloss_source') == 'auto' for x in records),
                        'n_used_equal_to_source_gold': sum(x.get('gloss_used') == x.get('gloss_gold') for x in records),
                        'source_sha256': sha(path)}
    weights = {x['id']: x for x in rows(files['cuad_small_diagnostic'])}
    cases = rows(RECOVERED)
    if len(cases) != 671:
        raise ValueError('Expected 671 recovered small-CUAD questions')
    if not all(x['gloss_used']['glossC'] == weights[x['id']]['gloss_used'] and
               x['gloss_used']['glossG'] == weights[x['id']]['gloss_gold'] for x in cases):
        raise ValueError('CUAD small source arm mapping inconsistent')
    arm_accuracy = {condition: sum(x['correct_recovered'][condition] for x in cases) / len(cases)
                    for condition in ('bare', 'glossC', 'glossG')}
    groups['cuad_small_recovered_671'] = {
        'n_questions': len(cases), 'proxy_and_reader_glossC': 'automatically_drafted',
        'reader_glossG': 'original_contract_definition',
        'n_C_equal_G': sum(x['gloss_used']['glossC'] == x['gloss_used']['glossG'] for x in cases),
        'n_correctness_C_differs_G': sum(x['correct_recovered']['glossC'] != x['correct_recovered']['glossG'] for x in cases),
        'accuracy': arm_accuracy, 'source_sha256': sha(RECOVERED)}
    full_terms = DATA / 'cuad/inputs/terms_full.jsonl'
    full = rows(full_terms)
    groups['cuad_full_library'] = {'n_extracted_term_records': len(full),
                                   'definition_field': 'def_raw_from_contract',
                                   'proxy_and_T2_reader_source': 't1_terms/t2_terms derived from def_raw; T2 reader invoked without weights',
                                   'term_source_sha256': sha(full_terms)}
    output = {'status': 'source_field_and_archived_prompt_mapping_audit', 'groups': groups,
              'distinction': 'The full 1500-question CUAD library uses original contract definitions. The separate 671-question small CUAD set scores and reports glossC from an automatic rewrite; its glossG arm supplies original contract text.'}
    (ROOT / 'definition_provenance_audit.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    for name, info in groups.items():
        print(name, {k: v for k, v in info.items() if k not in {'source_sha256', 'term_source_sha256'}})


if __name__ == '__main__':
    main()
