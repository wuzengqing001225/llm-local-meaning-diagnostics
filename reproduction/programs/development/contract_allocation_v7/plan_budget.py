import argparse,json,math,re,hashlib,random,os
from common import *
from reader import prompt

def main():
 p=argparse.ArgumentParser();p.add_argument('--cuad',type=Path);a=p.parse_args()
 if (ROOT/'reader_results.jsonl').exists():
  if (ROOT/'budget_freeze.json').exists():print('Budget already frozen');return
  raise ValueError('Cannot create budget plan after reader outcomes')
 from source_review_gate import apply
 apply()
 os.environ['HF_HUB_OFFLINE']='1'
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B',revision='d149729398750b98c0af14eb82c78cfe92750796',local_files_only=True)
 tasks=read('tasks_public.jsonl');cards={x['definition_id']:x for x in read('cards_for_A.jsonl')};scores={x['definition_id']:x for x in read('A_rule_scores.jsonl')}
 terms=json.loads((ROOT/'corpus_term_statistics.json').read_text())['terms']
 cost={t['id']:len(tok.encode(prompt(t,cards[t['definition_id']]['rule_quote'])))-len(tok.encode(prompt(t))) for t in tasks}
 assert all(v>0 for v in cost.values())
 full=sum(cost.values());policies=['mean_dp','mean_R','max_dp','max_R','dp_per_token','matched_fixed','frequency','idf']
 plans=[]
 for frac in [.25,.5,.75]:
  limit=math.floor(frac*full)
  def choose(order):
   selected=[];used=0
   for t in order:
    if used+cost[t['id']]<=limit:selected.append(t['id']);used+=cost[t['id']]
   return selected,used
  for policy in policies:
   def key(t):
    s=scores[t['definition_id']]
    v=s[policy] if policy in ['mean_dp','mean_R','max_dp','max_R'] else (s['mean_dp']/cost[t['id']] if policy=='dp_per_token' else (terms[t['definition_id']][policy] if policy in ['frequency','idf'] else 0))
    return (-v,hashlib.sha256(('v7-fixed:'+t['id']).encode()).hexdigest())
   selected,used=choose(sorted(tasks,key=key));plans.append({'fraction':frac,'policy':policy,'budget':limit,'spent':used,'selected':selected})
  for seed in range(100):
   order=list(tasks);random.Random(7700+seed).shuffle(order);selected,used=choose(order)
   plans.append({'fraction':frac,'policy':'random','seed':seed,'budget':limit,'spent':used,'selected':selected})
 write('budget_plans.jsonl',plans)
 (ROOT/'budget_costs.json').write_text(json.dumps({'cost_unit':'incremental input tokens under frozen Qwen2.5 tokenizer, not API billed tokens','full_cost':full,'task_costs':cost,'term_statistics':terms,'policy_scope':'each request has one matched note; individual-request greedy allocation, all strata retained'},indent=2)+'\n')
 files=['corpus_term_statistics.json','budget_plans.jsonl','budget_costs.json','tasks_public.jsonl','A_rule_scores.jsonl']
 (ROOT/'budget_freeze.json').write_text(json.dumps({'status':'budget_frozen_before_readers','sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}},indent=2)+'\n')
 print('Budget plans frozen:',len(tasks),'tasks',full,'tokens')
if __name__=='__main__':main()
