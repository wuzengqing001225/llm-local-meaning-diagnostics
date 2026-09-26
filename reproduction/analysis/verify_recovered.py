"""Offline, read-only audit of the returned archive. No model calls or writes to source."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,hashlib,math,random,ast

def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def auc(ys,scores,weights=None):
 pairs=sorted(zip(scores,ys,weights or [1.]*len(ys)));neg=0.;num=0.;pos=0.;i=0
 while i<len(pairs):
  j=i;wp=wn=0.
  while j<len(pairs) and pairs[j][0]==pairs[i][0]:
   _,y,w=pairs[j];wp+=w*y;wn+=w*(1-y);j+=1
  num+=wp*(neg+wn/2);neg+=wn;pos+=wp;i=j
 return num/(pos*neg) if pos*neg else None

def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--original',type=Path);p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True)
 root=a.source;idx=defaultdict(list)
 for f in (root/'data').rglob('*'):
  if f.is_file():idx[f.name].append(f)
 def load(n):
  assert len(idx[n])==1,(n,idx[n]);return rows(idx[n][0])
 mapping={'v1_deepseek':'v1_eqa.jsonl','v1_gpt6':'astra6_v1_eqa.jsonl','reddit_deepseek':'reddit_eqa.jsonl','reddit_gpt6':'astra6_reddit_eqa.jsonl','defi_strict_deepseek':'defi_strict_eqa.jsonl','defi_strict_gpt56':'defi_strict_eqa_gpt.jsonl','defi_strict_gpt6':'astra6_defi_strict_eqa.jsonl','cuad_usage_deepseek':'cuad_eqa_usage_deepseek.jsonl','cuad_gold_deepseek':'cuad_eqa_gold_deepseek.jsonl'}
 report={};reader_checks=[];recovered={}
 for tag,original in mapping.items():
  source=load(original);stored={r['id']:r for r in source};rec=rows(root/'audit/recovered'/(tag+'_raw.jsonl'));recovered[tag]=rec
  issues=[];comparisons=0;fields=Counter();counts=defaultdict(list);keys=set()
  for r in rec:
   key=(r['id'],r['qi']);assert key not in keys;keys.add(key)
   q=stored[r['id']]['questions'][r['qi']]
   for field in ['q','options','answer']:
    if q[field]!=r[field]:issues.append([key,'question mismatch',field])
   for condition,raw in r['raw'].items():
    assert raw in ['A','B','C','D','UNKNOWN'],(tag,key,raw)
    parsed=raw if raw in ['A','B','C','D'] else None
    correct=int(raw==q['answer']);fields[condition]+=1;counts[(r['id'],condition)].append(correct)
    if r['parsed'][condition]!=parsed or r['correct_recovered'][condition]!=correct:issues.append([key,'recovery mismatch',condition])
    if (q.get('correct') or {}).get(condition) is not None:
     comparisons+=1
     if q['correct'][condition]!=correct:issues.append([key,'original label mismatch',condition])
  aggregates=0
  for (term,condition),values in counts.items():
   if 'acc_'+condition in stored[term] and stored[term]['acc_'+condition] is not None:
    aggregates+=1
    if abs(sum(values)/len(values)-stored[term]['acc_'+condition])>1e-10:issues.append([term,'aggregate mismatch',condition])
  reader_checks.append({'file':tag+'_raw.jsonl','n_questions':len(rec),'source_questions':sum(len(r.get('questions',[])) for r in source),'condition_counts':dict(fields),'original_label_comparisons':comparisons,'aggregate_comparisons':aggregates,'issues':issues,'request_model_recorded':sorted({r['model'] for r in rec})})
 report['recovered_readers']=reader_checks
 # Ten samples, option order and separate greedy responses.
 rec=rows(root/'audit/recovered/unc_v1_raw_samples.jsonl');original={r['id']:r for r in load('unc_v1.jsonl')};eqa={r['id']:r for r in load('v1_eqa.jsonl')};rawgreedy={(r['id'],r['qi']):r for r in recovered['v1_deepseek']};lp={r['id']:r for r in load('lpmc_v1.jsonl')};checks=[];full=[];shared=[]
 for r in rec:
  term,j=r['id'],r['qi'];u=original[term]['per_question'][j];q=eqa[term]['questions'][j];votes=Counter(r['samples']);assert len(r['samples'])==10 and all(x in 'ABCD' and len(x)==1 for x in r['samples'])
  assert dict(votes)==r['stored_votes']==u['votes'];assert r['gold']==q['answer'];assert r['greedy']==rawgreedy[(term,j)]['raw']['bare']
  assert r['stored_majority']==u['majority'];assert votes[r['stored_majority']]==max(votes.values())
  entropy=-sum((v/10)*math.log(v/10) for v in votes.values())
  assert abs(entropy-u['mc_entropy'])<1e-10 and abs(1-max(votes.values())/10-u['consistency'])<1e-10
  item={'fail':r['greedy']!=r['gold'],'identical':len(votes)==1,'identical_wrong':len(votes)==1 and r['samples'][0]!=r['gold'],'majority_wrong':r['stored_majority']!=r['gold'],'consistency':u['consistency'],'entropy':entropy,'confidence':-u['verb_conf']};full.append(item)
  probes=lp.get(term,{}).get('per_question',[])
  if j<len(probes) and q['q'].startswith(probes[j]['q']):shared.append({**item,'risk':1-probes[j]['bare']['p_correct']})
 def unc_summary(items):
  fail=[r for r in items if r['fail']];return {'n':len(items),'greedy_errors':len(fail),'identical_among_errors':sum(r['identical'] for r in fail),'identical_wrong_among_errors':sum(r['identical_wrong'] for r in fail),'majority_wrong_among_errors':sum(r['majority_wrong'] for r in fail),'aucs':{k:auc([r['fail'] for r in items],[r[k] for r in items]) for k in ['consistency','entropy','confidence']+(['risk'] if items and 'risk' in items[0] else [])}}
 report['uncertainty']={'raw_sample_letters':sum(len(r['samples']) for r in rec),'full':unc_summary(full),'shared':unc_summary(shared),'alignment_and_vote_checks_passed':True}
 # Restored per-question CUAD gold labels, kept as a derived overlay.
 gold=recovered['cuad_gold_deepseek'];original=load('cuad_eqa_gold_deepseek.jsonl');recindex={(r['id'],r['qi']):r for r in gold}
 for term in original:
  for j,q in enumerate(term.get('questions',[])):
   r=recindex[(term['id'],j)];q['correct']=r['correct_recovered'];q['recovery_source']='audit/recovered/cuad_gold_deepseek_raw.jsonl'
 (a.out/'cuad_eqa_gold_deepseek.recovered.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in original))
 # Match all eight existing headline settings plus the recovered CUAD gold setting.
 settings=[('Synthetic / DeepSeek','lpmc_v1.jsonl','v1_eqa.jsonl'),('Synthetic / GPT6','lpmc_v1.jsonl','astra6_v1_eqa.jsonl'),('Reddit / DeepSeek','lpmc_reddit.jsonl','reddit_eqa.jsonl'),('Reddit / GPT6','lpmc_reddit.jsonl','astra6_reddit_eqa.jsonl'),('DeFi / DeepSeek','defi_strict_lpmc.jsonl','defi_strict_eqa.jsonl'),('DeFi / GPT5.6','defi_strict_lpmc.jsonl','defi_strict_eqa_gpt.jsonl'),('DeFi / GPT6','defi_strict_lpmc.jsonl','astra6_defi_strict_eqa.jsonl'),('CUAD library / GPT5.6','lpmc_full.jsonl','t2_answers.jsonl'),('CUAD gold / recovered DeepSeek','lpmc_cuad_v2.jsonl',None)]
 matched={};metrics=[]
 for name,lpname,ename in settings:
  E={r['id']:r for r in (load(ename) if ename else original)};matches=[];mismatches=[]
  for r in load(lpname):
   if r['id'] not in E:continue
   qs=E[r['id']]['questions']
   for j,q in enumerate(r.get('per_question') or []):
    candidates=[e for e in qs if str(e.get('ctx_idx'))==str(q.get('ctx_idx'))] if ename=='t2_answers.jsonl' else qs[j:j+1]
    if len(candidates)!=1:continue
    e=candidates[0]
    if not (e['q'].startswith(q['q']) or q['q'].startswith(e['q'])):mismatches.append([r['id'],j]);continue
    if (e.get('correct') or {}).get('bare') is None:continue
    matches.append({'id':r['id'],'ctx_idx':e.get('ctx_idx'),'risk':1-q['bare']['p_correct'],'pd':q['glossC']['p_correct']-q['bare']['p_correct'],'bare':e['correct']['bare'],'definition':e['correct']['glossC']})
  matched[name]=matches;metrics.append({'setting':name,'n':len(matches),'stem_mismatches':mismatches,'risk_auc':auc([1-x['bare'] for x in matches],[x['risk'] for x in matches]),'pd_auc':auc([1-x['bare'] for x in matches],[x['pd'] for x in matches]),'bare_accuracy':sum(x['bare'] for x in matches)/len(matches),'definition_accuracy':sum(x['definition'] for x in matches)/len(matches)})
 report['prediction_metrics']=metrics
 # Reconstruct sampler exactly, validate flat labels and serialized sample IDs.
 frame=[{'id':r['id'],'ctx_idx':p['ctx_idx'],'risk':1-p['bare']['p_correct']} for r in load('lpmc_full.jsonl') for p in r.get('per_question') or []];bins=defaultdict(list)
 for row in frame:bins[min(4,int(row['risk']*5))].append(row)
 rng=random.Random(42);sample=[]
 for _,rr in sorted(bins.items()):rng.shuffle(rr);sample.extend(rr[:300])
 key=lambda r:(r['id'],str(r['ctx_idx']))
 samplekeys={key(x) for x in sample};actual=matched['CUAD library / GPT5.6'];assert samplekeys=={key(x) for x in actual}=={key(x) for x in rows(root/'audit/t2_sample_ids.jsonl')}
 actual_by={key(x):x for x in actual}
 for row in load('labels_cuad_1500.jsonl'):
  ref=actual_by[key(row)];assert row['reader_failed']==1-ref['bare'] and row['reader_failed_with_definition']==1-ref['definition']
 weights=[len(bins[min(4,int(x['risk']*5))])/300 for x in actual]
 report['cuad_sampler']={'exact_sample_match':True,'frame_n':len(frame),'frame_counts':{k:len(v) for k,v in sorted(bins.items())},'flat_labels_match':True,'weighted_failure':sum(w*(1-r['bare']) for w,r in zip(weights,actual))/sum(weights),'weighted_risk_auc':auc([1-r['bare'] for r in actual],[r['risk'] for r in actual],weights),'weighted_pd_auc':auc([1-r['bare'] for r in actual],[r['pd'] for r in actual],weights),'transitions':dict(Counter(str((r['bare'],r['definition'])) for r in actual))}
 # RAG label conflicts: preserve archived and raw-response-derived branches.
 raw=rows(root/'audit/recovered/rag_v3_t1_raw_prompts_and_answers.jsonl');stored={(r['qkey'],r['arm']):r for r in load('rag_v3_t1.jsonl')};conflicts=[];eligible=[]
 for r in raw:
  if r['raw'] is None:
   assert r['parsed'] is None and r['correct_recovered'] is None
   continue
  assert r['parsed']==r['raw'] and r['correct_recovered']==int(r['raw']==r['answer'])
  k=(r['qkey'],r['arm'])
  if k in stored:
   eligible.append(r)
   if r['correct_recovered']!=stored[k]['correct']:conflicts.append({k:v for k,v in r.items() if k!='prompt'})
 by=defaultdict(dict)
 for r in stored.values():by[r['arm']][r['qkey']]=r
 recby={(r['qkey'],r['arm']):r for r in eligible};keys=sorted(by['rag']);rng=random.Random(20260923)
 def rag_summary(use_raw):
  values=[];groups=defaultdict(list)
  for k in keys:
   b=by['rag'][k]['correct'];g=recby[(k,'rag_gated')]['correct_recovered'] if use_raw else by['rag_gated'][k]['correct'];delta=g-b;groups[by['rag'][k]['ci']].append(delta);values.append((b,g))
  clusters=list(groups.values());means=[];rng=random.Random(20260923)
  for _ in range(2000):
   chosen=[clusters[rng.randrange(len(clusters))] for _ in clusters];means.append(sum(sum(g) for g in chosen)/sum(len(g) for g in chosen))
  means.sort();percentile=lambda p:means[int(p*(len(means)-1))]+(means[min(int(p*(len(means)-1))+1,len(means)-1)]-means[int(p*(len(means)-1))])*(p*(len(means)-1)%1)
  return {'n':len(values),'clusters':len(groups),'gated_accuracy':sum(g for b,g in values)/len(values),'net_gain':sum(g-b for b,g in values)/len(values),'repairs':sum(b==0 and g==1 for b,g in values),'harms':sum(b==1 and g==0 for b,g in values),'net_gain_cluster_ci':[percentile(.025),percentile(.975)]}
 report['rag_hybrid']={'raw_rows':len(raw),'raw_arms':dict(Counter(r['arm'] for r in raw)),'nonempty_raw_by_arm':dict(Counter(r['arm'] for r in raw if r['raw'] is not None)),'comparable_rows':len(eligible),'mismatches':conflicts,'stored':rag_summary(False),'raw_response_sensitivity':rag_summary(True),'note':'The published recovery view uses cache-order-corrected gated responses. Original raw experiment labels are unchanged. See provenance/resolution.json.'}
 (a.out/'rag_hybrid_conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2))
 # Validate tokenizer-check payloads, without loading historical weights.
 checks=[]
 for f in sorted((root/'audit').glob('tokenizer_check_*.json')):
  d=json.loads(f.read_text());ids=defaultdict(set)
  for label in d['labels']:
   for v in label['variants']:assert len(v['ids'])==1;ids[v['ids'][0]].add(label['letter'])
  assert all(len(v)==1 for v in ids.values());checks.append({'file':f.name,'model':d['model'],'revision':d['revision'],'reported_pass':d['old_first_token_assumption_passes'],'payload_consistent':True})
 report['tokenizer_checks']=checks
 # Compare data bytes with previous Workbench inputs. No unverified replacement.
 oldindex=defaultdict(list)
 for f in (a.original or root/'data').rglob('*'):
  if f.is_file():oldindex[f.name].append(f)
 same=[];different=[];new=[];manifest=[]
 for f in sorted(root.rglob('*')):
  if not f.is_file() or f.name=='.DS_Store' or f.relative_to(root).parts[:2]==('analysis','results'):continue
  manifest.append({'path':str(f.relative_to(root)),'bytes':f.stat().st_size,'sha256':sha(f)})
  if 'data'==f.relative_to(root).parts[0]:
   old=oldindex[f.name]
   if any(sha(x)==sha(f) for x in old):same.append(str(f.relative_to(root)))
   elif old:different.append(str(f.relative_to(root)))
   else:new.append(str(f.relative_to(root)))
 report['data_comparison']={'identical_count':len(same),'different':different,'new_to_workbench_by_name':new}
 report['python_syntax']={'files':0,'errors':[]}
 for f in root.rglob('*.py'):
  report['python_syntax']['files']+=1
  try:ast.parse(f.read_text())
  except (SyntaxError,UnicodeError) as e:report['python_syntax']['errors'].append({'file':str(f.relative_to(root)),'error':str(e)})
 (a.out/'source_manifest.json').write_text(json.dumps({'source':'.','files':manifest},ensure_ascii=False,indent=2))
 (a.out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'readers':len(reader_checks),'reader_issues':sum(len(x['issues']) for x in reader_checks),'uncertainty':report['uncertainty'],'cuad_gold':metrics[-1],'sampler':report['cuad_sampler'],'rag':report['rag_hybrid'],'data_comparison':report['data_comparison']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
