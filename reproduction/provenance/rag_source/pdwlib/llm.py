# -*- coding: utf-8 -*-
"""
LLM 客户端抽象（三种后端 + 磁盘缓存）。

  HostClient    通过 Claude Science 的 host.llm 调用（在 python 内核里运行脚本时使用）。
                需先 pdwlib.llm.set_host(host)；LLM_BACKEND=host。
  OpenAIClient  OpenAI 兼容 /chat/completions（DeepSeek/Qwen/Moonshot 等）。空 content + reasoning_content
                时自动放大 max_tokens 重试一次；LLM_EXTRA_BODY 可传 provider 特有 JSON 字段。
  MockClient    确定性伪随机读者（干跑）。

统一接口：
  client.complete(prompt, system=None, max_tokens=64, temperature=0.0) -> str
  client.complete_many([{prompt, system, max_tokens, temperature}, ...]) -> [str, ...]   # 批量并发
缓存按 (model, system, prompt, max_tokens, temperature) 的内容哈希；空回答不缓存。
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
    """在 python 内核中注入 host 对象（提供 host.llm）。"""
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
                     temperature=r.get("temperature", 0.0), seed=r.get("seed"), logprobs=r.get("logprobs")) for r in reqs]
        keys = [self._key(r["prompt"], ((r["system"] or "") + f"|seed={r['seed']}|lp={r['logprobs']}") if (r["seed"] is not None or r["logprobs"]) else r["system"],
                          r["max_tokens"], r["temperature"]) for r in reqs]
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
            elif '"verdict"' in p and "FAITHFUL" in p:
                outs.append(json.dumps({"verdict": rng.choice(["FAITHFUL", "MISREAD", "VAGUE"]), "reason": "mock"}))
            elif "Write ONE multiple-choice question" in p or "multiple-choice question" in p and "Output JSON only" in p:
                outs.append(json.dumps({"q": "In this note, what does the flagged step imply?",
                                        "options": ["mock A", "mock B", "mock C", "mock D"], "answer": rng.choice("ABCD")}))
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
            raise RuntimeError("HostClient 需要先调用 pdwlib.llm.set_host(host)")

    def _run(self, reqs):
        batch = []
        for r in reqs:
            # 注：部分 Claude 模型已弃用 temperature 参数，host 后端不传（采样为模型默认）
            # 读者以非推理模式运行（静默误读的定义即不经思考作答）；LLM_THINKING=adaptive 可改
            d = {"prompt": r["prompt"], "max_tokens": r["max_tokens"], "model": self.model,
                 "thinking": {"type": os.environ.get("LLM_THINKING", "disabled")}}
            if r["system"]:
                d["system"] = r["system"]
            batch.append(d)
        # host.llm 单次批量上限 512；按 100 分块
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
        if retry_idx:  # 一次串行重试
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
            # 新版 OpenAI 推理模型要求 max_completion_tokens、且不接受 temperature；首次 400 时自动切换并重试
            # 推理型模型（需要 max_completion_tokens 的那类）思考 token 计入输出预算：默认加 2048 的思考余量
            budget = max_tokens + (2048 if getattr(self, "use_mct", False) else 0)
            body["max_completion_tokens" if getattr(self, "use_mct", False) else "max_tokens"] = budget
            if not getattr(self, "no_temp", False):
                body["temperature"] = r["temperature"]
            if r.get("seed") is not None:
                body["seed"] = int(r["seed"])
            if r.get("logprobs"):
                body["logprobs"] = True; body["top_logprobs"] = min(20, int(r["logprobs"]))
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
                if r.get("logprobs"):
                    try:
                        tl = ch["logprobs"]["content"][0]["top_logprobs"]
                        return json.dumps({t["token"]: t["logprob"] for t in tl})
                    except Exception:  # noqa
                        pass  # 服务端没回 logprobs：退回字母内容
                reasoning_used = (msg.get("reasoning_content") or msg.get("reasoning") or ch.get("finish_reason") == "length"
                                  or ((o.get("usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens"))
                if not content and max_tokens < 8192:  # 空回答：无论是否可见 reasoning 字段，都放大预算重试一次
                    if not self._warned and reasoning_used:
                        print("[warn] 推理型模型：content 为空、reasoning 占满预算；放大 max_tokens 重试。"
                              "建议关闭思考或改用非推理模型（静默误读的定义即不经思考作答）。", file=sys.stderr)
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
                        # 推理占满预算：放大重试（OpenAI 对此返回 400 而不是空回答）
                        if not self._warned:
                            print(f"[warn] {self.model}: 思考 token 占满输出预算，放大预算重试（该模型关不掉思考，作为读者时结果需标注）", file=sys.stderr)
                            self._warned = True
                        return self._one(r, max(4096, max_tokens * 8))
                    if "max_completion_tokens" in low and not getattr(self, "use_mct", False):
                        self.use_mct = True
                        print(f"[openai] {self.model}: 改用 max_completion_tokens", file=sys.stderr); continue
                    if "temperature" in low and not getattr(self, "no_temp", False):
                        self.no_temp = True
                        print(f"[openai] {self.model}: 该模型不接受 temperature，已去掉", file=sys.stderr); continue
                    for k in list(self.extra_body):
                        if k.lower() in low:
                            print(f"[openai] {self.model}: 该模型不接受 extra_body 字段 {k!r}，已去掉", file=sys.stderr)
                            self.extra_body.pop(k); break
                    else:
                        raise RuntimeError(f"[openai] {self.model} HTTP 400（不可重试）: {detail or ex.reason}")
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
    """prefix ∈ {LLM, DRAFT, JUDGE}；缺省回落到 LLM_*。LLM_BACKEND=host 时用 HostClient。"""
    backend = os.environ.get(f"{prefix}_BACKEND") or os.environ.get("LLM_BACKEND", "openai")
    if mock or backend == "mock":
        return MockClient(cache_path=None)
    model = os.environ.get(f"{prefix}_MODEL") or os.environ.get("LLM_MODEL")
    if not model:
        raise RuntimeError(f"未设置 {prefix}_MODEL / LLM_MODEL")
    if backend == "host":
        return HostClient(model, cache_path=cache_path,
                          max_concurrency=int(os.environ.get("LLM_CONCURRENCY", "8")))
    base = os.environ.get(f"{prefix}_BASE_URL") or os.environ.get("LLM_BASE_URL")
    key = os.environ.get(f"{prefix}_API_KEY") or os.environ.get("LLM_API_KEY")
    extra = os.environ.get(f"{prefix}_EXTRA_BODY") or os.environ.get("LLM_EXTRA_BODY")
    if not base or not key:
        raise RuntimeError(f"未设置 {prefix}_BASE_URL/{prefix}_API_KEY（或 LLM_*）")
    return OpenAIClient(model, base, key, cache_path=cache_path, extra_body=json.loads(extra) if extra else None)
