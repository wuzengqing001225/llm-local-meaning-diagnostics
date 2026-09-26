#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inverse Scaling Prize `redefine` (1,244 human-written redefinition prompts, binary classification) × silent misreading.
This is the human-written version of "answers by prior despite definition being present" (our glossC condition); supplements §G / three-generation gradient, not a replacement for W1.

Two conditions:
  given  original prompt (includes redefinition sentence)           → correct = follows redefinition (answer_index)
  bare   redefinition sentence removed, question only            → reader answers by prior; recorded answer = prior answer
Derived quantities:
  follow_rate   fraction following redefinition under given (= official accuracy)
  prior_pull    fraction where given answer == bare answer (prior pulls it back)
  proxy         local white-box model's two-class logprob under given prompt → 1−P(correct); predicts API reader failure on same question (AUROC)
Usage:
  export LLM_BACKEND=openai LLM_MODEL=... LLM_BASE_URL=... LLM_API_KEY=... [LLM_EXTRA_BODY='{"thinking":{"type":"disabled"}}']
  python3 redefine_bench.py --reader --out redefine_<reader>.jsonl          # 2×1244 calls
  python3 redefine_bench.py --proxy Qwen/Qwen2.5-7B --out redefine_proxy_qwen7b.jsonl   # local, no API
  python3 redefine_bench.py --analyze redefine_<reader>.jsonl --proxy-file redefine_proxy_qwen7b.jsonl
"""
import argparse, json, os, re, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DATA = os.environ.get("REDEFINE_DATA") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "redefine_classification.jsonl")

def load():
    import ast
    R = [json.loads(l) for l in open(DATA, encoding="utf-8")]
    for r in R:  # in the dataset, classes is a string repr of a Python list ("[' 7', ' 5']"), needs parsing into a list
        if isinstance(r["classes"], str): r["classes"] = list(ast.literal_eval(r["classes"]))
    return R

def split_prompt(p):
    """Returns (redefinition sentence, question part). Redefinition sentence = first sentence (up to the first '. ' or ' Q:')."""
    m = re.search(r"\s(Q:|Question:)", p)
    if m and m.start() > 0:
        return p[:m.start()].strip(), p[m.start():].strip()
    m = re.search(r"\.\s+(?=[A-Z])", p)
    if m:
        return p[:m.end()].strip(), p[m.end():].strip()
    return "", p

SYS = "Answer with exactly one of the given options and nothing else."

def fmt(prompt, classes):
    opts = " / ".join(c.strip() for c in classes)
    return f"{prompt}\nOptions: {opts}\nAnswer:"

def pick(text, classes):
    t = (text or "").strip().lower()
    for i, c in enumerate(classes):
        if t.startswith(c.strip().lower()): return i
    for i, c in enumerate(classes):
        if c.strip().lower() in t: return i
    return None

def run_reader(a):
    from pdwlib.llm import client_from_env
    cl = client_from_env("LLM", cache_path=os.path.join(a.cache_dir, "reader.jsonl"))
    R = load(); rows = []
    reqs, meta = [], []
    for k, r in enumerate(R):
        redef, q = split_prompt(r["prompt"])
        for cond, p in (("given", r["prompt"]), ("bare", q)):
            reqs.append(dict(prompt=fmt(p, r["classes"]), system=SYS, max_tokens=8, temperature=0.0)); meta.append((k, cond))
    outs = []
    for i in range(0, len(reqs), 200):
        outs += cl.complete_many(reqs[i:i+200]); print(f"\r[reader] {min(i+200, len(reqs))}/{len(reqs)}", end="", file=sys.stderr)
    by = {}
    for (k, cond), o in zip(meta, outs): by.setdefault(k, {})[cond] = o
    with open(a.out, "w", encoding="utf-8") as f:
        for k, r in enumerate(R):
            g = pick(by[k].get("given"), r["classes"]); b = pick(by[k].get("bare"), r["classes"])
            redef, q = split_prompt(r["prompt"])
            f.write(json.dumps(dict(idx=k, part=r["part"], redef=redef, question=q, classes=r["classes"], gold=r["answer_index"],
                                    given=g, bare=b, given_raw=by[k].get("given"), bare_raw=by[k].get("bare"),
                                    model=os.environ.get("LLM_MODEL")), ensure_ascii=False) + "\n")
    print(f"\n[done] → {a.out}", file=sys.stderr); analyze(a.out, None)

def run_proxy(a):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    dev = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(a.proxy); tok.padding_side = "left"
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.proxy, torch_dtype=getattr(torch, a.dtype)).to(dev).eval()
    R = load()
    @torch.no_grad()
    def lp_of(prefixes, conts):
        # log P(cont | prefix), summed token-by-token
        out = []
        for i in range(0, len(prefixes), a.batch):
            P, C = prefixes[i:i+a.batch], conts[i:i+a.batch]
            full = [p + c for p, c in zip(P, C)]
            enc = tok(full, return_tensors="pt", padding=True).to(dev)
            logits = model(**enc).logits.float(); logp = torch.log_softmax(logits[:, :-1], -1)
            tgt = enc.input_ids[:, 1:]; g = logp.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
            for j, (p, c) in enumerate(zip(P, C)):
                n_c = len(tok(c, add_special_tokens=False).input_ids); L = int(enc.attention_mask[j].sum())
                out.append(float(g[j, L-1-n_c:L-1].sum()))
        return out
    rows = []
    for cond in ("given", "bare"):
        prefixes, conts, meta = [], [], []
        for k, r in enumerate(R):
            redef, q = split_prompt(r["prompt"]); p = fmt(r["prompt"] if cond == "given" else q, r["classes"])
            for ci, c in enumerate(r["classes"]): prefixes.append(p); conts.append(c if c.startswith(" ") else " " + c); meta.append((k, ci))
        lps = lp_of(prefixes, conts); byk = {}
        for (k, ci), v in zip(meta, lps): byk.setdefault(k, {})[ci] = v
        for k, r in enumerate(R):
            z = byk[k]; mx = max(z.values()); Z = sum(math.exp(v - mx) for v in z.values()); pr = {ci: math.exp(v - mx)/Z for ci, v in z.items()}
            rows.append(dict(idx=k, cond=cond, probs=[pr[i] for i in range(len(r["classes"]))], p_correct=pr[r["answer_index"]], argmax=max(pr, key=pr.get)))
        print(f"[proxy] {cond} done", file=sys.stderr)
    with open(a.out, "w") as f:
        for row in rows: f.write(json.dumps(dict(row, model=a.proxy)) + "\n")
    g = [r for r in rows if r["cond"] == "given"]; b = {r["idx"]: r for r in rows if r["cond"] == "bare"}
    acc = sum(r["argmax"] == R[r["idx"]]["answer_index"] for r in g)/len(g)
    pull = sum(r["argmax"] == b[r["idx"]]["argmax"] for r in g)/len(g)
    print(f"[proxy {a.proxy}] follow_rate={acc:.3f}  prior_pull={pull:.3f}  → {a.out}", file=sys.stderr)

def auroc(pos, neg):
    if not pos or not neg: return float("nan")
    return sum((p > n) + 0.5*(p == n) for p in pos for n in neg)/(len(pos)*len(neg))

def analyze(path, proxy_file):
    import ast
    R = [json.loads(l) for l in open(path, encoding="utf-8")]
    for r in R:
        if isinstance(r["classes"], str): r["classes"] = list(ast.literal_eval(r["classes"])); r["given"] = pick(r.get("given_raw"), r["classes"]); r["bare"] = pick(r.get("bare_raw"), r["classes"])
    m = lambda v: sum(v)/len(v) if v else float("nan")
    print(f"\n=== reader {R[0].get('model')}  n={len(R)}")
    for part in sorted({r["part"] for r in R}) + ["all"]:
        S = [r for r in R if part == "all" or r["part"] == part]
        ok = [r for r in S if r["given"] is not None and r["bare"] is not None]
        follow = m([r["given"] == r["gold"] for r in ok]); pull = m([r["given"] == r["bare"] for r in ok])
        bare_prior = m([r["bare"] != r["gold"] for r in ok])  # bare answer != redefinition answer = prior direction (should approach 1)
        print(f"part {part}: n={len(ok)}  follow_rate={follow:.3f}  prior_pull={pull:.3f}  bare answers prior-side={bare_prior:.3f}  unparsed={len(S)-len(ok)}")
    if proxy_file:
        P = {(json.loads(l)["idx"], json.loads(l)["cond"]): json.loads(l) for l in open(proxy_file)}
        ok = [r for r in R if r["given"] is not None and (r["idx"], "given") in P]
        pos = [1 - P[(r["idx"], "given")]["p_correct"] for r in ok if r["given"] != r["gold"]]
        neg = [1 - P[(r["idx"], "given")]["p_correct"] for r in ok if r["given"] == r["gold"]]
        print(f"\nproxy 1−P(correct|given) → reader fails to follow: AUROC={auroc(pos, neg):.3f} (n_fail={len(pos)}/{len(ok)})")
        for lo, hi in [(0, .2), (.2, .5), (.5, .8), (.8, 1.01)]:
            s = [r["given"] != r["gold"] for r in ok if lo <= 1 - P[(r["idx"], "given")]["p_correct"] < hi]
            if s: print(f"   proxy risk [{lo},{hi}): n={len(s):4d} reader fail {m(s):.2f}")
    print("\nPre-registration: H1 strong readers have follow_rate clearly <1 and high prior_pull (prior still dominates under human-written redefinition, consistent with §G 'definition present still needs gating'); "
          "H2 proxy 1−P(correct|given) predicts reader non-compliance with AUROC ≥0.7 (same question, shared prior mechanism); H3 three-generation readers' follow_rate rises monotonically but stays below 1 (human-written replication of the three-generation gradient).")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", action="store_true"); ap.add_argument("--proxy", default=None); ap.add_argument("--proxy-file", default=None)
    ap.add_argument("--analyze", default=None); ap.add_argument("--out", default=None); ap.add_argument("--cache-dir", default="data/cache_redefine")
    ap.add_argument("--dtype", default="bfloat16"); ap.add_argument("--batch", type=int, default=16)
    a = ap.parse_args(); os.makedirs(a.cache_dir, exist_ok=True)
    if a.analyze: analyze(a.analyze, a.proxy_file)
    elif a.reader: run_reader(a)
    elif a.proxy: run_proxy(a)
    else: ap.print_help()