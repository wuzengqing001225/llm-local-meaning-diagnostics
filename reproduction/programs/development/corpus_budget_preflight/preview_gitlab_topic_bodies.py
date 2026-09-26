"""Source-only body preview of pre-existing GitLab forum questions in three domains."""
import json,hashlib,datetime,urllib.request,collections,re,html
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'candidate_sources'
cutoff=datetime.datetime(2026,9,25,12,57,tzinfo=datetime.timezone.utc)
ids={}
for query in ['subscription','billing','license']:
 data=json.loads((SOURCE/f'gitlab_forum_search_{query}.json').read_text())
 xs=[]
 for t in data['topics']:
  dt=datetime.datetime.fromisoformat(t['created_at'].replace('Z','+00:00'))
  if dt<=cutoff:xs.append(t)
 xs.sort(key=lambda x:hashlib.sha256((query+':'+str(x['id'])).encode()).hexdigest())
 for t in xs[:10]:ids[t['id']]={'id':t['id'],'title':t['title'],'created_at':t['created_at'],'source_queries':sorted(set(ids.get(t['id'],{}).get('source_queries',[])+[query]))}
catalog=[json.loads(x) for x in (ROOT/'gitlab_definition_candidates_provisional.jsonl').read_text().splitlines()]
patterns=[]
for unit in catalog:
 pp=[re.compile(r'(?<!\w)'+re.escape(a).replace(r'\ ',r'\s+')+r'(?!\w)',re.I) for a in unit['aliases']]
 patterns.append((unit,pp))
def fetch(t):
 request=urllib.request.Request('https://forum.gitlab.com/t/'+str(t['id'])+'.json',headers={'User-Agent':'Mozilla/5.0 (Research preflight)'})
 with urllib.request.urlopen(request,timeout=25) as response:data=json.load(response)
 posts=data.get('post_stream',{}).get('posts',[])
 if not posts:return {'id':t['id'],'error':'missing first post'}
 first=min(posts,key=lambda x:x.get('post_number',999999))
 text=BeautifulSoup(first.get('cooked',''),'html.parser').get_text(' ',strip=True)
 if first.get('post_number')!=1:return {'id':t['id'],'error':'first post missing'}
 words=t['title']+'\n'+html.unescape(text)
 matched=[u['id'] for u,pp in patterns if any(p.search(words) for p in pp)]
 return {'id':t['id'],'created_at':t['created_at'],'source_queries':t['source_queries'],'scope':'gitlab:public_organization','matched_definition_ids':sorted(matched),
         'body_characters':len(text),'matcher_provenance':'pre-cutoff public forum first post; exact glossary names/aliases; no replies, answer labels or model outcomes'}
outs=[]
with ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(fetch,t):t['id'] for t in ids.values()}
 for fut in as_completed(futures):
  try:outs.append(fut.result())
  except Exception as e:outs.append({'id':futures[fut],'error':type(e).__name__})
outs.sort(key=lambda x:x['id']);(ROOT/'gitlab_forum_body_sample_matches.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in outs))
valid=[x for x in outs if not x.get('error')];c=collections.Counter(len(x['matched_definition_ids']) for x in valid)
report={'status':'bounded_source_only_sample_not_formal_B','n_requested':len(ids),'n_fetched':len(valid),'n_failures':len(outs)-len(valid),'n_with_two_plus':sum(len(x['matched_definition_ids'])>=2 for x in valid),'match_distribution':dict(sorted(c.items())),'limitations':['Search domains preselect subscription, billing, license; not general forum traffic.','Only first post body used; replies/accepted solutions are not gold labels.','Glossary definitions are provisional and current snapshot may not match older post date.']}
(ROOT/'gitlab_forum_body_sample_preview.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print({k:report[k] for k in ['n_requested','n_fetched','n_failures','n_with_two_plus','match_distribution']})
