"""
Team state model (docs/team-rescue/team-state-model.md).

A team is a CHANGING VECTOR, not a score. This module holds the decomposed state, classifies a
team's progress against an archetype-specific expectation envelope (EARLY / ON_TRACK / AT_RISK —
never "good/bad team"), and detects a likely stall from MULTIPLE signals (one signal never
concludes). Milestone velocity is descriptive and compared only within an archetype; it is never
exposed as a ranking.

Two hard rules, enforced here:
  * NO collapsed team score. `TeamState` exposes `.vector()`, not a number. `classify()` returns a
    LABEL derived from the milestone envelope + blocker, for routing support — not for ranking.
  * NO individual score. Contribution is voluntary ownership (see rescue_engine); this module never
    attributes progress to a person. `assert_clean` (live_research) rejects any forbidden field.

Pure stdlib. Part I–II, VI–VIII, XXX, XXXVI of the rescue-engine spec.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from live_research import assert_clean   # reuse the no-person-score / no-protected-trait guard

# The decomposed state vector (Part I). These are the dimension KEYS; we never auto-sum them.
DIMENSIONS = (
    "goal_clarity", "problem_quality", "scope_fit", "capability_coverage", "role_coverage",
    "task_ownership", "technical_progress", "artifact_progress", "blocker_severity", "mentor_need",
    "decision_latency", "team_coordination", "workload_balance", "energy", "confidence",
    "time_remaining", "submission_readiness",
)

LIFECYCLE = ("FORMING", "PLANNING", "BUILDING", "BLOCKED", "PIVOTING", "INTEGRATING",
             "TESTING", "POLISHING", "SUBMISSION_READY", "DONE")

ARCHETYPES = ("AI_APP", "DEVELOPER_TOOL", "HARDWARE", "OPTIMIZATION", "SIMULATION", "DATA_PROJECT",
              "CONSUMER_APP", "RESEARCH_PROTOTYPE", "RD_CHALLENGE", "DESIGN_PROTOTYPE")

# Milestones M0..M8 (Part VI).
MILESTONES = ("M0_team_formed", "M1_problem_selected", "M2_plan", "M3_first_component",
              "M4_core_loop", "M5_integration", "M6_testing", "M7_submission_ready", "M8_demo_ready")

# Expected-progress envelope: for an archetype, the milestone index a TYPICAL team has reached by a
# given fraction of build time. ASSUMPTION-based to start (is_learned=False); replaced by event data.
# (Part VII) — deliberately different shapes: hardware/R&D ramp slower; consumer apps faster early.
_ENVELOPE = {
    "AI_APP":            [(0.25, 2), (0.5, 4), (0.75, 6), (1.0, 7)],
    "DEVELOPER_TOOL":    [(0.25, 2), (0.5, 4), (0.75, 6), (1.0, 7)],
    "CONSUMER_APP":      [(0.25, 3), (0.5, 5), (0.75, 6), (1.0, 8)],
    "HARDWARE":          [(0.25, 1), (0.5, 3), (0.75, 5), (1.0, 7)],
    "OPTIMIZATION":      [(0.25, 2), (0.5, 3), (0.75, 5), (1.0, 7)],
    "SIMULATION":        [(0.25, 2), (0.5, 3), (0.75, 5), (1.0, 7)],
    "DATA_PROJECT":      [(0.25, 2), (0.5, 4), (0.75, 5), (1.0, 7)],
    "RESEARCH_PROTOTYPE":[(0.25, 1), (0.5, 3), (0.75, 4), (1.0, 6)],
    "RD_CHALLENGE":      [(0.25, 1), (0.5, 2), (0.75, 4), (1.0, 6)],
    "DESIGN_PROTOTYPE":  [(0.25, 3), (0.5, 5), (0.75, 6), (1.0, 8)],
}

# Stall signals (Part VIII). A stall is concluded only when >=2 DISTINCT signals co-occur.
STALL_SIGNALS = frozenset({
    "same_blocker_persists", "no_new_artifact", "repeat_mentor_request", "architecture_churn",
    "no_task_ownership", "submission_risk_rising", "self_reported_blocked", "integration_failed",
})
STALL_MIN_SIGNALS = 2


def expected_milestone(archetype: str, time_fraction: float) -> int:
    """The milestone index a typical team of this archetype is expected to have reached by
    `time_fraction` of build time. Interpolates the envelope's steps (floor to the last step ≤ t)."""
    env = _ENVELOPE.get(archetype)
    if not env:
        return 0
    exp = 0
    for frac, ms in env:
        if time_fraction >= frac:
            exp = ms
    return exp


@dataclass
class TeamState:
    team_id: str
    archetype: str
    lifecycle: str
    dims: dict                      # the vector; keys ⊆ DIMENSIONS
    milestone_index: int = 0
    time_fraction: float = 0.0      # fraction of build time elapsed
    signals: frozenset = frozenset()  # active stall signals right now

    def __post_init__(self):
        assert_clean(self.dims)     # no person-score / protected-trait keys may sneak in
        assert "team_score" not in self.dims, "team state is a vector, not a collapsed score (Invariant 1)"

    def vector(self) -> dict:
        """The decomposed state. There is deliberately no scalar summary method."""
        return dict(self.dims)

    def classify(self) -> str:
        """EARLY / ON_TRACK / AT_RISK — a routing LABEL, not a quality ranking. A team ahead of the
        envelope is EARLY (candidate for a side quest); behind-with-a-blocker is AT_RISK."""
        exp = expected_milestone(self.archetype, self.time_fraction)
        blocked = self.lifecycle == "BLOCKED" or self.dims.get("blocker_severity", 0) >= 2
        if self.milestone_index > exp:
            return "EARLY"
        if self.milestone_index < exp or blocked:
            return "AT_RISK"
        return "ON_TRACK"

    def is_stalled(self) -> bool:
        """True only when >=2 distinct stall signals co-occur (Part VIII — one alone never concludes)."""
        return len(self.signals & STALL_SIGNALS) >= STALL_MIN_SIGNALS


def milestone_velocity(milestones_done: int, elapsed_hours: float) -> float:
    """Descriptive: meaningful milestones per build hour. Compare ONLY within an archetype; never
    expose as a cross-team ranking (Part XXXVI). Used to anticipate support need, not to grade."""
    return milestones_done / elapsed_hours if elapsed_hours > 0 else 0.0


def role_coverage(needed: set, owned: set, overloaded: set = frozenset()) -> dict:
    """Coverage only — who is 'better' is never computed (Part XI). Returns covered / missing /
    overloaded capability sets so the rescue engine can route a skill gap."""
    return {
        "covered": sorted(needed & owned),
        "missing": sorted(needed - owned),
        "overloaded": sorted(set(overloaded) & needed),
    }


def ownership_gap(members: set, owners: dict) -> list:
    """Participants with no declared ownership. The TEAM is prompted ('does anyone need a clearer
    workstream?'); we never label an individual a free-rider (Invariant 2, Part XII)."""
    return sorted(m for m in members if not owners.get(m))


def team_state(team_id: str, snapshot: dict) -> TeamState:
    """The required accessor (Part LXVI). Builds the current decomposed state from a snapshot dict
    of {archetype, lifecycle, dims, milestone_index, time_fraction, signals}."""
    return TeamState(
        team_id,
        snapshot.get("archetype", "AI_APP"),
        snapshot.get("lifecycle", "BUILDING"),
        dict(snapshot.get("dims", {})),
        snapshot.get("milestone_index", 0),
        snapshot.get("time_fraction", 0.0),
        frozenset(snapshot.get("signals", ())),
    )
