# Temporal synthesis — the master queries answered

The temporal layer turns the static event DB into a time-aware dynamic system. This page answers the
master queries (Parts LXXV–LXXXI) and states what is honestly still unknown. It reuses — does not
replace — `capture.py` (tri-temporal spine), `burden_budget.py` (the participant floor), `voi.py`
(VOI math), and `compliance.py` (no person scores, no sensitive attributes).

Net-new files: [`temporal_core`](../../engine/temporal_core.py), [`context_envelope`](../../engine/context_envelope.py),
[`episode`](../../engine/episode.py), [`temporal_graph`](../../engine/temporal_graph.py),
[`state_space`](../../engine/state_space.py), [`survival`](../../engine/survival.py),
[`freshness`](../../engine/freshness.py), [`temporal_voi`](../../engine/temporal_voi.py),
[`optimal_stopping`](../../engine/optimal_stopping.py), [`dynamic_allocation`](../../engine/dynamic_allocation.py),
[`process_tracing`](../../engine/process_tracing.py), [`trajectory`](../../engine/trajectory.py),
[`test_temporal.py`](../../engine/test_temporal.py) (34 checks), [`schema/012_temporal.sql`](../../schema/012_temporal.sql).

## The master queries

| Query (spec part) | How to run it | Returns |
|---|---|---|
| **trace_episode(entity, start, end)** (LXXV) | `episode.reconstruct_episode` | prior state, context, opportunity set, events, decisions, interventions, artifacts, outcomes, explanations — point-in-time |
| **events_before(rel, minutes)** (LXXVI) | `temporal_graph.window_before` | the context window before every occurrence of an event (proximity ≠ cause) |
| **trajectory(entity)** (LXXVII) | `temporal_graph.trajectory` / `trajectory.py` | the entity's whole ordered evolution + archetype |
| **counterfactual_options(intervention)** (LXXVIII) | `process_tracing.counterfactual_options` | the counterfactual **or** `NOT_IDENTIFIED` — never invented |
| **client query: "why did builders abandon Product X?"** (LXXIX) | `temporal_graph.find_motifs` + `motif_outcomes` + `survival` | sequence patterns, durations, contexts, choice sets, negative cases, 7/30/90 outcomes |
| **professional evidence (opt-in)** (LXXX) | `trajectory` learning template + `capture.individual_disclosure` | an artifact-supported trajectory, not a person score |
| **venture (team opt-in): "projects active at 90 days"** (LXXXI) | `trajectory` venture template + `delayed_outcome` | project trajectory 0/7/30/90d |

## The client query, worked (LXXIX)

*"Why did builders abandon Product X?"* is answered as a **process**, not a number:

1. `find_motifs` over the sequences of teams that touched X → recurring patterns
   (e.g. `DocsFailure → Switch` vs `DocsFailure → MentorRequest → VendorRescue → Retention`).
2. `motif_outcomes` attaches outcomes **and negative cases** to each pattern.
3. `survival.kaplan_meier` on time-to-switch → how fast abandonment happens.
4. `temporal_graph.window_before("SWITCHED_TO", 30)` → what happened in the 30 min before each switch.
5. `context_at` at each switch → the choice set and context then.
6. `delayed_outcome` → 7/30/90-day retention.

Delivered with the discipline: **descriptive co-occurrence, negative cases shown, order is not
causation, counterfactual only if identified.**

## What time changes (not "just timestamps")

- **Interpretation** — an achievement is read *with* its `opportunity_at(t)`; context is `C_i(t)`.
- **Prediction** — every `prediction_snapshot` records its `information_cutoff`; `information_set`
  enforces no future leakage; backtests use strict temporal splits (LVI–LVIII).
- **Causal reasoning** — process tracing + identified-only counterfactuals; time orders the DAG so the
  past cannot be caused by the future (LI).
- **Allocation** — minute ledgers, interruption cost, critical path, phase reallocation.
- **Pricing** — VOI(E,t), decision deadlines, the temporal product ladder.
- **Evidence validity** — freshness/decay by claim type; old evidence aged, not deleted.
- **Professional / venture evidence** — trajectories, opt-in, never an IQ/potential score.

## What is honestly still UNKNOWN

Per the repo's `Evidence ≠ Claim ≠ Hypothesis ≠ Decision` discipline:

- **Transition probabilities, hazard curves, intervention effects, stopping thresholds** — all
  `INSUFFICIENT_DATA` / `INPUTS_UNKNOWN` until Event 1 (and repeated events) supply data. The engines
  are the *structure that collects what is needed to learn them*, not pretend-precise models. No
  premature HMM/POMDP/Hawkes.
- **WTP for every rung of the temporal product ladder** — UNKNOWN until buyers are asked.
- **Flow-recovery time, decay half-lives without grounding** — returned as UNKNOWN, never assumed.

## Guardrails (Part LXXXIV) — all enforced in `test_temporal.py`, 34/34 passing

no future leakage · sequence ordering · duration correctness (the 44-min / 14-min worked example) ·
point-in-time reconstruction (a day-30 outcome is invisible at submission) · freshness (stale vs fresh;
no ungrounded exponential) · delayed outcomes + follow-up horizon (post-deadline decision value = 0) ·
intervention timing (latency measured, differs by timing) · state reconstruction (dense→probabilities,
sparse→INSUFFICIENT_DATA) · missing context tolerated (UNKNOWN, None — never fabricated) · no
unsupported counterfactual (single case → NOT_IDENTIFIED) · no hidden socioeconomic/person-quality
score (opportunity/context/ trajectory can never become one).

## The standard (LXXXV)

> Time turns snapshots into trajectories. Context turns events into explanations. Together they turn
> hackathon telemetry into process-level decision intelligence.

The moat becomes less *"we know 2,000 data points about a participant"* and more *"we can reconstruct
high-value technical work, product decisions, interventions, failures, recoveries, and outcomes as
contextualized trajectories over time."*
