"""Budget feasibility on document sections and training first-user turns only.
Grounding references, agent answers, validation and test dialogues are not read.
"""
import json,re,math,hashlib,statistics,os
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parent
STOP=set('a an the is are was were i me my you your we our it its this that these those can could would should do does did have has had to for of in on at and or with from by about please help hello hi know want need thanks thank'.split())
def words(s):return [w for w in re.findall(r'[a-z0-9]+',s.lower()) if w not in STOP]
def dump(name,rows):(ROOT/name).write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
def main():
 os.environ['HF_HUB_OFFLINE']='1'
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B',revision='d149729398750b98c0af14eb82c78cfe92750796',local_files_only=True)
 docs=json.loads((ROOT/'multidoc2dial_doc.json').read_text())['doc_data']
 units=[];stats={}
 for scope,items in docs.items():
  before=len(units)
  for did,d in items.items():
   sections={}
   for sp in d['spans'].values():
    text=(sp.get('text_sec') or sp.get('text_sp') or '').strip()
    if not text:continue
    secid=str(sp.get('id_sec',sp['id_sp']));sections.setdefault(secid,text)
   for secid,text in sections.items():
    value=d['title']+'\n'+text
    units.append({'id':scope+':'+hashlib.sha256((did+':'+secid).encode()).hexdigest()[:20],'scope':scope,'doc_id':did,'section_id':secid,'text':value,'tokens':len(tok.encode(value,add_special_tokens=False))})
  stats[scope]={'n_documents':len(items),'n_sections':len(units)-before}
 dump('section_catalog.jsonl',units)
 # First user turn avoids leaking earlier agent answers; selection is hash-based, not answer-based.
 dialogs=json.loads((ROOT/'multidoc2dial_dial_train.json').read_text())['dial_data'];queries=[]
 for scope,ds in dialogs.items():
  pool=[]
  for d in ds:
   t=next((t for t in d['turns'] if t['role']=='user'),None)
   if t and len(words(t['utterance']))>=3:pool.append({'id':d['dial_id'],'scope':scope,'question':t['utterance']})
  pool.sort(key=lambda q:hashlib.sha256(('source-preflight:'+q['id']).encode()).hexdigest())
  queries.extend(pool[:50]);stats[scope]['n_train_dialogues']=len(ds);stats[scope]['n_preflight_queries']=min(50,len(pool))
 indexes={}
 for scope in docs:
  subset=[u for u in units if u['scope']==scope];inv=defaultdict(list);lens=[]
  for i,u in enumerate(subset):
   c=Counter(words(u['text']));lens.append(sum(c.values()))
   for w,f in c.items():inv[w].append((i,f))
  indexes[scope]=(subset,inv,lens,statistics.mean(lens))
 rows=[];candidates=[]
 for q in queries:
  subset,inv,lens,avg=indexes[q['scope']];scores=defaultdict(float);n=len(subset)
  for w in set(words(q['question'])):
   postings=inv.get(w,[]);idf=math.log(1+(n-len(postings)+.5)/(len(postings)+.5))
   for i,f in postings:scores[i]+=idf*f*2.5/(f+1.5*(.25+.75*lens[i]/avg))
  ranked=sorted(scores,key=lambda i:(-scores[i],subset[i]['id']))
  for k in [5,10,20]:
   chosen=[subset[i] for i in ranked[:k]];cost=sum(u['tokens'] for u in chosen)
   rows.append({'id':q['id'],'scope':q['scope'],'k':k,'n_candidates':len(chosen),'candidate_tokens':cost})
   if k==20:candidates.append(q|{'candidate_ids':[u['id'] for u in chosen],'retrieval_provenance':'BM25 k1=1.5 b=0.75, same-domain original sections; first training user turn; no references or answers'})
 dump('candidate_requests_top20.jsonl',candidates)
 summary={'status':'source_only_engineering_feasibility_not_real_deployment_budget_or_effectiveness','domains':stats,'n_queries':len(queries),'tokenizer':'Qwen2.5-7B fixed revision','no_paid_model_calls':True,'results':[],'rows':rows}
 for k in [5,10,20]:
  cs=[x['candidate_tokens'] for x in rows if x['k']==k]
  summary['results'].append({'k':k,'median_candidate_tokens':statistics.median(cs),'min_tokens':min(cs),'max_tokens':max(cs),'exceeds_simulated_budget_fraction':{str(b):sum(c>b for c in cs)/len(cs) for b in [512,1024,2048]}})
 (ROOT/'multidoc_source_preflight.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in summary.items() if k!='rows'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
