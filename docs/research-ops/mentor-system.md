# The Mentor System — Support First, Evidence Second

Mentors are **Layer 6** of the [live research OS](live-research-os.md). Their job is to help elite
builders get unstuck; the research value is a *byproduct* of that help, never its purpose. This doc
covers the mentor taxonomy, the routing engine, the ≤20-second log, and the mentor *experience* —
the briefing, shifts, rest, and separation rules that keep a mentor helpful rather than
bureaucratic. The confounder that arises when a mentor — especially a company engineer — does the
hard part for a team is treated on its own in [mentor-interventions.md](mentor-interventions.md).

> **The ordering is the whole design.** A mentor who logs well but helps poorly is a failure; a
> mentor who helps brilliantly and logs nothing is a minor data gap. The binding constraint is the
> participant experience ([live-research-os.md](live-research-os.md) — "the experience wins"), and a
> mentor is part of that experience. Everything below is tuned so the log never competes with the
> help.

## Why mentors are a sensor at all

At a mentor density of ~0.1 (roughly one elite mentor per ten builders — see
[event1-design.md](../event1-design.md)), mentors touch the event at exactly the moments research
cares about: a blocker, a stated reason for a switch, a repeated friction that is systemic rather
than personal. A help request is a **naturally occurring critical incident**
([critical-incidents.md](critical-incidents.md)) — the builder was going to ask anyway, so capturing
it costs them nothing. This is the same principle the [capture system](../capture-system.md) commits
to: spend explicit participant attention only at the freshest, highest-signal moments, and let
everything else ride on things people did anyway. A mentor note is an **ambient** channel, not an
explicit one — it is excluded from the ≤18-minute explicit research budget on purpose
([`burden_budget.py`](../../engine/burden_budget.py), `MENTOR_LOG_IMPACT ∈ AMBIENT_CHANNELS`).

## The mentor category taxonomy

A mentor carries exactly one `category` (schema [`006_live_research.sql`](../../schema/006_live_research.sql),
`mentor.category`). The names are fixed in [`mentor_routing.py`](../../engine/mentor_routing.py) and
must not drift — the routing map, the queue views, and the war room all key on them.

| Category | Covers | Typical problem categories routed in |
|---|---|---|
| `GENERAL` | triage, "who do I even ask", glue | `general` + fallback for any unrouted request |
| `FRONTEND` | UI frameworks, client state, rendering | `frontend` |
| `BACKEND` | servers, auth, API integration | `auth`, `api_integration` |
| `INFRA` | deploy, CI, containers, networking | `infra`, `deploy` |
| `CLOUD` | cloud provider services, quotas, IAM | `cloud` |
| `DB` | schema, queries, data modeling | `database`, `data_modeling` |
| `AI_ML` | models, training, inference, evals | `model`, `ml` |
| `AGENTS` | agent loops, tool use, orchestration | `agent` |
| `DATA` | pipelines, ETL, analytics | (data-heavy requests; often via `GENERAL`) |
| `ORIE_OPT` | operations research, optimization | `optimization` |
| `ECE` | electrical/computer engineering | (hardware-adjacent) |
| `HARDWARE` | devices, sensors, embedded | `hardware` |
| `ROBOTICS` | actuation, control, robotics stacks | `robotics` |
| `PRODUCT` | scoping, PRD, demo strategy | `product` |
| `DESIGN` | UX, visual design, interaction | `ui` |
| `DOMAIN` | subject-matter experts (a vertical) | `domain` |
| `COMPANY_ENGINEER` | sponsor engineers on their own product | **confounder** — never a neutral mentor |

`COMPANY_ENGINEER` is a category *and* a flag (`mentor.is_company_engineer`). It is listed here
because the routing engine treats it as a mentor pool, but every interaction it produces is a
confounder candidate — see [mentor-interventions.md](mentor-interventions.md). It is never silently
folded into a neutral category, and its help is never reported as organic product success.

## The routing engine (problem → mentor → assign → capture → resolution)

The request lifecycle is operations-first. Research reads the same rows afterward; it never steers
the assignment.

```
  BUILDER IS STUCK
        │  opens a support_request (category = problem category, e.g. "auth")
        ▼
  ROUTE ───────────► ROUTING[problem_category] → mentor category   (mentor_routing.ROUTING)
        │               "auth" → BACKEND ; unknown → GENERAL
        ▼
  ASSIGN ──────────► least-loaded available mentor in that category, else GENERAL
        │               route_request(): chosen = min(pool, key=active_load); load += 1
        ▼
  HELP  ───────────► the actual point of the whole system
        │
        ▼
  CAPTURE ─────────► one ≤20s mentor_interaction row (ambient; no participant tax)
        │
        ▼
  RESOLUTION ──────► resolution_state: RESOLVED | UNRESOLVED | ESCALATED | WITHDRAWN
        │
        └──────────► queue_depths() aggregates OPEN requests per category → war room
```

`route_request(req, mentors)` ([`mentor_routing.py`](../../engine/mentor_routing.py)) looks up the
problem category in `ROUTING`, builds the pool for the routed mentor category (falling back to
`GENERAL` if the pool is empty), picks the **least-loaded** mentor by `active_load`, increments that
load, and stamps `req.assigned_mentor`. It returns `None` only when no mentor fits at all — a
queue-is-empty operations signal, not a research event.

### Queue depth is operations data first

`queue_depths(requests)` counts open requests (`resolution_state ∈ {None, UNRESOLVED, ESCALATED}`)
per routed mentor category. This is a **left-half-of-the-war-room** view
([research-war-room.md](research-war-room.md)) — it runs the event: a spiking `BACKEND` queue means
pull a floater onto auth *now*, or open a group office hour. Only *after* it has served operations
does the same signal become research evidence: a persistent category queue is a candidate for a
systemic-friction memo. The two readings are kept provenance-separate so an operations signal is
never laundered into a client finding ([live-research-os.md](live-research-os.md), "Operations data
vs client research data").

```
OPERATIONS READING   BACKEND queue = 7 open → staff it, cut the wait          (act in minutes)
RESEARCH READING     BACKEND queue persistently deep across teams →           (memo, then confirm
                     candidate systemic-friction pattern, NOT yet a finding     and contradict)
```

Aggregate `queue_depths` — counts across teams — is the research-legitimate read. A single team's
request stream is operations, not a pattern.

## The lightweight mentor log (≤20 seconds)

Every mentor touch can produce one `mentor_interaction` row (schema
[`006_live_research.sql`](../../schema/006_live_research.sql)). The **target is ≤20 seconds to fill**
— the log is designed down to that budget, not up from a wish list. Fields:

| Field | What it is | Capture |
|---|---|---|
| Team | which team (grain is team, not person) | pre-filled from the request |
| Time | `occurred_at` | auto-stamped |
| Category | problem category | tap from the routed list |
| Problem | one short phrase | tap-or-type, ≤ a few words |
| Tool | product/approach in play | tap from recent tools |
| State | what state the team was in | tap (STUCK / EXPLORING / SHIPPING …) |
| Question | what they actually asked | optional free text |
| Intervention | what the mentor did | tap preset + optional text |
| Outcome | where it ended | tap (RESOLVED / STILL_STUCK / ESCALATED) |
| FollowUp | does a researcher need to circle back | one toggle |
| ResearchFlag | "this is worth a researcher's attention" | one toggle |

Most fields are a tap, not typing. `ResearchFlag` is the single most valuable bit: it is the mentor
handing the war room a lead without doing any analysis themselves. A flagged interaction may trigger
an adaptive-sampling decision ([adaptive-sampling.md](adaptive-sampling.md)) — but only if the
[interruption policy](interruption-policy.md) and the [burden budget](participant-burden.md) allow;
the mentor never owes the follow-up.

### What is actually worth asking — the 10/20/30-second format exploration

The log length is a genuine tradeoff: Signal vs MentorEffort vs TimeStolenFromHelping. We explore it
explicitly and keep it tiny. These are **illustrative** time targets, not measured figures:

```
10s  Team · Category · Outcome                         the irreducible minimum; pure ops telemetry
     ── always worth it: this alone drives queue_depths and "who is still stuck"

20s  + Tool · State · Intervention · ResearchFlag       the DEFAULT. One extra tap each.
     ── the flag is the highest-value 2 seconds in the whole system

30s  + Problem phrase · Question · FollowUp             only when the mentor volunteers it,
     ── diminishing returns; never required, never nagged                 or on a flagged incident
```

Design rules for the format:
- **Default to 20s.** Below that you lose the `ResearchFlag`; above it you start stealing help time.
- **Every required field is a tap.** Free text is optional on every field without exception.
- **Skippable is mandatory.** A mentor mid-help can log the 10s version and move on; a half-filled
  row is a valid row, not an error.
- **No person fields, ever.** The log carries behavior-in-context only — no quality, employability,
  or trait field exists to fill (`assert_clean` in [`live_research.py`](../../engine/live_research.py)
  rejects any record that tries to carry one).

## Mentor experience (the part that decides whether any of this works)

A bureaucratic mentor program produces bad help *and* bad data. The experience is engineered so the
logging burden is the smallest thing a mentor thinks about.

- **Briefing.** Short pre-event briefing: you are here to help, the log is a 20-second byproduct, the
  `ResearchFlag` is the one thing we really want, and you never score a person. Mentors are told
  plainly that the participant experience outranks the data.
- **Shifts & rest.** Shifts are bounded (`research_shift`, with `is_overnight`), with real breaks and
  no one on a double overnight. A tired mentor helps badly and logs worse.
- **Routing relief.** `route_request` load-balances by `active_load` so no single mentor is swamped
  while a category queue spikes — the war room watches `queue_depths` and reallocates.
- **Food & logistics.** Treated as `validity_impact = NONE` operations
  ([`006_live_research.sql`](../../schema/006_live_research.sql), `event_intervention`) — fed, warm,
  caffeinated. This is not research data; it is keeping the sensor network functional.
- **Company-mentor separation.** `COMPANY_ENGINEER` mentors are rostered and routed separately, and
  every interaction they log is flagged `is_company_engineer` for the confounder analysis
  ([mentor-interventions.md](mentor-interventions.md)). They help; they are never presented to a
  client as evidence of organic adoption.
- **Conflict policy.** A mentor affiliated with a sponsor does not mentor a team building directly on
  a competitor's product where judgment could be compromised; the `affiliation` field records the
  potential conflict so the war room can see it. Neutral mentors (`is_neutral`) are the default.
- **Reduce logging burden relentlessly.** The log is continuously pruned toward the 20s target. If a
  field is not earning its tap, it is cut. The measure of the program is help quality first and log
  *completeness of the cheap fields* second — never log length.

## Where this connects

- Success labels (`ORGANIC` / `ASSISTED` / `VENDOR_RESCUED`) and the intensity definition live in
  [mentor-interventions.md](mentor-interventions.md).
- The checkpoint slot that compliance is often tied to is in [checkpoints.md](checkpoints.md); the
  mentor slot is one of the things a builder *wants*, which is why it is a good incentive anchor
  ([measurement.md](../measurement.md)).
- Whether a flagged incident may actually interrupt a team is decided by
  [interruption-policy.md](interruption-policy.md), consulted by
  `LiveResearchOS.observe_then_decide` ([`live_research.py`](../../engine/live_research.py)).
- Program status, the unproven thesis, and the WTP gate are upstream in [STATE.md](../STATE.md).
