# Adaptive Sampling — Who To Interview Next

**Part XII of the [Live Research Operating System](live-research-os.md).** Layer 9 of the 17.

We do not pre-select every interview. Who we talk to *next* is driven by the live evidence: which
open question has the biggest gap, which segment is uncovered, and — critically — which active
explanation has **not** yet been tested against a disconfirming case. The runnable kernel is the
`Sampler` class in [`adaptive_sampling.py`](../../engine/adaptive_sampling.py); the stored form is
`interview.sampling_reason` / `sampling_segment` in
[`006_live_research.sql`](../../schema/006_live_research.sql).

This doc covers the *selection* of the next interview. The *content* of that interview is
[adaptive-questioning.md](adaptive-questioning.md); the *disconfirmation logic* it leans on is
[negative-case-analysis.md](negative-case-analysis.md); the *questions* it samples toward come from
the backlog in [analytic-memos.md](analytic-memos.md).

> The golden-goose constraint governs here hardest: **the sampler never farms one person.** It
> optimizes for evidence coverage, not extraction. More interviews is not better
> ([live-research-os.md](live-research-os.md), "those are categories, not targets").

## The sampling segments

The exact list from `SEGMENTS` in [`adaptive_sampling.py`](../../engine/adaptive_sampling.py). A
candidate belongs to a `frozenset` of these; each explanation implies a confirming **and** a
disconfirming segment.

```
ADOPTER            NON_ADOPTER            CHOOSER             NON_CHOOSER
SWITCHER           NON_SWITCHER           ABANDONER
SUCCESSFUL_TEAM    FAILED_TEAM            HIGH_MENTOR_SUPPORT LOW_MENTOR_SUPPORT
UNEXPECTED_USE_CASE COMMON_USE_CASE       OUTLIER
RD_WINNER          RD_FAILURE             RD_CONVERGENT       RD_DIVERGENT
```

The segments come in confirm/disconfirm pairs. `DISCONFIRMING` maps each confirming segment to the
one that could *falsify* an explanation built on it:

```
ADOPTER            → NON_ADOPTER          SWITCHER           → NON_SWITCHER
ABANDONER          → SUCCESSFUL_TEAM      SUCCESSFUL_TEAM    → FAILED_TEAM
HIGH_MENTOR_SUPPORT→ LOW_MENTOR_SUPPORT   UNEXPECTED_USE_CASE→ COMMON_USE_CASE
RD_WINNER          → RD_FAILURE           CHOOSER            → NON_CHOOSER
```

These segments describe *work-in-context*, never the person. `HIGH_MENTOR_SUPPORT` is a confounder
stratum (did the mentor cause the outcome?), not a competence label — there is no person score here
([STATE.md](../STATE.md) no-go list; schema Invariant 5).

## The algorithm — `Sampler.suggest_next`

Inputs the sampler weighs (the live research state):

| Input | Source | Role |
|---|---|---|
| **ResearchQuestion** | [analytic-memos.md](analytic-memos.md) backlog | what we are trying to answer |
| **EvidenceGap** | `Explanation.confirming_n` vs `target_each` | how under-tested an explanation is |
| **Coverage** | `coverage_gaps` list | segments with no data yet |
| **Contradiction** | `Explanation.disconfirming_n` | negative-case deficit (the priority) |
| **Novelty** | `OUTLIER` / `UNEXPECTED_USE_CASE` membership | a surprising case worth chasing |
| **ParticipantBurden** | `burden.is_over_half(pid)` | skip the half-spent |
| **Availability** | `Candidate.available` + `interrupt_ok(pid)` | is now an OK moment |

`suggest_next(explanations, candidates, coverage_gaps)` returns **a single** `SamplePlan`
(participant, segment, explicit `reason`, `polarity ∈ {CONFIRM, DISCONFIRM, COVERAGE}`), or `None`
if nothing is appropriate right now. The priority order, straight from the engine:

```
1. NEGATIVE CASES FIRST   any live explanation short of its disconfirming quota
                          (disconfirming_n < target_each) pulls a DISCONFIRMING candidate —
                          so an explanation never hardens on confirming evidence alone.
2. CONFIRMING DEFICIT     then fill confirming evidence for under-tested explanations
                          (confirming_n < target_each).
3. COVERAGE GAPS          then close a segment with no data yet.
   else                   → None. Staying idle is a correct, first-class outcome.
```

Step 1 is the anti-confirmation-bias guarantee, wired into sampling itself: before the system adds
*more* of the evidence an explanation already has, it spends its next interview trying to *break*
the explanation. This is the same discipline the evidence graph enforces at promotion time
([negative-case-analysis.md](negative-case-analysis.md),
[`evidence_graph.py`](../../engine/evidence_graph.py) `can_promote`) — here it shapes which interview
happens *next*, not just which claim ships.

## Burden-awareness — never farm one person

`_eligible(candidate)` gates every pick. A candidate is eligible only if **all** hold:

```python
c.available            and    # interrupt window allows a short interview
not c.interviewed      and    # not already done (don't return to the same well)
self.interrupt_ok(pid) and    # not in a DO_NOT_INTERRUPT window (team_interrupt_window)
not self.burden.is_over_half(pid)   # under half the research-minutes budget
```

So the sampler **skips** anyone over budget or in a `DO_NOT_INTERRUPT` state, and the `not
c.interviewed` guard stops it from repeatedly mining the most articulate, most available builder —
the failure mode where a research team accidentally builds its whole dataset from five extroverts.
`_pick` walks candidates for the first eligible member of the target segment; burden and availability
always beat convenience. The reason is always explicit (`SamplePlan.reason`) and is written to
`interview.sampling_reason`, so every conversation can answer "why this person, now?"

## Saturation — know when to stop (Part XXXVII)

The sampler's terminal state is `None`, and that is the point: **do not maximize interview count.**
Stopping is governed by three saturation conditions, not a quota:

```
THEME / MEANING SATURATION   new interviews in a segment stop yielding new codes or new
                             meaning — the explanation's mechanism is understood, not just repeated.
SEGMENT COVERAGE             every segment a live explanation implies has been sampled
                             (coverage_gaps is empty for the active questions).
NEGATIVE-CASE COVERAGE       every live explanation has met its disconfirming quota
                             (disconfirming_n ≥ target_each) — we looked for the counterexample
                             and recorded whether it exists.
```

When a question's backlog row reaches `SATURATED` ([analytic-memos.md](analytic-memos.md),
[`question_backlog.py`](../../engine/question_backlog.py)), it drops out of `ACTIVE` and stops
consuming sampling priority — unless a later contradiction reopens it (`CONTRADICTED`). Saturation is
**provisional**: a fresh disconfirming case can un-saturate a question and pull the sampler back.

```
          more data, same meaning          a surprise contradicts the answer
OPEN ──► ANSWERED_PARTIALLY ──► SATURATED ───────────────────► CONTRADICTED ──► PRIORITIZED
              │  (stops pulling samples when SATURATED)                 (reopens sampling)
```

## What this layer is not

- **Not a recruitment quota.** There is no "interview N people" target; the intensity of sampling is
  set by evidence gaps and the burden budget ([participant-burden.md](participant-burden.md)), not a
  number ([measurement.md](../measurement.md)).
- **Not representative-sample statistics.** n≈150–200, self-selected, Hawthorne-affected — this is
  *directional behavioral signal*, sampled for mechanism and disconfirmation, not a population
  estimate ([STATE.md](../STATE.md) internal-validity caveats). Sold as depth, not breadth.
- **Not a person-ranking.** Segments are work-in-context strata; the sampler holds no model of who is
  "good," only of where the evidence is thin and where it might be wrong.
