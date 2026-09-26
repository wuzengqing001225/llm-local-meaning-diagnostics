# -*- coding: utf-8 -*-
"""
Estimators (ALGORITHM.md §5). All implemented as "build requests first, batch-call, then score" for concurrency across terms.

  rarity(term)                      Common-language rarity = 8 − zipf (wordfreq; multi-word terms take the minimum zipf)
  subsample(contexts, k, seed)      Context subsampling
  cloze_requests(term, ctxs, spans, glosses, window)  -> (reqs, meta)   Build bare / glossC / glossM cloze requests
  cloze_score(meta, answers)        -> {bare, glossC, glossM, delta_raw, gain_bare, n, delta_ci}
  prior_request(term) / tier_request(term, ctxs, prior)   Self-report probe requests
  aggregate(tf_norm, cz)            -> {delta_hat, weight, deficit}
"""
import math
import random

from .text import mask_span, mask_window, token_f1, extract_json, bootstrap_mean_ci

try:
    from wordfreq import zipf_frequency
except ImportError:  # pragma: no cover
    zipf_frequency = None

CLOZE_SYSTEM = ("Fill in the blank marked ____ in the sentence. Output only the missing words, "
                "nothing else. Do not explain.")
CLOZE_BARE = "Sentence: {masked}\nMissing words:"
CLOZE_GLOSS = "Term note: \"{term}\" — {gloss}\n\nSentence: {masked}\nMissing words:"

PRIOR_PROMPT = ("PRIOR_MEANING. In one sentence, what does the term \"{term}\" mean? "
                "Answer from your own knowledge only. If you do not know the term, answer exactly UNKNOWN.")
# v0.3: in-context prior — give a domain hint (no corpus sentences), to obtain the meaning the model would default to in that domain
PRIOR_CTX_PROMPT = ("PRIOR_MEANING. Domain: {domain}\n"
                    "In one sentence, what would you assume the term \"{term}\" means when it appears in documents "
                    "from this domain? Answer from your own knowledge only. If it is an ordinary word or a standard term of the "
                    "field, state the meaning you would expect it to carry here (do not invent a special in-house sense). "
                    "Answer exactly UNKNOWN only if you genuinely have no idea what the term could mean.")
TIER_PROMPT = ("TIER_JSON. A reader believes the term \"{term}\" means: {prior}\n"
               "Below are usages of the term from a specific corpus:\n{contexts}\n\n"
               "Compare the corpus usage with the reader's belief and classify:\n"
               "  none      — same meaning\n"
               "  narrower  — corpus uses a more specific sense of the same meaning\n"
               "  shifted   — a different but related meaning\n"
               "  opposite  — contradicts the reader's belief\n"
               "  unknown   — the reader has no belief (UNKNOWN) or the term is invented\n"
               "Answer as JSON only: {{\"tier\": \"...\", \"corpus_meaning\": \"one sentence\"}}")

# v0.3.1: morphology-guess probe when there is no prior (allow guessing from word form/morphology; answer UNKNOWN when truly opaque)
GUESS_PROMPT = ("PRIOR_MEANING. Domain: {domain}\n"
                "You have never seen the term \"{term}\" before. Based only on how the word is formed (its parts, capitalisation, "
                "resemblance to known words), give your single best one-sentence guess of what it means in this domain. "
                "If the form gives you nothing to go on, answer exactly UNKNOWN.")


def guess_request(term, domain):
    return dict(prompt=GUESS_PROMPT.format(term=term, domain=domain or "unspecified"), max_tokens=100, temperature=0.0)


TIERS = ["none", "narrower", "shifted", "opposite", "unknown"]


def rarity(term, lang="en"):
    if zipf_frequency is None:
        return float("nan")
    parts = [p for p in term.replace("_", " ").split() if p]
    if not parts:
        return float("nan")
    z = min(zipf_frequency(p, lang) for p in parts)
    if z == 0:
        z = zipf_frequency(term, lang)
    return 8.0 - z


def subsample(contexts, k, seed=1):
    if len(contexts) <= k:
        return list(contexts)
    rng = random.Random(seed)
    return rng.sample(list(contexts), k)


def cloze_requests(term, ctxs, spans, glosses, window=4, max_tokens=16):
    """
    glosses: dict of condition name -> gloss text or None (None marks the bare condition). Example:
             {"bare": None, "glossC": gloss_C, "glossM": gloss_M}
    Returns (reqs, meta), where meta[i] = (cond, ctx_index, gold_span)
    """
    reqs, meta = [], []
    for ci, c in enumerate(ctxs):
        sp = spans[ci] if spans and ci < len(spans) and spans[ci] else None
        m = mask_span(c, sp) if sp else None
        if m is None:
            m = mask_window(c, term, window)
        if m is None:
            continue
        masked, gold = m
        for cond, g in glosses.items():
            if cond != "bare" and not g:
                continue
            p = CLOZE_BARE.format(masked=masked) if cond == "bare" else \
                CLOZE_GLOSS.format(term=term, gloss=g, masked=masked)
            reqs.append(dict(prompt=p, system=CLOZE_SYSTEM, max_tokens=max_tokens, temperature=0.0))
            meta.append((cond, ci, gold))
    return reqs, meta


def cloze_score(meta, answers):
    per = {}
    for (cond, ci, gold), ans in zip(meta, answers):
        per.setdefault(cond, {})[ci] = token_f1(ans, gold)
    out = {"n": len(per.get("bare", {}))}
    for cond, d in per.items():
        out[cond] = sum(d.values()) / len(d) if d else float("nan")
    common = set(per.get("glossC", {})) & set(per.get("glossM", {}))
    if common:
        diffs = [per["glossC"][i] - per["glossM"][i] for i in sorted(common)]
        out["delta_raw"] = sum(diffs) / len(diffs)
        out["delta_ci"] = list(bootstrap_mean_ci(diffs))
    else:
        out["delta_raw"] = float("nan")
        out["delta_ci"] = [float("nan")] * 2
    cb = set(per.get("glossC", {})) & set(per.get("bare", {}))
    if cb:
        d2 = [per["glossC"][i] - per["bare"][i] for i in sorted(cb)]
        out["gain_bare"] = sum(d2) / len(d2)
        out["gain_bare_ci"] = list(bootstrap_mean_ci(d2))
    else:
        out["gain_bare"] = float("nan")
        out["gain_bare_ci"] = [float("nan")] * 2
    return out


def prior_request(term, domain=None):
    if domain:
        return dict(prompt=PRIOR_CTX_PROMPT.format(term=term, domain=domain), max_tokens=100, temperature=0.0)
    return dict(prompt=PRIOR_PROMPT.format(term=term), max_tokens=100, temperature=0.0)


def is_unknown(text):
    return (text or "").strip().upper().startswith("UNKNOWN")


def tier_request(term, ctxs, prior):
    ctx = "\n".join(f"- {c}" for c in ctxs[:8])
    return dict(prompt=TIER_PROMPT.format(term=term, prior=prior or "UNKNOWN", contexts=ctx),
                max_tokens=120, temperature=0.0)


def parse_tier(text):
    o = extract_json(text)
    if o and str(o.get("tier", "")).lower() in TIERS:
        return str(o["tier"]).lower(), o.get("corpus_meaning")
    low = (text or "").lower()
    for t in TIERS:
        if t in low:
            return t, None
    return None, None


def aggregate(tf_norm, cz, prior_unknown=False, channel=None):
    """
    v0.3 dual channel:
      conflict channel (prior available): delta_hat = clip(glossC − glossM_ctx); weight_conflict = tf_norm · delta_hat
      unknown  channel (no prior): score_unknown = deficit = 1 − bare; weight_unknown = tf_norm · deficit
    weight (single ranking score) = the score of the applicable channel; the channel field indicates the source. Budgeting and evaluation are done separately per channel.
    """
    d = cz.get("delta_raw", float("nan"))
    dh = min(max(d, 0.0), 1.0) if d == d else float("nan")
    gb = cz.get("gain_bare", float("nan"))
    bare = cz.get("bare", float("nan"))
    deficit = (1 - bare) if bare == bare else float("nan")
    out = {"delta_hat": dh, "gain_bare_hat": min(max(gb, 0.0), 1.0) if gb == gb else float("nan"),
           "deficit": deficit, "channel": channel or ("unknown" if prior_unknown else "conflict"),
           "weight_conflict": tf_norm * dh if (dh == dh and not prior_unknown) else float("nan"),
           "weight_unknown": tf_norm * deficit if (deficit == deficit and prior_unknown) else float("nan")}
    if prior_unknown:
        out["weight"] = out["weight_unknown"]
    else:
        out["weight"] = out["weight_conflict"]
    return out