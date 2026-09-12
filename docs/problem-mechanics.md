# Problem Mechanics — the Problem primitive

Documents the code that already exists in [`engine/problem_model.py`](../engine/problem_model.py)
and the tables it mirrors in [`schema/004_environment_economy.sql`](../schema/004_environment_economy.sql)
(`problem`, `problem_mechanics`). Nothing here proposes new behavior; it describes what the file
does.

The governing idea is stated in the module docstring: **problems are characterized by their
MECHANICS, not their industry.** "Retail is a good industry" is useless; "this is a high-
parallelizability, high-prototypeability, low-path-dependence DIVERGENCE problem owned by a COO with
a real budget" is actionable. Industry is retained as a plain string field (`Problem.industry`) but
is never a routing input.

This carries the repo's standing discipline: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**, and the
status vocabulary **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**. A mechanic is a scored structural
observation; an economic magnitude is a belief that stays **UNKNOWN** until evidenced.

## The `Problem` dataclass

`problem_model.Problem` holds three kinds of field, kept deliberately separate:

1. **Descriptive strings** — `statement`, `industry`, `business_unit`, `decision_owner`,
   `budget_owner`, `current_alternative`, `missing_evidence`. All default to `"UNKNOWN"` (or `""`),
   mirroring the `problem` table columns.
2. **Structural mechanics** — 16 ordinal `int` fields, `0..3`, listed in `MECHANIC_DIMS`.
3. **Economic magnitudes** — three `beliefs.Belief` objects (`economic_value`, `cost_of_wrong`,
   `current_cost`) that default to **UNKNOWN** and cannot be fabricated into numbers.

`is_hypothetical: bool = False` is the quarantine flag (see below).

### The ordinal scale

Mechanics use the same ordinal scale as [`engine/score.py`](../engine/score.py) so the two engines
interoperate: `NONE, LOW, MED, HIGH = 0, 1, 2, 3`, with `_LABEL` mapping back to the strings. This
is the honest-precision convention from `score.py` — an ordinal 0..3 maps to human judgement and
never implies false precision.

`Problem.mechanics()` returns the decomposed vector as ordinal **labels** (e.g. `{"parallelizability":
"HIGH", ...}`); `Problem.mechanics_raw()` returns the same as raw ints for the matcher. Neither ever
averages the dimensions into a single number — the docstring of `mechanics()` says so explicitly
("never averaged into one number"). This is the "keep dimensions DECOMPOSED" rule.

## The 16 MECHANIC_DIMS

`MECHANIC_DIMS` (problem_model.py) is the P vector. Each dimension is ordinal `0..3`. Two dimensions
carry an inverted polarity, noted inline in the source and repeated here so the scoring reads
correctly.

| # | Mechanic | Meaning | Polarity note |
|---|---|---|---|
| 1 | `parallelizability` | can many independent teams attack it at once | higher = better |
| 2 | `prototypeability` | can a working artifact be built quickly | higher = better |
| 3 | `experimentability` | can causal interventions be run | higher = better |
| 4 | `feedback_latency` | speed of feedback | **0 = slow (bad), 3 = fast (good)** |
| 5 | `simulation_feasibility` | can it be simulated | higher = better |
| 6 | `behavioral_component` | how much depends on human behavior | descriptive |
| 7 | `technical_component` | technical content | descriptive |
| 8 | `creative_component` | creative content | descriptive |
| 9 | `operational_component` | operations / process content | descriptive |
| 10 | `scientific_component` | scientific content | descriptive |
| 11 | `need_domain_expertise` | how much deep domain knowledge it requires | drives a talent dock |
| 12 | `need_external_perspective` | value of outsider view | higher favors outsiders |
| 13 | `path_dependence` | lock-in to prior state | **0 = low (good for outsiders), 3 = high (bad)** |
| 14 | `internal_political_friction` | internal politics | **0 = low (good), 3 = high (bad)** |
| 15 | `longitudinal_need` | value of long follow-up | higher = better |
| 16 | `repeatability` | can the same solve be sold again | higher = better |

Dimensions 6–10 (the `*_component` fields) describe *what kind of work* the problem is; the matcher
reads them to decide which talent disciplines the population must supply (see
[problem-environment-fit.md](problem-environment-fit.md), `COMPONENT_TALENT`).

## The 11 MODES and why the primary MODE is the key routing variable

`MODES` (problem_model.py) enumerates the 11 problem-solving modes, mirroring the `problem_mode`
enum in schema 004:

`DIVERGENCE, CONVERGENCE, EXPERIMENTATION, OPTIMIZATION, DISCOVERY, PROTOTYPING, FORECASTING,
SIMULATION, RED_TEAMING, VENTURE_CREATION, MARKET_DESIGN`

`Problem.mode` defaults to `"DIVERGENCE"`. The schema comment states the reason directly: the mode
is *"the single most important routing variable: mode → environment shape."* The module docstring
gives the intuition — a DIVERGENCE problem wants many parallel teams; a FORECASTING problem wants a
prediction tournament; an OPTIMIZATION problem wants OR talent plus a simulation. The mode is what
turns a problem into a demand for specific environment capabilities.

## Economic magnitudes are beliefs, default UNKNOWN

The three economic fields are `beliefs.Belief` objects, not floats:

- `economic_value` — value of solving the problem
- `cost_of_wrong` — cost of a wrong decision (drives the VOI ceiling)
- `current_cost` — what they spend on the current alternative

`Problem.__post_init__` fills any of these left as `None` with `beliefs.unknown(...)` — **UNKNOWN**,
not zero. The docstring says it plainly: *"Uninitialised economic beliefs are UNKNOWN, not zero.
This is the whole point."*

This is not decoration. In [`engine/beliefs.py`](../engine/beliefs.py), `Belief.sample` **raises** if
the status is UNKNOWN:

> a belief that is UNKNOWN "may not silently become a number" — it must first be resolved to an
> ASSUMED scenario band.

So a downstream simulation physically cannot draw a value for an unevidenced problem. This enforces
the STATE.md gating discipline in code: value-of-solving and decision-value stay **UNKNOWN** until
evidenced, exactly as WTP does throughout the repo. The `problem` table mirrors this with
`*_belief_id` columns (`economic_value_belief_id`, `cost_of_wrong_belief_id`,
`current_cost_belief_id`) that reference belief rows and are UNKNOWN by default.

## `is_hypothetical` — the worked-example quarantine

`is_hypothetical: bool = False`. When `True`, the problem is a worked illustration, **not market
evidence**. The module docstring: worked-example problems *"are illustrations, NOT market evidence,
and downstream code must never treat them as demand-side proof."*

This mirrors schema 004's `demand_evidence_kind` enum, whose weakest value is `HYPOTHETICAL`
(*"invented for a worked example; NOT market evidence"*) and whose comment notes a hypothetical row
*"is quarantined by this tag."* The distinction matters because the whole engine exists to avoid the
supply-side bias STATE.md diagnoses: a hypothetical problem is a supply-side construction, and
counting it as demand would re-introduce exactly the confirmation error the frame correction warns
against. A real problem row, by contrast, requires at least one `problem_evidence` citation.

## MODE_CAPABILITY_NEEDS — mode → essential capabilities

`MODE_CAPABILITY_NEEDS` (problem_model.py) maps each mode to the environment capabilities it most
requires. The docstring flags these as an **ASSUMED** mapping, "kept explicit and editable." The
values are capability keys drawn from `environment.CAPABILITIES` (see
[`engine/environment.py`](../engine/environment.py)); the matcher gates on the subset for the
problem's mode.

| Mode | Essential capabilities (MODE_CAPABILITY_NEEDS) |
|---|---|
| `DIVERGENCE` | PARALLEL_SEARCH, SOLUTION_DIVERSITY, EXTERNAL_TALENT_ADVANTAGE |
| `CONVERGENCE` | COUNTERFACTUAL_QUALITY, FEEDBACK_SPEED, ARTIFACT_VALUE |
| `EXPERIMENTATION` | EXPERIMENTABILITY, MANIPULABILITY, OBSERVABILITY, COUNTERFACTUAL_QUALITY |
| `OPTIMIZATION` | SIMULATION_FEASIBILITY, PROTOTYPEABILITY, INTERDISCIPLINARY_ADVANTAGE |
| `DISCOVERY` | SOLUTION_DIVERSITY, EXTERNAL_TALENT_ADVANTAGE, PARALLEL_SEARCH |
| `PROTOTYPING` | PROTOTYPEABILITY, ARTIFACT_VALUE, TIME_COMPRESSION |
| `FORECASTING` | COUNTERFACTUAL_QUALITY, OBSERVABILITY, MANIPULABILITY |
| `SIMULATION` | SIMULATION_FEASIBILITY, MANIPULABILITY, EXPERIMENTABILITY |
| `RED_TEAMING` | PARALLEL_SEARCH, VALUE_OF_FAILURE, EXTERNAL_TALENT_ADVANTAGE |
| `VENTURE_CREATION` | ARTIFACT_VALUE, LONGITUDINAL_CAPTURE, EXTERNAL_TALENT_ADVANTAGE |
| `MARKET_DESIGN` | MANIPULABILITY, SIMULATION_FEASIBILITY, EXPERIMENTABILITY |

These are the *essential* capabilities: `problem_matcher.match` takes the **min** over this list as
the environment's structural advantage, so missing any one of them kills the pair (see the hard gate
in [problem-environment-fit.md](problem-environment-fit.md)).

## required_capabilities — mode needs plus structural augmentation

`required_capabilities(problem)` (problem_model.py) returns the full list of capabilities a problem
needs: the mode's needs **augmented by the problem's own structure**. Beyond the mode baseline, it
appends a capability whenever a mechanic reaches `MED` or higher:

| Mechanic at ≥ MED | Adds capability |
|---|---|
| `parallelizability` | PARALLEL_SEARCH |
| `prototypeability` | PROTOTYPEABILITY |
| `simulation_feasibility` | SIMULATION_FEASIBILITY |
| `longitudinal_need` | LONGITUDINAL_CAPTURE |
| `need_external_perspective` | EXTERNAL_TALENT_ADVANTAGE |
| `experimentability` | EXPERIMENTABILITY |

The result is de-duplicated with order preserved. Note the split in how the two capability lists are
used by the matcher: `MODE_CAPABILITY_NEEDS` (mode-essential) drives the **hard gate** via a min;
`required_capabilities` (the augmented, broader list) drives **coverage**, a softer ranking aid — it
is counted, never gated on. The distinction is deliberate: a problem can need many capabilities, but
only the mode-essential few are allowed to kill the match.

## What this primitive is and is not

- It **is** a decomposed, honestly-scored structural description of an expensive problem, with its
  economic weight held as evidence-gated beliefs.
- It is **not** a scored verdict. `Problem` produces no single number; scoring a problem against an
  environment is the matcher's job, and even there the dimensions stay decomposed.
- It **never** scores individual people. Talent enters only at the population level, downstream, in
  the matcher and allocator — a hard ethical boundary in the repo (see
  [talent-configuration.md](talent-configuration.md)).
