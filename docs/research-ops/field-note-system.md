# Field Note System

The standardized structure for every field observation. This is the atomic unit the field
researchers ([field-researcher-guide.md](field-researcher-guide.md)) produce; it is stored as the
`observation` table in [`schema/006_live_research.sql`](../../schema/006_live_research.sql) and its
hardest invariant is enforced in code by `FieldNote` in
[`engine/live_research.py`](../../engine/live_research.py).

## The one rule everything else serves

> **OBSERVED FACT must be separate from RESEARCHER INTERPRETATION — in different fields, never
> collapsed.** A note that reads "Team hated Supabase" has already thrown away the evidence and kept
> only the guess. The guess may be right, but it is no longer auditable, and it is exactly how a
> confident, wrong narrative gets built and sold to a client.

```
BAD                "Team hated Supabase."

GOOD
  observed_event   Team member said "we're wasting too much time on auth"; the team removed the
                   Supabase dependency approximately 12 minutes later.
  direct_quote     "we're wasting too much time on auth"
  interpretation   Authentication friction may have contributed to the switch.
  alternative      The teammate who took over already knew the alternative; familiarity, not
                   friction, may be the driver.
```

The fact can stand on its own forever. The interpretation is a **hypothesis** that the
[evidence graph](evidence-graph.md) will test against confirming *and* contradicting cases. Making
the interpretation a separate, clearly-labeled field is what lets a later analyst — or an auditor,
or the client — see the reasoning and disagree with it.

## The standard note

Every observation captures:

| Field | What it holds | Notes |
|---|---|---|
| `ObservationID` | unique id | |
| `ResearcherID` | who observed | for inter-observer calibration + disagreement tracking |
| `Time` | `occurred_at` / `observed_at` / `available_at` | three clocks (see below) |
| `Team` / `Participant` | subject | **grain is usually TEAM**, not person |
| `Location` | where | zone/room |
| `Context` | track, stage, team size, time-remaining snapshot | a finding without context is about our event, not the tool |
| **`ObservedEvent`** | the behavioral FACT — what was seen/heard | **required; no inference allowed here** |
| `DirectQuoteIfAny` | verbatim words | in quotation marks, exact |
| `DecisionBeingMade` | the choice in flight, if any | |
| `ToolsOrApproachesInvolved` | products/approaches | use canonical names |
| `PriorState` → `CurrentState` | the transition | |
| `Outcome` | what resulted, if known yet | |
| **`ResearcherInterpretation`** | the reading — explicitly the researcher's | labeled as interpretation, never fact |
| **`AlternativeInterpretation`** | a competing reading | **required whenever an interpretation is offered** |
| `FollowUpNeeded` | does this warrant a deeper interview? | feeds the [interview queue](adaptive-sampling.md) |
| `TriggerType` | which critical incident, if any | ties to [critical-incidents.md](critical-incidents.md) |
| `LinkedArtifact` | repo/commit/deploy pointer | the honest cross-check |
| `Confidence` | `[0,1]`, `<1.0` because observation is partly inference | |
| `EvidenceStatus` | RAW / CORROBORATED / CONTRADICTED / SUPERSEDED | how it has held up |

### Two structural guards (enforced, not just asked for)

The `FieldNote` dataclass refuses to construct a note that breaks the rule:

1. **An empty `observed_event` is rejected.** There is no note without a fact.
2. **An interpretation with no alternative is rejected.** If you have a reading, you must also name a
   competing reading — a single unchallenged interpretation is where confirmation bias enters. This
   is the same discipline the [evidence graph](evidence-graph.md) enforces at the claim level and the
   [sampler](adaptive-sampling.md) enforces at the interview level, pushed all the way down to the
   atom.

```python
FieldNote(..., observed_event="removed SDK", researcher_interpretation="they hated it")
# ValueError: an interpretation requires an alternative_interpretation
```

## The three clocks travel with the note

Like every raw row in the system ([research-data-model.md](../research-data-model.md)), an
observation carries:

```
occurred_at    when the observed behavior happened          (the survival/timeline axis)
observed_at    when the researcher wrote it down            (catches the "I logged it at the break" lag)
available_at   when it became queryable in the store        (drives point-in-time "as of D" queries)
```

A switch observed at 16:32 but written up at the 18:00 meal break has `occurred_at = 16:32`,
`observed_at = 18:00`. Retention and timeline reconstruction run on `occurred_at`; using
`observed_at` would silently shift the event later and corrupt the [team trajectory](team-trajectories.md).

## Provenance and corrections

- **Immutable + append-only.** A note is never edited. A correction is a new row whose
  `superseded_by` points back; the original stays, marked `SUPERSEDED`.
- **Confidence < 1.0.** An observation is always partly inference (you saw the SDK removed; you
  inferred it was deliberate). Only a logged machine event is 1.0 — and those come from telemetry,
  not field notes.
- **A quote can graduate to a raw qualitative row.** A strong verbatim quote is linked via
  `linked_qual_id` into `qualitative_observation`, so it can be [coded](qualitative-coding.md) and
  linked to the behavioral event it explains (the "why" ↔ "what" join).

## From note to understanding

A single note is a data point. The value is in how they aggregate — always through provenance, never
by laundering a guess into a fact:

```
observed_event + direct_quote          (raw, immutable)
        │  coded (qualitative-coding.md)
        ▼
   code → subtheme → theme              (a HYPOTHESIS, carries model_version + human review)
        │  many corroborating/contradicting notes
        ▼
   emerging pattern (research-war-room.md) → analytic memo (analytic-memos.md)
        │  confirming AND disconfirming evidence assembled
        ▼
   claim → (promotion gate) → finding → recommendation   (evidence-graph.md)
```

At every step the original fact is one link away. That is the whole point of keeping the fact and
the interpretation apart at the moment of capture: **the story you eventually tell a client can
always be walked back to the specific things that actually happened.**
