# The Economic Flow Model

The general economy layer, implemented in [`engine/economy.py`](../engine/economy.py) and backed by
[`schema/008_environment_economy.sql`](../schema/008_environment_economy.sql). This document describes
what the code actually does; it does not propose new behavior.

It generalizes [research-data-model.md](research-data-model.md)'s "hackathon as a compressed economic
laboratory" beyond participants-choosing-devtools. The module docstring states the frame directly: a
temporary organization is a real economy where "actors face opportunities, hold resources, respond to
incentives, decide, allocate resources, transact, behave, produce artifacts, and generate outcomes."

Two disciplines are carried over verbatim from the belief layer and stated at the top of
`economy.py`:

- **CASH IS ONLY ONE PRICE.** Non-cash resources (mentor-minutes, GPU-hours, customer intros) carry
  SHADOW PRICES represented as `beliefs.Belief`, default **UNKNOWN**. The code does not invent a
  dollar value for a mentor-hour without evidence.
- **FLOW ANALYTICS ARE DESCRIPTIVE.** The ledger reconstructs where attention and resources actually
  flowed; it does not impute value where none is evidenced. Marginal value stays **UNKNOWN** without a
  belief.

`Evidence != Claim != Hypothesis != Decision` holds here as everywhere: a flow count is evidence of
what happened, never a claim about what it was worth.

## The episode chain

The central object is `economy.Episode` — one actor's path from opportunity to (optional) outcome.
The chain the module documents is:

```
Actor -> Opportunity -> ChoiceSet -> ResourcesAvailable -> Incentives -> Decision
      -> ResourceAllocation -> Transaction -> Behavior -> Artifact -> Outcome
```

`Episode` (`economy.py:Episode`) records these as fields, and its docstring is explicit that **missing
stages stay `None` — we do not fill them in**:

| Field | Meaning | Default |
|---|---|---|
| `episode_id`, `actor_id` | identity + the acting `Actor` | required |
| `opportunity_kind` | `PROBLEM \| PROJECT \| TEAM \| BOUNTY \| ...` | required |
| `choice_set` | options that were **AVAILABLE** (choice != preference, schema 002) | `()` |
| `resources_available` | `{resource_kind: amount}` the actor held | `{}` |
| `incentives` | incentives in play | `{}` |
| `decision` | the option chosen; **`None` = abandoned / none** | `None` |
| `resource_allocation` | `{resource_kind: amount committed}` | `{}` |
| `behavior` | observed behavior | `{}` |
| `artifact_kind` | the artifact produced, if any | `None` |
| `outcome_kind` | the outcome, if any | `None` |
| `is_negative_result` | a failure that is itself informative (Phase 17) | `False` |
| `changed_a_decision` | **the only outcome that matters commercially** | `None` |

`choice_set` is the load-bearing distinction inherited from the research data model: it records what
was *available*, so that a chosen option can later be read as a preference signal rather than a raw
count. `decision is None` is a first-class state meaning the opportunity was abandoned — not a gap to
be imputed.

`Actor` (`economy.py:Actor`) is minimal: `actor_id`, `kind` (one of `ACTOR_KINDS`), and an optional
`label`. It corresponds to the `economic_actor` table.

## Actors and resources: the catalogues

`ACTOR_KINDS` (`economy.py:ACTOR_KINDS`) enumerates 18 actor kinds — `PARTICIPANT`, `TEAM`,
`CORPORATION`, `BUSINESS_UNIT`, `SPONSOR`, `BUYER`, `MENTOR`, `JUDGE`, `DOMAIN_EXPERT`, `INVESTOR`,
`VENDOR`, `RECRUITER`, `CUSTOMER`, `USER`, `GOVERNMENT`, `UNIVERSITY`, `ORGANIZER`, `STARTUP`. This is
the same controlled vocabulary as the `economic_actor_kind` enum in schema 004. Generalizing past
participant-only modelling is the point: a sponsor, a buyer, and a government are all actors in the
same economy.

`RESOURCE_KINDS` (`economy.py:RESOURCE_KINDS`) is the catalogue of what flows through the economy —
**24 resources, of which CASH is exactly one**:

```
CASH, PARTICIPANT_TIME_MIN, MENTOR_TIME_MIN, DOMAIN_EXPERT_TIME_MIN, COMPUTE_GPU_HR,
API_CREDITS, DATASET_ACCESS, CUSTOMER_ACCESS, CAPITAL, PRIZE, BOUNTY, GRANT, INTRODUCTION,
DISTRIBUTION, REPUTATION, SOCIAL_CAPITAL, WORKSPACE, MATERIALS, EQUIPMENT, JOB_OPPORTUNITY,
INVESTMENT_OPPORTUNITY, DESIGN_PARTNER_SLOT, PROCUREMENT_OPPORTUNITY, IP
```

This matches the `resource_kind` enum in schema 004. The rest of the catalogue — mentor time,
customer access, introductions, reputation — is exactly the value that ordinary accounting drops on
the floor. Because it is non-cash, its price is a belief, and that belief defaults **UNKNOWN**.

## `ShadowPrices`: every non-cash price is UNKNOWN until evidenced

`ShadowPrices` (`economy.py:ShadowPrices`) is a registry mapping each resource in `RESOURCE_KINDS` to
a price `Belief`. On construction, **every** resource is seeded with `beliefs.unknown(...)` carrying
the reason "non-cash resource price is UNKNOWN until evidenced." Nothing starts as a number.

- `ShadowPrices.set(resource, belief)` installs an evidenced price for one resource, raising
  `KeyError` if the resource is not in the catalogue.
- `ShadowPrices.value_of(resource, amount)` returns the point value `mean * amount` — but returns
  **`None`, not a number**, whenever the price belief is UNKNOWN (because `Belief.mean()` returns
  `None` for an UNKNOWN belief with `dist is None`). This is the honest-refusal behavior of the belief
  layer surfaced at the economy layer: you cannot get a dollar figure out of a resource you have no
  evidence to price.
- `ShadowPrices.unresolved()` returns the list of resources whose price is still UNKNOWN — described
  in the code as "the honest to-do list." It mirrors `beliefs.BeliefLedger.unresolved()`.

This corresponds to the `shadow_price` table, whose `price_belief_id` and `status` columns both
default to UNKNOWN in schema 004.

## `EconomicLedger`: descriptive flow analytics

`EconomicLedger` (`economy.py:EconomicLedger`) is an append-only store of `Actor`s and `Episode`s that
reconstructs the temporary economy (Phase 15). Its docstring is emphatic: **all analytics are
descriptive counts and sums over what actually happened** — they never impute unevidenced value.

- `add_actor(a)` / `add_episode(e)` append to the ledger.
- `attention_flow()` — counts, per `opportunity_kind`, how many episodes actually chose it
  (`decision is not None`). This is where talent and attention *actually flowed*, by observation.
- `abandonment()` — the mirror image: opportunities present in a choice set but **not** chosen
  (`decision is None`). Its docstring restates the research-data-model rule "offered != taken" and
  "absence of behavior != inability." An abandoned opportunity is recorded, not inferred away.
- `resource_flow()` — total committed amount by resource, summed across every episode's
  `resource_allocation`. A pure sum of what was committed.
- `bottlenecks(supply)` — given `{resource: capacity}`, returns `{resource: overshoot}` for the
  resources where committed demand exceeds supplied capacity. It compares `resource_flow()` against
  the caller-supplied capacities and reports only the binding ones. Nothing is priced; it reports
  where the economy was capacity-constrained.
- `negative_results()` — counts episodes with `is_negative_result` set. This is the value-of-failure
  surface (Phase 17): informative failures are counted, not discarded. It corresponds to the
  `outcome.is_negative_result` column.
- `decisions_changed()` — counts episodes where `changed_a_decision` is truthy. The code calls this
  **"the commercial numerator"**: the one outcome that matters commercially is whether the work
  changed a buyer's decision, matching the `outcome.changed_a_decision` column and the VOI pricing
  rule elsewhere in the engine.

None of these five analytics multiply a count by a shadow price. They are counts and sums. Turning a
flow into a dollar figure requires an evidenced belief, and that step is deliberately not taken here.

## `simulate_contribution`: contribution as a distribution, with the UNKNOWN guard inherited

`simulate_contribution(revenue_params, cost_params, n=40000, seed=7)` (`economy.py:simulate_contribution`)
generalizes `event_optimizer.economic`: contribution = `sum(revenue beliefs) - sum(cost beliefs)`,
computed as a Monte Carlo distribution. Both arguments map name -> `beliefs.Belief`.

The function builds a merged parameter dict and a model closure `rev - cost`, then delegates to
`monte_carlo.simulate` (`economy.py` imports `simulate` from `monte_carlo`). This matters for the
discipline: `monte_carlo.simulate` **raises `ValueError` if any input belief is UNKNOWN**
(`monte_carlo.py:simulate` checks `b.status == UNKNOWN` before sampling). So `simulate_contribution`
**inherits the UNKNOWN guard for free** — an unevidenced revenue line cannot silently become a number;
it makes the whole simulation refuse to run until resolved to an ASSUMED scenario band.

The return value is an `MCResult` (`monte_carlo.py:MCResult`), a full distribution — `.summary()`
gives mean/median/p5/p25/p75/p95/std, and `.prob_gt(t)`, `.var(alpha)`, and `.cvar(alpha)` give tail
risk. Never a single point estimate.

## Why this generalizes the "compressed economic laboratory"

[research-data-model.md](research-data-model.md) argued that a hackathon is a temporary micro-economy
of builders spending scarce resources under real incentives, and that the object model must record the
*economic* structure of each decision. `economy.py` lifts that from one implementation (participants
choosing devtools) to the primitive itself, exactly as schema 004's header describes: a hackathon
becomes **one configuration** — one actor mix, one resource catalogue, one buyer class — of a
configurable temporary organization engineered around an expensive problem.

Concretely:

- The chain `Actor -> Opportunity -> ChoiceSet -> ... -> Outcome` is the same chain from the research
  data model, now expressed for **any** `ACTOR_KIND`, not just participants.
- `ChoiceSet` remains the missing primitive (choice != preference), preserved as `Episode.choice_set`.
- Resource flows generalize from `economic_transaction` to the full 24-entry `RESOURCE_KINDS`
  catalogue, cash being one line.
- The commercial question — did the work **change a decision** — is captured as
  `decisions_changed()`, the numerator that the pricing rules elsewhere multiply against value.

The result is a laboratory that can be pointed at residencies, R&D arenas, procurement markets, or a
weekend hackathon, and will report where attention and resources actually flowed, where it was
bottlenecked, how many informative failures it produced, and how many decisions it changed — while
keeping every unevidenced price honestly UNKNOWN.
