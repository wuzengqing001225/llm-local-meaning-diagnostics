# -*- coding: utf-8 -*-
"""Text utilities (tokenization, masking, F1, JSON extraction) and statistics utilities (AUROC, Spearman, bootstrap, partial correlation)."""
import json
import math
import random
import re

_TOK = re.compile(r"[A-Za-z0-9_&']+")


def tokens(s):
    return _TOK.findall(s or "")


def norm_tokens(s):
    return [t.lower().strip("'") for t in tokens(s) if t.strip("'")]


def token_f1(pred, gold):
    p, g = norm_tokens(pred), norm_tokens(gold)
    if not p or not g:
        return 0.0
    from collections import Counter
    common = sum((Counter(p) & Counter(g)).values())
    if common == 0:
        return 0.0
    prec, rec = common / len(p), common / len(g)
    return 2 * prec * rec / (prec + rec)


def find_term(sentence, term):
    """Return the (start, end) character position of the term in the sentence; return None if not found. Case-insensitive, word boundaries."""
    pat = r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])"
    m = re.search(pat, sentence, flags=re.IGNORECASE)
    if not m:
        m = re.search(re.escape(term), sentence, flags=re.IGNORECASE)
    return (m.start(), m.end()) if m else None


def mask_span(sentence, span):
    """Replace the given span (substring in the sentence) with ____; return None if the span is not in the sentence."""
    i = sentence.find(span)
    if i < 0:
        i = sentence.lower().find(span.lower())
        if i < 0:
            return None
        span = sentence[i:i + len(span)]
    return sentence[:i] + "____" + sentence[i + len(span):], span


def mask_window(sentence, term, window=4):
    """Fallback when no span annotation exists: mask the window words after the term (or before it, if at sentence end). Returns (masked, span) or None."""
    pos = find_term(sentence, term)
    if not pos:
        return None
    after = sentence[pos[1]:]
    toks = list(_TOK.finditer(after))
    toks = [t for t in toks if t.group(0)]
    if len(toks) >= 2:
        sel = toks[:window]
        s, e = pos[1] + sel[0].start(), pos[1] + sel[-1].end()
    else:
        before = sentence[:pos[0]]
        toks = list(_TOK.finditer(before))
        if len(toks) < 2:
            return None
        sel = toks[-window:]
        s, e = sel[0].start(), sel[-1].end()
    return sentence[:s] + "____" + sentence[e:], sentence[s:e]


def extract_json(s):
    m = re.search(r"\{.*\}", s or "", flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:  # noqa
        return None


# ----------------------------------------------------------------- Statistics
def mean(xs):
    xs = [x for x in xs if x == x]
    return sum(xs) / len(xs) if xs else float("nan")


def rankdata(xs):
    idx = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and xs[idx[j + 1]] == xs[idx[i]]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[idx[k]] = r
        i = j + 1
    return ranks


def pearson(x, y):
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sxx * syy)


def spearman(x, y):
    pairs = [(a, b) for a, b in zip(x, y) if a == a and b == b]
    if len(pairs) < 3:
        return float("nan")
    return pearson(rankdata([p[0] for p in pairs]), rankdata([p[1] for p in pairs]))


def spearman_perm_p(x, y, n_perm=2000, seed=0):
    rho = spearman(x, y)
    if rho != rho:
        return rho, float("nan")
    rng = random.Random(seed)
    y2 = list(y)
    cnt = 0
    for _ in range(n_perm):
        rng.shuffle(y2)
        r = spearman(x, y2)
        if r == r and abs(r) >= abs(rho) - 1e-12:
            cnt += 1
    return rho, (cnt + 1) / (n_perm + 1)


def auroc(pos, neg):
    pos = [p for p in pos if p == p]
    neg = [n for n in neg if n == n]
    if not pos or not neg:
        return float("nan")
    s = 0.0
    for p in pos:
        for n in neg:
            s += 1.0 if p > n else (0.5 if p == n else 0.0)
    return s / (len(pos) * len(neg))


def auroc_ci(pos, neg, n_boot=1000, seed=0):
    pos = [p for p in pos if p == p]
    neg = [n for n in neg if n == n]
    if len(pos) < 2 or len(neg) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    vals = []
    for _ in range(n_boot):
        bp = [rng.choice(pos) for _ in pos]
        bn = [rng.choice(neg) for _ in neg]
        vals.append(auroc(bp, bn))
    vals.sort()
    return vals[int(0.025 * n_boot)], vals[int(0.975 * n_boot) - 1]


def bootstrap_mean_ci(xs, n_boot=1000, seed=0):
    xs = [x for x in xs if x == x]
    if len(xs) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    vals = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(n_boot))
    return vals[int(0.025 * n_boot)], vals[int(0.975 * n_boot) - 1]


def partial_spearman(y, x, covs):
    """Rank-transform, then take OLS residuals on covariates, then correlate residuals (partial Spearman)."""
    n = len(y)
    if n < 5:
        return float("nan")
    ry, rx = rankdata(y), rankdata(x)
    rc = [rankdata(c) for c in covs]
    X = [[1.0] + [c[i] for c in rc] for i in range(n)]

    def solve(A, b):
        m = len(A)
        M = [row[:] + [b[i]] for i, row in enumerate(A)]
        for col in range(m):
            piv = max(range(col, m), key=lambda r: abs(M[r][col]))
            if abs(M[piv][col]) < 1e-12:
                return None
            M[col], M[piv] = M[piv], M[col]
            for r in range(m):
                if r != col:
                    f = M[r][col] / M[col][col]
                    for c in range(col, m + 1):
                        M[r][c] -= f * M[col][c]
        return [M[i][m] / M[i][i] for i in range(m)]

    def resid(v):
        k = len(X[0])
        A = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
        bvec = [sum(X[i][a] * v[i] for i in range(n)) for a in range(k)]
        beta = solve(A, bvec)
        if beta is None:
            return None
        return [v[i] - sum(beta[j] * X[i][j] for j in range(k)) for i in range(n)]

    ey, ex = resid(ry), resid(rx)
    if ey is None or ex is None:
        return float("nan")
    return pearson(ey, ex)