import argparse,json
from .common import *

def main():
    p=argparse.ArgumentParser(description='Independent local-meaning experiment; source preparation does not call models.')
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('prepare');a.add_argument('--cuad',required=True);a.add_argument('--reddit');a.add_argument('--out',required=True);a.add_argument('--groups',type=int,default=12);a.add_argument('--passages',type=int,default=3);a.add_argument('--seed',type=int,default=20260922)
    a=sub.add_parser('validate');a.add_argument('--corpus',required=True);a.add_argument('--probes',required=True);a.add_argument('--tasks')
    a=sub.add_parser('score-probes');a.add_argument('--corpus',required=True);a.add_argument('--probes',required=True);a.add_argument('--model',required=True);a.add_argument('--revision',required=True);a.add_argument('--device',default='cpu');a.add_argument('--out',required=True)
    a=sub.add_parser('freeze');a.add_argument('--corpus',required=True);a.add_argument('--probes',required=True);a.add_argument('--scores',required=True);a.add_argument('--config',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('accept-tasks');a.add_argument('--snapshot',required=True);a.add_argument('--tasks',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('plan');a.add_argument('--snapshot',required=True);a.add_argument('--tasks',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('run-http');a.add_argument('--plan',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('analyze');a.add_argument('--snapshot',required=True);a.add_argument('--tasks',required=True);a.add_argument('--plan',required=True);a.add_argument('--predictions',required=True);a.add_argument('--out',required=True)
    a=sub.add_parser('smoke');a.add_argument('--out',required=True)
    args=p.parse_args()
    try:
        if args.cmd=='prepare':
            from .prepare import prepare,author_packets
            require(args.groups>0 and args.passages>0,'Positive sampling counts required')
            require(not Path(args.out).exists(),'Preparation output already exists')
            c=prepare(args.cuad,args.reddit,args.seed,args.groups,args.passages);write_json(Path(args.out)/'corpus.json',c);result=author_packets(c,Path(args.out)/'authoring')
        elif args.cmd=='validate':
            from .validation import validate_probes,validate_tasks
            c=read_json(args.corpus);probes=read_rows(args.probes);v=validate_probes(c,probes);result={'accepted_probes':len(v)}
            if args.tasks:result['accepted_tasks']=len(validate_tasks(c,probes,read_rows(args.tasks)))
        elif args.cmd=='score-probes':
            from .backends import score_probes
            result=score_probes(args.corpus,args.probes,args.model,args.revision,args.out,args.device)
        elif args.cmd=='freeze':
            from .experiment import freeze
            result=freeze(args.corpus,args.probes,args.scores,args.config,args.out)
        elif args.cmd=='accept-tasks':
            from .experiment import accept_tasks
            result=accept_tasks(args.snapshot,args.tasks,args.out)
        elif args.cmd=='plan':
            from .experiment import plan
            result=plan(args.snapshot,args.tasks,args.out)
        elif args.cmd=='run-http':
            from .backends import run_http
            result=run_http(args.plan,args.out)
        elif args.cmd=='analyze':
            from .analysis import analyze
            r=analyze(args.snapshot,args.tasks,args.plan,args.predictions,args.out);result={'mode':r['mode'],'primary_contrast':r['primary_contrast']}
        elif args.cmd=='smoke':
            from .smoke import smoke
            result=smoke(args.out)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (InvalidExperiment,FileNotFoundError) as e:p.exit(2,f'Experiment not ready: {e}\n')

if __name__=='__main__':main()
