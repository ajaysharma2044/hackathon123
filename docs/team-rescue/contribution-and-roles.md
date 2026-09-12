# Contribution & Roles

The **team-level** contribution layer of the [adaptive rescue engine](adaptive-rescue-engine.md). Its
job is to make sure every participant *has a place to contribute* and every team *knows what must
finish next* — never to grade who contributed more. The runnable core is
[`../../engine/critical_path.py`](../../engine/critical_path.py) with `role_coverage` / `ownership_gap`
in [`../../engine/team_state.py`](../../engine/team_state.py); the schema is
[`../../schema/008_team_rescue.sql`](../../schema/008_team_rescue.sql).

> **The one hard rule of this doc.** Coverage and ownership are properties of a *team*, captured
> *voluntarily*. There is no individual score here, no "free-rider" label, and no ranking of people
> by contribution. A gap triggers a **prompt to the team**, never a flag on a person
> ([firewalls-and-ethics.md](firewalls-and-ethics.md), Invariant 2). `teams_needing_help`
> ([event-control-and-waste.md](event-control-and-waste.md)) returns *teams*, never ranked builders.

```
  ROLE COVERAGE ──► CONTRIBUTION OWNERSHIP ──► WORKLOAD PULSE ──► CRITICAL PATH ──► WHERE HELP GOES
  (who is covered)   (what each owns)          (team feeling)     (what unblocks)   (bottleneck-first)
        │                    │                       │                  │                  │
        └──────── all feed one question: is anyone stuck with nothing useful to do? ───────┘
```

## Part XI — Participant Role Coverage

Coverage is asked as *capabilities present on the team*, not *who is best*. For a team's declared
need set we compute, via `role_coverage(needed, owned, overloaded)`:

| field | meaning | source |
|---|---|---|
| `NeededCapability` | a capability the project requires | project archetype + team declaration |
| `Covered` | needed ∩ owned — someone can carry it | voluntary self-report |
| `Missing` | needed − owned — **nobody** covers it | drives skill-gap routing (Part X) |
| `Overloaded` | needed ∩ overloaded — one person carries too much | drives the workload pulse (Part LIII) |

```
team 7f · archetype AI_APP        (ILLUSTRATIVE)
  needed:   backend  frontend  ml  data  product
  covered:  backend  frontend  ml         product
  missing:                         data                 → surface a data capability (Part X)
  overloaded: backend                                   → backend is one person for the whole stack
```

Capabilities are ordinal and coverage-only: `covered / missing / overloaded` — never a skill *rating*.
The schema is `role_coverage(team_id, capability, covered, overloaded)` — a per-team boolean matrix
with **no per-person skill column anywhere.** Coverage patterns aggregate across the event into
[capability_shortages](event-control-and-waste.md) so staffing can respond
([../research-ops/mentor-system.md](../research-ops/mentor-system.md)); the pattern is descriptive,
matching the observational discipline of [../event-ops/role-correlations.md](../event-ops/role-correlations.md).

## Part XII — Contribution Opportunity

The objective is **opportunity**, not audit: every participant should own *something* they can point
to. We ask one voluntary, low-burden question — *"what are you primarily owning?"* — and store the
answer in `contribution_ownership(team_id, participant_id, owns)` where `owns` is a coarse workstream
(`backend | model | frontend | data | hardware | ux | research | optimization | demo | other`), never
a quantity or a quality.

`ownership_gap(members, owners)` returns the members with **no declared ownership**. Crucially, what
fires is a **team-level prompt**, not a person flag:

```
if ownership_gap(team) is non-empty:
    → prompt the TEAM: "Does anyone need a clearer workstream? Some folks may not have a
                        piece they own yet — want help splitting the work?"
    ✗ NEVER: "Alice has contributed nothing"      ✗ NEVER: any free-rider score
```

An unowned workstream is treated as a **design problem for the team to solve** (split the work,
scope a piece in), which is usually what an idle participant actually needs — a clearer lane, not a
reprimand. The same signal often means the team over-scoped or mis-split, which routes to the scope
tools in [rescue-policy.md](rescue-policy.md).

## Part LIII — Workload Balance & the Contribution-Imbalance Pulse

Balance is sensed with the same one-tap `team_pulse` used everywhere else (Part II) — a single
`contribution` field the *team* answers, not a manager's assessment:

```
  ┌─────────────── HOW IS THE WORK SPLIT?  (one tap, ~3 sec, team-level) ───────────────┐
  │  ● YES_ALL_HAVE_WORK        everyone has a lane            → no action               │
  │  ● SOMEONE_NEEDS_TASK       a member has nothing to own    → contribution prompt XII │
  │  ● OVERLOADED_ROLE          too much on one role/person     → rebalance / add cover   │
  │  ● NEED_DIFFERENT_SKILL     a capability is missing         → skill-gap routing X     │
  └──────────────────────────────────────────────────────────────────────────────────────┘
```

There is deliberately **no hidden free-rider label** behind `SOMEONE_NEEDS_TASK`: the team is telling
*us* it wants help splitting work, and we answer with help. `OVERLOADED_ROLE` corroborates the
`overloaded` set from Part XI — two independent signals, consistent with the multi-signal stall
discipline (one signal never concludes). The pulse debits the participant burden budget in seconds
([../research-ops/participant-burden.md](../research-ops/participant-burden.md)); it is a *feeling*,
captured cheaply, not a measurement of people.

## Part XIV — The Critical Path

Teams do **not** enter Gantt charts. From a handful of lightweight tasks — a duration estimate, a few
dependencies, an owner *capability* (not a person), a status — [`critical_path.py`](../../engine/critical_path.py)
computes the project's critical path (`team_task` / `task_dependency` in the schema) and answers the
single operationally useful question:

> **`next_to_unblock` — "what must finish next to unblock the most downstream work?"**

```
  design─┐            (ILLUSTRATIVE 72h project DAG, minutes)
         ├─► api(180,BLOCKED)──► integrate(120)──► test(90)──► demo(30)
  schema─┘                    ▲
         data-pipeline(150)───┘
  critical_path  = design → api → integrate → test → demo   (total 600 min ≈ minimum finish time)
  next_to_unblock = api        ← earliest unfinished task ON the path; frees the most future work
  bottleneck_capability = backend (carries the most critical-path minutes → where an expert most moves it)
```

`critical_path` returns the longest-duration path (minimum finish time); `next_to_unblock` returns the
earliest unfinished task on it; `bottleneck_capability` returns the capability sitting on the most
critical-path minutes. These three feed bottleneck-first mentoring directly — we route help to the
task that *frees the most future work*, not the task that is easiest to answer.

## Part XV — Bottleneck-First Mentoring

Easiest-first triage is the wrong policy: it clears cheap questions while a project-killing blocker
sits for hours. Instead we route by a **priority that multiplies severity, structural importance, and
urgency against fit** — ordinal, not a fake cardinal score:

```
  route_priority  ~  blocker_severity           (HIGH … LOW)
                  ×  critical_path_importance    (on next_to_unblock? on the path? off-path?)
                  ×  wait_time                   (how long already blocked)
                  ×  expertise_fit               (does an available mentor match required_skill?)
                  ×  time_remaining_pressure     (less runway → higher weight)
```

A HIGH-severity blocker on `next_to_unblock` with a long wait and a matching mentor available
outranks a dozen easy off-path questions. The rescue ladder ([rescue-policy.md](rescue-policy.md))
decides *when* and *at what intensity*; the mentor router
([../research-ops/mentor-system.md](../research-ops/mentor-system.md)) decides *who*; this layer
supplies the *critical-path importance* term the router alone cannot see. Every dispatch is logged
`state_before → intervention → state_after` for cross-event learning, never as a causal claim.

## Part X — Skill-Gap Routing & the Voluntary Collaboration Board

When Part XI reports a `Missing` capability (or a pulse says `NEED_DIFFERENT_SKILL`), the team opens a
`capability_request(team_id, capability)`. Routing is a search over mentor capability, then a fallback
that is **strictly opt-in**:

```
  capability_request("data")
        │
        ├─ search available mentors for capability "data"
        │     ├─ match  → route a mentor / office-hour slot   (mentor_routed = true)
        │     └─ none   → surface to the VOLUNTARY collaboration board (surfaced_to_board = true)
        │                     other teams / floating specialists can OFFER help
        └─ ✗ NEVER auto-assign a participant to a team against their choice
```

The collaboration board is a **marketplace of offers**, not an assignment engine. We never move a
person without their explicit choice — the anti-coercion rule that also governs merges and switches
below.

## Part XIX — Team Merge

Two half-teams (one strong backend, one strong ML, each missing the other) can be worth more merged —
but a merge is **only ever suggested, and only proceeds if BOTH teams opt in.** The schema encodes the
gate directly: `team_merge_suggestion(team_a, team_b, a_opted_in, b_opted_in, status)` can reach
`MERGED` only when both flags are true.

```
  team_merge_suggestion
    rationale: "A owns a working backend + no model; B owns a strong model + no UI"
    a_opted_in ─┐
    b_opted_in ─┴─► both true → status MERGED       any false → status SUGGESTED / DECLINED (no-op)
```

A merge is a *possibility we surface with a reason*, never an org-chart move imposed on builders.

## Part XX — Participant Switch & the Rematching Pool

When a team dissolves, or a participant finds themselves with no viable role, **their weekend is not
lost.** They enter the `rematching_pool(participant_id, event_id, offers_capabilities)` — a
first-class place to be *seeking a team*, carrying the capabilities they offer. A team with a matching
`capability_request` can invite them; the switch is recorded in `rematched_team`. This closes the loop
that Parts X/XIX open: coverage gaps on one side, available talent on the other, matched **by mutual
opt-in** — never auto-assigned.

## Part XXVIII — No Idle Talent

The individual-level "does everyone have a lane?" question (Part XII) has an **event-level aggregate**:
skilled people sitting idle while other teams starve for exactly that skill is pure waste — it feeds
the [waste map](event-control-and-waste.md) as `IDLE_CAPABILITY`. We surface it as *aggregate,
optional opportunity matching*, never as a callout of a person:

```
  AGGREGATE (event view, ILLUSTRATIVE)          →  OPTIONAL MATCH
  6 idle frontend builders (finished early)     →  3 teams have a NEED_DIFFERENT_SKILL: frontend
  2 unused ORIE mentors                         →  4 optimization teams near a modeling blocker
  1 idle hardware specialist                     →  offer to the 1 hardware team on a bring-up wall
```

Idle-and-finished builders are also prime candidates for the [side quests / FRONTIER
challenges](event-control-and-waste.md) (Part XXVII) — a way to keep strong contributors engaged
without inventing busywork. Matching is always an *offer*.

## Part XIII — The Optional Team Charter

A few minutes at the start, entirely optional, that prevents hours of drift — stored as
`project_definition` plus the ownership rows. It is a **lightweight alignment note, not a pitch or
bureaucracy**:

```
  ┌──────────────────────── TEAM CHARTER (optional, ~5 min) ────────────────────────┐
  │  Project / who it's for      What are we building, for whom?                     │
  │  Roles present               which capabilities do we have?           (Part XI)  │
  │  Core goal — must ship       the one thing that must work         (success_if)   │
  │  Nice-to-have — can cut       droppable if time runs short          (can_cut)    │
  │  Who owns what               each person's primary workstream     (Part XII)     │
  │  How we ask for help          who pings a mentor / opens a capability_request     │
  └──────────────────────────────────────────────────────────────────────────────────┘
```

The charter pre-populates role coverage, ownership, and the *must-ship vs nice-to-have* split that the
scope optimizer ([rescue-policy.md](rescue-policy.md)) later leans on. Skipping it is fine; teams that
fill it in simply start with fewer preventable-confusion minutes ([event-control-and-waste.md](event-control-and-waste.md)).

## Part LIV — Team Conflict Support

Interpersonal conflict is a real failure mode, but it is the **most sensitive** signal the system
touches. The rule is narrow and firm:

- A team can *voluntarily* flag friction; it routes to a **human organizer** for support, at the top
  of the rescue ladder (Part III restructuring rung) — handled by people, not automation.
- This data is **never commercialized, never fed to sponsors, never part of any research dataset, and
  never attached to a participant record.** It sits behind the performance/research firewall
  (Invariant 4) as operational-support-only, and is minimized and discarded per
  [firewalls-and-ethics.md](firewalls-and-ethics.md).

## Part XLIX — Contribution, Ownership & the Firewall

Everything in this doc is captured *for support, not for judgment*, and the boundary is structural,
not a promise:

```
  USED FOR (operational support)                 NEVER USED FOR (forbidden by schema + assert_clean)
  ───────────────────────────────                ──────────────────────────────────────────────────
  routing help to a missing capability           a per-person contribution / productivity score
  prompting a team to split work                 a "free-rider" / "work-ethic" label
  matching idle talent to a need (opt-in)        ranking participants by ownership or output
  keeping every builder with a real lane         any input to sponsor / commercial evaluation
```

Coverage is a team matrix; ownership is a voluntary self-report; imbalance is a team pulse. None of it
collapses to a number about a person. The event-wide rollup of what these signals *cost when they go
unaddressed* — idle capability, duplicated work, preventable blocked minutes — lives next door in
[event-control-and-waste.md](event-control-and-waste.md), and feeds the shadow prices in
[../event-optimizer.md](../event-optimizer.md) and [../quant-engine.md](../quant-engine.md).
