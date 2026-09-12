# Environment → Capability Map

> **Governing rule: Evidence ≠ Claim ≠ Hypothesis ≠ Decision.** This document describes machinery that
> *exists* in [`engine/environment.py`](../engine/environment.py). The machinery is real; the numbers
> inside it are not measurements. Every coefficient that maps a configuration to a capability is an
> **ASSUMPTION**, collected in one dict `A` precisely so it is obvious that it is assumed
> (`environment.A`). The value here is the *structure* — which knob moves which capability, and in
> which direction — **not** the magnitudes.

## The Environment primitive E

`environment.Environment` is a frozen dataclass: a *configurable temporary organization*. It
generalizes the old `event_optimizer.EventDesign`, which hardcoded a 200-person, 72-hour, flown-in
software hackathon. Here the environment is the object under design, and every field is a **decision
variable** (a company brings a problem; the generator proposes values).

The docstring names the 14-tuple:

```
E = (Talent, Information, Tools, Capital, Incentives, Constraints, Time, Competition,
     Collaboration, Feedback, Governance, MarketMechanism, PhysicalEnvironment, DigitalEnvironment)
```

The dataclass fields group under those 14 elements as follows (see `environment.Environment`):

| E-element | Fields (`Environment.*`) | Type / range |
|---|---|---|
| Talent | `n_participants`, `talent_mix`, `interdisciplinarity`, `selectivity`, `experience_band`, `team_size` | mix of shares; floats 0..1; band enum |
| Information | `information_asymmetry`, `data_access` | 0..1; ordinal 0..3 |
| Tools / Digital | `tool_richness`, `instrumentation` | ordinal 0..3 each |
| Capital | `prize_pool`, `capital_access` | dollars; ordinal 0..3 |
| Incentives | `incentive`, `incentive_intensity` | enum; float 0..1 |
| Constraints | `constraints` | tuple of hard rules |
| Time | `duration_hours`, `has_continuation`, `followup_waves` | hours; bool; int |
| Competition | `competition` | float 0..1 |
| Collaboration | `collaboration`, `team_size` | float 0..1; int |
| Feedback | `feedback_cadence` | ordinal 0..3 |
| Governance | `judging`, `ip_terms` | enums |
| MarketMechanism | `market_mechanism` | `NONE / INTERNAL_MARKET / AUCTION / PROCUREMENT` |
| PhysicalEnvironment | `medium` | `IN_PERSON / ONLINE / HYBRID` |

A hackathon is **one point** in this space, expressed by `environment.hackathon_flagship()` — not the
space itself. The docstring says so directly: *"A hackathon is ONE point in this space … not the
space."* The prior "premium software hackathon for devtools research" thesis is therefore *a* point
here, never *the* answer.

The persistence side of the same primitive lives in
[`schema/008_environment_economy.sql`](../schema/008_environment_economy.sql): `environment_design`
carries the full 14-tuple in a `decision_vector jsonb`, `environment_archetype` registers archetypes
(a hackathon is one row), `environment_capability` stores the decomposed capability profile one row
per capability (`basis` = `ASSUMED | OBSERVED`), and `talent_configuration` models talent at the
population level, never by scoring individuals.

## The 21 capabilities (never one score)

Capabilities are returned as a **decomposed 21-dim vector**, mirroring `score.py`'s discipline that
dimensions are never averaged away. The list is fixed in `environment.CAPABILITIES` (and matches the
`environment_capability_kind` enum in schema 004). Two functions produce it:

- `environment.capability_scores(env)` — continuous latent scores (an ASSUMED structural model, `A`).
- `environment.capability_vector(env)` — those scores bucketed to ordinal **0..3** (NONE/LOW/MED/HIGH)
  via `environment._bucket` against ASSUMED per-capability bands.

Both return **all 21 dims**. Nothing collapses them to a scalar. `environment.tweak(env, **changes)`
returns the per-capability *delta* of changing one knob (mirrors `event_optimizer.tweak`).

The model is deliberately **structural** — thresholds and sums of labeled contributions — rather than
fitted coefficients the project does not have. Monotonicity (more participants → more parallel search)
is the property the tests pin; the magnitudes are not claims.

### Capability → driving knobs (from `capability_scores`)

For each capability: the knobs that drive it and the **direction** (↑ increases, ↓ decreases the
score). All coefficients named `A[...]` are ASSUMED (`environment.A`).

| Capability | Formula drivers (`Environment.*`) | Direction |
|---|---|---|
| PARALLEL_SEARCH | `teams = n_participants/team_size` via `log1p`, weight `A["parallel_k"]` | more participants ↑, larger `team_size` ↓ (sublinear) |
| SOLUTION_DIVERSITY | `interdisciplinarity`×`_n_disciplines`, `competition`, `log1p(teams)` | interdisciplinarity ↑, competition ↑, teams ↑ |
| FEEDBACK_SPEED | `feedback_cadence`, in-person bonus `A["inperson_feedback_bonus"]` | cadence ↑, IN_PERSON ↑ (HYBRID half) |
| PROTOTYPEABILITY | `tool_richness`, SOFTWARE share, `data_access` | tools ↑, software-heavy mix ↑, data ↑ |
| EXPERIMENTABILITY | `data_access`, `feedback_cadence`, `market_mechanism != NONE` | data ↑, cadence ↑, having a market ↑ |
| BEHAVIORAL_REALISM | in-person bonus, `data_access`, **minus** `incentive_intensity`×`A["behavioral_incentive_penalty"]` | IN_PERSON ↑, data ↑, **heavy prizes ↓** (contaminate natural behavior) |
| MANIPULABILITY | `feedback_cadence`, `market_mechanism != NONE` | cadence ↑, market ↑ (can we inject shocks/treatments?) |
| COUNTERFACTUAL_QUALITY | `feedback_cadence`, `competition>0.3`, `teams>=8` | cadence ↑, competition present ↑, ≥8 teams ↑ |
| OBSERVABILITY | `instrumentation`×`A["observability_digital_w"]`, in-person | instrumentation ↑, IN_PERSON ↑ |
| ARTIFACT_VALUE | `tool_richness`, `data_access`, `capital_access` | all ↑ |
| TIME_COMPRESSION | `log1p(teams)` ÷ duration term, weight `A["time_compression_w"]` | teams ↑, **longer `duration_hours` ↓** |
| INTERDISCIPLINARY_ADVANTAGE | `interdisciplinarity`×`_n_disciplines` | both ↑ |
| EXTERNAL_TALENT_ADVANTAGE | `selectivity`, `experience_band ∈ {SENIOR,MIXED}` | selectivity ↑, senior/mixed ↑ |
| SIMULATION_FEASIBILITY | `data_access`, `market_mechanism != NONE`, `tool_richness` | all ↑ |
| LONGITUDINAL_CAPTURE | `followup_waves`×`A["longitudinal_followup_w"]`, `has_continuation` | waves ↑, continuation ↑ |
| EXTERNAL_VALIDITY | base 2.0 **minus** `selectivity`×`A["external_validity_selectivity_penalty"]`, plus `data_access`, `has_continuation` | **elite selectivity ↓**, data ↑, continuation ↑ |
| REPEATABILITY | `archetype != BESPOKE`, `followup_waves>0` | templated ↑, has waves ↑ |
| DEFENSIBILITY | `followup_waves`, `has_continuation`, `instrumentation` | all ↑ |
| COST_ADVANTAGE | base 3.0 **minus** in-person penalty `A["cost_advantage_inperson_penalty"]`, **minus** `n_participants>150` | **IN_PERSON ↓**, large N ↓ |
| SPEED_ADVANTAGE | `log1p(teams)` ÷ duration term | teams ↑, longer duration ↓ |
| VALUE_OF_FAILURE | `log1p(teams)`×`A["value_of_failure_parallel_w"]`, `competition` | many parallel attempts ↑, competition ↑ |

Four caveats from `docs/STATE.md` are hard-wired into the *signs* above, and must be preserved:

- **Elite selectivity HURTS external validity.** `EXTERNAL_VALIDITY` subtracts a selectivity penalty
  (`A["external_validity_selectivity_penalty"]`). High selectivity buys prestige and pays for it in
  representativeness.
- **In-person flown-in is the COSTLIEST data path.** `COST_ADVANTAGE` subtracts an in-person penalty
  (`A["cost_advantage_inperson_penalty"]`); it is *lower* (worse) precisely when `medium="IN_PERSON"`.
- **Heavy incentives contaminate behavioral realism.** `BEHAVIORAL_REALISM` subtracts
  `incentive_intensity`×`A["behavioral_incentive_penalty"]` — prize money corrupts the "free tool
  choice" the research depends on.
- **Longitudinal follow-up is the differentiator — and it is UNTESTED.** `LONGITUDINAL_CAPTURE`,
  `DEFENSIBILITY`, and `REPEATABILITY` all reward `followup_waves`/`has_continuation`. The code models
  panel retention as valuable; STATE.md flags that retention into 7/30/90-day tracking is **untested**
  in reality. The model assigns it value; the world has not confirmed it.

## Bucketing: latent → ordinal 0..3

`environment.capability_vector` maps each latent score to an ordinal via `environment._bucket(x, lo, hi)`:
`q = (x-lo)/(hi-lo)`, then `floor(q*4)` clipped to 0..3 → NONE / LOW / MED / HIGH. The per-capability
`(lo, hi)` bands are **ASSUMED** (`capability_vector.bands`), chosen so a flagship hackathon lands
mid-range, leaving room above *and* below for other archetypes. Note the bands are not uniform: e.g.
`BEHAVIORAL_REALISM` is banded `(-1, 3)` (it can go negative under heavy incentives),
`ARTIFACT_VALUE` and `LONGITUDINAL_CAPTURE` are `(0, 6)`.

The ordinal buckets are what the matcher gates on
([`engine/problem_matcher.py`](../engine/problem_matcher.py) `match`, floor `FIT_ADVANTAGE_FLOOR = MED`),
and what schema 004 stores in `environment_capability.score` (a `check (score between 0 and 3)`).

## A hackathon is one point: flagship vs. with-panel

`environment.hackathon_flagship()` and `environment.hackathon_with_panel()` are two named reference
points. They differ **only** in the longitudinal knobs — `hackathon_with_panel()` is
`replace(hackathon_flagship(), has_continuation=True, followup_waves=3)`. That single change is the
STATE.md "untested moat engine." The computed vectors (verbatim from the engine):

| Capability | flagship raw → vec | with-panel raw → vec | changed? |
|---|---|---|---|
| PARALLEL_SEARCH | 3.539 → 2 | 3.539 → 2 | |
| SOLUTION_DIVERSITY | 2.260 → 2 | 2.260 → 2 | |
| FEEDBACK_SPEED | 2.500 → 2 | 2.500 → 2 | |
| PROTOTYPEABILITY | 2.650 → 2 | 2.650 → 2 | |
| EXPERIMENTABILITY | 1.600 → 1 | 1.600 → 1 | |
| BEHAVIORAL_REALISM | 1.100 → 2 | 1.100 → 2 | |
| MANIPULABILITY | 2.000 → 2 | 2.000 → 2 | |
| COUNTERFACTUAL_QUALITY | 2.400 → 3 | 2.400 → 3 | |
| OBSERVABILITY | 2.400 → 2 | 2.400 → 2 | |
| ARTIFACT_VALUE | 3.000 → 2 | 3.000 → 2 | |
| TIME_COMPRESSION | 2.932 → 3 | 2.932 → 3 | |
| INTERDISCIPLINARY_ADVANTAGE | 0.720 → 1 | 0.720 → 1 | |
| EXTERNAL_TALENT_ADVANTAGE | 0.950 → 2 | 0.950 → 2 | |
| SIMULATION_FEASIBILITY | 1.500 → 1 | 1.500 → 1 | |
| **LONGITUDINAL_CAPTURE** | 0.000 → **0** | 5.500 → **3** | ✅ |
| **EXTERNAL_VALIDITY** | 1.835 → **1** | 2.135 → **2** | ✅ |
| **REPEATABILITY** | 1.500 → **2** | 2.000 → **2** | (raw ↑, bucket same) |
| **DEFENSIBILITY** | 0.800 → **0** | 3.100 → **3** | ✅ |
| COST_ADVANTAGE | 1.600 → 2 | 1.600 → 2 | |
| SPEED_ADVANTAGE | 2.932 → 2 | 2.932 → 2 | |
| VALUE_OF_FAILURE | 3.052 → 3 | 3.052 → 3 | |

Adding the follow-up panel moves exactly three ordinal buckets — `LONGITUDINAL_CAPTURE` 0→3,
`DEFENSIBILITY` 0→3, `EXTERNAL_VALIDITY` 1→2 (and `REPEATABILITY`'s latent rises without crossing a
bucket boundary). Everything a weekend produces in a room — parallel search, prototypeability, time
compression — is identical between the two. **The panel is the whole delta**, and per STATE.md it is
the differentiator whose real-world retention is still UNKNOWN.

## Status of the load-bearing pieces

| Piece | Status | Why |
|---|---|---|
| The 14-tuple / 21-cap structure exists in code | **KNOWN** | `environment.py`, mirrored in schema 004 |
| Direction of each knob→capability (the signs) | **LIKELY** (design intent) | structural, monotonic, test-pinned; not measured |
| Magnitudes of the `A` coefficients and bands | **UNKNOWN** (ASSUMED) | stated plainly in `environment.A` and `capability_vector.bands` |
| Panel (`followup_waves`) is the flagship's real moat | **LIKELY** as design; retention **UNKNOWN** | STATE.md caveat #6: longitudinal retention untested |
| Premium in-person hackathon is *the* optimum | **CONTRADICTED** | it is one point (`hackathon_flagship`); costliest data path; better options exist per mode |

Because `capability_vector` returns ordinals and the matcher gates on a **MED floor per essential
capability**, an UNKNOWN/NONE on a mode-essential capability cannot be averaged away by strength
elsewhere — the pair is killed. Keep every dimension visible; do not collapse to one score.
