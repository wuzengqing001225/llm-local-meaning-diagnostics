import json,sys,hashlib,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parent
from api import config_role,request_one,canonical,parse_json_object

def read(name):
 p=Path(name);p=p if p.is_absolute() else ROOT/p
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
def write(name,rows):
 p=ROOT/name;p.write_text(''.join(canonical(x)+'\n' for x in rows))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def spec_for(config,role):
 s=config_role(config,'draft' if role=='deepseek' else 'reader')
 if role=='author':s['model']='gpt-6-astra'
 return s

def batch(config,role,jobs,out,system,max_tokens=6000):
 # job data is the full, auditable visible API input. No keys are persisted.
 if 'json' not in system.lower():system+='\nReturn valid JSON only.'
 s=spec_for(config,role);done={x['id']:x for x in read(out)};pending=[]
 for sid,data in jobs:
  payload={'model':s['model'],'messages':[{'role':'system','content':system},{'role':'user','content':canonical(data)}],
           'temperature':0,'max_tokens':max_tokens,'response_format':{'type':'json_object'}}
  h=digest(payload)
  if sid in done:
   if done[sid]['input_sha256']!=h:raise ValueError('Stale cached API input: '+sid)
  else:pending.append((sid,payload,h))
 def one(job):
  sid,payload,h=job;t=time.monotonic();r=request_one(s,payload)
  result=parse_json_object(r['content'])
  return {'id':sid,'input_sha256':h,'result':result,'content':r['content'],'requested_model':s['model'],
          'returned_model':r['returned_model'],'provider_response_id':r['provider_response_id'],'usage':r['usage'],
          'finish_reason':r['finish_reason'],'seconds':time.monotonic()-t}
 errors=[]
 with ThreadPoolExecutor(max_workers=4) as pool,(ROOT/out).open('a') as f:
  fs={pool.submit(one,j):j[0] for j in pending}
  for i,fu in enumerate(as_completed(fs),1):
   try:r=fu.result()
   except Exception as e:errors.append(fs[fu]);print('FAILED',fs[fu],type(e).__name__,str(e)[:160],flush=True);continue
   f.write(canonical(r)+'\n');f.flush();done[r['id']]=r
   print(out,i,'/',len(pending),r['id'],flush=True)
 if errors:raise RuntimeError(f'{len(errors)} requests failed, rerun to resume')
 return done
