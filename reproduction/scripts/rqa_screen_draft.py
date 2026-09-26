# -*- coding: utf-8 -*-
"""Reddit natural question posts: two-stage screen (community sense / dependence / reply-is-answer) -> for eligible posts, draft a four-option multiple-choice item from the top-voted reply. Executed by host.llm (runs inside a sub-agent).
Usage (python kernel): exec(open("rqa_screen_draft.py").read()); run(host, "qa_posts.jsonl", "out/", shard_k, shard_n)"""
import json, re, os
SCREEN = """A question was posted in the online community r/{sub}. The community's own glossary defines "{term}" as: {gloss}

POST TITLE: {title}
POST BODY: {body}
TOP-VOTED REPLY: {gold}

Answer JSON only:
{{"uses_community_sense": true/false, "answer_depends_on_sense": true/false, "reply_is_answer": true/false}}
uses_community_sense: does the post use "{term}" in the glossary sense above (not the everyday sense)?
answer_depends_on_sense: would a reader who takes "{term}" in its everyday sense misunderstand the question or the reply?
reply_is_answer: is the top reply actually an answer to the question (not a joke / tangent)?"""
DRAFT = """Turn a real community Q&A into ONE four-option multiple-choice item. Do not change the question; keep the community's wording.
Community: r/{sub}. Glossary term in the question: "{term}" (community sense: {gloss}).
QUESTION (title + body): {title} {body}
CORRECT ANSWER (top-voted human reply, paraphrase it into one concise option that preserves its substance): {gold}
OTHER REPLIES (may be used as distractors if they contradict the correct one): {others}
Rules: (1) exactly one option is faithful to the top-voted reply; (2) one distractor is what someone would answer if they took "{term}" in its EVERYDAY sense; (3) the other two are plausible community-flavoured but wrong; (4) options are similar in length and style; (5) do not restate the glossary definition inside any option.
Output JSON only: {{"q": "<the question, lightly cleaned>", "options": ["...","...","...","..."], "answer": "A|B|C|D", "everyday_distractor": "A|B|C|D"}}"""
def _b(t, k):
    m = re.search(rf'"{k}"\s*:\s*(true|false)', t or "", re.I); return (m.group(1).lower() == "true") if m else None
def run(host, inp, out_dir, k=0, n=1):
    os.makedirs(out_dir, exist_ok=True)
    Q = [json.loads(l) for i, l in enumerate(open(inp, encoding="utf-8")) if i % n == k]
    res = host.llm([dict(prompt=SCREEN.format(sub=q["subreddit"], term=q["term"], gloss=q["gloss_gold"][:250], title=q["title"], body=(q["selftext"][:500] or "(none)"), gold=q["gold_answer"][:500]), max_tokens=200) for q in Q], max_concurrency=8)
    for q, r in zip(Q, res):
        t = r.get("text") or ""; q["screen"] = {x: _b(t, x) for x in ("uses_community_sense", "answer_depends_on_sense", "reply_is_answer")}
    elig = [q for q in Q if q["screen"]["uses_community_sense"] and q["screen"]["reply_is_answer"]]
    res2 = host.llm([dict(prompt=DRAFT.format(sub=q["subreddit"], term=q["term"], gloss=q["gloss_gold"][:250], title=q["title"], body=q["selftext"][:500], gold=q["gold_answer"][:600], others="\n".join("- " + o[:250] for o in q["other_answers"][:4]) or "(none)"), max_tokens=700) for q in elig], max_concurrency=8)
    n_ok = 0
    for q, r in zip(elig, res2):
        t = r.get("text") or ""; m = re.search(r"\{.*\}", t, re.S)
        try:
            j = json.loads(m.group(0)); assert len(j["options"]) == 4 and j["answer"] in "ABCD"; q["mc"] = j; n_ok += 1
        except Exception: q["mc"] = None
    with open(os.path.join(out_dir, f"rqa_screened_{k}.jsonl"), "w", encoding="utf-8") as f:
        for q in Q: f.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(json.dumps({"shard": k, "posts": len(Q), "screened_ok": sum(1 for q in Q if q["screen"]["uses_community_sense"] is not None), "eligible": len(elig),
                      "depends_on_sense": sum(1 for q in elig if q["screen"]["answer_depends_on_sense"]), "mc_drafted": n_ok}))