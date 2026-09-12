# Team-State Model

The **team as a dynamic system**. This is the sensing half of the engine — how a team's condition is
represented, observed at near-zero burden, tracked against an archetype-specific expectation, and
labelled EARLY / ON_TRACK / AT_RISK so the rescue policy can decide whether to do anything at all.
It is the input to [rescue-policy.md](rescue-policy.md); the master framing (objective, loop, metric)
is [adaptive-rescue-engine.md](adaptive-rescue-engine.md). The runnable core is
[`../../engine/team_state.py`](../../engine/team_state.py); the storage is
[`../../schema/008_team_rescue.sql`](../../schema/008_team_rescue.sql).

The two invariants below are not aspirations; they are enforced in code and schema.

> **Invariant 1 — a team is a VECTOR, never one collapsed score.** There is deliberately no
> `team_score`. `TeamState.vector()` returns the labelled dimensions; there is intentionally no
> scalar-summary method.
>
> **Invariant 2 — no individual score.** Contribution is captured as *voluntary ownership*, never
> graded output. This module never attributes progress to a person; `assert_clean` (shared with the
> research layer, [../research-ops/live-research-os.md](../research-ops/live-research-os.md)) rejects
> any forbidden person-score / protected-trait key that tries to sneak into `dims`.

---

## Part I — The decomposed state vector

A single "how's the team doing" number would be worse than useless: it would invite ranking, hide
*which* thing is wrong, and destroy the one property the rescue policy needs — a diagnosis. So
`TeamState` carries **17 named dimensions** (`DIMENSIONS` in
[`team_state.py`](../../engine/team_state.py)), stored as labelled `dims` jsonb so they are **never
silently summed**:

```
goal_clarity        problem_quality      scope_fit           capability_coverage
role_coverage       task_ownership       technical_progress  artifact_progress
blocker_severity    mentor_need          decision_latency    team_coordination
workload_balance    energy               confidence          time_remaining
submission_readiness
```

Why kept separate, not collapsed:

- **Different dimensions imply different interventions.** Low `scope_fit` wants the scope optimizer;
  high `blocker_severity` wants a mentor; low `role_coverage` wants a capability route. A sum of the
  three points nowhere. Diagnosis (`diagnose` in [rescue-policy.md](rescue-policy.md)) reads the
  vector dimension-by-dimension.
- **A collapsed score is a ranking.** The moment two teams have comparable scalars, someone sorts
  them. The vector has no total order, on purpose.
- **Two dimensions can point opposite ways at once** and both be true: a team can be high on
  `technical_progress` and dangerously low on `submission_readiness`. That is a *demo-rescue* signal,
  invisible to any average.

Each dimension is an **ordinal status** (roughly 0–3 or a 1–5 pulse), never a continuous "quality."
It is an observation the engine holds, not a claim about the team — Evidence ≠ Claim. `dims` keys are
always a subset of `DIMENSIONS`; `__post_init__` asserts `"team_score" not in dims`.

---

## Part II — Low-burden observables + the one-tap pulse

The vector is only useful if filling it costs the team almost nothing. So most dimensions are
**inferred from things the team was doing anyway** — and the one deliberate ask is a single tap.

```
OBSERVABLE (passive, no participant tax)          →  DIMENSION(S) it informs
─────────────────────────────────────────────────────────────────────────────
commits / deploys / artifact updates              →  technical_progress, artifact_progress, milestone
taskboard state (TODO/DOING/DONE/BLOCKED)         →  task_ownership, workload_balance, blocker
mentor / support-request log                      →  blocker_severity, mentor_need, decision_latency
check-in + team roster                            →  role_coverage, capability_coverage
event-app telemetry (brokered, disclosed)         →  time_remaining, lifecycle transitions
```

These are the **same sensors** the research layer uses ([../research-ops/critical-incidents.md](../research-ops/critical-incidents.md)),
consumed here for a *different purpose* (support, not study) behind the firewall — see
[firewalls-and-ethics.md](firewalls-and-ethics.md). Passive capture is disclosed, never covert; no
keystrokes, no screen, no DMs, no camera.

**The one-tap team pulse** (`team_pulse` in [`008`](../../schema/008_team_rescue.sql)) is the only
active ask, and it is voluntary and debited to the participant-burden budget
([../research-ops/participant-burden.md](../research-ops/participant-burden.md)):

```
STATE:   [ BUILDING ] [ BLOCKED ] [ PIVOTING ] [ TESTING ] [ POLISHING ] [ NEED_HELP ]
+ optional:  contribution?  → YES_ALL_HAVE_WORK · SOMEONE_NEEDS_TASK · OVERLOADED_ROLE · NEED_DIFFERENT_SKILL
+ optional:  energy 1–5
```

One tap moves several dimensions at once and, critically, is a *team* self-report — `contribution`
is a team-level pulse, never a per-person label (Invariant 2). `NEED_HELP` is a direct request, not
an inferred deficiency; the engine treats a request as the strongest, cheapest signal it can get.

---

## Part VI — Milestones M0–M8

Progress is tracked as an ordered milestone ladder (`MILESTONES`), so the engine can ask a
falsifiable question — *how far along, by when?* — without a bureaucratic status meeting.

```
M0_team_formed → M1_problem_selected → M2_plan → M3_first_component → M4_core_loop
   → M5_integration → M6_testing → M7_submission_ready → M8_demo_ready
```

Each milestone is **captured through a tool the team already touches** (`team_milestone.source` ∈
`pulse | artifact | taskboard`): M3 lands when the first component builds; M5 when integration shows
in the repo; M7 when the submission checklist fills. No team is asked to "report milestone 4." The
milestone index is a monotonic `int` on `team_state`; it is a coordinate, not a grade.

---

## Part VII — The expected-progress envelope (per archetype)

The 10 `ARCHETYPES` **progress differently**, so the same milestone index means different things for
different projects. A hardware or R&D team that has reached M2 at the half-way mark may be perfectly
healthy; a consumer app at M2 at half-way is behind. The `_ENVELOPE` encodes, per archetype, the
milestone a *typical* team has reached by a fraction of build time:

```
                     25%   50%   75%  100%      shape
AI_APP                2     4     6     7        steady
DEVELOPER_TOOL        2     4     6     7        steady
CONSUMER_APP          3     5     6     8        fast early, polish-heavy
HARDWARE              1     3     5     7        slow ramp (bring-up cost)
OPTIMIZATION          2     3     5     7        back-loaded (tuning late)
SIMULATION            2     3     5     7        back-loaded
DATA_PROJECT          2     4     5     7        steady
RESEARCH_PROTOTYPE    1     3     4     6        exploratory, lower ceiling
RD_CHALLENGE          1     2     4     6        slowest ramp, high uncertainty
DESIGN_PROTOTYPE      3     5     6     8        fast early
```

`expected_milestone(archetype, time_fraction)` interpolates this (floor to the last step ≤ t).
`TeamState.classify()` then returns a **routing label, not a quality ranking**:

```
milestone_index > expected            → EARLY     (ahead of envelope — candidate for a side quest)
milestone_index == expected, unblocked→ ON_TRACK  (leave it alone)
milestone_index <  expected, OR blocked→ AT_RISK  (surface to the rescue policy)
```

`progress_flag` is an enum `EARLY | ON_TRACK | AT_RISK` in [`008`](../../schema/008_team_rescue.sql)
— deliberately **not** `GOOD | BAD`. AT_RISK means *"this team may be losing preventable time,"* an
invitation to check, never a verdict on the people.

> **Assumption first, learned later.** Every `_ENVELOPE` row starts as an engineering assumption
> (`progress_envelope.is_learned = false`). It is replaced by a curve *calibrated from event data*
> only once we have it. We do not dress an assumption up as a measurement — the flag is in the
> schema so the distinction can never be quietly lost.

---

## Part VIII — Stall detection (multi-signal)

A stall is expensive to get wrong in both directions: miss it and a team bleeds hours; over-call it
and you interrupt a team that is *thinking*. So the rule is deliberately conservative — **one signal
never concludes a stall.** `is_stalled()` fires only when **≥ 2 distinct** `STALL_SIGNALS` co-occur
(`STALL_MIN_SIGNALS = 2`):

```
same_blocker_persists     no_new_artifact          repeat_mentor_request     architecture_churn
no_task_ownership         submission_risk_rising    self_reported_blocked     integration_failed
```

```
   1 signal  →  NOT a stall   (a quiet hour is not a crisis; deep work looks idle from outside)
  ≥2 signals →  likely stall  →  hand to rescue policy for a DIAGNOSIS (never an automatic action)
```

Example: `no_new_artifact` alone is silence, which is often just concentration. `no_new_artifact`
**and** `repeat_mentor_request` together is a team going in circles — worth a look. Detection surfaces
a *candidate*; the human-reviewed rescue policy decides what, if anything, to do
([rescue-policy.md](rescue-policy.md)).

---

## Part XXX — The team lifecycle state machine

`LIFECYCLE` is the coarse mode a team is in — orthogonal to the milestone index (a team can be
`BLOCKED` at M5 or `BUILDING` at M2). It drives *tone*: a `FORMING` team gets composition help; a
`BLOCKED` team gets unblocking; a `SUBMISSION_READY` team is left alone.

```
  FORMING ──► PLANNING ──► BUILDING ──► INTEGRATING ──► TESTING ──► POLISHING ──► SUBMISSION_READY ──► DONE
                              │  ▲             │
                              ▼  │             ▼
                           BLOCKED         PIVOTING ──► (back to PLANNING / BUILDING)
                              │                 ▲
                              └─────────────────┘
```

`BLOCKED` and `PIVOTING` are the transient states the rescue engine watches most closely — but note
the state machine is descriptive, not prescriptive: a team that pivots twice is exploring, not
failing. The lifecycle is stored on every `team_state` row so trajectories are reconstructable after
the event ([../research-ops/team-trajectories.md](../research-ops/team-trajectories.md)).

---

## Parts XXXI–XXXII — Hazard of non-completion / project-success probability

The most tempting number to fabricate is *P(this team ships)*. We refuse to, for now.

> **INITIALLY UNKNOWN.** There is no calibrated project-success probability at Event 1. A real hazard
> model requires `state → outcome` data across *multiple* events; before that exists, any number
> would be invented. `simulate_intervention` (in [rescue-policy.md](rescue-policy.md)) returns
> scenarios with `calibrated_probability = None`, and this module returns **no** success score.

When the model does exist, it is trained on event data and used for **support prioritization only** —
"which AT_RISK teams should the scarce specialist mentor reach first" — and **never** as a
participant ranking or a client-facing judgement. The firewall
([firewalls-and-ethics.md](firewalls-and-ethics.md)) keeps it operational-only. Until then, the
label triplet (EARLY / ON_TRACK / AT_RISK) plus the stall check is the whole prioritization signal,
and that is enough for Event 1.

---

## Part XXXVI — Milestone velocity (descriptive, within-archetype only)

`milestone_velocity(milestones_done, elapsed_hours)` is meaningful milestones per build hour. It is
used to **anticipate** support need — a team decelerating relative to its own archetype's envelope is
worth watching — but it comes with a hard rule:

> Compare velocity **only within an archetype**, and **never** expose it as a cross-team ranking. A
> HARDWARE team's velocity is not comparable to a CONSUMER_APP team's; the `_ENVELOPE` shapes exist
> precisely because these ramps differ. Velocity anticipates need; it does not grade.

Velocity feeds the envelope classification, not a leaderboard. There is no place in the schema to
store a team's velocity *rank*.

---

## A worked illustrative team state vector

*Illustrative — the numbers below are invented to show the shape, not measured.* A DATA_PROJECT team,
~55% through build time, expected milestone ≈ 4, currently at M3:

```
TeamState(
  team_id="t-mango", archetype="DATA_PROJECT", lifecycle="BLOCKED",
  milestone_index=3, time_fraction=0.55,
  dims={
    goal_clarity: 3,  problem_quality: 3,  scope_fit: 1,   capability_coverage: 2,
    role_coverage: 2, task_ownership: 2,   technical_progress: 2, artifact_progress: 1,
    blocker_severity: 2, mentor_need: 2,   decision_latency: 2,   team_coordination: 2,
    workload_balance: 1, energy: 2, confidence: 2, time_remaining: 1, submission_readiness: 0,
  },
  signals={"same_blocker_persists", "no_new_artifact"},   # 2 distinct → stall candidate
)
```

Reading it:

| Question | From the vector | Verdict |
|---|---|---|
| Ahead or behind envelope? | `milestone_index=3 < expected≈4`, and `lifecycle=BLOCKED` | **AT_RISK** |
| Stalled? | `same_blocker_persists` + `no_new_artifact` = 2 signals ≥ `STALL_MIN_SIGNALS` | **likely stall** |
| What kind of trouble? | `scope_fit=1` (low) **and** `blocker_severity=2` | scope + technical — hand to `diagnose` |
| Success probability? | not computed at Event 1 (Parts XXXI–XXXII) | **UNKNOWN** |

This is an EARLY-warning shape, not a judgement: a team that is *behind its own archetype's envelope,
blocked on the same thing, shipping nothing new, and under-scoped-mismatched* — exactly the kind of
preventable friction the rescue policy exists to catch. The engine hands this vector, unranked and
un-scored, to [rescue-policy.md](rescue-policy.md), which decides the intervention (and may still
decide to do nothing). A team **making progress** — no second stall signal, milestone tracking the
envelope — never reaches that policy at all; it is left to build.

---

See also: [contribution-and-roles.md](contribution-and-roles.md) (role coverage, ownership, the
critical path) · [event-control-and-waste.md](event-control-and-waste.md) (event-wide bottlenecks and
Preventable Blocked Minutes) · [firewalls-and-ethics.md](firewalls-and-ethics.md) (why none of this
becomes a person score).
