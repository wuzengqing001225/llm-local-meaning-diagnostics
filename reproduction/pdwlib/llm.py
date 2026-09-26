# -*- coding: utf-8 -*-
"""
LLM client abstraction (three backends + disk cache).

  HostClient    Calls via Claude Science's host.llm (used when running scripts in the python kernel).
                Requires pdwlib.llm.set_host(host) first; LLM_BACKEND=host.
  OpenAIClient  OpenAI-compatible /chat/completions (DeepSeek/Qwen/Moonshot, etc). On empty content + reasoning_content,
                automatically enlarges max_tokens and retries once; LLM_EXTRA_BODY can pass provider-specific JSON fields.
  MockClient    Deterministic pseudo-random reader (dry run).

Unified interface:
  client.complete(prompt, system=None, max_tokens=64, temperature=0.0) -> str
  client.complete_many([{prompt, system, max_tokens, temperature}, ...]) -> [str, ...]   # batched concurrency
Cache keyed by content hash of (model, system, prompt, max_tokens, temperature); empty answers are not cached.
"""
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

_HOST = None


def set_host(host):
    """Inject the host object (providing host.llm) inside the python kernel."""
    global _HOST
    _HOST = host


class _Cache:
    def __init__(self, path):
        self.path = path
        self.mem = {}
        if path and os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                try:
                    o = json.loads(line)
                    if o.get("text"):
                        self.mem[o["key"]] = o["text"]
                except Exception:  # noqa
                    pass
        self._fh = open(path, "a", encoding="utf-8") if path else None

    def get(self, key):
        return self.mem.get(key)

    def put(self, key, text):
        if not text:
            return
        self.mem[key] = text
        if self._fh:
            self._fh.write(json.dumps({"key": key, "text": text}, ensure_ascii=False) + "\n")
            self._fh.flush()


class BaseClient:
    name = "base"

    def __init__(self, model, cache_path=None):
        self.model = model
        self.cache = _Cache(cache_path)
        self.n_calls = 0
        self.n_cache_hits = 0

    def _key(self, prompt, system, max_tokens, temperature):
        h = hashlib.sha256(json.dumps([self.name, self.model, system or "", prompt, max_tokens, temperature],
                                      ensure_ascii=False).encode("utf-8")).hexdigest()
        return h

    def complete(self, prompt, system=None, max_tokens=64, temperature=0.0):
        return self.complete_many([dict(prompt=prompt, system=system, max_tokens=max_tokens,
                                        temperature=temperature)])[0]

    def complete_many(self, reqs):
        reqs = [dict(prompt=r["prompt"], system=r.get("system"), max_tokens=r.get("max_tokens", 64),
                     temperature=r.get("temperature", 0.0)) for r in reqs]
        keys = [self._key(r["prompt"], r["system"], r["max_tokens"], r["temperature"]) for r in reqs]
        out = [self.cache.get(k) for k in keys]
        todo = [i for i, v in enumerate(out) if v is None]
        self.n_cache_hits += len(reqs) - len(todo)
        if todo:
            texts = self._run([reqs[i] for i in todo])
            self.n_calls += len(todo)
            for i, t in zip(todo, texts):
                t = (t or "").strip()
                out[i] = t
                self.cache.put(keys[i], t)
        return out

    def _run(self, reqs):  # -> list[str]
        raise NotImplementedError


class MockClient(BaseClient):
    name = "mock"

    def __init__(self, model="mock", cache_path=None, seed=0):
        super().__init__(model, None)
        self.seed = seed

    def _run(self, reqs):
        outs = []
        for r in reqs:
            rng = random.Random(hashlib.md5((r["prompt"] + str(self.seed)).encode()).hexdigest())
            p = r["prompt"]
            if "ANSWER_LETTER" in p:
                outs.append(rng.choice("ABCD"))
            elif "SAME_OR_DIFFERENT" in p:
                outs.append(rng.choice(["SAME", "DIFFERENT"]))
            elif "JUDGE_DEFINITION" in p:
                outs.append(rng.choice(["CORRECT", "INCORRECT"]))
            elif "TIER_JSON" in p:
                outs.append(json.dumps({"tier": rng.choice(["none", "narrower", "shifted", "opposite", "unknown"])}))
            elif "PRIOR_MEANING" in p:
                outs.append(rng.choice(["UNKNOWN", "a generic term meaning something ordinary"]))
            elif "DRAFT_GLOSS" in p:
                outs.append("a mock definition drafted from the usages")
            else:
                outs.append(" ".join(rng.choice(["the", "of", "and", "price", "risk", "day", "book"])
                                     for _ in range(4)))
        return outs


class HostClient(BaseClient):
    name = "host"

    def __init__(self, model, cache_path=None, max_concurrency=8):
        super().__init__(model, cache_path)
        self.max_concurrency = max_concurrency
        if _HOST is None:
            raise RuntimeError("HostClient requires calling pdwlib.llm.set_host(host) first")

    def _run(self, reqs):
        batch = []
        for r in reqs:
            # Note: some Claude models have deprecated the temperature parameter; the host backend omits it (sampling defaults to the model's default)
            # Readers run in non-reasoning mode (silent misreading of the definition means answering without deliberation); LLM_THINKING=adaptive can change this
            d = {"prompt": r["prompt"], "max_tokens": r["max_tokens"], "model": self.model,
                 "thinking": {"type": os.environ.get("LLM_THINKING", "disabled")}}
            if r["system"]:
                d["system"] = r["system"]
            batch.append(d)
        # host.llm has a per-call batch limit of 512; chunk by 100
        res = []
        for i in range(0, len(batch), 100):
            res.extend(_HOST.llm(batch[i:i + 100], max_concurrency=self.max_concurrency))
        texts = []
        retry_idx = []
        for i, x in enumerate(res):
            if isinstance(x, dict) and x.get("text") is not None and not x.get("error"):
                texts.append(x["text"])
            else:
                texts.append("")
                retry_idx.append(i)
        if retry_idx:  # one serial retry pass
            time.sleep(2)
            for i in retry_idx:
                try:
                    x = _HOST.llm(batch[i])
                    texts[i] = x.get("text") or ""
                except Exception as ex:  # noqa
                    print(f"[host.llm] retry failed: {str(ex)[:120]}", file=sys.stderr)
        return texts


class OpenAIClient(BaseClient):
    name = "openai"

    def __init__(self, model, base_url, api_key, cache_path=None, extra_body=None):
        super().__init__(model, cache_path)
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.extra_body = extra_body or {}
        self._warned = False

    def _one(self, r, max_tokens):
        msgs = ([{"role": "system", "content": r["system"]}] if r["system"] else []) + \
            [{"role": "user", "content": r["prompt"]}]
        for attempt in range(4):
            body = dict(model=self.model, messages=msgs)
            # Newer OpenAI reasoning models require max_completion_tokens and reject temperature; switch automatically on first 400 and retry
            # For reasoning models (the ones requiring max_completion_tokens), thinking tokens count against the output budget: add a 2048 thinking margin by default
            budget = max_tokens + (2048 if getattr(self, "use_mct", False) else 0)
            body["max_completion_tokens" if getattr(self, "use_mct", False) else "max_tokens"] = budget
            if not getattr(self, "no_temp", False):
                body["temperature"] = r["temperature"]
            body.update(self.extra_body)
            req = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(body).encode("utf-8"),
                                         headers={"Content-Type": "application/json",
                                                  "Authorization": f"Bearer {self.api_key}"})
            try:
                with urllib.request.urlopen(req, timeout=180) as resp:
                    o = json.loads(resp.read().decode("utf-8"))
                ch = o["choices"][0]
                msg = ch["message"]
                content = (msg.get("content") or "").strip()
                reasoning_used = (msg.get("reasoning_content") or msg.get("reasoning") or ch.get("finish_reason") == "length"
                                  or ((o.get("usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens"))
                if not content and max_tokens < 8192:  # empty answer: whether or not a visible reasoning field is present, enlarge the budget and retry once
                    if not self._warned and reasoning_used:
                        print("[warn] reasoning model: content is empty, reasoning filled the budget; enlarging max_tokens and retrying."
                              "Consider disabling thinking or switching to a non-reasoning model (silent misreading of the definition means answering without deliberation).", file=sys.stderr)
                        self._warned = True
                    return self._one(r, max(4096, max_tokens * 8))
                return content
            except urllib.error.HTTPError as ex:
                detail = ""
                try:
                    detail = ex.read().decode("utf-8", "ignore")[:400]
                except Exception:  # noqa
                    pass
                if ex.code == 400:
                    low = detail.lower()
                    if ("output limit" in low or "higher max_tokens" in low or "max_tokens or model output" in low) and max_tokens < 16384:
                        # reasoning filled the budget: enlarge and retry (OpenAI returns 400 rather than an empty answer for this)
                        if not self._warned:
                            print(f"[warn] {self.model}: thinking tokens filled the output budget, enlarging budget and retrying (this model cannot disable thinking; flag results when used as a reader)", file=sys.stderr)
                            self._warned = True
                        return self._one(r, max(4096, max_tokens * 8))
                    if "max_completion_tokens" in low and not getattr(self, "use_mct", False):
                        self.use_mct = True
                        print(f"[openai] {self.model}: switching to max_completion_tokens", file=sys.stderr); continue
                    if "temperature" in low and not getattr(self, "no_temp", False):
                        self.no_temp = True
                        print(f"[openai] {self.model}: this model does not accept temperature, removed", file=sys.stderr); continue
                    for k in list(self.extra_body):
                        if k.lower() in low:
                            print(f"[openai] {self.model}: this model does not accept extra_body field {k!r}, removed", file=sys.stderr)
                            self.extra_body.pop(k); break
                    else:
                        raise RuntimeError(f"[openai] {self.model} HTTP 400 (not retryable): {detail or ex.reason}")
                    continue
                if attempt == 3:
                    print(f"[openai] failed: HTTP {ex.code} {detail[:200]}", file=sys.stderr)
                    return ""
                time.sleep(2 * (attempt + 1))
            except Exception as ex:  # noqa
                if attempt == 3:
                    print(f"[openai] failed: {str(ex)[:160]}", file=sys.stderr)
                    return ""
                time.sleep(2 * (attempt + 1))

    def _run(self, reqs):
        return [self._one(r, r["max_tokens"]) for r in reqs]


def client_from_env(prefix, mock=False, cache_path=None):
    """prefix in {LLM, DRAFT, JUDGE}; falls back to LLM_* by default. Uses HostClient when LLM_BACKEND=host."""
    backend = os.environ.get(f"{prefix}_BACKEND") or os.environ.get("LLM_BACKEND", "openai")
    if mock or backend == "mock":
        return MockClient(cache_path=None)
    model = os.environ.get(f"{prefix}_MODEL") or os.environ.get("LLM_MODEL")
    if not model:
        raise RuntimeError(f"{prefix}_MODEL / LLM_MODEL not set")
    if backend == "host":
        return HostClient(model, cache_path=cache_path,
                          max_concurrency=int(os.environ.get("LLM_CONCURRENCY", "8")))
    base = os.environ.get(f"{prefix}_BASE_URL") or os.environ.get("LLM_BASE_URL")
    key = os.environ.get(f"{prefix}_API_KEY") or os.environ.get("LLM_API_KEY")
    extra = os.environ.get(f"{prefix}_EXTRA_BODY") or os.environ.get("LLM_EXTRA_BODY")
    if not base or not key:
        raise RuntimeError(f"{prefix}_BASE_URL/{prefix}_API_KEY (or LLM_*) not set")
    return OpenAIClient(model, base, key, cache_path=cache_path, extra_body=json.loads(extra) if extra else None)