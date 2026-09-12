"""
Study portfolio optimization (docs/quant-engine.md, Part 19). The event hosts multiple studies
under finite capacity and hard compatibility constraints. Exact solve by subset enumeration
(study counts are small). More sponsors is NOT automatically better.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import combinations


@dataclass
class Study:
    name: str
    exp_value: float             # expected contribution ($) — from the buyer/pricing model
    info_value: float            # strategic/information value ($-equivalent)
    participant_minutes: float   # research-minute budget consumed
    researcher_hours: float
    category: str                # competitive category (for exclusivity)
    conflicts: set = field(default_factory=set)   # study names that cannot coexist (contamination)


def select(studies, participant_minute_budget, researcher_hour_capacity, info_weight=1.0):
    """Return the highest-value compatible subset satisfying all constraints, and the binding ones."""
    best, best_val, best_binding = [], float("-inf"), []
    names = [s.name for s in studies]
    by_name = {s.name: s for s in studies}
    for r in range(len(studies) + 1):
        for combo in combinations(names, r):
            subset = [by_name[c] for c in combo]
            binding = _violations(subset, participant_minute_budget, researcher_hour_capacity)
            if binding:
                continue
            val = sum(s.exp_value + info_weight * s.info_value for s in subset)
            if val > best_val:
                best, best_val, best_binding = subset, val, _slack(subset, participant_minute_budget, researcher_hour_capacity)
    return {"selected": [s.name for s in best], "value": best_val, "slack": best_binding}


def _violations(subset, pm_budget, rh_cap):
    v = []
    if sum(s.participant_minutes for s in subset) > pm_budget: v.append("participant_minutes")
    if sum(s.researcher_hours for s in subset) > rh_cap: v.append("researcher_hours")
    cats = [s.category for s in subset]
    if len(cats) != len(set(cats)): v.append("category_exclusivity")   # one sponsor per competitive category
    nmeset = {s.name for s in subset}
    for s in subset:
        if s.conflicts & nmeset: v.append(f"conflict:{s.name}")
    return v

def _slack(subset, pm_budget, rh_cap):
    return {"participant_minutes_left": pm_budget - sum(s.participant_minutes for s in subset),
            "researcher_hours_left": rh_cap - sum(s.researcher_hours for s in subset)}
