import argparse,json,random,re,time,hashlib
from concurrent.futures import ThreadPoolExecutor,as_completed
from common import *

def prompt(t,note=None,abstain=False):
 s=('Local definition for this contract only:\n'+note+'\n\n') if note else ''
 s+=t['question']+'\n'+'\n'.join(c+'. '+x for c,x in zip('AB',t['options']))
 if abstain:s+='\nC. Insufficient information to determine the answer.\nChoose C if the provided information does not determine the answer. Answer with A, B or C only.'
 else:s+='\nChoose the best answer. Answer with A or B only.'
 return s

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);a=p.parse_args()
 for fname in ['B_freeze.json','budget_freeze.json']:
  freeze=json.loads((ROOT/fname).read_text())
  for f,h in freeze['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
 review=json.loads((ROOT/'agent_source_review.json').read_text())
 assert review['tasks_public_sha256']==hashlib.sha256((ROOT/'tasks_public.jsonl').read_bytes()).hexdigest(), 'Finish source-only review before target calls'
 tasks=read('tasks_public.jsonl');rules={x['definition_id']:x for x in read('cards_for_A.jsonl')}
 done={x['request_id']:x for x in read('reader_results.jsonl')};jobs=[]
 for role in ['gpt','deepseek']:
  s=spec_for(a.config,'deepseek' if role=='deepseek' else 'judge')
  settings={'thinking':{'type':'disabled'}} if role=='deepseek' else {'reasoning_effort':'none'}
  for t in tasks:
   for arm in ['forced_bare','forced_definition','abstain_bare','abstain_definition']:
    abst=arm.startswith('abstain');note=rules[t['definition_id']]['rule_quote'] if arm.endswith('definition') else None
    user=prompt(t,note,abst)
    payload={'model':s['model'],'messages':[{'role':'system','content':'Answer the question from the available facts and any supplied local definition. Follow the answer options.'},{'role':'user','content':user}],
             'temperature':0,'max_tokens':64,**settings}
    h=digest({'task':t['id'],'role':role,'arm':arm,'endpoint':s['base_url'],'payload':payload})
    if h not in done:jobs.append((h,role,t['id'],arm,s,payload))
 random.Random(20260926).shuffle(jobs)
 def one(j):
  h,role,sid,arm,s,payload=j;t=time.monotonic();r=request_one(s,payload)
  val=r['content'].strip();m=re.fullmatch(r'(?:Answer\s*:\s*)?([ABC])[.\s]*',val,re.I)
  pred=m.group(1).upper() if m else None
  if pred=='C' and not arm.startswith('abstain'):pred=None
  return {'request_id':h,'role':role,'task_id':sid,'arm':arm,'requested_model':s['model'],
          'settings':{k:v for k,v in payload.items() if k!='messages'},'elapsed_seconds':time.monotonic()-t,
          **r,'prediction':pred,'status':'provisional_development_only'}
 errors=[]
 with ThreadPoolExecutor(max_workers=4) as pool,(ROOT/'reader_results.jsonl').open('a') as f:
  fs={pool.submit(one,j):j[0] for j in jobs}
  for i,fu in enumerate(as_completed(fs),1):
   try:r=fu.result()
   except Exception as e:errors.append(fs[fu]);print('FAILED',type(e).__name__,str(e)[:120],flush=True);continue
   f.write(canonical(r)+'\n');f.flush()
   if i%20==0 or i==len(jobs):print('READER',i,'/',len(jobs),flush=True)
 if errors:raise RuntimeError(f'{len(errors)} calls failed; rerun same command to resume')
if __name__=='__main__':main()
