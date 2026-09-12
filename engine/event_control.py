"""
Event-wide control (docs/team-rescue/event-control-and-waste.md).

The ORIE layer: find the current binding constraint (Theory of Constraints, Parts LXII–LXIII),
map waste (Part LXI), allocate scarce resources fairly (Parts XVII, LVII, LIX), and track the one
metric Event 1 should obsess over — PREVENTABLE BLOCKED MINUTES (Parts XXXVII, LX). Plus the
required event-level accessors (Part LXVI): teams_needing_help, capability_shortages,
event_bottlenecks.

Two disciplines:
  * TEAMS, NEVER RANKED PARTICIPANTS. `teams_needing_help` returns teams; nothing here ranks people.
  * FAIRNESS FLOOR. Allocation satisfies a per-team minimum before any surplus is prioritized, and a
    commercial client can never buy below-floor priority over basic participant support (Part LVII).

Pure stdlib. Complements engine/event_optimizer.py (which optimizes the event DESIGN, pre-event);
this module runs the event LIVE.
"""
from __future__ import annotations
from dataclasses import dataclass

# Blocked-time causes. Everything except a genuine research failure is PREVENTABLE (Part XXV, XXXVII).
PREVENTABLE_CAUSES = frozenset({"DOCUMENTATION", "TOOL_FAILURE", "MENTOR_SHORTAGE", "CAPABILITY_GAP",
                                "RESOURCE_SHORTAGE", "SCOPE_ISSUE", "OPERATIONS"})
INFORMATIVE_CAUSES = frozenset({"INFORMATIVE_FAILURE"})


def teams_needing_help(states) -> list:
    """Required fn: the teams (NEVER participants) that are AT_RISK or stalled. Returns team_ids with
    their risk label + stall flag so the war room can route support — not a leaderboard."""
    out = []
    for s in states:
        if s.classify() == "AT_RISK" or s.is_stalled():
            out.append({"team_id": s.team_id, "risk": s.classify(), "stalled": s.is_stalled()})
    # order by most-in-need first (AT_RISK + stalled), but this is a support queue, not a ranking of worth
    return sorted(out, key=lambda r: (r["risk"] != "AT_RISK", not r["stalled"], r["team_id"]))


def capability_shortages(states, role_needs: dict) -> dict:
    """Required fn: aggregate missing capabilities across teams needing help. `role_needs` maps
    team_id → set of missing capabilities (from team_state.role_coverage). Returns {capability: count}."""
    need_ids = {r["team_id"] for r in teams_needing_help(states)}
    counts = {}
    for tid in need_ids:
        for cap in role_needs.get(tid, ()):
            counts[cap] = counts.get(cap, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def event_bottlenecks(demand: dict, capacity: dict) -> list:
    """Required fn + Theory of Constraints: the current binding constraints, ranked by how far demand
    exceeds capacity. Returns [{resource, demand, capacity, gap, recommended_action}, ...] worst first."""
    out = []
    for r in set(demand) | set(capacity):
        d, c = demand.get(r, 0), capacity.get(r, 0)
        gap = d - c
        if gap > 0:
            out.append({"resource": r, "demand": d, "capacity": c, "gap": gap,
                        "recommended_action": f"elevate '{r}' (shift capacity in / add office hours)"})
    return sorted(out, key=lambda x: -x["gap"])


def preventable_blocked_minutes(logs) -> dict:
    """THE key Event-1 metric (Part XXXVII). `logs` is a list of {minutes, cause}. Returns the total
    preventable minutes + a breakdown by cause, with informative (real research) failures EXCLUDED —
    we prevent preventable waste and capture informative failure, never conflate them (Part XXV)."""
    total, breakdown, informative = 0, {}, 0
    for l in logs:
        if l["cause"] in INFORMATIVE_CAUSES:
            informative += l["minutes"]
            continue
        total += l["minutes"]
        breakdown[l["cause"]] = breakdown.get(l["cause"], 0) + l["minutes"]
    return {"preventable_minutes": total,
            "by_cause": dict(sorted(breakdown.items(), key=lambda kv: -kv[1])),
            "informative_minutes_excluded": informative,
            "participant_hours_recoverable": round(total / 60, 1)}


def waste_map(items) -> dict:
    """Aggregate the waste map (Part LXI): {kind: total_amount}. `items` is [{kind, amount}]."""
    out = {}
    for i in items:
        out[i["kind"]] = out.get(i["kind"], 0) + i["amount"]
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def output_efficiency(outputs: dict, inputs: dict) -> dict:
    """Conceptual OutputEfficiency = UsefulOutputs / Resources — but kept DECOMPOSED (Part LX). We
    return the components and per-input ratios, never one collapsed magic number."""
    total_out = sum(outputs.values())
    return {"outputs": dict(outputs), "inputs": dict(inputs),
            "per_input_ratio": {k: (round(total_out / v, 3) if v else None) for k, v in inputs.items()},
            "note": "components kept separate; no single efficiency score"}


def allocate_resources(capacity: int, team_requests: dict, floor: int = 1,
                       commercial_priority: set = frozenset()) -> dict:
    """Allocate `capacity` units of a scarce resource across teams. FAIRNESS (Part LVII): every
    requesting team gets the `floor` first; only the SURPLUS is distributed by priority. A commercial
    client cannot buy below-floor priority over basic participant support."""
    teams = list(team_requests)
    alloc = {t: 0 for t in teams}
    remaining = capacity
    # 1) satisfy the floor for every team that needs it, before any prioritization
    for t in teams:
        give = min(floor, team_requests[t], remaining)
        alloc[t] += give; remaining -= give
        if remaining <= 0:
            break
    # 2) distribute surplus — commercial priority MAY order the surplus, never the floor
    order = sorted(teams, key=lambda t: (t not in commercial_priority, t))
    for t in order:
        if remaining <= 0:
            break
        want = team_requests[t] - alloc[t]
        give = min(want, remaining)
        alloc[t] += give; remaining -= give
    return {"allocation": alloc, "unmet": {t: team_requests[t] - alloc[t] for t in teams},
            "floor_guaranteed": floor}


def adaptive_schedule(aggregate: dict) -> list:
    """The schedule itself adapts (Parts XLII–XLIII). `aggregate` carries blocked_rate, ahead_rate,
    energy. Returns recommended adjustments."""
    recs = []
    if aggregate.get("blocked_rate", 0) >= 0.3:
        recs.append("reduce optional workshop programming; run a targeted clinic on the top blocker")
    if aggregate.get("ahead_rate", 0) >= 0.3:
        recs.append("offer advanced side quests / FRONTIER challenge level to teams that are EARLY")
    if aggregate.get("energy", 5) <= 2:
        recs.append("insert a food / social break; energy has crashed")
    return recs or ["no schedule change indicated"]
