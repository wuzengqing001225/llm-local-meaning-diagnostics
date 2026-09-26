"""Source-only diagnostic of whether ANY absolute budget permits definition choice.
This cannot change the locked median-half rule or validate a provisional glossary.
"""
import argparse,json,os,collections,itertools
from pathlib import Path
from definition_budget_preflight import rows,closure,render
p=argparse.ArgumentParser();p.add_argument('--definitions',type=Path,required=True);p.add_argument('--requests',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
os.environ['HF_HUB_OFFLINE']='1'
from transformers import AutoTokenizer
tok=AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B',revision='d149729398750b98c0af14eb82c78cfe92750796',local_files_only=True)
cat={x['id']:x for x in rows(a.definitions)};rs=rows(a.requests);cost=lambda ids:len(tok.encode(render(ids,cat),add_special_tokens=False)) if ids else 0
events=collections.Counter();bad=[]
for q in rs:
 ids=q['matched_definition_ids']
 if len(ids)<2:continue
 singles={i:cost(closure([i],cat)) for i in ids}
 intervals=[]
 for left,right in itertools.combinations(ids,2):
  lo=max(singles[left],singles[right]);hi=cost(closure([left,right],cat))-1
  if lo<=hi:intervals.append((lo,hi))
 if not intervals:
  bad.append({'request_id':q['id'],'second_smallest_individual_cost':sorted(singles.values())[1],
              'all_matched_cost':cost(closure(ids,cat))})
  continue
 # A request can have several competing pairs. Count it once at any budget.
 merged=[]
 for lo,hi in sorted(intervals):
  if merged and lo<=merged[-1][1]+1:merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
  else:merged.append((lo,hi))
 for lo,hi in merged:events[lo]+=1;events[hi+1]-=1
cur=0;best=0;at=None
for B,delta in sorted(events.items()):
 cur+=delta
 if cur>best:best=cur;at=B
out={'n_requests':len(rs),'n_with_any_two_individually_affordable_overflow_interval':sum(1 for x in rs if len(x['matched_definition_ids'])>=2)-len(bad),
     'maximum_competing_request_fraction_under_any_absolute_budget':best/len(rs),'budget_at_maximum_fraction':at,
     'scope':'Source-only structural upper envelope on this provisional catalog/matcher. It is NOT a proposal to select the best budget after seeing results; median-half remains the prespecified primary rule.',
     'examples_without_choice_at_any_budget':bad[:12]}
a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({k:out[k] for k in ['n_requests','n_with_any_two_individually_affordable_overflow_interval','maximum_competing_request_fraction_under_any_absolute_budget','budget_at_maximum_fraction']})
