"""
Trajectories — snapshots become paths (docs/temporal/trajectory.md; Parts XXX, XXXI, XXXVI, XXXVII,
XXXVIII, LXXVII).

A trajectory is tau_i = (S0,A0,S1,A1,...,ST). Two teams that look different at the end may have had
similar journeys; we can compare and (descriptively) cluster journeys into named PROJECT archetypes.
These are TEAM/PROJECT trajectory shapes, NEVER personality categories, and a learning trajectory is
evidence, NEVER an intelligence/IQ inference (participant-controlled, opt-in). Domain trajectories
(learning, venture, R&D, product) are ordered stage lists with timestamps.
"""
from __future__ import annotations

# LXXVII. A trajectory is an alternating state/action sequence.
def trajectory(states, actions=None):
    actions = actions or []
    seq = []
    for i, s in enumerate(states):
        seq.append(("S", s))
        if i < len(actions):
            seq.append(("A", actions[i]))
    return seq

def _states(tau):
    return [v for k, v in tau if k == "S"]

def similarity(tau_a, tau_b):
    """Normalised Levenshtein similarity over the STATE sequences (1.0 == identical path)."""
    a, b = _states(tau_a), _states(tau_b)
    if not a and not b:
        return 1.0
    m, n = len(a), len(b)
    d = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): d[i][0] = i
    for j in range(n + 1): d[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] != b[j-1]))
    return 1 - d[m][n] / max(m, n)

# Named PROJECT-trajectory archetypes (operational shapes, NOT personality types).
PROJECT_ARCHETYPES = ("FAST_STRAIGHT_LINE", "EARLY_FAILURE_SUCCESSFUL_PIVOT", "LATE_COLLAPSE",
                      "MENTOR_DEPENDENT_RECOVERY", "SLOW_START_RAPID_FINISH", "RD_EXPLORER",
                      "OVERSCOPED_CUT_SHIP")
ARCHETYPE_DISCLAIMER = "These describe the PROJECT's path, not the people. Never a personality label."

def classify_archetype(tau):
    """Descriptive, rule-based archetype from the state path — a labelled shape, explicitly not a
    judgement of the team. Returns UNCLASSIFIED when the path doesn't clearly match one."""
    s = _states(tau)
    joined = " ".join(s)
    early = s[:(len(s) + 1) // 2]   # first half, rounded UP so a mid-index blocker counts as early
    if "BLOCKED" in early and "PIVOTING" in s and s[-1] in ("DONE", "SUBMISSION_READY"):
        return {"archetype": "EARLY_FAILURE_SUCCESSFUL_PIVOT", "_note": ARCHETYPE_DISCLAIMER}
    if "MENTOR" in joined and "BLOCKED" in s and s[-1] in ("DONE", "SUBMISSION_READY"):
        return {"archetype": "MENTOR_DEPENDENT_RECOVERY", "_note": ARCHETYPE_DISCLAIMER}
    if s and s[-1] in ("BLOCKED", "PIVOTING") and "SUBMISSION_READY" not in s:
        return {"archetype": "LATE_COLLAPSE", "_note": ARCHETYPE_DISCLAIMER}
    if s[:2] == ["FORMING", "PLANNING"] and s.count("BLOCKED") == 0 and s[-1] == "DONE":
        return {"archetype": "FAST_STRAIGHT_LINE", "_note": ARCHETYPE_DISCLAIMER}
    return {"archetype": "UNCLASSIFIED", "_note": ARCHETYPE_DISCLAIMER}

# Domain trajectory stage templates (ordered). Missing stages are valid; timestamps attach per team.
LEARNING_TRAJECTORY = ("PriorExperience", "FirstExposure", "FirstAttempt", "Failure",
                       "LearningResource", "SuccessfulApplication", "Integration", "Continuation")
VENTURE_TRAJECTORY  = ("Idea", "Prototype", "Demo", "Continued", "Users", "Revenue", "Pivot",
                       "Stopped", "Startup")
RD_TRAJECTORY       = ("Hypothesis", "Experiment", "Failure", "Revision", "SecondExperiment",
                       "Convergence", "Prototype")
PRODUCT_JOURNEY     = ("Aware", "Considered", "Tried", "Activated", "Integrated", "Failed",
                       "ReceivedHelp", "Switched", "Retained")

NO_PERSON_SCORE = ("A learning/capability trajectory is artifact-anchored evidence a participant may "
                   "choose to share. It is NEVER an intelligence, IQ, or general-ability score.")

def stage_timestamps(template, observed):
    """Map a domain template to observed {stage: datetime}; absent stages -> None (missing is valid,
    never back-filled). Returns the ordered, timestamped trajectory."""
    return [{"stage": st, "at": observed.get(st)} for st in template]
