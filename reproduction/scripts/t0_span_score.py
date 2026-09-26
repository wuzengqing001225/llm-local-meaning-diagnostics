#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T0 occurrence-level span screening (SCALE_DEMO_PLAN): for each occurrence compute
  deficit = −mean logP(span | sentence prefix)                    (how "surprising" this sentence reads without any hint)
  gain    = mean logP(span | definition note + prefix) − same as above   (how much better this sentence gets given the definition → meaning load × reader gap)
span = at most 30 tokens after the term's first occurrence (up to sentence end). screen score = gain (primary) + deficit (secondary, each z-scored then averaged).
Usage:
  Full run: python3 t0_span_score.py --occ data/cuad_full/occurrences.jsonl --terms data/cuad_full/terms_full.jsonl \
            --model Qwen/Qwen2.5-7B --out data/cuad_full/t0_scores.jsonl
  Pilot (go/no-go): --pilot data/cuad/terms.jsonl:runs/local/deepseek/cuad/eqa_usage.jsonl:data/cuad/lpmc_cuad_usage.jsonl
        Score sentences from the existing 733 usage questions and compare against question-level risk (1−P correct): Spearman ≥ 0.6 and high-risk recall@20% ≥ 0.8 → GO
"""
import argparse, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def spearman(x, y):
    n = len(x)
    if n < 3: return float("nan")
    def rk(v):
        s = sorted(range(n), key=lambda i: v[i]); r = [0.0]*n
        i = 0
        while i < n:
            j = i
            while j+1 < n and v[s[j+1]] == v[s[i]]: j += 1
            for k in range(i, j+1): r[s[k]] = (i+j)/2
            i = j+1
        return r
    rx, ry = rk(x), rk(y)
    mx, my = sum(rx)/n, sum(ry)/n
    num = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a-mx)**2 for a in rx) * sum((b-my)**2 for b in ry))
    return num/den if den else float("nan")

@torch.no_grad()
def score_batch(model, tok, device, items):
    """items: [(prefix, sent, term)] → [mean logP of span tokens]"""
    texts, spans = [], []
    for prefix, sent, term in items:
        full = prefix + sent
        pos = sent.find(term)
        span_char = len(prefix) + (pos + len(term) if pos >= 0 else 0)
        texts.append(full); spans.append(span_char)
    enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=512, return_offsets_mapping=True)
    offs = enc.pop("offset_mapping")
    enc = {k: v.to(device) for k, v in enc.items()}
    logits = model(**enc).logits.float().log_softmax(-1)
    out = []
    for b in range(len(texts)):
        ids = enc["input_ids"][b]; att = enc["attention_mask"][b]
        lps, n = 0.0, 0
        for t in range(1, ids.shape[0]):
            if att[t] == 0: continue
            if offs[b][t][0] < spans[b]: continue
            if n >= 30: break
            lps += logits[b, t-1, ids[t]].item(); n += 1
        out.append(lps/n if n else float("nan"))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--occ"); ap.add_argument("--terms", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-7B"); ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--batch", type=int, default=16); ap.add_argument("--out", default="t0_scores.jsonl")
    ap.add_argument("--gloss-cap", type=int, default=300, help="gloss note truncation length (characters)")
    ap.add_argument("--pilot", help="terms.jsonl:eqa_usage.jsonl:lpmc.jsonl -- go/no-go mode")
    a = ap.parse_args()
    device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(a.model, padding_side="right")
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=getattr(torch, a.dtype)).to(device).eval()
    T = {json.loads(l)["id"]: json.loads(l) for l in open(a.terms, encoding="utf-8")}
    if a.pilot:
        tp, ep, lp = a.pilot.split(":")
        T = {json.loads(l)["id"]: json.loads(l) for l in open(tp, encoding="utf-8")}
        E = {json.loads(l)["id"]: json.loads(l) for l in open(ep, encoding="utf-8")}
        L = {json.loads(l)["id"]: json.loads(l) for l in open(lp, encoding="utf-8")}
        items, qrisk = [], []
        for i, e in E.items():
            pq = L.get(i, {}).get("per_question", [])
            if len(pq) != len(e.get("questions", [])): continue
            for q, p in zip(e["questions"], pq):
                ci = q.get("ctx_idx")
                if ci is None or ci >= len(T[i]["contexts"]) or "bare" not in p: continue
                g = (T[i].get("gloss_gold") or "")[: a.gloss_cap]
                sent = T[i]["contexts"][ci]
                items.append((i, f'Term note: "{e["term"]}" — {g}\n\n', sent, e["term"]))
                qrisk.append(1 - p["bare"]["p_correct"])
        print(f"[pilot] {len(items)} question-sentences", file=sys.stderr)
        bare, glos = [], []
        for k in range(0, len(items), a.batch):
            ch = items[k:k+a.batch]
            bare += score_batch(model, tok, device, [("", s, t) for _, _, s, t in ch])
            glos += score_batch(model, tok, device, [(pfx, s, t) for _, pfx, s, t in ch])
            print(f"\r[pilot] {min(k+a.batch, len(items))}/{len(items)}", end="", file=sys.stderr)
        print(file=sys.stderr)
        gain = [g - b for g, b in zip(glos, bare)]; deficit = [-b for b in bare]
        def z(v):
            mu = sum(v)/len(v); sd = (sum((x-mu)**2 for x in v)/len(v))**0.5 or 1
            return [(x-mu)/sd for x in v]
        screen = [(x+y)/2 for x, y in zip(z(gain), z(deficit))]
        rho_g, rho_s = spearman(gain, qrisk), spearman(screen, qrisk)
        hi = [k for k, r in enumerate(qrisk) if r >= 0.5]
        topn = max(1, len(screen)//5)
        top = set(sorted(range(len(screen)), key=lambda k: -screen[k])[:topn])
        rec = sum(1 for k in hi if k in top)/len(hi) if hi else float("nan")
        print(f"[pilot] Spearman(gain, q-risk)={rho_g:.3f}  Spearman(screen, q-risk)={rho_s:.3f}  recall@20% of high-risk(n={len(hi)})={rec:.3f}")
        print(f"[pilot] {'GO' if (max(rho_g, rho_s) >= 0.6 and rec >= 0.8) else 'NO-GO'} (thresholds: rho>=0.6, recall>=0.8)")
        json.dump({"rho_gain": rho_g, "rho_screen": rho_s, "recall_at20": rec, "n": len(items), "n_high": len(hi)},
                  open("t0_pilot_result.json", "w"), indent=1)
        return
    occs = [json.loads(l) for l in open(a.occ, encoding="utf-8")]
    done = set()
    if os.path.exists(a.out):
        done = {(r["id"], r["occ_idx"]) for r in map(json.loads, open(a.out, encoding="utf-8"))}
        print(f"[resume] {len(done)} already scored", file=sys.stderr)
    occs = [o for o in occs if (o["id"], o["occ_idx"]) not in done]
    with open(a.out, "a", encoding="utf-8") as f:
        for k in range(0, len(occs), a.batch):
            ch = occs[k:k+a.batch]
            pf = [f'Term note: "{o["term"]}" — {(T[o["id"]].get("def_raw") or T[o["id"]].get("gloss_gold") or "")[: a.gloss_cap]}\n\n' for o in ch]
            b = score_batch(model, tok, device, [("", o["sent"], o["term"]) for o in ch])
            g = score_batch(model, tok, device, [(p, o["sent"], o["term"]) for p, o in zip(pf, ch)])
            for o, bb, gg in zip(ch, b, g):
                f.write(json.dumps({"id": o["id"], "occ_idx": o["occ_idx"], "term": o["term"], "ci": o["ci"],
                                    "lp_bare": round(bb, 4), "gain": round(gg - bb, 4), "deficit": round(-bb, 4)}) + "\n")
            if k % (a.batch*20) == 0:
                print(f"\r[t0] {min(k+a.batch, len(occs))}/{len(occs)}", end="", file=sys.stderr)
    print(f"\n[done] → {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()