#!/usr/bin/env python3
"""Source-only budget competition audit. Requires real retrieval candidates, no gold."""
import argparse,json,hashlib,statistics,os
from pathlib import Path

def read(p):return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--catalog',type=Path,required=True,help='JSONL: id, scope, text')
 p.add_argument('--requests',type=Path,required=True,help='JSONL: id, scope, candidate_ids, retrieval_provenance; no gold')
 p.add_argument('--budget-tokens',type=int,required=True)
 p.add_argument('--budget-origin',choices=['documented_deployment_limit','engineering_pilot','simulation'],required=True)
 p.add_argument('--budget-evidence',required=True,help='Where the independent limit came from, not a claim inferred from results')
 p.add_argument('--out',type=Path,required=True)
 a=p.parse_args()
 if a.budget_tokens<=0:raise ValueError('Positive absolute token budget required')
 requests=read(a.requests)
 if not requests:raise ValueError('No requests')
 prohibited={'answer','gold','label','gold_answer','correct_answer','reader_result','target_error'}
 for q in requests:
  if prohibited & q.keys():raise ValueError('Preflight input must not contain test answers/outcomes')
  if not q.get('retrieval_provenance'):raise ValueError('Missing candidate provenance')
  if not q['candidate_ids'] or len(set(q['candidate_ids']))!=len(q['candidate_ids']):raise ValueError('Empty or duplicate candidates')
 os.environ['HF_HUB_OFFLINE']='1'
 from transformers import AutoTokenizer
 model='Qwen/Qwen2.5-7B';rev='d149729398750b98c0af14eb82c78cfe92750796'
 tok=AutoTokenizer.from_pretrained(model,revision=rev,local_files_only=True)
 needed={u for q in requests for u in q['candidate_ids']};units={}
 for u in read(a.catalog):
  if u['id'] not in needed:continue
  if u['id'] in units:raise ValueError('Duplicate unit ID')
  units[u['id']]={'scope':u['scope'],'tokens':len(tok.encode(u['text'],add_special_tokens=False))}
 rows=[]
 for q in requests:
  if any(i not in units for i in q['candidate_ids']):raise ValueError('Unknown candidate ID')
  if any(units[i]['scope']!=q['scope'] for i in q['candidate_ids']):raise ValueError('Cross-scope padding is not permitted in this preflight')
  costs=[units[i]['tokens'] for i in q['candidate_ids']]
  rows.append({'id':q['id'],'candidate_count':len(costs),'candidate_tokens':sum(costs),'exceeds_budget':sum(costs)>a.budget_tokens,'largest_unit_tokens':max(costs),'one_unit_over_budget':max(costs)>a.budget_tokens})
 report={'status':'source_only_budget_preflight_not_an_effectiveness_result','budget_origin':a.budget_origin,'budget_evidence':a.budget_evidence,'budget_tokens':a.budget_tokens,
         'tokenizer':model,'revision':rev,'n_requests':len(rows),'over_budget_fraction':sum(r['exceeds_budget'] for r in rows)/len(rows),
         'multi_candidate_fraction':sum(r['candidate_count']>1 for r in rows)/len(rows),'median_candidate_tokens':statistics.median(r['candidate_tokens'] for r in rows),
         'candidate_pools_hash':hashlib.sha256(a.requests.read_bytes()).hexdigest(),'catalog_hash':hashlib.sha256(a.catalog.read_bytes()).hexdigest(),
         'limitation':'Large candidate pools alone do not establish semantic relevance or a real deployment budget. Provenance and budget evidence require independent review. This is supplemental text only; total API-call costs require the separate ledger.', 'rows':rows}
 a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['n_requests','over_budget_fraction','multi_candidate_fraction','median_candidate_tokens','budget_origin']}))
if __name__=='__main__':main()
