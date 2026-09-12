"""
Generative environment design (docs/environment-archetypes.md, docs/discovery-engine.md; Phase 12).

The prior engine could only OPTIMIZE a fixed hackathon (event_optimizer.tweak over an EventDesign).
This module GENERATES environments from scratch for a given problem: it picks an archetype from the
problem's mode, produces configuration variants, scores Fit(P,E) via problem_matcher, and returns the
NON-DOMINATED designs. "A company brings a problem and the engine proposes the environment."

Honesty: the archetype templates are ASSUMED structural priors (which knobs a FORECASTING problem vs
an OPTIMIZATION problem wants), not fitted values. The output is a Pareto set of designs, never a
single "optimal" — the tradeoffs (cost vs behavioral realism vs external validity) stay visible.
"""
from __future__ import annotations
from dataclasses import replace
from environment import Environment
from problem_matcher import match, dominates
from problem_model import Problem

# Archetype templates keyed by problem mode (Phase 6 / Phase 16). Each is a base Environment; the
# generator perturbs a few knobs around it. Talent labels match problem_matcher.COMPONENT_TALENT.
ARCHETYPES = {
    "DIVERGENCE": dict(archetype="INNOVATION_TOURNAMENT", n_participants=180, team_size=3,
                       competition=0.8, interdisciplinarity=0.6, duration_hours=60,
                       talent_mix=(("SOFTWARE", 0.4), ("DESIGN", 0.2), ("PRODUCT", 0.2), ("BUSINESS", 0.2))),
    "DISCOVERY": dict(archetype="OPEN_INNOVATION_CHALLENGE", n_participants=200, team_size=3,
                      competition=0.7, interdisciplinarity=0.7, duration_hours=72,
                      talent_mix=(("SOFTWARE", 0.35), ("DESIGN", 0.2), ("SCIENCE", 0.2), ("BUSINESS", 0.25))),
    "OPTIMIZATION": dict(archetype="OPERATIONS_WAR_ROOM", n_participants=90, team_size=4,
                         data_access=3, instrumentation=3, feedback_cadence=3, market_mechanism="INTERNAL_MARKET",
                         interdisciplinarity=0.5, duration_hours=72,
                         talent_mix=(("OR_IE", 0.4), ("DATA_SCIENCE", 0.3), ("SOFTWARE", 0.3))),
    "EXPERIMENTATION": dict(archetype="PRODUCT_LABORATORY", n_participants=150, team_size=4,
                            instrumentation=3, data_access=2, feedback_cadence=3, competition=0.4,
                            incentive_intensity=0.3, talent_mix=(("SOFTWARE", 0.5), ("DATA_SCIENCE", 0.3), ("DESIGN", 0.2))),
    "PROTOTYPING": dict(archetype="BUILD_SPRINT", n_participants=120, team_size=4, tool_richness=3,
                        data_access=2, duration_hours=72,
                        talent_mix=(("SOFTWARE", 0.6), ("HARDWARE", 0.2), ("DESIGN", 0.2))),
    "FORECASTING": dict(archetype="FORECASTING_TOURNAMENT", n_participants=200, team_size=1,
                        medium="ONLINE", incentive="PEER_PREDICTION", incentive_intensity=0.4,
                        feedback_cadence=3, followup_waves=3, has_continuation=True, duration_hours=336,
                        talent_mix=(("QUANT", 0.4), ("DATA_SCIENCE", 0.3), ("SCIENCE", 0.3))),
    "SIMULATION": dict(archetype="CRISIS_SIMULATION", n_participants=80, team_size=5, data_access=3,
                       instrumentation=3, feedback_cadence=3, market_mechanism="INTERNAL_MARKET",
                       talent_mix=(("OR_IE", 0.35), ("OPERATIONS", 0.3), ("SOFTWARE", 0.35))),
    "RED_TEAMING": dict(archetype="RED_TEAM_ARENA", n_participants=160, team_size=3, competition=0.9,
                        instrumentation=3, talent_mix=(("SOFTWARE", 0.6), ("SCIENCE", 0.2), ("OR_IE", 0.2))),
    "VENTURE_CREATION": dict(archetype="VENTURE_FOUNDRY", n_participants=120, team_size=3,
                             capital_access=3, has_continuation=True, followup_waves=3,
                             incentive="CONTINUATION_CONTRACT", duration_hours=336, competition=0.5,
                             talent_mix=(("SOFTWARE", 0.4), ("BUSINESS", 0.3), ("PRODUCT", 0.3))),
    "MARKET_DESIGN": dict(archetype="MARKET_LABORATORY", n_participants=100, team_size=3,
                          market_mechanism="AUCTION", instrumentation=3, data_access=2, feedback_cadence=3,
                          talent_mix=(("QUANT", 0.4), ("OR_IE", 0.3), ("SOFTWARE", 0.3))),
    "CONVERGENCE": dict(archetype="DESIGN_MARKET", n_participants=120, team_size=3, judging="CUSTOMER_VOTE",
                        competition=0.5, feedback_cadence=3,
                        talent_mix=(("DESIGN", 0.4), ("PRODUCT", 0.3), ("SOFTWARE", 0.3))),
}

# Knob perturbations applied to each base to explore the frontier (label -> field overrides).
VARIANTS = {
    "base": {},
    "in_person": {"medium": "IN_PERSON"},
    "hybrid": {"medium": "HYBRID"},
    "with_panel": {"has_continuation": True, "followup_waves": 3},
    "senior_cohort": {"experience_band": "SENIOR", "selectivity": 0.7},
    "larger": {"n_participants": 300},
    "smaller_deep": {"n_participants": 60, "duration_hours": 240},
}


def archetype_for(problem: Problem) -> Environment:
    """The base environment an engine would reach for given the problem's mode."""
    tmpl = ARCHETYPES.get(problem.mode, ARCHETYPES["DIVERGENCE"])
    return Environment(name=f"{tmpl['archetype'].lower()}_for_{problem.mode.lower()}", **tmpl)


def candidates(problem: Problem):
    """All candidate environments for the problem = the mode archetype x knob variants."""
    base = archetype_for(problem)
    out = []
    for label, changes in VARIANTS.items():
        env = replace(base, name=f"{base.archetype}:{label}", **changes)
        out.append(env)
    return out


def generate(problem: Problem, top: int = 5):
    """Design environments for the problem and return them ranked, with gate + Pareto flags.
    Returns list of dicts sorted by (gate_passed, coverage, on_pareto). Never a single winner."""
    scored = []
    for env in candidates(problem):
        m = match(problem, env)
        scored.append((env.name, env, m))

    # Pareto frontier over the fit vector among gate-passing designs.
    live = [(n, m) for n, e, m in scored if m["gate_passed"]]
    front = set()
    for n, m in live:
        if not any(dominates(m2["fit"], m["fit"]) for n2, m2 in live if n2 != n):
            front.add(n)

    results = []
    for name, env, m in scored:
        results.append({"name": name, "env": env, "match": m,
                        "on_pareto": name in front})
    results.sort(key=lambda r: (r["match"]["gate_passed"], r["on_pareto"],
                                r["match"]["coverage"], r["match"]["env_advantage"]), reverse=True)
    return results[:top]


def best_feasible(problem: Problem):
    """The single highest-coverage gate-passing design, or None if the environment can't clear the
    structural-advantage gate for this problem at all (an honest 'we should not attempt this')."""
    ranked = generate(problem, top=1)
    if ranked and ranked[0]["match"]["gate_passed"]:
        return ranked[0]
    return None
