"""
The rescue engine (docs/team-rescue/rescue-policy.md).

Given a team's state, decide how to help — the No-Dead-Team ladder (Part III), diagnosis (Part IX),
the scope optimizer (Part V), quick wins (Part XXII), pivot/submission/demo support, and the
required accessor functions (Part LXVI). Support is a sequential decision problem
(state → intervention → next state → outcome); this module is the INITIAL, human-reviewed policy.
Contextual bandits / RL are explicitly deferred until multi-event data exists (Parts XXXIV–XXXV).

Disciplines enforced here:
  * COUNTERFACTUAL HONESTY — an intervention result is reported as "preceded resolution", never
    "caused" it (Part LVI). `record_outcome` refuses a causal flag.
  * PERFORMANCE/RESEARCH FIREWALL — rescue consumes OPERATIONAL team state only; it rejects a state
    carrying research-sourced or person-level fields (Part XLVI, and assert_clean from live_research).
  * SCENARIOS, NOT CERTAINTY — `simulate_intervention` returns a range of outcomes, never a single
    fake probability (Parts XXXI–XXXII).

Pure stdlib. Reuses mentor_routing for the mentor-dispatch actions.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from live_research import assert_clean, FORBIDDEN_KEYS
from team_state import TeamState

# Diagnosis taxonomy (Part IX).
DIAGNOSES = ("TECHNICAL_BLOCKER", "SCOPE_PROBLEM", "TEAM_ROLE_GAP", "COORDINATION",
             "PRODUCT_CONFUSION", "DEPENDENCY_FAILURE", "RESOURCE_SHORTAGE", "MOTIVATION",
             "DOMAIN_KNOWLEDGE", "OTHER")

# The No-Dead-Team escalation ladder (Part III). Monotonic: higher = more intervention.
LADDER = {
    0: "no action — team is making progress",
    1: "suggest a relevant resource / docs",
    2: "route a mentor",
    3: "route a SPECIALIST mentor",
    4: "short team diagnosis (a researcher/organizer sits with them ~5 min)",
    5: "scope reduction / architecture reset",
    6: "team restructuring / optional merge (voluntary)",
}

# Fields that must never reach the rescue engine (research/individual grain) — firewall (Part XLVI).
RESEARCH_ONLY_FIELDS = frozenset({"consent_scope", "interview_excerpt", "qual_id", "finding_id",
                                  "claim_id", "participant_id"})


def _firewall(state_dims: dict):
    assert_clean(state_dims)                       # no person score / protected trait
    bad = RESEARCH_ONLY_FIELDS & set(state_dims)
    if bad:
        raise PermissionError(
            f"rescue uses OPERATIONAL team state only; research-grain fields {sorted(bad)} are "
            f"firewalled out (team-rescue/firewalls-and-ethics.md)")


def escalation_level(blocker_severity: int, blocked_minutes: int, making_progress: bool) -> int:
    """Map (severity, duration, progress) → a ladder level. A team MAKING PROGRESS stays at 0 even
    if it briefly reports a blocker — we never interrupt working teams (Part III)."""
    if making_progress:
        return 0
    sev = max(0, min(3, blocker_severity))          # 0..3
    # duration escalates the response: the longer blocked, the higher we climb
    dur = 0 if blocked_minutes < 20 else 1 if blocked_minutes < 60 else 2 if blocked_minutes < 120 else 3
    level = min(6, max(1, sev + dur))               # at least 1 once genuinely blocked
    return level


def diagnose(state: TeamState) -> list:
    """Infer likely blocker type(s) from the decomposed vector. Returns an ordered list (most likely
    first); never a single opaque verdict."""
    _firewall(state.dims)
    d = state.dims
    out = []
    if d.get("blocker_severity", 0) >= 2:
        out.append("TECHNICAL_BLOCKER")
    if d.get("scope_fit", 2) <= 1:
        out.append("SCOPE_PROBLEM")
    if d.get("role_coverage", 2) <= 1 or d.get("capability_coverage", 2) <= 1:
        out.append("TEAM_ROLE_GAP")
    if d.get("team_coordination", 2) <= 1 or d.get("decision_latency", 0) >= 2:
        out.append("COORDINATION")
    if d.get("goal_clarity", 2) <= 1 or d.get("problem_quality", 2) <= 1:
        out.append("PRODUCT_CONFUSION")
    if d.get("energy", 3) <= 1 or d.get("confidence", 3) <= 1:
        out.append("MOTIVATION")
    return out or ["OTHER"]


def scope_optimizer(required_work: float, feasible_work: float) -> dict:
    """RequiredWork vs FeasibleWork (Part V). Over-scoped → cut/reuse/narrow/reset; under-scoped →
    stretch/extend/test. Never forces complexity for its own sake."""
    if feasible_work <= 0:
        return {"verdict": "UNKNOWN", "recommendations": []}
    ratio = required_work / feasible_work
    if ratio > 1.3:
        return {"verdict": "OVER_SCOPED",
                "recommendations": ["reduce features", "use an existing component", "narrow the problem",
                                    "change architecture", "build the core proof first"]}
    if ratio < 0.7:
        return {"verdict": "UNDER_SCOPED",
                "recommendations": ["a harder technical extension", "a better evaluation",
                                    "a real user test", "a stronger artifact", "additional functionality"]}
    return {"verdict": "WELL_MATCHED", "recommendations": []}


def quick_win(blocker_desc: str) -> str:
    """The smallest demonstrable success to restore momentum (Part XXII): e.g. 'one successful tool
    call' before 'full agent workflow'. Returns a suggestion string."""
    return (f"Find the smallest demonstrable success inside '{blocker_desc}': get ONE end-to-end "
            f"slice working (a single call / one record / one screen), then build outward.")


def pivot_support(state: TeamState) -> dict:
    """Decision support for continue-vs-pivot (Part XXIII) — the FACTORS, not a fake universal
    threshold. The team decides; we lay out the trade-off."""
    d = state.dims
    return {
        "factors": {
            "time_remaining": d.get("time_remaining"),
            "blocker_severity": d.get("blocker_severity"),
            "artifact_already_built": d.get("artifact_progress"),
            "motivation": min(d.get("energy", 3), d.get("confidence", 3)),
        },
        "note": "decision support only — the team chooses; there is no universal pivot threshold",
    }


def submission_risk(checklist: dict) -> dict:
    """Operational submission risk (Part LI) — which required pieces are missing. `checklist` maps
    piece→bool (present). Returns the missing set + a risk label, so reminders are specific not spam."""
    required = ("repo", "deploy_or_demo", "core_functionality", "submission_form")
    missing = [k for k in required if not checklist.get(k)]
    risk = "HIGH" if len(missing) >= 2 else "MED" if missing else "LOW"
    return {"missing": missing, "risk": risk}


def intervention_options(state: TeamState) -> list:
    """Required fn (Part LXVI): the support actions available for this state, low→high."""
    _firewall(state.dims)
    opts = ["NOTHING", "RESOURCE"]
    diags = diagnose(state)
    if "TECHNICAL_BLOCKER" in diags or state.dims.get("mentor_need", 0) >= 1:
        opts += ["MENTOR", "SPECIALIST"]
    if "SCOPE_PROBLEM" in diags:
        opts += ["SCOPE_RESET", "QUICK_WIN"]
    if "TEAM_ROLE_GAP" in diags:
        opts += ["REMATCH", "CHALLENGE_LEVEL"]
    if "MOTIVATION" in diags:
        opts += ["QUICK_WIN", "BREAK"]
    return list(dict.fromkeys(opts))     # de-dup, preserve order


@dataclass
class Recommendation:
    action: str
    level: int
    reason: str
    evidence: dict                    # the decomposed state that motivated it (status, not a claim)


def best_support(state: TeamState, blocked_minutes: int = 0) -> Recommendation:
    """Required fn (Part LXVI): the recommended intervention + evidence/status. Bottleneck-first —
    weighs blocker severity, blocked time, and time remaining — never a causal promise."""
    _firewall(state.dims)
    if state.classify() != "AT_RISK" and not state.is_stalled():
        return Recommendation("NOTHING", 0, "team is EARLY/ON_TRACK and not stalled", state.vector())
    level = escalation_level(state.dims.get("blocker_severity", 0), blocked_minutes,
                             making_progress=False)
    diags = diagnose(state)
    action = {0: "NOTHING", 1: "RESOURCE", 2: "MENTOR", 3: "SPECIALIST",
              4: "DIAGNOSIS", 5: "SCOPE_RESET", 6: "REMATCH"}[level]
    if "SCOPE_PROBLEM" in diags and level < 5:
        action = "SCOPE_RESET"        # scope problems are not fixed by another mentor
    return Recommendation(action, level, f"diagnosis={diags}; blocked {blocked_minutes}m", state.vector())


def classify_failure(cause: str) -> str:
    """PREVENTABLE vs INFORMATIVE failure (Part XXV). We prevent the first and CAPTURE the second —
    an algorithm that genuinely doesn't work is valuable research, not an operations failure."""
    informative = {"algorithm_failed", "hypothesis_failed", "architecture_underperformed",
                   "simulation_disproved_approach"}
    return "INFORMATIVE" if cause in informative else "PREVENTABLE"


def simulate_intervention(state: TeamState, intervention: str) -> dict:
    """Required fn (Part LXVI): return SCENARIOS, not certainty (Parts XXXI–XXXII). Until multi-event
    data exists we cannot give a calibrated probability, so we return a qualitative range + what we'd
    need to learn a real one."""
    return {
        "intervention": intervention,
        "scenarios": ["best: blocker clears, team re-enters BUILDING",
                      "likely: blocker eased, some time already lost",
                      "worst: blocker is deeper than diagnosed; escalate a level"],
        "calibrated_probability": None,   # UNKNOWN — never fabricated
        "to_learn_it": "requires state→intervention→outcome logged across multiple events",
    }


def record_outcome(state_before: dict, intervention: str, state_after: dict, outcome: str,
                   causal: bool = False) -> dict:
    """Log the loop for learning (Part LV). Refuses a causal claim from mere precedence (Part LVI)."""
    if causal:
        raise ValueError("counterfactual discipline: record that the intervention PRECEDED the "
                         "outcome; causal claims require an experiment/quasi-experiment (Part LVI)")
    return {"state_before": state_before, "intervention": intervention, "state_after": state_after,
            "outcome": outcome, "relationship": "intervention_preceded_outcome"}
