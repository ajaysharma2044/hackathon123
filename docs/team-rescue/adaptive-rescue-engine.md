# Adaptive Team Performance + Rescue Engine

A new section of the quant system whose objective is not "score which student is lazy" — that would
create exactly the wrong incentives — but:

> **Maximize useful contribution opportunity from every participant and every team**, while
> detecting, as early as possible, the failure modes that waste that opportunity, and **adapting the
> environment around the team** in response.

This is the master document for [`docs/team-rescue/`](.); the runnable core is
[`engine/team_state.py`](../../engine/team_state.py),
[`engine/rescue_engine.py`](../../engine/rescue_engine.py),
[`engine/critical_path.py`](../../engine/critical_path.py), and
[`engine/event_control.py`](../../engine/event_control.py), with the schema in
[`schema/008_team_rescue.sql`](../../schema/008_team_rescue.sql). It sits alongside the design-time
[event optimizer](../event-optimizer.md) (which chooses the event's shape *before* it runs) as the
**live** optimizer that runs *during* the event.

## What it reduces

```
dead teams · low-effort teams · no technical depth · one person doing everything · people with no
meaningful role · unclear ownership · bad team composition · impossible scope · trivial scope · teams
stuck for hours · mentor starvation · motivation collapse · weak demos from preventable failure ·
duplicated effort · idle talent · unused domain expertise
```

## What it must NEVER be (encoded, not just promised)

The anti-objectives are structural, enforced by [`schema/008`](../../schema/008_team_rescue.sql) and
the `assert_clean` guard shared with the research layer
([`live_research.py`](../../engine/live_research.py)) — the same no-go boundaries as the rest of the
system ([../research-ops/live-research-os.md](../research-ops/live-research-os.md)):

```
NO hidden individual productivity score          NO ranking people by "quality" / "intelligence" /
NO "work ethic" / "employability" / "founder"        "founder potential"
NO keystrokes · NO continuous screen monitoring · NO private-message surveillance · NO camera monitoring
```

The system **optimizes the ENVIRONMENT and TEAM SUPPORT** — it never secretly grades individuals.
There is deliberately no `team_score` column and no individual-score column anywhere in the schema;
`TeamState` exposes a **vector**, not a number, and contribution is captured as **voluntary
ownership**, not graded output. Details: [firewalls-and-ethics.md](firewalls-and-ethics.md).

## The feedback loop

The whole engine is one loop, run live and logged for learning:

```
   State_t  ──►  detect bottleneck / at-risk  ──►  Intervention_t  ──►  State_{t+1}  ──►  Outcome
      ▲                                                                                     │
      └─────────────────────────  logged: state_before → intervention → state_after ────────┘
                                   (across events we learn P(State_{t+1} | State_t, Intervention))
```

Eventually the log teaches things like *"a team with an integration blocker and < 6 hours left
usually benefits more from reducing scope than from adding another mentor"* — but we **learn that
from data, never hard-code a fake probability now** (Parts XXXI–XXXV, XXXIV–XXXV). `simulate_intervention`
returns scenarios with `calibrated_probability = None` until the data exists.

## The five parts, and where they live

| Part of the engine | What it does | Doc / module |
|---|---|---|
| **Team as a dynamic system** | the decomposed state vector, the archetype envelope, stall detection, milestones | [team-state-model.md](team-state-model.md) · [`team_state.py`](../../engine/team_state.py) |
| **Rescue policy** | the No-Dead-Team ladder, diagnosis, scope optimizer, quick-wins, pivot/submission/demo support | [rescue-policy.md](rescue-policy.md) · [`rescue_engine.py`](../../engine/rescue_engine.py) |
| **Contribution & roles** | role coverage, ownership, workload balance, critical path, skill routing, rematch/merge/switch | [contribution-and-roles.md](contribution-and-roles.md) · [`critical_path.py`](../../engine/critical_path.py) |
| **Event-wide control** | bottleneck map, waste map, fair resource allocation, adaptive schedule/workshops | [event-control-and-waste.md](event-control-and-waste.md) · [`event_control.py`](../../engine/event_control.py) |
| **Firewalls & ethics** | no person scores, the performance/research firewall, incentives, counterfactual discipline | [firewalls-and-ethics.md](firewalls-and-ethics.md) |

## The Event-1 metric: Preventable Blocked Minutes

Everything above rolls up to one simple number Event 1 should obsess over:

> **Preventable Blocked Minutes** — time a team lost to *preventable* confusion, missing expertise,
> waiting, bad scope, or operational friction. If 150 builders each lose ~90 minutes to preventable
> friction, that is **~225 participant-hours destroyed.** Recovering even a large share of it increases
> nearly everything at once.

```
more building → better projects → more fun → better artifacts → better research
             → better sponsor outcomes → more commercial value
```

`preventable_blocked_minutes` ([`event_control.py`](../../engine/event_control.py)) tracks it and
breaks it down by cause (documentation, tool failure, mentor shortage, capability gap, resource
shortage, scope issue, operations) — and it **excludes** informative failure, because a genuine
algorithm-doesn't-work result is valuable research to *capture*, not waste to *prevent*
([firewalls-and-ethics.md](firewalls-and-ethics.md), Part XXV).

## The multiplier

A single well-placed intervention moves many objectives at once — the reason this belongs in the
quant system as a genuine multiplier ([../value-engine-flowcharts.md](../value-engine-flowcharts.md),
[../commercial-engines.md](../commercial-engines.md)):

```
one mentor intervention  →  reduces blocked time
                         →  raises completion probability
                         →  improves participant experience
                         →  produces product-friction evidence (feeds the research layer)
                         →  generates mentor-demand data (improves next-event staffing_model.py)
```

## How it ties into the rest of the system

- **Detection** is fed by the same sensors as the research layer — mentor logs, checkpoints,
  observers, artifacts, event-app telemetry ([../research-ops/critical-incidents.md](../research-ops/critical-incidents.md)) —
  but consumed for a **different purpose** (support, not research), behind a firewall
  ([firewalls-and-ethics.md](firewalls-and-ethics.md), Part XLVI).
- **Mentor dispatch** uses the operations routing already built
  ([../research-ops/mentor-system.md](../research-ops/mentor-system.md),
  [`mentor_routing.py`](../../engine/mentor_routing.py)) — the rescue ladder decides *when* and *at
  what intensity*; the router decides *who*.
- **Adaptive research burden** (Part XLV): a struggling team gets *fewer* research prompts (the
  burden budget already supports this — [../research-ops/participant-burden.md](../research-ops/participant-burden.md));
  an idle/waiting team may be a good moment for a short contextual interview.
- **The event adapts** — mentor allocation, schedule, workshops, side quests — logged with validity
  impact just like any other change ([../research-ops/event-adaptation.md](../research-ops/event-adaptation.md)).

## The final standard

> The system should make it **hard for a team to quietly fail because of a preventable problem** — a
> participant should not sit for four hours with no task, no mentor, no role, and no idea what to do
> without the system offering help — **and yet it must never feel like a manager monitoring
> employees.** The ideal participant thinks: *"I always knew what I was working on, I could get help
> when I needed it, the event kept moving, my team actually shipped something, and somehow everything
> felt organized."* The backend is doing far more work than the participant realizes.

```
RIGHT TEAM + RIGHT PROBLEM + RIGHT SCOPE + RIGHT ROLE COVERAGE + RIGHT RESOURCE + RIGHT INTERVENTION
+ RIGHT TIME  →  MAXIMUM USEFUL OUTPUT  →  STRONG EXPERIENCE  →  BETTER ARTIFACTS  →  BETTER RESEARCH
             →  BETTER SPONSOR VALUE  →  MORE COMMERCIAL VALUE
```
