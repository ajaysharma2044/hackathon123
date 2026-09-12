# Structured Checkpoints — START / MIDPOINT / END / FOLLOW-UP

Checkpoints are **Layer 7** and **Part VI** of the [live research OS](live-research-os.md): the few,
deliberate, explicit touches that give every team a baseline and an endline even when nothing
interesting enough to trigger a [critical incident](critical-incidents.md) ever fires. They are the
spine the team story ([team-trajectories.md](team-trajectories.md)) hangs on — the `t0` plan, the
`t/2` drift, the `t1` outcome, and the `t+7/30/90` continuation.

> **Checkpoints are the one place we spend explicit attention on *every* team on purpose.** Micro-
> prompts are fired only at high-signal moments; interviews are sampled. Checkpoints are the
> universal, minimal, incentive-tied exception. Because they are universal, they must be ruthlessly
> short — the whole design objective is to **maximize Signal per unit ParticipantBurden**.

## The four checkpoints

Stored in the `checkpoint` table (schema [`006_live_research.sql`](../../schema/006_live_research.sql)),
one row per team (or participant) per kind, with the answers in a `payload` jsonb. Each checkpoint
debits the **explicit** burden budget (`CHECKPOINT ∈ EXPLICIT_CHANNELS`,
[`burden_budget.py`](../../engine/burden_budget.py)) — unlike a mentor note, a checkpoint is a real
tax and is counted as one.

```
  START          MIDPOINT           END                 FOLLOW-UP
  (t0, baseline) (≈ t/2, drift)     (t1, outcome)       (7 / 30 / 90 days)
  the plan       what changed       what shipped        what continued
     │               │                  │                   │
     └───────────────┴──────── the team trajectory ─────────┴──── the retention asset
```

### START — the baseline (team, at t0)

Captured at team formation / build start. This is the `t0` against which every later "what changed"
is measured; without it, drift is unmeasurable.

| Field | Question (short form) |
|---|---|
| intended project | what are you building? |
| main problem | what problem does it solve? |
| expected architecture | how do you expect to build it? |
| tools considered | which tools/products are you considering? |
| prior familiarity | how familiar are you with them already? *(adoption-vs-retention covariate)* |
| key uncertainty | what are you least sure about? |
| expected challenge | what do you expect to be hardest? |

`prior familiarity` is load-bearing: a team already fluent in a product is measuring **retention**,
not **adoption**, and mixing the two corrupts both numbers ([measurement.md](../measurement.md),
"Selection is an instrument too"). START is where that covariate is set.

### MIDPOINT — the drift (≈ t/2)

The single most informative checkpoint for the *decision* story, because it catches change while it
is fresh rather than reconstructed at the end.

| Field | Question (short form) |
|---|---|
| what changed | what's different since START? |
| largest blocker | what's blocking you most right now? |
| biggest surprise | what surprised you? |
| major switch | did you switch any tool/approach? |
| major pivot | did the project itself change? |
| remaining uncertainty | what are you still unsure about? |

`major switch` and `major pivot` are the explicit, every-team complement to the telemetry- and
mentor-detected switches in [critical-incidents.md](critical-incidents.md): even a team no detector
flagged gets asked once, directly.

### END — the outcome (t1)

Captured at submission/demo. The endline, and the raw material for the outcome episode on the
trajectory.

| Field | Question (short form) |
|---|---|
| what shipped | what did you actually ship? |
| what changed | what changed from the START plan? |
| what failed | what didn't work? |
| what worked | what worked well? |
| what surprised | what surprised you overall? |
| what you'd do differently | what would you change next time? |
| what you'd keep using | which tools would you keep using? |
| what should happen next | what's the next step for this project? |

`what you'd keep using` and `what should happen next` are the **bridge to follow-up** — a stated
intention at t1 that the 7/30/90-day waves then test against behavior.

### FOLLOW-UP — the continuation (7 / 30 / 90 days)

Stored as `FOLLOWUP_7 | FOLLOWUP_30 | FOLLOWUP_90` (`checkpoint.kind`). This is the retention asset
no other hackathon produces ([live-research-os.md](live-research-os.md), Layer 15). Response rates
decay hard (≈60% at 7d, maybe ≈25% at 90d without incentive — **illustrative**, from
[measurement.md](../measurement.md)), so the follow-up waves are budgeted real incentives.

| Field | Question (short form) |
|---|---|
| continued? | are you still working on it? |
| why | why / why not? |
| tools retained | which tools are you still using? |
| tools removed | which did you drop, and why? |
| what remains | what's left of the project? |
| collaboration continued | are you still working with the team? |
| outcome | where did it end up? |

`occurred_at ≠ observed_at` matters most here: everything learned at follow-up is a survey reported
later, and the two timestamps are kept distinct on every row so "as of day D" queries stay honest.

## Length and timing — ≤5 questions, <60 seconds

The hard limits, from [measurement.md](../measurement.md) and the burden budget:

```
≤ 5 questions shown at once     more than five and the response rate (and the data) collapse
< 60 seconds to complete        a checkpoint is a pit stop, not an interview
every ~6 hours of build time    frequent enough to catch drift, rare enough to not nag
one explicit debit each         counted against the ≤18-min explicit research cap per participant
```

The field tables above list the full intent, but the **shown** form is pruned to ≤5 questions per
checkpoint — the rest are inferred from artifacts or left to the sampled interview. Questions are
taps and short choices wherever possible; free text is optional on every field.

## Compliance — tie it to something they want

Voluntary checkpoints get ~30% response, and **the non-responders are exactly the people whose data
you most need** — the heads-down, the struggling, the about-to-abandon ([measurement.md](../measurement.md)).
So compliance is tied to something the builder already wants, never coerced:

```
CHECKPOINT COMPLETE  ──unlocks──►  mentor-slot booking  |  meal access  |  judging eligibility
```

This makes the checkpoint a natural step in something they were going to do anyway (book a mentor,
eat, qualify to demo) rather than a survey bolted on — the same "capture through things people were
going to do anyway" principle as the rest of the [capture system](../capture-system.md). The mentor
slot is a particularly clean anchor because it is also where the [mentor system](mentor-system.md)
already touches the team.

> The incentive tie is disclosed, not a trick. It is in the challenge/consent terms; a builder who
> genuinely wants to skip can, and the gap is recorded rather than pretended away.

## Optimize Signal / ParticipantBurden

The governing objective, made concrete:

- **Every field must earn its second.** If a field is reliably recoverable from an artifact
  ([capture-system.md](../capture-system.md)) or from telemetry, it is cut from the checkpoint and
  read from the cheaper channel instead — checkpoints spend *explicit* budget, artifacts do not.
- **START and MIDPOINT are the highest-leverage spends** (they capture state that is *unrecoverable
  later* — a plan and a fresh change), so they get first claim on the explicit budget; END overlaps
  with artifact capture and can lean on it.
- **A checkpoint is skippable and never blocks building.** It waits for a good moment in the
  [interruption policy](interruption-policy.md); a scheduled checkpoint is itself a
  `SHORT_INTERVIEW_OK`-class window, not a `DO_NOT_INTERRUPT` interruption.
- **Burden is a ledger, not a hope.** Each checkpoint writes a `participant_burden` row; the per-
  participant cap and prompt-rate governor in [`burden_budget.py`](../../engine/burden_budget.py)
  keep the checkpoints + prompts + interviews total under ~18 explicit minutes across the weekend.

## Where this connects

- Checkpoints feed the [team trajectory](team-trajectories.md) directly: START → `INITIAL_PLAN` /
  `TOOL_SET`, MIDPOINT → `SWITCH` / `PIVOT`, END → `OUTCOME`, FOLLOW-UP → `CONTINUATION`.
- They are **Layers 1, 2, 7, and 15** at once — baseline, team baseline, the checkpoints themselves,
  and the follow-up asset ([live-research-os.md](live-research-os.md)).
- Timing and interruptibility are governed by [interruption-policy.md](interruption-policy.md); the
  explicit burden accounting is [participant-burden.md](participant-burden.md).
- Program status and the WTP gate that decides whether Event 1 runs at all are upstream in
  [STATE.md](../STATE.md).
