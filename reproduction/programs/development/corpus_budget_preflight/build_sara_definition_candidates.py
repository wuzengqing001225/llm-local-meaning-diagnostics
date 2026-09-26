"""Exact source-span candidates for SARA; semantic closure still provisional."""
import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'candidate_sources/sara_inspect/sara/statutes/source'
# Extra tax-law cross-references are included only where the candidate's meaning requires them.
SPECS=[
 ('surviving_spouse','surviving spouse','section2',['a'],['dependent']),
 ('head_of_household','head of household','section2',['b'],['surviving_spouse','dependent']),
 ('dependent','dependent','section152',['a','b'],['qualifying_child','qualifying_relative']),
 ('qualifying_child','qualifying child','section152',['c'],[]),
 ('qualifying_relative','qualifying relative','section152',['d'],['qualifying_child']),
 ('taxable_income','taxable income','section63',['a','b'],['standard_deduction','itemized_deductions']),
 ('standard_deduction','standard deduction','section63',['c','f'],[]),
 ('itemized_deductions','itemized deductions','section63',['d'],[]),
 ('employer','employer','section3306',['a'],['wages','employment']),
 ('wages','wages','section3306',['b'],[]),
 ('employment','employment','section3306',['c'],[]),
 ('exemption_amount','exemption amount','section151',['d'],[]),
 ('applicable_amount','applicable amount','section68',['b'],[]),
 ('married','married','section7703',['a','b'],[]),
]
def split_parts(text):
 matches=list(re.finditer(r'(?m)^\(([a-z])\) [^\n]+',text));out={}
 for j,m in enumerate(matches):out[m.group(1)]=(text[m.start():matches[j+1].start() if j+1<len(matches) else len(text)].strip(),m.start(),matches[j+1].start() if j+1<len(matches) else len(text))
 return out
rows=[]
for ident,term,src,letters,deps in SPECS:
 full=(SOURCE/src).read_text();parts=split_parts(full);sub=[];refs=[]
 for part in letters:
  text,a,b=parts[part];assert full[a:b].strip()==text
  sub.append(text);refs.append({'file':src,'subsection':part,'start':a,'end':b,'text_sha256':hashlib.sha256(text.encode()).hexdigest()})
 rows.append({'id':'sara:'+ident,'term':term,'scope':'sara:us_federal_tax_simplified','unit_type':'local_definition','definition':'\n\n'.join(sub),'source_ref':src+' '+','.join(letters),'source_spans':refs,
              'dependencies':['sara:'+d for d in deps],'validation_status':'exact_source_span_semantics_provisional'})
( ROOT/'sara_definition_candidates.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows))
print('Saved',len(rows),'exact-source candidate definition units; semantic completeness is provisional')
