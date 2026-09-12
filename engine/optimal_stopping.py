"""
Optimal stopping — continue vs pivot / kill vs fund (docs/temporal/optimal-stopping.md; Parts XVII, XVIII).

A stuck team faces: keep trying or pivot now? Continue while E[value of another attempt] > E[value of
pivoting now]. R&D faces the same shape: continue a failing path, kill it, or fund an alternative. We
do NOT bake in magic thresholds — the probabilities and values are the caller's estimates, and when
they are unknown the engine REFUSES to decide (returns INPUTS_UNKNOWN) rather than inventing a number.
The engine's job now is to collect the data that will eventually let these functions be learned.
"""
from __future__ import annotations

INPUTS_UNKNOWN = {"decision": "INPUTS_UNKNOWN",
                  "_note": "supply estimated p_success/values; before Event 1 data these are UNKNOWN, "
                           "and the honest output is 'insufficient basis to decide', not a threshold"}

def should_continue(p_success_next, value_success, value_pivot_now, attempt_cost):
    """Continue-vs-pivot. EV_continue = p*value_success - attempt_cost (+ keep pivot option on failure);
    EV_pivot = value_pivot_now. Any None input -> INPUTS_UNKNOWN. Returns the decision AND both EVs so
    the reasoning is transparent, never a bare verdict."""
    if None in (p_success_next, value_success, value_pivot_now, attempt_cost):
        return INPUTS_UNKNOWN
    ev_continue = p_success_next * value_success + (1 - p_success_next) * value_pivot_now - attempt_cost
    ev_pivot = value_pivot_now
    return {"decision": "CONTINUE" if ev_continue > ev_pivot else "PIVOT",
            "ev_continue": ev_continue, "ev_pivot": ev_pivot,
            "margin": ev_continue - ev_pivot,
            "_note": "inputs are estimates; decision is only as good as they are"}

def rd_path_decision(p_success_current, value_success, cost_to_continue,
                     best_alternative_value, cost_to_switch):
    """R&D three-way: CONTINUE current path, KILL it, or FUND_ALTERNATIVE. Same expected-value logic
    (Part XVII). None inputs -> INPUTS_UNKNOWN."""
    if None in (p_success_current, value_success, cost_to_continue, best_alternative_value, cost_to_switch):
        return INPUTS_UNKNOWN
    ev_continue = p_success_current * value_success - cost_to_continue
    ev_alternative = best_alternative_value - cost_to_switch
    ev_kill = 0.0
    best = max([("CONTINUE", ev_continue), ("FUND_ALTERNATIVE", ev_alternative), ("KILL", ev_kill)],
               key=lambda kv: kv[1])
    return {"decision": best[0], "ev_continue": ev_continue, "ev_alternative": ev_alternative,
            "ev_kill": ev_kill}
