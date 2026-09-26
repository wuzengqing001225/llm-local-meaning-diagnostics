import argparse,json,hashlib,re
from common import *
DRAFT='''Create exactly 6 independent research requests for the supplied local contract definition. You do not see diagnostic A items, A answers, scores, strata, or target reader outcomes. Four requests must ask a concrete applicability question, and TWO must be definition-irrelevant factual controls. Use fresh concrete situations, realistic entities, actions, dates or objects. Do not convert a Boolean predicate checklist directly into prose. Do not disclose the definition, local inclusion/exclusion conclusion, or whether an exception is satisfied in the bare stem. State enough world facts to permit an unambiguous answer once the definition is supplied. Missing exhibits and uncertain background facts cannot be assumed. In the four applicability requests, cover both inclusion and exclusion, with varied rule facets; use source-explicit boundaries where present but do not force ordinary-meaning conflict for inherently unspecified territories or scopes. Aim for two yes and two no source answers. Controls must mention the target term naturally and a concrete object potentially affected by its definition, but ask about a separately stated price, count, date, sender or event. One control should answer yes and one no. E.g. a record mentions Products and lists a doughnut at $3, then asks whether the listed amount is $3; membership must be irrelevant. Avoid pronoun ambiguity or calling a weekday a calendar date. Controls can require one straightforward comparison, not merely repeat an isolated sentence. Return {"items":[{"kind":"application|control","world_facts":"...","question":"self-contained question including ALL needed facts, asking yes/no","answer":"yes|no","source_evidence":"exact source span or control facts supporting answer","mapping":"how concrete facts map to source, never shown to reader"},...]} with exactly 4 applications and 2 controls. No inference about what a target model will answer is allowed.'''
CHECK='''Independently answer and audit every question from the supplied local source note. Proposed answers and source mappings are hidden. For application questions, the source and stated concrete facts must suffice for one answer. Reject unsupported assumptions, missing cross-references, ambiguous classified objects, impossible situations, or source predicate checklists disguised as facts. Concrete category names and natural overlap are allowed; low lexical overlap alone is not evidence. For controls, answer from stated facts alone and verify local membership cannot change that answer, even though the term is mentioned. Return {"items":[{"id":"...","answer":"yes|no|undetermined","valid":bool,"facts_sufficient":bool,"no_semantic_leakage":bool,"definition_irrelevant":bool,"reason":"..."}]}. Do not require the bare application question to be answerable without the local definition. No target outcomes are available.'''
USUAL='''You see a question and term, but no local contract definition. For an application question, classify using ordinary English meaning, ignoring an unspecified contract's bespoke definition. Return yes or no only if that ordinary meaning and the stated facts determine it. Return undetermined when a territory, relationship, exclusion scope or required fact is unspecified. Do not invent local policy or guess. Return {"answer":"yes|no|undetermined","reason":"..."}.'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);a=p.parse_args()
 if (ROOT/'B_freeze.json').exists() and (ROOT/'agent_source_review.json').exists():
  frozen=json.loads((ROOT/'B_freeze.json').read_text())
  for f,h in frozen['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
  print('B already source-reviewed and frozen; no regeneration',flush=True);return
 freeze=json.loads((ROOT/'A_freeze.json').read_text())
 for f,h in freeze['sha256'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
 cards=read('B_author_rules.jsonl');cmap={x['definition_id']:x for x in cards}
 ds=batch(a.config,'author',[(x['definition_id'],{'term':x['term'],'local_source':x['rule_quote'],'application_quota':4,'control_quota':2}) for x in cards],'B_drafts.jsonl',DRAFT,6000)
 candidates=[]
 for c in cards:
  items=ds[c['definition_id']]['result'].get('items',[])
  if len(items)!=6 or sum(x.get('kind')=='application' for x in items)!=4 or sum(x.get('kind')=='control' for x in items)!=2:continue
  for i,x in enumerate(items):
   if x.get('answer') not in ['yes','no'] or not isinstance(x.get('question'),str):continue
   candidates.append({**x,'id':c['definition_id']+':B'+str(i+1),'definition_id':c['definition_id'],'term':c['term'],'contract_index':c['contract_index']})
 write('B_candidates.jsonl',candidates)
 checked=batch(a.config,'judge',[(c['definition_id'],{'term':c['term'],'source_note':c['rule_quote'],'items':[{k:x[k] for k in ['id','kind','question']} for x in candidates if x['definition_id']==c['definition_id']]}) for c in cards],'B_checks.jsonl',CHECK,7000)
 verdicts={x['id']:x for row in checked.values() for x in row['result'].get('items',[])}
 decisions=[];accepted=[]
 for x in candidates:
  v=verdicts.get(x['id'],{});good=all(v.get(k) is True for k in ['valid','facts_sufficient','no_semantic_leakage']) and v.get('answer')==x['answer']
  if x['kind']=='control':good=good and v.get('definition_irrelevant') is True
  decisions.append({'id':x['id'],'accepted':good,'draft_answer':x['answer'],'verdict':v})
  if good:accepted.append(x)
 write('B_quality_decisions.jsonl',decisions)
 # Label every candidate application, including rejected ones, preserving the full audit trail.
 usual=batch(a.config,'author',[(x['id'],{'term':x['term'],'question':x['question']}) for x in candidates if x['kind']=='application'],'B_usual_labels.jsonl',USUAL,1600)
 accepted.sort(key=lambda x:x['id'])
 public=[];private=[]
 for i,x in enumerate(accepted):
  gold='AB'[i%2];other='No' if x['answer']=='yes' else 'Yes';opts=[x['answer'].capitalize(),other] if gold=='A' else [other,x['answer'].capitalize()]
  ordinary=usual[x['id']]['result'].get('answer') if x['kind']=='application' else None
  if x['kind']=='application' and ordinary not in ['yes','no','undetermined']:raise ValueError('Invalid ordinary label')
  group='control' if x['kind']=='control' else ('undetermined' if ordinary=='undetermined' else ('agreement' if ordinary==x['answer'] else 'conflict'))
  pub={k:x[k] for k in ['id','definition_id','term','question']}|{'options':opts}
  public.append(pub);private.append(pub|{'gold':gold,'source_answer':x['answer'],'group':group,'ordinary_answer':ordinary,'kind':x['kind'],'contract_index':x['contract_index'],'mapping':x['mapping'],'status':'provisional_model_checked_not_human_gold'})
 write('tasks_public.jsonl',public);write('tasks_private.jsonl',private)
 frozen=['A_freeze.json','A_rule_scores.jsonl','cards_for_A.jsonl','tasks_public.jsonl','tasks_private.jsonl','B_quality_decisions.jsonl','B_usual_labels.jsonl','protocol.md']
 (ROOT/'B_freeze.json').write_text(json.dumps({'status':'B_frozen_before_readers','n_tasks':len(public),'n_rules':len(cards),'sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in frozen}},indent=2)+'\n')
 from collections import Counter
 print('B FROZEN',len(public),dict(Counter(x['group'] for x in private)),flush=True)
if __name__=='__main__':main()
