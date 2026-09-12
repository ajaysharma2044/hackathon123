"""
Temporal resource allocation (docs/temporal/allocation.md; Parts XXXIX, XL, XLII, XLIV, XLVI).

Participant minutes are the scarcest, most perishable resource. Ledgers track four minute-budgets;
each REUSES burden_budget.BurdenBudget (the participant-minute floor), so temporal allocation cannot
silently breach the experience floor. A 20-minute workshop can cost more than 20 minutes because it
interrupts flow (recovery time). Resources should MOVE across event phases (morning team-formation
mentors -> mid technical specialists -> late deploy/demo support). Critical-path finds the tasks whose
delay delays the most downstream work.
"""
from __future__ import annotations
from burden_budget import BurdenBudget, BurdenExceeded

class MinuteLedger:
    """A generic capacity pool of minutes for a SUPPLY side (mentor/researcher/engineer). spend()
    RAISES when over capacity rather than clamping — a full pool is a real constraint, not a rounding
    error. The participant ledger is deliberately NOT this: it is the richer burden_budget.BurdenBudget
    (the experience floor), so participant time cannot be treated as just another pool."""
    def __init__(self, capacity_minutes):
        self.capacity = capacity_minutes
        self.spent = 0.0
    def spend(self, minutes, what=""):
        if self.spent + minutes > self.capacity:
            raise BurdenExceeded(f"{what}: {minutes}min exceeds remaining {self.remaining()}min")
        self.spent += minutes
        return self
    def remaining(self):
        return max(0.0, self.capacity - self.spent)

def make_ledgers(participant_research_cap_sec, mentor_minutes, researcher_minutes, engineer_minutes):
    """XXXIX. Four minute-ledgers. The PARTICIPANT ledger is a real BurdenBudget (research-burden floor
    with channels + rate governor — reused, not reinvented); the three supply pools are MinuteLedgers.
    This keeps the participant floor structurally distinct from ordinary capacity."""
    return {
        "participant": BurdenBudget(cap_sec=participant_research_cap_sec),   # the floor
        "mentor":      MinuteLedger(mentor_minutes),
        "researcher":  MinuteLedger(researcher_minutes),
        "engineer":    MinuteLedger(engineer_minutes),
    }

def interruption_cost(direct_minutes, recovery_minutes=None):
    """XL. True time cost of an interrupting activity = direct + recovery-of-flow. recovery_minutes is
    UNKNOWN until measured — when None, we say so rather than assuming zero (which would undercount)."""
    if recovery_minutes is None:
        return {"direct": direct_minutes, "recovery": "UNKNOWN", "total": "UNKNOWN",
                "_note": "flow-recovery time not yet measured; do not assume it is zero"}
    return {"direct": direct_minutes, "recovery": recovery_minutes,
            "total": direct_minutes + recovery_minutes}

def time_budget_pack(modules, capacity):
    """XLII. Pick modules maximizing value subject to TEMPORAL capacity (team-hours, attention-minutes,
    mentor-hours). modules: list of {name, value, costs:{resource:amount}}. capacity: {resource:amount}.
    Greedy by value-per-scarcest-cost; honest, not claimed-optimal."""
    remaining = dict(capacity); chosen = []
    def fits(m): return all(remaining.get(r, 0) >= a for r, a in m["costs"].items())
    for m in sorted(modules, key=lambda m: m["value"] / (1 + sum(m["costs"].values())), reverse=True):
        if fits(m):
            for r, a in m["costs"].items():
                remaining[r] -= a
            chosen.append(m["name"])
    return {"selected": chosen, "remaining_capacity": remaining}

def reallocation_schedule(demand_by_phase):
    """XLVI. Where support should be over event time. demand_by_phase: {phase:{resource:demand}}.
    Returns the dominant need per phase — resources MOVE, they are not parked for visibility."""
    return {phase: (max(d, key=d.get) if d else None) for phase, d in demand_by_phase.items()}

def critical_path(tasks):
    """XLIV. Longest dependency chain by duration. tasks: {name:{'dur':minutes,'deps':[names]}}.
    Returns the path and its length — the tasks whose slip slips everything downstream."""
    memo = {}
    def longest(n):
        if n in memo: return memo[n]
        deps = tasks[n]["deps"]
        base = tasks[n]["dur"]
        if not deps:
            memo[n] = (base, [n]); return memo[n]
        best = max((longest(d) for d in deps), key=lambda x: x[0])
        memo[n] = (base + best[0], best[1] + [n]); return memo[n]
    end = max(tasks, key=lambda n: longest(n)[0])
    length, path = longest(end)
    return {"critical_path": path, "length_minutes": length}
