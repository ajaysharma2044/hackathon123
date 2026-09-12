"""
Mechanism design over the multi-sided market (docs/multi-sided/mechanism-design.md). Net-new layer:
HARD participant floors that revenue cannot override, a Pareto frontier over STAKEHOLDER utilities
(not one score), Nash welfare only as a secondary tie-breaker, attention shadow price / value-per-
participant-minute, the frontend-distortion gate, and multi-sided module packing.

Builds ON burden_budget (the minute floor) and value_matrix (U/C). Participant experience is a HARD
CONSTRAINT, never a soft one: a design violating a floor is INFEASIBLE regardless of revenue.
"""
from __future__ import annotations
import math
from value_matrix import U, C, ORD, MECHANICS, STAKEHOLDERS, cross_side_fanout, synergy

# Participant hard floors (Part VIII). A design must satisfy ALL of these to be feasible.
def participant_floor_ok(mechanics: set):
    v = []
    if "open_build_track" not in mechanics:
        v.append("build_freedom: no unconstrained/open-build surface")
    # research burden ceiling: too many burdensome research mechanics
    burdensome = sum(1 for m in ("exit_interview", "checkpoint", "follow_up_30_90") if m in mechanics)
    if burdensome >= 3 and "mentor_request" not in mechanics:
        v.append("research_burden: heavy research load without offsetting participant value")
    if "mentor_request" not in mechanics:
        v.append("mentor_access: no mentor support mechanic")
    # sponsor pressure: a sponsored bounty on top of a keynote with no open track balance
    if "sponsored_bounty_track" in mechanics and "open_build_track" not in mechanics:
        v.append("sponsor_pressure: sponsored track without a free-choice counterweight")
    return (len(v) == 0), v

def stakeholder_utility(mechanics: set) -> dict:
    """Scalar per stakeholder = sum of that side's ordinal utility over included mechanics. The
    decomposed cells stay visible in value_matrix.U; this scalar is ONLY for cross-side comparison."""
    return {s: sum(ORD[U[s][m][0]] for m in mechanics) for s in STAKEHOLDERS}

def pareto_frontier(designs):
    """designs: list of (name, mechanics_set). Non-dominated over stakeholder utility vectors."""
    utils = {n: stakeholder_utility(m) for n, m in designs}
    def dom(a, b): return all(utils[a][s] >= utils[b][s] for s in STAKEHOLDERS) and any(utils[a][s] > utils[b][s] for s in STAKEHOLDERS)
    return [n for n, _ in designs if not any(dom(o, n) for o, _ in designs if o != n)]

def nash_welfare(mechanics: set, floors: dict = None):
    """Secondary tie-breaker ONLY (Part X): sum log(U_s - floor_s). -inf if any side is at/below its
    floor -- which prevents one stakeholder capturing nearly all the benefit. NOT the canonical score."""
    ok, _ = participant_floor_ok(mechanics)
    if not ok:
        return float("-inf")   # participant floor dominates; infeasible
    u = stakeholder_utility(mechanics); floors = floors or {}
    total = 0.0
    for s in STAKEHOLDERS:
        margin = u[s] - floors.get(s, 0)
        if margin <= 0:
            return float("-inf")
        total += math.log(margin)
    return total

def value_per_participant_minute(j):
    """Attention shadow price (Parts XLI-XLII). Positive stakeholder value per unit participant-minute.
    mentor_request should rank far above sponsor_keynote."""
    minutes = {"NONE": 0, "LOW": 1, "MED": 2, "HIGH": 3}[C["participant_minutes"][j]]
    value = sum(ORD[U[s][j][0]] for s in STAKEHOLDERS if ORD[U[s][j][0]] > 0)
    return value / minutes if minutes else float("inf")   # inf = value with ~no attention cost

def frontend_distortion_gate(mechanics: set):
    """Reject designs where a commercial mechanic distorts the participant frontstage / research
    validity beyond bound (Part XLIV; the net-new frontend-distortion gate)."""
    problems = []
    for j in mechanics:
        if C["frontend_distortion"][j] == "HIGH":
            problems.append(f"{j}: HIGH frontend distortion")
    # the specific contamination: sponsored bounty + open build in the SAME free-choice surface
    if "sponsored_bounty_track" in mechanics and "open_build_track" in mechanics:
        if synergy("sponsored_bounty_track", "open_build_track")[0] == "NEG":
            problems.append("sponsored_bounty_track contaminates open_build_track (research validity)")
    return (len(problems) == 0), problems

def optimize_event_portfolio(candidate_mechanics, attention_capacity=8, require_floors=True):
    """Multi-sided packing (Parts XLIII, LXXI): pick the mechanic set maximizing total cross-side value
    subject to the participant floor, the distortion gate, and an attention-capacity cap. Exact over
    subsets (mechanic counts are small). Returns the best feasible set + why others were rejected."""
    from itertools import combinations
    best, best_val = None, float("-inf")
    def attention(m): return sum({"NONE":0,"LOW":1,"MED":2,"HIGH":3}[C["participant_minutes"][x]] for x in m)
    for r in range(1, len(candidate_mechanics) + 1):
        for combo in combinations(candidate_mechanics, r):
            m = set(combo)
            if attention(m) > attention_capacity:
                continue
            if require_floors and not participant_floor_ok(m)[0]:
                continue
            if not frontend_distortion_gate(m)[0]:
                continue
            u = stakeholder_utility(m); val = sum(max(x, 0) for x in u.values())
            if val > best_val:
                best, best_val = m, val
    return {"selected": sorted(best) if best else [], "total_cross_side_value": best_val}

def maximize_for(stakeholder, candidate_mechanics=None):
    """Part LXXII: mechanics with HIGH value for `stakeholder` that DO NOT push participants below the
    floor. Returns the mechanics, ranked -- never a design that harms participants for one side."""
    cands = candidate_mechanics or MECHANICS
    ranked = sorted(cands, key=lambda j: ORD[U[stakeholder][j][0]], reverse=True)
    out = []
    for j in ranked:
        if ORD[U[stakeholder][j][0]] <= 0:
            continue
        # does adding j alone violate the participant floor or distort the frontstage?
        harms_participants = ORD[U["participants"][j][0]] < 0
        distorts = C["frontend_distortion"][j] == "HIGH"
        out.append({"mechanic": j, "value_to_side": U[stakeholder][j][0],
                    "harms_participants": harms_participants, "distorts_frontstage": distorts,
                    "admissible": not (harms_participants and distorts)})
    return out
