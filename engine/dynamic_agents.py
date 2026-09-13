"""Dynamic research agents.

These agents deliberately contain no sector/company/logo lists.  They operate over a pluggable
ResearchExecutor supplied in ctx['research_executor'].  The executor performs live retrieval; these
agents plan questions, ingest atomic claims, spawn entities, and refuse resolution until deterministic
completion gates pass.

Importing this module registers the agents with the existing registry.
"""
from __future__ import annotations

from dataclasses import asdict
import re

from agent_os import Node, NodeStatus, Evidence, Decompose, Defer
from agents import agent
from research_contracts import AtomicClaim, EpistemicStatus, get_gate
from research_executor import MissingResearchExecutor
from research_planner import company_questions, generic_entity_discovery_questions


def _executor(ctx):
    return ctx.get("research_executor") or MissingResearchExecutor()


def _slug(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text[:72] or "entity"


def _serialize_claim(c: AtomicClaim) -> dict:
    d = asdict(c)
    d["status"] = c.status.value
    d["sources"] = [
        {**asdict(s), "tier": int(s.tier)} for s in c.sources
    ]
    return d


def _research_log(batch) -> dict:
    return {
        "queries_run": list(batch.queries_run),
        "sources_opened": list(batch.sources_opened),
        "notes": list(batch.notes),
    }


@agent("dynamic_discovery")
def dynamic_discovery(node, graph, ctx):
    objective = node.question
    round_number = int(ctx.get("discovery_round", 0))
    questions = generic_entity_discovery_questions(objective, round_number)
    batch = _executor(ctx).research(questions, context={
        "node_id": node.id,
        "node_type": node.node_type,
        "objective": objective,
        "round_number": round_number,
    })

    if not batch.claims and not batch.discovered_entities:
        return Defer(
            NodeStatus.PARTIAL,
            "No live research evidence returned. Configure ctx['research_executor']; do not synthesize from memory.",
        )

    children = []
    seen = set()
    for ent in batch.discovered_entities:
        canonical = ent.canonical_url or ent.canonical_name
        key = (ent.entity_type, canonical.lower())
        if key in seen:
            continue
        seen.add(key)
        eid = f"{ent.entity_type}:{_slug(ent.canonical_name)}"
        if eid in graph.nodes:
            continue
        resolver = "dynamic_company_research" if ent.entity_type == "company" else "dynamic_entity_research"
        gate = "company" if ent.entity_type == "company" else None
        children.append(Node(
            id=eid,
            question=f"Research {ent.entity_type}: {ent.canonical_name}",
            resolver=resolver,
            node_type=ent.entity_type,
            completion_gate=gate,
            voi=2.0,
            value={
                "canonical_name": ent.canonical_name,
                "canonical_url": ent.canonical_url,
                "relationship": ent.relationship,
                "discovery_claim_ids": list(ent.evidence_claim_ids),
            },
        ))

    # Discovery itself is not "complete" merely because one batch returned entities.  It becomes a
    # parent over evidence-producing children; saturation must be decided by a later discovery round.
    if children:
        ctx["discovery_round"] = round_number + 1
        return Decompose(children)

    return Evidence(
        {
            "claims": list(batch.claims),
            "research_log": _research_log(batch),
            "note": "Discovery produced evidence but no new entities; treat as a saturation signal, not proof of exhaustiveness.",
        },
        "dynamic discovery executor",
    )


@agent("dynamic_entity_research")
def dynamic_entity_research(node, graph, ctx):
    # Generic entities remain deliberately open until a type-specific contract exists.  This avoids
    # pretending that a one-size-fits-all completion gate works for industries, products, investors,
    # government bodies, and research institutions.
    return Defer(
        NodeStatus.PARTIAL,
        f"No type-specific research contract registered for node_type={node.node_type!r}; spawn a contract before resolution.",
    )


@agent("dynamic_company_research")
def dynamic_company_research(node, graph, ctx):
    name = (node.value or {}).get("canonical_name") if isinstance(node.value, dict) else None
    name = name or node.question.replace("Research company:", "").strip()
    gate = get_gate("company")

    existing_claims = []
    if isinstance(node.value, dict):
        existing_claims = [c for c in node.value.get("claims", []) if isinstance(c, AtomicClaim)]

    initial = gate.evaluate(existing_claims, node.critical_unknown_fields)
    missing = initial.missing + initial.weak + initial.primary_validation
    if not missing:
        missing = [r.field for r in gate.requirements] + ["counterevidence"]

    questions = company_questions(name, missing)
    batch = _executor(ctx).research(questions, context={
        "node_id": node.id,
        "node_type": "company",
        "company_name": name,
        "existing_claims": existing_claims,
    })

    claims = existing_claims + list(batch.claims)
    result = gate.evaluate(claims, node.critical_unknown_fields)
    payload = {
        "canonical_name": name,
        "canonical_url": (node.value or {}).get("canonical_url") if isinstance(node.value, dict) else None,
        "claims": claims,
        "gate": {
            "complete": result.complete,
            "missing": result.missing,
            "weak": result.weak,
            "primary_validation": result.primary_validation,
        },
        "research_log": _research_log(batch),
    }

    node.value = payload

    # Newly discovered adjacent entities become new research nodes rather than prose hidden in a
    # company dossier.
    spawned = []
    for ent in batch.discovered_entities:
        eid = f"{ent.entity_type}:{_slug(ent.canonical_name)}"
        if eid == node.id or eid in graph.nodes:
            continue
        spawned.append(Node(
            id=eid,
            question=f"Research {ent.entity_type}: {ent.canonical_name}",
            resolver="dynamic_company_research" if ent.entity_type == "company" else "dynamic_entity_research",
            node_type=ent.entity_type,
            completion_gate="company" if ent.entity_type == "company" else None,
            value={
                "canonical_name": ent.canonical_name,
                "canonical_url": ent.canonical_url,
                "relationship": ent.relationship,
                "discovery_claim_ids": list(ent.evidence_claim_ids),
            },
            voi=max(0.5, node.voi * 0.8),
        ))

    if spawned:
        # Keep the company open; adjacent research is useful but does not substitute for missing fields.
        for child in spawned:
            graph.add(child)
            if child.id not in node.children:
                node.children.append(child.id)

    if result.primary_validation:
        return Defer(
            NodeStatus.PRIMARY_VALIDATION_REQUIRED,
            f"Desk research cannot resolve fields: {', '.join(result.primary_validation)}",
        )
    if not result.complete:
        return Defer(
            NodeStatus.PARTIAL,
            "Company dossier incomplete. Missing=" + ",".join(result.missing) +
            "; weak=" + ",".join(result.weak),
        )

    return Evidence(payload, "source-backed dynamic company research")


@agent("dynamic_theme_generation")
def dynamic_theme_generation(node, graph, ctx):
    """Theme generation is evidence-bounded: it may only use resolved discovery children.

    The actual generative model belongs in a cognition adapter supplied through ctx.  Without one we
    leave the node open rather than invent themes in Python.
    """
    generator = ctx.get("theme_generator")
    if generator is None:
        return Defer(
            NodeStatus.PARTIAL,
            "No theme_generator configured. Theme cognition must consume graph evidence; hardcoded themes are forbidden.",
        )
    evidence = [
        n for n in graph.all()
        if n.id != node.id and n.status == NodeStatus.RESOLVED
    ]
    themes = generator.generate(evidence=evidence, objective=node.question)
    if not themes:
        return Defer(NodeStatus.PARTIAL, "Theme generator returned no evidence-backed candidates")
    children = []
    for t in themes:
        tid = f"theme:{_slug(t['name'])}"
        children.append(Node(
            id=tid,
            question=f"Research and falsify event theme: {t['name']}",
            resolver=t.get("resolver", "dynamic_entity_research"),
            node_type="theme",
            completion_gate="theme",
            value=t,
            voi=float(t.get("voi", 2.0)),
        ))
    return Decompose(children)


@agent("evidence_only_synthesis")
def evidence_only_synthesis(node, graph, ctx):
    """Synthesis may compare accepted evidence but may not invent factual state.

    A configured synthesizer must return references to resolved node ids.  If it needs a new fact, it
    must request/spawn research rather than adding prose unsupported by the graph.
    """
    synthesizer = ctx.get("synthesizer")
    if synthesizer is None:
        return Defer(NodeStatus.PARTIAL, "No evidence-only synthesizer configured")
    resolved = {n.id: n for n in graph.all() if n.status == NodeStatus.RESOLVED}
    out = synthesizer.synthesize(resolved_nodes=resolved, objective=node.question)
    refs = set(out.get("evidence_node_ids", [])) if isinstance(out, dict) else set()
    unknown_refs = refs - set(resolved)
    if unknown_refs:
        return Defer(
            NodeStatus.PARTIAL,
            "Synthesis referenced unresolved/nonexistent evidence nodes: " + ", ".join(sorted(unknown_refs)),
        )
    return Evidence(out, "evidence-only synthesis over resolved graph nodes")
