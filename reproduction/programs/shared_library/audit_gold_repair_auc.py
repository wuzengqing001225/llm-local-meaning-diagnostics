#!/usr/bin/env python3
"""Reddit conditional-repair AUROC with community-gold definitions.

Uses existing aligned Qwen A scores and archived DeepSeek glossG outcomes only.
No model calls. Direct A and held-out sibling B are reported separately.
"""
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / 'release_20260923/llm-idf-reproduce/data/reddit/raw_outputs'
GOLD_A = ROOT / 'gold_aligned_development/qwen_A_gold.jsonl'


def load(path):
    return {x['id']: x for x in (json.loads(line) for line in path.open())}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc(rows, label, score):
    ordered = sorted(rows, key=lambda x: x[score])
    positives = sum(x[label] for x in ordered)
    negatives = len(ordered) - positives
    if positives == 0 or negatives == 0:
        return None
    wins = 0.0
    lower_negatives = 0
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and ordered[j][score] == ordered[i][score]:
            j += 1
        tied_pos = sum(ordered[k][label] for k in range(i, j))
        tied_neg = (j - i) - tied_pos
        wins += tied_pos * (lower_negatives + .5 * tied_neg)
        lower_negatives += tied_neg
        i = j
    return wins / (positives * negatives)


def cluster_ci(rows, label, score, replicates=2000):
    groups = defaultdict(list)
    for row in rows:
        groups[row['community']].append(row)
    keys = sorted(groups)
    rng = random.Random(260926)
    draws = []
    for _ in range(replicates):
        sampled = [row for group in rng.choices(keys, k=len(keys)) for row in groups[group]]
        value = auc(sampled, label, score)
        if value is not None:
            draws.append(value)
    draws.sort()
    if not draws:
        return None
    return [draws[round(.025 * (len(draws) - 1))], draws[round(.975 * (len(draws) - 1))]]


def make_rows():
    gold = load(GOLD_A)
    old = load(DATA / 'lpmc_reddit_v2.jsonl')
    reader = load(DATA / 'reddit_v2_eqa.jsonl')
    weights = load(DATA / 'reddit_v2_weights.jsonl')
    if len(gold) != 215:
        raise ValueError('Expected 215 gold-scored target terms')
    records = []
    bare_mismatch = 0
    for term_id in sorted(gold):
        qwen, eqa, baseline, w = gold[term_id], reader[term_id], old[term_id], weights[term_id]
        if not w['labels'].get('is_target') or qwen['definition_sha256'] != hashlib.sha256(w['gloss_gold'].encode()).hexdigest():
            raise ValueError('Definition version or target type mismatch: ' + term_id)
        qs = eqa['questions']
        old_qs = baseline['per_question']
        if len(qs) != len(old_qs) or not all(q['q'].startswith(p['q']) for p, q in zip(old_qs, qs)):
            raise ValueError('Archived question alignment mismatch: ' + term_id)
        A = [j for j in range(0, len(qs), 2)]
        B = [j for j in range(1, len(qs), 2)]
        if len(A) != qwen['n_A'] or not B:
            raise ValueError('A/B split mismatch: ' + term_id)
        aligned = {int(x['question_id'].split(':A')[-1]): x for x in qwen['per_question']}
        if set(aligned) != set(A):
            raise ValueError('Missing A probability row: ' + term_id)
        for j in A:
            if aligned[j]['p_bare'] != old_qs[j]['bare']['p_correct']:
                bare_mismatch += 1
        mean_gold = sum(aligned[j]['delta_p'] for j in A) / len(A)
        mean_auto = sum(old_qs[j]['glossC']['p_correct'] - old_qs[j]['bare']['p_correct'] for j in A) / len(A)
        mean_risk = sum(1 - aligned[j]['p_bare'] for j in A) / len(A)
        for j in range(len(qs)):
            c = qs[j]['correct']
            if any(c.get(key) not in {0, 0.0, 1, 1.0} for key in ('bare', 'glossC', 'glossG')):
                raise ValueError('Missing reader correctness label: ' + term_id)
            if j in A:
                score_gold = aligned[j]['delta_p']
                score_auto = old_qs[j]['glossC']['p_correct'] - old_qs[j]['bare']['p_correct']
                risk = 1 - aligned[j]['p_bare']
            else:
                score_gold, score_auto, risk = mean_gold, mean_auto, mean_risk
            records.append({'term_id': term_id, 'community': w['labels']['subreddit'],
                            'index': j, 'split': 'A_direct' if j in A else 'B_sibling',
                            'bare_error': int(c['bare'] == 0),
                            'repair_gold': int(c['bare'] == 0 and c['glossG'] == 1),
                            'repair_auto': int(c['bare'] == 0 and c['glossC'] == 1),
                            'harm_gold': int(c['bare'] == 1 and c['glossG'] == 0),
                            'harm_auto': int(c['bare'] == 1 and c['glossC'] == 0),
                            'delta_p_gold': score_gold, 'delta_p_auto': score_auto,
                            'risk_R': risk})
    if bare_mismatch:
        raise ValueError('Bare probability changed in gold re-score')
    return records


def main():
    rows = make_rows()
    settings = []
    for split in ('A_direct', 'B_sibling'):
        full = [row for row in rows if row['split'] == split]
        failed = [row for row in full if row['bare_error']]
        for label, score, name in [
            ('repair_gold', 'delta_p_gold', 'same_gold_definition'),
            ('repair_auto', 'delta_p_auto', 'original_auto_definition'),
            ('repair_gold', 'delta_p_auto', 'auto_score_gold_reader_mismatch'),
            ('repair_auto', 'delta_p_gold', 'gold_score_auto_reader_mismatch'),
            ('repair_gold', 'risk_R', 'risk_R_gold_reader_secondary')]:
            settings.append({'split': split, 'comparison': name, 'n_all': len(full),
                             'n_bare_failures': len(failed), 'n_repairs': sum(x[label] for x in failed),
                             'n_harms': sum(x['harm_gold' if label == 'repair_gold' else 'harm_auto'] for x in full),
                             'n_communities': len({x['community'] for x in failed}),
                             'conditional_repair_auroc': auc(failed, label, score),
                             'community_cluster_95_interval': cluster_ci(failed, label, score)})
    output = {'status': 'DEVELOPMENT_SAME_TERM_QUESTIONS_NOT_INDEPENDENT_REQUESTS',
              'n_terms': len({x['term_id'] for x in rows}), 'n_questions': len(rows),
              'bare_probabilities_identical_to_original': True,
              'definition_rule': 'A Δp is valid only for the exact definition text scored; gold-gloss A versus glossG reader is aligned',
              'source_hashes': {str(path): sha(path) for path in
                                (GOLD_A, DATA / 'lpmc_reddit_v2.jsonl', DATA / 'reddit_v2_eqa.jsonl',
                                 DATA / 'reddit_v2_weights.jsonl')},
              'settings': settings}
    destination = ROOT / 'gold_aligned_development/gold_repair_auc.json'
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    records_path = ROOT / 'gold_aligned_development/gold_repair_rows.jsonl'
    records_path.write_text(''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows))
    for item in settings:
        if item['comparison'] in {'same_gold_definition', 'original_auto_definition', 'auto_score_gold_reader_mismatch'}:
            print(item['split'], item['comparison'], 'n_failed', item['n_bare_failures'],
                  'repairs', item['n_repairs'], 'AUROC', round(item['conditional_repair_auroc'], 3),
                  'CI', [round(x, 3) for x in item['community_cluster_95_interval']])


if __name__ == '__main__':
    main()
