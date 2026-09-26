"""Count source-literal definition matches in SARA train without case labels/Prolog."""
import json,re,tarfile,collections,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
archive=ROOT/'candidate_sources/sara.tar.gz'
train=(ROOT/'candidate_sources/sara_inspect/sara/splits/train').read_text().splitlines()
MAP={'2':{'a':'surviving spouse','b':'head of household'},'152':{'a':'dependent','c':'qualifying child','d':'qualifying relative'},'151':{'d':'exemption amount'},'63':{'a':'taxable income','c':'standard deduction','d':'itemized deductions'},'68':{'b':'applicable amount'},'3306':{'a':'employer','b':'wages','c':'employment'}}
TERMS=sorted({v for d in MAP.values() for v in d.values()}|{'applicable percentage'})
with tarfile.open(archive,'r:gz') as t:
 names={m.name for m in t.getmembers()}
 rows=[]
 for case in train:
  fn='sara/cases/'+case+'.pl'
  if fn not in names:continue
  text=t.extractfile(fn).read().decode()
  m=re.search(r'^% Text\s*\n(.*?)(?=^% Question)',text,re.M|re.S)
  q=re.search(r'^% Question\s*\n(.*?)(?=^% Facts)',text,re.M|re.S)
  if not m or not q:continue
  visible=m.group(1)+' '+q.group(1)
  visible=re.sub(r'\b(?:Entailment|Contradiction)\s*$', '',visible,flags=re.I)
  target=re.match(r's(\d+)_([a-z])_',case)
  tagged=set()
  if target:tagged.add(MAP.get(target.group(1),{}).get(target.group(2),''))
  tagged.discard('')
  literal={x for x in TERMS if re.search(r'(?<!\w)'+re.escape(x)+r'(?!\w)',visible,re.I)}
  rows.append({'case_id_without_label':re.sub(r'_(?:pos|neg)$','',case),'n_literal_names':len(literal),'n_plus_section_target':len(literal|tagged),'literal_names':sorted(literal),'with_section_target':sorted(literal|tagged)})
counts=collections.Counter(r['n_plus_section_target'] for r in rows)
report={'status':'source_only_literal_lower_bound_not_validated_definition_matching','n_train_cases':len(train),'n_readable_cases':len(rows),'n_named_candidates':len(TERMS),'count_distribution':dict(sorted(counts.items())),'fraction_at_least_two_with_section_target':sum(r['n_plus_section_target']>=2 for r in rows)/len(rows),'warning':'This uses exact term names plus the section named in the prompt. It excludes semantic aliases and source dependencies, so failure of 40% here does not prove every legitimate matcher fails. It also does not validate complete definitions or compute token budget. No target answers were read.','rows':rows}
(ROOT/'sara_literal_match_counts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print({k:report[k] for k in ['n_train_cases','n_readable_cases','n_named_candidates','count_distribution','fraction_at_least_two_with_section_target']})
