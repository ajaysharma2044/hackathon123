# Talent Configuration — talent as a decision variable

Documents the code in [`engine/talent_allocator.py`](../engine/talent_allocator.py) and the
`talent_configuration` table in
[`schema/004_environment_economy.sql`](../schema/004_environment_economy.sql). It describes what the
allocator already does; it invents no behavior.

Talent here is a **decision variable**, not a fixed input: given a problem portfolio, a configured
population, and scarce shared resources, the allocator chooses how many teams attack each problem.
Two disciplines are carried over verbatim from the module docstring:

1. **Population-level only.** *"We allocate at the POPULATION / team level and NEVER score individual
   humans (Phase 2, and the capture-risk-register.md hard boundary 'no person scoring')."*
2. **Solution diversity is a first-class objective**, not a tiebreaker. *"20 teams all piling onto
   one problem is usually worse than spreading them (Phase 27: 'when are 100 independent solutions
   worse than one expert team?' is exactly the tradeoff this exposes)."*

## The ethical boundary: no person scoring, ever

This is not a style note; it is a hard boundary in the repo. `talent_configuration`
(schema 004) stores one row per **capability band's share of the configured population** —
`capability_label`, `population_share`, `experience_band`, `scarcity_note` — with a comment stating
talent is *"modelled at the POPULATION level, never by scoring individuals (Phase 2 / Phase 14)."*

Every talent input the allocator consumes is a population aggregate: a `ProblemDemand.value_per_team`
(value per team, not per person) and, upstream in the matcher, `env.talent_mix` shares. No function
in `talent_allocator.py` accepts, produces, or ranks an individual. This matches the research-modules
boundary for the Talent-Evidence and Startup-Continuation modules — descriptive work-evidence at
individual grain is opt-in and never a score; the allocator does not even operate at that grain. A
person is never an object in this engine.

## ProblemDemand — the unit of allocation

`talent_allocator.ProblemDemand` is a dataclass describing one problem's demand for teams:

| Field | Meaning |
|---|---|
| `name` | problem identifier |
| `value_per_team` | expected value contribution per team assigned (from fit/economics) |
| `mentor_hours_per_team` | mentor hours one team consumes (default 0.0) |
| `compute_per_team` | compute one team consumes (default 0.0) |
| `mode` | the problem's mode (default `"DIVERGENCE"`) |
| `max_teams` | cap on *useful* parallel teams — diminishing returns beyond this (default 6) |

`value_per_team` is deliberately a per-team belief-derived expectation, not a raw dollar figure; it
carries the economics/fit judgement forward without re-introducing a fabricated number. `max_teams`
encodes the diminishing-returns reality that piling teams on one problem eventually stops adding
value.

## allocate — exact enumeration over a decomposed objective

`allocate(demands, n_teams, mentor_capacity, compute_capacity, diversity_weight=1.0)` solves the
assignment **exactly by bounded enumeration** — the docstring notes "team/problem counts are small,"
so `itertools.product` over each demand's `range(0, min(max_teams, n_teams) + 1)` is tractable and
avoids the false precision of an approximate optimizer.

For each candidate team-count combination it enforces the **hard capacity constraints** and skips
any combination that violates one:

```
if sum(combo) > n_teams:            continue   # team budget
mentor  = sum(c * d.mentor_hours_per_team ...)
compute = sum(c * d.compute_per_team ...)
if mentor > mentor_capacity or compute > compute_capacity:   continue
```

These are constraints, not penalties — an infeasible allocation is discarded, never scored down. This
mirrors the hard-gate discipline used elsewhere in the engine: a big expected value cannot buy past a
capacity limit.

The objective it maximizes is **decomposed** and reported decomposed:

```
value     = sum(c * d.value_per_team for c, d in zip(combo, demands))
diversity = sum(1 for c in combo if c > 0)          # DISTINCT problems that got >=1 team
objective = value + diversity_weight * diversity
```

Diversity is counted per **distinct problem that receives at least one team**, so parallel breadth is
valued in the objective itself, not applied as a tiebreak. The returned `best` dict keeps `value`,
`diversity`, `teams_used`, `mentor_hours_used`, `compute_used`, and a `slack` sub-dict (unused teams,
mentor hours, compute) all separate — the raw components stay visible rather than collapsing into one
opaque score.

### The tradeoff it exposes: breadth vs. piling on

Because `diversity` enters the objective additively and `max_teams` caps useful parallelism per
problem, `allocate` will, at a high enough `diversity_weight`, prefer spreading teams across several
distinct problems over concentrating them on one. This is Phase 27's question made operational:
**when are 100 independent solutions worse than one expert team?** The engine does not answer it with
a slogan; it exposes the tradeoff as a tunable term (`diversity_weight`) against per-problem
`value_per_team` and the `max_teams` diminishing-returns cap, so the tradeoff is inspectable and
adjustable rather than hidden. Twenty teams on one problem scores high on `value` only up to that
problem's `max_teams`, then the marginal team adds nothing — while assigning it to a fresh problem
adds both its value and a diversity point.

## select_problems — the portfolio-backed coarse gate

`select_problems(demands, participant_minute_budget, researcher_hour_capacity,
minutes_per_team=600.0)` answers the coarser question *which problems to run at all*, before
`allocate` decides how many teams each gets. It reuses [`engine/portfolio.py`](../engine/portfolio.py)
by turning each `ProblemDemand` into a `portfolio.Study`:

- `value` → `exp_value`
- `info_value` carried as `0.0` here
- `mentor_hours_per_team` → `researcher_hours`
- `minutes_per_team` → `participant_minutes`
- **`mode` → `category`**

Mapping mode onto `portfolio.select`'s `category` means the same mode is not double-booked — the
docstring calls this "mirroring one-sponsor-per-competitive-category," and `portfolio._violations`
enforces it via `category_exclusivity` (one study per category). So `select_problems` is a portfolio
gate: it picks the highest-value compatible set of problems under participant-minute and
researcher-hour budgets, and it will refuse to run two problems of the same mode at once. `allocate`
then works within the surviving set.

## marginal_value_of_capacity — the economic-flow question

`marginal_value_of_capacity(demands, n_teams, mentor_capacity, compute_capacity, resource="mentor",
step=1.0, diversity_weight=1.0)` answers **"what is one more mentor hour worth?"** (Phase 15) by
re-solving:

```
base   = allocate(..., mentor_capacity,        compute_capacity, ...)
bumped = allocate(..., mentor_capacity + step, compute_capacity, ...)   # for resource="mentor"
return round(bumped["objective"] - base["objective"], 4)
```

`resource` selects which constraint to relax — `"mentor"`, `"compute"`, or `"teams"` (which bumps
`n_teams` by `int(step)`); any other value raises `ValueError`. The return is the **objective delta**
from adding one unit of that resource, i.e. its marginal value / shadow price in objective units. If
either solve is infeasible (`None`), it returns `None` rather than a fabricated number.

This is the economic-flow view of the same allocation: rather than "what is the best plan," it asks
"what is the next unit of a scarce resource worth at the margin?" — the question that tells an
organizer whether to buy more mentor hours, more compute, or invite more teams. Because the delta is
computed against the same decomposed objective, a marginal value of 0 is meaningful: it says the
constraint is not binding, and the slack fields in `allocate`'s result show why.

## What this module is and is not

- It **is** a population-level allocation engine with hard capacity constraints, a decomposed
  objective (value + diversity), an exact solver, a portfolio-backed coarse gate, and a marginal-
  value probe.
- It is **not** an individual ranker, a founder-scorer, or a talent-scorer of any kind. No person is
  ever an object here — a hard ethical boundary, not a preference.
- It does **not** fabricate value. `value_per_team` arrives from fit/economics upstream, where
  unevidenced economic magnitudes stay **UNKNOWN** (see
  [problem-mechanics.md](problem-mechanics.md)); the allocator only combines what it is given.
