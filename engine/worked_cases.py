"""
worked_cases.py — twelve HYPOTHETICAL problems pushed end-to-end through the discovery engine.

RUN: python3 worked_cases.py

*** EVERYTHING HERE IS HYPOTHETICAL. These are illustrations of the machinery, NOT market evidence,
NOT claims that these companies have these problems or would pay. Every economic magnitude is UNKNOWN
by construction, so the engine's honest recommendation for almost all of them is GATHER_EVIDENCE —
which is exactly the point (STATE.md's gating unknown). ***

The cases deliberately span technical AND non-technical industries and multiple problem modes, to
show the engine does not privilege software / devtools / a 48-72h hackathon.
"""
from __future__ import annotations
from problem_model import Problem, NONE, LOW, MED, HIGH
from environment_generator import best_feasible
from problem_matcher import match
import bilevel
from beliefs import scenario

# (industry, statement, mode, {mechanic overrides})
CASES = [
    ("Airline", "Recover an operation after weather cancels hundreds of flights", "SIMULATION",
     dict(operational_component=HIGH, simulation_feasibility=HIGH, parallelizability=MED,
          feedback_latency=HIGH, need_domain_expertise=HIGH)),
    ("Bank", "Redesign analyst workflows around AI while keeping compliance", "EXPERIMENTATION",
     dict(technical_component=HIGH, behavioral_component=HIGH, experimentability=MED,
          internal_political_friction=HIGH, need_domain_expertise=HIGH)),
    ("Insurer", "Cut claims cycle-time and leakage", "OPTIMIZATION",
     dict(operational_component=HIGH, simulation_feasibility=MED, prototypeability=MED,
          need_domain_expertise=HIGH)),
    ("Retailer", "Route, inspect, reprice and reintegrate returns into inventory", "OPTIMIZATION",
     dict(operational_component=HIGH, simulation_feasibility=HIGH, parallelizability=MED)),
    ("Hotel", "Raise on-property spend without hurting guest satisfaction", "EXPERIMENTATION",
     dict(behavioral_component=HIGH, creative_component=MED, experimentability=MED)),
    ("Manufacturer", "Reconfigure a production line to cut downtime", "OPTIMIZATION",
     dict(operational_component=HIGH, simulation_feasibility=HIGH, need_domain_expertise=HIGH)),
    ("Logistics", "Dynamically reallocate capacity under uncertain demand", "SIMULATION",
     dict(operational_component=HIGH, simulation_feasibility=HIGH, technical_component=MED)),
    ("Media", "Redesign content discovery / creator incentives", "MARKET_DESIGN",
     dict(behavioral_component=HIGH, creative_component=HIGH, experimentability=MED)),
    ("Health system", "Improve patient flow under real staffing/capacity limits", "SIMULATION",
     dict(operational_component=HIGH, simulation_feasibility=HIGH, need_domain_expertise=HIGH,
          internal_political_friction=HIGH)),
    ("PE firm", "Pick an operational intervention to deploy across portfolio companies", "DISCOVERY",
     dict(operational_component=MED, need_external_perspective=HIGH, repeatability=HIGH)),
    ("Consumer brand", "Explore a radically different product-discovery experience", "DIVERGENCE",
     dict(creative_component=HIGH, prototypeability=HIGH, parallelizability=HIGH)),
    ("AI infra co", "Find 30 independent technical approaches to one hard integration", "DIVERGENCE",
     dict(technical_component=HIGH, prototypeability=HIGH, parallelizability=HIGH,
          need_external_perspective=HIGH)),
]


def run():
    print("=" * 88)
    print("HYPOTHETICAL worked cases — illustrations of the machinery, NOT market evidence.")
    print("=" * 88)
    feasible = 0
    for industry, statement, mode, mech in CASES:
        p = Problem(statement, industry=industry, mode=mode, is_hypothetical=True, **mech)
        rec = bilevel.evaluate_problem(p)
        best = best_feasible(p)
        env_name = best["name"] if best else "— (no design clears the fit gate)"
        cov = best["match"]["coverage"] if best else 0
        xval = best["match"]["fit"]["external_validity"] if best else None
        feasible += int(best is not None)
        print(f"\n[{industry}] {statement}")
        print(f"    mode={mode}  → environment: {env_name}")
        print(f"    fit coverage={cov}  external_validity={xval}  "
              f"price_ceiling={rec['rational_price_ceiling']}  action={rec['recommended_action']}")

    # One case WITH an ASSUMED contract band + decision value, to show the VOI path diverging from the
    # UNKNOWN default. Bands are explicitly ASSUMED — not a forecast.
    print("\n" + "-" * 88)
    print("Illustrative VOI branch (ASSUMED bands, not evidence):")
    p = Problem("parallel R&D search across approaches", industry="AI infra co", mode="DIVERGENCE",
                is_hypothetical=True, technical_component=HIGH, prototypeability=HIGH,
                parallelizability=HIGH, need_external_perspective=HIGH,
                cost_of_wrong=scenario("cost_of_wrong", 2e6, 8e6, 2e7, "ASSUMED",
                                       "illustrative decision at stake"))
    contract = scenario("contract", 40000, 120000, 300000, "ASSUMED", "illustrative contract band")
    rec = bilevel.evaluate_problem(p, contract_value=contract)
    print(f"    price_ceiling={rec['rational_price_ceiling']:.0f} (a CEILING, not observed WTP)  "
          f"action={rec['recommended_action']}")
    print(f"    {rec['action_detail']}")

    print("\n" + "=" * 88)
    print(f"{feasible}/{len(CASES)} hypothetical problems had a feasible environment design.")
    print("With every economic magnitude UNKNOWN, the honest recommendation is GATHER_EVIDENCE — the")
    print("$5-15K falsification test — before any environment is built. (STATE.md gating unknown.)")
    print("=" * 88)


if __name__ == "__main__":
    run()
