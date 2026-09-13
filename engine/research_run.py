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

def run(objective, executor=None, config=None, red_team_executor=None, **adapters):
    ctx = dict(objective=objective,research_executor=executor,
               research_config=config or ResearchConfig(),red_team_executor=red_team_executor,**adapters)
    graph = build_research_graph(objective)
    governor = Governor(graph,ctx)
    report = governor.run()
    rt = ResearchRuntime(graph,ctx)
    final = graph.get('final_synthesis')
    primary = [asdict(c) for c in rt.memory.claims.values() if c.status.value in ('UNKNOWN','PRIMARY_VALIDATION_REQUIRED')]
    for n in graph.all():
        if n.node_type=='company' and not any(c.field=='wtp_status' for c in rt.memory.for_subject(n.id)):
            primary.append({'subject_id':n.id,'field':'wtp_status','status':'PRIMARY_VALIDATION_REQUIRED',
                            'next':'Ask the actual buyer about a scoped paid pilot; do not infer from funding'})
    return {'status': 'RESEARCH_BACKEND_REQUIRED' if executor is None else
                'RESOLVED' if final.status.value=='RESOLVED' else 'PARTIAL',
        'objective':objective,'final_recommendation':final.value or 'UNKNOWN',
        'confidence':'UNKNOWN' if final.value is None else final.value.get('confidence','UNKNOWN'),
        'discovered_entities':[asdict(n) for n in rt.economy.nodes.values()],
        'source_documents':[asdict(d) for d in rt.memory.documents.values()],
        'atomic_claims':[asdict(c) for c in rt.memory.claims.values()],
        'finding_provenance':{i:f.trace() for i,f in rt.memory.findings.items()},
        'industries':[asdict(n) for n in graph.all() if n.node_type=='industry'],
        'economic_problems':[asdict(n) for n in graph.all() if n.node_type=='problem'],
        'candidate_event_concepts':[asdict(n) for n in graph.all() if n.node_type in ('theme','event_concept')],
        'company_dossiers':[asdict(n) for n in graph.all() if n.node_type=='company'],
        'research_opportunities':[asdict(n) for n in graph.all() if n.node_type in ('rd_opportunity','data_opportunity')],
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
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--objective',required=True)
    parser.add_argument('--executor',help='Installed trusted module:factory implementing ResearchExecutor')
    parser.add_argument('--red-team-executor',help='Independent reviewer module:factory')
    parser.add_argument('--synthesizer',help='Trusted module:factory returning evidence ID selections')
    parser.add_argument('--theme-generator',help='Optional trusted module:factory proposing evidence-linked themes')
    parser.add_argument('--opportunity-mapper',help='Trusted module:factory proposing structured research plans')
    parser.add_argument('--config',type=Path,help='JSON ResearchConfig overrides')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    cfg=ResearchConfig(**json.loads(args.config.read_text())) if args.config else ResearchConfig()
    result=run(args.objective,load_adapter(args.executor),cfg,load_adapter(args.red_team_executor),
        synthesizer=load_adapter(args.synthesizer,('synthesize',)),
        theme_generator=load_adapter(args.theme_generator,('generate',)),
        opportunity_mapper=load_adapter(args.opportunity_mapper,('map_opportunities',)))
    rendered=json.dumps(result,indent=2,default=serialize)
    if args.output:args.output.write_text(rendered+'\n')
    else:print(rendered)
    return 0 if result['status']=='RESOLVED' else 2

if __name__=='__main__':raise SystemExit(main())
