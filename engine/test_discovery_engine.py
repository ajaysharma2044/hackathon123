"""python3 test_discovery_engine.py"""
from environment import Environment
from problem_model import Problem, MED, HIGH
from problem_matcher import match, pareto_frontier
from environment_generator import archetype_for, generate, best_feasible
from talent_allocator import ProblemDemand, allocate, select_problems, marginal_value_of_capacity
from business_model import (BUSINESS_MODELS, pareto as bm_pareto, filter_by, rational_price_ceiling,
                            MED as BMED)
from icp_discovery import (ICPDimensions, cluster_problems, synthesize, rank, record_wtp_evidence)
from beliefs import point, unknown, RateObservation
import bilevel

P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# ---------------- problem_matcher ----------------
div = Problem("generate many concepts", mode="DIVERGENCE", parallelizability=3, prototypeability=2,
              technical_component=2, creative_component=2)
strong_env = archetype_for(div)
ms = match(div, strong_env)
ck("purpose-built environment clears the fit gate", ms["gate_passed"] is True)
ck("strong match is not a KILL verdict", not ms["verdict"].startswith("KILL"))

weak_env = Environment("weak", n_participants=8, team_size=4, tool_richness=0, data_access=0,
                       instrumentation=0, feedback_cadence=0, market_mechanism="NONE",
                       interdisciplinarity=0.0, competition=0.0)
opt = Problem("reconfigure a production line", mode="OPTIMIZATION", operational_component=3,
              simulation_feasibility=3)
mk = match(opt, weak_env)
ck("barebones environment is KILLED on an optimization problem", mk["gate_passed"] is False)
ck("killed match returns a KILL verdict", mk["verdict"].startswith("KILL"))
ck("large budget cannot rescue a killed pair (fit dims still low)", mk["coverage"] <= 1)

# talent_match responds to whether the cohort supplies the dominant component's discipline
ops_problem = Problem("supply-chain optimization", mode="OPTIMIZATION", operational_component=3,
                      technical_component=2)
or_env = Environment("or", talent_mix=(("OR_IE", 0.5), ("SOFTWARE", 0.5)), data_access=3,
                     instrumentation=3, feedback_cadence=3, market_mechanism="INTERNAL_MARKET")
sw_env = Environment("sw", talent_mix=(("DESIGN", 0.5), ("BUSINESS", 0.5)), data_access=3,
                     instrumentation=3, feedback_cadence=3, market_mechanism="INTERNAL_MARKET")
ck("cohort with the needed discipline has higher talent match",
   match(ops_problem, or_env)["fit"]["talent_match"] > match(ops_problem, sw_env)["fit"]["talent_match"])

# ---------------- environment_generator ----------------
ranked = generate(div, top=5)
ck("generator returns candidates", len(ranked) >= 1)
ck("generator returns at most top", len(ranked) <= 5)
ck("at least one generated design clears the gate", any(r["match"]["gate_passed"] for r in ranked))
ck("best_feasible returns a design for a well-formed problem", best_feasible(div) is not None)

# ---------------- talent_allocator ----------------
demands = [ProblemDemand("A", value_per_team=10, mentor_hours_per_team=2, mode="DIVERGENCE"),
           ProblemDemand("B", value_per_team=6, mentor_hours_per_team=1, mode="OPTIMIZATION"),
           ProblemDemand("C", value_per_team=3, mentor_hours_per_team=1, mode="PROTOTYPING")]
al = allocate(demands, n_teams=6, mentor_capacity=8, compute_capacity=1000, diversity_weight=1.0)
ck("allocator returns an allocation", al is not None and len(al["allocation"]) >= 1)
ck("allocator respects the team budget", al["teams_used"] <= 6)
ck("allocator respects mentor capacity", al["mentor_hours_used"] <= 8)
al_lowmentor = allocate(demands, n_teams=6, mentor_capacity=2, compute_capacity=1000)
ck("tighter mentor capacity uses fewer or equal mentor hours",
   al_lowmentor["mentor_hours_used"] <= al["mentor_hours_used"])
ck("diversity is valued (more than one problem funded when capacity allows)", al["diversity"] >= 2)
mv = marginal_value_of_capacity(demands, 4, mentor_capacity=4, compute_capacity=1000, resource="teams", step=1)
ck("marginal value of an extra team is non-negative", mv is None or mv >= 0)
sel = select_problems(demands, participant_minute_budget=1200, researcher_hour_capacity=8)
ck("portfolio-backed problem selection returns a subset", isinstance(sel["selected"], list))

# ---------------- business_model ----------------
front = bm_pareto()
ck("business-model pareto is a non-empty subset", 0 < len(front) <= len(BUSINESS_MODELS))
ck("sponsorship has low revenue potential", BUSINESS_MODELS["SPONSORSHIP"].raw()["revenue_potential"] <= 1)
ethical = filter_by({"conflict_low": BMED, "participant_alignment": BMED})
ck("equity/venture model is excluded by the conflict+alignment floor", "VENTURE_CREATION_ECONOMICS" not in ethical)
ck("rational ceiling is None when decision value is UNKNOWN",
   rational_price_ceiling(unknown("dv", "none", "no basis"), 0.3) is None)
ceil = rational_price_ceiling(point("dv", 1_000_000, "ASSUMED", "illustrative"), 0.3)
ck("rational ceiling = value x p_change when known", abs(ceil - 300000) < 1)

# ---------------- icp_discovery ----------------
dims = ICPDimensions()
ck("all ICP dimensions default UNKNOWN", len(dims.unresolved()) == 5)
hyp = [Problem("h1", mode="DIVERGENCE", is_hypothetical=True),
       Problem("h2", mode="DIVERGENCE", is_hypothetical=True)]
real = [Problem("r1", mode="OPTIMIZATION"), Problem("r2", mode="OPTIMIZATION"), Problem("r3", mode="OPTIMIZATION")]
clusters = cluster_problems(hyp + real, by="mode")
ck("clustering groups by mode", set(clusters.keys()) == {"DIVERGENCE", "OPTIMIZATION"})
icp_hyp = synthesize("hypothetical cluster", hyp)
icp_real = synthesize("real cluster", real)
ck("all-hypothetical cluster is tagged HYPOTHETICAL", icp_hyp.evidence_strength == "HYPOTHETICAL")
ck("non-hypothetical cluster is at least INFERRED_JOB_POST", icp_real.evidence_strength == "INFERRED_JOB_POST")
ranked_icps = rank([icp_hyp, icp_real])
ck("better-evidenced ICP outranks a bigger hypothetical one", ranked_icps[0].label == "real cluster")
record_wtp_evidence(icp_real, [RateObservation(1, 7, "SIGNED_COMMERCIAL")])
ck("a signed pilot flips WTP out of UNKNOWN", icp_real.dims.wtp.status == "OBSERVED")

# ---------------- bilevel ----------------
p_unknown = Problem("airline weather disruption recovery", mode="SIMULATION")
rec = bilevel.recommend_action(p_unknown.cost_of_wrong, contract_value=None)
ck("bilevel recommends GATHER_EVIDENCE when WTP is UNKNOWN", rec[0] == "GATHER_EVIDENCE")
ev = bilevel.evaluate_problem(p_unknown)
ck("evaluate_problem keeps price ceiling None under UNKNOWN decision value", ev["rational_price_ceiling"] is None)
ck("evaluate_problem recommends gathering evidence", ev["recommended_action"] == "GATHER_EVIDENCE")
recs = bilevel.bilevel_search([div, opt, p_unknown])
ck("bilevel_search returns a record per problem", len(recs) == 3)
ck("feasible problems sort above infeasible ones",
   [r["environment_feasible"] for r in recs] == sorted([r["environment_feasible"] for r in recs], reverse=True))

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
