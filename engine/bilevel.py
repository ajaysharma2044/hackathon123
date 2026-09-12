"""
Bilevel discovery (docs/discovery-engine.md; Phases 22-23).

    OUTER loop  : which recurring problems are most valuable?
    INNER loop  : for each problem, design the best environment, then decide act-vs-gather-evidence.

Conceptually  ICP*, E* = argmax over (ICP, E) EnterpriseValue(ICP, E), subject to participant
experience / methodological validity / capital / talent / trust. We do NOT force a single scalar
EnterpriseValue: objectives stay separate (Phase 23) and the output is a ranked, Pareto-aware set.

The inner decision reuses voi.py (EVSI / NetVOI). The important honest property: when a problem's
decision value or contract WTP is UNKNOWN (which is almost everything, per STATE.md), the engine
cannot compute a net VOI and therefore recommends GATHER_EVIDENCE — i.e. run the cheap falsification
test before building anything. The machine converges on the same conclusion the human synthesis did,
from the other direction.
"""
from __future__ import annotations
import numpy as np
from environment_generator import best_feasible, generate
from business_model import rational_price_ceiling
from beliefs import Belief
import voi


def recommend_action(decision_value: Belief, contract_value: Belief, close_prior=(1.0, 1.0),
                     pilot_n=8, pilot_cost=10000.0, pursuit_cost=50000.0):
    """Inner VOI decision. Returns (recommendation, detail).
    - If decision value or contract WTP is UNKNOWN -> GATHER_EVIDENCE (cannot value the bet; the
      $5-15K pilot is the highest-VOI move). This is the honest default.
    - Else compute EVSI of an m=pilot_n buyer test on the close-rate and compare to its cost."""
    if (decision_value is None or decision_value.status == "UNKNOWN" or
            contract_value is None or contract_value.status == "UNKNOWN"):
        return ("GATHER_EVIDENCE",
                "WTP/decision value UNKNOWN — run the cheapest falsification test (a $5-15K paid "
                "pilot / 10 buyer interviews) before committing to an environment. (STATE.md gating unknown)")

    cv = contract_value.mean()
    actions = ["act", "abandon"]

    def util(action, theta):
        theta = np.asarray(theta)
        if action == "abandon":
            return np.zeros_like(theta)
        return theta * cv - pursuit_cost      # act: expected contract value at close-rate theta, net of pursuit

    evsi = voi.evsi_beta(close_prior[0], close_prior[1], pilot_n, actions, util)
    net = voi.net_voi(evsi, pilot_cost)
    if net > 0:
        return ("GATHER_EVIDENCE", f"EVSI {evsi:,.0f} exceeds pilot cost {pilot_cost:,.0f} (net {net:,.0f}).")
    # act now vs abandon: expected value of acting at the prior mean close-rate
    prior_mean = close_prior[0] / (close_prior[0] + close_prior[1])
    act_ev = prior_mean * cv - pursuit_cost
    if act_ev > 0:
        return ("ACT_NOW", f"Evidence not worth its cost (net VOI {net:,.0f}); acting is +{act_ev:,.0f} in expectation.")
    return ("ABANDON", f"Evidence not worth its cost and acting is {act_ev:,.0f} in expectation.")


def evaluate_problem(problem, contract_value: Belief = None, close_prior=(1.0, 1.0)):
    """Inner loop for one problem: design the best environment and decide the action.
    Returns a decomposed record (objectives kept separate, never one score)."""
    best = best_feasible(problem)
    ceiling = rational_price_ceiling(problem.cost_of_wrong, p_change=0.3)  # p_change ASSUMED
    action, detail = recommend_action(problem.cost_of_wrong, contract_value, close_prior)
    return {
        "problem": problem.statement,
        "mode": problem.mode,
        "environment_feasible": best is not None,
        "best_environment": (best["name"] if best else None),
        "coverage": (best["match"]["coverage"] if best else 0),
        "external_validity": (best["match"]["fit"]["external_validity"] if best else None),
        "rational_price_ceiling": ceiling,          # None when decision value UNKNOWN (not fabricated)
        "recommended_action": action,
        "action_detail": detail,
    }


def bilevel_search(problems, contract_values=None, close_prior=(1.0, 1.0), top=None):
    """OUTER loop over the problem universe. Ranks by (environment feasible, coverage) — problems
    the environment cannot serve fall to the bottom, honestly. contract_values: optional
    {problem_statement: Belief}. Returns the ranked records; nothing is committed."""
    contract_values = contract_values or {}
    records = [evaluate_problem(p, contract_values.get(p.statement), close_prior) for p in problems]
    records.sort(key=lambda r: (r["environment_feasible"], r["coverage"]), reverse=True)
    return records if top is None else records[:top]
