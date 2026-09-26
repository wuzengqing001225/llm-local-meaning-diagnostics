#!/usr/bin/env python3
"""Resumable development run. Defaults reuse the user's separate-endpoint V4 config."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=ROOT.parent/'local_meaning_v4_config/config.json')
 p.add_argument('--cuad',type=Path,default=None);p.add_argument('--from-stage',choices=['A','score','B','budget','readers','analysis'],default='A');a=p.parse_args()
 stages=[('A','make_A.py',['--config',str(a.config.resolve())]),('score','score_A.py',[]),('B','make_B.py',['--config',str(a.config.resolve())]),('budget','plan_budget.py',(['--cuad',str(a.cuad.resolve())] if a.cuad else [])),('budget','make_review_packet.py',[]),('readers','reader.py',['--config',str(a.config.resolve())]),('analysis','analyze.py',[]),('analysis','verify.py',[])]
 order=['A','score','B','budget','readers','analysis'];start=order.index(a.from_stage)
 for stage,script,args in stages:
  if order.index(stage)<start:continue
  print('[V7]',stage,script,flush=True)
  subprocess.run([sys.executable,str(ROOT/script),*args],check=True,cwd=ROOT)
 print('V7 completed. Results remain provisional until human source review.',flush=True)
if __name__=='__main__':main()
