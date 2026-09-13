"""Dimension disclosure and deterministic Pareto comparison; no default winning weights."""
from math import isfinite
from research_contracts import EpistemicStatus, DIMENSIONS
BENEFITS=('student_value','technical_quality','company_value','research_value','rd_value',
          'recruiting_value','repeatability','founder_economics')
COSTS=('participant_burden','privacy_risk','research_contamination','operational_complexity','conflict')

def compare(candidates, memory, weights=None):
    disclosed, vectors = {}, {}
    for nid in candidates:
        cs=memory.for_subject(nid)
        disclosed[nid]={d:[{'claim_id':c.claim_id,'value':c.value,'status':c.status.value,
                           'statement':c.statement} for c in cs if c.field==d] or 'UNKNOWN' for d in DIMENSIONS}
        vector={}
        for d in DIMENSIONS:
            matches=[c for c in cs if c.field==d and c.status in (EpistemicStatus.FACT,EpistemicStatus.INFERENCE)
                     and isinstance(c.value,dict) and c.value.get('scale')=='normalized_0_1'
                     and type(c.value.get('score')) in (int,float)
                     and isfinite(c.value['score']) and 0<=c.value['score']<=1]
            if len(matches)==1:
                vector[d]=matches[0].value['score'] * (-1 if d in COSTS else 1)
        if len(vector)==len(DIMENSIONS):vectors[nid]=vector
    if len(vectors)!=len(candidates):
        return {'dimensions':disclosed,'pareto_frontier':'UNKNOWN','ranking':'UNKNOWN',
                'missing':'Comparable evidence-backed dimension scales required; no implicit weights'}
    frontier=[a for a in vectors if not any(all(vectors[b][d]>=vectors[a][d] for d in DIMENSIONS)
        and any(vectors[b][d]>vectors[a][d] for d in DIMENSIONS) for b in vectors if b!=a)]
    ranking='UNWEIGHTED_PARETO_ONLY'
    if weights:
        if set(weights)!=set(DIMENSIONS) or any(type(w) not in (int,float) or not isfinite(w) or w<0 for w in weights.values()) or not any(weights.values()):
            raise ValueError('Weights must explicitly cover every dimension, be finite, nonnegative, and not all zero')
        ranking=sorted(({'candidate':n,'score':sum(weights[d]*v[d] for d in DIMENSIONS)}
                        for n,v in vectors.items()),key=lambda x:-x['score'])
    return {'dimensions':disclosed,'pareto_frontier':frontier,'ranking':ranking}
