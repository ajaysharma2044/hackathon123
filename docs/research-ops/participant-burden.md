# Participant Burden Budget

Participant attention is the scarce resource that keeps the event excellent. This document defines
the burden model, the per-participant budget, and the rate governor — the mechanism that lets the
[live research OS](live-research-os.md) "capture as much as possible" without turning the weekend
into a study. It is implemented as [`engine/burden_budget.py`](../../engine/burden_budget.py) and
stored as the append-only `participant_burden` ledger in
[`schema/006_live_research.sql`](../../schema/006_live_research.sql).

## The principle

> Every *explicit* research touch is a debit against a per-participant budget. The system spends the
> budget on the highest-signal moments and **stays silent otherwise**. A refused prompt is correct
> behavior, not an error to route around — the absence of a prompt is the system protecting the
> golden goose.

This is the operational form of the one hard constraint: if research and experience conflict,
experience wins ([participant-experience.md](participant-experience.md)).

## The burden channels

Not every research interaction costs the same, and some cost *nothing* because the builder was going
to do the thing anyway. The ledger separates them:

```
EXPLICIT (counts against the budget)        AMBIENT (does NOT consume the budget)
  BASELINE        the pre-event survey         APPLICATION        they filled it to get in
  CHECKPOINT      the 6-hourly check-in        MENTOR_LOG_IMPACT  the mentor logs; the builder just got help
  MICRO_PROMPT    a triggered one-liner        ARTIFACT_SUBMISSION they submitted their repo anyway
  INTERVIEW       a sampled/triggered talk
  DIARY           any self-capture prompt
  FOLLOWUP        a 7/30/90-day survey wave
```

The distinction is the whole trick from [capture-system.md](../capture-system.md): the best capture
*is* the builder's flow, lightly structured — instrumenting the help they sought, reading the
artifacts they wrote, observing the demo they were giving anyway. Those are ambient. Only the things
that genuinely interrupt or add work are explicit, and only those are rationed.

## The budget

```
EXPLICIT_CAP_SEC     = 18 min of EXPLICIT research per participant, across the whole 72 hours
MIN_PROMPT_GAP_SEC   = ~45 min minimum between micro-prompts to the same participant
```

Why ~18 minutes: [event1-design.md](../event1-design.md) sets research burden at ≤18 min/participant
because past roughly 25 minutes the experience loss dominates the research gain. That 18 minutes is a
whole-event total — baseline + checkpoints + any prompts + any interview — not per instrument. An
exit interview is the single largest line item (~12–15 min), which is exactly why interviews are
**sampled, not universal** ([adaptive-sampling.md](adaptive-sampling.md)): we cannot afford to
interview everyone, and we don't need to.

An illustrative budget that fits under the cap for a *typical* participant:

```
BASELINE        ~4 min   (pre-event, before the weekend even starts)
START checkpoint ~1 min
MID checkpoints  ~2 min   (2 × ~1 min, tied to a meal/mentor slot)
END checkpoint   ~2 min   (the demo doubles as this — partly ambient)
~2 micro-prompts ~1 min   (only if they hit a high-signal switch/error)
───────────────────────
~10 min explicit → leaves headroom; a sampled exit interview (~12 min) is spent only on the
                   subset we deliberately choose, and those participants get fewer prompts instead.
```

Most participants never approach the cap. The cap exists to stop the *worst* case — a heavily-
observed, much-switched, frequently-interviewed builder — from being over-farmed.

## The rate governor

Beyond the total cap, a **gap** between prompts protects flow moment-to-moment. A builder in deep
flow who hasn't hit friction gets *no* prompts at all — there is nothing to ask and the silence is
correct. Two prompts cannot arrive within ~45 minutes of each other, even if both triggers are
legitimately high-value; the second waits, or is dropped if it goes stale.

```
can_spend(participant, channel, seconds, now) is False when:
   • channel is EXPLICIT and (spent_explicit + seconds) > cap           → budget exhausted
   • channel is MICRO_PROMPT and (now − last_prompt) < MIN_PROMPT_GAP    → too soon
   • (AMBIENT channels are always allowed — they never touch the budget)
```

`spend()` **raises** rather than silently clamping, because the caller must treat a full budget as a
reason to stay silent, not a number to nudge. This is the gate the live loop and the sampler both
consult before anything reaches a participant.

## How the budget steers the system

The budget is not just a cap checked at the end — it actively shapes behavior in real time:

- **The live loop** ([`live_research.py`](../../engine/live_research.py)) checks `can_spend` before
  firing any micro-prompt; over budget → `SILENT`.
- **The sampler** ([`adaptive_sampling.py`](../../engine/adaptive_sampling.py)) uses
  `is_over_half(participant)` to prefer lightly-burdened subjects and **skips anyone over half their
  budget** — we never optimize for extracting the most from one person.
- **The interruption policy** ([interruption-policy.md](interruption-policy.md)) is the timing layer
  on top: even with budget remaining, a bad moment means no ask.

## Researching the right number

Do **not** treat 18 minutes as revealed truth. It is a defensible starting cap from the optimizer
and comparable-event experience, and **how much burden is actually tolerable is itself something
Event 1 should measure** (the real research-minutes tolerance is on the "learnable only by running
it" list in [event1-design.md](../event1-design.md)). The [experience pulse](participant-experience.md)
(`experience_pulse.prompts_annoying`, `research_felt_intrusive`) is the feedback signal: if builders
report prompts as annoying well under the cap, the cap is too high for this cohort and comes down.
The budget is a dial we tune from evidence, not a constant we defend.

## What this prevents

```
the event feeling like a study       ← the cap + the silence-by-default routing
over-frequent checkpoints            ← the rate governor
one person farmed for all the data   ← is_over_half skipping in the sampler
a quiet creep toward "just one more" ← spend() raises; there is no nudge path
```

The burden budget is, in the end, the single most important safeguard that keeps the front end
genuinely excellent — and therefore the safeguard that keeps the whole compounding data asset alive.
