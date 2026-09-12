# Data Model

## Core entities

| Entity | Notes |
|---|---|
| `participant` | A builder. Persists across events; links to Club OS identity where one exists. |
| `team` | Formed during an event. Members may have prior shared history — that history is itself a feature. |
| `event` | One hackathon / sprint / beta cohort. |
| `track` | Sponsor-defined problem area within an event. |
| `sponsor` | The buyer. |
| `experiment` | A sponsor research question instantiated as a design. Versioned. |
| `project` | What a team builds. Has artifacts and a post-event trajectory. |
| `product` | A tool/API/service under observation (sponsor-owned or competitor). |

## Event stream

The atomic record. One row per observed behavior:

```
participant_id
team_id
experiment_id
timestamp
event_type
product
context
source
consent_scope
```

### Event taxonomy

**Exposure and activation**
`product_exposed` · `account_created` · `onboarding_started` · `onboarding_completed`

**Usage**
`feature_used` · `error_encountered` · `help_requested`

**Choice**
`tool_switched` · `tool_returned`

**Output**
`project_created` · `project_completed` · `submission_made`

**Qualitative**
`survey_answered` · `interview_completed`

**Post-event**
`voluntary_reuse`

`tool_switched` and `voluntary_reuse` carry most of the commercial signal. They are also the
two hardest to capture honestly — switching is often invisible unless the participant tells
you, and voluntary reuse happens off your property. Design for self-report plus sponsor-side
telemetry rather than assuming you can observe it directly.

## Temporal semantics

```
occurred_at ≠ observed_at
```

Store both wherever they can diverge. A `voluntary_reuse` learned from a 30-day survey occurred
days before it was observed; treating survey time as event time will silently corrupt every
retention curve and every time-to-event model. This is not a nicety — bitemporality is the
difference between a defensible retention number and a wrong one.

## Consent is load-bearing

`consent_scope` is a field on every event because the alternative — a single blanket consent at
registration — cannot support the thing being built. Distinct scopes are needed for at least:

1. **Event telemetry** — behavior during the event, for aggregate sponsor research.
2. **Identified sponsor visibility** — a named sponsor sees this participant's activity.
3. **Recruiting visibility** — work evidence exposed to employers.
4. **Post-event follow-up** — contact at 7/30/90 days.
5. **Longitudinal linkage** — joining event data to Club OS history.
6. **VC/team discovery** — team trajectory exposed to investors.

These are genuinely different decisions and a participant may reasonably grant some and refuse
others. Scoping them per-event-row means a revoked scope can be enforced at query time rather
than requiring a data purge.

Three constraints worth designing in from the start rather than retrofitting:

- **Revocation has to actually work.** If a participant withdraws scope 3 at day 45, already-
  delivered recruiting evidence needs a defined status. Decide this before the first event, not
  after the first request.
- **The population is mostly students, often under university affiliation.** Post-event tracking
  tied to educational records touches FERPA-adjacent territory; international participants pull
  in GDPR; several states have their own regimes. Worth a real legal read before event #1 —
  cheap now, expensive after you have 200 people's longitudinal records.
- **Aggregate-only is a promise with teeth.** The stated position is that identifiable student
  histories are not the product — aggregate research and permissioned evidence are. Small-n
  segment reporting can re-identify people even when no name is attached. A minimum cell size
  on every sponsor-facing cut enforces the promise instead of just asserting it.

None of this slows the concept down. It does determine the schema, so it belongs here.

## Derived structures

Built on the event stream, not stored independently:

- **Behavioral funnel** per `(participant, product, experiment)` — see
  [research-framework.md](research-framework.md).
- **Switching matrix** per category — `from_product → to_product`, with time-to-switch.
- **Work evidence record** per participant — the recruiting product's unit.
- **Team trajectory** — the VC product's unit.
