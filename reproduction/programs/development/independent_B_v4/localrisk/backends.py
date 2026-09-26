from .responses import response_text,ResponseFailure
"""Optional live adapters. Imported libraries and credentials are loaded on demand."""
from pathlib import Path
import json,os,time,urllib.request,urllib.error,urllib.parse,math
from .common import *
from .experiment import load_plan
from .validation import validate_probes


def label_sequences(tokenizer,n):
    seqs=[tokenizer.encode(' '+chr(65+i),add_special_tokens=False) for i in range(n)]
    require(all(seqs) and len({tuple(s) for s in seqs})==n,'Answer labels do not tokenize to distinct sequences')
    return seqs

def score_probes(corpus_path,probes_path,model,revision,out,device='cpu'):
    started_at=now();started=time.monotonic()
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    c=read_json(corpus_path);p=validate_probes(c,read_rows(probes_path));docs,defs,ps=validate_corpus(c)
    require(revision and not revision.startswith('REPLACE'),'Explicit proxy revision required')
    tok=AutoTokenizer.from_pretrained(model,revision=revision,trust_remote_code=False)
    dtype=torch.float32 if device=='cpu' else torch.float16
    net=AutoModelForCausalLM.from_pretrained(model,revision=revision,torch_dtype=dtype,trust_remote_code=False).to(device).eval()
    resolved=getattr(net.config,'_commit_hash',None)
    load_seconds=time.monotonic()-started;scoring_started=time.monotonic()
    rows=[]
    for q in p:
        probs=[];hashes=[];seqs=label_sequences(tok,len(q['options']))
        for definitions in [[],[defs[q['definition_id']]]]:
            prompt=public_prompt(q,[ps[q['passage_id']]],definitions);prefix=tok.encode(prompt,add_special_tokens=True);require(prefix,'Empty prompt tokens')
            scores=[]
            with torch.no_grad():
                # Full sequence likelihood: never assume the first token of " A" is A.
                for seq in seqs:
                    ids=prefix+seq;limit=getattr(net.config,'max_position_embeddings',None)
                    require(not limit or len(ids)<=limit,'Proxy context exceeds model limit; no silent truncation')
                    x=torch.tensor([ids],device=device);logits=net(input_ids=x).logits[0].float()
                    lp=torch.log_softmax(logits[len(prefix)-1:len(ids)-1],dim=-1)
                    scores.append(sum(lp[j,token].item() for j,token in enumerate(seq)))
            z=max(scores);v=[math.exp(x-z) for x in scores];probs.append([x/sum(v) for x in v]);hashes.append(digest({'prompt_ids':prefix,'label_sequences':seqs}))
        j=choice(q['answer'],len(q['options']));pb=probs[0][j];pd=probs[1][j]
        rows.append({'probe_id':q['probe_id'],'corpus_digest':digest(c),'probe_digest':digest(q),'backend':'hf_sequence_likelihood','proxy_model':model,'proxy_revision':revision,'resolved_model_commit':resolved,'p_bare':pb,'p_definition':pd,'risk':1-pb,'pd':pd-pb,'probabilities_bare':probs[0],'probabilities_definition':probs[1],'prompt_hashes':hashes,'label_token_ids':seqs,'forward_passes':2*len(seqs),'created_at':now()})
    write_rows(out,rows)
    metadata={'scored':len(rows),'model':model,'revision':revision,'resolved_model_commit':resolved,'device':device,'dtype':str(dtype),'torch_version':torch.__version__,'started_at':started_at,'finished_at':now(),'load_seconds_including_import_and_download':load_seconds,'scoring_seconds':time.monotonic()-scoring_started,'total_seconds':time.monotonic()-started,'forward_passes':sum(r['forward_passes'] for r in rows)}
    write_json(Path(out).with_suffix('.metadata.json'),metadata)
    return metadata


def run_http(plan_path,out):
    pm,requests,trials=load_plan(plan_path);require(pm['mode']=='real','Use smoke command for smoke plans')
    cfg=pm['reader'];base=cfg.get('base_url','').rstrip('/');parsed=urllib.parse.urlparse(base)
    local_http = parsed.scheme=='http' and parsed.hostname in ['localhost','127.0.0.1','::1']
    require(parsed.scheme=='https' or local_http or cfg.get('allow_remote_http') is True,
            'Use HTTPS or a local inference endpoint. This plan was not created with --allow-http.')
    env=cfg.get('api_key_env','LOCALRISK_READER_API_KEY');key=os.environ.get(env)
    require(key or cfg.get('allow_unauthenticated_local') and parsed.hostname in ['localhost','127.0.0.1','::1'],'Set the named API key environment variable locally')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);done={}
    if out.exists():
        for row in read_rows(out):
            require(row.get('plan_id')==pm['plan_id'],'Output contains a different experiment plan')
            if row.get('status')=='ok':done[row['request_id']]=row
    # Interleave policies through deterministic request shuffle; deduplicated requests are shared observations.
    import random
    queue=requests[:];random.Random(cfg.get('request_order_seed',0)).shuffle(queue)
    out.touch(exist_ok=True)
    failures=0
    for r in queue:
        if r['request_id'] in done:continue
        headers={'Content-Type':'application/json'}
        if key:headers['Authorization']='Bearer '+key
        data=canonical(r['payload']).encode();req=urllib.request.Request(base+'/chat/completions',data=data,headers=headers,method='POST')
        result={'plan_id':pm['plan_id'],'request_id':r['request_id'],'requested_model':cfg['model'],'endpoint':base,'started_at':now(),'mode':'real'}
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req,timeout=cfg.get('timeout_seconds',45)) as resp:obj=json.loads(resp.read())
                content=response_text(obj)
                result.update(status='ok',content=content,prediction=parse_answer(content,r['n_options']),returned_model=obj.get('model'),provider_response_id=obj.get('id'),usage=obj.get('usage'),finish_reason=obj['choices'][0].get('finish_reason'),system_fingerprint=obj.get('system_fingerprint'),finished_at=now(),attempts=attempt+1)
                break
            except ResponseFailure as e:
                result.update(status='error',error_type=e.kind,response_diagnostic=e.metadata,finished_at=now());break
            except urllib.error.HTTPError as e:
                if e.code in [429,500,502,503,504] and attempt<2:time.sleep(2**attempt);continue
                result.update(status='error',error_type='http',http_status=e.code,finished_at=now());break
            except (TimeoutError,urllib.error.URLError) as e:
                if attempt<2:time.sleep(2**attempt);continue
                result.update(status='error',error_type=type(e).__name__,finished_at=now());break
            except (ValueError,KeyError,IndexError,InvalidExperiment) as e:
                result.update(status='error',error_type=type(e).__name__,finished_at=now());break
        failures+=result['status']!='ok'
        with out.open('a',encoding='utf-8') as f:f.write(canonical(result)+'\n');f.flush()
    return {'planned_unique_requests':len(requests),'previously_completed':len(done),'new_errors':failures,'note':'HTTP errors are not scored as wrong answers; analysis requires complete outcomes.'}
