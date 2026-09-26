from pathlib import Path
exec((Path(__file__).resolve().parent/'recompute.py').read_text().split('results=[]')[0])
extra={}
# Recompute occurrence policy values from complete paired intervention outcomes.
occ=[]
for fn in ['occ_ab_v1.jsonl','occ_ab_cuad.jsonl']:
 rr=load(fn);n=len(rr);risk=np.array([r['risk'] for r in rr]);b=np.array([r['bare'] for r in rr]);i=np.array([r['inline'] for r in rr]);gain=i-b
 cl=[dict(cluster=':'.join(r['id'].split(':')[:2]) if r['id'].startswith('cuad:') else r['id']) for r in rr]
 tm=collections.defaultdict(list)
 for j,r in enumerate(rr):tm[r['id']].append(j)
 tr=np.array([np.mean([risk[j] for j in tm[r['id']]]) for r in rr]);curves=[]
 for frac in [0,.05,.1,.2,.3,.5,1]:
  k=int(np.ceil(n*frac));sel=np.argsort(-risk,kind='stable')[:k];selterm=np.argsort(-tr,kind='stable')[:k]
  curves.append(dict(budget=frac,k=k,risk_gain=float(gain[sel].sum()/n),term_gain=float(gain[selterm].sum()/n),random_expected_gain=float(k/n*gain.mean()),oracle_gain=float(np.sort(gain)[::-1][:k].sum()/n),repair_capture=float(((b[sel]==0)&(i[sel]==1)).sum()/((b==0)&(i==1)).sum()) if ((b==0)&(i==1)).any() else None))
 occ.append(dict(file=fn,n=n,bare=float(b.mean()),inline=float(i.mean()),repair=int(((b==0)&(i==1)).sum()),harm=int(((b==1)&(i==0)).sum()),net_ci=clustered(cl,lambda ii:gain[ii].mean()),risk_auc=auc(1-b,risk),curves=curves))
extra['occurrence']=occ
# Scaling on intersection of all six proxies and exactly matched question strings.
fns=['scaling_Qwen_Qwen2.5-0.5B.jsonl','scaling_Qwen_Qwen2.5-1.5B.jsonl','scaling_Qwen_Qwen2.5-3B.jsonl','lpmc_v1.jsonl','lpmc_v1_qwen14b.jsonl','lpmc_v1_llama8b.jsonl']
allrows={fn:pair(fn,'v1_eqa.jsonl') for fn in fns};keys=set.intersection(*({(r['id'],r['q']) for r in rr} for rr in allrows.values()));extra['scaling']=[]
for fn,rr in allrows.items():
 rr=[r for r in rr if (r['id'],r['q']) in keys];extra['scaling'].append(dict(file=fn,n=len(rr),auc=auc([r['fail'] for r in rr],[r['risk'] for r in rr])))
# Public forum items: qid alone repeats when two terms share a post; use (qid,term).
extra['rqa']=[]
for fn in ['rqa_answers_gpt.jsonl','rqa_answers_deepseek41.jsonl']:
 by=collections.defaultdict(dict)
 for r in load(fn):by[r['arm']][(r['qid'],r['term'])]=r
 ks=sorted(set.intersection(*(set(v) for v in by.values())));cl=[dict(cluster=by['plain'][k]['subreddit']) for k in ks];b=np.array([by['plain'][k]['correct'] for k in ks]);o=dict(file=fn,n=len(ks),unique_posts=len(set(k[0] for k in ks)),arms={})
 for a in by:
  x=np.array([by[a][k]['correct'] for k in ks]);o['arms'][a]=dict(accuracy=float(x.mean()),delta=float(np.mean(x-b)),ci=clustered(cl,lambda ii:np.mean((x-b)[ii])))
 extra['rqa'].append(o)
# Uniform condition summaries without pretending channel groupings identify causes.
extra['channels']={fn:dict(collections.Counter(r.get('channel_qa') for r in load(fn) if r.get('n_q',0)>0)) for fn in ['v1_eqa.jsonl','reddit_eqa.jsonl','cuad_eqa_gold_deepseek.jsonl','defi_strict_eqa.jsonl']}
# Detect mismatches of sampled questions with greedy ground truth.
u=load('unc_v1.jsonl');E={r['id']:r for r in load('v1_eqa.jsonl')};extra['unc_alignment']={'matched':0,'mismatch':0}
for r in u:
 for j,q in enumerate(r['per_question']):
  p=E[r['id']]['questions'][j];ok=p['q'].startswith(q['q']) or q['q'].startswith(p['q']);extra['unc_alignment']['matched' if ok else 'mismatch']+=1
# Source dates/cutoffs and undocumented model labels are not guessed.
(OUT/'extra_results.json').write_text(json.dumps(extra,indent=2));print(json.dumps(extra,indent=2))
