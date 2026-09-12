"""
Talent / problem allocation (docs/talent-configuration.md; Phase 14).

Given a problem portfolio, a configured population (teams), and scarce shared resources (mentor
hours, compute), choose how many teams attack each problem to maximize a DECOMPOSED objective —
expected problem value AND solution diversity (parallel search across distinct problems) — subject to
hard capacity constraints.

Two disciplines carried over:
- We allocate at the POPULATION / team level and NEVER score individual humans (Phase 2, and the
  capture-risk-register.md hard boundary "no person scoring").
- Solution diversity is a first-class objective, not a tiebreaker: 20 teams all piling onto one
  problem is usually worse than spreading them (Phase 27: "when are 100 independent solutions worse
  than one expert team?" is exactly the tradeoff this exposes).

Reuses portfolio.select (schema-mirrored) for the coarser "which problems to run at all" decision.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from itertools import product
import portfolio


@dataclass
class ProblemDemand:
    name: str
    value_per_team: float          # expected value contribution per team assigned (from fit/economics)
    mentor_hours_per_team: float = 0.0
    compute_per_team: float = 0.0
    mode: str = "DIVERGENCE"
    max_teams: int = 6             # cap on useful parallel teams (diminishing returns beyond this)


def allocate(demands, n_teams, mentor_capacity, compute_capacity, diversity_weight=1.0):
    """Exact allocation by bounded enumeration (team/problem counts are small). Returns the best
    team assignment, the decomposed objective, and the binding constraints. Diversity is rewarded per
    DISTINCT problem that receives >=1 team, so parallel breadth is valued, not just raw value."""
    demands = list(demands)
    ranges = [range(0, min(d.max_teams, n_teams) + 1) for d in demands]
    best = None
    for combo in product(*ranges):
        if sum(combo) > n_teams:
            continue
        mentor = sum(c * d.mentor_hours_per_team for c, d in zip(combo, demands))
        compute = sum(c * d.compute_per_team for c, d in zip(combo, demands))
        if mentor > mentor_capacity or compute > compute_capacity:
            continue
        value = sum(c * d.value_per_team for c, d in zip(combo, demands))
        diversity = sum(1 for c in combo if c > 0)
        objective = value + diversity_weight * diversity
        if best is None or objective > best["objective"]:
            best = {
                "allocation": {d.name: c for c, d in zip(combo, demands) if c > 0},
                "objective": objective, "value": value, "diversity": diversity,
                "teams_used": sum(combo),
                "mentor_hours_used": mentor, "compute_used": compute,
                "slack": {"teams": n_teams - sum(combo),
                          "mentor_hours": mentor_capacity - mentor,
                          "compute": compute_capacity - compute},
            }
    return best


def select_problems(demands, participant_minute_budget, researcher_hour_capacity,
                    minutes_per_team=600.0):
    """Coarser gate: which problems to run at all, reusing portfolio.select. Each problem becomes a
    portfolio.Study (value=value_per_team, info_value carried as 0 here, one 'category' per mode so
    the same mode isn't double-booked — mirroring one-sponsor-per-competitive-category)."""
    studies = [portfolio.Study(name=d.name, exp_value=d.value_per_team, info_value=0.0,
                               participant_minutes=minutes_per_team,
                               researcher_hours=d.mentor_hours_per_team, category=d.mode)
               for d in demands]
    return portfolio.select(studies, participant_minute_budget, researcher_hour_capacity)


def marginal_value_of_capacity(demands, n_teams, mentor_capacity, compute_capacity,
                               resource="mentor", step=1.0, diversity_weight=1.0):
    """The economic-flow question 'what is the marginal effect of one more mentor hour?' (Phase 15),
    answered by re-solving with +step capacity. Returns the objective delta (>=0)."""
    base = allocate(demands, n_teams, mentor_capacity, compute_capacity, diversity_weight)
    if resource == "mentor":
        bumped = allocate(demands, n_teams, mentor_capacity + step, compute_capacity, diversity_weight)
    elif resource == "compute":
        bumped = allocate(demands, n_teams, mentor_capacity, compute_capacity + step, diversity_weight)
    elif resource == "teams":
        bumped = allocate(demands, n_teams + int(step), mentor_capacity, compute_capacity, diversity_weight)
    else:
        raise ValueError(f"unknown resource {resource!r}")
    if base is None or bumped is None:
        return None
    return round(bumped["objective"] - base["objective"], 4)
