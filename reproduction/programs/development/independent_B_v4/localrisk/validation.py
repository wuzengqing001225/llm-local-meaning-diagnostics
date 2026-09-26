import math
from .common import *

def accepted(rows,idfield):
    unique(rows,idfield);out=[]
    for r in rows:
        status=r.get('review',{}).get('status')
        if status=='rejected':
            require(bool(r.get('review',{}).get('reason','').strip()),f'{r[idfield]} rejected without a reason')
            continue
        require(status=='accepted',f'{r[idfield]} still pending review')
        require(r.get('source_type') in ['human','model_assisted','model_generated','expert_benchmark','smoke_fixture'],f'{r[idfield]} missing author provenance')
        require(bool(r.get('author_id','').strip()),f'{r[idfield]} missing author id')
        require(isinstance(r.get('question'),str) and len(r['question'].strip())>8,'Question missing')
        opts=r.get('options');require(isinstance(opts,list) and 2<=len(opts)<=4 and all(isinstance(x,str) and x.strip() for x in opts),'Need 2–4 nonempty options')
        require(len(set(norm(x) for x in opts))==len(opts),'Duplicate options')
        choice(r.get('answer'),len(opts));rv=r['review']
        if rv.get('mode')=='automated_screen' and 'structure_valid' in rv:
            require(rv['structure_valid'] is True,'Draft structure invalid')
        else:
            require(rv.get('key_valid') is True and rv.get('source_sufficient') is True,'Key/source review incomplete')
        require(rv.get('mode','human') in ['human','automated_screen'],'Unknown review mode')
        if rv.get('mode')=='automated_screen':
            require(r['source_type']=='model_generated' and rv.get('human_review_completed') is False,'Automated screening must not claim human review')
        reviewers=rv.get('reviewer_ids',[])
        require(isinstance(reviewers,list) and len(set(reviewers))>=1 and all(isinstance(x,str) and x.strip() for x in reviewers),'Reviewer identities required')
        require(r['author_id'] not in reviewers,'Author cannot be their own independent reviewer')
        out.append(r)
    require(out,'No accepted items');return out

def validate_probes(c,rows,allow_fixture=False):
    docs,defs,ps=validate_corpus(c);rr=accepted(rows,'probe_id');pairs=set()
    for r in rr:
        require(allow_fixture or r['source_type']!='smoke_fixture','Smoke probes forbidden in real experiments')
        require(r.get('passage_id') in ps and r.get('definition_id') in defs,'Unknown probe source')
        p=ps[r['passage_id']];d=defs[r['definition_id']]
        require(r['doc_id']==p['doc_id']==d['doc_id'],'Probe crosses documents')
        require(d['definition_id'] in p['definition_ids'],'Probe term not a source candidate')
        pair=(r['passage_id'],r['definition_id']);require(pair not in pairs,'Use one prereviewed probe per occurrence in v1');pairs.add(pair)
    return rr

def validate_scores(c,probes,scores,allow_fixture=False):
    rr=validate_probes(c,probes,allow_fixture);by=unique(scores,'probe_id')
    require(set(by)=={r['probe_id'] for r in rr},'Score coverage differs from accepted probes')
    ch=digest(c)
    for p in rr:
        s=by[p['probe_id']]
        require(s.get('corpus_digest')==ch and s.get('probe_digest')==digest(p),'Score provenance mismatch')
        for k in ['p_bare','p_definition']:
            require(isinstance(s.get(k),(int,float)) and math.isfinite(s[k]) and 0<=s[k]<=1,'Invalid probability')
        require(abs(s.get('risk',-1)-(1-s['p_bare']))<1e-8,'Risk formula mismatch')
        require(abs(s.get('pd',-99)-(s['p_definition']-s['p_bare']))<1e-8,'PD formula mismatch')
        require(s.get('proxy_model') and s.get('proxy_revision'),'Proxy model/revision required')
        require(allow_fixture or s.get('backend')!='smoke_fixture','Smoke scores forbidden')
    return rr

def validate_tasks(c,probes,tasks,allow_fixture=False):
    docs,defs,ps=validate_corpus(c);rr=accepted(tasks,'task_id');ar=validate_probes(c,probes,allow_fixture)
    for t in rr:
        require(allow_fixture or t['source_type']!='smoke_fixture','Smoke tasks forbidden')
        require(t['doc_id'] in docs,'Task document missing')
        ids=t.get('context_ids');require(isinstance(ids,list) and ids and len(ids)==len(set(ids)),'Invalid task context')
        require(all(i in ps and ps[i]['doc_id']==t['doc_id'] for i in ids),'Task context crosses documents')
        require(t.get('definition_dependence') in ['required','not_required','uncertain'],'Missing independent semantic annotation')
        require(t['review'].get('independent_of_probes') is True,'Independent-task review incomplete')
        if t['review'].get('mode')!='automated_screen':
            require(len(set(t['review']['reviewer_ids']))>=2,'Independent tasks require two reviewers')
        relevant=[a for a in ar if a['passage_id'] in ids]
        for a in relevant:
            require(norm(t['question'])!=norm(a['question']),'Test question is the diagnostic question')
            require(t['author_id']!=a['author_id'],'A and B require independent authors/generator runs')
        quotes=t.get('evidence_quotes',[]);source='\n'.join(ps[i]['text'] for i in ids)+'\n'+'\n'.join(d['text'] for d in defs.values() if d['doc_id']==t['doc_id'])
        # Source quotations are provenance records. Match after whitespace/punctuation normalization so
        # harmless formatting changes by a drafter do not reject an otherwise inspectable item.
        normalized_source=norm(source)
        require(quotes and all(isinstance(q,str) and q.strip() and norm(q) in normalized_source for q in quotes),'Evidence quotes must occur in supplied source')
    return rr

def split_tasks(c,probes,tasks,allow_fixture=False):
    rr=validate_tasks(c,probes,tasks,allow_fixture);pub=[];gold=[]
    for t in rr:
        p={k:t[k] for k in ['task_id','doc_id','context_ids','question','options']}
        pub.append(p);gold.append({'task_id':t['task_id'],'answer':t['answer'],'public_digest':digest(p),'definition_dependence':t['definition_dependence'],'source_type':t['source_type'],'review':t['review'],'author_id':t['author_id'],'evidence_quotes':t['evidence_quotes']})
    return pub,gold
