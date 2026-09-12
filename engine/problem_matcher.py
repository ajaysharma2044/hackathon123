"""
Problem x Environment matching (docs/problem-environment-fit.md; Phase 11).

Fit(P,E) is computed on DECOMPOSED dimensions and gated by a HARD structural-advantage test, exactly
as score.py gates on HackathonAdvantage: a large budget or a big decision CANNOT rescue a problem the
environment holds no real advantage on. If a consulting team / university lab / the company's own
staff would do it as well, Fit is killed regardless of the other dimensions.

The gate generalizes score.py's `hackathon_advantage = min(naturalness, blind_spot)`: here the
environment must clear an ordinal FLOOR on EVERY capability the problem's mode essentially requires.
Miss one -> KILL. Fit dimensions are never averaged into a single number; `coverage` is only a
ranking aid, not a collapse.
"""
from __future__ import annotations
from environment import Environment, capability_vector
from problem_model import (Problem, required_capabilities, MODE_CAPABILITY_NEEDS,
                           NONE, LOW, MED, HIGH, _LABEL)

# Below this ordinal advantage on an essential capability, the (problem, environment) pair is killed.
FIT_ADVANTAGE_FLOOR = MED

# Which talent labels each problem component wants (ASSUMED, explicit). Used for talent_match.
COMPONENT_TALENT = {
    "technical_component":   {"SOFTWARE", "ML_RESEARCH", "DATA_SCIENCE", "HARDWARE"},
    "creative_component":    {"DESIGN", "PRODUCT"},
    "operational_component": {"OR_IE", "OPERATIONS", "SUPPLY_CHAIN"},
    "scientific_component":  {"ML_RESEARCH", "SCIENCE", "QUANT"},
}


def _talent_match(problem: Problem, env: Environment) -> int:
    """Ordinal 0..3: does the configured population supply the disciplines the problem's dominant
    components need? Population-level only (Phase 2) — we never score individuals. Also charges for
    domain expertise the cohort likely lacks (a student-elite cohort's structural weakness)."""
    labels = {lbl for lbl, share in env.talent_mix if share > 0}
    raw = problem.mechanics_raw()
    wants, have = set(), 0
    total = 0
    for comp, needed_labels in COMPONENT_TALENT.items():
        if raw[comp] >= MED:
            total += 1
            if labels & needed_labels:
                have += 1
            wants |= needed_labels
    base = HIGH if total == 0 else int(round(HIGH * have / total))
    # domain-expertise gap: if the problem needs deep domain knowledge and the cohort is junior/elite
    # students, dock the match (STATE.md: lack of domain expertise can destroy value).
    if raw["need_domain_expertise"] >= MED and env.experience_band in ("STUDENT", "EARLY"):
        base = max(NONE, base - 1)
    return int(max(NONE, min(HIGH, base)))


def match(problem: Problem, env: Environment) -> dict:
    """Return the decomposed Fit(P,E): the fit dimensions, the gate result, and a verdict.
    Never collapses the fit dimensions into one score."""
    cap = capability_vector(env)
    gating = MODE_CAPABILITY_NEEDS.get(problem.mode, [])
    env_advantage = min((cap[c] for c in gating), default=NONE)  # min => one weak essential kills it
    gate_passed = env_advantage >= FIT_ADVANTAGE_FLOOR

    needed = required_capabilities(problem)
    coverage = sum(1 for c in needed if cap.get(c, 0) >= MED)

    fit = {
        "parallel_search_advantage": cap["PARALLEL_SEARCH"],
        "talent_match": _talent_match(problem, env),
        "behavioral_realism": cap["BEHAVIORAL_REALISM"],
        "observability": cap["OBSERVABILITY"],
        "prototype_value": cap["PROTOTYPEABILITY"],
        "counterfactual_quality": cap["COUNTERFACTUAL_QUALITY"],
        "external_validity": cap["EXTERNAL_VALIDITY"],
    }

    if not gate_passed:
        verdict = (f"KILL — environment holds no structural advantage on the essential capability "
                   f"'{_weakest(cap, gating)}' (would be done as well by an existing substitute)")
    elif fit["talent_match"] < LOW:
        verdict = "KILL — configured talent cannot supply the problem's dominant components"
    elif coverage >= max(2, len(needed) - 1):
        verdict = "STRONG_FIT — environment covers the problem's required capabilities"
    elif coverage >= 1:
        verdict = "MODERATE_FIT — partial capability coverage"
    else:
        verdict = "WEAK_FIT — gate cleared but little capability coverage"

    return {"fit": fit, "gate_passed": gate_passed, "env_advantage": env_advantage,
            "coverage": coverage, "needed_capabilities": needed, "verdict": verdict}


def _weakest(cap: dict, gating: list) -> str:
    if not gating:
        return "NONE_REQUIRED"
    return min(gating, key=lambda c: cap.get(c, 0))


def dominates(a: dict, b: dict) -> bool:
    """Pareto dominance over the 7 fit dimensions (higher = better)."""
    keys = list(a.keys())
    return all(a[k] >= b[k] for k in keys) and any(a[k] > b[k] for k in keys)


def pareto_frontier(matches: list) -> list:
    """matches: list of (name, match_result). Returns names whose fit vector is non-dominated among
    the gate-passing pairs. A large budget cannot put a dominated (or killed) pair on the frontier."""
    live = [(n, m) for n, m in matches if m["gate_passed"]]
    front = []
    for n, m in live:
        if not any(dominates(m2["fit"], m["fit"]) for n2, m2 in live if n2 != n):
            front.append(n)
    return front
