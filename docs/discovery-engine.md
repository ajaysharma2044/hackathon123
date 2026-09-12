# The Discovery Engine

> How the modules compose into one machine for discovering *how configurable high-agency talent
> environments create economic value* — not a prettier hackathon model.

**Governing rule, preserved:** Evidence ≠ Claim ≠ Hypothesis ≠ Decision. Everything below is
machinery + explicitly-labeled assumptions. Where a quantity is not evidenced it is **UNKNOWN**, and
the engine refuses to fabricate it (`beliefs.py` will not sample an UNKNOWN; `business_model.rational_price_ceiling`
returns `None` rather than invent a price).

This document is the map. The individual pieces are documented in
[environment-capability-map.md](environment-capability-map.md),
[problem-mechanics.md](problem-mechanics.md), [problem-environment-fit.md](problem-environment-fit.md),
[talent-configuration.md](talent-configuration.md), [economic-flow-model.md](economic-flow-model.md),
[business-model-discovery.md](business-model-discovery.md),
[icp-discovery-engine.md](icp-discovery-engine.md),
[environment-archetypes.md](environment-archetypes.md), and the arms-race layer
([economic-arms-races.md](economic-arms-races.md), [structural-gap-map.md](structural-gap-map.md),
[high-value-gap-ranking.md](high-value-gap-ranking.md)).

---

## 1. What changed

The prior engine (`engine/event_optimizer.py`, `schema/003_quant.sql`) optimized ONE environment: a
200-person, 72-hour, flown-in **software hackathon** whose product was **developer research** sold to
**devtools companies**. That is now one point in a much larger space — `environment.hackathon_flagship()`
— and one hypothesis (`business_model.BUSINESS_MODELS["SPONSORSHIP"]` / `RESEARCH_ENGAGEMENT`) among
many. Nothing about it has been promoted to a fact; the gating unknown (**will any buyer pay?**)
still stands (see [STATE.md](STATE.md)).

The reset introduces four primitives and makes each an **output**, not an input:

| Primitive | Module | Was hardcoded to | Now |
|---|---|---|---|
| Environment `E` (14-tuple) | `environment.py` | one hackathon | a configurable design space |
| Problem `P` (by mechanics) | `problem_model.py` | "a research question" | any expensive problem |
| The economy | `economy.py` | participants ↔ devtools | actors ↔ any resource/opportunity |
| Buyer / ICP | `icp_discovery.py` | "a devtools company" | discovered from the problem universe |

---

## 2. The two directions

The engine runs in **both** directions. This is the core capability.

### Demand → environment ("We are Delta Airlines.")
```
Problem P (mechanics, mode)                      problem_model.Problem
  → required capabilities                         problem_model.required_capabilities
  → design candidate environments                 environment_generator.generate / best_feasible
  → Fit(P, E) with the hard advantage gate        problem_matcher.match  (KILL if no structural edge)
  → allocate talent + scarce resources            talent_allocator.allocate
  → decide act vs gather-evidence (VOI)           bilevel.evaluate_problem  (→ GATHER_EVIDENCE while WTP UNKNOWN)
```

### Supply → opportunity ("We have 100 OR/CS/design builders.")
```
A talent configuration                            environment.Environment.talent_mix
  → environment capabilities                       environment.capability_vector  (21-dim, decomposed)
  → problem mechanics those capabilities serve     problem_model.MODE_CAPABILITY_NEEDS (reverse lookup)
  → corporate problems with that shape             corporate-problem-universe.md (evidence)
  → buyers / budget owners                          icp_discovery
  → business model                                  business_model
```

### The arms-race overlay (demand-prioritization)
Before either direction, the arms-race layer asks *where is there already a spending war, and what
gap inside it can we fill?*
```
SpendCategory (a spending war)                    spend_intensity.SpendCategory  (spend = belief, default UNKNOWN)
  × StructuralGap ("what can't they buy?")        gap_finder.StructuralGap       (two-gate REAL test)
  → Opportunity (GAP × MONEY × FIT)               opportunity_matcher.evaluate   (12 decomposed dims, hard gates)
  → demand-shaped environment                     opportunity_matcher.demand_shaped_environment
```

---

## 3. The bilevel loop (`bilevel.py`)

```
OUTER: which recurring problems are most valuable?          bilevel.bilevel_search
  INNER (per problem):
    design the best environment                             environment_generator.best_feasible
    price ceiling = decision-value × P(change)   [CEILING]  business_model.rational_price_ceiling
    decide act vs gather-evidence                [VOI]      bilevel.recommend_action → voi.evsi_beta / net_voi
  feed environment capability back → new problems become possible → re-rank
```

**The honest fixed point.** For almost every problem today, decision value and contract WTP are
**UNKNOWN**, so `recommend_action` *cannot* compute a net VOI and returns **GATHER_EVIDENCE** — i.e.
run the cheap falsification test (a $5–15K paid pilot / 10 buyer interviews) before building
anything. The machine, run honestly, converges on the same conclusion the human synthesis reached in
[STATE.md](STATE.md), from the opposite direction. That convergence is a feature, not a coincidence:
both refuse to let a large *rational ceiling* masquerade as *observed willingness to pay*.

---

## 4. Objectives stay separate (no magic number)

Every ranking in the engine is **evidence-gated first, then decomposed** — never a single collapsed
score (the discipline inherited from `score.py` and `event_optimizer.pareto_frontier`):

- `problem_matcher` keeps 7 fit dims + a hard gate; `pareto_frontier` returns the non-dominated set.
- `business_model` keeps 9 dims; `pareto` returns non-dominated models.
- `opportunity_matcher` keeps 12 dims; ranking is `(is_live, evidence_strength, spend, gap, advantage, …)`.
- `icp_discovery.rank` and `spend_intensity.rank_categories` lead with **evidence strength**, so a
  well-sourced small cluster beats a large *imagined* one, and a HYPOTHETICAL worked example can
  never outrank real demand-side evidence.

---

## 5. What the engine is allowed to conclude

By construction, the engine can return any of these — none is ruled out a priori:

- the best ICP is **not** technical / not a software company;
- the best product is **not** research (could be prototype procurement, design-partner formation,
  parallel R&D search, a forecasting tournament…);
- the best environment is **not** a 48–72h hackathon (could be online multi-week, a residency, or
  an instrument layered onto someone else's event — "Wedge D");
- the event should be much **smaller** or much **longer**;
- or **the model does not work** — every opportunity can be KILLed by the fit gate, and every
  business model can fail the ethics/defensibility floors.

`UNKNOWN` is a valid and frequent output. That is the point of the reset.

---

## 6. Running it

```bash
# unit + property tests for every module (54 original + new)
cd engine && for t in test_*.py; do python3 "$t"; done

# worked HYPOTHETICAL cases pushed end-to-end through the engine
python3 engine/worked_cases.py
```

The worked cases in [worked-cases](../engine/worked_cases.py) are **HYPOTHETICAL** — illustrations of
the machinery, explicitly **not** market evidence.
