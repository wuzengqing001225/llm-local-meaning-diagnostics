#!/usr/bin/env python3
"""Compare a completed human blind review with sealed historical answer keys.

Run only after the reviewer has submitted all 80 answers. The script writes
aggregate estimates and a separate private item ledger. It never modifies the
blind ZIP or silently corrects the paper's proxy probability scores.
"""
import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIVATE = HERE.parent / 'historical_blind_audit_20260926_private'
FRAME_N = {'synthetic': 456, 'reddit_general': 1273,
           'reddit_disagreement': 118, 'defi': 379, 'cuad': 1500}


def wilson(errors, n, z=1.96):
    if n == 0:
        return None
    p = errors / n
    denominator = 1 + z*z/n
    center = (p + z*z/(2*n)) / denominator
    margin = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / denominator
    return [max(0, center-margin), min(1, center+margin)]


def normalize(value):
    return (value or '').strip().lower()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--answers', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=PRIVATE / 'completed_review_analysis.json')
    args = parser.parse_args()
    keys = {x['audit_id']: x for x in (json.loads(line) for line in (PRIVATE / 'stored_keys.jsonl').open())}
    with args.answers.open(encoding='utf-8-sig', newline='') as file:
        answers = list(csv.DictReader(file))
    if len(answers) != 80 or {x['audit_id'] for x in answers} != set(keys):
        raise ValueError('Review must contain each of the 80 sealed item IDs exactly once')
    comparisons = []
    for row in answers:
        audit_id = row['audit_id']
        answer = normalize(row['independent_answer'])
        unique = normalize(row['unique_answer_yes_no'])
        sufficient = normalize(row['source_sufficient_yes_no'])
        if answer not in {'a','b','c','d','undetermined'} or unique not in {'yes','no'} or sufficient not in {'yes','no'}:
            raise ValueError('Incomplete answer/uniqueness/source columns at ' + audit_id)
        valid = answer in {'a','b','c','d'} and unique == 'yes' and sufficient == 'yes'
        if valid and not normalize(row['evidence_quote']):
            raise ValueError('A valid answer requires a short source quote: ' + audit_id)
        stored = keys[audit_id]
        comparisons.append({'audit_id': audit_id, 'corpus': stored['corpus'],
                            'stratum': stored['stratum'], 'term_id': stored['term_id'],
                            'source_qid': stored['qid'], 'human_answer': answer.upper(),
                            'stored_answer': stored['stored_key'], 'valid_source_answer': valid,
                            'stored_key_disagrees': valid and answer.upper() != stored['stored_key'],
                            'source_insufficient': sufficient == 'no',
                            'ambiguous_or_invalid': not valid,
                            'evidence_quote': row['evidence_quote'], 'comment': row['comment']})
    by_corpus = defaultdict(list)
    by_stratum = defaultdict(list)
    for item in comparisons:
        by_corpus[item['corpus']].append(item)
        by_stratum[item['stratum']].append(item)
    results = {}
    for name, items in sorted(by_corpus.items()):
        valid = [x for x in items if x['valid_source_answer']]
        errors = sum(x['stored_key_disagrees'] for x in valid)
        invalid = sum(x['ambiguous_or_invalid'] for x in items)
        results[name] = {'sample_n': len(items), 'valid_n': len(valid),
                         'key_disagreements_among_valid': errors,
                         'key_disagreement_rate_among_valid': errors/len(valid) if valid else None,
                         'question_level_Wilson_95_for_key_error': wilson(errors,len(valid)),
                         'invalid_or_insufficient_n': invalid,
                         'invalid_or_insufficient_rate': invalid/len(items),
                         'question_level_Wilson_95_for_invalid': wilson(invalid,len(items))}
    # Reddit was intentionally enriched for the previously frozen policy-disagreement frame.
    # Use the complete frame counts, not the 10/10 sample proportions, to recover its overall rate.
    reddit_rows = [x for x in comparisons if x['corpus'] == 'reddit']
    def reddit_estimate(items):
        weighted_valid = weighted_bad = weighted_invalid = 0.0
        total_weight = 0.0
        for stratum in ('reddit_general','reddit_disagreement'):
            group = [x for x in items if x['stratum'] == stratum]
            if not group:
                return None
            weight = FRAME_N[stratum] / len(group)
            total_weight += weight*len(group)
            weighted_valid += weight*sum(x['valid_source_answer'] for x in group)
            weighted_bad += weight*sum(x['stored_key_disagrees'] for x in group)
            weighted_invalid += weight*sum(x['ambiguous_or_invalid'] for x in group)
        return {'key_error_among_valid': weighted_bad/weighted_valid if weighted_valid else None,
                'invalid_rate': weighted_invalid/total_weight,
                'weighted_valid': weighted_valid,
                'weighted_bad': weighted_bad}
    reddit = reddit_estimate(reddit_rows)
    rng = random.Random(260926)
    draws = []
    for _ in range(3000):
        sample = []
        for stratum in ('reddit_general','reddit_disagreement'):
            group = by_stratum[stratum]
            sample += rng.choices(group,k=len(group))
        estimate = reddit_estimate(sample)
        if estimate and estimate['key_error_among_valid'] is not None:
            draws.append(estimate['key_error_among_valid'])
    if draws:
        draws.sort()
        reddit['stratified_question_bootstrap_95_for_key_error'] = [draws[round(.025*(len(draws)-1))],
                                                                    draws[round(.975*(len(draws)-1))]]
    results['reddit']['frame_weighted_estimate'] = reddit
    output = {'status':'COMPLETE_HUMAN_SOURCE_AUDIT_ONE_REVIEWER',
              'selection_seed':'LLM-IDF-human-source-audit-v1-2026-09-26',
              'frame_sizes':FRAME_N,'per_corpus':results,
              'limitation':'20 items per main corpus, Reddit 10/10 enriched stratum; wide question-level intervals and possible within-term dependence. A key mismatch cannot be corrected by reusing old p_correct for the old key.',
              'next_rule':'If a corpus has substantial invalid/key-disagreement evidence, expand source audit before treating its original AUROC as robust. Rescore affected questions if changing gold keys.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    ledger=args.out.parent/'completed_review_private_item_ledger.jsonl'
    ledger.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in comparisons))
    print(json.dumps({name:{'sample_n':v['sample_n'],'valid_n':v['valid_n'],
                            'key_disagreements':v['key_disagreements_among_valid'],
                            'invalid':v['invalid_or_insufficient_n']} for name,v in results.items()},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
