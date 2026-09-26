#!/usr/bin/env python3
"""Attach exact dependency definitions from the same source contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import re

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--contracts',type=Path,required=True,help='Directory of extracted original contract texts')
    a=p.parse_args()
    if (a.root/'reader_results.jsonl').exists():raise ValueError('Use a fresh pilot directory after reader outcomes exist')
    rules=[json.loads(x) for x in (a.root/'seed_frame/rules.jsonl').read_text().splitlines()]
    files={108:('03_ci108.txt',['Affiliate','Person']),38:('26_ci38.txt',['Product Updates','Products'])}
    for r in rules:
        deps=[]
        if r['contract_index'] in files:
            filename,terms=files[r['contract_index']];s=(a.contracts/filename).read_text()
            for term in terms:
                m=re.search(r'\d+\.\d+\s+["“]'+re.escape(term)+r'["”].*?(?=\d+\.\d+\s+["“])',s,re.S)
                if not m:raise ValueError('Missing definition: '+term)
                q=m.group(0).strip()
                if r['contract_index']==108:q=re.split(r'\s+1\s+Source:',q)[0].strip()
                deps.append(q)
        r['supporting_source_quotes']=deps
        r['rule_quote']=r['term']+': '+r['source_quote']+ ('\n'+'\n'.join(deps) if deps else '')
        r['note_sha256']=hashlib.sha256(r['rule_quote'].encode()).hexdigest()
    (a.root/'rules_with_dependencies.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rules))

if __name__=='__main__':main()
