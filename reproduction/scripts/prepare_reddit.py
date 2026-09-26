#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reddit community language corpus (Lucy & Bamman 2021 glossary × Arctic Shift comment archive) → terms.jsonl for TF-PD pipeline.
Target terms = "commonly redefined words" in glossary: alphabetic only, general word frequency zipf ≥ --min-zipf, community gloss ≥4 words.
Control terms = high-frequency common words from same-community comments not in glossary (prior_consistent controls, for E1/E2-type detection testing).
Per term: fetch 2019 comments containing the word via phrase filter, split into sentences keeping ones containing the word (12–80 words), dedupe, ≤ --max-ctx items.
"""
import argparse, csv, json, os, random, re, sys, time, urllib.parse, urllib.request
from collections import Counter, defaultdict
from wordfreq import zipf_frequency
API = "https://arctic-shift.photon-reddit.com/api/comments/search"
def fetch(sub, phrase=None, after="2019-01-01", before="2020-01-01", limit=100):
    import urllib.error
    q = dict(subreddit=sub, limit=limit, after=after, before=before)
    variants = [f'"{phrase}"', phrase] if phrase and " " in phrase else ([f'"{phrase}"'] if phrase else [None])
    for body in variants:
        if body: q["body"] = body
        for att in range(3):
            try:
                req = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "tfpd-corpus-prep/0.1 (academic research tool)"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    d = json.load(r); return d.get("data", d)
            except urllib.error.HTTPError as e:
                if 400 <= e.code < 500 and e.code != 429: break          # 4xx (e.g. 422) not retried; try next phrase variant
                print(f"\n[reddit] retry {att+1} {sub}/{phrase}: HTTP {e.code}", file=sys.stderr); time.sleep(3 * (att + 1))
            except Exception as e:
                print(f"\n[reddit] retry {att+1} {sub}/{phrase}: {str(e)[:60]}", file=sys.stderr); time.sleep(3 * (att + 1))
    return []
def sents(text):
    text = re.sub(r"\s+", " ", re.sub(r"https?://\S+|&gt;|&amp;|\[deleted\]|\[removed\]", " ", text))
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if 12 <= len(s.split()) <= 80]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gloss", default="ingroup_lang-master/data/glossaries.csv"); ap.add_argument("--out", default="out")
    ap.add_argument("--min-zipf", type=float, default=4.0); ap.add_argument("--max-ctx", type=int, default=12)
    ap.add_argument("--min-ctx", type=int, default=4); ap.add_argument("--controls-per-sub", type=int, default=5)
    ap.add_argument("--subs", default=None, help="comma-separated, restrict to subreddits"); ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); rng = random.Random(a.seed)
    rows = list(csv.DictReader(open(a.gloss, encoding="utf-8")))
    targets = defaultdict(dict)
    for r in rows:
        t = r["term"].strip(); sub = r["subreddit"]
        if a.subs and sub not in a.subs.split(","): continue
        if not re.fullmatch(r"[A-Za-z][a-z]+( [a-z]+)?", t) or len(r["description"].split()) < 4: continue
        z = min(zipf_frequency(w, "en") for w in t.lower().split())
        if z >= a.min_zipf and t.lower() not in targets[sub]: targets[sub][t.lower()] = dict(term=t, zipf=round(z, 2), gloss=r["description"].strip())
    print(f"[reddit] {sum(len(v) for v in targets.values())} candidate redefined common words in {len(targets)} subs", file=sys.stderr)
    terms, corpus = [], []
    shard_dir = os.path.join(a.out, "shards"); os.makedirs(shard_dir, exist_ok=True)
    STOP = set("the a an of to in for and or is that on by at with as it this from be are its when which has been not one you i my we they he she your our their if but so do does did have had was were will would can could should just like get got about all any more than then there what who how also very much some out up".split())
    for sub, tv in targets.items():
        shard = os.path.join(shard_dir, f"{sub}.json")
        if os.path.exists(shard):
            d = json.load(open(shard, encoding="utf-8")); terms += d["terms"]; corpus.append(d["corpus"]); continue
        sub_terms, pool_sents = [], []
        t0 = time.time()
        for k, info in tv.items():
            cs = fetch(sub, info["term"]); time.sleep(0.3)
            print(f"\r[reddit] {sub}: {info['term']} ({len(cs)} comments, {time.time()-t0:.0f}s)      ", end="", file=sys.stderr)
            pat = re.compile(r"(?<![A-Za-z])" + re.escape(info["term"]) + r"(?![A-Za-z])", re.I)
            ctx = []
            for c in cs:
                for s in sents(c.get("body", "")):
                    if pat.search(s): ctx.append(s)
                    pool_sents.append(s)
            ctx = list(dict.fromkeys(ctx)); rng.shuffle(ctx)
            if len(ctx) < a.min_ctx: continue
            sub_terms.append({"id": f"reddit:{sub}:{info['term']}", "term": info["term"], "lang": "en", "contexts": ctx[: a.max_ctx],
                          "gloss_gold": info["gloss"], "labels": {"source": "reddit", "subreddit": sub, "quadrant": "glossary", "zipf": info["zipf"],
                                                                   "tf": len(ctx), "is_target": True, "variant": "main"}})
        # Control words: high-frequency, non-glossary, high general-frequency common words from same-community sentence pool
        gl = {r["term"].strip().lower() for r in rows if r["subreddit"] == sub}
        freq = Counter(w for s in pool_sents for w in re.findall(r"[a-z]{4,}", s.lower()) if w not in STOP and w not in gl and zipf_frequency(w, "en") >= 4.5)
        for w, _ in freq.most_common(a.controls_per_sub * 3):
            pat = re.compile(r"(?<![a-z])" + w + r"(?![a-z])", re.I); ctx = list(dict.fromkeys(s for s in pool_sents if pat.search(s)))
            if len(ctx) < a.min_ctx: continue
            rng.shuffle(ctx)
            sub_terms.append({"id": f"reddit:{sub}:{w}", "term": w, "lang": "en", "contexts": ctx[: a.max_ctx], "gloss_gold": None,
                          "labels": {"source": "reddit", "subreddit": sub, "quadrant": "control", "zipf": round(zipf_frequency(w, "en"), 2),
                                     "tf": len(ctx), "is_target": False, "variant": "main"}})
            if sum(1 for t in sub_terms if t["labels"]["quadrant"] == "control") >= a.controls_per_sub: break
        doc = {"doc_id": f"r/{sub}", "text": " ".join(dict.fromkeys(pool_sents))}
        json.dump({"terms": sub_terms, "corpus": doc}, open(shard, "w", encoding="utf-8"), ensure_ascii=False)
        terms += sub_terms; corpus.append(doc)
        print(f"\n[reddit] {sub}: {sum(1 for t in sub_terms if t['labels']['quadrant']=='glossary')} glossary / "
              f"{sum(1 for t in sub_terms if t['labels']['quadrant']=='control')} control terms", file=sys.stderr)
    with open(os.path.join(a.out, "terms.jsonl"), "w", encoding="utf-8") as f:
        for t in terms: f.write(json.dumps(t, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "corpus.jsonl"), "w", encoding="utf-8") as f:
        for d in corpus: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    q = Counter(t["labels"]["quadrant"] for t in terms)
    print(json.dumps({"terms": len(terms), "by_quadrant": dict(q), "subs": len(corpus), "occurrences": sum(len(t["contexts"]) for t in terms)}))
if __name__ == "__main__":
    main()