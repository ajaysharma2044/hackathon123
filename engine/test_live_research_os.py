"""
Cross-cutting tests for the Live Research OS — the correctness properties Part XLII requires:
participant-burden caps, evidence provenance, observation ≠ interpretation, timestamped
interventions, correct question branching (see test_adaptive_questions), adaptive sampling that
preserves negative cases, NO person score, NO protected traits, no raw client access where
prohibited, and consent/revocation rules.

`python3 engine/test_live_research_os.py`.
"""
from datetime import datetime, timedelta

from live_research import (FieldNote, assert_clean, ClientView, LiveResearchOS, Action,
                           DEFAULT_MIN_CELL)
from research_triggers import TriggerRegistry
from burden_budget import BurdenBudget, BurdenExceeded
from adaptive_sampling import Sampler, Candidate, Explanation, DISCONFIRMING
from question_backlog import Backlog, QItem, SATURATED, CONTRADICTED, PRIORITIZED
from team_trajectory import Episode, assemble
from evidence_graph import Claim, EvidenceRef, NegativeCase, Recommendation, SUPPORTS, CONTRADICTS, HIGH
from intervention_log import Intervention, InterventionLog, ValidityViolation, INVALIDATING, OPERATIONAL
from mentor_routing import (Mentor, SupportRequest, route_request, queue_depths, support_intensity,
                            classify_success)

D0 = datetime(2027, 10, 1, 9, 0)
def at(mins): return D0 + timedelta(minutes=mins)
PASS, FAIL = 0, 0
def check(name, cond):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  PASS  {name}")
    else:    FAIL += 1; print(f"  FAIL  {name}")


# --- observation ≠ interpretation ---------------------------------------------------------------
def test_observation_separates_fact_from_interpretation():
    n = FieldNote("o1", "r1", at(0), observed_event="said 'we're wasting time on auth'; removed the SDK ~12 min later",
                  subject_team="t1", direct_quote="we're wasting too much time on auth",
                  researcher_interpretation="auth friction may have driven the switch",
                  alternative_interpretation="teammate already knew the alternative")
    check("a clean field note keeps fact and interpretation in separate fields",
          "auth" in n.observed_event and n.researcher_interpretation != n.observed_event)
    # an interpretation with NO competing reading is rejected (anti-bias)
    raised = False
    try:
        FieldNote("o2", "r1", at(0), observed_event="removed SDK", subject_team="t1",
                  researcher_interpretation="they hated it")
    except ValueError:
        raised = True
    check("a lone interpretation with no alternative is refused", raised)
    # an empty behavioral fact is rejected
    raised2 = False
    try:
        FieldNote("o3", "r1", at(0), observed_event="   ", subject_team="t1")
    except ValueError:
        raised2 = True
    check("an empty observed-fact is refused", raised2)


# --- no person score, no protected traits -------------------------------------------------------
def test_no_person_score_no_protected_traits():
    for bad in [{"person_score": 9}, {"employability_score": 3}, {"personality": "high-O"},
                {"iq": 150}, {"gender": "x"}, {"race": "y"}, {"founder_score": 1}]:
        raised = False
        try:
            assert_clean(dict(bad, team="t1"))
        except PermissionError:
            raised = True
        check(f"record carrying {list(bad)[0]} is refused", raised)
    check("a clean behavioral record passes", assert_clean({"outcome": "shipped", "tool": "X"}) is not None)


# --- client sees aggregate, never raw -----------------------------------------------------------
def test_client_cannot_get_raw_or_small_cells():
    cv = ClientView()
    raised = False
    try:
        cv.refuse_raw({"observation": "a raw note"})
    except PermissionError:
        raised = True
    check("client is refused a raw observation", raised)
    # min-cell suppression on an aggregate
    rows = ([{"tool": "A", "p": f"a{i}"} for i in range(DEFAULT_MIN_CELL)]
            + [{"tool": "B", "p": f"b{i}"} for i in range(3)])
    agg = cv.aggregate(rows, cell_key=lambda r: r["tool"], subject_key=lambda r: r["p"])
    check("cell with n>=min is reported to the client", agg["A"] == DEFAULT_MIN_CELL)
    check("cell with n<min is suppressed", agg["B"] is None)


# --- participant burden cap + rate governor -----------------------------------------------------
def test_burden_cap_and_rate_limit():
    b = BurdenBudget(cap_sec=120, min_gap_sec=1800)
    b.spend("p1", "CHECKPOINT", 60, at(0))
    check("within-budget spend is allowed", b.remaining("p1") == 60)
    raised = False
    try:
        b.spend("p1", "INTERVIEW", 120, at(10))   # would exceed the 120s cap
    except BurdenExceeded:
        raised = True
    check("a spend that would exceed the cap is refused", raised)
    # rate limit: two micro-prompts too close together
    b2 = BurdenBudget(cap_sec=10000, min_gap_sec=2700)
    b2.spend("p2", "MICRO_PROMPT", 20, at(0))
    check("second prompt within the gap is blocked", not b2.can_spend("p2", "MICRO_PROMPT", 20, at(10)))
    check("a prompt after the gap is allowed", b2.can_spend("p2", "MICRO_PROMPT", 20, at(60)))
    # ambient channels never consume the explicit budget
    b3 = BurdenBudget(cap_sec=30)
    b3.spend("p3", "ARTIFACT_SUBMISSION", 999, at(0))
    check("artifact submission does not consume the explicit budget", b3.remaining("p3") == 30)


# --- the live loop respects timing + budget -----------------------------------------------------
def test_live_loop_stays_silent_when_it_should():
    b = BurdenBudget(cap_sec=10000)
    os_ = LiveResearchOS(TriggerRegistry(), b, interrupt_state=lambda team, now: "DO_NOT_INTERRUPT")
    a = os_.observe_then_decide({"trigger_type": "SWITCH", "subject_team": "t1", "subject_participant": "p1"}, at(0))
    check("a switch during a heads-down window is NOT interrupted", a.kind == "SILENT")
    os2 = LiveResearchOS(TriggerRegistry(), b, interrupt_state=lambda team, now: "MICRO_PROMPT_OK")
    a2 = os2.observe_then_decide({"trigger_type": "SWITCH", "subject_team": "t1", "subject_participant": "p1"}, at(0))
    check("the same switch at an OK moment fires a prompt", a2.kind == "FIRE_PROMPT")
    a3 = os2.observe_then_decide({"trigger_type": "HELP_REQUEST", "subject_team": "t1", "subject_participant": "p1"}, at(1))
    check("a help request is left to the mentor note", a3.kind == "MENTOR_NOTE_SUFFICIENT")


# --- adaptive sampling preserves negative cases -------------------------------------------------
def test_sampling_seeks_disconfirming_cases_first():
    b = BurdenBudget()
    s = Sampler(b, at(0))
    ex = Explanation("auth friction drives abandonment", confirming_segment="ABANDONER",
                     confirming_n=3, disconfirming_n=0, target_each=3)     # confirming full, disconfirming empty
    cands = [Candidate("pA", "t1", frozenset({"ABANDONER"})),
             Candidate("pB", "t2", frozenset({DISCONFIRMING["ABANDONER"]}))]  # SUCCESSFUL_TEAM
    plan = s.suggest_next([ex], cands)
    check("sampler schedules a DISCONFIRMING case before more confirming ones", plan.polarity == "DISCONFIRM")
    check("the disconfirming pick is the right counter-segment", plan.segment == DISCONFIRMING["ABANDONER"])


def test_sampling_is_burden_aware_and_not_extractive():
    b = BurdenBudget(cap_sec=100)
    b.spend("pA", "INTERVIEW", 60, at(0))     # pA is now over half the budget
    s = Sampler(b, at(0))
    ex = Explanation("x", confirming_segment="ADOPTER", confirming_n=0, disconfirming_n=5, target_each=3)
    cands = [Candidate("pA", "t1", frozenset({"ADOPTER"}))]   # only candidate is over-burdened
    plan = s.suggest_next([ex], cands)
    check("sampler will not re-tap an over-burdened participant", plan is None)


# --- question backlog lifecycle -----------------------------------------------------------------
def test_backlog_lifecycle_and_emergence():
    bl = Backlog()
    bl.add(QItem("q1", "why choose X over Y?", priority=3))
    bl.add_emergent("q14", "why do experienced users ignore starter templates?", at(300))
    check("emergent question is first-class and tracked", bl.items["q14"].is_emergent)
    bl.transition("q1", "PRIORITIZED"); bl.transition("q1", "ANSWERED_PARTIALLY"); bl.transition("q1", SATURATED)
    check("a saturated question leaves the active sampling set", "q1" not in {i.question_id for i in bl.top(10)})
    # an illegal jump is refused (q14 is PRIORITIZED; PRIORITIZED->OPEN is not allowed)
    raised = False
    try:
        bl.transition("q14", "OPEN")
    except ValueError:
        raised = True
    check("an illegal lifecycle transition is refused", raised)
    # a contradiction reopens a saturated question
    bl.contradict("q1")
    check("contradiction reopens a saturated question", bl.items["q1"].status == CONTRADICTED
          and "q1" in {i.question_id for i in bl.top(10)})


# --- team trajectory: provenance required, re-derivable -----------------------------------------
def test_trajectory_requires_provenance_and_is_rederivable():
    eps = [Episode(1, "PROBLEM_SELECTED", behavior="picked fraud detection", observation_ids=("o1",)),
           Episode(2, "SWITCH", behavior="A→B", explanation="teammate knew B", evidence_event_ids=("e9",))]
    t1 = assemble("t1", list(reversed(eps)), "assembler.v1")
    check("assembly orders episodes by seq regardless of input order",
          [e.seq for e in t1.episodes] == [1, 2])
    t2 = assemble("t1", eps, "assembler.v1")
    check("assembly is re-derivable (same story twice)", t1.story() == t2.story())
    raised = False
    try:
        assemble("t2", [Episode(1, "BLOCKER", behavior="stuck")], "assembler.v1")  # no provenance
    except ValueError:
        raised = True
    check("an episode with no provenance is rejected", raised)


# --- evidence graph: provenance + anti-confirmation-bias promotion gate --------------------------
def test_claim_cannot_promote_without_disconfirmation_search():
    c = Claim("c1", "auth friction is associated with early abandonment for first-timers")
    c.add_evidence(EvidenceRef(SUPPORTS, "observation", "o1"))
    ok, why = c.can_promote()
    check("a claim with support but no negative-case search cannot promote", not ok and "negative" in why.lower())
    c.negative_cases.append(NegativeCase("find first-timers who hit auth friction but stayed", "SUCCESSFUL_TEAM", found=None))
    check("an OPEN negative-case search still blocks promotion", not c.can_promote()[0])
    c.negative_cases[0].found = False       # searched, no counterexample
    ok2, _ = c.can_promote()
    check("with support + a completed disconfirmation search, the claim can promote", ok2)
    check("claim trace exposes supporting, contradicting, and negative-case search", "negative_cases" in c.trace())


def test_contradicting_evidence_caps_confidence_and_recs_need_a_basis():
    c = Claim("c2", "pricing complaints predict churn", confidence=HIGH)
    c.add_evidence(EvidenceRef(CONTRADICTS, "interview_excerpt", "x1"))
    check("a contradicting item drops an over-high claim to MED", c.confidence == "MED")
    raised = False
    try:
        Recommendation("do the thing", "big implication")   # no claim_id or finding_id
    except ValueError:
        raised = True
    check("a recommendation cannot float free of a claim/finding", raised)


# --- interventions are timestamped; the study spine is protected --------------------------------
def test_interventions_timestamped_and_spine_protected():
    raised = False
    try:
        Intervention("i0", occurred_at="sometime", reason="x", evidence="y",
                     affected_population="all", change="z", target="office_hours")
    except ValueError:
        raised = True
    check("an intervention without a real timestamp is refused", raised)

    log = InterventionLog()
    log.log(Intervention("i1", at(600), "12 teams stuck on DB setup", "mentor queue DB depth=12",
                         "all DB-track teams", "added 2 DB mentors", target="mentor_allocation",
                         validity_impact=OPERATIONAL, research_questions_affected=("q_db",)))
    check("a legal operational adaptation is logged", len(log.all()) == 1)
    check("before/after split point is recoverable", log.split_point("q_db") == at(600))
    # a locked-knob change without pre-specification is refused
    blocked = False
    try:
        log.log(Intervention("i2", at(700), "raise credit to boost usage", "low activation",
                             "treatment arm", "credit 100->250", target="credit_amount",
                             validity_impact=OPERATIONAL))
    except ValidityViolation:
        blocked = True
    check("changing a locked treatment mid-study (not pre-specified) is refused", blocked)
    # pre-specified spine change is allowed but forced to INVALIDATING honesty
    iv = log.log(Intervention("i3", at(800), "planned dose-ramp", "protocol step 2",
                              "treatment arm", "credit ramp", target="credit_amount",
                              validity_impact=OPERATIONAL, pre_specified=True))
    check("a pre-specified spine change is labelled INVALIDATING, not hidden", iv.validity_impact == INVALIDATING)


# --- mentor routing + the success confounder ----------------------------------------------------
def test_mentor_routing_and_confounder():
    mentors = [Mentor("m1", "DB", active_load=2), Mentor("m2", "DB", active_load=0),
               Mentor("m3", "GENERAL"), Mentor("mc", "DB", is_company_engineer=True, affiliation="SponsorX")]
    req = SupportRequest("req1", "t1", "database", at(0))
    chosen = route_request(req, mentors)
    check("a database problem routes to a DB mentor", chosen.category == "DB")
    check("routing picks the least-loaded mentor", chosen.mentor_id == "m2")
    reqs = [SupportRequest("r1", "t1", "database", at(0), resolution_state="UNRESOLVED"),
            SupportRequest("r2", "t2", "auth", at(1), resolution_state=None),
            SupportRequest("r3", "t3", "database", at(2), resolution_state="RESOLVED")]
    depths = queue_depths(reqs)
    check("queue depths count only open requests per category", depths.get("DB") == 1 and depths.get("BACKEND") == 1)
    # intensity + organic-vs-assisted separation, with no causal claim
    check("no mentor touch → NONE intensity", support_intensity(0, 0, False) == "NONE")
    check("long company-engineer rescue → HEAVY", support_intensity(40, 4, True) == "HEAVY")
    lab = classify_success("shipped_with_X", "HEAVY", is_company_engineer=True)
    check("heavy vendor help is labelled VENDOR_RESCUED, separated from organic", lab.label == "VENDOR_RESCUED_SUCCESS")
    check("the success label carries an explicit non-causal caveat", "not a causal" in lab.caveat)
    organic = classify_success("shipped_with_X", "LIGHT", is_company_engineer=True)
    check("light help counts as organic success", organic.label == "ORGANIC_SUCCESS")


if __name__ == "__main__":
    tests = [test_observation_separates_fact_from_interpretation, test_no_person_score_no_protected_traits,
             test_client_cannot_get_raw_or_small_cells, test_burden_cap_and_rate_limit,
             test_live_loop_stays_silent_when_it_should, test_sampling_seeks_disconfirming_cases_first,
             test_sampling_is_burden_aware_and_not_extractive, test_backlog_lifecycle_and_emergence,
             test_trajectory_requires_provenance_and_is_rederivable,
             test_claim_cannot_promote_without_disconfirmation_search,
             test_contradicting_evidence_caps_confidence_and_recs_need_a_basis,
             test_interventions_timestamped_and_spine_protected, test_mentor_routing_and_confounder]
    for t in tests:
        print(f"\n{t.__name__}"); t()
    print(f"\n{'='*50}\n{PASS} passed, {FAIL} failed")
    import sys; sys.exit(1 if FAIL else 0)
