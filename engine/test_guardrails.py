"""python3 test_guardrails.py — the Part LXXIV compliance suite for the talent + venture markets."""
import compliance
import work_evidence as we
from work_evidence import WorkEvidence, ProjectRole, contribution_summary, evidence_for_scope
from job_requirements import JobRequirement
import talent_matching as tm
from talent_matching import ParticipantEvidenceView
import venture_matching as vm
from venture_profile import VentureProfile
from fund_graph import Fund
from mutual_intro import IntroRequest, release_contact
import opportunity_market as om

P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")
def raises(fn, exc=Exception):
    try: fn(); return False
    except exc: return True

# --- no protected/sensitive traits used ---
ck("sensitive attribute is refused", raises(lambda: compliance.assert_no_sensitive(["race"]), ValueError))
ck("sensitive substring is refused", raises(lambda: compliance.assert_no_sensitive(["applicant_age_band"]), ValueError))
ck("non-sensitive fields pass", compliance.assert_no_sensitive(["backend", "location_preference"]) is True)
ck("job requirement with a sensitive field is refused",
   raises(lambda: JobRequirement("j", "Eng", required_capabilities={"religion": 3}), ValueError))

# --- no person scores of any kind ---
for bad in ["hireability", "founder_quality", "personality_score", "intelligence", "employability"]:
    ck(f"person score '{bad}' is refused", raises(lambda b=bad: compliance.assert_not_a_person_score(b), ValueError))

# --- matches are decomposed, never a single opaque score ---
job = JobRequirement("j1", "Backend Intern", required_capabilities={"BACKEND": 3}, technologies=("fastapi",))
pv = ParticipantEvidenceView("p1", opted_scopes={"EMPLOYER": True},
                             capabilities=({"capability": "BACKEND", "support_kind": "ARTIFACT_SUPPORTED"},),
                             technologies=("fastapi",), desired_roles=("backend",))
m = tm.match(job, pv)
ck("talent match has no overall/candidate score key", not any(k in m for k in ("overall_score", "score", "candidate_score")))
fund = Fund("f1", "Seed Infra", stage="SEED", sectors=("developer_tools",), thesis="developer infrastructure")
ven = VentureProfile("v1", attributes={"STAGE": "SEED", "SECTOR": "developer_tools", "TECHNICAL_DOMAIN": "infrastructure"},
                     investor_visible=True, continuation_status="CONTINUED")
vmatch = vm.match(ven, fund)
ck("venture match has no founder/overall score key", not any(k in vmatch for k in ("founder_score", "overall_score", "score")))

# --- missing evidence is neutral, never negative ---
ck("neutral_when_missing returns UNKNOWN", compliance.neutral_when_missing(None) == "UNKNOWN")
pv_missing = ParticipantEvidenceView("p2", opted_scopes={"EMPLOYER": True},
                                     capabilities=({"capability": "BACKEND", "support_kind": "SELF_REPORTED"},))
mm = tm.match(job, pv_missing)
ck("missing location/availability are None, not 0", mm["location_fit"] is None and mm["availability_fit"] is None)
ck("missing fields are listed as unknowns, not penalties", len(mm["unknowns"]) >= 1)

# --- mentor requests never become hiring/venture evidence; commit counts never rank ---
ck("mentor request fan-out has no hiring value", "HiringValue" not in om.fan_out("MENTOR_REQUEST", {"EMPLOYER": True}))
ck("mentor request fan-out has no venture value", "VentureValue" not in om.fan_out("MENTOR_REQUEST", {"INVESTOR": True}))
ck("commit count is a forbidden contribution metric", "commit_count" in we.FORBIDDEN_CONTRIBUTION_METRICS)
summ = contribution_summary([], [])
ck("contribution summary never returns a score", "score" not in summ and "confirmed_workstreams" in summ)

# --- individual disclosure requires an explicit, per-scope opt-in ---
evA = WorkEvidence("e1", "CODE_ARTIFACT", "ARTIFACT_OBSERVED", data_level="A_EVENT_OPERATIONS")
evC = WorkEvidence("e2", "CODE_ARTIFACT", "ARTIFACT_OBSERVED", data_level="C_OPT_IN_PROFESSIONAL", consent_scope=("EMPLOYER",))
ck("level-A evidence is never visible to a scope", evA.visible_to("EMPLOYER") is False)
ck("level-C evidence visible only to opted scope", evC.visible_to("EMPLOYER") is True and evC.visible_to("INVESTOR") is False)
ck("aggregate/level-A evidence does not leak into a scope packet", evidence_for_scope([evA], "EMPLOYER") == [])

# --- employer and investor scopes are distinct ---
pv_emp_only = ParticipantEvidenceView("p3", opted_scopes={"EMPLOYER": True})
ck("EMPLOYER opt-in does not imply INVESTOR", pv_emp_only.opted("EMPLOYER") and not pv_emp_only.opted("INVESTOR"))
ck("retrieve returns only EMPLOYER-opted participants", [x["participant_id"] for x in tm.retrieve(job, [pv, ParticipantEvidenceView("nope", opted_scopes={})])] == ["p1"])
ck("venture discover returns only INVESTOR-visible ventures",
   [x["venture_id"] for x in vm.discover(fund, [ven, VentureProfile("hidden", investor_visible=False)])] == ["v1"])

# --- revocation works; participant-side matching works without employer opt-in ---
pv.opted_scopes["EMPLOYER"] = False
ck("revoking visibility removes participant from retrieval", tm.retrieve(job, [pv]) == [])
ck("participant-side matching works even without employer opt-in", len(tm.participant_side_matches(pv, [job])) == 1)

# --- no autonomous employment/investment decisions ---
ck("talent match explanation states it is not a hiring recommendation", "not a hiring recommendation" in tm.explain(m))
ck("venture match explanation states it is not an investment recommendation", "not an investment recommendation" in vm.explain(vmatch))

# --- no contact release without mutual opt-in ---
req = IntroRequest("EMPLOYER", "companyX", "p1", subject_opted_in=False, subject_visible=False)
ck("contact is NOT released before mutual opt-in", raises(lambda: release_contact(req, "email@x.com"), PermissionError))
req.subject_visible = True; req.accept()
ck("contact released after mutual opt-in", release_contact(req, "email@x.com") == "email@x.com")

# --- securities guard: no investment success fees until counsel ---
ck("investment success fee is forbidden until counsel", raises(lambda: om.assert_monetization_allowed("INVESTMENT_SUCCESS_FEE"), PermissionError))
ck("access subscription is allowed", om.assert_monetization_allowed("TALENT_ACCESS_SUBSCRIPTION") == "ALLOWED")

# --- venture: weekend prototype is not production readiness ---
ck("venture diligence note flags prototype != production", "not production readiness" in VentureProfile("vv").diligence_note())

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
