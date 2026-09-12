# Event Control & Waste

The **ORIE layer** of the [adaptive rescue engine](adaptive-rescue-engine.md): treat the running event
as a live optimization problem — find the binding constraint, map the waste, allocate scarce resources
*fairly*, adapt the schedule, and obsess over one metric — **Preventable Blocked Minutes**. The
runnable core is [`../../engine/event_control.py`](../../engine/event_control.py); the schema is
[`../../schema/008_team_rescue.sql`](../../schema/008_team_rescue.sql). It complements the *design-time*
[event optimizer](../event-optimizer.md) (which picks the event's shape before it runs); this module
runs the event **live**.

> **Two disciplines carried through the whole layer.** (1) **Teams, never ranked participants** —
> `teams_needing_help` returns *teams* and nothing here ranks people. (2) **The fairness floor** —
> allocation gives every team a minimum before any surplus is prioritized, and a commercial client can
> **never** buy below-floor priority over basic participant support (Invariant 5).

```
   OBSERVE ──► FIND BINDING CONSTRAINT ──► ALLOCATE (floor first) ──► ADAPT SCHEDULE ──► MEASURE WASTE
   (state_t)   event_bottlenecks           allocate_resources        adaptive_schedule   preventable_blocked_minutes
      ▲                                                                                          │
      └──────────────────── learned across events → shadow prices → next event's design ─────────┘
```

## Part XVI · LXII–LXIII — The Bottleneck Map & Theory of Constraints

At any instant the event has **one binding constraint** — the resource whose demand most exceeds its
capacity. `event_bottlenecks(demand, capacity)` returns the constraints ranked by the `demand − capacity`
gap, worst first, so the war room spends attention where it actually moves throughput. We run Goldratt's
five focusing steps **live**:

```
  1 IDENTIFY    event_bottlenecks → the largest demand−capacity gap right now   (e.g. backend mentors)
  2 EXPLOIT     get more from it: office hours, triage the queue by critical path (Part XV), batch FAQs
  3 SUBORDINATE align everything else to it: don't schedule a workshop that pulls the scarce mentors away
  4 ELEVATE     add capacity: pull a floating specialist, open a clinic, bring a sponsor engineer (XLIV)
  5 REPEAT      the constraint moves (backend → compute → submission crush); re-identify, don't fixate
```

The constraint **moves** over 72 hours — an early architecture-decision bottleneck becomes a mid-event
compute bottleneck becomes a final submission-portal crush. `event_bottleneck` rows are stamped `as_of`
precisely because the binding constraint is a moving target; fixating on yesterday's constraint is
itself a waste.

## Part XVII — Adaptive Mentor & Resource Allocation

Mentors and hard resources flow to where demand spikes, scored by **need and structural leverage — not
commercial value.** The allocation weight multiplies genuine need against critical-path leverage and
available capacity:

```
  allocation_weight  ~  unmet_need              (how far short is this team of the floor / its request)
                     ×  participant_value        (does this help many builders learn/ship?)
                     ×  critical_path_leverage    (is the resource on next_to_unblock / bottleneck_capability?)
                     ×  capacity_available        (can we actually supply it now?)
   ✗ NOT: "which team has the paying sponsor attached"      (see the fairness floor, Part LVII)
```

Scarce resources (`resource_pool`: `MENTOR:<cat> | GPU | COMPUTE | EQUIPMENT | ROOM | DOMAIN_EXPERT |
COMPANY_ENGINEER`) are allocated by need × leverage × capacity, and every allocation is recorded in
`resource_allocation`. Demand is read from live `capability_request` / blocker / pulse signals; the
mentor router ([../research-ops/mentor-system.md](../research-ops/mentor-system.md)) then places the
specific person.

## Parts LVII · LIX — The Fairness Floor

Fairness is not a policy statement — it is the **shape of the allocation algorithm.**
`allocate_resources(capacity, team_requests, floor, commercial_priority)` distributes in **two strict
passes**:

```
  PASS 1  FLOOR   every requesting team gets `floor` units FIRST — before any prioritization at all
  PASS 2  SURPLUS only the remainder is ordered, and commercial_priority MAY order the surplus …
                  … but it can NEVER reach into pass 1. No below-floor override exists.
```

```
  capacity 10 · floor 2 · teams {A,B,C,D} each want 4 · commercial_priority {C}   (ILLUSTRATIVE)
  pass 1 (floor):   A2 B2 C2 D2            → 8 used, every team has its minimum
  pass 2 (surplus): C+2 (=4), then A+... → the paying team gets EXTRA, never A/B/D's floor
```

The schema hard-codes it: `resource_allocation.is_below_floor_override` carries a
`check (is_below_floor_override = false)` — the database itself refuses to record a below-floor buy-out
(Invariant 5). A commercial client can buy *surplus* priority; it can never buy *another team's basic
support*. This is the live-allocation counterpart to the design-time constraint in
[../event-optimizer.md](../event-optimizer.md).

## Parts XLII–XLIII · XLIV — Adaptive Schedule, Clinics & Sponsor Support

The schedule is **not fixed** — it responds to aggregate state. `adaptive_schedule(aggregate)` reads
`blocked_rate`, `ahead_rate`, and `energy` and recommends adjustments:

```
  blocked_rate ≥ 0.30 → reduce optional workshops; run a TARGETED CLINIC on the top blocker
  ahead_rate   ≥ 0.30 → offer ADVANCED side quests / FRONTIER level to teams that are EARLY
  energy       ≤ 2/5  → insert a food / social break; energy has crashed
```

Programming follows **real demand, not a pre-printed agenda.** A clinic is created (`adaptive_clinic`,
stamped with what `triggered_by` it) **only when demand emerges** — the discipline is: *run an auth
clinic only if ~30% of teams actually hit an auth blocker,* not because auth was on the schedule.
Empty scheduled workshops are counted as waste (Part LXI). **Sponsor engineer presence follows the
same rule** (Part XLIV): a `COMPANY_ENGINEER` is surfaced to the floor when live demand for that
stack appears (many teams blocked on that API), not parked for booth optics — demand-driven, and still
subordinate to the fairness floor.

## Parts XXVI–XXVII — Adaptive Challenge Difficulty & Side Quests

Difficulty adapts per team so nobody is bored or crushed. Three levels, plus dynamic side quests for
teams that finish the core early (`side_quest`, `challenge_level`):

```
  BASE      the core challenge — every team should reach a shippable version of this
  ADVANCED  a harder variant for teams moving fast
  FRONTIER  an open, research-flavored stretch for teams well ahead of the envelope (classify()==EARLY)
  + dynamic side quests: spun up live for idle-but-strong teams (No Idle Talent, contribution-and-roles.md XXVIII)
```

Side quests are the constructive answer to *No Idle Talent* — they keep strong contributors engaged
without inventing busywork, and they pair with the [team-state envelope](team-state-model.md) that
labels a team `EARLY`.

## Part LXI — The Waste Map

`waste_map(items)` aggregates every recoverable inefficiency into `{kind: total}`, worst first — the
event's live ledger of destroyed opportunity (`waste_item` in the schema):

```
  ┌──────────────────────── WASTE MAP (ILLUSTRATIVE, mid-event) ────────────────────────┐
  │  BLOCKED_HOURS      210 h   teams stuck on preventable friction   → biggest lever    │
  │  IDLE_CAPABILITY     18 h   skilled builders with nothing to own  → opportunity match │
  │  UNUSED_MENTOR       12 h   mentor capacity nobody was routed to   → rebalance         │
  │  DUPLICATED_WORK      9 h   two teams solving the identical thing  → introduce them    │
  │  EMPTY_WORKSHOP       6 h   scheduled sessions nobody needed       → cut; run clinics   │
  │  UNUSED_COMPUTE     140 GPU-h  provisioned, unclaimed             → reallocate          │
  │  EXCESS_QUEUE         4 h   people waiting past a sane SLA         → add capacity        │
  │  UNUSED_ROOM          2 rooms  bookable, empty                    → repurpose            │
  └──────────────────────────────────────────────────────────────────────────────────────┘
```

Every waste kind maps to an action; the map is what turns "the event feels chaotic" into a ranked
to-do list for the war room.

## Part XXXVII — Preventable Blocked Minutes (the key Event-1 metric)

Everything rolls up to **one number Event 1 should obsess over.**
`preventable_blocked_minutes(logs)` sums blocked time, breaks it down by cause, and **excludes
informative failure** — a genuine algorithm-doesn't-work or hypothesis-rejected result is captured
research, not waste to prevent ([firewalls-and-ethics.md](firewalls-and-ethics.md), Part XXV).

```
  PREVENTABLE_CAUSES = {DOCUMENTATION, TOOL_FAILURE, MENTOR_SHORTAGE, CAPABILITY_GAP,
                        RESOURCE_SHORTAGE, SCOPE_ISSUE, OPERATIONS}
  INFORMATIVE_FAILURE  → EXCLUDED (real research, counted separately, never conflated)

  by_cause (ILLUSTRATIVE)          minutes        the illustration to keep in mind:
    MENTOR_SHORTAGE     3,600      ┐             150 builders × ~90 preventable min each
    DOCUMENTATION       2,700      │  preventable   ≈ 13,500 min ≈ 225 participant-HOURS destroyed.
    TOOL_FAILURE        2,400      ├─ = 13,500 min   Recover even a large share and nearly
    CAPABILITY_GAP      2,100      │  ≈ 225 hrs      everything improves at once (more building →
    SCOPE_ISSUE / OPS   2,700      ┘                 better projects → better artifacts → research).
    INFORMATIVE_FAILURE   900      → excluded (captured as research value)
```

`participant_hours_recoverable = preventable_minutes / 60` is the headline the war room watches fall.
The exclusion of informative failure is not a footnote — conflating a real research failure with waste
would create exactly the wrong incentive (teams hiding the failures that are the most valuable data).

## Part LX — Output Efficiency, Decomposed

We want a sense of *output per resource*, but we **refuse to collapse it into one magic number** — and
output is never "lines of code." `output_efficiency(outputs, inputs)` returns the components and
per-input ratios, kept separate:

```
  outputs (kept as a vector, ILLUSTRATIVE):  milestones_reached · artifacts_shipped · demos_ready · research_signals
  inputs  (kept as a vector):                mentor_hours · gpu_hours · staff_hours · rooms
  per_input_ratio: total_output / each input   ← reported per input, NEVER summed into one score
  note: "components kept separate; no single efficiency score"
```

Output-per-team and output-per-participant are read the same way — **decomposed, within-archetype,
descriptive** (a hardware team and a consumer-app team are not on one scale), consistent with the
milestone-velocity discipline in [team-state-model.md](team-state-model.md). No leaderboard falls out
of this.

## Part LXIV — The Production Function

Conceptually, a team's useful output is a function of many inputs:

```
  Y  =  f( time, capabilities, mentorship, compute, information, team_composition, tools, incentives, environment )
```

We write the function down to make the *levers* explicit — **not** because we know its coefficients.
The functional form, the returns to each input, and the interactions are **UNKNOWN until multi-event
data exists.** We never estimate a marginal product before the data is there; any illustrative figure
is labeled as such, exactly as [../event-optimizer.md](../event-optimizer.md) treats its
assumption-driven numbers.

## Part LXV — Marginal Productivity & Shadow Prices

The operational question is marginal: *what does one more unit of an input buy?*

```
  ∂Y/∂(mentor_hour)   = ?   ┐  ALL UNKNOWN until we log state_before → intervention → state_after
  ∂Y/∂(GPU_hour)      = ?   ├  across many events and LEARN them from data — never hard-coded now.
  ∂Y/∂(doc_fix)       = ?   ┘  (the rescue loop is built precisely to generate this evidence)
```

Once learned, these marginal products become **shadow prices** — the value of relaxing each constraint
by one unit — which feed straight back into the design-time optimizer's allocation and the value
engine ([../event-optimizer.md](../event-optimizer.md), [../quant-engine.md](../quant-engine.md)). The
live layer's logged interventions are the *training data* for those shadow prices; until then the
prices are `None`, not a guess.

## Part LXVI — Maximize Event-Wide Output s.t. the Floor

The objective is **event-wide**, and it is explicitly *not* "optimize the likely winners":

```
  maximize   Σ  useful_output(team)          (the whole cohort, not the top of the leaderboard)
             over all teams
  subject to every team receiving its minimum support FLOOR      (Part LVII fairness)
             no person scoring · no surveillance · burden ≤ budget    (the standing constraints)
```

Pouring all mentors onto the three projected winners would raise a vanity metric and destroy the
event; the floor constraint forbids it. The required event-level accessors that drive this loop:

| function | returns | discipline |
|---|---|---|
| `teams_needing_help(states)` | AT_RISK / stalled **teams** with risk + stall flags | a support queue, never a ranking of worth |
| `capability_shortages(states, role_needs)` | `{capability: count}` across teams needing help | aggregate demand → staffing |
| `event_bottlenecks(demand, capacity)` | binding constraints by `demand − capacity` gap | Theory of Constraints, worst first |

## Part LXVII — The Event Control Dashboard

The war room's single pane — an aggregate operational view, and pointedly **not** a "worst
participants" board:

```
  ┌────────────────────────── EVENT CONTROL · hour 34 / 72 (ILLUSTRATIVE) ──────────────────────────┐
  │  42 teams   27 BUILDING · 5 TESTING · 3 PIVOTING · 4 BLOCKED · 3 SUBMISSION_RISK                 │
  │                                                                                                  │
  │  MENTOR DEMAND     Backend 8   AI 6   ORIE 4   Frontend 2        (demand − capacity, worst first) │
  │  BINDING CONSTRAINT  ▶ backend mentor capacity   (demand 8, capacity 5, gap +3)                   │
  │  PREVENTABLE BLOCKED  ~225 participant-hours to date   top cause: MENTOR_SHORTAGE                 │
  │  WASTE  BLOCKED_HOURS 210 · IDLE_CAPABILITY 18 · UNUSED_COMPUTE 140 GPU-h                          │
  │                                                                                                  │
  │  ACTION  ▶ shift 2 backend mentors from the (empty) 3pm workshop to office hours                  │
  │          ▶ open a targeted clinic on the top blocker · match 6 idle frontend builders to 3 teams │
  │  FAIRNESS  every team at/above floor ✓   surplus-only priority in effect                          │
  └──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Every panel is teams and resources; the recommended action is always *shift capacity to the
constraint* — never *name and shame a builder*. This dashboard is the live sibling of the design-time
picture in [../event-optimizer.md](../event-optimizer.md), and the per-team detail behind it lives in
[contribution-and-roles.md](contribution-and-roles.md) and [team-state-model.md](team-state-model.md).
