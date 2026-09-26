"""Lower-bound extraction of explicit named definitions in public Housing rows.
The label/reference_prolog columns are deliberately not read.
"""
import re,json,collections,statistics
from pathlib import Path
import pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parent
P=ROOT/'candidate_sources/deonticbench/housing_whole.parquet'
# Exact written forms only; no generic paragraph, rule or quoted evidence is counted.
PATTERNS=[re.compile(r'(?i)\b(?:the\s+)?term\s+["“]([^"”]{2,90})["”]\s+(?:shall\s+)?(?:mean|means|include|includes)\b'),
          re.compile(r'(?i)["“]([^"”]{2,90})["”]\s+(?:shall\s+)?(?:mean|means|include|includes)\b'),
          re.compile(r'(?i)\b(?:the\s+)?term\s+[\'‘]([^\'’]{2,90})[\'’]\s+(?:shall\s+)?(?:mean|means|include|includes)\b')]
rows=[]
for batch in pq.ParquetFile(P).iter_batches(batch_size=256,columns=['id','state','question','statutes']):
 for x in batch.to_pylist():
  text=x['statutes'] or '';q=x['question'] or ''
  found={m.group(1).strip().casefold() for pat in PATTERNS for m in pat.finditer(text)}
  matched=[t for t in found if re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',q,re.I)]
  rows.append({'id':x['id'],'state':x['state'],'n_explicit_named_definitions_in_supplied_statutes':len(found),'n_named_definitions_mentioned_in_question':len(matched),
               'question':q,'explicit_names':sorted(found)[:30],'question_names':sorted(matched)})
c=collections.Counter(r['n_explicit_named_definitions_in_supplied_statutes'] for r in rows);d=collections.Counter(r['n_named_definitions_mentioned_in_question'] for r in rows)
result={'status':'lower_bound_source_only_named_definition_screen_not_formal_matching','n':len(rows),'n_with_2_names_in_statutes':sum(r['n_explicit_named_definitions_in_supplied_statutes']>=2 for r in rows),'n_with_2_names_explicit_in_question':sum(r['n_named_definitions_mentioned_in_question']>=2 for r in rows),
        'statutes_name_count_distribution':dict(sorted(c.items())),'question_name_count_distribution':dict(sorted(d.items())),
        'limitation':'Regex misses other legal definition forms. Statute excerpts in the dataset are case-specific and may already be gold-relevant. Named definitions are candidates only; no term completeness or relevance check. Labels and Prolog were not read.',
        'examples':[r for r in rows if r['n_explicit_named_definitions_in_supplied_statutes']>=2][:8]}
(ROOT/'deontic_housing_named_definition_preview.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print({k:result[k] for k in ['n','n_with_2_names_in_statutes','n_with_2_names_explicit_in_question']});print('statute distribution first',dict(list(sorted(c.items()))[:8]))
if __name__=='__main__':pass
