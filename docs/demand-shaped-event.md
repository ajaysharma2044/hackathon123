# Demand-Shaped Event Design

> **Governing rule: Evidence ≠ Claim ≠ Hypothesis ≠ Decision.** The environment is derived **FROM the
> winning gap**, not designed independently. But one thing the demand can never override:
> **ParticipantExperience is a hard constraint** — the event must never become unpaid consulting labor.
> This document describes what [`engine/opportunity_matcher.py`](../engine/opportunity_matcher.py)
> actually implements.

## The flow

The design runs **demand-first**. Instead of "we have a hackathon; who will sponsor it," the chain is
"a buyer has an expensive problem; what environment does that problem require, and only then, is that
environment still a fair deal for builders."

```
HighValueGap ─▶ Buyer ─▶ CommercialProduct ─▶ RequiredParticipants
                                                     │
                                                     ▼
                                             RequiredEnvironment
                                                     │
                                                     ▼
                              EventModule ─▶ EventPortfolio ─▶ FinalHackathonDesign
                                                     ▲
                          ParticipantExperience (HARD CONSTRAINT, cannot be overridden)
```

Where each step lives in code:

| Step | Where | Note |
|---|---|---|
| HighValueGap | `opportunity_matcher.Opportunity` (fuses `spend_intensity.SpendCategory` + `gap_finder.StructuralGap`) | the gap must clear hard gates to be *live* |
| Buyer | `Opportunity.buyer`, gate `buyer_authority` | "someone can sign" |
| CommercialProduct | `Opportunity.business_model` | how it is sold |
| RequiredParticipants | `Problem.mode` → `ARCHETYPES[...].talent_mix` | population-level talent, never individual scoring |
| RequiredEnvironment | `opportunity_matcher.demand_shaped_environment` → `environment_generator.best_feasible` | derived FROM the gap's problem |
| EventModule / EventPortfolio / FinalHackathonDesign | the generated `Environment` + its Pareto set (`environment_generator.generate`) | a set of designs, not one |

## Opportunities: 12 decomposed dims, hard gates

`opportunity_matcher.Opportunity` keeps **12 dimensions decomposed** (`OPP_DIMS`), each ordinal 0..3.
The docstring states the rule verbatim: *"Do not hide weak dimensions inside a single composite score."*
`Opportunity.vector()` returns the labeled dims; there is no collapsed scalar.

`opportunity_matcher.evaluate(...)` assembles an `Opportunity` from a spending war
(`SpendCategory`) + a structural gap (`StructuralGap`) + hand-assessed access/feasibility dims. Two
honesty details:

- **Evidence strength is the weaker of the two sources** — `ev = min(category, gap, key=EVIDENCE_ORDER)`
  ("you cannot be more confident than your weakest input").
- **`hackathon_advantage = min(category.hackathon_fit, gap.hackathon_advantage)`** — a min, not a
  blend, so an advantage claim needs *both* the spend side and the gap side to hold.

### The five hard gates

`Opportunity.is_live` (and the human-readable `Opportunity.verdict()`) require **all** of:

| Gate | Threshold | Meaning |
|---|---|---|
| `existing_spend` | ≥ MED | there is already an active spending war |
| `gap_severity` | ≥ MED | a real "cannot buy this today" |
| `hackathon_advantage` | ≥ MED | we *structurally* win at filling it |
| `buyer_authority` | ≥ LOW | an identifiable buyer who can sign |
| `participant_fit` | ≥ MED | **a fair deal for participants** |

Miss any one → not live, *regardless of how big the market is* (module docstring: "Miss a gate → the
opportunity is not live"). `verdict()` returns the specific SKIP reason for the first failed gate;
notably `participant_fit < MED` returns *"SKIP — would be extractive / poor participant experience
(hard constraint)."*

`rank()` sorts LIVE-first, then evidence-first, then by the decomposed intensity tuple — never one
score. `pareto()` returns non-dominated live opportunities via `dominates()` over all 12 `OPP_DIMS`.

## `demand_shaped_environment(problem)` — the derivation

```python
def demand_shaped_environment(problem):
    best = best_feasible(problem)
    return {
        "problem": problem.statement,
        "required_environment": (best["name"] if best else None),
        "feasible": best is not None,
        "hard_constraint": "ParticipantExperience — the event must remain one of the best builder "
                           "experiences available; demand cannot turn it into unpaid consulting labor.",
    }
```

What this does, precisely (`opportunity_matcher.demand_shaped_environment`):

1. Calls `environment_generator.best_feasible(problem)`, which runs the full demand-first pipeline:
   `archetype_for(problem)` picks the base archetype **from `problem.mode`**, `candidates()` perturbs
   it with `VARIANTS`, `generate()` gates + Pareto-ranks, and the single highest-coverage gate-passing
   design comes back.
2. If nothing clears the structural-advantage gate, `best_feasible` returns `None` →
   `feasible=False`, `required_environment=None`. This is the honest *"we should not attempt this"* —
   the demand does not conjure an environment that has no real advantage.
3. It **always** returns the `hard_constraint` string, whether or not a design was found. The
   constraint is standing, not conditional: the event must remain one of the best builder experiences
   available; demand cannot turn it into unpaid consulting labor.

So the environment is a **function of the winning gap's problem**, resolved through the same mode →
archetype → variants → Pareto machinery documented in
[environment-archetypes.md](environment-archetypes.md). The design is *derived*, not asserted.

## ParticipantExperience is a hard constraint the demand cannot override

This is the one place demand-first design stops. It shows up in **two** enforcement points:

1. **In the opportunity gate** — `participant_fit ≥ MED` is a *live* gate in `Opportunity.is_live`.
   An opportunity that would make the event extractive is not live no matter how large the spend, the
   gap, or the buyer's budget. `verdict()` labels it "extractive / poor participant experience (hard
   constraint)."
2. **In the environment derivation** — `demand_shaped_environment` returns the ParticipantExperience
   reminder unconditionally, encoding it as a standing constraint on any design the demand produces.

This mirrors `event_optimizer.py`, where participant experience is a **hard constraint, not an
objective** (see [event-optimizer.md](event-optimizer.md): *"participant experience ≥ floor … ≥1
unconstrained free-choice surface … no surveillance … no person scoring"*). A buyer's willingness to
pay cannot buy below the experience floor. The economic logic is also in the optimizer's tweak table:
cutting the free-choice surface *raises* nothing worth having and triggers the contamination penalty —
extractive designs are bad research **and** bad experience at once.

## How the event adapts when demand needs something else

Because the environment is generated from `problem.mode`, if the strongest live opportunities point at
a problem whose mode is not DIVERGENCE/PROTOTYPING, the derived design will **not** be a classic
weekend hackathon. Concretely, from `environment_generator.ARCHETYPES`:

| If the winning gap's problem is… | The derived environment differs from a classic hackathon by… |
|---|---|
| FORECASTING | `medium=ONLINE`, `duration_hours=336` (multi-week), `team_size=1`, peer-prediction incentive |
| VENTURE_CREATION | `has_continuation=True`, `capital_access=3`, `followup_waves=3`, continuation-contract incentive, multi-week |
| OPTIMIZATION / SIMULATION | small (80–90), high `data_access`/`instrumentation`, an INTERNAL_MARKET, OR/OPERATIONS talent |
| EXPERIMENTATION | high `instrumentation`, *low* `competition`/`incentive_intensity` (protect behavioral realism) |
| MARKET_DESIGN | an AUCTION market mechanism, QUANT talent |

The knobs that adapt are exactly talent (`talent_mix`, `experience_band`), duration
(`duration_hours`), tools/data (`tool_richness`, `data_access`, `instrumentation`), and medium
(`medium`). If the demand needs senior domain experts rather than elite students, `_talent_match`
(`problem_matcher`) *docks* a junior/elite cohort for a domain-expertise gap — so a demand that needs
domain depth will push the generator toward the `senior_cohort` variant or fail the gate honestly
rather than pretend a student cohort fits.

The prior *"premium in-person software hackathon for devtools research"* thesis is therefore **one
possible output** of this flow (the `hackathon_flagship` point), reached only when the winning gap's
problem actually calls for it — never the assumed answer. Per STATE.md, the in-person flown-in form is
also the **costliest data path** (`COST_ADVANTAGE` penalty), and Wedge D (run the first study on
someone else's event) is the cheaper first instrument; the demand-shaped flow will surface a cheaper
environment whenever the gap permits one.

## Status

| Claim | Status | Why |
|---|---|---|
| The environment is derived from the winning gap (in code) | **KNOWN** | `demand_shaped_environment` → `best_feasible` |
| ParticipantExperience is enforced as a hard constraint | **KNOWN** | `Opportunity.is_live` gate + unconditional reminder string |
| Opportunity gate thresholds (the specific MED/LOW floors) | **LIKELY** (ASSUMED) | explicit ordinals, editable; not measured WTP |
| A rational value ceiling equals observed WTP | **CONTRADICTED** | STATE.md: value-of-information is the *route* to high price, not evidence of it — WTP is UNKNOWN |
| A hackathon is the right derived environment for any given gap | **UNKNOWN until the gap's mode is set** | the mode routes the archetype; hackathon is one output |
