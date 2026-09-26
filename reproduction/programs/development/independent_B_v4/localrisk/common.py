from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re,os,tempfile

class InvalidExperiment(ValueError):
    pass

def require(ok,message):
    if not ok: raise InvalidExperiment(message)

def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def digest(obj): return hashlib.sha256(canonical(obj).encode()).hexdigest()
def filehash(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def read_json(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def read_rows(path):
    return [json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]
def write_json(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    # Atomic replacement protects manifests and summaries from interrupted writes.
    fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.'+p.name)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
        os.replace(tmp,p)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def write_rows(path,rows):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(''.join(canonical(r)+'\n' for r in rows),encoding='utf-8')
def unique(rows,key):
    ids=[r[key] for r in rows];require(len(ids)==len(set(ids)),f'Duplicate {key}')
    return {r[key]:r for r in rows}
def norm(s): return ' '.join(re.findall(r'\w+',s.casefold()))
def contains(term,text):
    return bool(re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text,re.I))
def choice(answer,n):
    require(isinstance(answer,str) and answer in 'ABCDEFGH'[:n],'Invalid answer letter')
    return ord(answer)-65

def validate_corpus(c):
    require(c.get('schema_version')==1,'Unsupported corpus schema')
    docs=unique(c['documents'],'doc_id');defs=unique(c['definitions'],'definition_id');ps=unique(c['passages'],'passage_id')
    for d in defs.values():
        require(d['doc_id'] in docs and d['text'].strip() and d['term'].strip(),'Invalid definition')
    for p in ps.values():
        require(p['doc_id'] in docs and p['text'].strip(),'Invalid passage')
        require(len(p['definition_ids'])==len(set(p['definition_ids'])),'Duplicate candidate definition')
        for i in p['definition_ids']:
            require(i in defs and defs[i]['doc_id']==p['doc_id'],'Cross-document definition')
            require(contains(defs[i]['term'],p['text']),'Candidate term absent from passage')
    return docs,defs,ps

def parse_answer(text,n):
    """Strict parsing; never select the first arbitrary letter in a rationale."""
    t=text.strip()
    try:
        obj=json.loads(t)
        if isinstance(obj,dict) and set(obj)=={'answer'}:t=obj['answer']
    except (ValueError,TypeError):pass
    return t if isinstance(t,str) and t in 'ABCDEFGH'[:n] else None

SCOPE='Definitions apply only to the supplied document. Unlisted words keep their ordinary meaning.'
def definition_block(defs):
    if not defs:return ''
    return SCOPE+'\nLocal definitions:\n'+'\n'.join('- '+d['term']+': '+d['text'] for d in sorted(defs,key=lambda d:d['definition_id']))+'\n\n'

def public_prompt(task,passages,definitions=()):
    """Allowlisted fields only. Gold answers/rationales cannot reach a reader."""
    ctx='\n\n'.join(p['text'] for p in passages)
    opts='\n'.join(f'{chr(65+i)}. {s}' for i,s in enumerate(task['options']))
    return (definition_block(definitions)+'Source passages:\n'+ctx+'\n\nQuestion:\n'+task['question']+'\n'+opts+'\nAnswer with one option letter only.\nAnswer:')


def quote_present(quote,parts):
    """Allow typography/whitespace differences only, never dropped punctuation or words."""
    import unicodedata
    def clean(text):
        text=unicodedata.normalize('NFKC',text).translate(str.maketrans({'“':'"','”':'"','‘':"'",'’':"'"}))
        return ' '.join(text.split())
    if not isinstance(quote,str) or len(re.findall(r'\w+',quote))<2:return False
    q=clean(quote)
    return bool(q) and any(q in clean(s) for s in parts)
