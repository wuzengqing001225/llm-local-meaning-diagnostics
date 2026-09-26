#!/usr/bin/env python3
"""Count matched local definitions, never generic passages or answer evidence."""
import argparse,json,hashlib,math,os,statistics,itertools
from pathlib import Path

def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def closure(roots,catalog):
 seen=set();stack=list(roots)
 while stack:
  i=stack.pop()
  if i in seen:continue
  if i not in catalog:raise ValueError('Unresolved definition dependency: '+i)
  seen.add(i);stack.extend(catalog[i].get('dependencies',[]))
 return sorted(seen)
def render(ids,catalog):return '\n\n'.join(catalog[i]['term']+': '+catalog[i]['definition'] for i in ids)
def main():
 p=argparse.ArgumentParser();p.add_argument('--definitions',type=Path,required=True);p.add_argument('--requests',type=Path,required=True)
 p.add_argument('--budget-tokens',type=int,help='Explicit secondary budget. Omit for the median-half primary rule')
 p.add_argument('--budget-origin',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.budget_tokens is not None and a.budget_tokens<=0:raise ValueError('Positive explicit budget required')
 entries=rows(a.definitions);catalog={e['id']:e for e in entries}
 if len(catalog)!=len(entries):raise ValueError('Duplicate definition IDs')
 for e in entries:
  if e.get('unit_type')!='local_definition':raise ValueError('Only local_definition units are allowed; paragraph preflight is out of scope')
  for k in ['term','definition','scope','source_ref']:
   if not isinstance(e.get(k),str) or not e[k].strip():raise ValueError('Missing definition field: '+k)
 qs=rows(a.requests)
 if not qs:raise ValueError('No requests')
 os.environ['HF_HUB_OFFLINE']='1'
 from transformers import AutoTokenizer
 model='Qwen/Qwen2.5-7B';revision='d149729398750b98c0af14eb82c78cfe92750796'
 tok=AutoTokenizer.from_pretrained(model,revision=revision,local_files_only=True)
 cost=lambda ids:len(tok.encode(render(ids,catalog),add_special_tokens=False)) if ids else 0
 frames=[]
 for q in qs:
  if {'answer','gold','target_error','gold_definition_ids','reference_ids'} & q.keys():raise ValueError('Matching input must not carry test answers or answer-derived definition lists')
  if not q.get('matcher_provenance'):raise ValueError('Missing pre-outcome matcher provenance')
  ids=q['matched_definition_ids']
  if len(set(ids))!=len(ids):raise ValueError('Duplicate matches')
  allids=closure(ids,catalog)
  if any(catalog[i]['scope']!=q['scope'] for i in allids):raise ValueError('Cross-scope definition mixing requires separate source adjudication')
  costs=[cost(closure([i],catalog)) for i in ids];total=cost(allids)
  frames.append((q,ids,allids,costs,total))
 median_cost=statistics.median(x[4] for x in frames)
 budget=math.floor(median_cost*.5) if a.budget_tokens is None else a.budget_tokens
 result=[]
 for q,ids,allids,costs,total in frames:
  affordable_ids=[i for i,c in zip(ids,costs) if c<=budget]
  # Two separately affordable entries must *compete* for the budget.  A third
  # unaffordable entry must not make a jointly affordable pair count as choice.
  competing_pair=any(cost(closure([left,right],catalog))>budget
                     for left,right in itertools.combinations(affordable_ids,2))
  result.append({'request_id':q['id'],'n_matched_definitions':len(ids),'n_with_dependencies':len(allids),'all_matched_definition_tokens':total,'exceeds_budget':total>budget,'n_individually_affordable_matches':len(affordable_ids),'genuine_choice_under_this_budget':competing_pair})
 overflow=sum(x['exceeds_budget'] for x in result)/len(result)
 choice=sum(x['genuine_choice_under_this_budget'] for x in result)/len(result)
 source_review_complete=all(e.get('validation_status')=='source_checked' for e in entries)
 summary={'unit':'matched_local_definition','n_catalog_definitions':len(entries),'n_requests':len(qs),'budget_rule':'floor(0.5 * median(all_matched_definition_tokens))' if a.budget_tokens is None else 'explicit_secondary_budget',
          'median_all_matched_definition_tokens':median_cost,'budget_tokens':budget,'budget_origin':a.budget_origin,'tokenizer':model,'revision':revision,
          'median_matched_definitions':statistics.median(x['n_matched_definitions'] for x in result),'median_definition_tokens':statistics.median(x['all_matched_definition_tokens'] for x in result),
          'over_budget_fraction':overflow,'multiple_affordable_choices_fraction':choice,
          'source_review_complete':source_review_complete,
          'primary_gate_passed':a.budget_tokens is None and source_review_complete and budget>0 and overflow>=.4 and choice>=.4,
          'definitions_sha256':hashlib.sha256(a.definitions.read_bytes()).hexdigest(),'requests_sha256':hashlib.sha256(a.requests.read_bytes()).hexdigest(),
          'scope_limit':'Schema and token checks do not prove source definitions are complete or all matches are relevant. Validate those separately. No A/B outcomes are read.','requests':result}
 a.out.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='requests'},ensure_ascii=False))
if __name__=='__main__':main()
