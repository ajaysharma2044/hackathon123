"""
Tests for the event-operations engines: the staffing model, the judging assignment + stack-rank
scoring, and the role-correlation graph. `python3 engine/test_event_ops.py`.
"""
from staffing_model import plan, judges_needed, COMMITTEE_UNITS
from judging_assignment import (Submission, Judge, assign_science_fair, assign_category,
                                stack_rank_batch, aggregate, judges_needed as jn)
from org_graph import event1_graph, OrgGraph, CROSS_LAYER_KINDS

PASS, FAIL = 0, 0
def check(name, cond):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  PASS  {name}")
    else:    FAIL += 1; print(f"  FAIL  {name}")


# --- staffing model -----------------------------------------------------------------------------
def test_judge_formula_matches_mlh_reference():
    # MLH reference: 175 projects, 2h window, n=3, t=4 → 18 judges.
    check("MLH 175-project reference yields 18 judges",
          judges_needed(175, rounds=3, minutes=4, window_min=120) == 18)
    check("no projects → no judges", judges_needed(0) == 0)


def test_staffing_scales_and_warns():
    p = plan(180)
    roles = p.by_role()
    check("180 builders → ~45 teams", p.teams == 45)
    check("mentors derived at 1:10", roles["Mentors"] == 18)
    check("field researchers derived at ~1:28", roles["Field researchers"] == 7)
    check("exactly one data steward", roles["Data steward"] == 1)
    check("all committee units have a head", roles["Organizer committee heads"] == len(COMMITTEE_UNITS))
    # a tiny event should warn about thin research coverage
    small = plan(20)
    check("a 20-person event flags single-researcher risk",
          any("field researcher" in w for w in small.warnings))
    big = plan(260)
    check("above ~200 the bear-case warning fires", any("bear case" in w for w in big.warnings))


def test_staffing_is_overridable():
    p = plan(100, cfg={"mentor_ratio": 5})
    check("a denser mentor ratio override is honored", p.by_role()["Mentors"] == 20)


# --- judging assignment -------------------------------------------------------------------------
def _subs(n, tag=None):
    return [Submission(f"s{i}", f"t{i}", frozenset({tag}) if tag else frozenset()) for i in range(n)]

def test_science_fair_coverage_and_balance():
    subs = _subs(9)
    judges = [Judge(f"j{k}") for k in range(6)]
    asn = assign_science_fair(subs, judges, rounds=3)
    check("every submission is seen exactly `rounds` times", all(len(v) == 3 for v in asn.values()))
    check("no submission is judged by the same judge twice", all(len(set(v)) == 3 for v in asn.values()))
    # load balance: total assignments = 9*3 = 27 spread over 6 judges → max-min small
    load = {}
    for v in asn.values():
        for j in v: load[j] = load.get(j, 0) + 1
    check("judge load is balanced (max-min ≤ 1)", max(load.values()) - min(load.values()) <= 1)


def test_conflicted_judge_never_sees_own_team():
    subs = _subs(4)
    # j0 is conflicted on t0 (mentored them); there must be enough other judges
    judges = [Judge("j0", conflict_team_ids=frozenset({"t0"})),
              Judge("j1"), Judge("j2"), Judge("j3")]
    asn = assign_science_fair(subs, judges, rounds=3)
    check("a conflicted judge is never assigned their own team's submission",
          "j0" not in asn["s0"])


def test_impossible_coverage_raises():
    subs = _subs(2)
    judges = [Judge("j0", conflict_team_ids=frozenset({"t0"})), Judge("j1")]  # only 2 judges, rounds=3
    raised = False
    try:
        assign_science_fair(subs, judges, rounds=3)
    except ValueError:
        raised = True
    check("too few non-conflicted judges for the rounds → raises", raised)


def test_category_round_uses_expertise():
    subs = _subs(3, tag="AI") + _subs(2)  # 3 AI-tagged, 2 untagged
    judges = [Judge("a1", expertise=frozenset({"AI"})), Judge("a2", expertise=frozenset({"AI"})),
              Judge("a3", expertise=frozenset({"AI"}))]
    asn = assign_category(subs, judges, "AI", rounds=2)
    check("category round only judges tagged submissions", set(asn) == {"s0", "s1", "s2"})


def test_stack_rank_normalizes_and_aggregates():
    # a strict judge and a lenient judge would differ on absolute scores; stack-rank only cares order
    strict = stack_rank_batch(["sB", "sA", "sC"])   # ranks B>A>C
    lenient = stack_rank_batch(["sA", "sB", "sD"])  # ranks A>B>D
    check("top of a batch gets 3 points", strict["sB"] == 3 and lenient["sA"] == 3)
    check("4th+ place gets 0", stack_rank_batch(["s1", "s2", "s3", "s4"]).get("s4", 0) == 0)
    ranked = aggregate([strict, lenient])
    # A: 2+3=5, B: 3+2=5, C:1, D:1 → A and B tie at top (A first by id tiebreak)
    check("aggregate sums points across judges", dict(ranked)["sA"] == 5 and dict(ranked)["sB"] == 5)
    check("aggregate returns a deterministic ranked list", ranked[0][0] in ("sA", "sB"))


# --- org correlation graph ----------------------------------------------------------------------
def test_graph_reports_chain_and_escalation():
    g = event1_graph()
    chain = g.reports_chain("Field Researcher")
    check("a field researcher's report chain reaches the Research Director",
          "Research Director" in chain)
    esc = g.escalation_path("Volunteer")
    check("a volunteer's escalation path reaches Safety then the Event Director",
          "Safety Lead" in esc and esc[-1] == "Event Director")


def test_graph_feeds_research_is_the_sensor_network():
    g = event1_graph()
    feeders = {src for src, _ in g.feeds_research()}
    for role in ["Mentor", "Field Researcher", "Judge", "Registration/Check-in"]:
        check(f"{role} feeds the research layer", role in feeders)


def test_graph_cross_layer_and_constraints():
    g = event1_graph()
    xl = g.cross_layer_edges()
    check("cross-layer edges exist (ops↔research interlock)", len(xl) > 0)
    check("all cross-layer edges are of a cross-layer kind", all(e.kind in CROSS_LAYER_KINDS for e in xl))
    # mentors are constrained by the burden budget + consent gate
    constrained = [e.dst for e in g.out_edges("Mentor", "CONSTRAINED_BY")]
    check("mentors are constrained by the burden/consent rules", any("Budget" in d for d in constrained))


def test_graph_criticality_surfaces_key_roles():
    g = event1_graph()
    top = [r for r, _ in g.criticality()[:5]]
    check("the Event Director is among the most-connected (critical) roles", "Event Director" in top)


if __name__ == "__main__":
    tests = [test_judge_formula_matches_mlh_reference, test_staffing_scales_and_warns,
             test_staffing_is_overridable, test_science_fair_coverage_and_balance,
             test_conflicted_judge_never_sees_own_team, test_impossible_coverage_raises,
             test_category_round_uses_expertise, test_stack_rank_normalizes_and_aggregates,
             test_graph_reports_chain_and_escalation, test_graph_feeds_research_is_the_sensor_network,
             test_graph_cross_layer_and_constraints, test_graph_criticality_surfaces_key_roles]
    for t in tests:
        print(f"\n{t.__name__}"); t()
    print(f"\n{'='*50}\n{PASS} passed, {FAIL} failed")
    import sys; sys.exit(1 if FAIL else 0)
