#!/usr/bin/env python3
"""Source-only glossary and public-issue feasibility preview. No issue outcomes used."""
import hashlib
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / 'candidate_sources'
GLOSSARY_URL = 'https://docs.gitlab.com/auth/auth_glossary/'
ISSUES_URL = 'https://gitlab.com/api/v4/projects/278964/issues'
CUTOFF = datetime(2026, 9, 25, tzinfo=timezone.utc)


def fetch(url, params=None):
    for attempt in range(4):
        response = requests.get(url, params=params, timeout=45)
        if response.status_code in {429, 500, 502, 503, 504}:
            time.sleep(2 ** attempt)
            continue
        response.raise_for_status()
        return response
    raise RuntimeError(f'Could not fetch {url}')


def glossary():
    response = fetch(GLOSSARY_URL)
    path = SOURCES / 'gitlab_auth_glossary.html'
    path.write_bytes(response.content)
    main = BeautifulSoup(response.content, 'html.parser').find('main')
    terms = []
    for tag in main.find_all('dt'):
        sibling = tag.find_next_sibling('dd')
        if not sibling:
            continue
        name = tag.get_text(' ', strip=True)
        definition = sibling.get_text(' ', strip=True)
        if not name or not definition:
            continue
        terms.append({'term': name, 'definition': definition})
    return terms, {'url': GLOSSARY_URL, 'sha256': hashlib.sha256(response.content).hexdigest()}


def issues(search=None):
    params = {'state': 'all', 'per_page': 100, 'page': 1, 'order_by': 'created_at', 'sort': 'desc'}
    if search:
        params['search'] = search
    raw = []
    source_pages = []
    for page in range(1, 5):
        params['page'] = page
        response = fetch(ISSUES_URL, params)
        batch = response.json()
        raw.extend(batch)
        source_pages.append({'url': response.url, 'sha256': hashlib.sha256(response.content).hexdigest()})
        if sum(datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')) < CUTOFF for item in raw) >= 100 or len(batch) < 100:
            break
    path = SOURCES / ('gitlab_auth_issues_' + (search or 'latest') + '.json')
    path.write_text(json.dumps(raw, ensure_ascii=False) + '\n')
    records = []
    for issue in raw:
        created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
        if created >= CUTOFF:
            continue
        text = issue['title'] + '\n' + (issue.get('description') or '')
        # Code and links are not ordinary request language and would inflate
        # literal term matches. Headers and prose remain available.
        text = re.sub(r'```.*?```', ' ', text, flags=re.S)
        text = re.sub(r'`[^`]*`', ' ', text)
        text = re.sub(r'https?://\S+', ' ', text)
        records.append({'id': issue['id'], 'iid': issue['iid'], 'title': issue['title'],
                        'created_at': issue['created_at'], 'url': issue['web_url'], 'text': text})
    records = records[:100]
    return records, {'pages': source_pages, 'returned': len(raw), 'before_cutoff_used': len(records)}


def variants(term):
    out = {term}
    for parenthetical in re.findall(r'\(([^)]+)\)', term):
        if 2 <= len(parenthetical) <= 20:
            out.add(parenthetical)
    out.add(re.sub(r'\s*\([^)]*\)', '', term).strip())
    return {x for x in out if len(x) >= 3 and x.lower() not in {'the', 'and', 'for'}}


def main():
    terms, glossary_meta = glossary()
    pools = {}
    meta = {}
    for query in [None, 'SAML', 'OIDC', 'SCIM', '2FA']:
        name = query or 'latest'
        pools[name], meta[name] = issues(query)
    counts = {}
    examples = {}
    for name, records in pools.items():
        histogram = Counter()
        hits = []
        for issue in records:
            found = []
            for term in terms:
                if any(re.search(r'(?<!\w)' + re.escape(v) + r'(?!\w)', issue['text'], re.I)
                       for v in variants(term['term'])):
                    found.append(term['term'])
            histogram[len(found)] += 1
            if found and len(hits) < 15:
                hits.append({'iid': issue['iid'], 'title': issue['title'], 'terms': found})
        counts[name] = {'n': len(records), 'histogram': dict(sorted(histogram.items())),
                        'fraction_2plus': sum(v for k, v in histogram.items() if k >= 2) / len(records) if records else 0}
        examples[name] = hits
    output = {'glossary': {**glossary_meta, 'n_provisional_entries': len(terms), 'entries': terms},
              'issue_sources': meta, 'counts': counts, 'examples': examples,
              'caveat': 'Topical searches are enriched by search terms; latest is project-wide. Literal mentions include request descriptions but exclude code fences, inline code, and URLs. Entries and mappings require source review. No issue resolution or answer outcome read.'}
    (ROOT / 'gitlab_auth_glossary_issue_preview.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'glossary_entries': len(terms), 'counts': counts}, ensure_ascii=False))


if __name__ == '__main__':
    main()
