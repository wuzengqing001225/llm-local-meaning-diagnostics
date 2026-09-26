import json,hashlib,re
from collections import Counter
from common import *

def main():
 checks={}
 for filename in ['A_freeze.json','B_freeze.json','budget_freeze.json']:
  m=json.loads((ROOT/filename).read_text())
  for f,h in m['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
  checks[filename]=len(m['sha256'])
 pub=read('tasks_public.jsonl');private=read('tasks_private.jsonl');a=read('diagnostics_A.jsonl');cards=read('cards_for_A.jsonl')
 assert len({t['id'] for t in pub})==len(pub)==len(private)
 for x,y in zip(pub,private):
  assert all(y[k]==v for k,v in x.items())
  assert not {'gold','group','source_answer','ordinary_answer','mapping'} & x.keys()
  assert x['options']['AB'.index(y['gold'])].lower()==y['source_answer']
 assert all(4<=n<=6 for n in Counter(x['definition_id'] for x in a).values())
 rows=read('reader_results.jsonl');lookup={(x['role'],x['task_id'],x['arm']) for x in rows}
 expected={(r,t['id'],arm) for r in ['gpt','deepseek'] for t in pub for arm in ['forced_bare','forced_definition','abstain_bare','abstain_definition']}
 assert len(rows)==len(lookup) and lookup==expected
 for x in rows:
  assert x['settings']['temperature']==0
  if x['role']=='deepseek':assert x['settings']['thinking']=={'type':'disabled'}
  else:assert x['settings']['reasoning_effort']=='none'
 tasks={t['id'] for t in pub};cost=json.loads((ROOT/'budget_costs.json').read_text())['task_costs']
 for p in read('budget_plans.jsonl'):
  assert len(p['selected'])==len(set(p['selected'])) and set(p['selected'])<=tasks
  assert sum(cost[t] for t in p['selected'])==p['spent']<=p['budget']
 checks.update(n_A=len(a),n_B=len(pub),n_rules=len(cards),n_reader_responses=len(rows),gold_positions=dict(Counter(x['gold'] for x in private)),unparsed=sum(x['prediction'] is None for x in rows),all_policy_costs_within_budget=True,public_inputs_without_gold=True)
 (ROOT/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n');print(checks)
if __name__=='__main__':main()
