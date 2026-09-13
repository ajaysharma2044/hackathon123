"""One-button Run-2 economy-wide discovery pipeline.

Usage from repo root/engine:
    python3 discovery_runner.py /path/to/session_findings.json

The findings file is produced by a live session/browser researcher and records its mode as
SESSION_ASSISTED. The Python governor does not claim it browsed the web itself.
"""
from __future__ import annotations
import json, sys
from agent_os import Node, NodeGraph
from governor import Governor
from research_bridge import ResearchBridge
import discovery_agents


def build_discovery_graph() -> NodeGraph:
    g = NodeGraph()
    add = lambda **kw: g.add(Node(**kw))
    add(id="cornell_v2", question="What rare Cornell capability intersections are real now?", resolver="deep_cornell", voi=5)
    add(id="capability_intersections", question="Which capability intersections create an unusual Cornell advantage?",
        resolver="capability_intersection", deps=["cornell_v2"], voi=5)
    add(id="industries_v2", question="What economy-wide battles deserve serious consideration?",
        resolver="industry_expansion_live", voi=6)
    add(id="theme_frontier", question="Generate and preserve the broad anti-anchored theme frontier",
        resolver="theme_generation", deps=["capability_intersections", "industries_v2"], voi=5)
    add(id="finalists", question="Which themes survive hackathon/substitute/anchor-product falsification?",
        resolver="topic_synthesis_live", deps=["theme_frontier"], voi=5)
    add(id="product_economy", question="Map recursive products and products-behind-products for finalists",
        resolver="product_stack", deps=["finalists"], voi=4)
    add(id="sponsor_universe_v2", question="Expand economically connected organizations, not generic logos",
        resolver="sponsor_universe_live", deps=["finalists", "product_economy"], voi=4)
    add(id="account_value_v2", question="Map legitimate account value surfaces for the winner",
        resolver="account_value", deps=["sponsor_universe_v2"], voi=4)
    add(id="multiplier_v2", question="Find maximum natural value fan-out per unit participant attention",
        resolver="multiplier", deps=["account_value_v2"], voi=4)
    add(id="cost_v2", question="What event costs are observed, quote-pending, scenario or unknown?",
        resolver="cost_live", voi=4)
    add(id="pricing_v2", question="What pricing is observed versus comparable versus hypothesis?",
        resolver="pricing_live", deps=["account_value_v2"], voi=4)
    add(id="attendance_v2", question="What capability-constrained attendance is evidenced versus scenario?",
        resolver="attendance_live", deps=["cornell_v2"], voi=3)
    add(id="capacity_v2", question="What resource vector could bind event capacity?",
        resolver="capacity_live", deps=["attendance_v2", "cost_v2"], voi=3)
    add(id="in_kind_v2", question="Which required resources can be offset naturally without inflating face value?",
        resolver="in_kind_live", deps=["cost_v2"], voi=2)
    add(id="conflicts_v2", question="Map commercial, IP, data-rights and research-validity conflicts",
        resolver="conflict", deps=["sponsor_universe_v2"], voi=3)
    add(id="portfolio_v2", question="Choose a Pareto commercial portfolio subject to hard participant/research constraints",
        resolver="portfolio_optimizer_live", deps=["multiplier_v2", "conflicts_v2", "cost_v2", "pricing_v2", "attendance_v2", "capacity_v2", "in_kind_v2"], voi=4)
    add(id="final_recommendation", question="What hackathon should Cornell host?", resolver="final_synthesis",
        deps=["portfolio_v2"], voi=6)
    add(id="final_falsification", question="Try to kill the final recommendation", resolver="theme_falsifier_live",
        deps=["final_recommendation"], voi=6)
    return g


def run_discovery(findings_path: str):
    bridge = ResearchBridge.from_json(findings_path)
    gov = Governor(build_discovery_graph(), ctx={"research_bridge": bridge}, max_steps=1000)
    return gov, gov.run()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 discovery_runner.py /path/to/session_findings.json")
    gov, report = run_discovery(sys.argv[1])
    print(json.dumps(report, indent=2, default=str))
