"""python3 test_environment_economy.py"""
import numpy as np
from environment import (Environment, CAPABILITIES, capability_scores, capability_vector, tweak,
                         hackathon_flagship, hackathon_with_panel)
from problem_model import Problem, required_capabilities, MECHANIC_DIMS, MED
from economy import (Actor, Episode, ShadowPrices, EconomicLedger, simulate_contribution,
                     RESOURCE_KINDS)
from beliefs import point, unknown

P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# ---------------- environment.py ----------------
big = Environment("big", n_participants=300)
small = Environment("small", n_participants=60)
ck("more participants raises parallel search", capability_scores(big)["PARALLEL_SEARCH"] > capability_scores(small)["PARALLEL_SEARCH"])

ck("continuation+followup raises longitudinal capture",
   capability_scores(hackathon_with_panel())["LONGITUDINAL_CAPTURE"] > capability_scores(hackathon_flagship())["LONGITUDINAL_CAPTURE"])

online = Environment("online", medium="ONLINE")
inperson = Environment("inperson", medium="IN_PERSON")
ck("in-person has higher behavioral realism than online",
   capability_scores(inperson)["BEHAVIORAL_REALISM"] > capability_scores(online)["BEHAVIORAL_REALISM"])
ck("in-person has LOWER cost advantage than online (costliest data path, caveat #5)",
   capability_scores(inperson)["COST_ADVANTAGE"] < capability_scores(online)["COST_ADVANTAGE"])

elite = Environment("elite", selectivity=1.0)
open_ = Environment("open", selectivity=0.2)
ck("higher selectivity lowers external validity (caveat #4)",
   capability_scores(elite)["EXTERNAL_VALIDITY"] < capability_scores(open_)["EXTERNAL_VALIDITY"])

heavy_prize = Environment("heavy", incentive_intensity=0.9)
light_prize = Environment("light", incentive_intensity=0.1)
ck("heavy extrinsic incentive lowers behavioral realism (contamination)",
   capability_scores(heavy_prize)["BEHAVIORAL_REALISM"] < capability_scores(light_prize)["BEHAVIORAL_REALISM"])

vec = capability_vector(hackathon_flagship())
ck("capability_vector has all 21 dims", set(vec.keys()) == set(CAPABILITIES))
ck("capability_vector values are ordinal 0..3", all(0 <= v <= 3 for v in vec.values()))

t = tweak(hackathon_flagship(), followup_waves=3)
ck("tweak: adding follow-up waves raises longitudinal capture", t["LONGITUDINAL_CAPTURE"] > 0)

# ---------------- problem_model.py ----------------
p = Problem("An airline loses money in large weather disruptions", mode="SIMULATION")
ck("new problem economic_value is UNKNOWN", p.economic_value.status == "UNKNOWN")
try:
    p.economic_value.sample(10, np.random.default_rng(0)); sampled_ok = False
except ValueError:
    sampled_ok = True
ck("UNKNOWN economic value refuses to sample", sampled_ok)
ck("problem mechanics has 16 dims", set(p.mechanics().keys()) == set(MECHANIC_DIMS))
ck("problem is not hypothetical by default", p.is_hypothetical is False)

div = Problem("generate many product concepts", mode="DIVERGENCE", parallelizability=3)
ck("divergence problem needs parallel search", "PARALLEL_SEARCH" in required_capabilities(div))
longp = Problem("does the workflow change stick?", mode="EXPERIMENTATION", longitudinal_need=MED)
ck("high longitudinal-need problem needs longitudinal capture", "LONGITUDINAL_CAPTURE" in required_capabilities(longp))

# ---------------- economy.py ----------------
sp = ShadowPrices()
ck("all shadow prices default UNKNOWN", len(sp.unresolved()) == len(RESOURCE_KINDS))
ck("value_of an UNKNOWN resource is None", sp.value_of("MENTOR_TIME_MIN", 100) is None)
sp.set("MENTOR_TIME_MIN", point("mentor_min", 5.0, "ASSUMED", "illustrative $5/mentor-minute"))
ck("value_of a set resource returns a number", abs(sp.value_of("MENTOR_TIME_MIN", 100) - 500.0) < 1e-6)
ck("setting one price shortens the unresolved list", len(sp.unresolved()) == len(RESOURCE_KINDS) - 1)

led = EconomicLedger(sp)
led.add_actor(Actor("a1", "PARTICIPANT"))
led.add_episode(Episode("e1", "a1", "PROBLEM", choice_set=("P1", "P2"), decision="P1",
                        resource_allocation={"PARTICIPANT_TIME_MIN": 600}, changed_a_decision=True))
led.add_episode(Episode("e2", "a1", "PROBLEM", choice_set=("P1", "P2"), decision=None))  # abandoned
led.add_episode(Episode("e3", "a1", "BOUNTY", decision="B1",
                        resource_allocation={"PARTICIPANT_TIME_MIN": 300}, is_negative_result=True))
ck("attention flow counts chosen opportunities", led.attention_flow().get("PROBLEM") == 1)
ck("abandonment counts un-chosen opportunities", led.abandonment().get("PROBLEM") == 1)
ck("resource flow sums allocations", abs(led.resource_flow()["PARTICIPANT_TIME_MIN"] - 900) < 1e-6)
ck("bottleneck detected when demand exceeds supply",
   "PARTICIPANT_TIME_MIN" in led.bottlenecks({"PARTICIPANT_TIME_MIN": 500}))
ck("no bottleneck when supply is ample", led.bottlenecks({"PARTICIPANT_TIME_MIN": 5000}) == {})
ck("negative results counted", led.negative_results() == 1)
ck("decisions changed counted", led.decisions_changed() == 1)

# generalized contribution simulator reuses monte_carlo (and its UNKNOWN guard)
mc = simulate_contribution({"contract": point("contract", 100000, "ASSUMED", "illustrative")},
                           {"cost": point("cost", 40000, "ASSUMED", "illustrative")}, n=2000)
ck("contribution mean ~ revenue - cost", abs(mc.summary()["mean"] - 60000) < 5000)
ck("contribution is profitable here", mc.prob_gt(0) > 0.99)
try:
    simulate_contribution({"mystery": unknown("mystery", "none", "no basis")},
                          {"cost": point("cost", 1, "ASSUMED", "x")}, n=100)
    unk_guard = False
except ValueError:
    unk_guard = True
ck("UNKNOWN revenue line refuses to simulate (honesty guard)", unk_guard)

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
