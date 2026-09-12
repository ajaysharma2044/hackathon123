"""
Business-model discovery (docs/business-model-discovery.md; Phase 21).

Sponsorship is ONE row here, not the frame. Each monetization model is scored on DECOMPOSED ordinal
dimensions (never collapsed) and the module returns a Pareto set, mirroring the "keep the vector"
discipline of icp_profile / sponsor_economics. It also carries the single most important pricing
rule from the whole repo, made executable:

    rational WTP ceiling  =  ValueOfDecision  x  P(evidence changes the decision)      (a CEILING)
    observed WTP          =  UNKNOWN until a signed check                              (the truth)

`rational_price_ceiling` returns None whenever the decision value is UNKNOWN — it refuses to invent a
price, exactly as beliefs.py refuses to sample UNKNOWN. A high ceiling means a buyer COULD rationally
pay a lot; it is never evidence they WILL.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from beliefs import Belief

NONE, LOW, MED, HIGH = 0, 1, 2, 3
_LABEL = {0: "NONE", 1: "LOW", 2: "MED", 3: "HIGH"}

# Dimensions where HIGHER is better. sales_cycle/conflict_risk/capital_intensity are stored so that
# HIGHER = BETTER too (i.e. 3 = short cycle / low conflict / low capital need), keeping dominance
# monotonic across the whole vector.
DIMS = ["revenue_potential", "gross_margin", "repeatability", "sales_cycle_short", "scalability",
        "conflict_low", "participant_alignment", "defensibility", "capital_light"]


@dataclass
class BusinessModel:
    code: str
    name: str
    revenue_potential: int
    gross_margin: int
    repeatability: int
    sales_cycle_short: int      # 3 = short sales cycle (good)
    scalability: int
    conflict_low: int           # 3 = low conflict-of-interest risk (good)
    participant_alignment: int  # 3 = participants are well-served, not extracted from (good)
    defensibility: int
    capital_light: int          # 3 = low capital intensity (good)
    note: str = ""

    def vector(self) -> dict:
        d = asdict(self)
        return {k: _LABEL[d[k]] for k in DIMS}

    def raw(self) -> dict:
        d = asdict(self)
        return {k: d[k] for k in DIMS}


# ASSUMED ordinal ratings (labeled). Grounded in the repo's cited evidence where it exists:
# sponsorship revenue caps ~$30-50K (research-findings.md, event-comps.md); research engagements
# $25-250K (research-pricing.md); standalone passive intelligence "not a business by itself"
# (STATE.md caveat #7); recruiting has proven WTP but is FCRA-constrained (recruiting-legal.md).
BUSINESS_MODELS = {
    "SPONSORSHIP": BusinessModel(
        "SPONSORSHIP", "Event sponsorship (logo/booth/prize)", revenue_potential=LOW, gross_margin=MED,
        repeatability=MED, sales_cycle_short=MED, scalability=LOW, conflict_low=HIGH,
        participant_alignment=MED, defensibility=LOW, capital_light=LOW,
        note="Capped ~$30-50K/sponsor (Cal Hacks $50K/3000). Trivially copyable; the frame the reset rejects."),
    "RESEARCH_ENGAGEMENT": BusinessModel(
        "RESEARCH_ENGAGEMENT", "Custom research study", revenue_potential=HIGH, gross_margin=MED,
        repeatability=MED, sales_cycle_short=LOW, scalability=LOW, conflict_low=HIGH,
        participant_alignment=MED, defensibility=MED, capital_light=MED,
        note="$25-250K comparables (LF/Forrester/IDC). WTP-for-THIS cohort still UNKNOWN (caveat #1)."),
    "PER_PROBLEM_MANDATE": BusinessModel(
        "PER_PROBLEM_MANDATE", "Per-problem solving mandate", revenue_potential=HIGH, gross_margin=MED,
        repeatability=MED, sales_cycle_short=LOW, scalability=MED, conflict_low=HIGH,
        participant_alignment=HIGH, defensibility=MED, capital_light=MED,
        note="Company brings an expensive problem; we design the environment. The reset's native shape."),
    "RND_CONTRACT": BusinessModel(
        "RND_CONTRACT", "R&D exploration contract", revenue_potential=HIGH, gross_margin=MED,
        repeatability=MED, sales_cycle_short=LOW, scalability=LOW, conflict_low=MED,
        participant_alignment=HIGH, defensibility=MED, capital_light=MED,
        note="Federal hackathon-delivery comps $28K-$2.5M (innovation-budget.md). Bundling predicts 6 figures."),
    "ANNUAL_RETAINER": BusinessModel(
        "ANNUAL_RETAINER", "Annual problem-solving retainer", revenue_potential=HIGH, gross_margin=HIGH,
        repeatability=HIGH, sales_cycle_short=LOW, scalability=MED, conflict_low=HIGH,
        participant_alignment=MED, defensibility=HIGH, capital_light=MED,
        note="Recurring is the margin prize, but requires proven repeatable value first."),
    "RESEARCH_WALLET": BusinessModel(
        "RESEARCH_WALLET", "University-affiliate research wallet", revenue_potential=HIGH, gross_margin=MED,
        repeatability=HIGH, sales_cycle_short=LOW, scalability=MED, conflict_low=HIGH,
        participant_alignment=HIGH, defensibility=MED, capital_light=MED,
        note="Stanford HAI mechanic ($400-800K wallet). Biggest budget line; needs institutional standing."),
    "PE_PORTFOLIO_CONTRACT": BusinessModel(
        "PE_PORTFOLIO_CONTRACT", "PE portfolio-wide operating contract", revenue_potential=HIGH, gross_margin=HIGH,
        repeatability=HIGH, sales_cycle_short=MED, scalability=MED, conflict_low=MED,
        participant_alignment=MED, defensibility=HIGH, capital_light=MED,
        note="One buyer, many portfolio-company problems, repeated. A non-obvious ICP (Phase 20)."),
    "LONGITUDINAL_PANEL_SUBSCRIPTION": BusinessModel(
        "LONGITUDINAL_PANEL_SUBSCRIPTION", "Longitudinal panel subscription", revenue_potential=MED, gross_margin=HIGH,
        repeatability=HIGH, sales_cycle_short=MED, scalability=HIGH, conflict_low=HIGH,
        participant_alignment=MED, defensibility=HIGH, capital_light=MED,
        note="The compounding-moat play, BUT panel retention is UNKNOWN (caveat #6) and standalone intel is weak (caveat #7)."),
    "PROTOTYPE_PROCUREMENT": BusinessModel(
        "PROTOTYPE_PROCUREMENT", "Prototype procurement market", revenue_potential=MED, gross_margin=MED,
        repeatability=MED, sales_cycle_short=MED, scalability=MED, conflict_low=MED,
        participant_alignment=HIGH, defensibility=MED, capital_light=MED,
        note="Corporation runs a mini-market for prototype solutions; artifact value is the product."),
    "TALENT_RECRUITING_ADDON": BusinessModel(
        "TALENT_RECRUITING_ADDON", "Work-evidence recruiting access", revenue_potential=MED, gross_margin=HIGH,
        repeatability=HIGH, sales_cycle_short=MED, scalability=MED, conflict_low=MED,
        participant_alignment=MED, defensibility=MED, capital_light=HIGH,
        note="Proven WTP (RippleMatch ~$69K avg) but FCRA/LL144-constrained: access/subscription only, never a score."),
    "METHODOLOGY_LICENSING": BusinessModel(
        "METHODOLOGY_LICENSING", "License the environment methodology", revenue_potential=MED, gross_margin=HIGH,
        repeatability=HIGH, sales_cycle_short=MED, scalability=HIGH, conflict_low=HIGH,
        participant_alignment=MED, defensibility=LOW, capital_light=HIGH,
        note="Scales, but methodology alone is weakly defensible without the proprietary panel/data."),
    "VENTURE_CREATION_ECONOMICS": BusinessModel(
        "VENTURE_CREATION_ECONOMICS", "Equity / venture creation", revenue_potential=HIGH, gross_margin=HIGH,
        repeatability=LOW, sales_cycle_short=LOW, scalability=LOW, conflict_low=LOW,
        participant_alignment=LOW, defensibility=MED, capital_light=LOW,
        note="venture-upside.md recommends AGAINST equity: four-hats conflict, Carta precedent. Kept for completeness."),
}


def pareto(models=None) -> list:
    """Non-dominated business models over the decomposed vector (higher=better on every DIM)."""
    models = list((models or BUSINESS_MODELS).values())
    def dom(a, b): return all(a.raw()[k] >= b.raw()[k] for k in DIMS) and any(a.raw()[k] > b.raw()[k] for k in DIMS)
    return [m.code for m in models if not any(dom(o, m) for o in models if o.code != m.code)]


def filter_by(min_dims: dict, models=None) -> list:
    """Return model codes meeting every ordinal floor in min_dims, e.g. {'conflict_low': MED,
    'participant_alignment': MED} to exclude extractive/conflicted models."""
    models = models or BUSINESS_MODELS
    out = []
    for code, m in models.items():
        r = m.raw()
        if all(r[k] >= v for k, v in min_dims.items()):
            out.append(code)
    return out


def rational_price_ceiling(decision_value: Belief, p_change: float):
    """The VOI ceiling on price = E[decision value] x P(evidence changes the decision).
    Returns None if the decision value is UNKNOWN — we do NOT invent a price. This is a CEILING,
    not observed WTP (STATE.md); the caller must keep observed WTP UNKNOWN until a signed check."""
    if decision_value is None or decision_value.status == "UNKNOWN":
        return None
    ev = decision_value.mean()
    if ev is None:
        return None
    return float(ev * max(0.0, min(1.0, p_change)))
