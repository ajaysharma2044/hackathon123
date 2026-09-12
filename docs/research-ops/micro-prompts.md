# Micro-Prompts — The One-Breath Question

**Parts XIX–XX of the [Live Research Operating System](live-research-os.md).**

A micro-prompt is the smallest research instrument in the system: **one line, fired at the freshest
moment, answerable in one breath, skippable, budgeted.** It is what most triggers get *instead of* an
interview — and most triggers get nothing at all ([critical-incidents.md](critical-incidents.md),
default-silence rule). The catalog lives in `MICRO_PROMPTS` in
[`adaptive_questions.py`](../../engine/adaptive_questions.py); each instance shown becomes a `prompt`
row in [`006_live_research.sql`](../../schema/006_live_research.sql).

> **"Answerable in one breath, branch deeper only if useful."** A micro-prompt is not a shrunk
> survey — it is the single highest-value question for *this* detected moment. If the answer turns
> out to be rich, the war room escalates to a sampled interview and a full tree walk
> ([adaptive-questioning.md](adaptive-questioning.md)); the prompt itself stays one line.

## The catalog (`MICRO_PROMPTS`)

Keyed by the `prompt_key` that [`research_triggers.py`](../../engine/research_triggers.py) routes to.
Each is wording already passed through the leading-question audit of
[adaptive-questioning.md](adaptive-questioning.md) — concrete, specific, no assumed cause.

| `prompt_key` | Prompt text | Fired by trigger | Burden |
|---|---|---|---|
| `switch_reason` | "What was the main reason you switched?" | `SWITCH` | 20s |
| `abandon_reason` | "What made you stop using it?" | `ABANDONMENT` | 20s |
| `expected_what` | "What did you expect to happen?" | `TECHNICAL_FAILURE` | 20s |
| `tool_choice_reason` | "What mattered most in choosing this?" | `TOOL_SELECTION` | 20s |
| `credit_effect` | "Did the credit affect your choice?" | `CREDIT_USE` | 15s |
| `credit_ignore` | "You had a credit available — what made you not use it?" | `CREDIT_IGNORE` | 15s |
| `doc_looking_for` | "What were you looking for in the docs?" | `DOCUMENTATION_FAILURE` | 20s |
| `workaround` | "What were you working around?" | `PRODUCT_WORKAROUND` | 20s |
| `pivot_reason` | "What changed your mind?" | `PROBLEM_CHANGE` | 20s |
| `why_not_shortlist` | "What ruled it out?" | `TOOL_REJECTION` | 20s |
| `non_completion` | "What was the main thing that blocked finishing?" | `NON_COMPLETION` | 20s |
| `continuation` | "Do you plan to keep working on this? Why?" | `CONTINUATION_DECISION` | 20s |

Triggers whose action is `MENTOR_NOTE_SUFFICIENT`, `FLAG_FOR_INTERVIEW`, or `OBSERVE_ONLY` fire **no
prompt** — the "why" is already captured by a mentor note, deferred to a richer interview, or simply
logged. Only `FIRE_PROMPT` triggers reach this catalog.

## Examples by trigger (the fresh-moment framing)

```
SWITCH            (telemetry sees product A go quiet, B light up)
   → switch_reason:  "What was the main reason you switched?"        [one tap in-tool, ~20s]

DOCUMENTATION_FAILURE (self-reported 😕 on a doc page, or repeated search-then-leave)
   → doc_looking_for: "What were you looking for in the docs?"       [the gap, in their words]

TOOL_SELECTION    (brokered key first activates)
   → tool_choice_reason: "What mattered most in choosing this?"      [decision criterion, fresh]

CREDIT_USE / CREDIT_IGNORE  (credit consumed — or conspicuously not)
   → credit_effect:  "Did the credit affect your choice?"
   → credit_ignore:  "You had a credit available — what made you not use it?"

MENTOR help (HELP_REQUEST)
   → NO participant prompt. The mentor logs the interaction (≤20s, mentor_interaction table);
     the "why" is a byproduct of the help they already wanted, not a tax on them.

MAJOR_PIVOT / RD_HYPOTHESIS_FAILURE
   → NO prompt. FLAG_FOR_INTERVIEW — too rich for one line; queue a sampled conversation.
```

The timing is the whole point ([capture-system.md](../capture-system.md), freshest-signal
principle): a prompt fired the instant the switch is detected asks while the reason is still on the
screen, not reconstructed at hour 14 from memory.

## Format comparison (capture formats, scored)

The same moment can be captured in different *formats*. Ordinal HIGH/MED/LOW/NONE; these are
design trade-offs, not measured values.

| Format | SignalDepth | Burden | Bias | Cost | ProcessingDifficulty | Scalability | ParticipantComfort | BestUse |
|---|---|---|---|---|---|---|---|---|
| **Multiple-choice + optional text** | MED | LOW | MED (fixed options frame the answer) | LOW | LOW | HIGH | HIGH | the default micro-prompt; fast branch key + room to elaborate |
| **Short voice note** | HIGH | LOW-MED | LOW | MED (transcription) | MED | MED | MED | rich "why" when typing would cost more than talking |
| **Short text** | MED | MED | LOW | LOW | LOW | HIGH | MED | a specific recalled fact ("what were you looking for") |
| **Researcher prompt** (a human asks the one line) | HIGH | MED | MED (interviewer effects) | HIGH | MED | LOW | MED-HIGH | when presence and a follow-up probe matter |
| **Mentor capture** (logged as a byproduct of help) | MED-HIGH | NONE (to participant) | MED (helper is not neutral; intensity confound) | LOW | MED | HIGH | HIGH | friction surfaced while helping; never counted as a neutral observation |

The default micro-prompt is **multiple-choice + optional text**: the choice is the branch key that
`Node.next_qid` resolves, and the optional text is the verbatim that may become a
`qualitative_observation`. Voice is offered where the "why" is worth more than the typing cost (the
"rubber-duck" note in [capture-system.md](../capture-system.md)). Mentor capture costs the
participant *nothing* — it is the help they already sought — but carries the mentor-intensity
confounder and is never laundered into a neutral observation.

## Method comparison (the full qualitative spectrum)

Micro-prompts sit at the low-burden end of a spectrum. The war room chooses the *lightest* method
that answers the question ([adaptive-sampling.md](adaptive-sampling.md) burden-awareness):

```
            burden → participant          signal depth          scalability
typed text          LOW                   MED                   HIGH
multiple-choice     LOW                   LOW-MED               HIGH
voice note          LOW-MED               HIGH                  MED
audio interview     HIGH                  HIGH                  LOW
live researcher     MED-HIGH              HIGH                  LOW
mentor note         NONE (byproduct)      MED-HIGH              HIGH     (confounded: helper ≠ neutral)
team retro          MED (shared)          HIGH (group dynamics) MED
artifact walkthrough LOW (they pitch anyway) HIGH (observed, honest) MED
```

| Method | When to reach for it |
|---|---|
| **typed text / MC** | a fresh, detectable moment; the micro-prompt default |
| **short voice note** | the "why" is rich but a full interview is unwarranted |
| **audio interview** | a sampled/flagged deep dive; walks a full question tree, consent-recorded |
| **live researcher** | presence and adaptive follow-up matter; fact ≠ interpretation enforced in the note |
| **mentor note** | friction that surfaces during help they asked for — logged in ≤20s, confound flagged |
| **team retro** | team-level decisions and coordination; good teams retro anyway |
| **artifact walkthrough** | the demo/pitch reframed as a structured interview — honest, low added burden |

## Rules that keep the prompt a prompt

- **Skippable is mandatory.** `prompt.skipped` exists because a prompt the participant can't dismiss
  is a tax. A dismissed prompt is a valid, logged outcome.
- **Budgeted.** Every fired prompt debits `participant_burden` (`MICRO_PROMPT` channel); the
  prompt-rate governor in [`burden_budget.py`](../../engine/burden_budget.py) will suppress a prompt
  that would push a participant over budget or violate the rate limit — the absence of a prompt is
  correct behavior ([participant-burden.md](participant-burden.md)).
- **Interruptible-aware.** A prompt does not fire into a `DO_NOT_INTERRUPT` window
  (`team_interrupt_window`, [Part XVIII](live-research-os.md)).
- **Branch only if useful.** The one line is complete on its own; it escalates to a tree walk only
  when the war room decides the thread is worth a deeper, sampled interview — never by stacking more
  lines on the same participant in the moment.
