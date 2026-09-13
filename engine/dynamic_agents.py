"""Dynamic, evidence-first research agents. No production company/sector lists."""
from __future__ import annotations
from urllib.parse import urlparse
import re
from agent_os import Node,NodeStatus,Evidence,Defer
from agents import agent
from research_contracts import AtomicClaim,EpistemicStatus,ResearchCoverage,get_gate
from research_executor import MissingResearchExecutor
from research_planner import company_questions,generic_entity_discovery_questions,theme_questions

def _executor(ctx):
    if ctx.get("research_executor") is not None: return ctx["research_executor"]
    if ctx.get("offline"): return MissingResearchExecutor()
    try:
        from web_research import build_default_web_executor
        ex=build_default_web_executor(extractor=ctx.get("grounded_extractor")); ctx["research_executor"]=ex; return ex
    except Exception: return MissingResearchExecutor()

def _slug(text): return re.sub(r"[^a-z0-9]+","-",text.lower()).strip("-")[:72] or "entity"
def _official_domain(value):
    if not isinstance(value,dict) or not value.get("canonical_url"): return None
    return (urlparse(value["canonical_url"]).hostname or "").lower().removeprefix("www.") or None

def _merge_claims(a,b):
    out={c.claim_id:c for c in a if isinstance(c,AtomicClaim)}
    for c in b:
        if isinstance(c,AtomicClaim): out.setdefault(c.claim_id,c)
    return list(out.values())
def _merge_candidates(a,b,limit=500):
    out={getattr(c,"candidate_id",str(i)):c for i,c in enumerate(a)}
    for c in b: out.setdefault(c.candidate_id,c)
    return list(out.values())[-limit:]
def _coverage(value): return value.get("coverage") if isinstance(value,dict) and isinstance(value.get("coverage"),ResearchCoverage) else ResearchCoverage()

def _validated_inferences(ctx,subject,missing,claims,node_type):
    r=ctx.get("grounded_reasoner")
    if r is None: return []
    raw=r.infer(subject=subject,missing_fields=list(missing),claims=list(claims),node_type=node_type); known={c.claim_id for c in claims}; out=[]
    for c in raw or []:
        if not isinstance(c,AtomicClaim) or c.status not in {EpistemicStatus.INFERENCE,EpistemicStatus.HYPOTHESIS}: continue
        if c.status==EpistemicStatus.INFERENCE and not set(c.supporting_claim_ids).issubset(known): continue
        out.append(c)
    return out

def _spawn(graph,ent,parent_voi=2):
    eid=f"{ent.entity_type}:{_slug(ent.canonical_name)}"
    if eid in graph.nodes: return graph.nodes[eid],False
    resolver={"company":"dynamic_company_research","theme":"dynamic_theme_research"}.get(ent.entity_type,"dynamic_entity_research"); gate={"company":"company","theme":"theme"}.get(ent.entity_type)
    n=Node(eid,f"Research {ent.entity_type}: {ent.canonical_name}",resolver,node_type=ent.entity_type,completion_gate=gate,voi=max(.5,parent_voi*.8),value={"canonical_name":ent.canonical_name,"canonical_url":ent.canonical_url,"relationship":ent.relationship,"discovery_claim_ids":list(ent.evidence_claim_ids)},max_attempts=7); graph.add(n); return n,True

@agent("dynamic_discovery")
def dynamic_discovery(node,graph,ctx):
    state=node.value if isinstance(node.value,dict) else {}; rounds=int(state.get("rounds",0)); no_new=int(state.get("no_new_rounds",0)); known=set(state.get("known_entity_names",[])); claims=[c for c in state.get("claims",[]) if isinstance(c,AtomicClaim)]; candidates=list(state.get("evidence_candidates",[])); coverage=_coverage(state)
    batch=_executor(ctx).research(generic_entity_discovery_questions(node.question,rounds,sorted(known)),{"node_id":node.id,"node_type":"discovery","objective":node.question,"round_number":rounds})
    if not batch.backend_available: return Defer(NodeStatus.RESEARCH_BACKEND_REQUIRED,"No live search/scrape backend is available")
    before=len(claims); claims=_merge_claims(claims,batch.claims); candidates=_merge_candidates(candidates,batch.evidence_candidates); coverage.merge(batch.coverage); new=0
    lower={x.lower() for x in known}
    for ent in batch.discovered_entities:
        if ent.canonical_name.lower() not in lower:
            known.add(ent.canonical_name); lower.add(ent.canonical_name.lower()); _,created=_spawn(graph,ent,node.voi); new+=int(created)
    rounds+=1; no_new=no_new+1 if new==0 and len(claims)==before else 0
    node.value={"rounds":rounds,"no_new_rounds":no_new,"known_entity_names":sorted(known),"claims":claims,"evidence_candidates":candidates,"coverage":coverage,"research_log":{"queries_run":list(coverage.queries_run),"sources_opened":sorted(coverage.source_urls),"last_batch_notes":list(batch.notes),"rejected_claims":list(batch.rejected_claims)}}
    if rounds>=int(ctx.get("discovery_max_rounds",5)) or no_new>=int(ctx.get("discovery_saturation_patience",2)):
        if not known and not claims: return Defer(NodeStatus.RESEARCH_EXHAUSTED,"Discovery produced no grounded entities or claims")
        return Evidence(node.value,"live search/scrape discovery reached saturation")
    return Defer(NodeStatus.PARTIAL,f"Discovery round {rounds} complete; continue until saturation")

@agent("dynamic_entity_research")
def dynamic_entity_research(node,graph,ctx): return Defer(NodeStatus.CONTRACT_REQUIRED,f"No type-specific completion contract for node_type={node.node_type!r}")

def _research_typed(node,graph,ctx,gate_name,planner,node_type):
    state=node.value if isinstance(node.value,dict) else {}; name=state.get("canonical_name") or node.question.split(":",1)[-1].strip(); claims=[c for c in state.get("claims",[]) if isinstance(c,AtomicClaim)]; candidates=list(state.get("evidence_candidates",[])); coverage=_coverage(state); no_progress=int(state.get("no_progress_rounds",0)); gate=get_gate(gate_name)
    before=gate.evaluate(claims,node.critical_unknown_fields,coverage); missing=before.missing+before.weak+before.missing_negative_search
    if not missing and before.primary_validation: return Defer(NodeStatus.PRIMARY_VALIDATION_REQUIRED,"Desk research reached primary validation: "+", ".join(before.primary_validation))
    domain=_official_domain(state); qs=planner(name,missing or [r.field for r in gate.requirements],official_domain=domain) if planner is company_questions else planner(name,missing or [r.field for r in gate.requirements])
    batch=_executor(ctx).research(qs,{"node_id":node.id,"node_type":node_type,"subject_name":name,"company_name":name if node_type=="company" else None,"official_domain":domain,"existing_claims":claims})
    if not batch.backend_available: return Defer(NodeStatus.RESEARCH_BACKEND_REQUIRED,"No live search/scrape backend is available")
    old_ids={c.claim_id for c in claims}; old_sources=set(coverage.source_urls); claims=_merge_claims(claims,batch.claims); candidates=_merge_candidates(candidates,batch.evidence_candidates); coverage.merge(batch.coverage); interim=gate.evaluate(claims,node.critical_unknown_fields,coverage); claims=_merge_claims(claims,_validated_inferences(ctx,name,interim.missing+interim.weak,claims,node_type)); result=gate.evaluate(claims,node.critical_unknown_fields,coverage); progressed={c.claim_id for c in claims}!=old_ids or set(coverage.source_urls)!=old_sources; no_progress=0 if progressed else no_progress+1
    node.value={**state,"canonical_name":name,"claims":claims,"evidence_candidates":candidates,"coverage":coverage,"no_progress_rounds":no_progress,"gate":{"complete":result.complete,"missing":result.missing,"weak":result.weak,"primary_validation":result.primary_validation,"missing_negative_search":result.missing_negative_search},"research_log":{"queries_run":list(coverage.queries_run),"sources_opened":sorted(coverage.source_urls),"last_batch_notes":list(batch.notes),"rejected_claims":list(batch.rejected_claims)}}
    for ent in batch.discovered_entities: _spawn(graph,ent,node.voi)
    if result.primary_validation: return Defer(NodeStatus.PRIMARY_VALIDATION_REQUIRED,"Primary validation required: "+", ".join(result.primary_validation))
    if result.complete: return Evidence(node.value,f"grounded {node_type} research: search + fetched pages + anchored claims")
    if no_progress>=int(ctx.get("research_no_progress_patience",2)): return Defer(NodeStatus.RESEARCH_EXHAUSTED,"Search/scrape stopped adding evidence. Missing="+",".join(result.missing)+"; weak="+",".join(result.weak)+"; negative="+",".join(result.missing_negative_search))
    return Defer(NodeStatus.PARTIAL,"More grounded research required. Missing="+",".join(result.missing)+"; weak="+",".join(result.weak)+"; negative="+",".join(result.missing_negative_search))

@agent("dynamic_company_research")
def dynamic_company_research(node,graph,ctx): return _research_typed(node,graph,ctx,"company",company_questions,"company")
@agent("dynamic_theme_research")
def dynamic_theme_research(node,graph,ctx): return _research_typed(node,graph,ctx,"theme",theme_questions,"theme")

@agent("dynamic_theme_generation")
def dynamic_theme_generation(node,graph,ctx):
    generator=ctx.get("theme_generator")
    if generator is None: return Defer(NodeStatus.CONTRACT_REQUIRED,"No evidence-bounded theme generator configured; hardcoded themes are forbidden")
    evidence=[n for n in graph.all() if n.id!=node.id and n.status==NodeStatus.RESOLVED]; resolved_ids={n.id for n in evidence}; themes=generator.generate(evidence=evidence,objective=node.question)
    ids=[]
    for t in themes or []:
        refs=set(t.get("evidence_node_ids",[]))
        if not refs or not refs.issubset(resolved_ids): continue
        tid=f"theme:{_slug(t['name'])}"
        if tid not in graph.nodes: graph.add(Node(tid,f"Research and falsify event theme: {t['name']}","dynamic_theme_research",node_type="theme",completion_gate="theme",value={"canonical_name":t["name"],"generation_evidence_node_ids":sorted(refs)},voi=float(t.get("voi",2)),max_attempts=6))
        ids.append(tid)
    if not ids: return Defer(NodeStatus.RESEARCH_EXHAUSTED,"No generated theme had valid evidence-node references")
    return Evidence({"theme_node_ids":sorted(ids),"evidence_node_ids":sorted(resolved_ids)},"evidence-bounded theme generation")

def _claim_index(graph):
    out={}
    for n in graph.all():
        if n.status==NodeStatus.RESOLVED and isinstance(n.value,dict):
            for c in n.value.get("claims",[]):
                if isinstance(c,AtomicClaim): out[c.claim_id]=c
    return out

@agent("evidence_only_synthesis")
def evidence_only_synthesis(node,graph,ctx):
    syn=ctx.get("synthesizer")
    if syn is None: return Defer(NodeStatus.CONTRACT_REQUIRED,"No claim-locked synthesizer configured")
    resolved={n.id:n for n in graph.all() if n.status==NodeStatus.RESOLVED}; claims=_claim_index(graph); out=syn.synthesize(resolved_nodes=resolved,claims=claims,objective=node.question)
    if not isinstance(out,dict): return Defer(NodeStatus.RESEARCH_EXHAUSTED,"Synthesizer must return structured output")
    sections=list(out.get("assertions",[]))+list(out.get("recommendations",[]))
    for item in sections:
        refs=set(item.get("evidence_claim_ids",[])) if isinstance(item,dict) else set()
        if not refs: return Defer(NodeStatus.PARTIAL,"Every assertion/recommendation must cite evidence_claim_ids")
        if not refs.issubset(claims): return Defer(NodeStatus.PARTIAL,"Synthesis referenced unknown claim ids: "+", ".join(sorted(refs-set(claims))))
    if not sections: return Defer(NodeStatus.PARTIAL,"Synthesis returned no claim-locked assertions/recommendations")
    return Evidence(out,"claim-locked synthesis over resolved evidence graph")
