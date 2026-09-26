#!/usr/bin/env python3
"""Pre-reader lexical gate for concrete facts versus local rule text.

Named entities and the target term are exempt; synonym-based clues still need
independent semantic review. No B reader result is loaded.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'local_meaning_v5_development'))
from audit_lexical_overlap import content, tokens


def read(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--rules', type=Path, required=True)
    p.add_argument('--items', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--text-field', choices=['world_fact', 'question'], default='world_fact')
    a = p.parse_args()
    rules = {x['definition_id']: x for x in read(a.rules)}
    rows = []
    for item in read(a.items):
        if item.get('case_type') == 'definition_irrelevant_control':
            continue
        rule = rules[item['definition_id']]
        excluded = set(tokens(rule['term']))
        for name in rule['lexical_name_exemptions']:
            excluded.update(tokens(name))
        source = content(rule['source_quote'], excluded)
        visible = content(item[a.text_field], excluded)
        overlap = sorted(source & visible)
        ratio = len(overlap) / len(visible) if visible else 0.0
        rows.append({'id': item['id'], 'definition_id': item['definition_id'],
                     'visible_content_word_count': len(visible),
                     'overlap_words': overlap, 'overlap_ratio': ratio,
                     'passes_20pct': ratio <= .20})
    if not rows:
        raise ValueError('No membership items')
    summary = {'status':'source_only_lexical_gate_before_reader_outcomes',
               'n':len(rows),'median_overlap_ratio':statistics.median(x['overlap_ratio'] for x in rows),
               'n_passes_20pct':sum(x['passes_20pct'] for x in rows),
               'n_fails_20pct':sum(not x['passes_20pct'] for x in rows),
               'threshold':.20,'proper_name_policy':'per-rule name exemptions plus target term tokens',
               'limitations':['Lexical overlap cannot detect synonym paraphrases or internally inconsistent facts.'],
               'rows':rows}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(f"Lexical gate: {summary['n_passes_20pct']}/{len(rows)} pass, median={summary['median_overlap_ratio']:.3f}")


if __name__=='__main__':
    main()
