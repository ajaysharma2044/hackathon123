"""python3 test_talent_venture.py — functional tests for the talent + venture markets."""
import capability_graph as cg
from work_evidence import WorkEvidence, ProjectRole, render_claim
from job_requirements import JobRequirement
import talent_matching as tm
from talent_matching import ParticipantEvidenceView
from mutual_intro import IntroRequest, funnel_liquidity, TALENT_FUNNEL
from fund_graph import Fund, Investor, funds_in_sector
from venture_profile import VentureProfile, VentureClaim
import venture_matching as vm
import opportunity_market as om

P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# ---- capability graph ----
caps = cg.capabilities_from_technologies(["FastAPI", "Postgres", "Redis", "unknown_tool"])
codes = {c["capability"] for c in caps}
ck("tech maps to backend/database capabilities", {"BACKEND", "DATABASES"} <= codes)
ck("all tech-derived evidence is artifact-supported", all(c["support_kind"] == "ARTIFACT_SUPPORTED" for c in caps))
ck("unknown tech is skipped, never penalized", all("unknown_tool" not in c["note"] for c in caps))
ck("self-reported capability is tagged distinctly", cg.self_reported_capability("BACKEND")["support_kind"] == "SELF_REPORTED")
ck("ontology is extensible / has subskills", "API_DESIGN" in cg.subskills("BACKEND"))

# ---- work evidence + claim rendering ----
role = ProjectRole("p1", "proj1", "BACKEND", declared_by_team=True, confirmed_by_participant=True)
ck("role valid only when team-declared AND participant-confirmed", role.is_valid is True)
ck("unconfirmed role is not valid", ProjectRole("p1", "proj1", "BACKEND", declared_by_team=True).is_valid is False)
ev = WorkEvidence("e1", "ROLE_OWNERSHIP", "TEAM_CONFIRMED", participant_id="p1")
claim = render_claim(ev, "Ajay", "the backend workstream (FastAPI/Postgres)")
ck("claim is evidence-with-provenance, not a trait judgement", "opted to disclose" in claim and "excellent" not in claim.lower())

# ---- job + talent matching ----
job = JobRequirement("j1", "ML Infra Intern", job_family="ML Infrastructure",
                     required_capabilities={"ML": 3, "BACKEND": 2}, domains=("ml_infra",),
                     technologies=("pytorch", "docker"))
pv = ParticipantEvidenceView("p1", opted_scopes={"EMPLOYER": True},
                             capabilities=({"capability": "ML", "support_kind": "ARTIFACT_SUPPORTED"},
                                           {"capability": "BACKEND", "support_kind": "ARTIFACT_SUPPORTED"}),
                             domains=("ml_infra",), technologies=("pytorch", "docker"),
                             desired_roles=("infrastructure", "ml infra"), location_preference="Remote",
                             availability="Summer 2027")
m = tm.match(job, pv)
ck("full-coverage match scores capability coverage HIGH", m["capability_coverage"] == 3)
ck("artifact relevance is scored", m["artifact_relevance"] == 3)
ck("match includes human-readable reasons", len(m["why"]) >= 2)
ck("retrieve returns the opted-in candidate", len(tm.retrieve(job, [pv])) == 1)
ck("explanation is generated", "ML Infra Intern".split()[0] in tm.explain(m) or "j1" in tm.explain(m))

# ---- mutual intro funnel ----
liq = funnel_liquidity({"INTRODUCTION": 5, "INTERVIEW": 2, "HIRE": 0}, kind="talent")
ck("funnel liquidity reports all talent stages", set(TALENT_FUNNEL) <= set(liq.keys()))
ck("funnel liquidity carries the intro!=transaction caveat", "not a hire" in liq["_note"])

# ---- fund graph ----
f1 = Fund("f1", "Seed Infra Fund", stage="SEED", sectors=("developer_tools", "infrastructure"),
          geography="US", thesis="developer infrastructure and observability", source_url="https://example.vc")
Investor("i1", "f1", "A. Partner", role="PARTNER")
ck("funds_in_sector filters correctly", [f.fund_id for f in funds_in_sector([f1], "infrastructure")] == ["f1"])

# ---- venture profile + matching (non-winner included; continuation matters) ----
ven = VentureProfile("v1", problem="observability for LLM apps",
                     attributes={"STAGE": "SEED", "SECTOR": "developer_tools", "TECHNICAL_DOMAIN": "observability"},
                     claims=[VentureClaim("has 3 pilot users", status="SELF_REPORTED")],
                     investor_visible=True, continuation_status="CONTINUED")
ck("material claims all carry a status", ven.material_claims_ok() is True)
vmatch = vm.match(ven, f1)
ck("sector fit recognized", vmatch["sector_fit"] == 3)
ck("continuation at follow-up is a first-class signal", vmatch["continuation_evidence"] == 3)
ck("discover includes a non-winning but continuing team", "v1" in [x["venture_id"] for x in vm.discover(f1, [ven])])

# ---- opportunity market value fan-out ----
ck("repo submission serves research value with no opt-in", "ResearchValue" in om.fan_out("REPO_SUBMISSION"))
ck("repo submission serves hiring value ONLY with employer opt-in",
   "HiringValue" in om.fan_out("REPO_SUBMISSION", {"EMPLOYER": True}) and "HiringValue" not in om.fan_out("REPO_SUBMISSION"))
ck("value surfaces include hiring and venture", {"HiringValue", "VentureValue"} <= set(om.VALUE_SURFACES))
hub = om.participant_opportunity_hub({"EmployerInterest": ["companyX"], "InvestorInterest": []})
ck("participant hub gathers all categories and states participant control", "_control" in hub and "EmployerInterest" in hub)
ck("revenue is not double-counted across transactions",
   om.dedup_revenue([{"id": "a", "amount": 100}, {"id": "a", "amount": 100}, {"id": "b", "amount": 50}]) == 150)

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
