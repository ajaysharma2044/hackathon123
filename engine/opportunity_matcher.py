"""
GAP x MONEY x FIT opportunity matching (docs/high-value-gap-ranking.md, docs/demand-shaped-event.md).

Fuses a spending war (spend_intensity.SpendCategory) with a structural gap (gap_finder.StructuralGap)
and the environment fit into a single Opportunity whose 12 dimensions are kept DECOMPOSED — the
message's explicit rule: "Do not hide weak dimensions inside a single composite score."

Hard gates (the message's "a top prospect should generally satisfy ..."):
  - HIGH-ish existing spend      (there must already be a spending war)
  - HIGH gap severity            (a real "cannot buy today")
  - HIGH hackathon advantage     (we structurally win at filling it)
  - identifiable buyer authority (someone can sign)
  - adequate participant fit     (never turn the event into unpaid consulting labor)
Miss a gate -> the opportunity is not live, regardless of how big the market is.

Demand-shaped event design (Phase: DEMAND-SHAPED EVENT DESIGN): the environment is derived FROM the
winning gap (environment_generator), not designed independently — but ParticipantExperience remains a
hard constraint that the demand cannot override.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from spend_intensity import SpendCategory, EVIDENCE_ORDER
from gap_finder import StructuralGap
from environment_generator import best_feasible

NONE, LOW, MED, HIGH = 0, 1, 2, 3
_LABEL = {0: "NONE", 1: "LOW", 2: "MED", 3: "HIGH"}

OPP_DIMS = ["economic_intensity", "existing_spend", "competitive_intensity", "problem_severity",
            "gap_severity", "hackathon_advantage", "buyer_authority", "budget_accessibility",
            "decision_urgency", "execution_feasibility", "participant_fit", "repeatability"]


@dataclass
class Opportunity:
    label: str
    category_code: str
    gap_code: str
    buyer: str = ""
    best_environment: str = ""
    business_model: str = ""
    evidence_strength: str = "HYPOTHETICAL"
    # 12 decomposed dims (ordinal 0..3)
    economic_intensity: int = NONE
    existing_spend: int = NONE
    competitive_intensity: int = NONE
    problem_severity: int = NONE
    gap_severity: int = NONE
    hackathon_advantage: int = NONE
    buyer_authority: int = NONE
    budget_accessibility: int = NONE
    decision_urgency: int = NONE
    execution_feasibility: int = NONE
    participant_fit: int = NONE
    repeatability: int = NONE

    def vector(self) -> dict:
        d = asdict(self)
        return {k: _LABEL[d[k]] for k in OPP_DIMS}

    def raw(self) -> dict:
        d = asdict(self)
        return {k: d[k] for k in OPP_DIMS}

    @property
    def is_live(self) -> bool:
        r = self.raw()
        return (r["existing_spend"] >= MED and r["gap_severity"] >= MED and
                r["hackathon_advantage"] >= MED and r["buyer_authority"] >= LOW and
                r["participant_fit"] >= MED)

    def verdict(self) -> str:
        r = self.raw()
        if r["existing_spend"] < MED:
            return "SKIP — no active spending war (nobody is already spending aggressively here)"
        if r["gap_severity"] < MED:
            return "SKIP — no real structural gap (a substitute already covers it)"
        if r["hackathon_advantage"] < MED:
            return "SKIP — no structural advantage (an existing method fills the gap as well)"
        if r["buyer_authority"] < LOW:
            return "SKIP — no identifiable buyer who can sign"
        if r["participant_fit"] < MED:
            return "SKIP — would be extractive / poor participant experience (hard constraint)"
        return "LIVE — spending war + real gap + structural advantage + a buyer + a fair participant deal"


def evaluate(label, category: SpendCategory, gap: StructuralGap, buyer="", business_model="",
             buyer_authority=NONE, budget_accessibility=NONE, execution_feasibility=NONE,
             participant_fit=NONE, repeatability=NONE, best_environment="") -> Opportunity:
    """Assemble an Opportunity from a spending war + a structural gap + hand-assessed access/feasibility
    dims. Spend/intensity dims are pulled from the category; gap dims from the gap. Evidence strength
    is the WEAKER of the two sources (you cannot be more confident than your weakest input)."""
    ev = min([category.evidence_strength, gap.evidence_strength], key=lambda s: EVIDENCE_ORDER.index(s))
    return Opportunity(
        label=label, category_code=category.code, gap_code=gap.code, buyer=buyer,
        business_model=business_model, best_environment=best_environment, evidence_strength=ev,
        economic_intensity=category.economic_value,
        existing_spend=(HIGH if category.spend_is_evidenced and category.competitive_intensity >= MED
                        else category.competitive_intensity),
        competitive_intensity=category.competitive_intensity,
        problem_severity=category.cost_of_failure,
        gap_severity=gap.gap_severity,
        hackathon_advantage=min(category.hackathon_fit, gap.hackathon_advantage),
        buyer_authority=buyer_authority, budget_accessibility=budget_accessibility,
        decision_urgency=category.decision_urgency, execution_feasibility=execution_feasibility,
        participant_fit=participant_fit, repeatability=repeatability,
    )


def rank(opportunities) -> list:
    """Rank opportunities LIVE-first, then evidence-first, then by the decomposed intensity tuple.
    Never a single collapsed score; weak dimensions stay visible in .vector()."""
    def key(o: Opportunity):
        return (o.is_live, EVIDENCE_ORDER.index(o.evidence_strength),
                o.existing_spend, o.gap_severity, o.hackathon_advantage, o.economic_intensity)
    return sorted(opportunities, key=key, reverse=True)


def dominates(a: Opportunity, b: Opportunity) -> bool:
    ra, rb = a.raw(), b.raw()
    return all(ra[k] >= rb[k] for k in OPP_DIMS) and any(ra[k] > rb[k] for k in OPP_DIMS)


def pareto(opportunities) -> list:
    live = [o for o in opportunities if o.is_live]
    return [o.label for o in live if not any(dominates(x, o) for x in live if x.label != o.label)]


def demand_shaped_environment(problem):
    """Derive the environment FROM demand (the winning gap's problem), not independently. Returns the
    best feasible environment design + the standing reminder that participant experience is a hard
    constraint the demand cannot override."""
    best = best_feasible(problem)
    return {
        "problem": problem.statement,
        "required_environment": (best["name"] if best else None),
        "feasible": best is not None,
        "hard_constraint": "ParticipantExperience — the event must remain one of the best builder "
                           "experiences available; demand cannot turn it into unpaid consulting labor.",
    }
