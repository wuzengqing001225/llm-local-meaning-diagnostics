#!/usr/bin/env python3
"""One entry point for the staged shared-definition experiment.

Use `python run_main.py --stage status` for the next required input.
Each stage is resumable. No stage silently fetches public posts.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from shared_budget_plan import file_hash

HERE = Path(__file__).resolve().parent

STUDY_TEMPLATE = {
    'catalog': 'data/catalog.jsonl',
    'a_questions': 'data/A_questions.jsonl',
    'f_posts': 'data/F_posts.jsonl',
    'f_start_utc': 'SET_F_START_UTC',
    'f_end_utc': 'SET_F_END_UTC',
    'b_start_utc': 'SET_B_START_UTC',
    'b_tasks': 'data/B_tasks.jsonl',
    'frequency_complete_stream': False,
    'budget_fraction': .25,
    'proxy_model': 'Qwen/Qwen2.5-7B',
    'proxy_revision': 'd149729398750b98c0af14eb82c78cfe92750796',
    'proxy_device': 'auto',
    'development_only': False,
    'results_dir': 'results',
}


def rows(path):
    return [json.loads(line) for line in path.open() if line.strip()]


def iter_rows(path):
    with path.open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def path(base, value):
    return (base / value).resolve()


def load(config_path):
    if not config_path.exists():
        raise FileNotFoundError('config.json missing. Run `python run_main.py --init-from /path/to/old/config.json`.')
    config = json.loads(config_path.read_text())
    if not isinstance(config.get('study'), dict):
        raise ValueError('config.json needs a study section; --init-from can create the template')
    return config, config['study'], config_path.parent.resolve()


def invoke(script, args):
    subprocess.run([sys.executable, str(HERE / script), *map(str, args)], check=True)


def init_from(old_path, new_path):
    if new_path.exists():
        raise FileExistsError('config.json already exists; it was not overwritten')
    old = json.loads(old_path.read_text())
    if not isinstance(old.get('roles'), dict):
        raise ValueError('Previous config needs a roles object')
    old['study'] = STUDY_TEMPLATE
    new_path.write_text(json.dumps(old, ensure_ascii=False, indent=2) + '\n')
    os.chmod(new_path, 0o600)
    print('Created local config.json with previous role settings and study path placeholders. Keys were not printed.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=HERE / 'config.json')
    parser.add_argument('--init-from', type=Path, help='Copy private model settings into a local single config.json')
    parser.add_argument('--stage', choices=['status', 'frequency', 'score-a', 'plan', 'run-b', 'analyze'], default='status')
    parser.add_argument('--limit', type=int, default=0, help='Optional A scoring pilot size')
    args = parser.parse_args()
    config_path = args.config.resolve()
    if args.init_from:
        init_from(args.init_from.resolve(), config_path)
        return
    config, study, base = load(config_path)
    catalog = path(base, study['catalog'])
    A_questions = path(base, study['a_questions'])
    F_posts = path(base, study['f_posts'])
    B_tasks = path(base, study['b_tasks'])
    results = path(base, study['results_dir'])
    F_dir = results / 'F'
    A_dir = results / 'A'
    B_dir = results / 'B'
    plan = results / 'frozen_plan.json'
    if args.stage == 'status':
        print(json.dumps({'catalog_available': catalog.exists(),
                          'A_questions_available': A_questions.exists(),
                          'authorized_F_export_available': F_posts.exists(),
                          'F_imported': (F_dir / 'source_frame.json').exists(),
                          'A_scored': (A_dir / 'a_scores.jsonl').exists(),
                          'plan_frozen': plan.exists(),
                          'B_tasks_available': B_tasks.exists(),
                          'B_reader_complete': (B_dir / 'B_trials.jsonl').exists(),
                          'analysis_available': (B_dir / 'evaluation.json').exists(),
                          'development_only': study.get('development_only', False)},
                         ensure_ascii=False, indent=2))
        return
    if args.stage == 'frequency':
        if not study.get('development_only') and study.get('frequency_complete_stream') is not True:
            raise ValueError('Formal frequency import requires a complete authorized community stream')
        command = ['--posts', F_posts, '--catalog', catalog,
                   '--start-utc', study['f_start_utc'], '--end-utc', study['f_end_utc'],
                   '--out-dir', F_dir]
        if study.get('frequency_complete_stream'):
            command.append('--complete-stream')
        if study.get('development_only'):
            command.append('--development')
        invoke('import_authorized_posts.py', command)
        return
    if args.stage == 'score-a':
        command = ['--catalog', catalog, '--questions', A_questions, '--out-dir', A_dir,
                   '--model', study['proxy_model'], '--revision', study['proxy_revision'],
                   '--device', study.get('proxy_device', 'auto')]
        if study.get('development_only'):
            command.append('--development')
        if args.limit:
            command.extend(['--limit', args.limit])
        invoke('score_A.py', command)
        return
    if args.stage == 'plan':
        if not (F_dir / 'source_frame.json').exists() or not (A_dir / 'a_scores.jsonl').exists():
            raise ValueError('Import F and finish A scoring before planning')
        frame = json.loads((F_dir / 'source_frame.json').read_text())
        A_post_ids = {q.get('source_post_id') for q in rows(A_questions) if q.get('source_post_id')}
        all_A_have_posts = all(q.get('source_post_id') for q in rows(A_questions))
        F_post_ids = {q['post_id'] for q in iter_rows(F_dir / 'post_matches.jsonl')}
        disjoint = all_A_have_posts and not (A_post_ids & F_post_ids)
        if not study.get('development_only') and not disjoint:
            raise ValueError('A source posts overlap F, or A source IDs are missing')
        runtime = {'catalog': str(catalog), 'a_scores': str(A_dir / 'a_scores.jsonl'),
                   'frequency': str(F_dir / 'frequency.jsonl'),
                   'frequency_matches': str(F_dir / 'post_matches.jsonl'),
                   'budget_fraction': study.get('budget_fraction', .25),
                   'frequency_frame': {'type': frame['frame_type'],
                                       'sha256': frame['posts_sha256'],
                                       'matches_sha256': frame['matches_sha256'],
                                       'communities_sha256': frame['communities_sha256'],
                                       'start_utc': frame['start_utc'], 'end_utc': frame['end_utc'],
                                       'overlap_check_passed': disjoint},
                   'b_start_utc': study['b_start_utc'],
                   'development_only': study.get('development_only', False),
                   'out': str(plan)}
        results.mkdir(parents=True, exist_ok=True)
        runtime_path = results / 'study_frozen_inputs.json'
        content = json.dumps(runtime, ensure_ascii=False, indent=2) + '\n'
        if runtime_path.exists() and runtime_path.read_text() != content:
            raise RuntimeError('Study inputs changed after planning; use a new results directory')
        runtime_path.write_text(content)
        invoke('shared_budget_plan.py', ['--config', runtime_path])
        return
    if args.stage == 'run-b':
        if not plan.exists() or not B_tasks.exists():
            raise ValueError('Frozen plan and independently checked B_tasks.jsonl required')
        locked = json.loads(plan.read_text())
        for label, actual in [('catalog', catalog), ('a_scores', A_dir / 'a_scores.jsonl'),
                              ('frequency', F_dir / 'frequency.jsonl'),
                              ('frequency_matches', F_dir / 'post_matches.jsonl')]:
            if file_hash(actual) != locked['input_sha256'][label]:
                raise ValueError(f'{label} differs from frozen plan')
        F_post_ids = {q['post_id'] for q in iter_rows(F_dir / 'post_matches.jsonl')}
        A_post_ids = {q.get('source_post_id') for q in rows(A_questions) if q.get('source_post_id')}
        B_post_ids = {q['post_id'] for q in iter_rows(B_tasks)}
        if len(B_post_ids) != sum(1 for _ in iter_rows(B_tasks)) or B_post_ids & (A_post_ids | F_post_ids):
            raise ValueError('B post IDs duplicate or overlap A/F')
        invoke('run_B_reader.py', ['--plan', plan, '--catalog', catalog,
                                   '--tasks', B_tasks, '--config', config_path, '--out-dir', B_dir])
        return
    if args.stage == 'analyze':
        trials = B_dir / 'B_trials.jsonl'
        if not trials.exists():
            raise ValueError('Complete B reader calls first')
        command = ['--plan', plan, '--catalog', catalog, '--trials', trials,
                   '--out', B_dir / 'evaluation.json']
        if study.get('development_only'):
            command.append('--development')
        invoke('evaluate_shared_budget.py', command)


if __name__ == '__main__':
    main()
