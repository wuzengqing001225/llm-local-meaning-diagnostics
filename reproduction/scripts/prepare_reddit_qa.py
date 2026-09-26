#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reddit natural question-post task (W1 human-written task): post title contains a glossary term and is a question → highest-voted reply is gold.
Both question and answer are human-written and predate this study; drafters only rewrite gold and other replies into a four-choice format (same reader protocol as cnli/rag).
Compliance: store only post id / comment id / community / derived fields; author fields fully discarded; restricted to 2019 (before Reddit API policy change); release package contains only id + labels.
Output qa_posts.jsonl: {qid, subreddit, term, title, selftext(≤600 chars), gold_answer, other_answers[≤6], gold_score, n_comments}
"""
import argparse, csv, json, os, re, sys, time, urllib.parse, urllib.request
from wordfreq import zipf_frequency
API = "https://arctic-shift.photon-reddit.com/api"
UA = {"User-Agent": "tfpd-corpus-prep/0.1 (academic research tool)"}
def get(path, **kw):
    import urllib.error
    for att in range(3):
        try:
            req = urllib.request.Request(f"{API}/{path}?" + urllib.parse.urlencode(kw), headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r: return json.load(r).get("data", [])
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 429: return []
            time.sleep(3 * (att + 1))
        except Exception: time.sleep(3 * (att + 1))
    return []
def clean(t): return re.sub(r"\s+", " ", re.sub(r"https?://\S+|&gt;|&amp;|\[deleted\]|\[removed\]", " ", t or "")).strip()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gloss", default="glossaries.csv"); ap.add_argument("--terms", default=None, help="use only glossary terms from this terms.jsonl (consistent with main experiment)")
    ap.add_argument("--out", default="out_qa"); ap.add_argument("--min-comments", type=int, default=4); ap.add_argument("--min-gold-score", type=int, default=3)
    ap.add_argument("--max-per-term", type=int, default=6); ap.add_argument("--subs", default=None)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.terms:
        T = [json.loads(l) for l in open(a.terms, encoding="utf-8")]
        targets = [(t["labels"]["subreddit"], t["term"], t["gloss_gold"]) for t in T if t["labels"]["quadrant"] == "glossary"]
    else:
        rows = list(csv.DictReader(open(a.gloss, encoding="utf-8")))
        targets = [(r["subreddit"], r["term"].strip(), r["description"]) for r in rows if re.fullmatch(r"[A-Za-z][a-z]+( [a-z]+)?", r["term"].strip())
                   and min(zipf_frequency(w, "en") for w in r["term"].lower().split()) >= 4.0 and len(r["description"].split()) >= 4]
    if a.subs: targets = [t for t in targets if t[0] in a.subs.split(",")]
    out = open(os.path.join(a.out, "qa_posts.jsonl"), "w", encoding="utf-8"); n_posts = n_q = 0; stats = {}
    for k, (sub, term, gloss) in enumerate(targets):
        posts = get("posts/search", subreddit=sub, title=term, after="2019-01-01", before="2020-01-01", limit=100); time.sleep(0.3)
        pat = re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])", re.I)
        cand = [p for p in posts if "?" in (p.get("title") or "") and pat.search(p.get("title") or "") and (p.get("num_comments") or 0) >= a.min_comments
                and not (p.get("selftext") or "").startswith("[removed")]
        cand.sort(key=lambda p: -(p.get("num_comments") or 0)); n_posts += len(cand); got = 0
        for p in cand:
            if got >= a.max_per_term: break
            cs = get("comments/search", link_id=p["id"], limit=100); time.sleep(0.3)
            cs = [c for c in cs if clean(c.get("body")) and c.get("author") != p.get("author") and c.get("parent_id", "").endswith(p["id"]) and 8 <= len(clean(c["body"]).split()) <= 120]
            if not cs: continue
            cs.sort(key=lambda c: -(c.get("score") or 0))
            if (cs[0].get("score") or 0) < a.min_gold_score: continue
            out.write(json.dumps({"qid": f"rqa:{sub}:{p['id']}", "subreddit": sub, "term": term, "gloss_gold": gloss, "title": clean(p["title"]),
                                  "selftext": clean(p.get("selftext"))[:600], "gold_answer": clean(cs[0]["body"]), "gold_score": cs[0].get("score"),
                                  "other_answers": [clean(c["body"]) for c in cs[1:7]], "n_comments": p.get("num_comments"), "post_id": p["id"], "gold_comment_id": cs[0]["id"]},
                                 ensure_ascii=False) + "\n"); got += 1; n_q += 1
        stats[sub] = stats.get(sub, 0) + got
        print(f"\r[rqa] {k+1}/{len(targets)} {sub}/{term}: {got} q (total {n_q})      ", end="", file=sys.stderr)
    print(f"\n[rqa] candidate question posts {n_posts} → usable {n_q}; per sub {stats}", file=sys.stderr)
if __name__ == "__main__":
    main()