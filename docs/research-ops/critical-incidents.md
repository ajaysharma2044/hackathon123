# Critical Incident Engine

The taxonomy of "something interesting just happened" and the routing rule for each one. This is
layer 4 of the [live research OS](live-research-os.md) — the thing that *notices*, so the system can
ask the right person one good question at the freshest moment instead of surveying everyone at the
end. It is implemented as [`engine/research_triggers.py`](../../engine/research_triggers.py) and
stored as `incident_type_registry` + `critical_incident` in
[`schema/006_live_research.sql`](../../schema/006_live_research.sql).

## The governing bias: silence by default

A trigger firing does **not** mean a participant gets a question. Most triggers route to
`OBSERVE_ONLY` or `MENTOR_NOTE_SUFFICIENT` — the signal is already captured passively, and asking
would just spend attention we promised to protect ([participant-burden.md](participant-burden.md)).
Fewer than half of the defined triggers ever fire a participant-facing prompt. We spend a question
only where the signal is **high-value, freshest now, and not already captured** by a mentor note, an
artifact, or telemetry.

```
trigger detected → route():  FIRE_PROMPT            one micro-prompt, if burden + timing allow
                             MENTOR_NOTE_SUFFICIENT  the mentor log already has the "why"
                             FLAG_FOR_INTERVIEW      too rich for a prompt — queue a deeper talk
                             OBSERVE_ONLY            log it, ask nothing
```

The routing gate is `LiveResearchOS.observe_then_decide` in
[`engine/live_research.py`](../../engine/live_research.py): even a `FIRE_PROMPT` trigger stays silent
if the team is in a `DO_NOT_INTERRUPT` window ([interruption-policy.md](interruption-policy.md)) or
the participant's research-minutes budget is spent.

## The taxonomy

For each trigger: **who detects it**, **whether it asks a question**, **which prompt / interview
segment** ([micro-prompts.md](micro-prompts.md), [adaptive-questioning.md](adaptive-questioning.md)),
the **participant burden** of the answer, and its **commercial value** (why we care).

### Tool & product decisions — the commercial core

| Trigger | Detector | Action | Prompt/segment | Burden | Value |
|---|---|---|---|---|---|
| `TOOL_CONSIDERATION` | observer | observe | technology_choice | 0s | MED |
| `TOOL_SELECTION` | telemetry | **prompt** | "what mattered most?" | 20s | HIGH |
| `TOOL_REJECTION` | checkpoint | **prompt** | "what ruled it out?" | 20s | HIGH |
| `SWITCH` | telemetry | **prompt** + follow-up | "main reason you switched?" | 20s | HIGH |
| `ABANDONMENT` | telemetry | **prompt** + follow-up | "what made you stop?" | 20s | HIGH |
| `PROBLEM_CHANGE` | checkpoint | **prompt** | "what changed your mind?" | 20s | MED |
| `MAJOR_PIVOT` | observer | **interview** | pivot | — | HIGH |
| `ARCHITECTURE_CHANGE` | observer | observe | architecture | 0s | MED |

### Help & friction — route to support first, capture as byproduct

| Trigger | Detector | Action | Prompt/segment | Burden | Value |
|---|---|---|---|---|---|
| `HELP_REQUEST` | mentor | mentor-note | (the mentor log *is* the capture) | 0s | MED |
| `REPEATED_HELP_REQUEST` | mentor | **interview** | repeated_friction | — | HIGH |
| `TECHNICAL_FAILURE` | telemetry | **prompt** | "what did you expect to happen?" | 20s | HIGH |
| `DOCUMENTATION_FAILURE` | self (`/blocked`, doc reaction) | **prompt** | "what were you looking for?" | 20s | HIGH |
| `MENTOR_DEPENDENCY` | mentor | observe | dependency | 0s | HIGH |
| `RESOURCE_CONSTRAINT` | checkpoint | observe | resource | 0s | MED |

### Outcomes — successes, surprises, non-completion

| Trigger | Detector | Action | Prompt/segment | Burden | Value |
|---|---|---|---|---|---|
| `UNEXPECTED_SUCCESS` | observer | **interview** | unexpected | — | MED |
| `UNEXPECTED_USE_CASE` | observer | **interview** + follow-up | unexpected_use | — | HIGH |
| `PRODUCT_WORKAROUND` | observer | **prompt** | "what were you working around?" | 20s | HIGH |
| `FEATURE_REQUEST` | self | observe | feature | 0s | MED |
| `PROTOTYPE_COMPLETION` | artifact | observe | completion | 0s | LOW |
| `NON_COMPLETION` | artifact | **prompt** | "main thing that blocked finishing?" | 20s | MED |

### R&D-specific

| Trigger | Detector | Action | Prompt/segment | Burden | Value |
|---|---|---|---|---|---|
| `RD_HYPOTHESIS_FAILURE` | observer | **interview** + follow-up | rd_failure | — | HIGH |
| `RD_CONVERGENCE` | observer | observe | rd_converge | 0s | HIGH |
| `RD_DIVERGENCE` | observer | observe | rd_diverge | 0s | HIGH |

### Incentives, team, continuation

| Trigger | Detector | Action | Prompt/segment | Burden | Value |
|---|---|---|---|---|---|
| `CREDIT_USE` | telemetry | **prompt** | "did the credit affect your choice?" | 15s | HIGH |
| `CREDIT_IGNORE` | telemetry | **prompt** | "what made you not use the credit?" | 15s | HIGH |
| `TEAM_CHANGE` | observer | observe | team | 0s | LOW |
| `CONTINUATION_DECISION` | self | **prompt** + follow-up | "keep working on this? why?" | 20s | HIGH |

## How a trigger is detected

Detection is triangulated, never asserted from one source — the hardest case is `SWITCH`, which the
[capture system](../capture-system.md) builds from brokered-key telemetry going silent + a dependency
manifest change + a checkpoint "what are you using now" delta. The detector field records *which*
channel fired, so the war room can see, e.g., that a switch was inferred from telemetry silence
alone (lower confidence) vs confirmed by three signals (higher).

```
TELEMETRY   brokered-key activity/silence, error class, cadence     → TOOL_SELECTION, SWITCH, FAILURE, CREDIT_*
MENTOR      a help request, or the Nth repeat                        → HELP_REQUEST, REPEATED_HELP, DEPENDENCY
OBSERVER    a field researcher sees it                               → PIVOT, UNEXPECTED_*, WORKAROUND, RD_*
CHECKPOINT  a delta between two 6-hourly check-ins                   → TOOL_REJECTION, PROBLEM_CHANGE, RESOURCE
ARTIFACT    repo/deploy/dependency state at submit                   → PROTOTYPE_COMPLETION, NON_COMPLETION
SELF        a one-tap signal the builder sends (`/blocked`, reaction)→ DOCUMENTATION_FAILURE, FEATURE, CONTINUATION
```

## The highest-value triggers

The ones the [war room](research-war-room.md) watches for — both worth a participant ask *and*
high commercial value (`TriggerRegistry.high_value_asks()`):

```
SWITCH · ABANDONMENT · TOOL_SELECTION · TOOL_REJECTION · TECHNICAL_FAILURE · DOCUMENTATION_FAILURE
PRODUCT_WORKAROUND · UNEXPECTED_USE_CASE · CREDIT_USE · CREDIT_IGNORE · CONTINUATION_DECISION
+ (interview-only) MAJOR_PIVOT · REPEATED_HELP_REQUEST · RD_HYPOTHESIS_FAILURE
```

These map directly onto the questions clients pay most for ([question-catalog.md](../question-catalog.md)):
why the non-choosers didn't choose, whether credits buy retention or just activation, where
integration breaks, and what the failed R&D paths were.

## Discovering new triggers

The taxonomy is **versioned** (`incident_type_registry(trigger_type, version)`) precisely because
the event will surface incident types we didn't anticipate. When a field researcher or the war room
notices a recurring moment that no trigger names — say, "experienced builders skipping the starter
template entirely" — it becomes a candidate new trigger *and* an emergent
[backlog question](analytic-memos.md). New triggers are added at a new version; old
`critical_incident` rows keep their original version, so the taxonomy can evolve without rewriting
history.

## For each trigger, the design questions we answered

Per the brief, every trigger was specified on: who detects it · how · whether to ask · which
question · whether researcher follow-up is needed · whether a mentor note is enough · participant
burden · commercial value · relevant engines. The tables above are that specification in compact
form; the machine-readable version is the `TRIGGERS` registry in
[`research_triggers.py`](../../engine/research_triggers.py), and the burden/ask columns are what the
[burden budget](participant-burden.md) and [interruption policy](interruption-policy.md) consult
before anything reaches a participant.
