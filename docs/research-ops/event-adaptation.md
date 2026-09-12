# Event Adaptation — Every Change Logged, With Its Validity Impact

**Parts XV–XVI of the [Live Research Operating System](live-research-os.md).** Layer 12 of the 17:
intervention logging.

A great event adapts. When twelve teams are stuck on database setup, you add database mentors. When
a challenge is being misread, you clarify it. When the mentor queue overloads, you open office
hours. Refusing to adapt to protect "clean data" would violate the one hard constraint — **the
experience wins** ([live-research-os.md](live-research-os.md)). So the event *should* change under
our feet.

The danger is forgetting that it changed. A study silently running across an environment that
shifted at hour 20 produces confident nonsense. So the rule is not "don't adapt" — it is:

> **Adapt freely where it is safe, refuse where it is not, and log every material change with its
> validity impact and a recoverable before/after boundary.** Encoded in
> [`intervention_log.py`](../../engine/intervention_log.py) and stored in the `event_intervention`
> table ([`006_live_research.sql`](../../schema/006_live_research.sql)).

## When the event should adapt — worked examples

These are the live signals the war room ([research-war-room.md](research-war-room.md)) surfaces, and
the adaptations they license. All numbers are **illustrative**.

| Signal (war-room evidence) | Adaptation | `target` knob | `validity_impact` |
|---|---|---|---|
| 12 teams stuck on DB setup (mentor-demand spike) | add 2 DB mentors, stand up a DB office hour | `mentor_allocation` | `OPERATIONAL` |
| A challenge's wording is being misread by ≥4 teams | clarify the instructions, announce once to all | `clarify_instructions` | `OPERATIONAL` |
| Mentor queue overloaded, avg wait >25m | open scheduled office hours to drain the queue | `office_hours` | `OPERATIONAL` |
| A product's docs repeatedly fail teams | add an extra support resource / pinned FAQ | `operational_support` | `OPERATIONAL` |
| Interview queue starving a segment (no SWITCHERs sampled) | raise that segment's interview target | `research_interview_targets` | `OPERATIONAL` |
| Food line blocks a whole track at dinner | restagger meal timing | `food_logistics` | `NONE` |

Every one of these is a change to the *environment a study is running in*. Even the "harmless" ones
are logged: a meal restagger is `NONE`, but it is still a timestamped row, because the discipline of
logging everything is cheaper than deciding case-by-case what counts.

## The intervention record

Each change is one `Intervention` ([`intervention_log.py`](../../engine/intervention_log.py),
`@dataclass Intervention`), appended to the `InterventionLog` and persisted to `event_intervention`:

```
 Intervention
 ├─ intervention_id          IV-014
 ├─ occurred_at              2026-…T20:12Z     ← INVARIANT 1: construction without this FAILS
 ├─ reason                   "DB setup blocking 12 teams; mentor wait 38m"
 ├─ evidence                 "war-room mentor-demand panel; 12 open DB support_requests"
 ├─ affected_population      "all teams requesting DB help after 20:12"
 ├─ change                   "+2 DB mentors; DB office hour at 20:30"
 ├─ target                   "mentor_allocation"          ← checked against ADAPTABLE / LOCKED
 ├─ expected_effect          "DB queue drains; wait < 15m within the hour"
 ├─ research_questions_affected  (Q-07, Q-12)   ← whose before/after must be split
 ├─ validity_impact          OPERATIONAL
 ├─ pre_specified            False
 └─ reversible               True
```

The record mirrors the schema one-to-one: `event_intervention(occurred_at, reason, evidence,
affected_population, change, expected_effect, research_questions_affected[], validity_impact,
decided_by, reversible)`. `evidence` is not a free-text justification — it points back at the
war-room view that prompted the change, so an intervention is always traceable to the signal that
caused it.

## What may adapt freely vs what is locked

The knob being turned is checked against two frozen sets in
[`intervention_log.py`](../../engine/intervention_log.py). These names are authoritative — use them
exactly.

```
 ADAPTABLE — turn these freely, log them, keep going
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ mentor_allocation · office_hours · clarify_instructions · operational_support│
 │ food_logistics · research_interview_targets · question_backlog ·             │
 │ research_sampling                                                            │
 └────────────────────────────────────────────────────────────────────────────┘

 LOCKED — the study spine; changing mid-event INVALIDATES unless pre-specified
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ core_randomized_treatment · product_exposure_assignment · credit_amount ·    │
 │ challenge_rules · evaluation_metric · primary_outcome · stopping_rule ·       │
 │ study_definition                                                             │
 └────────────────────────────────────────────────────────────────────────────┘
```

The split is intuitive once named: **ADAPTABLE knobs make the event better without redefining what
the study measures.** Adding DB mentors changes who gets help faster; it does not change what
"adoption" means. **LOCKED knobs are the measurement itself.** Changing the credit amount, the
exposure assignment, or the primary outcome mid-event means the data before the change and after it
are measuring different things — and if the study was pre-registered, that is the definition of
invalidating it.

### The refusal

`InterventionLog.log(iv)` enforces the boundary:

```
  log(iv):
    if iv.target in LOCKED and not iv.pre_specified:
        raise ValidityViolation(      # the change is REFUSED, not just warned about
            "'<target>' is part of the study spine; changing it mid-event invalidates the
             study unless pre-specified. Intervention refused.")
    if iv.target in LOCKED and iv.pre_specified:
        iv.validity_impact = INVALIDATING   # a pre-specified spine change can't be mislabeled NONE
```

So a request to bump the credit amount at hour 30 because "teams aren't using it" does not quietly
succeed — it raises `ValidityViolation`. The only way a LOCKED knob moves is if the change was
**written into the protocol before the event** (`pre_specified = True`), in which case it is forced
to `INVALIDATING` and the analysis must treat the whole study as a before/after design from the
start. There is no path where a spine change happens and is recorded as harmless.

## The four validity levels

Defined as the `validity_impact` enum in both the schema and the engine — use these exact names:

| Level | Meaning | Analysis consequence |
|---|---|---|
| `NONE` | logistics/food; no research effect | log it; nothing downstream changes |
| `OPERATIONAL` | mentor allocation, office hours; populations before/after differ *operationally* | note the context shift; usually no split needed, but the shift is documented |
| `CONFOUNDING` | changes something a study measures | **before/after must be split** on `split_point` |
| `INVALIDATING` | touches a pre-registered treatment/outcome/stopping-rule | forbidden unless pre-specified; if forced, the study is a before/after design |

The ladder climbs from "doesn't touch the research" to "is the research." An intervention is labeled
honestly at the level it actually sits; there is no incentive to under-label, because the same log
that records the change also records the split that repairs it.

## Preserving the before/after split

The repair for a `CONFOUNDING` change is not to pretend it didn't happen — it is to condition the
analysis on it. `InterventionLog.split_point(question_id)` returns the **earliest** intervention
time affecting a given research question:

```
  split_point(Q-07)  →  2026-…T20:12Z
      │
      ▼
  analysis for Q-07 conditions on BEFORE 20:12  vs  AFTER 20:12
      pre-intervention population  │  post-intervention population
      (saw the old environment)    │  (saw +2 DB mentors + office hour)
```

Because `research_questions_affected` is carried on every intervention, any question can ask "what
changed under me, and when?" (`affecting(question_id)`) and recover the boundary timestamp. The
before/after populations are then analyzed separately rather than pooled — the change becomes a
*known covariate* instead of a silent confounder. This is the operational payoff of Invariant 3:
the environment is allowed to move, as long as every move is recoverable.

## Protecting research integrity

- **The event stays excellent.** Refusing to help stuck teams to protect data is never the answer;
  ADAPTABLE knobs exist precisely so the event can respond.
- **The spine stays fixed.** LOCKED knobs do not move mid-event without pre-specification; the
  refusal is structural, not a matter of discipline.
- **Nothing is forgotten.** Every material change is a timestamped row with its validity impact and
  its affected questions, feeding the war room ([research-war-room.md](research-war-room.md)) and
  visible in the dashboard's Intervention Log view ([dashboard-spec.md](dashboard-spec.md)).
- **Clients see aggregate only.** The intervention log is internal research/ops data. A client
  never sees it as a live feed, and never directs an adaptation — clients do not interfere in the
  research ([client-protocols.md](client-protocols.md), [live-research-os.md](live-research-os.md)).

The result is an event that is free to become one of the best weekends the builders ever attend,
*and* a dataset that can still be honestly analyzed afterward — because we never let the second one
quietly decay while improving the first.
