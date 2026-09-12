"""
Tests for the Adaptive Team Performance + Rescue Engine. `python3 engine/test_team_rescue.py`.

Verifies the invariants the spec insists on: team state is a VECTOR not a score, no person score,
multi-signal stall detection, the archetype envelope classification, the monotonic No-Dead-Team
ladder, the scope optimizer both directions, the critical path + next-to-unblock, teams (never
participants) needing help, the fairness floor in allocation, Preventable Blocked Minutes (excluding
informative failure), scenarios-not-certainty, and the performance/research firewall.
"""
from team_state import (TeamState, team_state, expected_milestone, milestone_velocity,
                        role_coverage, ownership_gap, DIMENSIONS)
from critical_path import Task, critical_path, next_to_unblock, bottleneck_capability
from rescue_engine import (diagnose, escalation_level, scope_optimizer, intervention_options,
                           best_support, simulate_intervention, classify_failure, record_outcome)
from event_control import (teams_needing_help, capability_shortages, event_bottlenecks,
                           preventable_blocked_minutes, allocate_resources, output_efficiency,
                           adaptive_schedule)

PASS, FAIL = 0, 0
def check(name, cond):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  PASS  {name}")
    else:    FAIL += 1; print(f"  FAIL  {name}")

def mk(team="t1", arch="AI_APP", life="BUILDING", dims=None, ms=3, tf=0.5, sig=()):
    return TeamState(team, arch, life, dims or {}, ms, tf, frozenset(sig))


# --- no collapsed team score, no person score --------------------------------------------------
def test_state_is_a_vector_not_a_score():
    s = mk(dims={"goal_clarity": 2, "scope_fit": 1})
    check("TeamState exposes a decomposed vector", set(s.vector()) == {"goal_clarity", "scope_fit"})
    check("TeamState has no scalar-score method", not hasattr(s, "score"))
    raised = False
    try:
        mk(dims={"team_score": 5})          # a collapsed score is refused
    except AssertionError:
        raised = True
    check("a collapsed team_score is refused", raised)

def test_no_person_score_in_state():
    for bad in ({"employability_score": 3}, {"personality": "x"}, {"iq": 1}):
        raised = False
        try:
            mk(dims=bad)
        except PermissionError:
            raised = True
        check(f"state carrying {list(bad)[0]} is refused", raised)


# --- envelope classification (EARLY/ON_TRACK/AT_RISK) ------------------------------------------
def test_classify_against_envelope():
    # AI_APP at 50% expects milestone 4.
    check("AI_APP at t=0.5 expects milestone 4", expected_milestone("AI_APP", 0.5) == 4)
    check("ahead of envelope → EARLY", mk(ms=6, tf=0.5).classify() == "EARLY")
    check("on envelope → ON_TRACK", mk(ms=4, tf=0.5).classify() == "ON_TRACK")
    check("behind envelope → AT_RISK", mk(ms=2, tf=0.5).classify() == "AT_RISK")
    check("blocked team is AT_RISK even if on milestone", mk(ms=4, tf=0.5, life="BLOCKED").classify() == "AT_RISK")
    # archetypes differ: R&D ramps slower, so the same milestone/time is not 'behind'
    check("R&D envelope is gentler than AI app at t=0.5",
          expected_milestone("RD_CHALLENGE", 0.5) < expected_milestone("AI_APP", 0.5))


# --- multi-signal stall detection --------------------------------------------------------------
def test_stall_needs_two_signals():
    check("one signal alone is not a stall", not mk(sig={"same_blocker_persists"}).is_stalled())
    check("two distinct signals → stall",
          mk(sig={"same_blocker_persists", "repeat_mentor_request"}).is_stalled())


# --- coverage + ownership (no individual grading) ----------------------------------------------
def test_role_coverage_and_ownership_gap():
    cov = role_coverage({"backend", "ml", "design"}, {"backend", "ml"}, overloaded={"backend"})
    check("missing capability is surfaced", cov["missing"] == ["design"])
    check("overloaded capability is surfaced", cov["overloaded"] == ["backend"])
    gap = ownership_gap({"p1", "p2", "p3"}, {"p1": "backend", "p2": "model"})
    check("ownership gap lists who lacks a workstream (team prompt, not a free-rider label)", gap == ["p3"])


# --- critical path ------------------------------------------------------------------------------
def test_critical_path_and_next_to_unblock():
    tasks = [Task("A", 30, (), "backend", "DONE"), Task("B", 60, ("A",), "ml", "TODO"),
             Task("C", 20, ("A",), "frontend", "TODO"), Task("D", 40, ("B", "C"), "backend", "TODO")]
    path, length = critical_path(tasks)
    check("critical path is the longest-duration chain A→B→D", path == ["A", "B", "D"] and length == 130)
    check("next-to-unblock is the first unfinished critical task (B)", next_to_unblock(tasks) == "B")
    cap, mins = bottleneck_capability(tasks)
    check("bottleneck capability sits on the most critical minutes", cap in ("ml", "backend"))
    raised = False
    try:
        critical_path([Task("X", 1, ("Y",)), Task("Y", 1, ("X",))])
    except ValueError:
        raised = True
    check("a dependency cycle is rejected", raised)


# --- the No-Dead-Team ladder -------------------------------------------------------------------
def test_escalation_ladder_monotonic_and_respects_progress():
    check("a team making progress stays at level 0 even if it reports a blocker",
          escalation_level(3, 200, making_progress=True) == 0)
    l_short = escalation_level(2, 10, False)
    l_long = escalation_level(2, 150, False)
    check("longer blocked time escalates the level", l_long > l_short)
    check("level is capped at 6", escalation_level(3, 9999, False) == 6)
    check("a genuinely blocked team is at least level 1", escalation_level(1, 30, False) >= 1)


# --- diagnosis + scope optimizer ---------------------------------------------------------------
def test_diagnose_and_scope_optimizer():
    d = diagnose(mk(dims={"scope_fit": 1, "blocker_severity": 2}))
    check("diagnosis surfaces both the technical blocker and the scope problem",
          "TECHNICAL_BLOCKER" in d and "SCOPE_PROBLEM" in d)
    over = scope_optimizer(100, 50)
    under = scope_optimizer(20, 80)
    check("over-scoped → reduce/reuse/narrow", over["verdict"] == "OVER_SCOPED" and over["recommendations"])
    check("under-scoped → stretch/extend/test", under["verdict"] == "UNDER_SCOPED" and under["recommendations"])
    check("well-matched → no forced complexity", scope_optimizer(100, 100)["verdict"] == "WELL_MATCHED")
    check("a scope problem routes to SCOPE_RESET, not another mentor",
          best_support(mk(dims={"scope_fit": 1, "blocker_severity": 2}, ms=2, tf=0.6), blocked_minutes=90).action == "SCOPE_RESET")


# --- best_support / options / simulate ---------------------------------------------------------
def test_best_support_and_options_and_sim():
    healthy = mk(ms=5, tf=0.5)                      # EARLY, not stalled
    check("a healthy team gets NOTHING (don't interrupt progress)", best_support(healthy).action == "NOTHING")
    opts = intervention_options(mk(dims={"blocker_severity": 2, "mentor_need": 1}))
    check("options include a mentor path when there's a technical blocker", "MENTOR" in opts)
    sim = simulate_intervention(mk(), "MENTOR")
    check("simulate returns SCENARIOS, never a fake probability",
          sim["calibrated_probability"] is None and len(sim["scenarios"]) >= 2)


# --- failure classification + counterfactual discipline ----------------------------------------
def test_failure_and_counterfactual_discipline():
    check("a preventable cause (missing api key) is PREVENTABLE", classify_failure("missing_api_key") == "PREVENTABLE")
    check("a real algorithm failure is INFORMATIVE (captured, not prevented)",
          classify_failure("algorithm_failed") == "INFORMATIVE")
    rec = record_outcome({"a": 1}, "MENTOR", {"a": 2}, "resolved")
    check("an outcome is recorded as 'preceded', not 'caused'", rec["relationship"] == "intervention_preceded_outcome")
    raised = False
    try:
        record_outcome({}, "MENTOR", {}, "resolved", causal=True)
    except ValueError:
        raised = True
    check("a causal claim from precedence is refused", raised)


# --- the performance/research firewall ---------------------------------------------------------
def test_performance_research_firewall():
    raised = False
    try:
        diagnose(mk(dims={"blocker_severity": 2, "consent_scope": ["X"]}))  # research-grain field
    except PermissionError:
        raised = True
    check("research-grain fields are firewalled out of the rescue engine", raised)


# --- event-wide control ------------------------------------------------------------------------
def test_teams_needing_help_returns_teams_not_people():
    states = [mk("t1", ms=2, tf=0.5), mk("t2", ms=5, tf=0.5), mk("t3", sig={"no_new_artifact", "self_reported_blocked"})]
    need = teams_needing_help(states)
    ids = {r["team_id"] for r in need}
    check("at-risk + stalled teams surface (t1 behind, t3 stalled)", ids == {"t1", "t3"})
    check("the result is teams, with no participant-level field", all(set(r) == {"team_id", "risk", "stalled"} for r in need))

def test_capability_shortages_aggregate():
    states = [mk("t1", ms=2, tf=0.5), mk("t2", ms=2, tf=0.5)]
    short = capability_shortages(states, {"t1": {"backend", "ml"}, "t2": {"backend"}})
    check("backend is the top aggregate shortage", list(short)[0] == "backend" and short["backend"] == 2)

def test_event_bottleneck_is_the_binding_constraint():
    b = event_bottlenecks(demand={"MENTOR:BACKEND": 8, "MENTOR:AI": 6, "GPU": 3},
                          capacity={"MENTOR:BACKEND": 3, "MENTOR:AI": 5, "GPU": 4})
    check("the worst gap (backend mentors) is the top bottleneck", b[0]["resource"] == "MENTOR:BACKEND")
    check("a resource with spare capacity is not a bottleneck", all(x["resource"] != "GPU" for x in b))

def test_preventable_blocked_minutes_excludes_informative():
    logs = [{"minutes": 40, "cause": "DOCUMENTATION"}, {"minutes": 50, "cause": "MENTOR_SHORTAGE"},
            {"minutes": 90, "cause": "INFORMATIVE_FAILURE"}]
    r = preventable_blocked_minutes(logs)
    check("preventable total sums only preventable causes", r["preventable_minutes"] == 90)
    check("informative failure minutes are excluded, not conflated", r["informative_minutes_excluded"] == 90)
    check("recoverable participant-hours reported", r["participant_hours_recoverable"] == 1.5)

def test_allocation_respects_fairness_floor():
    # 5 units, three teams each wanting 3; a commercial-priority team cannot starve the others' floor
    a = allocate_resources(5, {"t1": 3, "t2": 3, "t3": 3}, floor=1, commercial_priority={"t1"})
    check("every team gets at least the floor before surplus", all(a["allocation"][t] >= 1 for t in ["t1", "t2", "t3"]))
    check("commercial priority only orders the surplus (t1 gets the extra)", a["allocation"]["t1"] == 3)
    check("total allocated never exceeds capacity", sum(a["allocation"].values()) == 5)

def test_output_efficiency_is_decomposed():
    oe = output_efficiency({"prototypes": 10, "experiments": 6}, {"mentor_hours": 40, "gpu_hours": 20})
    check("efficiency keeps components, no single score", "per_input_ratio" in oe and "outputs" in oe)

def test_adaptive_schedule():
    recs = adaptive_schedule({"blocked_rate": 0.4, "ahead_rate": 0.1, "energy": 2})
    check("high blocker rate → fewer workshops + a clinic", any("clinic" in r for r in recs))
    check("low energy → a break", any("break" in r for r in recs))


if __name__ == "__main__":
    tests = [test_state_is_a_vector_not_a_score, test_no_person_score_in_state,
             test_classify_against_envelope, test_stall_needs_two_signals,
             test_role_coverage_and_ownership_gap, test_critical_path_and_next_to_unblock,
             test_escalation_ladder_monotonic_and_respects_progress, test_diagnose_and_scope_optimizer,
             test_best_support_and_options_and_sim, test_failure_and_counterfactual_discipline,
             test_performance_research_firewall, test_teams_needing_help_returns_teams_not_people,
             test_capability_shortages_aggregate, test_event_bottleneck_is_the_binding_constraint,
             test_preventable_blocked_minutes_excludes_informative, test_allocation_respects_fairness_floor,
             test_output_efficiency_is_decomposed, test_adaptive_schedule]
    for t in tests:
        print(f"\n{t.__name__}"); t()
    print(f"\n{'='*50}\n{PASS} passed, {FAIL} failed")
    import sys; sys.exit(1 if FAIL else 0)
