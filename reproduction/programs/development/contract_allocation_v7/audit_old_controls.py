import argparse,json
from common import *
from api import prompt,parse_answer

def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);a=p.parse_args()
 old=ROOT.parent/'local_meaning_v6_boundary_pilot'
 tasks={x['id']:x for x in read(old/'tasks_private.jsonl')};cards={x['definition_id']:x for x in read(old/'rules_with_dependencies.jsonl')}
 selected=[('deepseek','cuadfull:450:Covered Regions:control'),('judge','cuadfull:170:Products:control')]
 path=ROOT/'old_control_recheck.jsonl';done={(x['role'],x['task_id'],x['arm']) for x in read(path)}
 for role,sid in selected:
  t=tasks[sid];s=spec_for(a.config,role)
  for arm in ['bare','definition']:
   if (role,sid,arm) in done:continue
   settings={'thinking':{'type':'disabled'}} if role=='deepseek' else {'reasoning_effort':'none'}
   payload={'model':s['model'],'messages':[{'role':'system','content':'You answer multiple-choice research questions about a contract. Choose one option letter.'},{'role':'user','content':prompt(t,cards[t['definition_id']]['rule_quote'] if arm=='definition' else None)}],'temperature':0,'max_tokens':64,**settings}
   r=request_one(s,payload)
   row={'role':role,'task_id':sid,'arm':arm,'gold':t['gold'],'options':t['options'],'question':t['question'],'requested_settings':settings,'correct':r['prediction']==t['gold'],'status':'posthoc_mode_recheck_not_replacement',**r}
   with path.open('a') as f:f.write(canonical(row)+'\n')
   print(role,arm,'raw:',r['content'],'correct:',row['correct'],flush=True)
if __name__=='__main__':main()
