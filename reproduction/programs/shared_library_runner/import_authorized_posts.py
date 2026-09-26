#!/usr/bin/env python3
"""Match a user-supplied, authorized local post export to frozen glossary terms.

Does not fetch the internet or write post text to output. A complete-stream
assertion is recorded as user-supplied provenance, never inferred from the file.
"""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from shared_budget_plan import file_hash, read_rows


def timestamp(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def term_pattern(text):
    return re.compile(r'(?<!\w)' + re.escape(text) + r'(?!\w)', re.I)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--posts', type=Path, required=True, help='Authorized local JSONL export, no API access here')
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--start-utc', required=True)
    parser.add_argument('--end-utc', required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    parser.add_argument('--complete-stream', action='store_true', help='Affirm export covers this full community/time window')
    parser.add_argument('--development', action='store_true', help='Allow provisional historical glossary only')
    args = parser.parse_args()
    if timestamp(args.start_utc) >= timestamp(args.end_utc):
        raise ValueError('Start must precede end')
    catalog = read_rows(args.catalog)
    if not args.development and any(x.get('validation_status') != 'source_checked' for x in catalog):
        raise ValueError('Formal import requires source-checked definitions')
    patterns = defaultdict(list)
    ids = set()
    for term in catalog:
        if term['id'] in ids:
            raise ValueError('Duplicate definition ID')
        ids.add(term['id'])
        aliases = [term['term'], *(term.get('aliases') or [])]
        patterns[term['scope']].append((term['id'], [term_pattern(alias) for alias in aliases]))
    seen = set()
    scope_counts = Counter()
    term_counts = Counter()
    rejected = Counter()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    match_path = out / 'post_matches.jsonl'
    n_in_scope = 0
    n_matched_posts = 0
    with args.posts.open(encoding='utf-8') as source, match_path.open('w') as matched_out:
        for line in source:
            if not line.strip():
                continue
            post = json.loads(line)
            post_id = str(post['post_id'])
            if post_id in seen:
                raise ValueError('Duplicate post ID in snapshot: ' + post_id)
            seen.add(post_id)
            created = timestamp(post['created_utc'])
            if not timestamp(args.start_utc) <= created < timestamp(args.end_utc):
                rejected['outside_window'] += 1
                continue
            scope = post.get('scope') or post.get('subreddit')
            if scope not in patterns:
                rejected['outside_catalog_scope'] += 1
                continue
            title, body = post.get('title') or '', post.get('selftext') or ''
            if not isinstance(title, str) or not isinstance(body, str):
                raise ValueError('Non-text title/selftext: ' + post_id)
            if body.strip().lower() in {'[deleted]', '[removed]'} or title.strip().lower() in {'[deleted]', '[removed]'}:
                rejected['removed_or_deleted'] += 1
                continue
            text = title + '\n' + body
            term_ids = sorted(i for i, pats in patterns[scope] if any(p.search(text) for p in pats))
            matched_out.write(json.dumps({'post_id': post_id, 'scope': scope,
                                          'created_utc': post['created_utc'],
                                          'matched_definition_ids': term_ids},
                                         ensure_ascii=False, sort_keys=True) + '\n')
            n_in_scope += 1
            n_matched_posts += bool(term_ids)
            scope_counts[scope] += 1
            term_counts.update(term_ids)
    frequency = [{'id': x['id'], 'post_count': term_counts[x['id']]} for x in catalog if x.get('selectable', True)]
    (out / 'frequency.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in frequency))
    result = {'status': 'DEVELOPMENT_ONLY' if args.development else 'SOURCE_ONLY_IMPORT',
              'asserted_complete_stream': args.complete_stream,
              'frame_type': 'complete_community_stream' if args.complete_stream else 'partial_or_targeted',
              'posts_sha256': file_hash(args.posts), 'catalog_sha256': file_hash(args.catalog),
              'matches_sha256': file_hash(match_path),
              'communities_sha256': hashlib.sha256(json.dumps(sorted(scope_counts)).encode()).hexdigest(),
              'start_utc': args.start_utc, 'end_utc': args.end_utc,
              'n_input_posts': len(seen), 'n_in_window_scope_posts': n_in_scope,
              'n_posts_with_matched_definition': n_matched_posts,
              'n_terms_with_1plus_posts': sum(term_counts[x['id']] >= 1 for x in catalog),
              'n_terms_with_4plus_posts': sum(term_counts[x['id']] >= 4 for x in catalog),
              'scope_post_counts': dict(scope_counts), 'rejected': dict(rejected),
              'matcher': 'case-insensitive exact term/alias with word boundaries; one count per term per post',
              'no_raw_post_text_written': True}
    (out / 'source_frame.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'n_input_posts', 'n_in_window_scope_posts',
                                             'n_posts_with_matched_definition', 'n_terms_with_4plus_posts')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
