"""One-page HTML summary of a risk map: per-document risk density, highest-risk terms, boundary sentences."""
import html
from collections import defaultdict

def render_report(riskmap, title="Prior-divergence risk map", top_terms=25, top_sentences=20):
    m = lambda v: sum(v) / len(v) if v else 0.0
    by_doc, by_term = defaultdict(list), defaultdict(list)
    for r in riskmap:
        by_doc[r.get("doc")].append(r); by_term[(r.get("doc"), r["term"])].append(r)
    n = len(riskmap); hi = sum(r["risk"] >= 0.5 for r in riskmap); bnd = sum(r["pd"] > 0.3 for r in riskmap)
    ch = defaultdict(int)
    for r in riskmap: ch[r["channel"]] += 1
    rows_doc = sorted(((d, len(v), m([r["risk"] >= 0.5 for r in v]), m([r["pd"] for r in v])) for d, v in by_doc.items()), key=lambda x: -x[2])
    rows_term = sorted(((d, t, len(v), m([r["risk"] for r in v]), m([r["pd"] for r in v]), max(v, key=lambda r: r["pd"])["channel"], m([r["repairable"] for r in v]))
                        for (d, t), v in by_term.items()), key=lambda x: -x[4])[:top_terms]
    sents = sorted(riskmap, key=lambda r: -(r["pd"] * r["risk"]))[:top_sentences]
    h = [f"<!doctype html><meta charset='utf-8'><title>{html.escape(title)}</title>",
         "<style>body{font:14px/1.45 system-ui,sans-serif;max-width:1000px;margin:30px auto;color:#222}table{border-collapse:collapse;width:100%;margin:8px 0 22px}"
         "th,td{border-bottom:1px solid #ddd;padding:4px 8px;text-align:left;vertical-align:top}th{background:#f4f4f4}.n{text-align:right;font-variant-numeric:tabular-nums}"
         "h2{margin-top:28px;font-size:17px}.k{display:inline-block;margin:0 18px 8px 0}.k b{font-size:20px}</style>",
         f"<h1>{html.escape(title)}</h1>",
         f"<div><span class='k'><b>{n:,}</b><br>scored occurrences</span><span class='k'><b>{hi / max(n, 1):.0%}</b><br>risk &ge; 0.5</span>"
         f"<span class='k'><b>{bnd / max(n, 1):.0%}</b><br>definition changes the reading (PD &gt; 0.3)</span>"
         f"<span class='k'><b>{ch['conflict']} / {ch['instantiation']} / {ch['consistent']}</b><br>conflict / instantiation / consistent</span></div>",
         "<h2>Documents by risk density</h2><table><tr><th>document</th><th class='n'>occurrences</th><th class='n'>share at risk &ge; 0.5</th><th class='n'>mean PD</th></tr>"]
    h += [f"<tr><td>{html.escape(str(d))}</td><td class='n'>{k}</td><td class='n'>{s:.2f}</td><td class='n'>{p:.2f}</td></tr>" for d, k, s, p in rows_doc]
    h += ["</table><h2>Highest-divergence terms</h2><table><tr><th>document</th><th>term</th><th class='n'>occ.</th><th class='n'>mean risk</th><th class='n'>mean PD</th><th>channel</th><th class='n'>repairable</th></tr>"]
    h += [f"<tr><td>{html.escape(str(d))}</td><td>{html.escape(t)}</td><td class='n'>{k}</td><td class='n'>{rk:.2f}</td><td class='n'>{p:.2f}</td><td>{c}</td><td class='n'>{rep:.0%}</td></tr>" for d, t, k, rk, p, c, rep in rows_term]
    h += ["</table><h2>Boundary sentences (highest risk &times; PD)</h2><table><tr><th>term</th><th>sentence</th><th class='n'>risk</th><th class='n'>PD</th></tr>"]
    h += [f"<tr><td>{html.escape(r['term'])}</td><td>{html.escape((r.get('sentence') or '')[:300])}</td><td class='n'>{r['risk']:.2f}</td><td class='n'>{r['pd']:.2f}</td></tr>" for r in sents]
    h += ["</table><p style='color:#777'>risk = 1 &minus; P(correct option | sentence only); PD = P(correct | definition shown) &minus; P(correct | sentence only); "
          "both from the local proxy model. PD locates where a reading would change if the document's meaning were applied; it does not measure the cost of a misread.</p>"]
    return "\n".join(h)
