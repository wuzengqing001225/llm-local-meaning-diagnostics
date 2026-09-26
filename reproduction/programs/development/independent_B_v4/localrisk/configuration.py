"""Load local credentials without serializing them into experiment artifacts."""
import json, os
from pathlib import Path
from contextlib import contextmanager
from urllib.parse import urlparse
from .common import require

ROLES = {'reader':'LLM', 'draft':'DRAFT', 'test_draft':'TEST_DRAFT',
         'judge':'JUDGE', 'second_judge':'SECOND_JUDGE', 'mechanism_judge':'MECH_JUDGE'}
DEFAULT_MODELS = {'reader':'gpt-5.6-terra', 'draft':'deepseek-flash'}
FALLBACK = {'test_draft':'draft', 'judge':'reader', 'second_judge':'draft', 'mechanism_judge':'judge'}
FIELDS = {'base_url','model','api_key','extra_body'}

def read_settings(path):
    try:
        data=json.loads(Path(path).read_text(encoding='utf-8'))
    except (ValueError, UnicodeError):
        raise ValueError('Invalid config JSON. Check commas and double quotes. Contents omitted to protect keys.') from None
    require(isinstance(data,dict),'Config must be a JSON object.')
    require(not (set(data)-{'defaults','roles','allow_http'}),'Unknown top-level config field.')
    require(type(data.get('allow_http',False)) is bool,'allow_http must be true or false.')
    common=data.get('defaults',{}); roles=data.get('roles',{})
    require(isinstance(common,dict) and not(set(common)-FIELDS),'Invalid defaults fields.')
    require(isinstance(roles,dict) and not(set(roles)-set(ROLES)),'Unknown role in config.')
    resolved={}
    for role,prefix in ROLES.items():
        overrides=roles.get(role,{})
        require(isinstance(overrides,dict) and not(set(overrides)-FIELDS),'Invalid fields for role '+role)
        value=dict(resolved[FALLBACK[role]]) if role in FALLBACK else dict(common)
        if role in DEFAULT_MODELS:value.setdefault('model',DEFAULT_MODELS[role])
        value.update(overrides)
        for field in ['base_url','model','api_key']:
            require(isinstance(value.get(field),str) and bool(value[field].strip()),role+': missing '+field)
            value[field]=value[field].strip()
        require(value['api_key'] not in ['PASTE_API_KEY_HERE','YOUR_API_KEY','[key]'],role+': fill in api_key in config.json.')
        url=urlparse(value['base_url'])
        require(url.scheme in ['http','https'] and bool(url.hostname) and not url.username and not url.password and not url.query and not url.fragment and not any(ch.isspace() for ch in value['base_url']),role+': base_url must be a plain HTTP(S) URL, without Markdown, credentials or query parameters.')
        require(isinstance(value.get('extra_body',{}),dict),role+': extra_body must be an object.')
        resolved[role]=value
    return resolved,data.get('allow_http',False)

@contextmanager
def configured(args):
    if getattr(args,'smoke',False) or getattr(args,'env',False):
        yield
        return
    path=getattr(args,'config',None)
    if path is None:
        candidate=Path(__file__).resolve().parent.parent/'config.json'
        if not candidate.exists():
            yield
            return
        path=candidate
    resolved,allow_http=read_settings(path)
    names=[prefix+'_'+field.upper() for prefix in ROLES.values() for field in FIELDS]
    previous={name:os.environ.get(name) for name in names}
    previous_http=args.allow_http
    try:
        for name in names:os.environ.pop(name,None)
        for role,values in resolved.items():
            for field,value in values.items():
                os.environ[ROLES[role]+'_'+field.upper()]=json.dumps(value) if field=='extra_body' else value
        args.allow_http=args.allow_http or allow_http
        yield
    finally:
        args.allow_http=previous_http
        for name,value in previous.items():
            if value is None:os.environ.pop(name,None)
            else:os.environ[name]=value
