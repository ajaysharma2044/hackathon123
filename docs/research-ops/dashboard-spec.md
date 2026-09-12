# Dashboard Spec — Entities, Views, and Who Sees What

**Part XL of the [Live Research Operating System](live-research-os.md)**, with the client-visibility
boundary as **Part XXXVI**. This specifies the views that render the war room
([research-war-room.md](research-war-room.md)) and the strict rule for which audience sees each one.

The dashboard is the ideal-state software for what Event 1 can run as a disciplined human process on
a spreadsheet ([live-research-os.md](live-research-os.md), "Minimum viable vs ideal"). Specifying it
now means that when it is built, it is built against the same invariants the engines already encode
— aggregation, consent-at-query-time, fact ≠ interpretation, no person scores.

> Three audiences, and the gate between them is not a setting — it is enforced in code.
> [`live_research.py`](../../engine/live_research.py) `ClientView` refuses any raw observation,
> unreviewed quote, or researcher note to a client, and `ClientView.aggregate` min-cell-suppresses
> every count. A view's audience below is a contract, not a preference.

```
  OPS TEAM            runs the event: queues, rooms, demand. Operations data.
  RESEARCH TEAM       builds the deliverable: triggers, themes, memos, evidence.
  CLIENT (carefully)  aggregate, min-cell-suppressed, reviewed-only. Part XXXVI.
```

## The views

Each view names what it shows, which tables/engines back it, its audience, and its refresh + grain.
All figures in examples are **illustrative**.

### Event Overview
- **Shows:** active team count, teams by state, phase clock, aggregate module/challenge progress,
  headline mentor demand. The one screen that orients everyone.
- **Backed by:** `team`, `team_interrupt_window`, `support_request`; phase from `EVENT_PHASES`
  ([`live_research.py`](../../engine/live_research.py)).
- **Audience:** OPS + RESEARCH full; CLIENT sees a **reduced** card (active team count, aggregate
  challenge progress only).
- **Refresh / grain:** live; grain = event + team-count.

### Teams
- **Shows:** per-team state, current blocker, last-observed / last-prompted / last-interviewed, open
  trigger count. The "neither ignored nor over-interrupted" view.
- **Backed by:** `research_assignment` (`last_observed_at`, `last_prompted_at`,
  `open_trigger_count`), `team_interrupt_window`, `team_trajectory`.
- **Audience:** OPS + RESEARCH only. **Never CLIENT** — this is team-grain operational detail.
- **Refresh / grain:** live; grain = team.

### Triggers
- **Shows:** the routed trigger queue — trigger_type, detector, action, commercial_value, burden,
  fired/answered/skipped state. The war room's heartbeat.
- **Backed by:** [`research_triggers.py`](../../engine/research_triggers.py) (`TriggerRegistry.route`,
  `high_value_asks`), `critical_incident`, `incident_type_registry`.
- **Audience:** RESEARCH only.
- **Refresh / grain:** live; grain = incident.

### Research Queue
- **Shows:** the next research actions the loop has decided — FIRE_PROMPT / FLAG_FOR_INTERVIEW /
  SEEK_NEGATIVE_CASE / SILENT — under burden + interrupt policy.
- **Backed by:** `LiveResearchOS.observe_then_decide` + `Action`
  ([`live_research.py`](../../engine/live_research.py)), `prompt`, `participant_burden`.
- **Audience:** RESEARCH only.
- **Refresh / grain:** live; grain = action/participant (research side).

### Mentor Queue
- **Shows:** open `support_request` depth by routed category, avg/longest wait, mentor load,
  support-intensity mix.
- **Backed by:** [`mentor_routing.py`](../../engine/mentor_routing.py) (`queue_depths`,
  `route_request`, `support_intensity`), `support_request`, `mentor_interaction`.
- **Audience:** OPS full; RESEARCH sees it as a signal source; CLIENT sees **aggregate help
  categories only** (never who asked).
- **Refresh / grain:** live; grain = category (client) / request (ops).

### Emerging Themes
- **Shows:** provisional themes with mention/team counts, per-product split, confidence label,
  EVOLVING/STABLE status. The AUTHENTICATION-style panels.
- **Backed by:** `analytic_memo`, `code`, `coding_assignment`, `theme` (001), qualitative-coding
  pipeline ([qualitative-coding.md](qualitative-coding.md)).
- **Audience:** RESEARCH only (themes are hypotheses, not findings).
- **Refresh / grain:** on synthesis cadence (~3–4h); grain = theme.

### Question Backlog
- **Shows:** live research questions with priority, status (`OPEN | PRIORITIZED |
  ANSWERED_PARTIALLY | SATURATED | DEPRIORITIZED | CONTRADICTED`), evidence/sample needed, emergent
  flag.
- **Backed by:** `research_question_backlog`, `research_question` (001).
- **Audience:** RESEARCH only.
- **Refresh / grain:** on synthesis cadence; grain = question.

### Interview Queue
- **Shows:** who to interview next and why — segment, sampling reason, coverage gap, interrupt
  eligibility.
- **Backed by:** [`adaptive_sampling.py`](../../engine/adaptive_sampling.py), `interview`,
  `research_assignment`, `team_interrupt_window`.
- **Audience:** RESEARCH only.
- **Refresh / grain:** live; grain = subject/segment.

### Participant Burden
- **Shows:** per-participant spent minutes vs the ≤~18-min cap, by channel; prompt-rate headroom;
  who is near the cap (so they are left alone).
- **Backed by:** `participant_burden` ledger + `burden_budget.py`
  ([participant-burden.md](participant-burden.md)).
- **Audience:** RESEARCH + `DATA_STEWARD`. **Never CLIENT.** Used to *protect* participants, never
  to score them.
- **Refresh / grain:** live; grain = participant (internal only).

### Intervention Log
- **Shows:** every event change — time, reason, evidence, affected population, change, validity
  impact, affected questions, split points.
- **Backed by:** [`intervention_log.py`](../../engine/intervention_log.py) (`InterventionLog`,
  `split_point`), `event_intervention` ([event-adaptation.md](event-adaptation.md)).
- **Audience:** OPS + RESEARCH. CLIENT never sees it live and never directs it.
- **Refresh / grain:** append-only; grain = intervention.

### R&D Approaches
- **Shows:** approach distribution and failed-approach counts per challenge (e.g. `approaches A:4
  B:3 C:1 D:2`, `failed A1 A2 C1`); convergence/divergence signals.
- **Backed by:** `decision_episode` (kind=`RD_REASONING`), `critical_incident`
  (`RD_HYPOTHESIS_FAILURE`, `RD_CONVERGENCE`, `RD_DIVERGENCE`).
- **Audience:** RESEARCH; CLIENT only as **aggregate, min-cell-suppressed** approach counts for an
  R&D engagement ([client-protocols.md](client-protocols.md)).
- **Refresh / grain:** on synthesis cadence; grain = approach/challenge.

### Product Switching
- **Shows:** the switching matrix (`X→Y:4  Y→X:1`), activation→meaningful-use→in-artifact funnel,
  per-product, aggregate.
- **Backed by:** `EvidenceEvent` (`TOOL_SWITCHED`), `ProductUsageEvent`, `decision_episode`
  (kind=`PRODUCT_JOURNEY`); triangulated, never asserted from one source.
- **Audience:** RESEARCH full; CLIENT sees aggregate, min-cell-suppressed funnel/matrix for *their
  own* product, never competitor-attributed individual data.
- **Refresh / grain:** near-live (telemetry) + checkpoint reconciliation; grain = product/aggregate.

### Follow-Up Queue
- **Shows:** scheduled 7/30/90-day waves, consent-eligible subjects, `CONTINUATION_DECISION`
  outcomes, response state.
- **Backed by:** `checkpoint` (`FOLLOWUP_7/30/90`), `follow_up` (001), consent re-resolved at query
  time.
- **Audience:** RESEARCH + `DATA_STEWARD`.
- **Refresh / grain:** per wave; grain = subject (consent-gated).

## Audience matrix

| View | OPS | RESEARCH | CLIENT |
|---|:--:|:--:|:--:|
| Event Overview | full | full | reduced card |
| Teams | full | full | — |
| Triggers | — | full | — |
| Research Queue | — | full | — |
| Mentor Queue | full | signal | aggregate categories |
| Emerging Themes | — | full | — |
| Question Backlog | — | full | — |
| Interview Queue | — | full | — |
| Participant Burden | — | full | — |
| Intervention Log | full | full | — |
| R&D Approaches | — | full | aggregate only |
| Product Switching | — | full | own-product aggregate |
| Follow-Up Queue | — | full | — |

## Client visibility (Part XXXVI)

What a paying client may see *live* is deliberately narrow, and the boundary is enforced by
`ClientView`, not by a dashboard toggle.

```
 CLIENTS MAY SEE LIVE                         CLIENTS MUST NEVER SEE
 ┌────────────────────────────────┐          ┌────────────────────────────────────┐
 │ aggregate module progress       │          │ individual participant surveillance  │
 │ aggregate help categories       │   ──╳──  │ (any per-person timeline or score)   │
 │ active team count               │          │ private researcher notes             │
 │ aggregate challenge progress     │          │ raw, unreviewed quotes               │
 │ artifact previews (opted-in)     │          │ any interference in the research      │
 │ scheduled, disclosed observation │          │ (directing prompts, sampling, adapts)│
 └────────────────────────────────┘          └────────────────────────────────────┘
   all min-cell-suppressed (ClientView)         refuse_raw() raises PermissionError
```

The rules, each tied to its enforcement point:

- **Aggregate only, min-cell-suppressed.** Every client number flows through
  `ClientView.aggregate`; a cell below `min_cell` renders as `—`, never as a small, re-identifiable
  count ([`live_research.py`](../../engine/live_research.py)).
- **No raw, no unreviewed, no notes.** `ClientView.refuse_raw` raises `PermissionError` on any
  observation, unreviewed quote, or researcher note. A quote reaches a client only after the
  human-review gate and only as promoted, provenance-backed evidence
  ([evidence-graph.md](evidence-graph.md)).
- **No individual surveillance.** There is no per-participant view for a client, ever. The only
  individual-grain disclosure anywhere is a participant's *own* opted-in work evidence, and that
  path does not pass through the client research view ([capture-system.md](../capture-system.md)).
- **No interference.** Clients observe on a scheduled, disclosed basis; they do not direct prompts,
  pick interview subjects, or trigger adaptations. Adaptation is a research/ops decision
  ([event-adaptation.md](event-adaptation.md), [client-protocols.md](client-protocols.md)).
- **Operations stays separate from research.** A client sees research deliverables, not the ops
  room; the two streams are kept apart even though one signal can feed both
  ([live-research-os.md](live-research-os.md)).

The dashboard's job is to make the right thing easy and the wrong thing impossible: the ops team
keeps the event excellent, the research team builds an honest deliverable, and the client sees an
aggregate, caveated view that can never become surveillance — because the gate that stops it is the
same code that renders it.
