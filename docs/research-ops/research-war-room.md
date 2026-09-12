# The Research War Room — Live Operations Room

**Part X of the [Live Research Operating System](live-research-os.md).** Layers 10–11 of the 17:
emerging-theme detection and the live operations room that runs the loop.

The war room is the place where the event stops being a stream of disconnected events and becomes
an *emerging understanding*. Its one job is stated in the master doc's live loop
([live-research-os.md](live-research-os.md), "the core mechanism"): **turn raw observations into
provisional patterns DURING the event, so the next question is sharper than the last.** It is not a
reporting dashboard built after the weekend — it runs while the weekend runs, and what it learns at
hour 14 changes who we talk to at hour 20.

> The binding constraint still governs: **the experience wins.** The war room watches the event at
> the **team and event level**, never the person level. It is a synthesis surface, not a
> surveillance surface. Every panel below is built from team-grain or event-grain evidence; none of
> them renders a per-person score, attention signal, or protected-trait inference — the schema has
> no column for any of these ([`006_live_research.sql`](../../schema/006_live_research.sql),
> Invariant 5), and [`live_research.py`](../../engine/live_research.py) `assert_clean` rejects a row
> that tries to carry one.

## The two halves of the room

The room is split down the middle, and the split is the operations-vs-research firewall from the
master doc ([live-research-os.md](live-research-os.md), "Operations data vs client research data").
One signal can feed both halves, but it is never laundered from one into the other.

```
  ┌─────────────────────────── THE WAR ROOM ────────────────────────────┐
  │  LEFT HALF — OPERATIONS              │  RIGHT HALF — RESEARCH         │
  │  (keeps the event excellent now)     │  (builds the deliverable)      │
  │                                      │                                │
  │  active teams · team state           │  research-trigger queue        │
  │  mentor demand by category           │  interview queue               │
  │  major blockers · support load       │  emerging themes               │
  │  food · rooms · check-in · Wi-Fi     │  unanswered questions          │
  │  product usage (aggregate)           │  negative cases · unusual runs │
  │                                      │  candidate follow-ups          │
  │      → drives event-adaptation.md    │      → drives analytic-memos.md │
  └──────────────────────────────────────────────────────────────────────┘
```

The LEFT half is fed by [`mentor_routing.py`](../../engine/mentor_routing.py) (`queue_depths`,
`support_intensity`) and the operations tables (`support_request`, `team_interrupt_window`). The
RIGHT half is fed by [`research_triggers.py`](../../engine/research_triggers.py) (the routed trigger
queue) and the research tables (`observation`, `critical_incident`, `analytic_memo`,
`research_question_backlog`, `negative_case`).

## The live views (ASCII panels)

All numbers below are **illustrative** — placeholders to show the shape of a panel, not measured
values from any event. Grain and refresh are noted per panel; most refresh on event time (when the
underlying behavior happened, `occurred_at`), not on wall-clock polling.

### Operations: active teams, team state, blockers

```
 ACTIVE TEAMS  47 building · 3 on break · 2 at judging prep      (grain: team · live)
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ STATE          teams │  MAJOR BLOCKERS (open >30m)     teams │ INTERRUPTIBLE  │
 │ building         31  │  auth / API keys                  7   │ DO_NOT      12 │
 │ blocked          9   │  database setup                  12   │ MICRO_OK    26 │
 │ switching        4   │  deploy / infra                   4   │ SHORT_OK     9 │
 │ pivoting         2   │  model latency                    3   │ DEEP_OK      0 │
 │ idle/unknown     1   │  docs can't find answer           5   │                │
 └────────────────────────────────────────────────────────────────────────────┘
```

Team state and the interrupt column come from `team_interrupt_window.state`
(`DO_NOT_INTERRUPT | MICRO_PROMPT_OK | SHORT_INTERVIEW_OK | DEEP_INTERVIEW_OK`); a team near a
deadline is never prompted, regardless of how interesting its blocker is.

### Operations: mentor demand + product usage (aggregate only)

```
 MENTOR DEMAND  (open support_request by routed category)        (grain: category · live)
   DB        ████████████ 12   ← spike; see event-adaptation.md (add DB capacity)
   BACKEND   ██████ 6
   INFRA     ████ 4
   AI_ML     ███ 3
   FRONTEND  ██ 2          avg wait 14m · longest open 38m (DB)

 PRODUCT USAGE  (aggregate, min-cell-suppressed; NEVER per-participant)
   Product X   activation 41/47 teams · meaningful-use 28 · in shipped artifact 19
   Product Y   activation 22/47 teams · meaningful-use 11 · in shipped artifact  7
   (cells < min_cell render as "—"; raw telemetry stays on the research side)
```

Product usage is the one panel that straddles the firewall: it is operationally useful (is the
brokered-key path healthy?) and research-relevant. It is shown **aggregate and min-cell-suppressed**
via [`live_research.py`](../../engine/live_research.py) `ClientView.aggregate` even to the internal
room, so the habit of aggregation is never broken.

### Research: the trigger queue (the room's heartbeat)

```
 RESEARCH-TRIGGER QUEUE   (from research_triggers.py routing)   (grain: incident · live)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ trigger_type        detector   action              value  burden  state       │
 │ SWITCH              TELEMETRY   FIRE_PROMPT         HIGH    20s    fired→answd  │
 │ RD_HYPOTHESIS_FAIL  OBSERVER    FLAG_FOR_INTERVIEW  HIGH     0s    queued ●    │
 │ REPEATED_HELP       MENTOR      FLAG_FOR_INTERVIEW  HIGH     0s    queued ●    │
 │ ABANDONMENT         TELEMETRY   FIRE_PROMPT         HIGH    20s    fired→skip  │
 │ DOCUMENTATION_FAIL  SELF        FIRE_PROMPT         HIGH    20s    fired→answd │
 │ HELP_REQUEST        MENTOR      MENTOR_NOTE_SUFFICIENT MED   0s    note logged │
 │ ARCHITECTURE_CHANGE OBSERVER    OBSERVE_ONLY        MED      0s    logged      │
 └──────────────────────────────────────────────────────────────────────────────┘
 ● = needs a researcher. Most rows ask the participant NOTHING — OBSERVE_ONLY and
   MENTOR_NOTE_SUFFICIENT are the majority, by design (silence is the default action).
```

The room watches `TriggerRegistry.high_value_asks()` most closely — the triggers that both warrant a
participant question AND carry HIGH commercial value. A `FIRE_PROMPT` row only becomes an actual
participant ask if the burden budget ([participant-burden.md](participant-burden.md)) and the
interrupt window both allow it; otherwise it degrades to a mentor note or silence.

### Research: interview queue, emerging themes, open questions

```
 INTERVIEW QUEUE              EMERGING THEMES (provisional)       OPEN QUESTIONS
 (adaptive_sampling.py)       (qualitative-coding.md, EVOLVING)   (question_backlog)
 ┌──────────────────────┐     ┌──────────────────────────────┐   ┌──────────────────┐
 │ seg        n  reason  │     │ AUTHENTICATION    conf: MED   │   │ Q-07 PRIORITIZED │
 │ SWITCHER   3  fresh   │     │   12 mentions / 7 teams        │   │ Q-12 OPEN        │
 │ R&D_FAIL   2  gap     │     │   5 Product X · 2 Product Y    │   │ Q-19 OPEN (emerg)│
 │ NON_ADOPT  2  gap     │     │ DB_SETUP_FRICTION conf: MED   │   │ Q-03 SATURATED   │
 │ ABANDONER  1  neg-case│     │   12 teams stuck · 4 switched  │   │ Q-22 CONTRADICTED│
 └──────────────────────┘     │ DOCS_GAP          conf: LOW   │   └──────────────────┘
                              └──────────────────────────────┘
```

Emerging themes are labeled `conf: LOW | MED | HIGH` and carry `status = EVOLVING | STABLE |
RETIRED` (`analytic_memo`). A theme is a **hypothesis, not a finding** — it never crosses to a
client without passing the promotion gate ([evidence-graph.md](evidence-graph.md)). The
AUTHENTICATION panel reads as an illustrative worked example:

```
 AUTHENTICATION      12 mentions / 7 teams / 5 Product X / 2 Product Y
 DATABASE SWITCHES   X→Y: 4   Y→X: 1          (net flow toward Y; why? → interview SWITCHERs)
 R&D CHALLENGE       approaches  A:4  B:3  C:1  D:2
 FAILED APPROACHES   A1  A2  C1                 (→ flag RD_HYPOTHESIS_FAILURE interviews)
```

These counts are **descriptive (L1)**. "AUTHENTICATION is the top friction" is a frequency claim;
"auth friction predicts switching" is a different, testable claim and must not be conflated with it
([capture-system.md](../capture-system.md), "LLM themes are labels, not ground truth").

### Research: negative cases, unusual behaviors, candidate follow-ups

```
 NEGATIVE CASES (disconfirmation search)        UNUSUAL / CANDIDATE FOLLOW-UPS
 ┌──────────────────────────────────────┐      ┌──────────────────────────────────┐
 │ claim: "DB friction causes switching" │      │ Team 14: shipped w/ Product Y but │
 │  looking in: teams that HIT DB        │      │   never opened the brokered key → │
 │  friction but did NOT switch          │      │   UNEXPECTED_USE_CASE? (interview) │
 │  found: 3 (so the claim is partial)   │      │ Team 31: zero mentor touches,     │
 │  → memo updated, confidence held MED  │      │   finished early → OUTLIER, not a │
 └──────────────────────────────────────┘      │   "best team" score (NO scoring)  │
                                                └──────────────────────────────────┘
```

The negative-case panel is non-optional: the loop **deliberately seeks the contradiction**
([live-research-os.md](live-research-os.md), "confirm AND contradict";
[`live_research.py`](../../engine/live_research.py) `Action.kind == SEEK_NEGATIVE_CASE`). An "unusual
behavior" is logged as an outlier to understand, never as a ranking of participants.

## The synthesis rhythm

The room runs on a cadence, not on a stream of alerts. Every few hours the Research Ops Lead and
the lead researchers step back from the live panels and *synthesize*:

```
  every ~3-4h (and at each phase boundary, event-phase-plan.md)
      observe the panels  →  write / update an ANALYTIC MEMO  →  sharpen ONE question
            │                        │                                 │
            │                 (emerging_pattern +                (re-prioritize the
            │                  supporting_evidence +              research_question_backlog;
            │                  REQUIRED contradictory_evidence)    the next ask is sharper)
            ▼                        ▼                                 ▼
      a pattern is named       a memo is a research STATE,       the loop closes: the next
      with a confidence        never a finding (analytic-        prompt/interview targets the
      label                    memos.md)                         gap the memo exposed
```

A memo without `contradictory_evidence` is **rejected at write time** (`analytic_memo` requires the
field; [analytic-memos.md](analytic-memos.md)). That is the structural guard against the room
drifting into confirmation — every synthesis step has to say what it looked at that did *not* fit.
The output of the rhythm is not a conclusion; it is a **better next question**, fed back to the
backlog and to [adaptive-sampling.md](adaptive-sampling.md).

## What the war room is NOT

- **Not a participant-monitoring room.** No per-person timeline, no attention or productivity score,
  no "who is slacking" view. Grain is team/event. The no-go list in
  [live-research-os.md](live-research-os.md) holds here in full.
- **Not a client-facing screen.** What a client may see live is the narrow, aggregate subset
  specified in [dashboard-spec.md](dashboard-spec.md) (Client-Visibility, Part XXXVI) — never these
  raw panels, never the trigger queue, never the memos.
- **Not a findings engine.** It produces *provisional* understanding. The jump from memo → claim →
  finding happens through the promotion gate in [evidence-graph.md](evidence-graph.md), with both
  supporting and contradictory evidence enumerated.

The war room is where the human sensor network ([live-research-os.md](live-research-os.md)) becomes
coordinated: field researchers, mentors, and the adaptive engine all report into one room, and the
room decides — under burden and interruption policy — what the event should learn next.
