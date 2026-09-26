"""Offline audit; reads source artifacts, writes aggregate summaries only. No model calls.
Usage: python recompute.py [Workbench path]
"""
from pathlib import Path
import json,sys,collections,csv,hashlib
import numpy as np
from scipy.stats import rankdata
if len(sys.argv)<2:
 raise SystemExit('Usage: python recompute.py /path/to/Workbench')
ROOT=Path(sys.argv[1])
DATA=ROOT/'data'; OUT=Path(__file__).resolve().parent/'results'; OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(20260922)
index=collections.defaultdict(list)
for p in DATA.rglob('*'):
 if p.is_file():index[p.name].append(p)
def load(fn):
 ps=index[fn]
 if len(ps)!=1:raise ValueError((fn,len(ps)))
 p=ps[0];return [json.loads(x) for x in p.read_text().splitlines()] if p.suffix=='.jsonl' else json.loads(p.read_text())
def auc(y,s,w=None):
 y=np.asarray(y);s=np.asarray(s);w=np.ones(len(y)) if w is None else np.asarray(w)
 order=np.argsort(s,kind='stable');y=y[order];s=s[order];w=w[order]
 starts=np.r_[0,np.flatnonzero(np.diff(s))+1];pos=np.add.reduceat(w*y,starts);neg=np.add.reduceat(w*(1-y),starts)
 return float(np.sum(pos*(np.cumsum(neg)-neg/2))/(sum(pos)*sum(neg))) if sum(pos)*sum(neg)>0 else np.nan
def interval(arr):return [float(x) for x in np.nanquantile(arr,[.025,.975])]
def clustered(rows,stat,B=2000):
 ids=list(dict.fromkeys(r['cluster'] for r in rows));groups={k:[] for k in ids}
 for i,r in enumerate(rows):groups[r['cluster']].append(i)
 arrays=[np.array(groups[k]) for k in ids]; vals=[]
 for _ in range(B):
  ii=np.concatenate([arrays[j] for j in rng.integers(len(ids),size=len(ids))]);vals.append(stat(ii))
 return interval(vals)
def cluster_id(r):
 lab=r.get('labels') or {};i=r['id']
 if i.startswith(('cuad:','cuadfull:','reddit:')):return ':'.join(i.split(':')[:2])
 return i
align=[];matched={}
def pair(lpfn,efn,ctx=False):
 lp=load(lpfn);E={r['id']:r for r in load(efn)};rows=[];mismatch=0;unlabelled=0
 for r in lp:
  e=E.get(r['id'])
  if not e:continue
  eq=e.get('questions',[])
  for j,p in enumerate(r.get('per_question') or []):
   qq=[q for q in eq if str(q.get('ctx_idx'))==str(p.get('ctx_idx'))] if ctx else eq[j:j+1]
   if len(qq)!=1:continue
   q=qq[0]
   if not (q.get('q','').startswith(p.get('q','')) or p.get('q','').startswith(q.get('q',''))):mismatch+=1;continue
   c=q.get('correct') or {}
   if c.get('bare') is None:unlabelled+=1;continue
   pb=p['bare']['p_correct'];pc=p['glossC']['p_correct'];cb=c['bare'];cc=c.get('glossC')
   rows.append(dict(id=r['id'],cluster=cluster_id(e),risk=1-pb,pd=pc-pb,p_def=pc,fail=1-cb,repair=int(cb==0 and cc==1),harm=int(cb==1 and cc==0),bare=cb,definition=cc,q=q['q']))
 align.append(dict(proxy=lpfn,reader=efn,n=len(rows),mismatched_stems=mismatch,unlabelled=unlabelled))
 return rows
settings=[('Synthetic / DeepSeek','lpmc_v1.jsonl','v1_eqa.jsonl',False),('Synthetic / GPT6','lpmc_v1.jsonl','astra6_v1_eqa.jsonl',False),('Reddit / DeepSeek','lpmc_reddit.jsonl','reddit_eqa.jsonl',False),('Reddit / GPT6','lpmc_reddit.jsonl','astra6_reddit_eqa.jsonl',False),('DeFi / DeepSeek','defi_strict_lpmc.jsonl','defi_strict_eqa.jsonl',False),('DeFi / GPT5.6','defi_strict_lpmc.jsonl','defi_strict_eqa_gpt.jsonl',False),('DeFi / GPT6','defi_strict_lpmc.jsonl','astra6_defi_strict_eqa.jsonl',False),('CUAD library / GPT5.6','lpmc_full.jsonl','t2_answers.jsonl',True)]
results=[]
for name,l,e,c in settings:
 rows=pair(l,e,c);matched[name]=rows;y=np.array([r['fail'] for r in rows]);s=np.array([r['risk'] for r in rows]);d=np.array([r['pd'] for r in rows]);rep=np.array([r['repair'] for r in rows])
 out=dict(setting=name,n=len(rows),clusters=len(set(r['cluster'] for r in rows)),failure=float(y.mean()),definition_accuracy=float(np.mean([r['definition'] for r in rows])),risk_auc=auc(y,s),pd_auc=auc(y,d),risk_repair_auc=auc(rep,s),pd_repair_auc=auc(rep,d),risk_ci=clustered(rows,lambda ii:auc(y[ii],s[ii])),pd_minus_risk_ci=clustered(rows,lambda ii:auc(y[ii],d[ii])-auc(y[ii],s[ii]),1000))
 results.append(out)
# Reader results with missing question labels: term aggregates are retained, never fabricated as question labels.
term_only=[]
for lpfn,efn in [('lpmc_v1.jsonl','eqa_v1_sonnet_samequestions.jsonl'),('lpmc_cuad_usage.jsonl','cuad_eqa_usage_deepseek.jsonl'),('lpmc_cuad_v2.jsonl','cuad_eqa_gold_deepseek.jsonl')]:
 rows=pair(lpfn,efn);LP={r['id']:r for r in load(lpfn)};es=[e for e in load(efn) if e['id'] in LP and e.get('acc_bare') is not None]
 term_only.append(dict(proxy=lpfn,reader=efn,terms=len(es),questions=sum(e.get('n_q',0) for e in es),accuracy_weighted=sum(e['acc_bare']*e['n_q'] for e in es)/sum(e['n_q'] for e in es),any_error_term_auc=auc([e['acc_bare']<1 for e in es],[LP[e['id']]['fail_pred_bare'] for e in es])))
# Risk stratification is not probability calibration; compute survey-weighted results over eligible frame.
full=[p for r in load('lpmc_full.jsonl') for p in (r.get('per_question') or [])];bins=lambda v:min(4,int(v*5))
N=collections.Counter(bins(1-p['bare']['p_correct']) for p in full);rows=matched['CUAD library / GPT5.6'];nn=collections.Counter(bins(r['risk']) for r in rows)
w=np.array([N[bins(r['risk'])]/nn[bins(r['risk'])] for r in rows]);y=np.array([r['fail'] for r in rows]);s=np.array([r['risk'] for r in rows]);d=np.array([r['pd'] for r in rows])
weighted=dict(frame_n=len(full),frame_bins=dict(N),sample_bins=dict(nn),weighted_failure=float(np.average(y,weights=w)),weighted_risk_auc=auc(y,s,w),weighted_pd_auc=auc(y,d,w),sampling_assumption='Seed-42 stratified shuffle exactly reproduces the 1500 released IDs, with 300 per stratum.')
cuad_trans=collections.Counter((r['bare'],r['definition']) for r in rows);weighted['transitions']={str(k):v for k,v in cuad_trans.items()};weighted['bins']=[dict(bin=i,n=nn[i],frame_n=N[i],failure=np.mean([r['fail'] for r in rows if bins(r['risk'])==i])) for i in range(5)]
# RAG matched paired contrasts, document/community bootstrap.
rag=[]
for corpus,tier,fn in [('CUAD','BM25','rag_v3_bm25.jsonl'),('CUAD','dense','rag_v3_t2.jsonl'),('CUAD','hybrid','rag_v3_t1.jsonl'),('Reddit','BM25','rag_reddit_bm25.jsonl'),('Reddit','hybrid','rag_reddit_t1.jsonl')]:
 by=collections.defaultdict(dict)
 for r in load(fn):by[r['arm']][r['qkey']]=r
 keys=sorted(set.intersection(*(set(v) for v in by.values())))
 for subset in (['all'] if corpus=='CUAD' else ['all','glossary','control']):
  ks=[k for k in keys if subset=='all' or (by['rag'][k]['quadrant']=='control')==(subset=='control')]
  B=np.array([by['rag'][k]['correct'] for k in ks]);G=np.array([by['rag_gated'][k]['correct'] for k in ks]);F=np.array([by['rag_full'][k]['correct'] for k in ks]);cl=[dict(cluster=by['rag'][k]['ci']) for k in ks]
  ts={a:float(np.mean([by[a][k]['inject_tokens'] for k in ks])) for a in by};ts['definition_increment_gated']=ts['rag_gated']-ts['rag'];ts['definition_increment_full']=ts['rag_full']-ts['rag']
  needs=(B==0)&(F==1);no_needs=~needs
  rag.append(dict(corpus=corpus,tier=tier,subset=subset,n=len(ks),clusters=len(set(r['cluster'] for r in cl)),accuracy={a:float(np.mean([by[a][k]['correct'] for k in ks])) for a in by},gated_minus_rag=float(np.mean(G-B)),gated_minus_rag_ci=clustered(cl,lambda ii:np.mean((G-B)[ii])),gated_minus_full=float(np.mean(G-F)),gated_minus_full_ci=clustered(cl,lambda ii:np.mean((G-F)[ii])),tokens=ts,entries={a:float(np.mean([by[a][k]['n_gloss'] for k in ks])) for a in by},need_n=int(needs.sum()),need_fraction=float(needs.mean()),recall=float(G[needs].mean()) if needs.any() else None,harm_rate_among_no_full_repair=float(((B==1)&(G==0))[no_needs].mean()),repair_n=int(((B==0)&(G==1)).sum()),harm_n=int(((B==1)&(G==0)).sum())))
# Same question uncertainty comparison at genuinely shared n.
U={r['id']:r for r in load('unc_v1.jsonl')};E={r['id']:r for r in load('v1_eqa.jsonl')};LP={r['id']:r for r in load('lpmc_v1.jsonl')};unc=[]
for i,r in U.items():
 for j,p in enumerate(r['per_question']):
  q=E[i]['questions'][j];c=q['correct']['bare'];proxy=LP.get(i,{}).get('per_question',[])
  unc.append(dict(cluster=i,y=1-c,consistency=p['consistency'],entropy=p['mc_entropy'],confidence=-p['verb_conf'],identical=max(p['votes'].values())==10,majority=max(p['votes'],key=p['votes'].get),answer=q['answer'],risk=1-proxy[j]['bare']['p_correct'] if j<len(proxy) and q['q'].startswith(proxy[j]['q']) else None))
unc_results=[]
for name,rr in [('full',unc),('proxy_overlap',[r for r in unc if r['risk'] is not None])]:
 y=np.array([r['y'] for r in rr]);unc_results.append(dict(subset=name,n=len(rr),failed=int(y.sum()),identical_failed=sum(r['y'] and r['identical'] for r in rr),identical_wrong_failed=sum(r['y'] and r['identical'] and r['majority']!=r['answer'] for r in rr),aucs={key:auc(y,[r[key] for r in rr]) for key in ['consistency','entropy','confidence']+(['risk'] if name=='proxy_overlap' else [])}))
# Public task outcomes.
public=[]
for fn,unit,metric in [('cuad_bench_answers.jsonl','qid','f1'),('cnli_answers.jsonl',None,'correct'),('rqa_answers_gpt.jsonl','qid','correct'),('rqa_answers_deepseek41.jsonl','qid','correct')]:
 by=collections.defaultdict(dict)
 for r in load(fn):by[r['arm']][(r[unit]+'#'+r['term'] if fn.startswith('rqa') else r[unit]) if unit else str(r['ci'])+'#'+r['hyp']]=r
 ks=sorted(set.intersection(*(set(v) for v in by.values())));base='rag' if 'rag' in by else 'plain';cl=[dict(cluster=by[base][k].get('ci',by[base][k].get('subreddit',k))) for k in ks]
 b=np.array([by[base][k][metric] for k in ks]);o=dict(file=fn,n=len(ks),metric=metric,base=base,arms={})
 for a in by:
  aa=np.array([by[a][k][metric] for k in ks]);o['arms'][a]=dict(mean=float(aa.mean()),delta=float(np.mean(aa-b)),ci=clustered(cl,lambda ii:np.mean((aa-b)[ii]),1000))
 public.append(o)
# Clause alignment is a proxy outcome, not human stakes.
cat=load('cuad_cat_align.json');inside=[r for r in cat if r['cats']];outside=[r for r in cat if not r['cats']]
clauses=dict(n=len(cat),inside_n=len(inside),outside_n=len(outside),inside_boundary=float(np.mean([r['D']>.3 for r in inside])),outside_boundary=float(np.mean([r['D']>.3 for r in outside])))
unrep=load('unrepaired_decomp.json');clauses['unrepaired_audit_n']=len(unrep);clauses['unrepaired_labels']=dict(collections.Counter(r['label'] for r in unrep))
# Completeness ledger for every raw-output file. This is inventory, not an independent replication claim.
ledger=[]
for p in sorted(DATA.rglob('*.jsonl')):
 if 'raw_outputs' not in p.parts:continue
 rr=[json.loads(l) for l in p.open()];groups=collections.defaultdict(list)
 for r in rr:
  key=' / '.join(str(r.get(k,'')) for k in ['set','arm','decode','cond']).strip(' /') or 'all';groups[key].append(r)
 for g,v in groups.items():
  o=dict(file=str(p.relative_to(DATA)),group=g,rows=len(v),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
  for metric in ['correct','f1','bare','inline','ctx_full','ctx_retrieved','acc_bare','acc_glossC','acc_glossM','fail_pred_bare','delta_mc']:
   vv=[r[metric] for r in v if isinstance(r.get(metric),(float,int)) and np.isfinite(r[metric])]
   if vv:o[metric]=float(np.mean(vv))
  ledger.append(o)
with (OUT/'experiment_inventory.tsv').open('w') as f:
 fields=list(dict.fromkeys(k for r in ledger for k in r));cw=csv.DictWriter(f,fields,delimiter='\t');cw.writeheader();cw.writerows(ledger)
summary=dict(settings=results,term_only=term_only,alignment=align,weighted_cuad=weighted,rag=rag,uncertainty=unc_results,public_tasks=public,clauses=clauses)
(OUT/'audit_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False,indent=2))
