import argparse,os,time,hashlib,json
from pathlib import Path
from common import read,write,ROOT,digest,canonical
MODEL='Qwen/Qwen2.5-7B';REV='d149729398750b98c0af14eb82c78cfe92750796'
def text(item,note=None):
 prefix='You answer a multiple-choice question about a contract. Answer with one option letter only.\n\n'
 if note:prefix+='Local definition for this contract only:\n'+note+'\n\n'
 return prefix+item['question']+'\n'+'\n'.join(f'{c}. {x}' for c,x in zip('ABCD',item['options']))+'\nAnswer:'
def main():
 os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
 import torch
 from transformers import AutoTokenizer,AutoModelForCausalLM
 torch.set_num_threads(4)
 items=read('diagnostics_A.jsonl');cards={x['definition_id']:x for x in read('cards_for_A.jsonl')}
 tok=AutoTokenizer.from_pretrained(MODEL,revision=REV,local_files_only=True)
 ids=[tok.encode(' '+c,add_special_tokens=False) for c in 'ABCD'];assert all(len(x)==1 for x in ids)
 print('Loading local frozen proxy for',len(items),'four-option A items',flush=True)
 net=AutoModelForCausalLM.from_pretrained(MODEL,revision=REV,dtype=torch.float32,local_files_only=True).eval()
 def score(s):
  x=tok(s,return_tensors='pt')
  with torch.inference_mode():v=net(**x).logits[0,-1,[i[0] for i in ids]].float()
  return torch.softmax(v,0).tolist()
 done={x['id']:x for x in read('A_scores.jsonl')}
 with (ROOT/'A_scores.jsonl').open('a') as f:
  for i,x in enumerate(items):
   note=cards[x['definition_id']]['rule_quote'];h=digest({'item':x,'note':note,'model':MODEL,'revision':REV,'prompt':1})
   if x['id'] in done:
    assert done[x['id']]['input_sha256']==h;continue
   b=score(text(x));d=score(text(x,note));j='ABCD'.index(x['answer'])
   row={'id':x['id'],'definition_id':x['definition_id'],'input_sha256':h,'p_bare':b[j],'p_definition':d[j],'R':1-b[j],'dp':d[j]-b[j],'probabilities_bare':b,'probabilities_definition':d,'model':MODEL,'revision':REV,'label_token_ids':ids,'status':'provisional_model_checked_A'}
   f.write(canonical(row)+'\n');f.flush();print('A',i+1,'/',len(items),'R',round(row['R'],3),'dp',round(row['dp'],3),flush=True)
 rows=read('A_scores.jsonl');aggregate=[]
 for did,c in cards.items():
  rs=[x for x in rows if x['definition_id']==did];n=len(rs);assert n>=4
  dp=[x['dp'] for x in rs];rr=[x['R'] for x in rs]
  aggregate.append({'definition_id':did,'n_A':n,'mean_dp':sum(dp)/n,'max_dp':max(dp),'mean_R':sum(rr)/n,'max_R':max(rr),'dp_min':min(dp),'dp_max':max(dp),'source_cohort':c['source_cohort']})
 aggregate.sort(key=lambda x:(x['mean_dp'],x['definition_id']))
 for i,x in enumerate(aggregate):x['A_stratum']=['low','middle','high'][min(2,i*3//len(aggregate))]
 write('A_rule_scores.jsonl',aggregate)
 # The B author file contains no A questions, scores, ranks or stratum labels.
 write('B_author_rules.jsonl',[{k:c[k] for k in ['definition_id','term','contract_index','rule_quote']} for c in cards.values()])
 frozen=['cards_for_A.jsonl','diagnostics_A.jsonl','A_scores.jsonl','A_rule_scores.jsonl','B_author_rules.jsonl','protocol.md']
 (ROOT/'A_freeze.json').write_text(json.dumps({'status':'A_frozen_before_B_creation','sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in frozen},'n_rules':len(cards),'n_A':len(items)},indent=2)+'\n')
 print('A frozen; all strata retained with equal B quota',flush=True)
if __name__=='__main__':main()
