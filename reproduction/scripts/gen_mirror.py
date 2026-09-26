#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a fictional structural-twin corpus from specified distributional parameters."""
import argparse, csv, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdwlib.llm import client_from_env
from pdwlib.text import extract_json

TF = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 7, 8, 10, 10, 11, 11, 12, 12, 17, 21, 27, 27, 31, 41]
LEN = {1: 4, 2: 25, 3: 5, 4: 5, 6: 1, 7: 1, 8: 1, 9: 1}
TIER = {"shifted": 19, "narrower": 14, "none": 6, "unknown": 3, "opposite": 1}
TIER_DESC = {
    "shifted": "A common everyday word that within the team is given a **related but different** specific meaning (outsiders would misread it using the everyday sense)",
    "narrower": "A common everyday word that within the team is used only to refer to a **specific subclass/specific object** of the everyday sense (outsiders would understand it too broadly)",
    "none": "A common business term whose team usage **matches** the everyday sense (control item, no explanation needed)",
    "unknown": "A term or abbreviation **coined by the team** that outsiders wouldn't recognize at all (not any everyday word)",
    "opposite": "A common everyday word whose internal team meaning is **opposite to or conflicting with** the everyday sense",
}
# The two prompt templates below are intentionally in Chinese: the structural twin is a Chinese-language corpus,
# generated to match the distributional parameters of a private Chinese operations notebook (see the paper, Appendix A.1).
GLOSS_PROMPT = """你在为一个虚构的团队编写内部词表，用于研究"内部私有词义与公共词义的偏离"。情景：{scenario}。
请设计 {n} 个术语条目，严格满足下列结构约束（这些是统计约束，不是内容约束）：
1. 术语字数分布（字数: 条目数）：{lens}
2. 档位分布（档位: 条目数）：{tiers}。档位含义：
{tier_desc}
3. 每条 definition 是**稳定的类层含义**，20–48 个汉字，中位约 35 字；不含数字阈值、具体案例。
4. 每条 note 是**易变标注**（参数、阈值、具体流程、案例），可为空字符串；约一半条目有 note。
5. 术语必须是真实存在的中文常用词（除 unknown 档为自造词）；不得与金融、交易、投资、加密货币有任何关系；不得使用任何真实公司或人名。
6. 43 个术语彼此不同，内部含义互不重叠，整体像一个真实团队几年内自然形成的黑话。
只输出 JSON：{{"terms": [{{"term": "...", "tier": "shifted|narrower|none|unknown|opposite", "definition": "...", "note": "...", "standard": "该词的日常公共含义（unknown 档写空）"}}]}}"""
SENT_PROMPT = """情景：{scenario}。这个团队内部把"{term}"用作特定含义：
  内部含义：{definition}{note_line}{std_line}
请写 {n} 句这个团队内部运营笔记里会出现的句子，每句都**实际使用**"{term}"这个词（原形出现一次），要求：
(1) 句子预设读者已懂内部含义，**绝不解释或定义**它；(2) 至少 {n_bearing} 句里，按内部含义读与按日常含义读会得出**不同结论**（含义承重）；
(3) 风格多样：规则条目、事故复盘、检查清单、群聊短句、带数字/日期/人名代号（用 A/B/小王这类代号）的记录；每句 15–60 字；(4) 不得出现金融/交易内容。
再写 3 道四选一选择题，考察读者是否按内部含义理解某一句：题干引用该句情境，四个选项都是同一业务场景里合理的具体说法，只在"{term}"取何义上不同；
其中一个错误选项必须是按日常含义会选的答案；正确选项**不得复述定义的措辞**。
只输出 JSON：{{"sentences": ["..."], "spans": ["每句中承载内部含义的 2–8 字片段，无则 null"], "qa": [{{"q": "...", "options": ["A...","B...","C...","D..."], "answer": "A", "sense": "corpus"}}]}}"""
AUDIT_PROMPT = """The term \"{term}\" has the following internal meaning within a certain team: {definition}
For each sentence below, does it (a) actually use this word consistently with this internal meaning, (b) not explain/define the word within the sentence?
{sents}
Output only a JSON array, one per sentence: "OK" or "BAD:reason"."""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="Internal work notes of a mid-size chain gym's store operations and membership management team (front desk, trainers, membership consultants, store manager)")
    ap.add_argument("--out", default="data/mirror"); ap.add_argument("--seed", type=int, default=7); ap.add_argument("--mock", action="store_true")
    ap.add_argument("--cache-dir", default="data/cache_mirror"); ap.add_argument("--n-docs", type=int, default=26)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); os.makedirs(a.cache_dir, exist_ok=True)
    rng = random.Random(a.seed)
    gen = client_from_env("DRAFT", mock=a.mock, cache_path=os.path.join(a.cache_dir, "gen.jsonl"))
    judge = client_from_env("JUDGE", mock=a.mock, cache_path=os.path.join(a.cache_dir, "judge.jsonl"))
    # 1) Word list: generate separately by tier, ensuring exact tier counts; word-length distribution is written into the prompt as an overall soft constraint
    tier_desc = "\n".join(f"   - {k}: {v}" for k, v in TIER_DESC.items())
    G = []
    if a.mock:
        G = [dict(term=f"word{i}", tier=t, definition="This is an internal meaning description for smoke testing, roughly thirty-five characters long or so.", note="", standard="everyday sense") for i, t in enumerate(sum(([k]*v for k, v in TIER.items()), []))]
    else:
        for tier, n in TIER.items():
            taken = "、".join(g["term"] for g in G) or "(none)"
            p = GLOSS_PROMPT.format(scenario=a.scenario, n=n, lens=json.dumps(LEN, ensure_ascii=False), tiers=json.dumps({tier: n}, ensure_ascii=False), tier_desc=tier_desc)
            p += f"\n\nThis time only generate {n} entries for tier {tier} (each entry's tier field must be {tier}). Terms already generated that must not be repeated: {taken}. The word-length distribution constraint is an overall constraint for all 43 entries; this batch should roughly follow the proportion (mostly 2-character words)."
            for attempt in range(3):
                txt = gen.complete(p + ("" if attempt == 0 else f"\n\n(Retry {attempt}: previous count or tier didn't match, please strictly output {n} entries, tier all {tier})"), max_tokens=4000, temperature=0.7)
                arr = [g for g in ((extract_json(txt) or {}).get("terms") or []) if isinstance(g, dict) and g.get("term") and g.get("definition")]
                arr = [dict(g, tier=tier) for g in arr if g["term"] not in {x["term"] for x in G}]
                if len(arr) >= n: G += arr[:n]; break
            else:
                G += arr[:n]; print(f"[gloss] WARNING tier {tier}: only {len(arr)} generated", file=sys.stderr)
    G = G[:len(TF)]
    print(f"[gloss] {len(G)} terms; tiers {json.dumps({t: sum(1 for g in G if g.get('tier')==t) for t in TIER}, ensure_ascii=False)}; "
          f"len dist {json.dumps({L: sum(1 for g in G if len(g['term'])==L) for L in sorted({len(g['term']) for g in G})})}", file=sys.stderr)
    # tf allocation: prioritize giving high tf to shifted/narrower (consistent with private corpus: core jargon appears most)
    order = sorted(range(len(G)), key=lambda i: {"shifted": 0, "narrower": 1, "opposite": 1, "none": 2, "unknown": 3}[G[i].get("tier", "none")] + rng.random()*0.5)
    tfs = sorted(TF, reverse=True); tf_of = {}
    for rank, i in enumerate(order): tf_of[i] = tfs[rank]
    # 2) Sentences + QA
    reqs = []
    for i, g in enumerate(G):
        n = tf_of[i]; nb = max(1, round(n * 0.6))
        reqs.append(dict(prompt=SENT_PROMPT.format(scenario=a.scenario, term=g["term"], definition=g["definition"], n=n, n_bearing=nb,
                                                    note_line=f"\n  Volatile annotation (can appear as fact in the sentence, but do not explain it): {g['note']}" if g.get("note") else "",
                                                    std_line=f"\n  The word's everyday public meaning (how outsiders would understand it): {g['standard']}" if g.get("standard") else ""),
                         max_tokens=4000, temperature=0.8))
    outs = gen.complete_many(reqs)
    packs = []
    for g, o in zip(G, outs):
        pk = extract_json(o) or {}
        if a.mock or not pk.get("sentences"):
            pk = dict(sentences=[f"Today {g['term']} had a problem again, Xiao Wang please note it down."]*tf_of[G.index(g)], spans=[g["term"]]*tf_of[G.index(g)],
                      qa=[dict(q=f"What does {g['term']} mean here?", options=["internal meaning", "everyday sense", "other", "neither"], answer="A", sense="corpus")]*3)
        packs.append(pk)
    # 3) Audit
    areqs = [dict(prompt=AUDIT_PROMPT.format(term=g["term"], definition=g["definition"], sents="\n".join(f"{k+1}. {s}" for k, s in enumerate(pk["sentences"]))), max_tokens=1500, temperature=0.0) for g, pk in zip(G, packs)]
    aouts = judge.complete_many(areqs); n_bad = 0
    for g, pk, ao in zip(G, packs, aouts):
        arr = extract_json(ao) if not a.mock else None
        if isinstance(arr, list):
            keep = [k for k, v in enumerate(arr) if str(v).strip().upper().startswith("OK")]
            n_bad += len(pk["sentences"]) - len(keep)
            if keep:
                pk["sentences"] = [pk["sentences"][k] for k in keep if k < len(pk["sentences"])]
                pk["spans"] = [pk.get("spans", [None]*99)[k] if k < len(pk.get("spans", [])) else None for k in keep]
    print(f"[audit] dropped {n_bad} sentences", file=sys.stderr)
    # 4) Assembly
    terms, all_sents = [], []
    for i, (g, pk) in enumerate(zip(G, packs)):
        ctx = [s for s in pk["sentences"] if g["term"] in s]
        if len(ctx) < 2: continue
        gloss = g["definition"] + (f"(Note: {g['note']})" if g.get("note") else "")
        terms.append(dict(id=f"mirror:{g['term']}", term=g["term"], lang="zh", contexts=ctx, spans=(pk.get("spans") or [None]*len(ctx))[:len(ctx)], gloss_gold=g["definition"], gloss_note=g.get("note", ""),
                          standard=g.get("standard", ""), labels=dict(source="mirror", quadrant={"none": "prior_consistent", "unknown": "no_prior"}.get(g["tier"], "prior_conflict"), tier_design=g["tier"], tf=len(ctx), is_target=True, variant="main", n_words=1),
                          qa=[dict(question=q["q"], options=q["options"], answer=q["answer"], depends_on=g["term"], sense=q.get("sense", "corpus")) for q in pk.get("qa", [])[:3]]))
        all_sents += ctx
    rng.shuffle(all_sents)
    with open(os.path.join(a.out, "terms.jsonl"), "w", encoding="utf-8") as f:
        for t in terms: f.write(json.dumps(t, ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "corpus.jsonl"), "w", encoding="utf-8") as f:
        for d in range(a.n_docs): f.write(json.dumps(dict(doc_id=f"note{d+1:02d}", text="\n".join(all_sents[d::a.n_docs])), ensure_ascii=False) + "\n")
    with open(os.path.join(a.out, "glossary.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["term", "tier_design", "definition", "note", "standard_meaning", "tf"])
        for t in terms: w.writerow([t["term"], t["labels"]["tier_design"], t["gloss_gold"], t["gloss_note"], t["standard"], t["labels"]["tf"]])
    json.dump(dict(scenario=a.scenario, n_terms=len(terms), n_sentences=len(all_sents), n_docs=a.n_docs, tf=sorted(t["labels"]["tf"] for t in terms),
                   tiers={t: sum(1 for x in terms if x["labels"]["tier_design"] == t) for t in TIER}, spec_source="distributional parameters of the private corpus only; no text was used"),
              open(os.path.join(a.out, "MIRROR_SPEC.json"), "w"), ensure_ascii=False, indent=1)
    print(f"[mirror] {len(terms)} terms / {len(all_sents)} sentences / {a.n_docs} docs → {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
