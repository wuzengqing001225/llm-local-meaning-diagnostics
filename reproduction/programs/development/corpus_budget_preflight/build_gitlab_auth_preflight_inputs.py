#!/usr/bin/env python3
"""Prepare provisional definition-level frames from the GitLab source-only screen."""
import json
import re
import subprocess
import sys
from pathlib import Path

from preview_gitlab_auth_issues import variants

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'candidate_sources'
SCOPE = 'gitlab_auth_glossary_current_snapshot'


def jsonl(path, rows):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows))


def clean(text):
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    text = re.sub(r'`[^`]*`', ' ', text)
    text = re.sub(r'https?://\S+', ' ', text)
    return text


def main():
    preview = json.loads((ROOT / 'gitlab_auth_glossary_issue_preview.json').read_text())
    entries = []
    for i, row in enumerate(preview['glossary']['entries']):
        entries.append({'id': f'auth_{i:03}', 'scope': SCOPE, 'unit_type': 'local_definition',
                        'term': row['term'], 'definition': row['definition'],
                        'source_ref': 'https://docs.gitlab.com/auth/auth_glossary/',
                        'validation_status': 'provisional', 'dependencies': []})
    def_path = ROOT / 'gitlab_auth_definitions_provisional.jsonl'
    jsonl(def_path, entries)
    seen = set()
    for pool in ['latest', 'SAML', 'OIDC', 'SCIM', '2FA']:
        raw = json.loads((SOURCE / f'gitlab_auth_issues_{pool}.json').read_text())
        requests = []
        for issue in raw:
            key = issue['id']
            if issue['created_at'] >= '2026-09-25':
                continue
            # Search pools can overlap. Each pool's preview is separate; a
            # combined final frame must deduplicate issue IDs.
            text = clean(issue['title'] + '\n' + (issue.get('description') or ''))
            ids = [e['id'] for e in entries if any(
                re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', text, re.I)
                for alias in variants(e['term']))]
            requests.append({'id': str(key), 'scope': SCOPE,
                             'matched_definition_ids': ids,
                             'matcher_provenance': 'literal_glossary_term_or_parenthetic_alias_in_issue_title_and_prose;code_and_urls_removed'})
            if len(requests) >= 100:
                break
        path = ROOT / f'gitlab_auth_{pool}_requests_provisional.jsonl'
        jsonl(path, requests)
        out = ROOT / f'gitlab_auth_{pool}_budget_preliminary.json'
        subprocess.run([sys.executable, str(ROOT / 'definition_budget_preflight.py'),
                        '--definitions', str(def_path), '--requests', str(path),
                        '--budget-origin', 'locked_median_half_primary_rule_provisional_source_only',
                        '--out', str(out)], check=True)
        seen.update(int(x['id']) for x in requests)
    print('union issue IDs across pools', len(seen))


if __name__ == '__main__':
    main()
