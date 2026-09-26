#!/usr/bin/env python3
"""Recompute completed experiments offline. No model/API calls."""
from pathlib import Path
import argparse,subprocess,sys,json,shutil,os
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--figures',action='store_true');a=p.parse_args()
 steps=[('main statistics','analysis/recompute.py',[str(ROOT)]),('supplementary statistics','analysis/recompute_extra.py',[str(ROOT)]),('recovered responses','analysis/verify_recovered.py',[str(ROOT),'--out',str(ROOT/'analysis/results/recovered')]),('RAG response linkage','analysis/resolve_rag.py',[])]
 for title,script,args in steps:
  print('Recomputing '+title,flush=True)
  with (ROOT/'analysis/results'/ (Path(script).stem+'.log')).open('w') as log:
   subprocess.run([sys.executable,str(ROOT/script),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 d=json.loads((ROOT/'analysis/results/audit_results.json').read_text());e=json.loads((ROOT/'analysis/expected_main.json').read_text());checks=[]
 for actual,expected in zip(d['settings'],e['settings']):
  for field in ['n','risk_auc','pd_auc','failure','definition_accuracy']:
   if abs(actual[field]-expected[field])>1e-10:raise RuntimeError('Reference mismatch: '+actual['setting']+' '+field)
  checks.append(actual['setting'])
 r=json.loads((ROOT/'analysis/results/recovered/verification.json').read_text())
 if any(x['issues'] for x in r['recovered_readers']):raise RuntimeError('Recovered label mismatch')
 if r['rag_hybrid']['mismatches']:raise RuntimeError('Corrected RAG recovery does not match original result labels')
 result={'status':'passed','main_settings_verified':checks,'raw_sample_letters':r['uncertainty']['raw_sample_letters'],'identical_wrong_among_greedy_errors':r['uncertainty']['full']['identical_wrong_among_errors'],'cuad_definition_anchored':r['prediction_metrics'][-1],'independent_question_experiments':'development data only, not part of the paper claims','api_calls':0}
 (ROOT/'analysis/results/reproduction_status.json').write_text(json.dumps(result,indent=2)+'\n')
 if a.figures:
  target=ROOT/'analysis/results/paper_assets';target.mkdir(exist_ok=True);(target/'figs').mkdir(exist_ok=True)
  for name in ['rebuild_tables_figures.py','data_summary.json']:shutil.copy2(ROOT/'paper'/name,target/name)
  env=dict(os.environ);env['MPLCONFIGDIR']=str(ROOT/'analysis/results/mpl_cache')
  subprocess.run([sys.executable,str(target/'rebuild_tables_figures.py')],env=env,check=True)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
