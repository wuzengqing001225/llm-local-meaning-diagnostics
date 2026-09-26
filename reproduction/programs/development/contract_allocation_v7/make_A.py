import argparse,re,json
from common import *
EXTRACT='''You prepare source-grounded research diagnostics from a complete contract. Extract the COMPLETE definition of the target term, not the potentially truncated supplied extraction. Also extract any exact source clauses necessary to resolve its meaning and exclusions. Do not invent or paraphrase quotations. Preserve quotation text verbatim. Decide whether a useful closed set of 6 meaning/use diagnostics and concrete application questions is possible using this source. Missing essential exhibits or redacted essential rules make it ineligible; do not pretend they are present. Return JSON {"eligible":bool,"main_quote":"verbatim complete definition","dependency_quotes":["verbatim"],"reason":"...","boundary_summary":"..."}. Do not select based on what a reader model might get wrong.'''
SOURCE_CHECK='''Independently audit a proposed definition note against the complete original contract. Is the main definition complete, are the quotations faithful, and are necessary dependencies present for meaningful diagnostics? Flag any missing essential exhibits, redactions, or exceptions. Merely needing concrete case facts is not a missing definition. Return JSON {"eligible":bool,"definition_complete":bool,"dependencies_sufficient":bool,"reason":"..."}. No model outcomes are available.'''
A_DRAFT='''Create exactly SIX diagnostic A questions about the meaning of a contract term in original usage. You see a verified local definition and actual usage contexts. No B questions exist yet. This is a meaning/use diagnostic, NOT six fabricated membership scenarios. Use diverse contexts and different facets of the rule. Each question must be understandable on its own with the term name and at most a short source-use phrase. Do not display the definition or correct conclusion in the stem. Source context is drafting provenance, not automatically reader-visible. Make four parallel plausible interpretation options, exactly one entailed by the complete local definition and usage. Avoid explicit answer cues, "all of above", overlapping alternatives, and unnecessary terms. At least 3 distinct context indices if available. Return {"items":[{"question":"...","options":[four strings],"answer":"A|B|C|D","context_index":0,"source_evidence":"exact supporting span from supplied source note","facet":"..."},...]} with six items. Distribute correct answers across A/B/C/D. Do not call an option correct just because the others are worse.'''
A_CHECK='''Independently answer each diagnostic using the source note and usage context. You are not shown the proposed answer. Evaluate whether the question is a meaning/use diagnostic (not a fabricated membership scenario), the stem avoids disclosing its answer, options are mutually exclusive enough and exactly one is supported. Return {"items":[{"id":"...","answer":"A|B|C|D|undetermined","valid":bool,"reason":"..."}]} for every item. Missing definition dependencies, ambiguous answers, and unsupported source claims must fail. No target outcomes or scores are available.'''
norm=lambda s:re.sub(r'\s+',' ',s).strip()
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);a=p.parse_args()
 frames=read('source_frame.jsonl');fmap={x['definition_id']:x for x in frames}
 proposed=batch(a.config,'author',[(x['definition_id'],{'term':x['term'],'extracted_unverified':x['extracted_definition_unverified'],'full_contract':x['source_text']}) for x in frames],'source_proposals.jsonl',EXTRACT)
 # Compact only semantic dependencies, not every contractual obligation.
 compact_system="""Produce a minimal complete source note for interpreting the meaning and membership scope of the target term. This is NOT an audit of all rights, licenses, obligations, termination remedies, or commercial permissions under the contract. Retain the entire main definition verbatim. Add exact quotations ONLY of definitions or clauses directly needed to interpret that definition. Do not add operative grants merely because they USE the target term. Missing unrelated operational time limits do not invalidate meaning diagnostics. Eligibility requires at least some determinate applications and 6 diverse meaning/use questions using disclosed semantics; questions must stay inside that stated scope. If an essential referenced definition is missing, flag it. Return {\"eligible\":bool,\"main_quote\":\"verbatim\",\"dependency_quotes\":[\"verbatim\"],\"reason\":\"...\",\"scope_restrictions\":[\"...\"]}.""" 
 compact=batch(a.config,'author',[(x['definition_id'],{'term':x['term'],'main_definition':proposed[x['definition_id']]['result']['main_quote'],'full_contract':x['source_text']}) for x in frames],'source_notes_v2.jsonl',compact_system,6000)
 candidates=[];decisions=[]
 for f in frames:
  r=compact[f['definition_id']]['result'];quotes=[r.get('main_quote','')]+r.get('dependency_quotes',[])
  exact=bool(quotes[0]) and all(isinstance(q,str) and norm(q) in norm(f['source_text']) for q in quotes)
  decisions.append({'definition_id':f['definition_id'],'author_eligible':r.get('eligible') is True,'quotes_exact':exact,'reason':r.get('reason')})
  if exact and r.get('eligible') is True:
   candidates.append({k:f[k] for k in ['definition_id','term','contract_index','source_cohort','source_sha256','usage_contexts']}|{'main_quote':quotes[0],'dependency_quotes':quotes[1:],'rule_quote':'\n'.join(quotes),'scope_restrictions':r.get('scope_restrictions',[])})
 write('source_semantic_decisions.jsonl',decisions)
 semantic_check="""Audit the proposed note for interpreting ONLY the meaning and membership scope of the target term. This is NOT a legal-rights, exclusivity, payment, remedy or full-contract compliance task. Ignore omitted provisions that merely USE the term without changing its meaning. Is the main definition complete and faithful, and are directly necessary semantic dependencies available for questions restricted to the stated scope? Redactions in unrelated operational obligations do not invalidate classification. Return {\"eligible\":bool,\"definition_complete\":bool,\"dependencies_sufficient\":bool,\"reason\":\"...\"}."""
 checked=batch(a.config,'judge',[(x['definition_id'],{'term':x['term'],'proposed_note':x['rule_quote'],'scope_restrictions':x['scope_restrictions'],'full_contract':fmap[x['definition_id']]['source_text']}) for x in candidates],'source_semantic_checks.jsonl',semantic_check,2500)
 cards=[x for x in candidates if all(checked[x['definition_id']]['result'].get(k) is True for k in ['eligible','definition_complete','dependencies_sufficient'])]
 write('source_cards.jsonl',cards)
 print('SOURCE ACCEPTED',len(cards),'/',len(frames),flush=True)
 drafts=batch(a.config,'author',[(x['definition_id'],{'term':x['term'],'source_note':x['rule_quote'],'usage_contexts':x['usage_contexts'],'scope_restrictions':x['scope_restrictions']}) for x in cards],'A_drafts.jsonl',A_DRAFT,6000)
 candidate_A=[]
 for c in cards:
  items=drafts[c['definition_id']]['result'].get('items',[])
  if len(items)!=6:continue
  for i,x in enumerate(items):
   if not (isinstance(x.get('question'),str) and len(x.get('options',[]))==4 and x.get('answer') in 'ABCD' and isinstance(x.get('context_index'),int) and 0<=x['context_index']<len(c['usage_contexts'])):continue
   candidate_A.append({**x,'id':c['definition_id']+':A'+str(i+1),'definition_id':c['definition_id'],'term':c['term'],'contract_index':c['contract_index'],'study_split':'A'})
 write('A_candidates.jsonl',candidate_A)
 checks=batch(a.config,'judge',[(c['definition_id'],{'term':c['term'],'source_note':c['rule_quote'],'items':[{k:x[k] for k in ['id','question','options']}|{'source_usage':c['usage_contexts'][x['context_index']]} for x in candidate_A if x['definition_id']==c['definition_id']]}) for c in cards],'A_checks.jsonl',A_CHECK,7000)
 verdicts={y['id']:y for row in checks.values() for y in row['result'].get('items',[])}
 accepted=[];dec=[]
 for x in candidate_A:
  v=verdicts.get(x['id'],{});good=v.get('valid') is True and v.get('answer')==x['answer']
  dec.append({'id':x['id'],'accepted_individually':good,'draft_answer':x['answer'],'verdict':v})
  if good:accepted.append(x|{'status':'model_source_checked_provisional'})
 good_dids={c['definition_id'] for c in cards if sum(x['definition_id']==c['definition_id'] for x in accepted)>=4}
 accepted=[x for x in accepted if x['definition_id'] in good_dids]
 cards=[x for x in cards if x['definition_id'] in good_dids]
 write('A_quality_decisions.jsonl',dec);write('diagnostics_A.jsonl',accepted);write('cards_for_A.jsonl',cards)
 print('A ACCEPTED',len(accepted),'items in',len(cards),'rules',flush=True)
 if not cards:raise RuntimeError('No quality-accepted A rules; stop before B')
if __name__=='__main__':main()
