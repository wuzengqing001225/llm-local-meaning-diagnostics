"""Budgeted policies. No answer keys or evaluation outcomes are accepted here."""
import math,random,re
from collections import defaultdict,Counter
from .common import *

POLICIES={'none','matched','random','idf','term_mean','term_max','occurrence_risk','pd','repairability','all_matched','full_glossary'}

def index_scores(c,probes,scores):
    by=unique(scores,'probe_id');occ={};term=defaultdict(list)
    for p in probes:
        if p.get('review',{}).get('status')!='accepted':continue
        s=by[p['probe_id']];occ[(p['passage_id'],p['definition_id'])]=s;term[p['definition_id']].append(s['risk'])
    return occ,term

def candidates(c,task):
    docs,defs,ps=validate_corpus(c)
    require(set(task)=={'task_id','doc_id','context_ids','question','options'},'Policy input must be the allowlisted public task, with no gold/target annotations')
    require(task['doc_id'] in docs,'Unknown task doc')
    require(task['context_ids'] and len(task['context_ids'])==len(set(task['context_ids'])),'Invalid context list')
    require(all(pid in ps and ps[pid]['doc_id']==task['doc_id'] for pid in task['context_ids']),'Invalid context scope')
    # All definitions for terms in fixed passages. No focal-definition id from test authors.
    ids=sorted({i for pid in task['context_ids'] for i in ps[pid]['definition_ids']})
    return [defs[i] for i in ids]

def corpus_idf(c):
    docs,defs,ps=validate_corpus(c);df=defaultdict(set)
    terms={d['term'].casefold() for d in defs.values()}
    for p in ps.values():
        for term in terms:
            if contains(term,p['text']):df[term].add(p['doc_id'])
    # Corpus is the explicitly supplied pilot document frame, not global Zipf frequency.
    return {d['definition_id']:math.log((1+len(docs))/(1+len(df[d['term'].casefold()]))) for d in defs.values()}

def candidate_value(policy,c,task,d,occ,term,idfs):
    did=d['definition_id']
    if policy=='idf':return idfs[did]
    if policy=='matched':
        return 1000*int(contains(d['term'],task['question']))+sum(len(re.findall(r'(?<!\w)'+re.escape(d['term'])+r'(?!\w)',p['text'],re.I)) for p in c['passages'] if p['passage_id'] in task['context_ids'])
    if policy in ['term_mean','term_max']:
        require(did in term and term[did],'Missing term score: '+did)
        return sum(term[did])/len(term[did]) if policy=='term_mean' else max(term[did])
    wanted=[pid for pid in task['context_ids'] if did in next(p for p in c['passages'] if p['passage_id']==pid)['definition_ids']]
    require(all((pid,did) in occ for pid in wanted),'Missing occurrence probe score: '+did)
    field={'occurrence_risk':'risk','pd':'pd','repairability':'p_definition'}[policy]
    return max(occ[(pid,did)][field] for pid in wanted)

def ranked(policy,c,task,ds,occ,term,idfs,seed):
    require(policy in POLICIES,'Unknown policy')
    if policy=='random':
        out=sorted(ds,key=lambda d:d['definition_id']);random.Random(str(seed)+':'+task['task_id']).shuffle(out);return out
    if policy in ['all_matched','full_glossary']:return sorted(ds,key=lambda d:d['definition_id'])
    return sorted(ds,key=lambda d:(-candidate_value(policy,c,task,d,occ,term,idfs),d['definition_id']))

def select_workload(policy,c,tasks,occ,term,idfs,average_budget,counter,seed=0):
    """A fixed finite workload shares N * average_budget definition tokens.
    Greedy raw-score order with exact marginal serialized-block cost; not an optimal knapsack solver.
    The workload/questions are visible; their answers and outcomes are never available here.
    """
    require(policy not in ['none','all_matched','full_glossary'],'Use unbounded baselines separately')
    require(type(average_budget)==int and average_budget>=0,'Invalid workload budget')
    available={t['task_id']:candidates(c,t) for t in tasks};bytask={t['task_id']:t for t in tasks}
    pairs=[(t['task_id'],d) for t in tasks for d in available[t['task_id']]]
    pairs.sort(key=lambda pair:(pair[0],pair[1]['definition_id']))
    if policy=='random':random.Random(seed).shuffle(pairs)
    else:pairs.sort(key=lambda pair:(-candidate_value(policy,c,bytask[pair[0]],pair[1],occ,term,idfs),digest([pair[0],pair[1]['definition_id']])))
    chosen={t['task_id']:[] for t in tasks};costs={t['task_id']:0 for t in tasks};total=0;cap=len(tasks)*average_budget
    for tid,d in pairs:
        proposal=chosen[tid]+[d];cost=counter.count(definition_block(proposal));delta=cost-costs[tid]
        if total+delta<=cap:
            chosen[tid]=proposal;costs[tid]=cost;total+=delta
    require(sum(costs.values())<=cap,'Workload budget overflow')
    return {tid:(chosen[tid],costs[tid],available[tid]) for tid in chosen}

def select(policy,c,task,occ,term,idfs,budget,counter,seed=0):
    require(isinstance(budget,int) and budget>=0,'Budget must be a nonnegative integer')
    ds=candidates(c,task)
    if policy=='none':return [],0,ds
    if policy=='full_glossary':ds=[d for d in c['definitions'] if d['doc_id']==task['doc_id']]
    order=ranked(policy,c,task,ds,occ,term,idfs,seed)
    if policy in ['all_matched','full_glossary']:
        return order,counter.count(definition_block(order)),ds
    picked=[]
    for d in order:
        proposal=picked+[d]
        # Exact count of the full serialized block, including scope/header/separators.
        if counter.count(definition_block(proposal))<=budget:picked=proposal
    cost=counter.count(definition_block(picked));require(cost<=budget,'Budget overflow')
    return picked,cost,ds
