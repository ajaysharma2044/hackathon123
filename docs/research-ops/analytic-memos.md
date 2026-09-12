# Analytic Memos — Live Synthesis Cadence

**Part XIV (with the Part XI backlog) of the [Live Research Operating System](live-research-os.md).**

An analytic memo is the unit of *thinking* in the war room: a short, structured record of an emerging
pattern, the evidence for it, **the evidence against it**, and what to chase next. It is written
every few hours during the event, not at the end. The stored form is the `analytic_memo` table in
[`006_live_research.sql`](../../schema/006_live_research.sql); the live question queue it feeds is
`research_question_backlog`, whose logic is [`question_backlog.py`](../../engine/question_backlog.py).

> **A memo is evolving research state, NOT a finding.** Its `status` starts `EVOLVING`. A finding is
> a different object, reached only through the evidence-graph promotion gate
> ([negative-case-analysis.md](negative-case-analysis.md),
> [`evidence_graph.py`](../../engine/evidence_graph.py)). Confusing the two is how a vivid mid-event
> hunch becomes a client claim it never earned.

Memos are where the [war room](research-war-room.md) turns raw notes — observations, excerpts,
mentor logs, telemetry — into provisional patterns, and where the *next* question is born. They sit
between emerging-theme detection (Layer 10) and adaptive sampling (Layer 9): a memo names a pattern,
flags who to interview, and re-prioritizes the backlog.

## The analytic-memo template

Every field maps to a column in `analytic_memo`. The template is the discipline; two fields are
**required by structure** and will reject a memo that omits them.

```
┌─ ANALYTIC MEMO ────────────────────────────────────────────────────────────────┐
│ memo_id            unique id                                                     │
│ written_at         timestamp (memos are time-stamped thinking, re-readable)      │
│ author_id          which researcher (LEAD_RESEARCHER owns cluster synthesis)     │
│ question_id        the research_question this memo advances                      │
│ emerging_pattern   the provisional pattern, in one or two lines                  │
│ supporting_evidence    pointers + counts — never a bare assertion  [REQUIRED]    │
│ contradictory_evidence the evidence AGAINST it                      [REQUIRED]    │
│ possible_explanation   the leading reading (hedged)                              │
│ alternative_explanations  competing readings that also fit                       │
│ what_we_still_need     the gap — what would move this from hunch to claim        │
│ who_to_interview       segment(s) to sample next (feeds the sampler)             │
│ next_question          the sharper question this memo surfaces                   │
│ confidence         LOW | MED | HIGH  (labeled, honest — never an adjective)      │
│ status             EVOLVING | STABLE | RETIRED                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

**`contradictory_evidence` is a required field — a memo without it is rejected.** This is the same
anti-confirmation-bias spine as the claim gate, applied one layer earlier: you cannot write down a
pattern without writing down what argues against it. `supporting_evidence` must be *pointers and
counts* (observation ids, excerpt ids, "4 of 7 switchers"), never "clearly, teams hate auth." The
`alternative_explanations` field forces a competing reading to exist before the leading one hardens.

A memo's `who_to_interview` and `next_question` are not decoration — they are the hand-off. The
former becomes a sampler input ([adaptive-sampling.md](adaptive-sampling.md)); the latter may become
a new backlog row.

## Synthesis cadence — every few hours, tied to the war-room rhythm

Synthesis is continuous, not terminal. The rhythm follows the war room's operating beat
([research-war-room.md](research-war-room.md)):

```
  ~every 2–4 hours        LEAD_RESEARCHERs write/update memos for their cluster of zones
                          (new observations since last pass → pattern check → memo)
  shift boundaries        hand-off memo: what's live, what's saturating, what's contradicted
  overnight               lighter cadence; memos flag what the morning shift should chase
  checkpoint beats        START / MIDPOINT / END data lands → memos reconcile against it
```

Why "every few hours" and not daily: the event is 72 hours. A pattern noticed at hour 10 can still
*change the sampling* for hours 11–72 — that is the entire point of a **live** loop
([live-research-os.md](live-research-os.md), the core mechanism). A memo written too late can only
describe; a memo written live can redirect. The memo cadence is what converts observation into the
"better next question" step of the loop.

Memos **evolve in place**: the same `memo_id` is revised as evidence arrives (`status` moves
`EVOLVING → STABLE` when the pattern holds across a disconfirming search, or `→ RETIRED` when it
dissolves). A stable memo is a *candidate* for claim construction in the evidence graph — still not a
finding until promotion.

## The live question backlog — lifecycle

Research questions are not fixed at t0. New ones **emerge** from the evidence ("why do experienced
users ignore the starter templates?") and old ones saturate or get contradicted. The backlog
(`research_question_backlog`, one live row per `research_question`) is a disciplined priority queue.
The `backlog_status` enum and the legal transitions are enforced in
[`question_backlog.py`](../../engine/question_backlog.py):

```
OPEN ──► PRIORITIZED ──► ANSWERED_PARTIALLY ──► SATURATED
   │           │                 │                  │
   └──────► DEPRIORITIZED ◄───────┘                  │  (stops consuming sampling priority)
                                                      ▼
  any state ─────────────────────────────────► CONTRADICTED ──► PRIORITIZED / ANSWERED_PARTIALLY
                    (new evidence undercuts a prior answer; reopens attention, priority bumped)
```

| Status | Meaning | In `ACTIVE` (pulls samples)? |
|---|---|---|
| `OPEN` | logged, not yet prioritized | yes |
| `PRIORITIZED` | the war room is chasing it now | yes |
| `ANSWERED_PARTIALLY` | some evidence, not yet saturated | yes |
| `SATURATED` | theme/segment/negative-case saturation reached | **no** — stops pulling samples |
| `DEPRIORITIZED` | parked (low value or out of scope) | no |
| `CONTRADICTED` | a prior answer was undercut — reopened | yes (priority bumped ≥2) |

Two rules the engine enforces: saturation is **reopenable only via `CONTRADICTED`** (it is
provisional, not permanent — `contradict()` is legal from any state and bumps priority); and
`top(n)` returns only `ACTIVE` questions, highest priority first, so the war room always sees the
sharpest open questions and never wastes sampling on a settled one.

## How emergent questions are created and prioritized

```
observation / excerpt / memo
        │  a memo's next_question names something the backlog doesn't cover
        ▼
Backlog.add_emergent(question_id, text, now, priority=1, ...)
        │  status=PRIORITIZED, is_emergent=True, emerged_at=now
        ▼
sampler pulls toward it (sample_needed / who_to_interview)  →  evidence arrives
        │
        ▼
memo updates → ANSWERED_PARTIALLY → SATURATED     or     CONTRADICTED (reopens, priority ≥2)
```

Emergent questions are **first-class and carry their emergence time** (`emerged_at`,
`is_emergent=True`), so the final report can show *which questions the event itself surfaced* — a
distinctive asset of a live loop over a fixed survey. `Backlog.emergent()` lists them in emergence
order. Each backlog row also carries `client` and `engine` (research / rd / product_dev /
activation), so a question stays attached to the buyer who cares — kept in a separate, aggregate-only
graph, never laundered across clients ([live-research-os.md](live-research-os.md), operations vs
client research data).

Prioritization is evidence-driven, not calendar-driven: a contradiction bumps priority (high-signal,
reopens a supposedly-answered question); a saturated question drops out. The sampler reads the
backlog's `top(n)`; the memos feed the backlog; the backlog steers the sampler. That triangle —
**memo → backlog → sampler → evidence → memo** — is the live loop turning.

## What this layer is not

- **Not a findings document.** Memos are `EVOLVING` research state; findings come only through the
  promotion gate ([negative-case-analysis.md](negative-case-analysis.md)).
- **Not a quota tracker.** The backlog prioritizes by evidence value and contradiction, never by "how
  many interviews done" ([adaptive-sampling.md](adaptive-sampling.md) saturation,
  [measurement.md](../measurement.md)).
- **Not permanent truth.** Saturation is provisional; any memo or question can be reopened by a
  single well-placed disconfirming case. The system is built to change its mind
  ([STATE.md](../STATE.md)).
