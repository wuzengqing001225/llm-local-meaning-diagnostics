"""Assistant source-only vetoes declared before target responses; never reads outcomes."""
import json,hashlib
from collections import Counter
from common import *
# IDs are original candidate slots. These are based on visible question wording only.
VETO={**{f'cuadfull:39:Force Majeure:B{i}':'Abstract reasonable-control / professional-prudence predicates are asserted directly instead of derived from concrete observations.' for i in [1,2,3]},
      **{f'cuadfull:130:Support Request:B{i}':'Invented software is asserted to be a Deployed Product or to meet a defined severity class; the required source-specific mapping is supplied as a predicate.' for i in [1,2,3,4]},
      **{f'cuadfull:268:Regulatory Approval:B{i}':'The question assumes use in the contract Field, whose concrete scope is not established in the scenario; source-specific class membership is given as a predicate.' for i in [1,2,3,4]},
      'cuadfull:329:Third Party Agreements:B3':'The non-Affiliate / Lead Compound status is asserted as a source-specific category without a concrete mapping.',
      'cuadfull:329:Third Party Agreements:B4':'The negative application recites the target definition activities and supplies their inapplicability directly.',
      'cuadfull:129:Net Revenue:B4':'Excluded Theatre and outside-Service predicates are supplied directly, avoiding the mapping from concrete observations.'}

def apply():
 if (ROOT/'reader_results.jsonl').exists():raise RuntimeError('Cannot change source gate after reader outcomes')
 review=ROOT/'agent_source_review.json'
 if review.exists():
  r=json.loads(review.read_text());assert r['tasks_public_sha256']==hashlib.sha256((ROOT/'tasks_public.jsonl').read_bytes()).hexdigest();return
 private=read('tasks_private.jsonl');public=read('tasks_public.jsonl')
 # Keep immutable pre-gate candidate files for the audit trail.
 write('tasks_private_before_source_gate.jsonl',private);write('tasks_public_before_source_gate.jsonl',public)
 pre={t['id']:t for t in private};kept=[t for t in private if t['id'] not in VETO]
 napps=Counter(t['definition_id'] for t in kept if t['kind']=='application')
 rules={t['definition_id'] for t in kept};drop={did for did in rules if napps[did]<2}
 kept=[t for t in kept if t['definition_id'] not in drop]
 # Balance answer positions again, prior to all target calls.
 pubs=[]
 for i,t in enumerate(kept):
  gold='AB'[i%2];yesno=t['source_answer'].capitalize();other='No' if yesno=='Yes' else 'Yes'
  t['options']=[yesno,other] if gold=='A' else [other,yesno];t['gold']=gold
  pubs.append({k:t[k] for k in ['id','definition_id','term','question','options']})
 write('tasks_private.jsonl',kept);write('tasks_public.jsonl',pubs)
 r={'status':'source_only_assistant_review_before_target_calls','n_before':len(private),'n_after':len(kept),'explicit_vetoes':VETO,'rules_dropped_fewer_than_two_applications':sorted(drop),
    'decision_basis':'Source-wording quality only. Ordinary labels and target outcomes not used. Assistant review is not independent human annotation.',
    'tasks_public_sha256':hashlib.sha256((ROOT/'tasks_public.jsonl').read_bytes()).hexdigest()}
 review.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 m=json.loads((ROOT/'B_freeze.json').read_text());(ROOT/'B_freeze_before_source_gate.json').write_text(json.dumps(m,indent=2)+'\n')
 m['n_tasks']=len(kept);m['n_rules_with_B']=len({t['definition_id'] for t in kept})
 for f in ['tasks_public.jsonl','tasks_private.jsonl','agent_source_review.json','source_review_gate.py']:
  m['sha256'][f]=hashlib.sha256((ROOT/f).read_bytes()).hexdigest()
 (ROOT/'B_freeze.json').write_text(json.dumps(m,indent=2)+'\n')
 print('Source-only assistant gate:',len(private),'->',len(kept),'tasks;',len({t['definition_id'] for t in kept}),'rules',flush=True)
if __name__=='__main__':apply()
