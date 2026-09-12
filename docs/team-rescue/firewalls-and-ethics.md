# Firewalls & Ethics

The disciplines that keep the [Adaptive Team Performance + Rescue Engine](adaptive-rescue-engine.md)
from becoming the thing it must never be: a surveillance tool, a hidden individual-productivity
grader, or a way for a paying client to buy priority over a struggling team. These are not
aspirations — most are enforced in [`schema/008_team_rescue.sql`](../../schema/008_team_rescue.sql)
and the engines, and tested in [`test_team_rescue.py`](../../engine/test_team_rescue.py).

## 1 — No individual scoring, ever

The engine optimizes the **environment and team support**, not individuals. Structurally:

```
NO person / quality / intelligence / work-ethic / employability / founder-potential score
NO ranking of people by any of the above
NO keystroke logging · NO continuous screen monitoring · NO private-message surveillance · NO camera
```

- **State is team-level and a vector.** `TeamState` exposes `.vector()`, and its `__post_init__`
  *refuses* a `team_score` key — a team is a decomposed state plus a routing label
  (EARLY/ON_TRACK/AT_RISK), never a number ([team-state-model.md](team-state-model.md)).
- **Contribution is voluntary ownership, not graded output.** A participant with no declared
  workstream triggers a *team* prompt — *"does anyone need a clearer workstream?"* — never a hidden
  "free-rider" label on a person ([contribution-and-roles.md](contribution-and-roles.md), Parts XII,
  LIII). `ownership_gap` returns who lacks a workstream so the *team* can rebalance, and nothing else.
- **The no-go guard is shared with the research layer.** Every state payload passes `assert_clean`
  ([`live_research.py`](../../engine/live_research.py)), which rejects any forbidden score or
  protected-trait key — the same boundary as the rest of the system
  ([../research-ops/live-research-os.md](../research-ops/live-research-os.md)).

## 2 — The performance/research firewall (Part XLVI)

The rescue engine and the research OS are fed by the same sensors but serve **different purposes**,
and the purposes are kept separate:

```
TEAM-SUPPORT SYSTEM   uses OPERATIONAL state (blocker, scope, lifecycle, mentor demand) to HELP now.
RESEARCH SYSTEM       uses CONSENTED evidence to understand WHY, for a client deliverable, in aggregate.
```

- **Support decisions never rank or exclude a participant.** Operational state exists to route help;
  it is never used to punish, rank, or gate anyone during the event.
- **Research-grain fields are firewalled OUT of the rescue engine.** `rescue_engine._firewall`
  rejects any state carrying `consent_scope`, `interview_excerpt`, `qual_id`, `finding_id`,
  `claim_id`, or `participant_id` — the rescue layer works on team operational state, not on the
  consented research record. The test suite asserts this refusal.
- **The direction that IS allowed** is the reverse and it is disclosed: a *blocker the support system
  resolves* is also product-friction evidence the research layer may read — but only under the normal
  consent gate, in aggregate, never as an individual support record handed to a client.

## 3 — Adaptive research burden respects team state (Part XLV)

Support state modulates research load, in the participant's favor:

```
team doing poorly / heads-down    →  FEWER research prompts (the burden budget already backs this)
team idle / waiting               →  a good moment for a short contextual interview (if sampled)
```

This runs through the existing budget + interruption policy
([../research-ops/participant-burden.md](../research-ops/participant-burden.md),
[../research-ops/interruption-policy.md](../research-ops/interruption-policy.md)) — the rescue engine
just supplies the "is this team struggling right now" signal.

## 4 — Fairness: no bought priority over the support floor (Parts XVII, LVII, LIX)

Scarce resources (mentor time, GPU, rooms, domain experts) are allocated by **need, participant
value, and critical-path importance — not by commercial value alone.**

```
allocate_resources:  1) give EVERY requesting team the minimum floor
                     2) only then distribute the SURPLUS, where commercial priority may order it
```

The schema makes the sharp case a CHECK constraint: `resource_allocation.is_below_floor_override =
false`. **A commercial client can never buy priority below another team's basic support floor**, and
the event-wide objective is to *maximize total output subject to a minimum for every team* — not to
funnel everything to the likely winners ([event-control-and-waste.md](event-control-and-waste.md)).

## 5 — Counterfactual discipline (Part LVI)

Because the whole engine is a `state → intervention → outcome` loop, the temptation is to claim the
intervention *caused* the outcome. We refuse that from mere precedence:

```
ALLOWED   "the mentor intervention PRECEDED the blocker's resolution"
FORBIDDEN "the mentor saved the team"  (a causal claim)
```

`rescue_engine.record_outcome` stores the relationship as `intervention_preceded_outcome` and
**raises** if asked to record a causal claim; `schema/008` mirrors this with
`rescue_intervention.causal_claim = false`. Causal language is reserved for the places we can run an
experiment or quasi-experiment — the same standard as the research layer's evidence graph
([../research-ops/evidence-graph.md](../research-ops/evidence-graph.md)).

## 6 — No fabricated probabilities (Parts XXXI–XXXV)

We do not hard-code fake pre-event completion or success probabilities. `simulate_intervention`
returns qualitative **scenarios** with `calibrated_probability = None`, plus a note on what would be
needed to learn a real one. Hazard-of-non-completion and project-success models are **UNKNOWN** until
trained on multi-event data, and even then they are used for **support prioritization, never
participant ranking**. Contextual bandits and RL are explicitly deferred until the data exists; the
initial policy is human-reviewed.

## 7 — Preventable ≠ informative failure (Part XXV)

The metric the engine optimizes — **Preventable Blocked Minutes** — deliberately **excludes**
informative failure:

```
PREVENTABLE (prevent it)     forgot a dependency · no mentor available · bad scope · unclear
                             instructions · a missing API key · tool/ops friction
INFORMATIVE (capture it)     the algorithm genuinely doesn't work · the hypothesis fails · the
                             architecture underperforms · the simulation disproves the approach
```

`event_control.preventable_blocked_minutes` counts the first and reports informative minutes
separately; `rescue_engine.classify_failure` labels a cause. Treating a real research failure as
"waste to prevent" would destroy exactly the value the R&D engine is built to capture
([../rd-engine.md](../rd-engine.md)) — so the firewall runs in this direction too.

## 8 — No productivity leaderboard; incentives that don't backfire (Parts XLVII–XLVIII)

- **No public gamification of productivity** — no leaderboard of commit counts, hours worked, mentor
  requests, or lines of code. That invites gaming (commit spam, sleep-deprivation signaling,
  information hiding). Public competition stays **project-oriented** (the judging system,
  [../event-ops/judging-system.md](../event-ops/judging-system.md)).
- **Incentives encourage** shipping, collaboration, learning, technical ambition, helping peers, good
  documentation, and continuation — and **avoid** rewarding sleep deprivation, information hoarding,
  sabotage, fake complexity, or commit spam.

## 9 — Value is multi-dimensional (Part XXIV)

The engine does not optimize teams only to *win*. A project can be valuable as technical learning, a
working prototype, a research insight, an *informative* R&D failure, creative novelty, commercial
relevance, participant enjoyment, startup potential, or open-source value — kept decomposed, never
collapsed into one "success" number ([event-control-and-waste.md](event-control-and-waste.md)).

## The one-line test

> The system should make it **hard for a team to quietly fail because of a preventable problem**, and
> **impossible for it to quietly grade, rank, surveil, or sell out a participant.** If a proposed
> feature helps the first and risks the second, it does not get built — the same standard that governs
> the research layer, applied to team support.
