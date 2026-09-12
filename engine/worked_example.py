"""Worked example (docs/quant-engine.md Part 31): run the engine on 3 Event-1 designs.
ALL numeric inputs are ASSUMED scenario bands (docs/quant-assumptions.md), NOT measurements.
The output demonstrates the machinery; the specific numbers move the moment real evidence arrives."""
import numpy as np
from event_optimizer import (EventDesign, objectives, economic, pareto_frontier, tweak, robust_eval,
                             research_quality_multiplier, cost)
from voi import evpi, evsi_beta, net_voi
from portfolio import Study, select

A = EventDesign("A: 120 ultra-premium, few sponsors", n_builders=120, n_research_sponsors=2,
                free_choice_share=0.55, mentor_ratio=0.15, research_minutes=15)
B = EventDesign("B: 200 balanced", n_builders=200, n_research_sponsors=4,
                free_choice_share=0.40, mentor_ratio=0.10, research_minutes=18)
C = EventDesign("C: 300 sponsor-heavy", n_builders=300, n_research_sponsors=7,
                free_choice_share=0.20, mentor_ratio=0.06, research_minutes=28)

print("="*78, "\nOBJECTIVES (all inputs ASSUMED — see quant-assumptions.md)\n", "="*78)
print(f"{'design':<34}{'exp':>5}{'research':>10}{'E[contrib]':>12}{'p5':>10}{'P(BE)':>7}{'longT':>7}{'qmult':>7}")
objs = []
for d in (A, B, C):
    o = objectives(d); objs.append((d.name, o))
    print(f"{d.name:<34}{o['experience']:>5.1f}{o['research_info']:>10.1f}"
          f"{o['econ_mean_contribution']:>12,.0f}{o['econ_p5']:>10,.0f}{o['econ_p_breakeven']:>7.2f}"
          f"{o['longterm']:>7.1f}{research_quality_multiplier(d):>7.2f}")
print("\nPareto frontier (non-dominated on experience/research/econ/longterm):",
      pareto_frontier([(n, o) for n, o in objs]))

print("\n" + "="*78, "\nEVENT-1 REVENUE AS A DISTRIBUTION — Design B (contribution margin, $)\n", "="*78)
mc = economic(B); s = mc.summary()
print(f"  cost @0.6 scholarship (ASSUMED): ${cost(B, scholarship=0.6):,.0f}   (gross ${cost(B):,.0f})")
for k in ("p5", "p25", "median", "mean", "p75", "p95"):
    print(f"  {k:>7}: ${s.get(k, mc.percentile({'median':50}.get(k,50))) if k=='median' else s[k]:>12,.0f}")
for t in (0, 100000, 250000, 500000):
    print(f"  P(contribution > ${t:>7,}): {mc.prob_gt(t):.2f}")
print(f"  VaR(95%): ${mc.var(0.95):,.0f}    CVaR(95%) / expected shortfall: ${mc.cvar(0.95):,.0f}")

print("\n" + "="*78, "\nEVENT TWEAK ENGINE — one knob at a time, deltas on Design B\n", "="*78)
tweaks = {"+mentors (0.10->0.20)": dict(mentor_ratio=0.20),
          "+2 research sponsors (4->6)": dict(n_research_sponsors=6),
          "-free-choice (0.40->0.20)": dict(free_choice_share=0.20),
          "+free-choice (0.40->0.60)": dict(free_choice_share=0.60),
          "over-burden research (18->35 min)": dict(research_minutes=35),
          "+continuation grants": dict(continuation_grants=True),
          "drop 90d follow-up": dict(followup_90d=False)}
print(f"{'tweak':<36}{'d_exp':>7}{'d_research':>11}{'d_contrib':>11}{'d_P(BE)':>9}{'d_longT':>8}")
for label, ch in tweaks.items():
    t = tweak(B, **ch)
    print(f"{label:<36}{t['experience']:>7.2f}{t['research_info']:>11.1f}{t['econ_mean_contribution']:>11,.0f}{t['econ_p_breakeven']:>9.2f}{t['longterm']:>8.2f}")

print("\n" + "="*78, "\nROBUST EVALUATION — Design B under bear/base/bull WTP\n", "="*78)
for scen, r in robust_eval(B).items():
    print(f"  {scen:<5}  E[contrib]=${r['mean']:>10,}   P(break-even)={r['p_breakeven']:.2f}   CVaR95=${r['cvar95']:>10,}")

print("\n" + "="*78, "\nVALUE OF INFORMATION — should we sell now or gather more evidence?\n", "="*78)
VALUE, COST = 900000, cost(B, scholarship=0.6)
acts = ["GO", "NOGO"]
def util(a, theta): return (theta*VALUE - COST) if a=="GO" else np.zeros_like(np.asarray(theta,float))
prior = np.random.default_rng(3).beta(2, 6, size=40000)   # ASSUMED ~25% anchor-close belief
ev = evpi(prior, acts, util)
print(f"  EVPI (value of perfectly knowing anchor close-prob): ${ev:,.0f}")
for m, c in [(5, 8000), (10, 15000), (20, 28000)]:
    e = evsi_beta(2, 6, m, acts, util); print(f"  {m:>2} buyer interviews: EVSI=${e:>9,.0f}  cost=${c:>6,}  NetVOI=${net_voi(e,c):>9,.0f}")

print("\n" + "="*78, "\nSTUDY PORTFOLIO — max value under capacity + one-per-competitive-category\n", "="*78)
studies = [Study("anthropic_ai",120000,40000,1200,60,"ai_coding"), Study("cursor_ai",110000,30000,1200,60,"ai_coding"),
           Study("stripe_pay",80000,20000,900,40,"payments"), Study("datadog_obs",70000,25000,800,40,"observability"),
           Study("supabase_db",75000,22000,850,40,"database")]
r = select(studies, participant_minute_budget=3200, researcher_hour_capacity=150)
print(f"  selected: {r['selected']}\n  value: ${r['value']:,.0f}   slack: {r['slack']}")
