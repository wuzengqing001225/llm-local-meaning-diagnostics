"""Recompute synthetic headline metrics with source-conflict exclusions. No API calls."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
DATA=ROOT.parent/'release_20260923/llm-idf-reproduce'
TERM='v1:desk:interest'
DIRECT={(TERM,1),(TERM+'@mix0.7',0)} # zero-based evaluated question indices
MANIFEST={}
def load(name):
 fs=[DATA/name] if '/' in name else list(DATA.rglob(name))
 if len(fs)>1:
  assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in fs})==1,('Different copies',name)
  fs=sorted(fs)[:1]
 assert len(fs)==1,(name,fs)
 p=fs[0];MANIFEST[name]={'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def auc(y,s):
 y=np.asarray(y);s=np.asarray(s);order=np.argsort(s,kind='stable');y=y[order];s=s[order]
 starts=np.r_[0,np.flatnonzero(np.diff(s))+1];pos=np.add.reduceat(y,starts);neg=np.add.reduceat(1-y,starts)
 return float(np.sum(pos*(np.cumsum(neg)-neg/2))/(sum(pos)*sum(neg))) if sum(pos)*sum(neg)>0 else None

def filter_rows(rows,scenario):
 if scenario=='original':return list(rows)
 if scenario=='exclude_direct_2':return [r for r in rows if (r['id'],r['qi']) not in DIRECT]
 if scenario=='exclude_signed_4':return [r for r in rows if (r['id'],r['qi']) not in DIRECT|{(TERM,0),(TERM,2)}]
 if scenario=='exclude_family':return [r for r in rows if not r['id'].startswith(TERM)]
 raise ValueError(scenario)

def match(lp,reader):
 E={r['id']:r for r in reader};out=[]
 for r in lp:
  if r['id'] not in E:continue
  qs=E[r['id']]['questions']
  for j,p in enumerate(r.get('per_question') or []):
   if j>=len(qs):continue
   q=qs[j]
   if not(q['q'].startswith(p['q']) or p['q'].startswith(q['q'])):continue
   c=q.get('correct') or {}
   if c.get('bare') is None:continue
   out.append({'id':r['id'],'qi':j,'q':q['q'],'answer':q['answer'],'R':1-p['bare']['p_correct'],'dp':p['glossC']['p_correct']-p['bare']['p_correct'],'fail':int(c['bare']==0),'definition_correct':int(c['glossC']==1),'repair':int(c['bare']==0 and c['glossC']==1),'harm':int(c['bare']==1 and c['glossC']==0)})
 return out

def ci(rows,target,score,rng,B=2000,contrast=False):
 ids=list(dict.fromkeys(r['id'] for r in rows));groups=[np.array([i for i,r in enumerate(rows) if r['id']==k]) for k in ids]
 y=np.array([r[target] for r in rows]);s=np.array([r[score] for r in rows]);d=np.array([r['dp'] for r in rows]);vals=[]
 for _ in range(B):
  ix=np.concatenate([groups[j] for j in rng.integers(len(ids),size=len(ids))]);v=auc(y[ix],s[ix])
  if contrast:v=auc(y[ix],d[ix])-v
  if v is not None:vals.append(v)
 return [float(x) for x in np.quantile(vals,[.025,.975])]

def summarize(rows,rng):
 failures=[r for r in rows if r['fail']];other=[]
 groups=defaultdict(list)
 for r in rows:groups[r['id']].append(r)
 for r in rows:
  sib=[x for x in groups[r['id']] if x['qi']!=r['qi']]
  if sib:other.append(r|{'other_dp':sum(x['dp'] for x in sib)/len(sib)})
 failed_other=[r for r in other if r['fail']]
 out={'n':len(rows),'n_terms':len(groups),'bare_errors':len(failures),'definition_errors':sum(not r['definition_correct'] for r in rows),'repairs':sum(r['repair'] for r in rows),'harms':sum(r['harm'] for r in rows),
      'table3_R_auc':auc([r['fail'] for r in rows],[r['R'] for r in rows]),'table3_dp_auc':auc([r['fail'] for r in rows],[r['dp'] for r in rows]),
      'table3_R_ci':ci(rows,'fail','R',rng),
      'table4_R_conditional_repair_auc':auc([r['repair'] for r in failures],[r['R'] for r in failures]),
      'table4_dp_conditional_repair_auc':auc([r['repair'] for r in failures],[r['dp'] for r in failures]),
      'table4_other_dp_conditional_repair_auc':auc([r['repair'] for r in failed_other],[r['other_dp'] for r in failed_other]),'table4_other_n':len(failed_other),
      'appendix_R_unconditional_repair_auc':auc([r['repair'] for r in rows],[r['R'] for r in rows]),'appendix_dp_unconditional_repair_auc':auc([r['repair'] for r in rows],[r['dp'] for r in rows])}
 # Preserve the original bootstrap RNG advance before the next reader's risk interval.
 out['appendix_dp_minus_R_error_ci']=ci(rows,'fail','R',rng,1000,True)
 return out,other

def main():
 lp=load('lpmc_v1.jsonl');ds=load('v1_eqa.jsonl');gpt=load('astra6_v1_eqa.jsonl');terms=load('v1_terms.jsonl');weights=load('data/synthetic_v1/inputs/v1_weights.jsonl');rawweights=load('data/synthetic_v1/raw_outputs/v1_weights.jsonl')
 raw=load('unc_v1_raw_samples.jsonl');unc=load('unc_v1.jsonl');E={x['id']:x for x in ds};U={x['id']:x for x in unc}
 samples=[]
 for r in raw:
  q=E[r['id']]['questions'][r['qi']];u=U[r['id']]['per_question'][r['qi']]
  assert r['gold']==q['answer'] and len(r['samples'])==10 and dict(Counter(r['samples']))==u['votes']
  assert int(r['greedy']==r['gold'])==q['correct']['bare']
  samples.append({'id':r['id'],'qi':r['qi'],'greedy_error':r['greedy']!=r['gold'],'same':len(set(r['samples']))==1,'stable_wrong':len(set(r['samples']))==1 and r['samples'][0]!=r['gold'],'majority_wrong':r['stored_majority']!=r['gold'],'consistency':u['consistency'],'entropy':u['mc_entropy'],'negative_confidence':-u['verb_conf']})
 paired={'DeepSeek':match(lp,ds),'GPT6':match(lp,gpt)}
 assert [len(v) for v in paired.values()]==[457,457]
 scenarios={}
 for scenario in ['original','exclude_direct_2','exclude_signed_4','exclude_family']:
  rng=np.random.default_rng(20260922);results={}
  for reader,rows in paired.items():
   filtered=filter_rows(rows,scenario);results[reader],other=summarize(filtered,rng)
   (ROOT/(scenario+'_'+reader+'_rows.jsonl')).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in other))
  ss=filter_rows(samples,scenario);fails=[r for r in ss if r['greedy_error']]
  n=sum(r['stable_wrong'] for r in fails);den=len(fails)
  scenarios[scenario]={'readers':results,'uncertainty':{'n_questions':len(ss),'raw_letters':len(ss)*10,'greedy_errors':den,'identical_among_greedy_errors':sum(r['same'] for r in fails),'identical_wrong_among_greedy_errors':n,'stable_wrong_fraction':n/den,'majority_wrong_among_greedy_errors':sum(r['majority_wrong'] for r in fails),'aucs':{key:auc([int(r['greedy_error']) for r in ss],[r[key] for r in ss]) for key in ['consistency','entropy','negative_confidence']}}}
 for scenario in scenarios:
  valid={(r['id'],r['qi']) for r in filter_rows(paired['DeepSeek'],scenario)}
  shared=[r for r in filter_rows(samples,scenario) if (r['id'],r['qi']) in valid]
  scenarios[scenario]['uncertainty']['shared_n']=len(shared)
  scenarios[scenario]['uncertainty']['shared_aucs']={key:auc([int(r['greedy_error']) for r in shared],[r[key] for r in shared]) for key in ['consistency','entropy','negative_confidence']}
 assert scenarios['original']['uncertainty']['identical_wrong_among_greedy_errors']==93
 assert scenarios['original']['uncertainty']['greedy_errors']==231
 baseline=json.loads((ROOT.parent/'paper_two_signals_20260923/data_summary.json').read_text())
 for reader in ['DeepSeek','GPT6']:
  old=next(x for x in baseline['settings'] if x['setting']=='Synthetic / '+reader);now=scenarios['original']['readers'][reader]
  assert abs(now['table3_R_auc']-old['risk_auc'])<1e-12
  assert np.max(np.abs(np.array(now['table3_R_ci'])-old['risk_ci']))<1e-12,(reader,now['table3_R_ci'],old['risk_ci'])
 inventory=[]
 for term in terms:
  if not term['id'].startswith(TERM):continue
  evalqs=E[term['id']]['questions'];w=next((w for w in weights if w['id']==term['id']),{})
  for j,q in enumerate(evalqs):inventory.append({'id':term['id'],'qi':j,'evaluated_question':q,'directly_affected':(term['id'],j) in DIRECT,'source_input_qa_count':len(term.get('qa',[])),'gloss_gold':term.get('gloss_gold'),'gloss_used_input_copy':w.get('gloss_used'),'gloss_used_raw_copy':next((a.get('gloss_used') for a in rawweights if a['id']==term['id']),None),'raw_uncertainty':next((r for r in raw if r['id']==term['id'] and r['qi']==j),None),'in_proxy_table':any(r['id']==term['id'] and r['qi']==j for r in paired['DeepSeek'])})
 (ROOT/'interest_question_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
 result={'scope':'Targeted interest-family source conflict sensitivity; not a corpus-wide semantic audit. No key flips or model calls.', 'direct_exclusions':[{'id':i,'qi_zero_based':j} for i,j in sorted(DIRECT)],'scenarios':scenarios,'source_manifest':MANIFEST}
 (ROOT/'interest_sensitivity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 for name,r in scenarios.items():
  print(name,json.dumps(r,ensure_ascii=False))
if __name__=='__main__':main()
