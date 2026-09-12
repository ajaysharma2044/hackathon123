"""
The PROBLEM primitive (docs/problem-mechanics.md, docs/corporate-problem-universe.md).

Problems are characterized by their MECHANICS, not their industry (Phase 7). "Retail is a good
industry" is a useless statement; "this is a high-parallelizability, high-prototypeability,
low-path-dependence divergence problem owned by a COO with a real budget" is actionable.

Two honesty disciplines carried from the existing engine:
- Economic magnitudes (value of solving, cost of a wrong decision, current spend) are `beliefs.Belief`
  objects with provenance and status. They default to UNKNOWN and CANNOT be fabricated into numbers
  (beliefs.py enforces that UNKNOWN cannot be sampled). This is the STATE.md gating discipline: WTP
  and decision-value stay UNKNOWN until evidenced.
- Structural mechanics are ordinal 0..3 (score.py NONE/LOW/MED/HIGH) and kept as a decomposed VECTOR.

`is_hypothetical=True` quarantines worked-example problems: they are illustrations, NOT market
evidence, and downstream code must never treat them as demand-side proof.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from beliefs import Belief, unknown

# Problem-solving modes (Phase 16 / schema 004 problem_mode). The primary mode routes the problem to
# an environment shape: a DIVERGENCE problem wants many parallel teams; a FORECASTING problem wants a
# prediction tournament; an OPTIMIZATION problem wants OR talent + a simulation.
MODES = ("DIVERGENCE", "CONVERGENCE", "EXPERIMENTATION", "OPTIMIZATION", "DISCOVERY",
         "PROTOTYPING", "FORECASTING", "SIMULATION", "RED_TEAMING", "VENTURE_CREATION",
         "MARKET_DESIGN")

# Ordinal scale (identical to score.py so the two engines interoperate).
NONE, LOW, MED, HIGH = 0, 1, 2, 3
_LABEL = {0: "NONE", 1: "LOW", 2: "MED", 3: "HIGH"}

# The structural mechanics that make up the P vector (Phase 7). Ordinal 0..3 each.
MECHANIC_DIMS = [
    "parallelizability", "prototypeability", "experimentability", "feedback_latency",
    "simulation_feasibility", "behavioral_component", "technical_component", "creative_component",
    "operational_component", "scientific_component", "need_domain_expertise",
    "need_external_perspective", "path_dependence", "internal_political_friction",
    "longitudinal_need", "repeatability",
]


@dataclass
class Problem:
    """An expensive organizational problem, characterized by mechanics. Economic quantities are
    beliefs (default UNKNOWN). See MECHANIC_DIMS for the ordinal fields."""
    statement: str
    industry: str = "UNKNOWN"
    business_unit: str = "UNKNOWN"
    mode: str = "DIVERGENCE"
    decision_owner: str = "UNKNOWN"
    budget_owner: str = "UNKNOWN"
    current_alternative: str = "UNKNOWN"
    missing_evidence: str = ""
    is_hypothetical: bool = False

    # --- structural mechanics (ordinal 0..3) ---
    parallelizability: int = 0
    prototypeability: int = 0
    experimentability: int = 0
    feedback_latency: int = 0            # 0 = slow feedback (bad), 3 = fast (good)
    simulation_feasibility: int = 0
    behavioral_component: int = 0
    technical_component: int = 0
    creative_component: int = 0
    operational_component: int = 0
    scientific_component: int = 0
    need_domain_expertise: int = 0
    need_external_perspective: int = 0
    path_dependence: int = 0             # 0 = low lock-in (good for outsiders), 3 = high (bad)
    internal_political_friction: int = 0 # 0 = low (good), 3 = high (bad)
    longitudinal_need: int = 0
    repeatability: int = 0

    # --- economic magnitudes: beliefs, default UNKNOWN (never fabricated) ---
    economic_value: Belief = field(default=None)     # value of solving it
    cost_of_wrong: Belief = field(default=None)      # cost of a wrong decision (drives VOI ceiling)
    current_cost: Belief = field(default=None)       # what they spend on the current alternative

    def __post_init__(self):
        # Uninitialised economic beliefs are UNKNOWN, not zero. This is the whole point.
        if self.economic_value is None:
            self.economic_value = unknown(f"economic_value[{self.statement[:24]}]",
                                          "no evidence", "value of solving is UNKNOWN until evidenced")
        if self.cost_of_wrong is None:
            self.cost_of_wrong = unknown(f"cost_of_wrong[{self.statement[:24]}]",
                                         "no evidence", "cost of a wrong decision is UNKNOWN")
        if self.current_cost is None:
            self.current_cost = unknown(f"current_cost[{self.statement[:24]}]",
                                        "no evidence", "current spend is UNKNOWN")

    def mechanics(self) -> dict:
        """The decomposed P vector as ordinal labels — never averaged into one number."""
        d = asdict(self)
        return {k: _LABEL[d[k]] for k in MECHANIC_DIMS}

    def mechanics_raw(self) -> dict:
        d = asdict(self)
        return {k: d[k] for k in MECHANIC_DIMS}


# Which environment capabilities each MODE most requires (Phase 16 -> Phase 11). ASSUMED mapping,
# kept explicit and editable. Used by problem_matcher to compute Fit(P,E). Values are the capability
# keys from environment.CAPABILITIES that matter for that mode.
MODE_CAPABILITY_NEEDS = {
    "DIVERGENCE":       ["PARALLEL_SEARCH", "SOLUTION_DIVERSITY", "EXTERNAL_TALENT_ADVANTAGE"],
    "CONVERGENCE":      ["COUNTERFACTUAL_QUALITY", "FEEDBACK_SPEED", "ARTIFACT_VALUE"],
    "EXPERIMENTATION":  ["EXPERIMENTABILITY", "MANIPULABILITY", "OBSERVABILITY", "COUNTERFACTUAL_QUALITY"],
    "OPTIMIZATION":     ["SIMULATION_FEASIBILITY", "PROTOTYPEABILITY", "INTERDISCIPLINARY_ADVANTAGE"],
    "DISCOVERY":        ["SOLUTION_DIVERSITY", "EXTERNAL_TALENT_ADVANTAGE", "PARALLEL_SEARCH"],
    "PROTOTYPING":      ["PROTOTYPEABILITY", "ARTIFACT_VALUE", "TIME_COMPRESSION"],
    "FORECASTING":      ["COUNTERFACTUAL_QUALITY", "OBSERVABILITY", "MANIPULABILITY"],
    "SIMULATION":       ["SIMULATION_FEASIBILITY", "MANIPULABILITY", "EXPERIMENTABILITY"],
    "RED_TEAMING":      ["PARALLEL_SEARCH", "VALUE_OF_FAILURE", "EXTERNAL_TALENT_ADVANTAGE"],
    "VENTURE_CREATION": ["ARTIFACT_VALUE", "LONGITUDINAL_CAPTURE", "EXTERNAL_TALENT_ADVANTAGE"],
    "MARKET_DESIGN":    ["MANIPULABILITY", "SIMULATION_FEASIBILITY", "EXPERIMENTABILITY"],
}


def required_capabilities(problem: Problem) -> list:
    """The environment capabilities this problem most needs = mode needs, augmented by structure.
    E.g. a high-longitudinal-need problem also needs LONGITUDINAL_CAPTURE; a high-parallelizability
    problem also needs PARALLEL_SEARCH. Returns a de-duplicated list."""
    needs = list(MODE_CAPABILITY_NEEDS.get(problem.mode, []))
    if problem.parallelizability >= MED:
        needs.append("PARALLEL_SEARCH")
    if problem.prototypeability >= MED:
        needs.append("PROTOTYPEABILITY")
    if problem.simulation_feasibility >= MED:
        needs.append("SIMULATION_FEASIBILITY")
    if problem.longitudinal_need >= MED:
        needs.append("LONGITUDINAL_CAPTURE")
    if problem.need_external_perspective >= MED:
        needs.append("EXTERNAL_TALENT_ADVANTAGE")
    if problem.experimentability >= MED:
        needs.append("EXPERIMENTABILITY")
    # de-dup, preserve order
    seen, out = set(), []
    for c in needs:
        if c not in seen:
            seen.add(c); out.append(c)
    return out
