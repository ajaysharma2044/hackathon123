"""Run-2 product agents for economy-wide, source-backed discovery.

These agents deliberately do not browse by themselves. They consume the ResearchBridge, whose
findings are produced by a live browser/session researcher with source provenance. This is the honest
boundary between SESSION_ASSISTED_LIVE_RESEARCH and a future self-contained browser runtime.
"""
from __future__ import annotations
import json
from agent_os import Node, NodeStatus, Evidence, Decompose, Defer
from agents import agent


def _bridge(ctx):
    return ctx.get("research_bridge")


def _provenance(packet) -> str:
    return json.dumps({
        "research_mode": packet.get("research_mode"),
        "sources": packet.get("provenance", []),
    }, sort_keys=True, default=str)


def _packet_agent(node, graph, ctx):
    bridge = _bridge(ctx)
    if bridge is None:
        return Defer(NodeStatus.NEEDS_RESEARCH, "ResearchBridge unavailable; live/session research required")
    packet = bridge.packet(node.id, node.resolver)
    if packet is None:
        return Defer(NodeStatus.NEEDS_RESEARCH, f"no sourced research packet for {node.id}")
    if packet["status"] == "CONTRADICTED":
        return Evidence({"status": "CONTRADICTED", "claims": packet["claims"]}, _provenance(packet))
    value = packet["value"]
    if isinstance(value, dict) and value.get("children"):
        children = []
        for spec in value["children"]:
            children.append(Node(
                id=spec["id"], question=spec.get("question", spec["id"]),
                resolver=spec.get("resolver"), voi=spec.get("voi", 1.0), deps=spec.get("deps", []),
            ))
        return Decompose(children)
    return Evidence(value, _provenance(packet))


for _name in [
    "live_research", "deep_cornell", "capability_intersection", "economic_battle_live", "problem",
    "workflow", "product_stack", "product_dependency", "competitor_complement", "structural_gap",
    "hackathon_fit", "anchor_product", "theme_generation", "topic_synthesis_live", "theme_falsifier_live",
    "company_research_live", "account_value", "multiplier", "research_product", "rd_product",
    "pricing_live", "cost_live", "attendance_live", "in_kind_live", "capacity_live",
    "portfolio_optimizer_live", "conflict", "continuation", "final_synthesis",
]:
    agent(_name)(_packet_agent)


@agent("industry_expansion_live")
def industry_expansion_live(node, graph, ctx):
    """Economy-wide expansion from sourced session findings, never a six-sector constant."""
    bridge = _bridge(ctx)
    if bridge is None:
        return Defer(NodeStatus.NEEDS_RESEARCH, "live economy-wide industry sweep required")
    fs = bridge.resolver_findings("industry_expansion_live", tag="industry_family")
    if not fs:
        return Defer(NodeStatus.NEEDS_RESEARCH, "no sourced industry-family findings ingested")
    children = []
    seen = set()
    for f in fs:
        v = f.value
        fid = v.get("id") if isinstance(v, dict) else None
        name = v.get("name") if isinstance(v, dict) else str(v)
        if not fid or fid in seen:
            continue
        seen.add(fid)
        children.append(Node(fid, f"economic battle: {name}", resolver="economic_battle_live", voi=v.get("voi", 1.0)))
    return Decompose(children)


@agent("sponsor_universe_live")
def sponsor_universe_live(node, graph, ctx):
    """Expand concrete organizations from sourced findings; no fixed four-logo universe."""
    bridge = _bridge(ctx)
    if bridge is None:
        return Defer(NodeStatus.NEEDS_RESEARCH, "live sponsor/buyer expansion required")
    fs = bridge.resolver_findings("sponsor_universe_live", tag="organization")
    if not fs:
        return Defer(NodeStatus.NEEDS_RESEARCH, "no sourced organization findings ingested")
    children = []
    seen = set()
    for f in fs:
        v = f.value
        if not isinstance(v, dict) or not v.get("id") or v["id"] in seen:
            continue
        seen.add(v["id"])
        children.append(Node(v["id"], f"account: {v.get('name', v['id'])}", resolver="company_research_live", voi=v.get("voi", 1.0)))
    return Decompose(children)
