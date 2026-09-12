# The Live Research Operating System

The complete, event-embedded research system for **Event 1** — a Cornell-only premium hackathon.
This is the master document; the rest of [`docs/research-ops/`](.) expands each layer, and the
runnable kernel is in [`engine/`](../../engine/) with the schema in
[`schema/006_live_research.sql`](../../schema/006_live_research.sql).

It sits **downstream of the decision to run Event 1**. Everything about whether to run it, at what
price, and for which buyer is governed by [STATE.md](../STATE.md) (the thesis is unproven; WTP is the
gating unknown) and [event1-design.md](../event1-design.md) (the recommended shape). This document
assumes that gate has been passed and answers a narrower question: **given that Event 1 runs, how do
we extract an exceptionally rich, traceable, adaptive understanding of how elite builders decide,
struggle, switch, build, and continue — without ever making it feel like a study?**

## The one hard constraint

> **If the research and the participant experience ever conflict, the experience wins.** A weekend
> the builders call one of the best events they ever attended is worth more than any single
> weekend's data, because the data asset compounds only if the event keeps happening
> ([monetization-map.md](../monetization-map.md), extraction frontier).

Everything below is built to make that constraint and "extremely rich research" compatible rather
than opposed. The mechanism is the same one the capture system already commits to
([capture-system.md](../capture-system.md)): **capture through things people were going to do anyway,
and spend their explicit attention only at the freshest, highest-signal moments.**

## What we are trying to reconstruct

For every team, by the end of the 90-day window:

```
WHAT DID THEY WANT?  →  WHAT DID THEY CONSIDER?  →  WHAT DID THEY EXPECT?  →  WHAT DID THEY CHOOSE?
  →  WHY?  →  WHAT HAPPENED?  →  WHERE DID THEY FAIL?  →  WHO HELPED?  →  WHAT CHANGED THEIR MIND?
  →  WHAT DID THEY SWITCH TO?  →  WHY?  →  WHAT DID THEY BUILD?  →  WHAT DID THEY LEARN?
  →  WHAT CONTINUED AFTER THE EVENT?  →  WHY?
```

And, simultaneously, for the research operation itself:

```
WHAT PATTERNS ARE EMERGING?  →  WHAT DON'T WE UNDERSTAND?  →  WHO SHOULD WE TALK TO NEXT?
  →  WHAT EVIDENCE WOULD DISPROVE OUR INTERPRETATION?  →  WHAT QUESTION SHOULD WE ASK NEXT?
  →  SHOULD THE EVENT ITSELF ADAPT?
```

The first chain is the **team story** ([team-trajectories.md](team-trajectories.md)). The second is
the **live loop** — the thing that makes this more than a hackathon-plus-a-survey.

## The live loop (the core mechanism)

```
  NATURAL EVENT ACTIVITY
        │  (building, choosing, asking for help, failing, switching, shipping)
        ▼
  IMPORTANT MOMENT ───────────────► a critical incident is detected   (critical-incidents.md)
        │                              by telemetry / mentor / observer / checkpoint / artifact
        ▼
  LOW-FRICTION CAPTURE ───────────► mentor note, artifact, ambient signal — no participant tax
        │
        ▼
  TARGETED QUESTION IF NEEDED ────► one good micro-prompt at the fresh moment, IF burden + timing
        │                              allow; most incidents ask nothing   (micro-prompts.md)
        ▼
  STRUCTURED EVIDENCE ────────────► observation / excerpt / telemetry row, fact ≠ interpretation
        │
        ▼
  LIVE SYNTHESIS ─────────────────► war room: themes emerge, memos written   (research-war-room.md)
        │                              a new question is added to the backlog (analytic-memos.md)
        ▼
  DELIBERATE CONFIRM *AND* CONTRADICT ► adaptive sampling seeks the negative case, not just more of
        │                                the same  (adaptive-sampling.md, negative-case-analysis.md)
        ▼
  BETTER NEXT QUESTION ───────────► the backlog re-prioritizes; the next ask is sharper
        │                              (question_backlog.py)
        └──────────────────────────────── loops back into the event, live
```

The loop is implemented as `LiveResearchOS.observe_then_decide(...)` in
[`engine/live_research.py`](../../engine/live_research.py): an incident comes in, and the system
decides the next action (fire a prompt / leave it to the mentor note / flag a deeper interview /
stay silent) **under the burden budget and the interruption policy**. Staying silent is a
first-class, correct outcome.

## The 17 layers

| # | Layer | What it does | Where |
|---|---|---|---|
| 1 | **Participant baseline** | pre-event SAID state, stack, familiarity (the adoption-vs-retention covariate) | [capture-system.md](../capture-system.md) Phase A/B; [checkpoints.md](checkpoints.md) |
| 2 | **Team baseline** | problem, plan, intended tools, prior-collaboration graph at t0 | [checkpoints.md](checkpoints.md) (START) |
| 3 | **Passive legitimate capture** | brokered keys, event-app actions, artifacts — disclosed, invisible-but-not-covert | [capture-system.md](../capture-system.md) Part 3 |
| 4 | **Behavioral-event triggers** | the critical-incident taxonomy that notices "something interesting happened" | [critical-incidents.md](critical-incidents.md); [`research_triggers.py`](../../engine/research_triggers.py) |
| 5 | **Field-researcher observation** | trained humans, zone coverage, fact ≠ interpretation | [field-researcher-guide.md](field-researcher-guide.md), [field-note-system.md](field-note-system.md) |
| 6 | **Mentor observation** | help-first support that reveals blockers as a byproduct | [mentor-system.md](mentor-system.md) |
| 7 | **Structured checkpoints** | START / MIDPOINT / END, minimal, incentive-tied | [checkpoints.md](checkpoints.md) |
| 8 | **Targeted interviewing** | deeper, sampled or trigger-flagged conversations | [adaptive-questioning.md](adaptive-questioning.md) |
| 9 | **Adaptive sampling** | who to interview next, given the evidence gaps | [adaptive-sampling.md](adaptive-sampling.md); [`adaptive_sampling.py`](../../engine/adaptive_sampling.py) |
| 10 | **Emerging-theme detection** | the war room turns raw notes into provisional patterns | [research-war-room.md](research-war-room.md), [qualitative-coding.md](qualitative-coding.md) |
| 11 | **Live research war room** | the operations room/dashboard that runs the loop | [research-war-room.md](research-war-room.md), [dashboard-spec.md](dashboard-spec.md) |
| 12 | **Intervention logging** | every material event change, timestamped, with validity impact | [event-adaptation.md](event-adaptation.md); [`intervention_log.py`](../../engine/intervention_log.py) |
| 13 | **Artifact analysis** | the honest cross-check on all self-report (repos, deps, deploys) | [capture-system.md](../capture-system.md); [measurement.md](../measurement.md) |
| 14 | **End-of-event synthesis** | the team stories + the claim/evidence graph | [team-trajectories.md](team-trajectories.md), [evidence-graph.md](evidence-graph.md) |
| 15 | **7/30/90-day follow-up** | the retention asset no other hackathon has | [longitudinal-followup.md](longitudinal-followup.md) |
| 16 | **Client-specific analysis** | the same instrument serving research / R&D / product / activation clients | [client-protocols.md](client-protocols.md) |
| 17 | **Evidence provenance** | every client-facing claim traces to evidence, including against it | [evidence-graph.md](evidence-graph.md); [`evidence_graph.py`](../../engine/evidence_graph.py) |

## The human sensor network

The distinctive asset is not any one instrument — it is that **field researchers + mentors + the
adaptive question engine act as a coordinated human sensor network** over the event. Instead of
ending Sunday with ~120 survey responses, Event 1 should end (and then compound over 90 days) with
something closer to:

```
  participant baselines  +  team decision histories  +  hundreds of critical incidents
  +  mentor support histories  +  switching explanations  +  failure explanations
  +  technical artifacts  +  structured interviews  +  emerging themes  +  negative cases
  +  7/30/90-day follow-up
```

> **Those are categories, not targets.** The right *intensity* of capture — how many observers, how
> many interviews, how many prompts — is set by the event size and the participant-burden budget
> ([participant-burden.md](participant-burden.md)), not by a quota. More interviews is not better;
> [saturation](negative-case-analysis.md) and burden decide when to stop.

## What this system deliberately is NOT

Encoded structurally, not just promised ([`live_research.py`](../../engine/live_research.py)
`assert_clean`, the `ClientView` gate, and [consent-design.md](consent-design.md)):

- **Not a survey company.** The default response to an incident is *no question*. Explicit research
  is budgeted to ≤~18 minutes per participant across the whole weekend.
- **Not a surveillance system.** No keystroke logging, no continuous screen capture, no private-
  message scraping, no covert audio, no attention monitoring. Permanently out of scope — see the
  no-go list below and [capture-risk-register.md](../capture-risk-register.md).
- **Not a participant-scoring system.** There is no quality / employability / founder / personality
  score and no protected-trait inference anywhere in the schema or the engines. `assert_clean`
  rejects any record that tries to carry one.
- **Not a source of raw individual data for clients.** Clients get aggregate, min-cell-suppressed
  findings and promoted claims; the only individual-grain disclosure is the participant's own
  opted-in work evidence, which never passes through the client research view.

### The no-go list (default-prohibited, permanently)

```
keystroke logging · continuous screen recording · private-message capture · secret audio
personality/intelligence inference · employability/quality/founder scoring · protected-trait inference
covert monitoring · individual sponsor dossiers on participants
```

Nothing on this list is built unless an independent ethical + legal review explicitly clears a
specific, disclosed, consented use — and nothing in Event 1 requires any of it.

## Operations data vs client research data

Two streams, kept separate (Part XXXIII), though one action can feed both:

```
OPERATIONS DATA            mentor queue depth · food · room capacity · team count · check-in · Wi-Fi
(runs the event)           · support demand by category        → the war room's left half
CLIENT RESEARCH DATA       choice · behavior · artifact · interview · outcome · retention
(the deliverable)          → the evidence graph → aggregate findings, per client, confidential
```

Operations data is how we keep the event excellent in real time ([event-adaptation.md](event-adaptation.md));
research data is the product. Provenance is maintained so a signal used for both is never laundered
from one into the other.

## Minimum viable vs ideal

Event 1 does not need all of this built in software. See
[event1-live-playbook.md](event1-live-playbook.md) for the full build-vs-manual split and the
60-question synthesis; in brief:

```
MINIMUM VIABLE RESEARCH OS (Event 1)
  consent gate (exists: engine/capture.py) · brokered keys for the primary product
  · a paper/Airtable field-note form enforcing fact ≠ interpretation · a 20-second mentor log
  · the trigger→micro-prompt routing run by a human in the war room · a burden tally per participant
  · START/MID/END checkpoints · stratified exit interviews · 7/30-day follow-up
  Most of the "engine" can be a disciplined human process + a spreadsheet for Event 1.

IDEAL RESEARCH OS (by Event 3–4)
  telemetry-fired micro-prompts in-app · a live war-room dashboard (dashboard-spec.md)
  · the adaptive sampler suggesting the next interview · the evidence graph as software
  · AI-assisted first-pass coding with human gates (qualitative-coding.md)
```

The engines in this repo are the **reference implementation of the invariants** — the burden cap,
the fact/interpretation split, the promotion gate, the timestamped interventions — so that when the
software is built, it is built against executable, tested correctness properties rather than prose.

## The test this whole system has to pass

> Can we hand one paying client an aggregate, honestly-caveated, potentially-negative finding —
> traceable to evidence and to the evidence *against* it, respecting every participant's consent at
> query time — produced from a weekend the builders would still call one of the best they attended?

If yes, the live research OS works. Every layer below is built so the answer can be yes — and so the
system can tell us honestly when it is not.
