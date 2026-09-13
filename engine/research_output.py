"""Readable run exports and append-only, flushed checkpoints; no generated factual prose."""
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
import hashlib
import json
import os
import re

def serialize(value):
    if is_dataclass(value): return asdict(value)
    if isinstance(value,Enum): return value.value
    if isinstance(value,set): return sorted(value)
    raise TypeError(type(value).__name__)

def slug(value):
    return re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')[:90] or 'entity'

def dump(path,value):
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,default=serialize)+'\n')
    tmp.replace(path)

class RunWriter:
    def __init__(self,path):
        self.path = Path(path)
        if self.path.exists() and any(self.path.iterdir()):
            raise ValueError('Output directory is not empty; choose a new directory (resume is not yet supported)')
        self.path.mkdir(parents=True,exist_ok=True)
        for folder in ('companies','themes','opportunities'): (self.path/folder).mkdir(exist_ok=True)
        self.seen_sources,self.seen_claims = set(),{}

    def append(self,name,record):
        with (self.path/name).open('a') as stream:
            stream.write(json.dumps(record,default=serialize)+'\n')
            stream.flush()
            os.fsync(stream.fileno())

    def checkpoint(self,rt,event,payload=None):
        for sid,doc in rt.memory.documents.items():
            if sid not in self.seen_sources:
                self.append('sources.jsonl',doc); self.seen_sources.add(sid)
        for cid,claim in rt.memory.claims.items():
            encoded=json.dumps(claim,default=serialize,sort_keys=True)
            if self.seen_claims.get(cid)!=encoded:
                self.append('claims.jsonl',claim); self.seen_claims[cid]=encoded
        self.append('events.jsonl',{'event':event,'payload':payload})
        if event in ('QUERY_COMPLETE','FINAL','INTERRUPTED','ERROR','ENTITY','NODE'):
            dump(self.path/'nodes.json',[asdict(n) for n in rt.graph.all()])
            dump(self.path/'entities.json',[asdict(n) for n in rt.economy.nodes.values()])
        if event=='QUERY_COMPLETE': self.append('trace.jsonl',payload)

    def finish(self,result):
        result=json.loads(json.dumps(result,default=serialize))
        dump(self.path/'result.json',result)
        for name,key in [('sources','source_documents'),('claims','atomic_claims'),('entities','discovered_entities')]:
            dump(self.path/(name+'.json'),result.get(key,[]))
        trace=result.get('full_research_trace',[])
        # Final trace includes entity spawn updates made after the per-query checkpoint.
        (self.path/'trace.jsonl').write_text(''.join(json.dumps(r,default=serialize)+'\n' for r in trace))
        errors=[r for r in trace if r.get('error') or r.get('source_errors') or r.get('claims_rejected') or r.get('status') in ('REJECTED','RESEARCH_BACKEND_ERROR','SOURCE_ACCESS_FAILED','NO_RELEVANT_EVIDENCE')]
        dump(self.path/'errors.json',errors)
        claims=result.get('atomic_claims',[])
        by_id={c['claim_id']:c for c in claims}
        def line(c):
            sources=' '.join(f"[source]({s['url']})" for s in c.get('sources',[]))
            support=', '.join(c.get('supporting_claim_ids',[]))
            return f"- **{c['status']}** {c['statement']} — `{c['claim_id']}` {sources}"+(f" (supports: {support})" if support else '')
        sections = [
            ('Identity',['identity']),('Capital / financial capacity',['financial_capacity']),
            ('Current initiatives',['current_initiative']),('Products',['product_business_model']),
            ('Talent need',['talent_need_status']),('Developer adoption need',['developer_need_status']),
            ('Internal capabilities',['internal_capability']),('Existing programs',['existing_programs','internal_capability']),
            ('Research blind spot',['event_answerable_question','strategic_need']),
            ('Potential Cornell event value',['cohort_fit','external_incremental_value','event_value_chain']),
            ('Natural participant activity',['natural_activity']),('Data / qualitative opportunity',['data_opportunity']),
            ('R&D opportunity',['rd_opportunity']),('Recruiting opportunity',['recruiting_opportunity']),
            ('Buyer',['buyer_function','budget_function']),('Alternatives / substitutes',['substitute']),
            ('Strongest objections',['strongest_objection']),('Counterevidence',['counterevidence']),('WTP',['wtp_status'])]
        company_links=[]
        for node in result.get('company_dossiers',[]):
            v=node.get('value') or {}; name=v.get('canonical_name',node['question'])
            filename=slug(name)+'-'+hashlib.sha256(node['id'].encode()).hexdigest()[:6]+'.md'
            company_links.append(f"- [{name}](companies/{filename}) — {node['status']}")
            own=[c for c in claims if c['subject_id']==node['id']]
            why=[by_id[i] for i in v.get('discovery_claim_ids',[]) if i in by_id]
            body=[f'# {name}', '## Status',node['status'], '## Why discovered',
                  v.get('event_connection','User-supplied research target; relevance remains unvalidated.'),
                  *(line(c) for c in why)]
            for title,fields in sections:
                body+=['## '+title]
                matches=[c for c in own if c['field'] in fields]
                body += [line(c) for c in matches] or ['PRIMARY_VALIDATION_REQUIRED' if title=='WTP' else 'UNKNOWN — no accepted answer yet.']
                for op in result.get('research_opportunities',[]):
                    ov=op.get('value') or {}
                    if ov.get('company_id')==node['id'] and op['node_type'] in fields:
                        body.append('HYPOTHESIS — '+json.dumps(ov.get('opportunity'),default=serialize))
            body+=['## Primary validation required','Confirm buyer, scoped question, cohort fit, consent, artifact utility and willingness to pay.',
                   '## Sources',*(f"- [{d['source']['title']}]({d['source']['url']}) — `{d['source_id']}`" for d in result.get('source_documents',[]) if any(c.get('source_id')==d['source_id'] for c in own)),
                   '## Claim IDs',*(f"- `{c['claim_id']}`" for c in own),'## Research trace',
                   *(f"- {r.get('status')}: {r.get('query')} (negative={r.get('negative_query')}; opened={len(r.get('sources_opened',[]))})" for r in trace if r.get('node')==node['id'] and r.get('query')),
                   '## Missing fields','```json',json.dumps(v.get('gate','UNKNOWN'),indent=2,default=serialize),'```',
                   '## Canonical identity','```json',json.dumps({k:v[k] for k in ('identity_status','official_domain','identity_evidence_claim_ids') if k in v},indent=2),'```']
            (self.path/'companies'/filename).write_text('\n\n'.join(body)+'\n')
        for folder,key in [('themes','candidate_event_concepts'),('opportunities','research_opportunities')]:
            for n in result.get(key,[]):
                filename=slug(n['id'])+'.md'
                (self.path/folder/filename).write_text('# '+n['question']+'\n\nHYPOTHESIS — completion and buyer validation remain separate.\n\n```json\n'+json.dumps(n,indent=2,default=serialize)+'\n```\n')
        stats={'queries executed':sum('query' in r for r in trace),
               'sources opened (unique)':len(result.get('source_documents',[])),
               'source open failures':sum(len(r.get('source_errors',[])) for r in trace),
               'claims accepted':len(claims),'claims rejected':sum(len(r.get('claims_rejected',[])) for r in trace),
               'companies discovered/seeded':len(company_links),
               'companies researched':sum(any(r.get('node')==n['id'] and r.get('query') for r in trace) for n in result.get('company_dossiers',[]))}
        summary=['# Research run','## Run status',result['status'],
            'Termination: '+result.get('termination_reason','UNKNOWN'),
            'Budget stops: '+', '.join(result.get('budget_exhausted',[])),
            'Review independence: '+result.get('independence_level','NOT_RUN'),
            '## Objective',result['objective'],'## Search stats',*(f'- {k}: {v}' for k,v in stats.items()),
            '## Company prospects (unranked)',*(company_links or ['UNKNOWN']),
            '## Why they surfaced','See each dossier’s discovery claim IDs; inclusion is not sponsor qualification.',
            '## What we know',*([line(c) for c in claims if c['status']=='FACT'][:30] or ['UNKNOWN']),
            '## What is inferred',*([line(c) for c in claims if c['status']=='INFERENCE'][:20] or ['UNKNOWN']),
            '## What is still unknown','See dossier missing-field gates and primary-validation.md.',
            '## Research / data opportunities','See opportunities/; all plans are hypotheses, not validated company demand.',
            '## R&D opportunities','Only plans with structural supporting evidence are included.',
            '## Potential event concepts','NO FINAL WINNER YET','```json',json.dumps(result.get('partial_synthesis',{}),indent=2,default=serialize),'```',
            '## Cornell fit',*([line(c) for c in claims if c['subject_id']=='cornell'][:15] or ['UNKNOWN — Cornell-specific capability and cohort evidence needed.']),
            '## Commercial validation required','Buyer interviews and a scoped paid commitment are required; funding is not WTP.',
            '## Critical unknowns','See result.json → critical_unknowns and every dossier → Missing fields.',
            '## Failed / blocked research',f'{len(errors)} trace records need review; see errors.json.',
            '## Next actions','Resolve retrieval/configuration errors; research missing material fields; validate proposed questions with buyers.']
        (self.path/'summary.md').write_text('\n\n'.join(summary)+'\n')
        (self.path/'primary-validation.md').write_text('# Primary validation required\n\nConfirm buyer, need, budget, scoped artifact, participant value, consent, cohort fit and IP before any commercial conclusion.\n\n```json\n'+json.dumps(result.get('primary_validation_required',[]),indent=2,default=serialize)+'\n```\n')
