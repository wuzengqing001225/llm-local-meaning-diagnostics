"""Source-only GitLab glossary / public forum topic feasibility screen."""
import json,re,html,hashlib,collections
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'candidate_sources'
CAT=[];by={};screened=[]
for name in ['gitlab_support.html','gitlab_licensing.html']:
 soup=BeautifulSoup((SOURCE/name).read_text(),'html.parser');main=soup.select_one('.td-content')
 for table in main.find_all('table'):
  rows=table.find_all('tr')
  if not rows:continue
  cells=[x.get_text(' ',strip=True).lower() for x in rows[0].find_all(['td','th'])]
  if name=='gitlab_support.html' and not {'acronym','more information'}<=set(cells):continue
  if name=='gitlab_licensing.html' and cells[:2]!=['term','description']:continue
  for rownum,tr in enumerate(rows[1:],1):
   td=tr.find_all('td')
   if len(td)<2:continue
   term=td[0].get_text(' ',strip=True);detail=td[2].get_text(' ',strip=True) if name=='gitlab_support.html' and len(td)>=3 else td[1].get_text(' ',strip=True)
   if name=='gitlab_support.html':
    expanded=td[1].get_text(' ',strip=True)
    definition=expanded+'. '+detail
    # Pure acronym expansion and link-only entries are not source-complete local definitions.
    complete=len(detail.split())>=8 and not re.match(r'^(see\b|read\b|\w+ on wikipedia\b)',detail,re.I)
   else:
    definition=detail;complete=len(detail.split())>=8 and not re.match(r'^see\b',detail,re.I)
   if not complete:
    screened.append({'source':name,'term':term,'row':rownum,'reason':'expansion-only, link-only, or no substantive description'});continue
   key=(name,term.casefold())
   if key in by:
    screened.append({'source':name,'term':term,'row':rownum,'reason':'duplicate term in same glossary'});continue
   by[key]=True
   aliases=[term]
   if name=='gitlab_support.html':aliases.append(expanded)
   else:
    aliases += [re.sub(r'\s*\([^)]*\)','',x).strip() for x in re.split(r'\s*/\s*',term) if x.strip()]
   aliases=list(dict.fromkeys(x for x in aliases if len(x)>=3))
   item={'id':'gitlab:'+hashlib.sha256((name+':'+str(rownum)+':'+term).encode()).hexdigest()[:20],
         'term':term,'definition':definition,'scope':'gitlab:public_organization','source_ref':name+':table_row_'+str(rownum),
         'unit_type':'local_definition','dependencies':[],'validation_status':'provisional_glossary_row_not_human_reviewed','aliases':aliases}
   CAT.append(item)
(ROOT/'gitlab_definition_candidates_provisional.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in CAT))
qraw=[json.loads(x) for x in (SOURCE/'gitlab_forum_topics_preview.jsonl').read_text().splitlines() if x.strip()]
patterns=[]
for x in CAT:
 ps=[]
 for alias in x['aliases']:
  if alias.casefold() in {'user','users','trial','subscription','license','support','issue','seat','seats'}:
   # Common exact names are allowed as candidate matches, but never a relevance oracle.
   pass
  ps.append(re.compile(r'(?<!\w)'+re.escape(alias).replace(r'\ ',r'\s+')+r'(?!\w)',re.I))
 patterns.append((x,ps))
req=[]
for q in qraw:
 text=html.unescape(q['title']+'\n'+(q.get('excerpt') or ''))
 text=BeautifulSoup(text,'html.parser').get_text(' ',strip=True)
 ids=[d['id'] for d,pps in patterns if any(pp.search(text) for pp in pps)]
 req.append({'id':'gitlab_forum:'+str(q['id']),'scope':'gitlab:public_organization','matched_definition_ids':sorted(ids),
             'matcher_provenance':'frozen GitLab forum title/excerpt before 2026-09-25; exact glossary term/declared alias; no post answers or target outcomes'})
(ROOT/'gitlab_forum_definition_matches_provisional.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in req))
ct=collections.Counter(len(x['matched_definition_ids']) for x in req)
summary={'status':'source_only_forum_title_excerpt_preflight_not_formal_B','n_glossary_candidates':len(CAT),'screened_rows':len(screened),'n_forum_questions':len(req),
         'n_with_two_plus':sum(len(x['matched_definition_ids'])>=2 for x in req),'match_distribution':dict(sorted(ct.items())),
         'glossary_source_hashes':{f:hashlib.sha256((SOURCE/f).read_bytes()).hexdigest() for f in ['gitlab_support.html','gitlab_licensing.html']},
         'question_snapshot_hash':hashlib.sha256((SOURCE/'gitlab_forum_topics_preview.jsonl').read_bytes()).hexdigest(),
         'limitations':['Some full descriptions still need source review and may depend on linked policy text.','Forum title/excerpt is not full original post; matcher counts are provisional.','Forum replies are not vetted answer keys.']}
(ROOT/'gitlab_forum_glossary_preview.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['n_glossary_candidates','n_forum_questions','n_with_two_plus','match_distribution']},ensure_ascii=False))
