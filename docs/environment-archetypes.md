# Environment Archetypes

> **Governing rule: Evidence ≠ Claim ≠ Hypothesis ≠ Decision.** The archetype templates in
> [`engine/environment_generator.py`](../engine/environment_generator.py) (`ARCHETYPES`) are
> **ASSUMED structural priors** — which knobs a FORECASTING problem wants vs. an OPTIMIZATION problem —
> **not fitted values**. The generator's docstring says so directly. The output is a **Pareto set of
> designs, never a single "optimal,"** so the tradeoffs (cost vs. behavioral realism vs. external
> validity) stay visible.

## What the module does

The prior engine could only *optimize* a fixed hackathon (`event_optimizer.tweak` over an
`EventDesign`). `environment_generator` *generates* an environment for a given problem:

1. `archetype_for(problem)` picks a base `Environment` from `ARCHETYPES` keyed on `problem.mode`
   (falls back to `ARCHETYPES["DIVERGENCE"]` if the mode is unknown).
2. `candidates(problem)` = that base × the `VARIANTS` knob perturbations.
3. `generate(problem, top)` scores each with `problem_matcher.match`, keeps gate-passing designs,
   computes the Pareto frontier over the fit vector, and returns a ranked list **with flags** — never
   one winner.
4. `best_feasible(problem)` returns the single highest-coverage gate-passing design, or `None` — an
   honest *"we should not attempt this."*

A traditional 48–72h in-person hackathon is **one** archetype (`hackathon_flagship`, and closest to
`INNOVATION_TOURNAMENT` / `BUILD_SPRINT`). It is **not optimal for several modes** — see the
"wrong choice" column throughout. Each archetype is one row of the design space, mirroring
`environment_archetype` in [`schema/008_environment_economy.sql`](../schema/008_environment_economy.sql)
(`is_hackathon_like boolean`, `primary_mode problem_mode`).

## The archetypes

Every archetype below is a `dict` of knob overrides on `Environment` (`environment_generator.ARCHETYPES`),
keyed by the `problem_mode` it serves. Knob values shown are the ones the template actually sets;
unset knobs keep `Environment`'s defaults.

### INNOVATION_TOURNAMENT — mode `DIVERGENCE`
- **Key knobs:** `n_participants=180`, `team_size=3`, `competition=0.8`, `interdisciplinarity=0.6`,
  `duration_hours=60`, mixed SOFTWARE/DESIGN/PRODUCT/BUSINESS talent.
- **Good at:** many radically different solutions — high competition + interdisciplinary mix drives
  `SOLUTION_DIVERSITY` and `PARALLEL_SEARCH` (the `DIVERGENCE` essentials in `MODE_CAPABILITY_NEEDS`).
- **Wrong choice when:** the problem needs *causal* answers (EXPERIMENTATION) or deep domain expertise
  — a broad student mix and short clock give little `OBSERVABILITY`/`MANIPULABILITY` and get docked on
  `talent_match` for domain gaps (`problem_matcher._talent_match`).

### OPEN_INNOVATION_CHALLENGE — mode `DISCOVERY`
- **Key knobs:** `n_participants=200`, `team_size=3`, `competition=0.7`, `interdisciplinarity=0.7`,
  `duration_hours=72`, SOFTWARE/DESIGN/SCIENCE/BUSINESS.
- **Good at:** surfacing unknown opportunities/problems — breadth of talent + parallel teams
  (`SOLUTION_DIVERSITY`, `EXTERNAL_TALENT_ADVANTAGE`, `PARALLEL_SEARCH`).
- **Wrong choice when:** the buyer already knows the options and needs a pick (CONVERGENCE), or wants
  build-out depth over surface-area.

### OPERATIONS_WAR_ROOM — mode `OPTIMIZATION`
- **Key knobs:** `n_participants=90`, `team_size=4`, `data_access=3`, `instrumentation=3`,
  `feedback_cadence=3`, `market_mechanism="INTERNAL_MARKET"`, OR_IE/DATA_SCIENCE/SOFTWARE.
- **Good at:** best allocation / system configuration — high data + feedback + a market mechanism
  drive `SIMULATION_FEASIBILITY` and `EXPERIMENTABILITY`.
- **Wrong choice when:** you want wild divergence — small, tightly-instrumented, OR-heavy setups
  narrow the search rather than widen it.

### PRODUCT_LABORATORY — mode `EXPERIMENTATION`
- **Key knobs:** `n_participants=150`, `team_size=4`, `instrumentation=3`, `data_access=2`,
  `feedback_cadence=3`, `competition=0.4`, `incentive_intensity=0.3`.
- **Good at:** testing causal interventions — high instrumentation → `OBSERVABILITY`/`MANIPULABILITY`;
  and note the *deliberately low* `competition`/`incentive_intensity`, because heavy prizes contaminate
  `BEHAVIORAL_REALISM` (the `A["behavioral_incentive_penalty"]` term).
- **Wrong choice when:** the goal is maximum solution count or venture formation — the low-competition,
  controlled design trades diversity for clean causal reads.

### BUILD_SPRINT — mode `PROTOTYPING`
- **Key knobs:** `n_participants=120`, `team_size=4`, `tool_richness=3`, `data_access=2`,
  `duration_hours=72`.
- **Good at:** shippable artifacts / feasibility demos — `PROTOTYPEABILITY`, `ARTIFACT_VALUE`,
  `TIME_COMPRESSION` (the `PROTOTYPING` essentials). This is the archetype closest to a classic
  weekend hackathon.
- **Wrong choice when:** the problem is FORECASTING or MARKET_DESIGN — a build sprint produces demos,
  not calibrated predictions or tested mechanisms.

### FORECASTING_TOURNAMENT — mode `FORECASTING`
- **Key knobs:** `n_participants=200`, `team_size=1`, **`medium="ONLINE"`**, `incentive="PEER_PREDICTION"`,
  `incentive_intensity=0.4`, `feedback_cadence=3`, **`followup_waves=3`, `has_continuation=True`,
  `duration_hours=336`** (two weeks), QUANT/DATA_SCIENCE/SCIENCE.
- **Good at:** predicting uncertain outcomes — individual online forecasters over weeks, peer-prediction
  scoring, `COUNTERFACTUAL_QUALITY`/`OBSERVABILITY`.
- **Wrong choice when:** you reach for a 48–72h in-person hackathon. **FORECASTING explicitly wants an
  online, multi-week tournament** — the template sets `medium=ONLINE`, `duration_hours=336`, and
  `team_size=1`. A flown-in weekend event is the wrong shape for this mode.

### CRISIS_SIMULATION — mode `SIMULATION`
- **Key knobs:** `n_participants=80`, `team_size=5`, `data_access=3`, `instrumentation=3`,
  `feedback_cadence=3`, `market_mechanism="INTERNAL_MARKET"`, OR_IE/OPERATIONS/SOFTWARE.
- **Good at:** testing decisions against scenarios — high data + market + instrumentation drive
  `SIMULATION_FEASIBILITY`, `MANIPULABILITY`, `EXPERIMENTABILITY`.
- **Wrong choice when:** you want breadth of external ideas — it is small, operational, and controlled.

### RED_TEAM_ARENA — mode `RED_TEAMING`
- **Key knobs:** `n_participants=160`, `team_size=3`, `competition=0.9`, `instrumentation=3`,
  SOFTWARE-heavy + SCIENCE + OR_IE.
- **Good at:** finding vulnerabilities / failure modes — very high competition + many teams drive
  `PARALLEL_SEARCH` and `VALUE_OF_FAILURE` (informative negative results, `A["value_of_failure_parallel_w"]`).
- **Wrong choice when:** the deliverable is a single built product or a venture — adversarial search is
  not construction.

### VENTURE_FOUNDRY — mode `VENTURE_CREATION`
- **Key knobs:** `n_participants=120`, `team_size=3`, **`capital_access=3`, `has_continuation=True`,
  `followup_waves=3`**, `incentive="CONTINUATION_CONTRACT"`, **`duration_hours=336`**, `competition=0.5`,
  SOFTWARE/BUSINESS/PRODUCT.
- **Good at:** forming companies around problem spaces — capital + continuation + longitudinal waves
  drive `ARTIFACT_VALUE`, `LONGITUDINAL_CAPTURE`, `EXTERNAL_TALENT_ADVANTAGE` (the essentials).
- **Wrong choice when:** you reach for a weekend hackathon. **VENTURE_CREATION wants continuation +
  capital** — the template sets `capital_access=3`, `has_continuation=True`, and a multi-week clock. A
  72h prize event with `PARTICIPANT_OWNS` IP and no capital cannot form companies.

### MARKET_LABORATORY — mode `MARKET_DESIGN`
- **Key knobs:** `n_participants=100`, `team_size=3`, **`market_mechanism="AUCTION"`**,
  `instrumentation=3`, `data_access=2`, `feedback_cadence=3`, QUANT/OR_IE/SOFTWARE.
- **Good at:** designing incentives / rules / mechanisms — a live market + instrumentation drive
  `MANIPULABILITY`, `SIMULATION_FEASIBILITY`, `EXPERIMENTABILITY`.
- **Wrong choice when:** the problem is creative/product convergence or pure prototyping.

### DESIGN_MARKET — mode `CONVERGENCE`
- **Key knobs:** `n_participants=120`, `team_size=3`, **`judging="CUSTOMER_VOTE"`**, `competition=0.5`,
  `feedback_cadence=3`, DESIGN/PRODUCT/SOFTWARE.
- **Good at:** picking the best among known options — customer-vote governance + fast feedback drive
  `COUNTERFACTUAL_QUALITY`, `FEEDBACK_SPEED`, `ARTIFACT_VALUE` (the CONVERGENCE essentials).
- **Wrong choice when:** the options are not yet known (that is DISCOVERY/DIVERGENCE).

> `environment_generator.ARCHETYPES` currently defines the eleven archetypes above (one per non-fallback
> mode). `environment_archetype` in schema 004 is an open registry, so others (e.g. `R_AND_D_ARENA`,
> `BESPOKE`) can be added as rows without a migration; the code path today generates from these eleven.

## VARIANTS — perturbing each base to build the frontier

`environment_generator.VARIANTS` maps a label to field overrides. `candidates()` applies each variant
to the mode's base archetype, producing the candidate set the Pareto search runs over:

| Variant | Override(s) | What it probes |
|---|---|---|
| `base` | *(none)* | the archetype as-is |
| `in_person` | `medium="IN_PERSON"` | behavioral realism/feedback ↑ vs. `COST_ADVANTAGE` ↓ (costliest data path) |
| `hybrid` | `medium="HYBRID"` | the middle of the medium tradeoff |
| `with_panel` | `has_continuation=True`, `followup_waves=3` | the longitudinal moat (LONGITUDINAL_CAPTURE, DEFENSIBILITY) — retention UNTESTED |
| `senior_cohort` | `experience_band="SENIOR"`, `selectivity=0.7` | trades some selectivity for domain expertise / external validity |
| `larger` | `n_participants=300` | more parallel search vs. cost/experience |
| `smaller_deep` | `n_participants=60`, `duration_hours=240` | depth over breadth (long, small) |

These variants are exactly the axes STATE.md's caveats live on: `in_person` is the costliest data path,
`senior_cohort` relaxes the selectivity that hurts external validity, and `with_panel` is the untested
longitudinal engine. The variants make those tradeoffs *visible as separate candidates*, rather than
baking one choice in.

## `generate()` produces a Pareto set, not a winner

`generate(problem, top=5)`:

1. Scores every candidate with `problem_matcher.match(problem, env)` → a decomposed 7-dim `fit`
   vector, a `gate_passed` boolean, `env_advantage`, and `coverage`.
2. Restricts to gate-passing designs (`m["gate_passed"]`). The gate is the hard structural-advantage
   floor: `env_advantage = min(cap[c] for essential c) ≥ FIT_ADVANTAGE_FLOOR (MED)`
   (`problem_matcher.match`). One weak essential capability kills the pair — a big design cannot buy
   its way onto the frontier.
3. Computes the Pareto frontier over the `fit` vector using `problem_matcher.dominates` (a design is on
   the frontier if no other gate-passing design dominates it on all 7 fit dims).
4. Returns dicts `{name, env, match, on_pareto}` sorted by
   `(gate_passed, on_pareto, coverage, env_advantage)` — **flags preserved**, tradeoffs visible.

`coverage` is explicitly *"only a ranking aid, not a collapse"* (`problem_matcher` docstring); the fit
dimensions are never averaged. `best_feasible()` is the one place a single design is returned, and it
returns `None` when nothing clears the gate — the honest null result. This mirrors
`problem_environment_fit` in schema 004 (`fit_gate_passed`, `on_pareto`), which stores non-dominated
(problem, environment) pairs, not a scalar.

## Status of the archetype layer

| Claim | Status | Why |
|---|---|---|
| The generator maps mode → base archetype → variants → Pareto set (in code) | **KNOWN** | `environment_generator.py` |
| Which knobs each mode "wants" (the templates) | **LIKELY** (ASSUMED priors) | structural, editable; not fitted — stated in the docstring |
| A weekend in-person hackathon is one archetype among many | **KNOWN** | it is `BUILD_SPRINT`/`INNOVATION_TOURNAMENT`, `hackathon_flagship` |
| A weekend hackathon is *optimal* across modes | **CONTRADICTED** | FORECASTING wants online multi-week; VENTURE_CREATION wants continuation + capital |
| The `with_panel` longitudinal variant delivers a retained panel | **UNKNOWN** | STATE.md: longitudinal retention untested |
