"""Minimal chat-completion client for the drafting step (OpenAI-compatible endpoints) with a disk cache.

Configuration by environment variables:
  PD_DRAFT_MODEL     model name (required)
  PD_DRAFT_BASE_URL  e.g. https://api.openai.com/v1 or https://api.deepseek.com/v1  (required)
  PD_DRAFT_API_KEY   bearer token (required)
Use a drafter from a DIFFERENT model family than the reader you care about; a same-family drafter reproduces the reader's own misreads.
"""
import hashlib, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

class Cache:
    def __init__(self, path):
        self.path = path; self.d = {}
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for l in f:
                    try:
                        r = json.loads(l); self.d[r["k"]] = r["v"]
                    except Exception:
                        pass
    def get(self, k): return self.d.get(k)
    def put(self, k, v):
        self.d[k] = v
        if self.path:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"k": k, "v": v}, ensure_ascii=False) + "\n")

class ChatClient:
    def __init__(self, model, base_url, api_key, cache_path=None, concurrency=8, timeout=180):
        self.model, self.base_url, self.api_key = model, base_url.rstrip("/"), api_key
        self.cache = Cache(cache_path); self.concurrency = concurrency; self.timeout = timeout
    def _key(self, prompt, system, max_tokens, temperature):
        return hashlib.sha1(json.dumps([self.model, prompt, system, max_tokens, temperature]).encode()).hexdigest()
    def _one(self, prompt, system, max_tokens, temperature):
        msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        body = {"model": self.model, "messages": msgs, "max_tokens": max_tokens, "temperature": temperature}
        for attempt in range(4):
            req = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(body).encode("utf-8"),
                                         headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    o = json.loads(resp.read().decode("utf-8"))
                content = (o["choices"][0]["message"].get("content") or "").strip()
                if not content and max_tokens < 8192:  # reasoning-style model spent the budget on hidden tokens
                    body["max_tokens"] = max_tokens = max(4096, max_tokens * 8); continue
                return content
            except urllib.error.HTTPError as ex:
                detail = ex.read().decode("utf-8", "ignore")[:300]
                low = detail.lower()
                if ex.code == 400 and "max_completion_tokens" in low:
                    body["max_completion_tokens"] = body.pop("max_tokens"); continue
                if ex.code == 400 and "temperature" in low:
                    body.pop("temperature", None); continue
                if attempt == 3:
                    print(f"[pd.llm] HTTP {ex.code}: {detail}", file=sys.stderr); return ""
            except Exception as ex:  # network errors
                if attempt == 3:
                    print(f"[pd.llm] {ex}", file=sys.stderr); return ""
            time.sleep(2 * (attempt + 1))
        return ""
    def complete_many(self, prompts, system=None, max_tokens=600, temperature=0.0):
        keys = [self._key(p, system, max_tokens, temperature) for p in prompts]
        todo = [i for i, k in enumerate(keys) if self.cache.get(k) is None]
        with ThreadPoolExecutor(self.concurrency) as ex:
            for i, txt in zip(todo, ex.map(lambda i: self._one(prompts[i], system, max_tokens, temperature), todo)):
                self.cache.put(keys[i], txt)
        return [self.cache.get(k) for k in keys]

class MockClient:
    """Deterministic stand-in for tests and dry runs: writes a well-formed question whose correct option follows the definition."""
    def __init__(self, *a, **k): pass
    def complete_many(self, prompts, **k):
        out = []
        for p in prompts:
            term = p.split('the term "')[1].split('"')[0] if 'the term "' in p else "term"
            out.append(json.dumps({"q": f"In the sentence above, what follows from how '{term}' is used here?",
                                   "options": ["The document-specific consequence applies.", "The ordinary-meaning consequence applies.",
                                               "Neither applies.", "Both apply equally."], "answer": "A"}))
        return out

def client_from_env(mock=False, cache_path=None):
    if mock:
        return MockClient()
    model, base, key = os.environ.get("PD_DRAFT_MODEL"), os.environ.get("PD_DRAFT_BASE_URL"), os.environ.get("PD_DRAFT_API_KEY")
    if not (model and base and key):
        raise RuntimeError("set PD_DRAFT_MODEL, PD_DRAFT_BASE_URL and PD_DRAFT_API_KEY (or pass --mock for a dry run)")
    return ChatClient(model, base, key, cache_path=cache_path, concurrency=int(os.environ.get("PD_DRAFT_CONCURRENCY", "8")))
