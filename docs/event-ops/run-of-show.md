# Run of Show — The 72-Hour Operating Timeline

The hour-by-hour, block-by-block run sheet for Event 1: a Cornell-only premium fly-in, ~150–200
builders, 72h ([event1-design.md](../event1-design.md)). Its sibling is [logistics.md](logistics.md)
(what physically exists); this doc is **when it happens, who does it, and who owns it.** The org that
fills the "owns it" column is [org-chart-and-roles.md](org-chart-and-roles.md); coverage is staffed by
`ops_shift` / `shift_assignment` in [`../../schema/007_event_ops.sql`](../../schema/007_event_ops.sql)
and sized by [`../../engine/staffing_model.py`](../../engine/staffing_model.py).

The central idea: **the ops run-of-show and the research cadence are two layers on ONE timeline.** The
ops layer runs the event; the research layer ([../research-ops/event-phase-plan.md](../research-ops/event-phase-plan.md))
rides lightly on top, spending explicit participant attention only at the freshest, cheapest moments
and going silent in deep build. Neither layer taxes the other — that is the design constraint, not an
aspiration.

> **Times are illustrative.** The clock below labels a Friday-morning start with 3 nights (Fri/Sat/Sun),
> consistent with [funding.md](../funding.md). `T+0h` is the opening ceremony; the 72h build clock and
> the exact deadline are planning choices, not sourced facts. Real dates replace these.

## The shape of the 72 hours

```
 DAY 0 (Fri)   check-in ▸ OPENING ▸ team formation ▸ BUILD STARTS ─────────────┐
 DAY 1 (Sat)   deep build · workshops · mentor hours · meals · night mini-event │  ≥40%
 DAY 2 (Sun)   deep build · sponsor talks · MIDPOINT · night activity           │  UNCONSTRAINED
 DAY 3 (Mon)   final crunch ▸ SUBMISSION ▸ science-fair EXPO ▸ FINALS ▸ AWARDS ──┘  BUILD TIME
        ▲ heaviest research touch at the EDGES (arrival, meals, post-switch, submission, demo)
        ▼ near-silent in the middle of each build block and through both overnight windows
```

**≥40% of the build surface stays unconstrained** ([event1-design.md](../event1-design.md)): workshops,
talks, and mini-events are optional and scheduled *around* the free-choice core, never on top of it.
Sponsor programming that eats the open track kills the tool-choice baseline the research depends on.

## The master run sheet

Legend for the owning role (`staff_role` in [`../../schema/007_event_ops.sql`](../../schema/007_event_ops.sql)):
**PX** participant-experience · **LOG** logistics/crew · **AV** tech/AV · **OPS** operations/F&B · **MENT**
mentorship · **JUDGE** judging & awards · **SAFE** safety/on-call · **EXEC** director · **RES** research org.

| Clock | Participant-facing activity | Ops crew action | Owns it |
|---|---|---|---|
| **DAY 0 — Friday** | | | |
| −4h | (doors closed) | Setup: tables, power strips, signage, A/V check | LOG + AV |
| −2h → +0 | **Check-in window** — ID → badge → swag → consent → baseline → team area | Run arrival pipeline; staff peak line | PX (+RES at consent/baseline) |
| **T+0h** | **Opening ceremony** — welcome, **CoC briefing**, safety/quiet-room walkthrough | Stage A/V, livestream, seat the hall | EXEC + AV + SAFE |
| +0.5h | Sponsor / challenge intros (3–4 non-competing) | Mic runners; slide handoff | EXEC + AV |
| +1.5h | **Team formation** — pitch board, matchmaking, team registration | Facilitate; register teams; fix t0 collab graph | PX (+RES observing) |
| +3h | **Build starts** — clock begins | Open help desk; hardware lab live | MENT + LOG |
| +5h | **Fri dinner** (opening meal) | Serve; refresh coffee/snacks | OPS |
| +6h → late | Deep build · first workshop (optional) | Mentor office hours; floaters | MENT |
| overnight | Quiet hours; snacks stocked | **Overnight shift** (`is_overnight`); on-call live | SAFE + LOG |
| **DAY 1 — Saturday** | | | |
| +14h | **Breakfast** | Serve; hall reset | OPS |
| +16h | Workshops + **sponsor tech talks** (optional, off the open track) | Room A/V; capacity mgmt | AV + MENT |
| +19h | **Lunch** | Serve | OPS |
| +20h → eve | Deep build · **mentor office hours** peak | Help-queue triage; runners | MENT |
| +26h | **Dinner** | Serve | OPS |
| +28h | **Night mini-event** (optional: games, wellness, social) | Run activity; keep it opt-in | PX |
| +32h | Overnight snack (2am); quiet hours | Overnight shift; on-call | SAFE + LOG |
| **DAY 2 — Sunday** | | | |
| +38h | **Breakfast** | Serve | OPS |
| +40h | Workshops / advanced talks (optional) | Room A/V | AV + MENT |
| +43h | **Lunch** | Serve | OPS |
| +44h | **MIDPOINT** — deep build; pivots and switches peak | Mentor surge; expo-hall prep begins | MENT + LOG |
| +50h | **Dinner** | Serve | OPS |
| +52h | Night activity (optional); final-stretch briefing | Announce deadline logistics + expo format | PX + EXEC |
| +56h | Overnight snack; quiet hours | Overnight shift; on-call | SAFE + LOG |
| **DAY 3 — Monday** | | | |
| +62h | **Breakfast**; final crunch | Serve; stage/expo turnover | OPS + LOG |
| **+66h** | **Submission deadline** — repo, deploy, Devpost, table number | Collect `submission` rows; assign stations | AV + JUDGE |
| +67h | **Science-fair expo** — teams demo at stations | Run rotation; time-keep | JUDGE |
| +69h | **Finals** — top teams on stage | Stage A/V; judge escort | JUDGE + AV |
| +71h | **Closing + awards** — prizes, thanks | Award logistics; `prize_award` | EXEC + JUDGE |
| +72h → | Departure; teardown (30 min); equipment return | Teardown; lost-and-found | LOG + CREW |

Coverage is not a table of names but a set of `ops_shift` rows with a `min_headcount` floor and
`is_overnight` flag; `shift_assignment.checked_in_at` records who actually showed. `staffing_model.py`
sizes each role (mentors ~1:10, judges by the MLH formula, volunteers ~1:20, overnight coverage) and
**warns on the thin spots** — a check-in peak or an under-staffed overnight is a flagged risk, not a
surprise.

## Judging in the run sheet

The Monday close is the science-fair format ([judging-system.md](judging-system.md)): teams demo at
`submission.table_number` stations, judges rotate on the MLH cadence (`J = ceil(P·rounds·min/window)`,
n=3, t=4), scoring is **stack-rank** (3/2/1) rather than absolute to de-bias strict/lenient judges, and
finals put the top teams on stage. Conflicted judges are blocked in `judging_assignment`
(`conflict_blocked = true` for a judge's own team or sponsor). Judging is a hard `DO_NOT_INTERRUPT`
window for the research layer — see below.

## The research cadence — the second layer on the same timeline

The research OS is **not** a parallel schedule that competes for participant time. It overlays the ops
run sheet at the moments the ops layer already creates, and stays silent otherwise
([../research-ops/event-phase-plan.md](../research-ops/event-phase-plan.md), and the burden budget of
≤~18 explicit research-minutes per participant across the whole weekend). Where each research touch
sits:

```
 OPS TIMELINE   check-in ── build ─ meals ─ build ─ MIDPOINT ─ build ── SUBMIT ─ EXPO ─ AWARDS
 RESEARCH       │baseline│   ·  │ micro │  ·  │ war-room │  ·  │ (silent)│ retro │interviews│ ···
                 (START)     ↑ prompts   ↑ synth       ↑ near-deadline: NOTHING     (POST_EVENT)
                             only at good moments      every ~3–4h        exit interviews → 7/30/90d
```

| Where on the ops timeline | Research activity | Why it sits here |
|---|---|---|
| Check-in (Day 0) | **Consent + START baseline** | must precede any capture; fixes t0 before exposure |
| Build blocks | **Micro-prompts on switch / help-resolution only** | the two highest-signal fresh moments ([../research-ops/interruption-policy.md](../research-ops/interruption-policy.md)) |
| Meal breaks | `SHORT_INTERVIEW_OK` window | they're already paused and social |
| Every ~3–4h | **War-room synthesis** — memos, next-question backlog | staff-side; touches no participant |
| MIDPOINT (Sun) | MIDPOINT checkpoint (≤5 items) | pivots/switches peak; richest window, carefully metered |
| Near the deadline (Mon) | **NOTHING — `DO_NOT_INTERRUPT`** | the worst possible moment to ask ([../research-ops/interruption-policy.md](../research-ops/interruption-policy.md)) |
| Overnight (both nights) | **NOTHING — protected sleep hours** | rest is protected even for the tired team |
| Submission / retro | END checkpoint, framed as the retro they'd do anyway | pressure off; reflection is cheap |
| Expo / demo | Structured exit-interview prompts; scheduled client observation | they're presenting anyway; judging itself is untouched |
| Post-event → 7/30/90d | Stratified exit interviews → longitudinal follow-up | the retention asset ([../research-ops/event-phase-plan.md](../research-ops/event-phase-plan.md)) |

Two lines are absolute and worth restating because they are where the two layers could collide and
must not:

- **No prompts near the submission deadline.** The Monday final crunch is `DO_NOT_INTERRUPT`; the
  incident is still captured passively (mentor note, telemetry, artifact) but no explicit ask reaches
  the builder. Research yields to the crunch, unconditionally.
- **No prompts during sleep hours.** Both overnight windows are protected — the quiet room's posted
  hours (from [logistics.md](logistics.md)) and the research sleep-hours are the same hours by
  construction.

## The two layers, staffed separately, on one clock

The ops crew and the research staff are **different people on different shift systems** — ops runs on
`ops_shift`, the research org runs on `research_shift` (schema 006) — precisely so that running the
event well and observing it richly never contend for the same hands ([operational-architecture.md](operational-architecture.md)).
The war room reads the ops feed (mentor-queue depth, meal timing, room capacity, team count) to keep
the weekend excellent in real time, but that operations data and the client research data stay separate
streams ([../research-ops/live-research-os.md](../research-ops/live-research-os.md)). One timeline, two
layers, one hard rule: **if the research and the experience ever conflict, the experience wins** — and
the run sheet above is built so they rarely have to.
