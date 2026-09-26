"""Small shared API helpers, vendored from the prior development runner."""
import json,re,time,urllib.request,urllib.error
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def config_role(config, role):
    raw = json.loads(config.read_text())
    roles = raw.get('roles') or {}
    fallback = {'judge': 'reader', 'second_judge': 'draft',
                'test_draft': 'draft', 'mechanism_judge': 'judge'}
    spec = dict(raw.get('defaults') or {})
    if role in fallback:
        spec.update(config_role(config, fallback[role]))
    spec.update(roles[role])
    for key in ('model', 'base_url', 'api_key'):
        if not isinstance(spec.get(key), str) or not spec[key].strip() or spec[key] in {'[key]', 'YOUR_API_KEY', 'PASTE_API_KEY_HERE'}:
            raise ValueError(f'Role {role} needs a real {key} in config.json')
    return spec

def prompt(item, rule=None):
    opts = '\n'.join(f'{c}. {x}' for c, x in zip('AB', item['options']))
    note = '' if rule is None else (
        f'Local definition for this contract only:\n{item["term"]}: {rule}\n\n'
    )
    return note + item['question'] + '\n' + opts + '\nAnswer with A or B only.'

def parse_answer(content):
    value = content.strip()
    try:
        obj = json.loads(value)
        if isinstance(obj, dict) and isinstance(obj.get('answer'), str):
            value = obj['answer'].strip()
    except ValueError:
        pass
    if value in {'A', 'B'}:
        return value
    match = re.fullmatch(r'(?:Answer\s*:\s*)?([AB])[.\s]*', value, re.I)
    return match.group(1).upper() if match else None

def request_one(spec, payload):
    url = spec['base_url'].rstrip('/') + '/chat/completions'
    request = urllib.request.Request(
        url, data=canonical(payload).encode(), method='POST',
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + spec['api_key']},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = json.loads(response.read())
            choice = raw['choices'][0]
            content = choice['message'].get('content')
            finish = choice.get('finish_reason')
            if not isinstance(content, str) or not content.strip() or finish == 'length':
                raise RuntimeError(f'Empty/truncated response, finish_reason={finish}; rerun to resume')
            return {
                'content': content, 'prediction': parse_answer(content),
                'returned_model': raw.get('model'), 'provider_response_id': raw.get('id'),
                'usage': raw.get('usage'), 'finish_reason': finish,
            }
        except urllib.error.HTTPError as e:
            if e.code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'HTTP {e.code} for configured model {spec["model"]}; no key or response body logged') from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'Connection failed for configured model {spec["model"]}; no key logged') from None
    raise RuntimeError('Request failed after retries')

def parse_json_object(content):
    s = content.strip()
    try:
        x = json.loads(s)
        if isinstance(x, dict):
            return x
    except ValueError:
        pass
    if s.startswith('```'):
        s = re.sub(r'^```(?:json)?\s*|\s*```$', '', s, flags=re.I | re.S)
        try:
            x = json.loads(s)
            if isinstance(x, dict):
                return x
        except ValueError:
            pass
    start = s.find('{')
    end = s.rfind('}')
    if start >= 0 and end > start:
        try:
            x = json.loads(s[start:end + 1])
            if isinstance(x, dict):
                return x
        except ValueError:
            pass
    return None
