"""Evidence-first CLI. An absent adapter yields UNKNOWN, never a prewritten recommendation."""
from __future__ import annotations
import argparse
from dataclasses import asdict, is_dataclass
from enum import Enum
import importlib
import json
from pathlib import Path
import sys
# The historical engines use flat imports. One entrypoint shim preserves their class identity.
if __package__:
    sys.path.insert(0,str(Path(__file__).resolve().parent))
from governor import Governor, build_research_graph
from research_config import ResearchConfig
from research_runtime import ResearchRuntime

def serialize(value):
    if is_dataclass(value):return asdict(value)
    if isinstance(value,Enum):return value.value
    raise TypeError(f'unsupported research output: {type(value).__name__}')

def load_adapter(spec, methods=('search','open_source','extract_claims')):
    if not spec:return None
    module, name = spec.split(':',1)
    adapter = getattr(importlib.import_module(module),name)()
    for method in methods:
        if not callable(getattr(adapter,method,None)):raise ValueError(f'adapter missing {method}')
    return adapter

def run(objective, executor=None, config=None, red_team_executor=None, company=None, **adapters):
    ctx = dict(objective=objective,research_executor=executor,
               research_config=config or ResearchConfig(),red_team_executor=red_team_executor,**adapters)
    graph = build_research_graph(objective)
    if company:
        from agent_os import Node, NodeStatus
        graph.get('discovery').retryable = False
        graph.get('discovery').status = NodeStatus.PARTIAL
        graph.add(Node('company:starter',f'Research company: {company}',resolver='dynamic_company_research',
            node_type='company',completion_gate='company',voi=4.5,auto_rollup=False,
            value={'canonical_name':company,'identity_status':'UNVERIFIED','event_connection':'User-supplied target'}))
    if ctx.get('live_mode'):
        # Reserve queries for the adversarial pass. Nodes remain open when allocations are consumed.
        cfg=ctx['research_config']
        reserve=max(1,min(12,cfg.max_queries//10)) if cfg.max_queries>1 else 0
        ctx['active_query_limit']=cfg.max_queries-reserve
        ctx['company_query_budget']=max(3,(cfg.max_queries-reserve-12-30)//(1 if company else cfg.max_companies))
        if company: ctx['company_query_budget']=max(1,cfg.max_queries-reserve)
        # Partial proposals are generated after independent company research, not on discovery completion.
        for name in ('themes','final_synthesis','red_team'): graph.get(name).retryable=False
        if company:
            for name in ('cornell','cost','attendance','capacity','pricing'): graph.get(name).retryable=False
    governor = Governor(graph,ctx)
    rt = ResearchRuntime(graph,ctx)
    if company:
        from research_executor import DiscoveredEntity
        for key in rt.identity_keys(DiscoveredEntity('company',company)): rt.aliases[key]='company:starter'
        rt.economy.add_node('company',company,node_id='company:starter')
    rt.checkpoint('NODE', {'status':'STARTED'})
    interrupted=False
    try:
        report = governor.run()
        if ctx.get('live_mode'):
            from agent_os import NodeStatus
            from research_executor import ResearchQuestion
            # Second retrieval/extraction context sees accepted evidence, never synthesis prose.
            ctx['active_query_limit']=ctx['research_config'].max_queries
            reviewer=red_team_executor
            if reviewer:
                red=graph.get('red_team')
                questions=[]
                for n in graph.all():
                    if n.node_type!='company': continue
                    name=(n.value or {}).get('canonical_name',n.question)
                    questions.append(ResearchQuestion('adversarial:'+n.id,
                        name+' product limitations competitors failed adoption internal alternatives hiring freeze',
                        ('counterevidence',),True,agent='red_team'))
                if not questions:
                    questions=[ResearchQuestion('adversarial:objective',objective+' limitations counterevidence alternatives',('counterevidence',),True,agent='red_team')]
                rt.execute(red,questions,reviewer)
                red.status=NodeStatus.PARTIAL
                red.value={'independence_level':ctx.get('independence_level'),
                           'claims':rt.memory.for_subject(red.id),'gate':asdict(rt.gate(red))}
                for c in rt.memory.for_subject(red.id):
                    for cid in c.contradictory_claim_ids:
                        owner=rt.memory.claims[cid].subject_id
                        if owner in graph.nodes: graph.get(owner).status=NodeStatus.CONTRADICTED
            generator=ctx.get('theme_generator')
            if generator:
                from research_executor import DiscoveredEntity
                try:
                    for t in generator.generate(evidence=list(rt.memory.claims.values()),objective=objective):
                        rt.spawn(graph.get('themes'),[DiscoveredEntity('theme',t['name'],
                            evidence_claim_ids=tuple(t['evidence_claim_ids']),relevance=t['event_connection'])])
                except Exception as exc:
                    rt.trace.append({'agent':'theme_generator','status':'REJECTED','error':str(exc)})
            synthesizer=ctx.get('synthesizer')
            if hasattr(synthesizer,'partial'): ctx['partial_synthesis']=synthesizer.partial(rt)
            report=governor.report()
    except KeyboardInterrupt:
        interrupted=True
        rt.checkpoint('INTERRUPTED')
        report=governor.report()
    finally:
        rt.checkpoint('FINAL')
    final = graph.get('final_synthesis')
    primary = [asdict(c) for c in rt.memory.claims.values() if c.status.value in ('UNKNOWN','PRIMARY_VALIDATION_REQUIRED')]
    for n in graph.all():
        if n.node_type=='company' and not any(c.field=='wtp_status' for c in rt.memory.for_subject(n.id)):
            primary.append({'subject_id':n.id,'field':'wtp_status','status':'PRIMARY_VALIDATION_REQUIRED',
                            'next':'Ask the actual buyer about a scoped paid pilot; do not infer from funding'})
    return {'status': 'INTERRUPTED' if interrupted else 'RESEARCH_BACKEND_REQUIRED' if executor is None else
                'RESOLVED' if final.status.value=='RESOLVED' else 'PARTIAL',
        'objective':objective,'termination_reason':'BUDGET_EXHAUSTED' if ctx.get('budget_exhausted') else 'INTERRUPTED' if interrupted else 'RESEARCH_STOPPED',
        'budget_exhausted':sorted(ctx.get('budget_exhausted',[])),
        'independence_level':ctx.get('independence_level','NOT_CONFIGURED'),
        'partial_synthesis':ctx.get('partial_synthesis',{}),
        'final_recommendation':final.value or 'UNKNOWN',
        'confidence':'UNKNOWN' if final.value is None else final.value.get('confidence','UNKNOWN'),
        'discovered_entities':[asdict(n) for n in rt.economy.nodes.values()],
        'source_documents':[asdict(d) for d in rt.memory.documents.values()],
        'atomic_claims':[asdict(c) for c in rt.memory.claims.values()],
        'finding_provenance':{i:f.trace() for i,f in rt.memory.findings.items()},
        'industries':[asdict(n) for n in graph.all() if n.node_type=='industry'],
        'economic_problems':[asdict(n) for n in graph.all() if n.node_type=='problem'],
        'candidate_event_concepts':[asdict(n) for n in graph.all() if n.node_type in ('theme','event_concept')],
        'company_dossiers':[asdict(n) for n in graph.all() if n.node_type=='company'],
        'research_opportunities':[asdict(n) for n in graph.all() if n.node_type in ('rd_opportunity','data_opportunity','recruiting_opportunity')],
        'cornell_capability_intersections':graph.get('cornell').value or 'UNKNOWN',
        'pricing_comparables':graph.get('pricing').value or 'UNKNOWN',
        'cost':graph.get('cost').value or 'UNKNOWN',
        'attendance':graph.get('attendance').value or 'UNKNOWN',
        'capacity':graph.get('capacity').value or 'UNKNOWN',
        'economic_edges':[asdict(e) for e in rt.economy.edges.values()],
        'nodes':[asdict(n) for n in graph.all()], 'primary_validation_required':primary,
        'critical_unknowns':[{'node':n.id,'status':n.status.value,'gate':n.value.get('gate') if isinstance(n.value,dict) else None}
                              for n in graph.all() if n.status.value!='RESOLVED'],
        'full_research_trace':rt.trace,'governor':report}

def main(argv=None):
    from dataclasses import replace
    from research_output import RunWriter
    parser=argparse.ArgumentParser(description='Evidence-first company and event research; --live opts into network access.')
    target=parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--objective')
    target.add_argument('--company',help='Start one company node, skipping economy discovery')
    parser.add_argument('--live',action='store_true',help='Automatically configure live search, scraping, semantic interpretation and partial reports')
    parser.add_argument('--executor',help='Advanced trusted module:factory implementing ResearchExecutor')
    parser.add_argument('--red-team-executor',help='Advanced reviewer module:factory')
    parser.add_argument('--synthesizer',help='Advanced evidence-only synthesis module:factory')
    parser.add_argument('--theme-generator',help='Advanced hypothesis generator module:factory')
    parser.add_argument('--opportunity-mapper',help='Advanced structured plan module:factory')
    parser.add_argument('--config',type=Path,help='JSON ResearchConfig overrides')
    parser.add_argument('--output',type=Path,default=Path('runs')/('research-'+__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')),help='New run directory')
    parser.add_argument('--max-companies',type=int)
    parser.add_argument('--max-rounds',type=int)
    parser.add_argument('--max-queries',type=int)
    parser.add_argument('--max-sources-per-query',type=int)
    args=parser.parse_args(argv)
    try:
        cfg=ResearchConfig(**json.loads(args.config.read_text())) if args.config else ResearchConfig()
        overrides={k:getattr(args,k) for k in ('max_companies','max_rounds','max_queries') if getattr(args,k) is not None}
        if args.max_sources_per_query is not None: overrides['max_results_per_query']=args.max_sources_per_query
        cfg=replace(cfg,**overrides)
        executor=load_adapter(args.executor)
        reviewer=load_adapter(args.red_team_executor)
        adapters=dict(synthesizer=load_adapter(args.synthesizer,('synthesize',)),
            theme_generator=load_adapter(args.theme_generator,('generate',)),
            opportunity_mapper=load_adapter(args.opportunity_mapper,('map_opportunities',)))
        if args.live:
            from web_research import ScrapingResearchExecutor, default_search_provider
            from semantic_extractor import OpenAICompatibleProvider, SemanticGroundedExtractor
            from live_defaults import DefaultOpportunityMapper, DefaultThemeGenerator, DefaultSynthesis
            provider,missing=OpenAICompatibleProvider.from_env()
            search=default_search_provider()
            executor=executor or ScrapingResearchExecutor(search_provider=search,
                extractor=SemanticGroundedExtractor(provider) if provider else None,
                max_results_per_query=cfg.max_results_per_query)
            print('Live search configured: YES (availability verified when requests run)',file=sys.stderr)
            print('Search provider: '+type(getattr(executor,'search_provider',executor)).__name__,file=sys.stderr)
            print('Semantic extractor: '+('CONFIGURED' if provider else 'MISSING'),file=sys.stderr)
            if missing: print(missing+'\nThe scraper can collect evidence without it, but business conclusions remain PARTIAL.',file=sys.stderr)
            second,_=OpenAICompatibleProvider.from_env('RESEARCH_RED_TEAM_LLM')
            independence='EXTERNAL_ADAPTER' if reviewer else ('SECOND_PROVIDER_SEPARATE_PASS' if second else 'SAME_PROVIDER_SEPARATE_PASS' if provider else 'EVIDENCE_ONLY_SEPARATE_PASS')
            reviewer=reviewer or ScrapingResearchExecutor(search_provider=search,fetcher=getattr(executor,'fetcher',None),
                extractor=SemanticGroundedExtractor(second or provider,adversarial=True) if second or provider else None,
                max_results_per_query=cfg.max_results_per_query)
            adapters.update(live_mode=True,independence_level=independence)
            adapters['opportunity_mapper']=adapters['opportunity_mapper'] or DefaultOpportunityMapper(provider)
            adapters['theme_generator']=adapters['theme_generator'] or DefaultThemeGenerator(provider)
            adapters['synthesizer']=adapters['synthesizer'] or DefaultSynthesis()
        writer=RunWriter(args.output)
        def progress(event,payload):
            if event=='SEARCH': print(f"[SEARCH {len_seen[0]+1}/{cfg.max_queries}] {payload['node']}: {payload['query']}",file=sys.stderr,flush=True)
            elif event=='QUERY_COMPLETE':
                len_seen[0]+=1
                print(f"[{payload['status']}] opened={len(payload['sources_opened'])} accepted={len(payload['claims_added'])} rejected={len(payload['claims_rejected'])}",file=sys.stderr,flush=True)
                if payload.get('error'): print('  '+payload['error'],file=sys.stderr,flush=True)
            elif event in ('OPEN','ENTITY','RESEARCH'): print(f"[{event}] {payload.get('name',payload.get('url',payload.get('node','')))}",file=sys.stderr,flush=True)
        len_seen=[0]
        objective=args.objective or 'Research '+args.company+' for a Cornell technical event: company needs, student value, research opportunities and commercial validation.'
        result=run(objective,executor,cfg,reviewer,company=args.company,run_writer=writer,
                   progress=progress if args.live else None,**adapters)
        writer.finish(result)
        print(f"{result['status']} — {args.output / 'summary.md'}")
        return 130 if result['status']=='INTERRUPTED' else 0 if result['status']=='RESOLVED' else 2
    except Exception as exc:
        print('Research configuration/run error: '+str(exc),file=sys.stderr)
        print('Check --help. Any completed work is retained in the run directory JSONL checkpoints.',file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())
