#!/usr/bin/env python3
"""No-key, no-network smoke test of import, frozen selection and paired scoring."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows))


def run(args):
    result = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def main():
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        words = ['Alpha', 'Beta', 'Gamma', 'Delta']
        definitions = [f'{name} means a distinct local source category.' for name in words]
        catalog = [{'id': f's:{name}', 'scope': 's', 'term': name, 'definition': definition,
                    'source_ref': 'fictional self-test source', 'validation_status': 'source_checked',
                    'unit_type': 'local_definition'} for name, definition in zip(words, definitions)]
        write_rows(root / 'data/catalog.jsonl', catalog)
        questions = [{'id': f's:{name}:A{i}', 'term_id': f's:{name}', 'q': 'Which option fits?',
                      'options': ['first', 'second'], 'answer': 'A',
                      'source_post_id': f'outside_F_{name}_{i}', 'quality_status': 'source_checked'}
                     for name in words for i in range(4)]
        write_rows(root / 'data/A_questions.jsonl', questions)
        posts = [{'post_id': f'F{n}', 'scope': 's', 'created_utc': '2020-06-01T00:00:00Z',
                  'title': name, 'selftext': ''}
                 for n, name in enumerate(['Alpha'] * 5 + ['Beta'] * 4 + ['Gamma'])]
        write_rows(root / 'data/F_posts.jsonl', posts)
        study = {'catalog': 'data/catalog.jsonl', 'a_questions': 'data/A_questions.jsonl',
                 'f_posts': 'data/F_posts.jsonl', 'f_start_utc': '2020-01-01T00:00:00Z',
                 'f_end_utc': '2021-01-01T00:00:00Z', 'b_start_utc': '2021-01-01T00:00:00Z',
                 'b_tasks': 'data/B_tasks.jsonl', 'frequency_complete_stream': True,
                 'budget_fraction': .25, 'proxy_model': 'fixture', 'proxy_revision': 'fixture',
                 'proxy_device': 'auto', 'development_only': False, 'results_dir': 'results'}
        (root / 'config.json').write_text(json.dumps({'roles': {}, 'study': study}) + '\n')
        run([HERE / 'run_main.py', '--config', root / 'config.json', '--stage', 'frequency'])
        a = [{'id': f's:{name}', 'definition_sha256': hashlib.sha256(definition.encode()).hexdigest(),
              'mean_delta_p': score, 'n_A': 4, 'question_ids': [f's:{name}:A{i}' for i in range(4)],
              'proxy_model': 'fixture'}
             for name, definition, score in zip(words, definitions, [.01, .9, .5, .2])]
        write_rows(root / 'results/A/a_scores.jsonl', a)
        run([HERE / 'run_main.py', '--config', root / 'config.json', '--stage', 'plan'])
        plan = json.loads((root / 'results/frozen_plan.json').read_text())
        base = plan['policies']['frequency_per_cost']['root_definition_ids']
        method = plan['policies']['frequency_delta_p_per_cost']['root_definition_ids']
        if base == method or plan['status'] != 'FROZEN_BEFORE_B':
            raise AssertionError('Fixture must produce distinct formal library selections')
        trials = []
        for request_id, term_id, cluster in [('B1', base[0], 'c1'), ('B2', method[0], 'c2')]:
            for policy in ('frequency_per_cost', 'frequency_delta_p_per_cost'):
                injected = [term_id] if term_id in plan['policies'][policy]['root_definition_ids'] else []
                trials.append({'request_id': request_id, 'policy': policy, 'scope': 's', 'cluster': cluster,
                               'created_utc': '2021-06-01T00:00:00Z', 'matched_definition_ids': [term_id],
                               'injected_definition_ids': injected, 'sampling_weight': 1,
                               'gold_source_checked': True,
                               'judgment': 'correct' if injected else 'wrong',
                               'reader_model': 'gpt-5.6-terra', 'question_sha256': 'fixture-question',
                               'prompt_sha256': 'fixture-prompt', 'settings_sha256': 'fixture-settings',
                               'provider_response_id': 'fixture-response', 'returned_model': 'gpt-5.6-terra',
                               'usage': {'prompt_tokens': 10, 'completion_tokens': 2}, 'api_call_made': True})
        write_rows(root / 'results/B/B_trials.jsonl', trials)
        run([HERE / 'run_main.py', '--config', root / 'config.json', '--stage', 'analyze'])
        summary = json.loads((root / 'results/B/evaluation.json').read_text())
        if summary['primary']['n_requests'] != 2:
            raise AssertionError('Paired evaluator count incorrect')
        print('SELF_TEST_PASS: import, formal freeze, differing policies, paired evaluation; no API calls')


if __name__ == '__main__':
    main()
