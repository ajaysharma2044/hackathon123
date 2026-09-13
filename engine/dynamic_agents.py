"""Evidence-first resolvers. Specialization lives in contracts and executable query strategies."""
from __future__ import annotations
from dataclasses import asdict
from agent_os import Node, NodeStatus, Evidence, Decompose, Defer
from agents import agent
from research_contracts import EpistemicStatus
from research_runtime import ResearchRuntime

@agent('dynamic_discovery')
def dynamic_discovery(node, graph, ctx):
    runtime = ResearchRuntime(graph,ctx)
    status = runtime.discover(node)
    if status == 'SATURATED':
        return Evidence(node.value,'runtime discovery saturation; not exhaustive company qualification')
    return Defer(NodeStatus.RESEARCH_BACKEND_REQUIRED if status=="RESEARCH_BACKEND_REQUIRED" else
                 NodeStatus.RESEARCH_EXHAUSTED if "BUDGET_EXHAUSTED" in status else NodeStatus.PARTIAL,status)

@agent('dynamic_company_research')
def dynamic_company_research(node, graph, ctx):
    node.completion_gate = 'company'
    return dynamic_entity_research(node,graph,ctx)

@agent('dynamic_entity_research')
def dynamic_entity_research(node, graph, ctx):
    rt = ResearchRuntime(graph,ctx)
    status = rt.research(node)
    if node.node_type == 'company':
        rt.map_opportunities(node)
    if status == 'EVIDENCE_COMPLETE':
        if node.node_type in ('data_opportunity','rd_opportunity','recruiting_opportunity'):
            from research_opportunities import ResearchOpportunity
            try:
                spec = node.value.get('opportunity')
                if not isinstance(spec, ResearchOpportunity):
                    return Defer(NodeStatus.PARTIAL,'structured opportunity mapping required')
                errors = spec.validate(rt.memory,rt.config)
                if errors:return Defer(NodeStatus.PARTIAL,','.join(errors))
            except (TypeError,ValueError) as exc:
                return Defer(NodeStatus.PARTIAL,str(exc))
        return Evidence(node.value,'opened-source claims passed deterministic contract')
    claims = rt.memory.for_subject(node.id)
    state = NodeStatus.CONTRADICTED if any(c.contradictory_claim_ids for c in claims) else (
        NodeStatus.PRIMARY_VALIDATION_REQUIRED if node.completion_gate and rt.gate(node).primary_validation
        else NodeStatus.PARTIAL)
    if status=='RESEARCH_BACKEND_REQUIRED':state=NodeStatus.RESEARCH_BACKEND_REQUIRED
    elif status=='CONTRACT_REQUIRED':state=NodeStatus.CONTRACT_REQUIRED
    elif status=='ROUND_BUDGET_EXHAUSTED' and state==NodeStatus.PARTIAL:state=NodeStatus.RESEARCH_EXHAUSTED
    return Defer(state,status)

@agent('dynamic_theme_generation')
def dynamic_theme_generation(node, graph, ctx):
    rt = ResearchRuntime(graph,ctx)
    # Entity extraction can discover event concepts directly. Optional cognition only proposes
    # hypothesis names and accepted evidence IDs; it cannot supply a resolver or resolved dossier.
    candidates = [n for n in graph.all() if n.node_type in ('theme','event_concept')]
    generator = ctx.get('theme_generator')
    if generator:
        proposed = generator.generate(evidence=list(rt.memory.claims.values()),objective=ctx.get('objective',node.question))
        from research_executor import DiscoveredEntity
        for t in proposed:
            if set(t) - {'name','evidence_claim_ids','event_connection'}:
                return Defer(NodeStatus.PARTIAL,'theme proposal contains unsupported factual fields')
            ent = DiscoveredEntity('theme',t.get('name',''),evidence_claim_ids=tuple(t.get('evidence_claim_ids',())),
                                   relevance=t.get('event_connection',''))
            spawned,_ = rt.spawn(node,[ent])
            candidates.extend(graph.get(i) for i in spawned)
    if not candidates:
        return Defer(NodeStatus.PARTIAL,'event concepts UNKNOWN; no source-supported candidates discovered')
    node.children = list(dict.fromkeys(n.id for n in candidates))
    if all(graph.dependency_complete(i) for i in node.children):
        return Evidence({'candidate_node_ids':node.children},'evidence-complete candidate contracts')
    return Decompose([])  # existing required candidates continue; no duplicated architecture

@agent('independent_red_team')
def independent_red_team(node, graph, ctx):
    reviewer = ctx.get('red_team_executor')
    if reviewer is None or reviewer is ctx.get('research_executor'):
        return Defer(NodeStatus.PARTIAL,'INDEPENDENT_REVIEW_BACKEND_REQUIRED')
    rt = ResearchRuntime(graph,ctx)
    node.question += ' Review accepted evidence IDs: ' + ', '.join(rt.memory.claims)
    status = rt.research(node,executor=reviewer)
    attacked = set()
    for c in rt.memory.for_subject(node.id):
        attacked.update(c.contradictory_claim_ids)
    owners = {rt.memory.claims[i].subject_id for i in attacked if i in rt.memory.claims}
    for owner in owners:
        if owner in graph.nodes:
            graph.get(owner).status = NodeStatus.CONTRADICTED
            graph.get(owner).provenance = 'Reopened by independent red team'
    # Invalidate dependent decisions transitively, including already-resolved rollups.
    changed = True
    while changed:
        changed = False
        for n in graph.all():
            if n.id not in owners and owners.intersection(n.deps+n.children):
                owners.add(n.id);n.status = NodeStatus.PARTIAL;changed = True
    if attacked:return Defer(NodeStatus.CONTRADICTED,'critical evidence challenged; upstream research reopened')
    if status == 'EVIDENCE_COMPLETE':return Evidence(node.value,'independent negative-search contract passed')
    return Defer(NodeStatus.PARTIAL,status)

@agent('evidence_only_synthesis')
def evidence_only_synthesis(node, graph, ctx):
    rt = ResearchRuntime(graph,ctx)
    synth = ctx.get('synthesizer')
    if synth is None:return Defer(NodeStatus.PARTIAL,'SYNTHESIS_ADAPTER_REQUIRED')
    resolved = {n.id:n for n in graph.all() if n.id != node.id and graph.dependency_complete(n.id)}
    out = synth.synthesize(resolved_nodes=resolved,objective=ctx.get('objective',node.question))
    if not isinstance(out,dict) or set(out) - {'claim_ids','candidate_node_ids','missing_questions'}:
        return Defer(NodeStatus.PARTIAL,'synthesis may return evidence IDs and research requests, not factual prose')
    if out.get('missing_questions'):
        # Questions are open research, never implicitly supplied facts.
        import hashlib
        for q in out['missing_questions']:
            nid = 'missing:' + hashlib.sha256(str(q).encode()).hexdigest()[:16]
            graph.add(Node(nid,str(q),resolver='dynamic_entity_research',node_type='problem',completion_gate='problem'))
            if nid not in node.deps:node.deps.append(nid)
        return Defer(NodeStatus.PARTIAL,'synthesis requested missing research')
    ids = out.get('claim_ids',[])
    if not ids or any(i not in rt.memory.claims for i in ids):
        return Defer(NodeStatus.PARTIAL,'synthesis references absent claims')
    if any(rt.memory.claims[i].subject_id not in resolved for i in ids):
        return Defer(NodeStatus.PARTIAL,'synthesis references incomplete evidence owners')
    candidates = out.get('candidate_node_ids',[])
    if not candidates or any(i not in resolved or resolved[i].node_type not in ('theme','event_concept') for i in candidates):
        return Defer(NodeStatus.PARTIAL,'candidate evidence contracts must pass')
    # The renderer copies evidence statements. Arbitrary names, numeric scores, and explanatory
    # prose are not accepted from synthesis. Dimension values retain their epistemic status.
    from research_comparison import compare
    comparisons = compare(candidates, rt.memory, rt.config.decision_weights)
    return Evidence({'claim_ids':ids,'findings':[rt.memory.trace_claim(i) for i in ids],
        'candidates':comparisons,'recommendation':comparisons.get('ranking','UNKNOWN'),
        'commercial_validation':'PRIMARY_VALIDATION_REQUIRED',
        'confidence':'Evidence-bounded comparison; buyer demand and missing dimensions remain explicit',
        'weights':rt.config.decision_weights},'deterministic rendering of accepted evidence only',
        status=NodeStatus.PARTIAL if comparisons['pareto_frontier']=='UNKNOWN' else NodeStatus.RESOLVED)
