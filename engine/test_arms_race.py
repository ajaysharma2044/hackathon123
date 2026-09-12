"""python3 test_arms_race.py"""
from spend_intensity import (SpendCategory, DesperationSignal, rank_categories, spend_rationale,
                             INTENSITY_DIMS, NONE, LOW, MED, HIGH)
from gap_finder import StructuralGap, real_gaps, rank_gaps, assets_in_play
from opportunity_matcher import evaluate, rank, pareto, demand_shaped_environment, Opportunity, OPP_DIMS
from problem_model import Problem
from beliefs import point

P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# ---------------- spend_intensity ----------------
c_default = SpendCategory("X", "win the thing")
ck("category annual spend defaults UNKNOWN", c_default.current_annual_spend.status == "UNKNOWN")
ck("category with UNKNOWN spend reports spend_is_evidenced False", c_default.spend_is_evidenced is False)
ck("intensity vector has all 8 dims", set(c_default.intensity_vector().keys()) == set(INTENSITY_DIMS))

sig_bare = DesperationSignal("RAPID_HIRING", "AcmeAI")
sig_linked = DesperationSignal("RAPID_HIRING", "AcmeAI", linked_gap="cannot buy parallel R&D search")
ck("unlinked desperation signal is not an opportunity", sig_bare.counts_as_opportunity is False)
ck("gap-linked desperation signal counts", sig_linked.counts_as_opportunity is True)

strong = SpendCategory("AI_TALENT", "win scarce AI capability",
                       economic_value=HIGH, competitive_intensity=HIGH, cost_of_failure=HIGH,
                       decision_urgency=HIGH, hackathon_fit=HIGH, spend_growth=HIGH, value_of_winning=HIGH,
                       scarcity=HIGH, cost_of_delay=HIGH,
                       current_annual_spend=point("spend", 5e8, "PUBLIC_STATEMENT", "illustrative evidenced"),
                       evidence_strength="PUBLIC_STATEMENT",
                       budget_categories="R&D headcount")
weak_hyp = SpendCategory("MAYBE", "some outcome", economic_value=LOW, competitive_intensity=LOW,
                         evidence_strength="HYPOTHETICAL")
order = rank_categories([weak_hyp, strong])
ck("evidenced high-intensity war ranks above a hypothetical one", order[0].code == "AI_TALENT")

sr = spend_rationale(strong)
ck("spend rationale detects a real economic surface", sr["economic_surface_exists"] is True)
ck("spend rationale reports spend evidenced for the evidenced category", sr["spend_evidenced"] is True)
ck("spend rationale for a hypothetical category is not evidenced", spend_rationale(weak_hyp)["spend_evidenced"] is False)

# ---------------- gap_finder ----------------
g_real = StructuralGap("PARALLEL_RND", "AI_TALENT", they_can_buy="consultants",
                       they_cannot_buy="30 independent technical approaches in 72h",
                       scarce_asset="INDEPENDENT_PARALLEL_TECHNICAL_SEARCH", substitute="CONSULTING",
                       gap_severity=HIGH, hackathon_advantage=HIGH, evidence_strength="PUBLIC_STATEMENT")
g_covered = StructuralGap("COVERED", "AI_TALENT", they_can_buy="a survey", they_cannot_buy="nothing much",
                          gap_severity=LOW, hackathon_advantage=HIGH)
g_notours = StructuralGap("NOTOURS", "AI_TALENT", they_can_buy="a lab", they_cannot_buy="deep domain research",
                          gap_severity=HIGH, hackathon_advantage=LOW)
ck("a genuinely-unmet, structurally-suited gap is real", g_real.is_real_gap is True)
ck("a well-covered gap is not a gap", g_covered.is_real_gap is False)
ck("a real gap we can't fill is NOT_OURS", g_notours.verdict().startswith("NOT_OURS"))
ck("real_gaps filters to the passing gap only", [g.code for g in real_gaps([g_real, g_covered, g_notours])] == ["PARALLEL_RND"])
ck("rank_gaps puts the real gap first", rank_gaps([g_covered, g_real, g_notours])[0].code == "PARALLEL_RND")
ck("assets_in_play surfaces the recurring scarce asset",
   assets_in_play([g_real]).get("INDEPENDENT_PARALLEL_TECHNICAL_SEARCH") == 1)

# ---------------- opportunity_matcher ----------------
opp_live = evaluate("AI parallel R&D", strong, g_real, buyer="Head of Applied Research",
                    business_model="PER_PROBLEM_MANDATE", buyer_authority=MED, budget_accessibility=MED,
                    execution_feasibility=MED, participant_fit=HIGH, repeatability=MED)
ck("a full-stack opportunity is LIVE", opp_live.is_live is True)
ck("opportunity evidence = weaker of the two inputs", opp_live.evidence_strength == "PUBLIC_STATEMENT")
ck("opportunity vector keeps all 12 dims", set(opp_live.vector().keys()) == set(OPP_DIMS))

opp_extractive = evaluate("extractive", strong, g_real, buyer="X", buyer_authority=MED,
                          participant_fit=NONE)   # fails the participant-experience hard constraint
ck("an extractive opportunity is not LIVE", opp_extractive.is_live is False)
ck("extractive opportunity verdict flags participant experience", "participant" in opp_extractive.verdict().lower())

opp_nowar = evaluate("no war", weak_hyp, g_real, buyer="X", buyer_authority=MED, participant_fit=HIGH)
ck("no-spending-war opportunity is skipped", opp_nowar.is_live is False)

ranked = rank([opp_nowar, opp_live, opp_extractive])
ck("live opportunity ranks first", ranked[0].label == "AI parallel R&D")
ck("pareto returns only live labels", set(pareto([opp_live, opp_nowar, opp_extractive])) <= {"AI parallel R&D"})

dse = demand_shaped_environment(Problem("parallel R&D search across approaches", mode="DISCOVERY"))
ck("demand-shaped environment is feasible for a good problem", dse["feasible"] is True)
ck("demand-shaped environment keeps participant experience as a hard constraint",
   "ParticipantExperience" in dse["hard_constraint"])

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
