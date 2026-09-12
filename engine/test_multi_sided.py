"""python3 test_multi_sided.py — the Part-LXXIX guardrail suite for the multi-sided market layer."""
import value_matrix as vm
import mechanism_design as md
import multiuse_assets as ma
from mutual_intro import IntroRequest, release_contact
from compliance import assert_not_a_person_score, assert_no_sensitive
from opportunity_market import dedup_revenue
P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# 1. Participant floor CANNOT be overridden by revenue.
sponsor_max = {"sponsor_keynote", "sponsored_bounty_track", "workshop"}   # high sponsor value, NO open build
ok, viol = md.participant_floor_ok(sponsor_max)
ck("revenue-max design missing open-build VIOLATES participant floor", not ok and len(viol) > 0)
ck("floor-violating design is infeasible (nash = -inf) regardless of sponsor value",
   md.nash_welfare(sponsor_max) == float("-inf"))
good = {"open_build_track", "mentor_request", "demo", "brokered_key_use"}
ck("a floor-respecting design is feasible", md.participant_floor_ok(good)[0])

# 2. Mutual opt-in required for any individual contact release.
req = IntroRequest(scope="EMPLOYER", counterparty="AcmeCo", subject_id="p1", subject_visible=False)
try:
    release_contact(req, "p1@x.com"); ck("contact released without opt-in", False)
except PermissionError:
    ck("contact NOT released without mutual opt-in", True)
req2 = IntroRequest(scope="EMPLOYER", counterparty="AcmeCo", subject_id="p1", subject_visible=True).accept()
ck("contact released after mutual opt-in", release_contact(req2, "p1@x.com") == "p1@x.com")

# 3. No hidden hiring / VC person scores.
for bad in ("candidate_score", "founder_quality", "employability_score", "hireability"):
    try:
        assert_not_a_person_score(bad); ck(f"person score {bad} allowed", False)
    except ValueError:
        ck(f"person score '{bad}' refused", True)

# 4. No unauthorized cross-purpose data use (individual reuse needs the exact opt-in scope).
ck("employer cannot reuse a repo as individual work-evidence without opt-in",
   not ma.rights_ok("project_repo", "employers", set()))
ck("employer CAN reuse it with the recruiting opt-in", ma.rights_ok("project_repo", "employers", {"RECRUITING_DISCOVERABILITY"}))
ck("product client reuses repo aggregate without individual opt-in (aggregate grain)",
   ma.rights_ok("project_repo", "product_clients", set()))

# 5. No double-counting revenue: one contract Shapley-split sums to the present-component share once.
att, total = ma.attribute_revenue(90000, {"artifact", "interview"}, {"artifact", "interview", "mentor_log", "followup"})
ck("Shapley attributes only present components, summing once", abs(total - 45000) < 1 and att["mentor_log"] == 0.0)
ck("dedup_revenue counts each economic id once",
   dedup_revenue([{"id": "d1", "amount": 50000}, {"id": "d1", "amount": 50000}, {"id": "d2", "amount": 20000}]) == 70000)

# 6. Frontend-distortion / research-validity contamination enforced.
ok_g, probs = md.frontend_distortion_gate({"sponsored_bounty_track", "open_build_track"})
ck("sponsored bounty contaminating open-build is rejected by the distortion gate", not ok_g)

# 7. Attention capacity enforced in packing.
sel = md.optimize_event_portfolio({"mentor_request", "demo", "open_build_track", "exit_interview", "sponsor_keynote"}, attention_capacity=3)
tot_att = sum({"NONE":0,"LOW":1,"MED":2,"HIGH":3}[md.C["participant_minutes"][m]] for m in sel["selected"])
ck("packed portfolio respects the attention-capacity cap", tot_att <= 3)
ck("packed portfolio still satisfies the participant floor", md.participant_floor_ok(set(sel["selected"]))[0] or sel["selected"] == [])

# 8. Attention shadow price: mentor help >> sponsor keynote in value per participant-minute.
ck("mentor_request has far higher value-per-minute than sponsor_keynote",
   md.value_per_participant_minute("mentor_request") > md.value_per_participant_minute("sponsor_keynote"))

# 9. High cross-side fan-out mechanic (multi-use) identified.
ck("demo creates value for many sides (>=6)", vm.cross_side_fanout("demo")["count"] >= 6)
ck("sponsor_keynote harms participants (negative cell)", "participants" in vm.cross_side_fanout("sponsor_keynote")["sides_harmed"])

# 10. WTP stays UNKNOWN.
ck("analyze_mechanic states WTP is UNKNOWN", "UNKNOWN" in vm.analyze_mechanic("demo")["unknowns"])

# 11. Protected/sensitive attributes never accepted in a schema (distinct guard from person-scores).
try:
    assert_no_sensitive(["name", "email", "age"]); ck("sensitive attr accepted", False)
except ValueError:
    ck("protected attribute (age) refused in schema", True)

# 12. Cost separated from value in analyze_mechanic (no conflation of burden with benefit).
prof = vm.analyze_mechanic("exit_interview")
ck("cost/burden kept separate from value cells", "research_burden" in prof["resources_consumed"] and "product_clients" in prof["value_cells"])

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
