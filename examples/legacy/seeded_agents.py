"""
Agent registry + concrete agents (docs/agentic/agents.md). Every agent declares a Permission and a
run(node, graph, ctx) -> Evidence | Decompose | Defer | RequestAction.

AUTONOMOUS agents do real work now by reusing the engines already in the repo (node_scraper, grounding,
event_optimizer, voi, value_matrix). DISCOVERY/COGNITION agents that need live web/LLM reasoning
(discover 200 firms, research a business unit, synthesize the topic) DECOMPOSE what they can and
Defer(NEEDS_RESEARCH) the rest -- they never fabricate a firm, a buyer, or a price.
"""
from __future__ import annotations
from agent_os import Node, NodeStatus, Permission, Evidence, Decompose, Defer, RequestAction

REGISTRY = {}   # name -> (fn, permission)
def agent(name, permission=Permission.AUTONOMOUS_READ):
    def deco(fn): REGISTRY[name] = (fn, permission); return fn
    return deco
def get(name): return REGISTRY.get(name)

# ---------------------------------------------------------------- AUTONOMOUS: reuse real engines ----
@agent("grounding")
def grounding_agent(node, graph, ctx):
    """Resolve a scraped/cost input node from the grounding registry (refreshes stale via node_scraper)."""
    import grounding, node_scraper
    key = ctx.get("grounding_key", node.id)
    if key in node_scraper.SOURCE_SPECS:
        node_scraper.refresh()                      # autonomous web refresh of stale nodes
    d = grounding.NODES.get(key)
    if not d: return Defer(NodeStatus.NEEDS_RESEARCH, f"no grounding node {key!r}")
    if d["status"] == "PRIMARY": return Defer(NodeStatus.PRIMARY, d["src"])
    if d["status"] == "QUOTE":   return Defer(NodeStatus.QUOTE, d["src"])
    return Evidence(d["v"], d["src"])

@agent("cost")
def cost_agent(node, graph, ctx):
    """CostResolutionAgent: compute grounded event cost from real scraped catering + venue anchor."""
    import cornell_scenario as cs
    cost, food, venue, ops = cs.grounded_cornell(n=ctx.get("n_builders", 250))
    return Evidence(round(cost), f"grounded: food ${food}/builder (scraped) + venue ${venue} (QUOTE-anchored) + ops ${ops}")

@agent("pricing")
def pricing_agent(node, graph, ctx):
    """PricingAgent: recommend an ask from SCRAPED rate cards (LF syndicated/Tier-A, panel floor)."""
    import grounding as g
    lf_synd = g.NODES["rc_lf_syndicated"]["v"]; lf_a = g.NODES["rc_lf_tierA"]["v"]; panel = g.NODES["rc_panel_complete"]["v"]
    rec = {"sponsorship_study_syndicated": lf_synd, "custom_study_tierA_floor": lf_a,
           "per_complete_panel_floor": panel, "note": "rational ceilings from published cards; observed WTP is PRIMARY"}
    return Evidence(rec, "grounding rate cards (LF prospectus, panel pass-through)")

@agent("event_design")
def event_design_agent(node, graph, ctx):
    """Pick the event design via the mechanism-design + quant engines already built."""
    import event_optimizer as eo
    d = eo.EventDesign("Cornell", n_builders=ctx.get("n_builders", 250), duration_h=36,
                       travel_funded=False, hotel_premium=False, n_research_sponsors=2,
                       mentor_ratio=0.08, research_minutes=15.0)
    o = eo.objectives(d)
    return Evidence({"experience": round(o["experience"], 2), "research_info": round(o["research_info"], 1)},
                    "event_optimizer.objectives (mechanism-design engine)")

@agent("portfolio_optimizer")
def portfolio_agent(node, graph, ctx):
    """Combine resolved cost + a sponsorship-raise assumption into the contribution, honestly labeled."""
    cost = graph.get("cost").value
    if cost is None: return Defer(NodeStatus.UNKNOWN, "waiting on cost")
    breakeven = cost
    return Evidence({"grounded_cost": cost, "breakeven_sponsorship": breakeven,
                     "note": "profit above this raise; the raise itself is PRIMARY (a sponsor 'yes')"},
                    "cost (grounded) + break-even identity")

# --------------------------------------------------- AUTONOMOUS: deterministic structure/transforms ----
@agent("cornell_capability")
def cornell_capability_agent(node, graph, ctx):
    """Enumerate Cornell builder segments from KNOWN counts; buildable-fraction stays PRIMARY (memory)."""
    segs = [("ai_ml", "Cornell Data Science 92 + Bowers DS"), ("quant", "Quant Fund + 150-competition (Jump/IMC courting)"),
            ("technical_builder", "Bowers CIS 2,000+ majors"), ("founders", "eLab 8-12 ventures/yr"),
            ("hardware_robotics", "~25 active project teams")]
    kids = [Node(f"cap_{k}", f"capability: {k}", resolver="attendance", status=NodeStatus.RESOLVED,
                 value=src, provenance="cornell-audience-map.md (KNOWN counts)") for k, src in segs]
    kids.append(Node("cap_buildable_fraction", "what fraction can actually build a weekend project?",
                     resolver=None, status=NodeStatus.PRIMARY, voi=2.5,
                     provenance="Tableau-locked per-dept counts; the real unknown (memory)"))
    return Decompose(kids)

@agent("industry_expansion")
def industry_expansion_agent(node, graph, ctx):
    """Seed the industry set deterministically; full 30-industry discovery is flagged NEEDS_RESEARCH."""
    seed = ["fintech_payments", "ai_infra_devtools", "quant_finance", "logistics", "healthcare", "energy"]
    kids = [Node(f"battle_{i}", f"economic battle: {i}", resolver="economic_battle", voi=1.5) for i in seed]
    kids.append(Node("industry_full_universe", "the other ~24 industries", resolver="industry_expansion",
                     status=NodeStatus.NEEDS_RESEARCH, voi=1.0, provenance="live industry sweep needed (hook)"))
    return Decompose(kids)

@agent("sponsor_discovery")
def sponsor_discovery_agent(node, graph, ctx):
    """Seed sponsors from the repo's verified prospect list; the full universe is NEEDS_RESEARCH."""
    seed = [("jump_imc", "quant recruiters already courting Cornell"), ("citadel", "standing elite-competition intake"),
            ("startup_credit_programs", "AWS Activate / GCP / MongoDB / Anthropic"), ("stripe_growth", "80% blind spot")]
    kids = [Node(f"company_{k}", f"company: {k}", resolver="company_research", status=NodeStatus.RESOLVED,
                 value=why, provenance="top-prospects.md (verified seed)") for k, why in seed]
    kids.append(Node("sponsor_full_universe", "discover the full 150-300 firm universe",
                     resolver="sponsor_discovery", status=NodeStatus.NEEDS_RESEARCH, voi=2.0,
                     provenance="live 30-industry x N-firm sweep needed (hook)"))
    return Decompose(kids)

@agent("attendance")
def attendance_agent(node, graph, ctx):
    """Estimate accessible attendance from KNOWN Cornell counts; the yield rate is PRIMARY."""
    return Evidence({"accessible_pool": "hundreds who self-select (of 2,000+ CIS + eng)", "target_n": 250,
                     "yield_rate": "PRIMARY - depends on recruiting"}, "cornell-audience-map.md")

# ------------------------------------------------------- COGNITION agents: honest research hooks ----
@agent("economic_battle")
def economic_battle_agent(node, graph, ctx):
    return Defer(NodeStatus.NEEDS_RESEARCH, "needs a live pain/spend sweep for this industry (Economic Battle Agent hook)")

@agent("company_research")
def company_research_agent(node, graph, ctx):
    if node.status == NodeStatus.RESOLVED: return Evidence(node.value, node.provenance)  # seeded
    return Defer(NodeStatus.NEEDS_RESEARCH, "needs live business-unit + buyer + budget research (hook)")

@agent("topic_synthesis")
def topic_synthesis_agent(node, graph, ctx):
    return Defer(NodeStatus.NEEDS_RESEARCH, "synthesize topic from resolved capability x industry battles (LLM hook)")

@agent("falsifier")
def falsifier_agent(node, graph, ctx):
    """For a claim/topic, emit the falsification test as a child (STATE.md discipline). Deterministic."""
    kid = Node(f"falsify_{node.id}", f"falsification test for: {node.question}", resolver=None,
               status=NodeStatus.PRIMARY, voi=3.5,
               provenance="10-15 buyer interviews / a $5-15K paid pilot; no check in ~4 weeks weakens the thesis")
    return Decompose([kid])

# creativity / novelty-search: deterministic transforms over the capability set
@agent("analogist")
def analogist_agent(node, graph, ctx):
    return Evidence(["what industry has THIS shape of problem elsewhere?"], "analogist transform (seed)")

# ------------------------------------------------------------------- EXTERNAL ACTION (gated) --------
@agent("outreach", permission=Permission.NEEDS_APPROVAL)
def outreach_agent(node, graph, ctx):
    """Proposes an external email (sponsor ask / venue quote). NEVER sends autonomously -> approval gate."""
    return RequestAction("send sponsor/venue outreach email",
                         {"to": ctx.get("to", "Cornell Conf & Event Svcs / a quant recruiter"),
                          "purpose": node.question})
