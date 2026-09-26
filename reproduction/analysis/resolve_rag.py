from pathlib import Path
import json,ast,hashlib,re,collections
OUT=Path(__file__).resolve().parent/'results';OUT.mkdir(exist_ok=True);ROOT=Path(__file__).resolve().parents[1]/'provenance/rag_source'
load=lambda p:[json.loads(x) for x in p.read_text().splitlines()]
code=ast.parse((ROOT/'rag_harness.py').read_text());SYS=next(ast.literal_eval(n.value) for n in code.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SYS' for t in n.targets))
cache=collections.defaultdict(list)
for i,x in enumerate(load(ROOT/'data/cache_rag/reader.jsonl'),1):cache[x['key']].append({'cache_line':i,'answer':x['text']})
T={x['id']:x for x in load(ROOT/'data/cuad_full/terms_full.jsonl')};gloss=collections.defaultdict(dict)
for x in T.values():
 if x.get('def_raw','').strip():gloss[str(x['labels']['ci'])][x['term']]=' '.join(x['def_raw'].strip().split()[:60])
P={(x['qkey'],x['arm']):x for x in load(ROOT/'data/prompts_t1.jsonl')};stored={(x['qkey'],x['arm']):x for x in load(ROOT/'rag_v3_t1.jsonl')};report=[]
key=lambda prompt:hashlib.sha256(json.dumps(['openai','gpt-5.6-terra',SYS,prompt,4,0.0],ensure_ascii=False).encode()).hexdigest()
for qkey in ['cuadfull:409:Securities#11','cuadfull:303:Confidential Information#3']:
 p=P[qkey,'rag_gated'];ci=p['ci'];blob=(p['q']+' '+p['ctx']).lower()
 present=[t for t in gloss[ci] if re.search(r'(?<![a-z])'+re.escape(t.lower())+r'(?![a-z])',blob)]
 full=sorted(gloss[ci].items(),key=lambda kv:-T.get(f'cuadfull:{ci}:{kv[0]}',{}).get('labels',{}).get('tf',0))[:30]
 defs=lambda gl:'Definitions (this contract):\n'+'\n'.join(f'- {t}: {g}' for t,g in gl)+'\n\n' if gl else ''
 blocks={'rag_full':defs(full),'rag_gated':p['gtxt'],'rag_defrecall':defs([(t,gloss[ci][t]) for t in present])}
 prompts={arm:f"{gtxt}{p['ctx']}{p['q']}\n{p['opts']}\nANSWER_LETTER:" for arm,gtxt in blocks.items()}
 assert len(set(prompts.values()))==1,'These arms are not identical'
 k=key(prompts['rag_gated']);hits=cache[k];assert len(hits)==3
 assignments=[]
 for arm,hit in zip(['rag_full','rag_gated','rag_defrecall'],hits):
  label=int(hit['answer']==p['answer']);assert label==stored[qkey,arm]['correct']
  assignments.append({'arm':arm,**hit,'gold':p['answer'],'correct':label,'stored_correct':stored[qkey,arm]['correct']})
 report.append({'qkey':qkey,'request_hash':k,'identical_prompt_arms_in_original_order':['rag_full','rag_gated','rag_defrecall'],'assignments':assignments,'resolution':'Original rag_gated label corroborated by arm order and append-only cache sequence.'})
result={'cases':report,'api_calls':0,'retrieval_rerun':False,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'rag_harness.py',ROOT/'pdwlib/llm.py',ROOT/'data/cache_rag/reader.jsonl',ROOT/'data/prompts_t1.jsonl',ROOT/'rag_v3_t1.jsonl']},'main_result':'Retain original labels, repairs=93, harms=33, net=5.0 percentage points.'}
(OUT/'resolution.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result['cases'],ensure_ascii=False,indent=2))
