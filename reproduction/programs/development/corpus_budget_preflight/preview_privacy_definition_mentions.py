#!/usr/bin/env python3
"""Answer-blind, conservative screen of named policy definitions in existing questions.

This is a source feasibility diagnostic, not a complete definition catalog or
an answer-derived retrieval evaluation. PolicyQA repeated question templates are
kept separate from policy-specific instances.
"""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'candidate_sources'


def normalize(s):
    return re.sub(r'\s+', ' ', s).strip()


def policyqa():
    segments = defaultdict(set)
    questions = defaultdict(set)
    for path in sorted((SRC / 'policyqa').glob('*.json')):
        for doc in json.loads(path.read_text())['data']:
            title = doc['title']
            for para in doc['paragraphs']:
                segments[title].add(normalize(para['context']))
                for qa in para['qas']:
                    questions[title].add(normalize(qa['question']))
    return segments, questions


def privacyqa():
    segments = defaultdict(set)
    questions = defaultdict(set)
    for path in sorted((SRC / 'privacyqa').glob('*.csv')):
        with path.open(newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f, delimiter='\t'):
                title = row['DocID']
                segments[title].add(normalize(row['Segment']))
                questions[title].add(normalize(row['Query']))
    return segments, questions


# A named phrase immediately preceding a defining verb. This deliberately
# excludes generic policy prose such as "this includes" and "by other means".
QUOTED = re.compile(r'["“]([^"”]{2,65})["”]\s+(?:means|refers to|is defined as|includes)\b', re.I)
UNQUOTED = re.compile(
    r'(?<![A-Za-z])([A-Z][a-zA-Z-]*(?:\s+[A-Z][a-zA-Z-]*){0,4})\s+'
    r'(?:means|refers to|is defined as|includes)\b'
)
STOP = {'This', 'That', 'It', 'Which', 'And', 'Or', 'We', 'You', 'They', 'Information'}


def candidates(segments):
    found = defaultdict(dict)
    for doc, units in segments.items():
        for unit in units:
            for pattern in (QUOTED, UNQUOTED):
                for m in pattern.finditer(unit):
                    term = normalize(m.group(1)).strip('"“” .,:;')
                    if term in STOP or len(term) < 3 or len(term.split()) > 7:
                        continue
                    key = term.casefold()
                    found[doc].setdefault(key, {'term': term, 'example': unit[:500]})
    return found


def main():
    results = {}
    for name, loader in [('PolicyQA', policyqa), ('PrivacyQA', privacyqa)]:
        segments, questions = loader()
        terms = candidates(segments)
        match_counts = Counter()
        source_examples = []
        matched_examples = []
        by_doc = []
        for doc in sorted(questions):
            doc_terms = terms[doc]
            n_multi = 0
            for question in questions[doc]:
                matched = sorted(
                    d['term'] for key, d in doc_terms.items()
                    if re.search(r'(?<!\w)' + re.escape(key) + r'(?!\w)', question, re.I)
                )
                match_counts[len(matched)] += 1
                n_multi += len(matched) >= 2
                if matched and len(matched_examples) < 30:
                    matched_examples.append({'doc': doc, 'question': question, 'terms': matched})
            by_doc.append({'doc': doc, 'questions': len(questions[doc]), 'named_definitions': len(doc_terms), 'questions_matching_2plus': n_multi})
            for item in doc_terms.values():
                if len(source_examples) < 80:
                    source_examples.append({'doc': doc, **item})
        n_questions = sum(map(len, questions.values()))
        summary = {
            'source': name,
            'n_policies': len(segments),
            'n_unique_policy_segments': sum(map(len, segments.values())),
            'n_policy_question_instances': n_questions,
            'n_global_distinct_question_texts': len({q.casefold() for qs in questions.values() for q in qs}),
            'n_provisional_named_definitions': sum(map(len, terms.values())),
            'n_questions_matching_1plus': sum(v for k, v in match_counts.items() if k >= 1),
            'n_questions_matching_2plus': sum(v for k, v in match_counts.items() if k >= 2),
            'fraction_matching_2plus': sum(v for k, v in match_counts.items() if k >= 2) / n_questions,
            'match_count_distribution': dict(sorted(match_counts.items())),
            'by_doc': by_doc,
            'named_definition_examples': source_examples,
            'matched_question_examples': matched_examples,
            'limitations': 'Strong-form named definitions and exact question mentions only; not an upper bound on all possible semantic matches. No answer, label, relevant segment, or gold definition IDs were read.'
        }
        results[name] = summary
        print(name, {k: v for k, v in summary.items() if k not in {'by_doc', 'named_definition_examples', 'matched_question_examples'}})
    (ROOT / 'privacy_policy_named_definition_preview.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
