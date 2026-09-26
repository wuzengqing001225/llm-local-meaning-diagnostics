"""Small OpenAI-compatible client for the role-based private config.json."""
import json
import re
import time
import urllib.error
import urllib.request


def config_role(path, role):
    config = json.loads(path.read_text())
    roles = config.get('roles') or {}
    fallback = {'judge': 'reader', 'second_judge': 'draft',
                'test_draft': 'draft', 'mechanism_judge': 'judge'}
    spec = dict(config.get('defaults') or {})
    if role in fallback:
        parent = config_role(path, fallback[role])
        spec.update(parent)
    spec.update(roles.get(role) or {})
    for key in ('model', 'base_url', 'api_key'):
        if not isinstance(spec.get(key), str) or not spec[key].strip() or spec[key] in {
                '[key]', 'YOUR_API_KEY', 'PASTE_API_KEY_HERE', 'PASTE_KEY_HERE',
                'YOUR_GPT_KEY', 'YOUR_DEEPSEEK_KEY'}:
            raise ValueError(f'Missing {key} for {role} in private config.json')
    if spec['base_url'].startswith('http://') and config.get('allow_http') is not True:
        raise ValueError('HTTP endpoint requires allow_http=true in private config.json')
    return spec


def parse_json_object(content):
    value = content.strip()
    if value.startswith('```'):
        value = re.sub(r'^```(?:json)?\s*|\s*```$', '', value, flags=re.I | re.S).strip()
    for candidate in (value, value[value.find('{'):value.rfind('}') + 1]):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except (ValueError, TypeError):
            pass
    return None


def request_one(spec, payload):
    url = spec['base_url'].rstrip('/') + '/chat/completions'
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    request = urllib.request.Request(url, data=body, method='POST', headers={
        'Content-Type': 'application/json', 'Authorization': 'Bearer ' + spec['api_key']})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read())
            choice = data['choices'][0]
            content = choice['message'].get('content')
            finish = choice.get('finish_reason')
            if not isinstance(content, str) or not content.strip() or finish == 'length':
                raise RuntimeError('Empty or truncated response; rerun the same command to resume')
            return {'content': content, 'returned_model': data.get('model'),
                    'provider_response_id': data.get('id'), 'usage': data.get('usage'),
                    'finish_reason': finish}
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'HTTP {exc.code} for configured {spec["model"]}; key/body not logged') from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'Connection failed for {spec["model"]}; key not logged') from None
    raise RuntimeError('Model request failed after retries')
