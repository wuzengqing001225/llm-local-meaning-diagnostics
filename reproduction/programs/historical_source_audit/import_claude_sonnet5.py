#!/usr/bin/env python3
"""Validate and import the Sonnet 5 blind audit without reading old keys."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
BLIND=HERE/'blind_review_packet'
DEST=HERE/'model_stage_private'

def sha(s):return hashlib.sha256(s.encode()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('zip',type=Path);args=p.parse_args()
    import run_model_stage as common
    source=(BLIND/'selected_questions.jsonl').read_text()
    items={x['audit_id']:x for x in (json.loads(s) for s in source.splitlines())}
    with zipfile.ZipFile(args.zip) as z:
        names=z.namelist()
        expected={'results_claude/manifest.json'}|{f'results_claude/{aid}_claude.json' for aid in items}
        if set(names)!=expected or z.testzip() is not None:raise ValueError('ZIP content or CRC mismatch')
        manifest=json.loads(z.read('results_claude/manifest.json'))
        if manifest.get('source_question_sha256')!=hashlib.sha256(source.encode()).hexdigest():
            raise ValueError('Frozen question file differs')
        if manifest.get('system_sha256')!=sha(common.SYSTEM):raise ValueError('System prompt differs')
        if manifest.get('model')!='claude-sonnet-5' or manifest.get('thinking')!='disabled':
            raise ValueError('Unexpected model or thinking setting')
        if manifest.get('max_tokens')!=1000:raise ValueError('Unexpected token limit')
        rows=[]
        for aid,item in items.items():
            row=json.loads(z.read(f'results_claude/{aid}_claude.json'))
            material,omitted=common.source_material(item)
            if row.get('audit_id')!=aid or row.get('model_role')!='claude':raise ValueError('ID/role mismatch')
            if row.get('requested_model')!='claude-sonnet-5' or row.get('returned_model')!='claude-sonnet-5':
                raise ValueError('Model mismatch at '+aid)
            if row.get('source_material_sha256')!=sha(material) or row.get('source_excerpted_or_omitted_count')!=omitted:
                raise ValueError('Source excerpt differs at '+aid)
            if row.get('answer') not in {'A','B','C','D','UNDETERMINED'}:
                raise ValueError('Invalid answer at '+aid)
            if not isinstance(row.get('unique_answer'),bool) or not isinstance(row.get('source_sufficient'),bool):
                raise ValueError('Missing quality flags at '+aid)
            if row.get('finish_reason') not in {'end_turn','stop'}:
                raise ValueError('Truncated or nonfinal result at '+aid)
            settings=row.get('settings') or {}
            if settings.get('max_tokens')!=1000 or settings.get('thinking')!='disabled':
                raise ValueError('Setting mismatch at '+aid)
            if not str(row.get('raw_response') or '').strip():raise ValueError('Empty answer at '+aid)
            rows.append(row)
    DEST.mkdir(exist_ok=True)
    for row in rows:
        dest=DEST/f"{row['audit_id']}_claude.json"
        data=json.dumps(row,ensure_ascii=False,indent=2)+'\n'
        if dest.exists() and dest.read_text()!=data:raise ValueError('Existing result differs: '+dest.name)
        dest.write_text(data)
    (DEST/'claude_sonnet5_import_manifest.json').write_text(json.dumps({
        'zip_sha256':hashlib.sha256(args.zip.read_bytes()).hexdigest(),
        'item_count':len(rows),'model':'claude-sonnet-5','temperature':'provider default',
        'thinking':'disabled','max_tokens':1000,'provider_response_ids_present':False,
        'limitation':'Model-only screening; long documents excerpted; no human gold decision.'},ensure_ascii=False,indent=2)+'\n')
    print('Validated and imported',len(rows),'Sonnet 5 results')

if __name__=='__main__':main()
