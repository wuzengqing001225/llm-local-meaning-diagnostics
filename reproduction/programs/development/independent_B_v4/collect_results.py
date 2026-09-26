#!/usr/bin/env python3
"""Collect the actual code and selected run artifacts. Never include .env or unrelated files."""
from pathlib import Path
import argparse,hashlib,json,os,re,zipfile

SECRET_FIELDS={'api_key','apikey','authorization','access_token','refresh_token','password','secret'}
KEY_ENVS=['LLM_API_KEY','DRAFT_API_KEY','TEST_DRAFT_API_KEY','JUDGE_API_KEY','MECH_JUDGE_API_KEY','SECOND_JUDGE_API_KEY','LOCALRISK_READER_API_KEY']

def scrub(data,secrets):
    text=data.decode('utf-8');changed=False
    for secret in secrets:
        if secret and secret in text:text=text.replace(secret,'<REDACTED_API_KEY>');changed=True
    text,n=re.subn(r'(?i)Bearer\s+[A-Za-z0-9._~+/-]{12,}','Bearer <REDACTED>',text);changed|=bool(n)
    def walk(x):
        nonlocal changed
        if isinstance(x,dict):
            return {k:('<REDACTED>' if k.casefold() in SECRET_FIELDS and mark() else walk(v)) for k,v in x.items()}
        if isinstance(x,list):return [walk(v) for v in x]
        return x
    def mark():
        nonlocal changed
        changed=True;return True
    try:
        obj=json.loads(text);clean=walk(obj)
        if changed:text=json.dumps(clean,ensure_ascii=False,indent=2)+'\n'
    except ValueError:
        lines=[]
        for line in text.splitlines(keepends=True):
            try:
                obj=json.loads(line);old=changed;clean=walk(obj)
                if clean!=obj:line=json.dumps(clean,ensure_ascii=False)+'\n'
            except ValueError:pass
            lines.append(line)
        text=''.join(lines)
    return text.encode('utf-8') if changed else data,changed

def collect(run_dirs,out,code_dir=None,config_path=None):
    code=Path(code_dir or __file__).resolve().parent if code_dir is None else Path(code_dir).resolve()
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    secrets=[os.environ[k] for k in KEY_ENVS if os.environ.get(k)];records=[];status=[]
    config_files=[code/'config.json']
    if config_path:config_files.append(Path(config_path).resolve())
    def find_secrets(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key.casefold() in SECRET_FIELDS and isinstance(item,str) and item:secrets.append(item)
                else:find_secrets(item)
        elif isinstance(value,list):
            for item in value:find_secrets(item)
    for config_file in config_files:
        if config_file.exists():
            try:find_secrets(json.loads(config_file.read_text()))
            except (ValueError,UnicodeError):raise ValueError('Cannot safely read config for redaction. Fix JSON before collecting.') from None
    excluded={p.resolve() for p in config_files}
    def write(z,path,name):
        if path.resolve() in excluded or path.name=='config.json' or path.name.endswith('.local.json'):return
        raw=path.read_bytes();clean,redacted=scrub(raw,secrets)
        z.writestr(name,clean);records.append({'path':name,'source_sha256':hashlib.sha256(raw).hexdigest(),'archive_sha256':hashlib.sha256(clean).hexdigest(),'redacted':redacted})
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(code.rglob('*')):
            rel=p.relative_to(code)
            if p.is_symlink() or not p.is_file() or '__pycache__' in p.parts:continue
            allowed=(len(rel.parts)==1 and (p.suffix=='.py' or p.name in ['README.md','README_advanced.md','requirements.txt'])) or (rel.parts[0] in ['localrisk','tests'] and p.suffix=='.py') or (rel.parts[0]=='configs' and p.suffix=='.json')
            if allowed:write(z,p,'code/'+str(rel))
        for i,run in enumerate(run_dirs,1):
            run=Path(run).resolve()
            if not run.is_dir():raise ValueError('Run folder does not exist: '+str(run))
            root=f'runs/{i:02d}-{run.name}'
            for p in sorted(run.rglob('*')):
                if p.is_symlink() or not p.is_file() or p.name.startswith('.env') or p.suffix not in ['.json','.jsonl','.md','.log','.txt']:continue
                if any(part.startswith('.stage-') for part in p.relative_to(run).parts):continue
                write(z,p,root+'/'+str(p.relative_to(run)))
            evaluation=run/'evaluation' if (run/'evaluation').is_dir() else run
            status.append({'archive_root':root,'has_study_status':(run/'study_status.json').exists(),'has_summary':(evaluation/'summary.json').exists(),'has_scores':(run/'_study/scores_A.jsonl').exists() or (evaluation/'_work/scores_A.jsonl').exists(),'has_budget_predictions':(evaluation/'_work/predictions.jsonl').exists(),'has_mechanism_predictions':(evaluation/'_work/mechanism_predictions.jsonl').exists()})
        z.writestr('return_manifest.json',json.dumps({'runs':status,'files':records,'redacted_files':sum(r['redacted'] for r in records),
            'note':'Unchanged bytes preserve original manifests. Redacted files intentionally have different hashes. Custom hardcoded credentials not present in the named environment variables may require manual inspection.'},ensure_ascii=False,indent=2))
    return {'archive':str(out),'files':len(records),'redacted_files':sum(r['redacted'] for r in records),'runs':status}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='append',required=True);p.add_argument('--out',default='return_bundle.zip');p.add_argument('--code-dir');p.add_argument('--config',help='Custom local credential JSON, if used')
    a=p.parse_args();print(json.dumps(collect(a.run,a.out,a.code_dir,a.config),ensure_ascii=False,indent=2))
