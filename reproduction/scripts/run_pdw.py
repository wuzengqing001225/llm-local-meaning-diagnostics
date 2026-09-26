#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDW Runner v0.2: computes weight and baseline for each term in terms.jsonl, outputs weights.jsonl. Batch concurrent implementation.

Estimators (ALGORITHM.md §5):
  rarity          public-language rarity (wordfreq), a modern IDF baseline
  tf_norm         exposure weight (--tf-source labels|contexts|none|query)
  delta_raw       primary estimator (contrastive): cloze_glossC − cloze_glossM; delta_hat = clip(delta_raw, 0, 1)
  gain_bare       v0.1 estimator (glossC − bare), for ablation
  deficit         1 − cloze_bare
  self_report     prior self-report (gloss_M / prior_guess, always collected because the control condition needs it) + tier (--self-report, requires judge)
Robustness variants (ERROR_STANDARD E6/E7): --robust another context subsample (delta_hat_alt); truncated gloss (delta_hat_gloss_perturbed)
gloss source (--gloss-mode auto|gold|both): auto drafted by the drafting model (DRAFT_*); gold uses gloss_gold; both uses auto as primary, stores gold as delta_hat_gold

Environment variables: LLM_BACKEND=host|openai; LLM_MODEL (reader); DRAFT_MODEL / JUDGE_MODEL (default to LLM_* if unset)
Usage: python3 run_pdw.py --terms data/synth_terms.jsonl --out data/synth_weights.jsonl --gloss-mode both --robust --self-report
"""
import argparse
import json
import os
import random
import sys

import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from pdwlib.llm import client_from_env, MockClient
from pdwlib.estimators import (rarity, cloze_requests, cloze_score, prior_request, is_unknown, guess_request,
                               tier_request, parse_tier, aggregate)

DRAFT_PROMPT = (
    "DRAFT_GLOSS. Based only on the usages below, write a one-sentence definition of the term "
    "\"{term}\" as it is used in this corpus. Do not use general knowledge if the usages contradict it. "
    "Output only the definition.\n\nUsages:\n{contexts}")
PLACEBO_GLOSS = "This term appears in the corpus; no further information about its meaning is available."
DOMAIN_PROMPT = ("Below are sentences sampled from a document collection. In one sentence (max 25 words), describe what kind "
                 "of organisation and activity these documents come from. Do not define any specific term.\n\n{sample}")


def perturb_gloss(gloss):
    words = gloss.split()
    return " ".join(words[: max(4, len(words) * 2 // 3)])


def sub_idx(n, k, seed):
    if n <= k:
        return list(range(n))
    return random.Random(seed).sample(range(n), k)


def run_batches(client, reqs, label, chunk=200):
    out = []
    for i in range(0, len(reqs), chunk):
        out.extend(client.complete_many(reqs[i:i + chunk]))
        print(f"\r[{label}] {min(i + chunk, len(reqs))}/{len(reqs)} calls={client.n_calls} "
              f"cache_hits={client.n_cache_hits}", end="", file=sys.stderr)
    if reqs:
        print(file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terms", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=8, help="number of contexts sampled per term")
    ap.add_argument("--window", type=int, default=4)
    ap.add_argument("--gloss-mode", choices=["auto", "gold", "both"], default="both")
    ap.add_argument("--tf-source", choices=["labels", "contexts", "none", "query"], default="labels")
    ap.add_argument("--self-report", action="store_true", help="assign tier via judge (gloss_M is always collected)")
    ap.add_argument("--robust", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--cache-dir", default="data/cache")
    ap.add_argument("--domain", default=None,
                    help="v0.3: domain description (one sentence); when given, the prior probe is an in-context prior. 'auto' means the drafting model infers it from a corpus sample")
    ap.add_argument("--no-guess", action="store_true", help="v0.3.1: disable the morphological-guess probe for terms with no prior (for ablation)")
    ap.add_argument("--prior-mode", choices=["ctx", "zero"], default="ctx",
                    help="ctx: in-context prior used as gloss_M (v0.3 default); zero: zero-context prior (v0.2 behavior, for ablation)")
    args = ap.parse_args()

    os.makedirs(args.cache_dir, exist_ok=True)
    reader = client_from_env("LLM", mock=args.mock, cache_path=os.path.join(args.cache_dir, "reader.jsonl"))
    drafter = reader if args.mock else (
        client_from_env("DRAFT", cache_path=os.path.join(args.cache_dir, "draft.jsonl"))
        if os.environ.get("DRAFT_MODEL") else reader)
    judge = None
    if args.self_report:
        judge = reader if args.mock else (
            client_from_env("JUDGE", cache_path=os.path.join(args.cache_dir, "judge.jsonl"))
            if os.environ.get("JUDGE_MODEL") else reader)
    if drafter is reader and args.gloss_mode in ("auto", "both") and not args.mock:
        print("[warn] the drafting model and the reader model are the same (DRAFT_MODEL not set); risk of circularity.", file=sys.stderr)

    entries = [json.loads(l) for l in open(args.terms, encoding="utf-8") if l.strip()]
    if args.limit:
        entries = entries[: args.limit]
    done = set()
    if os.path.exists(args.out):
        for l in open(args.out, encoding="utf-8"):
            try:
                done.add(json.loads(l)["id"])
            except Exception:  # noqa
                pass
    entries = [e for e in entries if e["id"] not in done]
    if not entries:
        print("[pdw] nothing to do", file=sys.stderr)
        return
    max_tf = max((e.get("labels", {}).get("tf") or 0) for e in entries) or 1
    max_qf = max((e.get("labels", {}).get("query_freq") or 0) for e in entries) or 1
    max_nctx = max(len(e["contexts"]) for e in entries)

    # ---- context subsampling (keeping spans aligned)
    S = {}
    for e in entries:
        n = len(e["contexts"])
        i1 = sub_idx(n, args.k, 1)
        i2 = sub_idx(n, args.k, 2) if args.robust else None
        sp = e.get("spans")
        S[e["id"]] = dict(ctx1=[e["contexts"][i] for i in i1],
                          sp1=[sp[i] for i in i1] if sp else None,
                          ctx2=[e["contexts"][i] for i in i2] if i2 else None,
                          sp2=[sp[i] for i in i2] if (sp and i2) else None)

    # ---- stage 0: domain description (v0.3)
    # ---- stage 0: domain description (condition for the in-context prior). When --domain auto, group by labels.domain and
    #      infer one sentence per group; fall back to the reader model if the drafting model fails; error if still empty.
    dom_of = {}
    if args.prior_mode == "ctx":
        groups = {}
        for e in entries:
            groups.setdefault(e.get("labels", {}).get("domain", "_all") if (args.domain in (None, "auto")) else "_fixed", []).append(e)
        for g, es in groups.items():
            if args.domain not in (None, "auto"):
                d = args.domain
            elif isinstance(drafter, MockClient):
                d = "(mock domain)"
            else:
                sample = []
                for e in es[:60]:
                    sample.extend(e["contexts"][:2])
                random.Random(0).shuffle(sample)
                prompt = DOMAIN_PROMPT.format(sample="\n".join(f"- {c}" for c in sample[:40]))
                d = drafter.complete(prompt, max_tokens=400).strip()
                if not d:
                    print("[domain] drafting model returned empty, falling back to reader model for domain description", file=sys.stderr)
                    d = reader.complete(prompt, max_tokens=400).strip()
                if not d:
                    raise RuntimeError("[domain] neither the drafting model nor the reader model returned a domain description. Check the API configuration, or supply --domain '<one-sentence domain description>' explicitly.")
            for e in es:
                dom_of[e["id"]] = d
            print(f"[domain] {g}: {d[:160]}", file=sys.stderr)
    domain = None  # legacy field compatibility: with multiple groups, each entry records its own domain

    # ---- stage 1: prior self-report (reader; in-context prior serves as the control condition gloss_M)
    pri = run_batches(reader, [prior_request(e["term"], dom_of.get(e["id"])) for e in entries], "prior")
    prior = {e["id"]: p for e, p in zip(entries, pri)}
    # v0.3.1: for terms whose in-context prior is UNKNOWN, add a morphological-guess probe; if guessed, use it as the control gloss_M (channel guess)
    guess = {}
    if args.prior_mode == "ctx" and not args.no_guess:
        unk = [e for e in entries if is_unknown(prior[e["id"]])]
        if unk:
            gs = run_batches(reader, [guess_request(e["term"], dom_of.get(e["id"])) for e in unk], "guess")
            guess = {e["id"]: g for e, g in zip(unk, gs)}
    prior_zero = {}
    if args.prior_mode == "ctx":  # also collect the zero-context prior, for interpretation and ablation
        pz = run_batches(reader, [prior_request(e["term"], None) for e in entries], "prior0")
        prior_zero = {e["id"]: p for e, p in zip(entries, pz)}
    # ---- stage 2: draft gloss (drafting model)
    g_auto = {}
    if args.gloss_mode in ("auto", "both"):
        if isinstance(drafter, MockClient):
            g_auto = {e["id"]: f"(mock gloss for {e['term']})" for e in entries}
        else:
            reqs = [dict(prompt=DRAFT_PROMPT.format(term=e["term"], contexts="\n".join(
                f"- {c}" for c in S[e["id"]]["ctx1"])), max_tokens=120, temperature=0.0) for e in entries]
            g_auto = {e["id"]: g for e, g in zip(entries, run_batches(drafter, reqs, "draft"))}

    # ---- stage 3: cloze requests (reader)
    all_reqs, owners = [], []  # owners[i] = (id, variant)

    def add(eid, variant, reqs, meta):
        for r, m in zip(reqs, meta):
            all_reqs.append(r)
            owners.append((eid, variant, m))

    glossC_of, chan = {}, {}
    for e in entries:
        eid = e["id"]
        gA = g_auto.get(eid) or None
        gG = e.get("gloss_gold") if args.gloss_mode in ("gold", "both") else None
        primary = gA if gA else gG
        glossC_of[eid] = (primary, "auto" if gA else ("gold" if gG else None))
        if prior[eid] and not is_unknown(prior[eid]):
            gM, channel = prior[eid], "conflict"
        elif guess.get(eid) and not is_unknown(guess[eid]):
            gM, channel = guess[eid], "guess"
        else:
            gM, channel = PLACEBO_GLOSS, "unknown"
        chan[eid] = channel
        s = S[eid]
        r, m = cloze_requests(e["term"], s["ctx1"], s["sp1"],
                              {"bare": None, "glossC": primary, "glossM": gM}, args.window)
        add(eid, "main", r, m)
        if args.gloss_mode == "both" and gG and gA:
            r, m = cloze_requests(e["term"], s["ctx1"], s["sp1"], {"glossC": gG, "glossM": gM}, args.window)
            add(eid, "gold", r, m)
        if args.robust:
            if s["ctx2"]:
                r, m = cloze_requests(e["term"], s["ctx2"], s["sp2"],
                                      {"bare": None, "glossC": primary, "glossM": gM}, args.window)
                add(eid, "alt", r, m)
            if primary:
                r, m = cloze_requests(e["term"], s["ctx1"], s["sp1"],
                                      {"glossC": perturb_gloss(primary), "glossM": gM}, args.window)
                add(eid, "perturbed", r, m)
    answers = run_batches(reader, all_reqs, "cloze")
    per = {}
    for (eid, variant, m), a in zip(owners, answers):
        per.setdefault((eid, variant), ([], []))
        per[(eid, variant)][0].append(m)
        per[(eid, variant)][1].append(a)

    # ---- stage 4: tier (judge)
    tiers = {}
    if args.self_report:
        reqs = [tier_request(e["term"], S[e["id"]]["ctx1"], prior[e["id"]]) for e in entries]
        for e, t in zip(entries, run_batches(judge, reqs, "tier")):
            tiers[e["id"]] = parse_tier(t)

    # ---- output
    with open(args.out, "a", encoding="utf-8") as out:
        for e in entries:
            eid = e["id"]
            lab = e.get("labels", {})
            if args.tf_source == "labels":
                tf_norm = (lab.get("tf") or 1) / max_tf
            elif args.tf_source == "query":
                tf_norm = (lab.get("query_freq") or 1) / max_qf
            elif args.tf_source == "contexts":
                tf_norm = len(e["contexts"]) / max_nctx
            else:
                tf_norm = 1.0
            rec = {"id": eid, "term": e["term"], "labels": lab, "tf_norm": tf_norm,
                   "rarity": rarity(e["term"], e.get("lang", "en")),
                   "n_contexts": len(e["contexts"]), "n_used": len(S[eid]["ctx1"]),
                   "prior_guess": prior[eid], "prior_unknown": is_unknown(prior[eid]),
                   "gloss_used": glossC_of[eid][0], "gloss_source": glossC_of[eid][1],
                   "gloss_auto": g_auto.get(eid), "gloss_gold": e.get("gloss_gold")}
            m, a = per.get((eid, "main"), ([], []))
            cz = cloze_score(m, a)
            rec.update({"cloze_bare": cz.get("bare", float("nan")), "cloze_glossC": cz.get("glossC", float("nan")),
                        "cloze_glossM": cz.get("glossM", float("nan")), "delta_raw": cz["delta_raw"],
                        "delta_ci": cz["delta_ci"], "gain_bare": cz["gain_bare"], "n_masked": cz["n"]})
            rec.update(aggregate(tf_norm, cz, chan[eid] == "unknown", chan[eid]))
            rec["prior_form_guess"] = guess.get(eid)
            rec["domain"] = dom_of.get(eid)
            rec["prior_zero"] = prior_zero.get(eid)
            rec["prior_mode"] = args.prior_mode
            for variant, key in (("gold", "delta_hat_gold"), ("alt", "delta_hat_alt"),
                                 ("perturbed", "delta_hat_gloss_perturbed")):
                if (eid, variant) in per:
                    czv = cloze_score(*per[(eid, variant)])
                    rec[key] = aggregate(tf_norm, czv, chan[eid] == "unknown", chan[eid])["delta_hat"]
                    rec[key.replace("delta_hat", "delta_raw")] = czv["delta_raw"]
                    if variant == "alt":
                        rec["gain_bare_alt"] = czv["gain_bare"]
            if eid in tiers:
                rec["tier"], rec["corpus_meaning_judge"] = tiers[eid]
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[done] {len(entries)} terms → {args.out}  reader_calls={reader.n_calls}", file=sys.stderr)


if __name__ == "__main__":
    main()