"""Answer-blind candidate matcher for existing SARA train cases.

These candidates are not gold relevant-definition labels; per-item source review
and complete definition review are still required before a confirmatory study.
"""
import argparse,hashlib,json,re,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT/'candidate_sources/sara.tar.gz'
TARGET={'2':{'a':'surviving_spouse','b':'head_of_household'},'152':{'a':'dependent','c':'qualifying_child','d':'qualifying_relative'},'151':{'d':'exemption_amount'},'63':{'a':'taxable_income','b':'taxable_income','c':'standard_deduction','d':'itemized_deductions'},'68':{'b':'applicable_amount'},'3306':{'a':'employer','b':'wages','c':'employment'},'7703':{'a':'married','b':'married'}}
# Restricted section-specific cues. They can match plausible, non-necessary definitions.
# They do not consult the case answer or target reader output.
CUES={'2':{'surviving_spouse':[r'\bwidow(?:er)?\b',r'\bspouse.{0,45}\b(?:died|death|dead)\b'],
            'head_of_household':[r'\bhousehold\b'], 'married':[r'\bmarried\b',r'\blegally separated\b'],
            'dependent':[r'\bdependent\b']},
      '152':{'dependent':[r'\bdependent\b'], 'qualifying_child':[r'\bchild\b',r'\bson\b',r'\bdaughter\b'],
             'qualifying_relative':[r'\brelative\b',r'\bmother\b',r'\bfather\b']},
      '63':{'taxable_income':[r'\btaxable income\b',r'\badjusted gross income\b'],
            'standard_deduction':[r'\bstandard deduction\b',r'\bdoes not itemize\b'],
            'itemized_deductions':[r'\bitemiz(?:e|ed|ing)\b']},
      '3306':{'employer':[r'\bemployer\b'], 'wages':[r'\bwages?\b',r'\bpaid\b',r'\bsalary\b'],
              'employment':[r'\bemployment\b',r'\blabor\b',r'\bservices?\b']},
      '151':{'exemption_amount':[r'\bexemption\b'], 'dependent':[r'\bdependent\b']},
      '68':{'applicable_amount':[r'\bapplicable amount\b',r'\bthreshold\b'], 'itemized_deductions':[r'\bitemized deduction\b']},
      '7703':{'married':[r'\bmarried\b',r'\bspouse\b'], 'head_of_household':[r'\bhousehold\b']}}

def main():
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['literal','section_cues'],required=True);a=p.parse_args()
 catalog={x['id']:x for x in map(json.loads,(ROOT/'sara_definition_candidates.jsonl').read_text().splitlines())}
 train=(ROOT/'candidate_sources/sara_inspect/sara/splits/train').read_text().splitlines();out=[]
 with tarfile.open(ARCHIVE,'r:gz') as tar:
  members={m.name for m in tar.getmembers()}
  for source_id in train:
   path='sara/cases/'+source_id+'.pl'
   if path not in members:raise ValueError('Missing official train case: '+path)
   content=tar.extractfile(path).read().decode()
   facts=re.search(r'(?ms)^% Text\s*\n(.*?)(?=^% Question)',content)
   claim=re.search(r'(?ms)^% Question\s*\n(.*?)(?=^% Facts)',content)
   if not facts or not claim:raise ValueError('Missing human-language case fields')
   text=facts.group(1)+' '+claim.group(1)
   text=re.sub(r'\b(?:Entailment|Contradiction)\s*$','',text,flags=re.I)
   section=re.search(r'Section\s+(\d+)\s*\(\s*([a-z])\s*\)',claim.group(1),re.I)
   if not section:section=re.match(r's(\d+)_([a-z])_',source_id)
   family=section.group(1) if section else ''
   hits={}
   for did,card in catalog.items():
    term=card['term']
    if re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',text,re.I):hits[did]='literal term in original case'
   if section:
    target=TARGET.get(family,{}).get(section.group(2).lower())
    if target:hits['sara:'+target]='statute subsection named in original case'
   if a.mode=='section_cues' and family in CUES:
    for name,patterns in CUES[family].items():
     did='sara:'+name
     if did not in hits and any(re.search(r,text,re.I|re.S) for r in patterns):hits[did]='predeclared cue within the referenced statute family'
   if set(hits)-set(catalog):raise ValueError('Candidate not in source catalog')
   # The suffix is a task label, not part of the reader question or matcher.
   base=re.sub(r'_(?:pos|neg)$','',source_id)
   rid=hashlib.sha256((base+'\n'+text).encode()).hexdigest()[:24]
   out.append({'id':'sara:'+rid,'scope':'sara:us_federal_tax_simplified','candidate_names':hits,
               'matched_definition_ids':sorted(hits),
               'matcher_provenance':('SARA source text+named section; '+a.mode+'; no Prolog facts, test answers, or reader outcomes')})
 assert len(out)==256 and len({x['id'] for x in out})==len(out)
 dest=ROOT/('sara_match_'+a.mode+'.jsonl')
 dest.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in out))
 from collections import Counter
 print(a.mode,dict(sorted(Counter(len(x['matched_definition_ids']) for x in out).items())), 'n>=2',sum(len(x['matched_definition_ids'])>=2 for x in out))
if __name__=='__main__':main()
