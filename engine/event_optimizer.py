"""
Event design as multi-objective stochastic optimization (docs/quant-engine.md Parts 6-8, 20-23;
docs/event-optimizer.md). The event is a DECISION VECTOR. We do NOT collapse the objectives into
one score — we build the Pareto frontier and show the tradeoffs.

CRITICAL HONESTY: the effect coefficients below are ASSUMPTIONS, not measurements. They live in one
ASSUMPTIONS dict so they are obviously assumptions (mirrored in docs/quant-assumptions.md). The value
of this engine is the machinery + the explicit assumption ledger + sensitivity showing which
assumption drives the answer — NOT the specific output numbers. Participant experience is a core
objective, never a soft constraint.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
import numpy as np
from beliefs import scenario, beta
from monte_carlo import simulate, correlated_bernoulli

# ---- ASSUMED effect model (every number here is an assumption; see docs/quant-assumptions.md) ----
A = {
    "exp_base": 5.0,
    "exp_travel_funded": 1.5, "exp_hotel_premium": 1.2, "exp_free_choice": 1.5,
    "exp_mentor_saturation_k": 6.0, "exp_mentor_max": 2.0,
    "exp_social_continuation": 0.6,
    "exp_burden_penalty_per_min_over": 0.06,   # experience lost per research-minute above comfort
    "burden_comfort_minutes": 18.0,            # research-minutes a builder won't notice
    "info_power_exp": 0.5,                      # info ~ n_builders^0.5 (sublinear power)
    "info_free_choice_weight": 1.4,             # unconstrained surface is the unique asset
    "info_minutes_saturation_k": 0.08,
    "info_followup_multiplier": 1.35,           # 90d retention data is the differentiator
    "info_contamination_penalty": 0.5,          # if free_choice too low with many sponsors
    "longterm_panel_base": 1.0,
    "cost_fixed": 120000,                        # venue/ops/staff (ASSUMED)
    "cost_per_builder_base": 350,                # food/materials
    "cost_travel_per_builder": 400, "cost_hotel_premium_per_builder": 600,  # 3 nights
    "cost_per_mentor": 500, "cost_continuation_grants": 50000,
    "wtp_research_elasticity": 0.6, "wtp_mult_floor": 0.55, "wtp_mult_ceiling": 1.9,
    # Scholarship coverage: fraction of travel+hotel funded BY SPONSORS (Reality Hack model, event-comps.md).
    # Ancillary revenue: activation-tier sponsors + logistics recovery (economics.md, logistics-revenue.md).
    "scholarship_band": (0.30, 0.60, 0.90), "ancillary_band": (30000, 80000, 180000),
}

@dataclass(frozen=True)
class EventDesign:
    name: str
    n_builders: int = 200
    duration_h: int = 72
    free_choice_share: float = 0.4        # fraction of building that is unconstrained
    n_research_sponsors: int = 4
    travel_funded: bool = True
    hotel_premium: bool = True
    mentor_ratio: float = 0.1             # mentors per builder
    research_minutes: float = 18.0        # per participant, total, across the event
    followup_90d: bool = True
    continuation_grants: bool = False
    prize_pool: float = 20000


# ---- objective 1: participant experience (0..10), diminishing returns ----
def experience(d: EventDesign) -> float:
    e = A["exp_base"]
    e += A["exp_travel_funded"] * d.travel_funded
    e += A["exp_hotel_premium"] * d.hotel_premium
    e += A["exp_free_choice"] * d.free_choice_share
    e += A["exp_mentor_max"] * (1 - np.exp(-A["exp_mentor_saturation_k"] * d.mentor_ratio))
    e += A["exp_social_continuation"] * d.continuation_grants
    over = max(0.0, d.research_minutes - A["burden_comfort_minutes"])
    e -= A["exp_burden_penalty_per_min_over"] * over
    return float(np.clip(e, 0, 10))

# ---- objective 2: research information value (unitless score) ----
def research_information(d: EventDesign) -> float:
    relevant = d.n_builders * (0.3 + 0.7 * d.free_choice_share)   # unconstrained surface = signal
    power = relevant ** A["info_power_exp"]
    depth = 1 - np.exp(-A["info_minutes_saturation_k"] * d.research_minutes)
    breadth = 1 + 0.25 * (d.n_research_sponsors - 1)
    score = power * (0.5 + 0.5 * depth) * (1 + A["info_free_choice_weight"] * d.free_choice_share) * breadth
    if d.followup_90d: score *= A["info_followup_multiplier"]
    if d.free_choice_share < 0.25 and d.n_research_sponsors >= 4:   # contamination
        score *= A["info_contamination_penalty"]
    return float(score)

# ---- objective 3: economic value (contribution-margin DISTRIBUTION via Monte Carlo) ----
def _buyer_beliefs(close_band, contract_band):
    return {"close": scenario("close", *close_band, "ASSUMED", "no signed deals yet; scenario band"),
            "contract": scenario("contract", *contract_band, "ASSUMED", "the-quote.md ceilings, not observed WTP")}

def _fundable_travel_hotel(d: EventDesign) -> float:
    """The travel+hotel portion sponsors can underwrite via scholarships (the big, offsettable line)."""
    th = 0.0
    if d.travel_funded: th += d.n_builders * A["cost_travel_per_builder"]
    if d.hotel_premium: th += d.n_builders * A["cost_hotel_premium_per_builder"]
    return th

def _fixed_non_travel(d: EventDesign) -> float:
    c = A["cost_fixed"] + d.n_builders * A["cost_per_builder_base"]
    c += d.n_builders * d.mentor_ratio * A["cost_per_mentor"]
    if d.continuation_grants: c += A["cost_continuation_grants"]
    c += d.prize_pool
    return float(c)

def cost(d: EventDesign, scholarship=0.0) -> float:
    """Total organizer cost NET of sponsor-funded scholarships (default: none funded = gross)."""
    return float(_fixed_non_travel(d) + (1 - scholarship) * _fundable_travel_hotel(d))

# Reference design whose research_info anchors the quality->WTP coupling (ASSUMED baseline).
_REF_INFO = None
def _ref_info():
    global _REF_INFO
    if _REF_INFO is None: _REF_INFO = research_information(EventDesign("_ref"))
    return _REF_INFO

def research_quality_multiplier(d: EventDesign) -> float:
    """THE THESIS, made economic: better research (more builders, more free-choice, follow-up) makes
    sponsors pay more. Coupling elasticity is ASSUMED (docs/quant-assumptions.md); clipped so it can
    neither vanish nor explode. This is why flying in 200 builders can beat a cheap 120-person event."""
    return float(np.clip((research_information(d) / _ref_info()) ** A["wtp_research_elasticity"],
                         A["wtp_mult_floor"], A["wtp_mult_ceiling"]))

def economic(d: EventDesign, close_band=(0.10, 0.25, 0.45), contract_band=(40000, 75000, 150000),
             rho=0.3, n=40000, seed=7):
    """Contribution = research-sponsor contracts (quality-scaled) + ancillary revenue
    - (fixed + travel/hotel net of sponsor scholarships). Returns MCResult. All bands ASSUMED."""
    fixed_non_travel = _fixed_non_travel(d)
    fundable = _fundable_travel_hotel(d)
    qmult = research_quality_multiplier(d)
    params = _buyer_beliefs(close_band, contract_band)
    params["scholarship"] = scenario("scholarship", *A["scholarship_band"], "ASSUMED",
                                      "sponsor-funded travel share, Reality Hack model")
    params["ancillary"] = scenario("ancillary", *A["ancillary_band"], "ASSUMED",
                                    "activation sponsors + logistics recovery")
    def model(s, rng):
        k = len(s["close"])
        closes = correlated_bernoulli(np.full(d.n_research_sponsors, s["close"].mean()), k, rho, rng)
        contract = s["contract"] * qmult
        revenue = closes.sum(axis=1) * contract + s["ancillary"]
        net_cost = fixed_non_travel + (1 - s["scholarship"]) * fundable
        return revenue - net_cost
    return simulate(model, params, n=n, seed=seed)

# ---- objective 4: long-term panel/network value (score) ----
def longterm(d: EventDesign) -> float:
    exp = experience(d)
    panel = A["longterm_panel_base"] * (exp / 10.0)
    if d.followup_90d: panel *= 1.4
    if d.continuation_grants: panel *= 1.3
    return float(panel * (d.n_builders ** 0.5))


def objectives(d: EventDesign, econ_kwargs=None):
    econ = economic(d, **(econ_kwargs or {}))
    return {"experience": experience(d), "research_info": research_information(d),
            "econ_mean_contribution": econ.summary()["mean"], "econ_p5": econ.percentile(5),
            "econ_p_breakeven": econ.prob_gt(0), "longterm": longterm(d), "_mc": econ}


def pareto_frontier(design_objs):
    """design_objs: list of (name, {obj->val}) using the 4 headline objectives (higher=better).
    Returns names on the non-dominated frontier."""
    keys = ["experience", "research_info", "econ_mean_contribution", "longterm"]
    def dominates(a, b): return all(a[k] >= b[k] for k in keys) and any(a[k] > b[k] for k in keys)
    front = []
    for name, o in design_objs:
        if not any(dominates(o2, o) for n2, o2 in design_objs if n2 != name):
            front.append(name)
    return front


def tweak(d: EventDesign, **changes):
    """Event Tweak Engine (Part 23): change one knob, return the delta on each objective."""
    base = objectives(d); d2 = replace(d, **changes); new = objectives(d2)
    return {k: round(new[k] - base[k], 3) for k in
            ("experience", "research_info", "econ_mean_contribution", "econ_p_breakeven", "longterm")}


def robust_eval(d: EventDesign):
    """Evaluate economic contribution under bear/base/bull WTP scenarios (Part 21)."""
    scen = {"bear": ((0.05, 0.12, 0.20), (25000, 45000, 75000)),
            "base": ((0.10, 0.25, 0.45), (40000, 75000, 150000)),
            "bull": ((0.20, 0.40, 0.60), (75000, 120000, 250000))}
    out = {}
    for name, (cb, vb) in scen.items():
        mc = economic(d, close_band=cb, contract_band=vb)
        out[name] = {"mean": round(mc.summary()["mean"]), "p_breakeven": round(mc.prob_gt(0), 3),
                     "cvar95": round(mc.cvar(0.95))}
    return out
