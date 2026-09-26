#!/usr/bin/env python3
"""Build a credential-free, portable ZIP of this folder."""
import hashlib
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZIP = HERE.parent / 'shared_definition_library_runner_20260925.zip'
SKIP_DIRS = {'__pycache__', 'results', 'data', '.git'}
SKIP_FILES = {'config.json', 'MANIFEST.json', '.DS_Store'}


def source_files():
    return sorted(p for p in HERE.rglob('*') if p.is_file()
                  and not (set(p.relative_to(HERE).parts) & SKIP_DIRS)
                  and p.name not in SKIP_FILES and p.suffix != '.zip')


def main():
    example = json.loads((HERE / 'config.example.json').read_text())
    if any(role.get('api_key') != 'PASTE_KEY_HERE' for role in example['roles'].values()):
        raise RuntimeError('config.example.json unexpectedly contains a non-placeholder key')
    files = source_files()
    manifest = {'package': 'shared_definition_library_runner',
                'status': 'PROGRAM_ONLY_REQUIRES_SOURCE_CHECKED_DATA_AND_AUTHORIZED_F_B',
                'contains_private_api_keys': False,
                'contains_reddit_post_text': False,
                'files': {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    manifest_path = HERE / 'MANIFEST.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    with zipfile.ZipFile(ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in [*files, manifest_path]:
            archive.write(path, 'shared_definition_library_runner/' + str(path.relative_to(HERE)))
    print('Built', ZIP, 'files', len(files) + 1, 'bytes', ZIP.stat().st_size)


if __name__ == '__main__':
    main()
