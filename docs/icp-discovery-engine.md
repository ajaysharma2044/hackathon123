# The ICP Discovery Engine

The Ideal-Customer-Profile layer, implemented in [`engine/icp_discovery.py`](../engine/icp_discovery.py)
(Phases 19-20) and backed by the `icp_candidate`, `icp_problem`, and `problem` tables in
[`schema/008_environment_economy.sql`](../schema/008_environment_economy.sql). This document describes
what the code does; it does not invent behavior.

## The governing inversion: ICP is an OUTPUT, never an input

The module docstring states it plainly: **"The ICP is an OUTPUT, never an input."** The engine
clusters high-opportunity problems and synthesizes candidate ICPs *from the problem universe*. It
**deliberately does NOT start from "our customer is a devtools company"** — the docstring names that
exact hypothesis and demotes it: it "is one hypothesis in a much larger space, and it must earn its
place from the problem universe like any other."

Two disciplines, quoted from the module:

- Every buyer dimension (pain, urgency, budget, decision value, WTP) is a `beliefs.Belief`, default
  **UNKNOWN**. `update_beta` moves them only on reliability-weighted evidence — "a signed check moves
  them far; a comparable barely." No dimension is fabricated into a number.
- Candidates are ranked by **EVIDENCE STRENGTH first, not by imagined opportunity size** — a cluster
  built only from HYPOTHETICAL worked examples can never outrank one with real demand-side evidence.

`Evidence != Claim != Hypothesis != Decision` is the whole point of the layer: a synthesized candidate
is a hypothesis assembled from evidence, and nothing in `icp_candidate` is a committed **DECISION**
(the schema comment says so directly).

## The evidence ladder

`EVIDENCE_ORDER` (`icp_discovery.py:EVIDENCE_ORDER`) is the demand-side strength ordering, weakest to
strongest — matching the `demand_evidence_kind` enum in schema 004:

```
HYPOTHETICAL          invented for a worked example; NOT market evidence
INFERRED_JOB_POST     a mandate inferred from a job posting
PUBLIC_STATEMENT      earnings call / annual report / exec interview
REGULATORY_FILING     10-K / procurement notice / filing
PROGRAM_ANNOUNCEMENT  a named innovation / R&D / accelerator program
BUYER_STATED          a buyer said it to us directly (cheap-talk discount)
SIGNED_COMMERCIAL     a signed pilot / contract for this exact thing
```

`HYPOTHETICAL` at the bottom is quarantined by its own tag: it exists so worked examples can live in
the same structure as real evidence without being mistaken for it. `SIGNED_COMMERCIAL` at the top is
the only kind that flips WTP out of UNKNOWN (below).

## `ICPDimensions`: five belief dimensions, all UNKNOWN by default

`ICPDimensions` (`icp_discovery.py:ICPDimensions`) is the latent buyer state — five dimensions, each a
`beliefs.Belief`:

| Dimension | Meaning |
|---|---|
| `pain` | how acute the problem is for the buyer |
| `urgency` | how time-pressured |
| `budget` | whether budget exists |
| `decision_value` | the value of the decision the evidence would inform |
| `wtp` | willingness-to-pay — **stays UNKNOWN until a signed check (caveat #1)** |

`__post_init__` seeds any unset dimension with `beliefs.unknown(...)`, so **all five default UNKNOWN**.
This mirrors schema 003's `buyer_state`, where every dimension is a belief id. `unresolved()` returns
the dimensions still UNKNOWN — the honest to-do list for a candidate, in the same idiom as
`beliefs.BeliefLedger.unresolved()` and `economy.ShadowPrices.unresolved()`.

`ICPCandidate` (`icp_discovery.py:ICPCandidate`) is the synthesized profile: the descriptive fields a
human/analyst fills (`company_characteristics`, `exact_problem`, `exact_buyer`, `trigger`,
`budget_source`, `existing_alternative`, `why_alternative_fails`, `why_our_environment_wins`,
`required_talent`, `required_environment`, `frequency`, `business_model`, `risks`), plus
`evidence_strength` (defaulting `"HYPOTHETICAL"`) and a `dims: ICPDimensions`. Its
`is_hypothetical_only` property is `True` exactly when `evidence_strength == "HYPOTHETICAL"`. These map
onto the `icp_candidate` table columns.

## `cluster_problems`: cluster by mechanics/mode, not industry

`cluster_problems(problems, by="mode")` (`icp_discovery.py:cluster_problems`) groups problems into
candidate clusters. `by` may be `"mode"`, `"industry"`, or `"buyer"` (keyed on `p.mode`, `p.industry`,
`p.budget_owner` respectively). **The default is `"mode"`**, and the docstring states the reason:
clustering by mechanics/mode rather than industry is the Phase 7 discipline; industry is *offered but
secondary.* Two problems that share a problem-solving *mode* (e.g. `DIVERGENCE`, `RED_TEAMING`,
`OPTIMIZATION` — the `problem_mode` enum in schema 004) belong together even across industries,
because mode is the variable that drives environment shape. The function returns a plain
`{key: [problems]}` dict.

## `synthesize`: evidence strength is the strongest evidence in the cluster

`synthesize(label, problems, evidence_lookup=None, **fields)` (`icp_discovery.py:synthesize`) builds an
`ICPCandidate` from a cluster. The descriptive `**fields` are human/analytic judgements passed
straight through; **the quantitative `dims` stay UNKNOWN** until evidenced (it constructs a default
`ICPDimensions`).

The candidate's `evidence_strength` is computed by `_cluster_evidence_strength(problems,
evidence_lookup)` (`icp_discovery.py:_cluster_evidence_strength`), which takes the **strongest**
evidence across the cluster via `max(..., key=EVIDENCE_ORDER.index)`. Per problem:

- if `evidence_lookup` supplies a kind for `p.statement`, that kind is used;
- else if the problem `is_hypothetical`, it contributes `"HYPOTHETICAL"`;
- else it contributes `"INFERRED_JOB_POST"`.

The docstring is careful about that last branch: with no external evidence, a cluster of real
(non-hypothetical) problems reaches **only `INFERRED_JOB_POST` at best** — "the engine will not upgrade
evidence it cannot see." And an all-hypothetical cluster (every contribution `HYPOTHETICAL`, or an
empty cluster) **stays HYPOTHETICAL**. A worked example can never inflate itself into market evidence.

## `record_wtp_evidence`: reliability-weighted, and only a signed pilot flips WTP to OBSERVED

`record_wtp_evidence(icp, observations)` (`icp_discovery.py:record_wtp_evidence`) moves the WTP belief
using `beliefs.update_beta` — the only automatic Bayesian update in the engine, a justified
Beta-Binomial conjugate for rates. Each observation is a `beliefs.RateObservation` (e.g. "1 of 8
buyers signed a pilot" as a close-rate). Evidence is **reliability-weighted** by
`beliefs.EVIDENCE_WEIGHT`, so a `SIGNED_COMMERCIAL` observation (weight 1.00) moves the posterior far
more than an `EXTERNAL_COMPARABLE` (weight 0.25). The result is written back to `icp.dims.wtp`.

Critically, `update_beta` only sets status **OBSERVED** when at least one observation is
`SIGNED_COMMERCIAL` or `DIRECT_OBSERVATION`; otherwise the posterior is **ASSUMED**. So a **signed
check is the only thing that flips WTP out of UNKNOWN into OBSERVED** — comparables and buyer talk can
sharpen the belief but cannot promote it to observed truth. This is the WTP caveat (#1) enforced in
code, not just documented.

## `rank`: evidence-first, then size

`rank(candidates)` (`icp_discovery.py:rank`) sorts candidates best-first by a two-key tuple:
`(EVIDENCE_ORDER.index(evidence_strength), len(problems))`, reversed. **Evidence strength dominates;
cluster size only breaks ties within the same strength.** The docstring: "A well-sourced small cluster
beats a large imagined one." A cluster of twenty HYPOTHETICAL problems ranks below a single problem
backed by a `SIGNED_COMMERCIAL` — imagined opportunity size can never outrank real demand-side
evidence.

## Why the inversion matters

Read together, the four functions enforce one stance: the customer profile is *discovered*, not
*assumed*. `cluster_problems` starts from problems (by mechanics), `synthesize` tags each cluster with
the honest strongest-evidence it actually has, `record_wtp_evidence` refuses to call WTP observed
without a signed check, and `rank` orders the whole field by evidence before size. "Our customer is a
devtools company" enters this pipeline as one hypothesis among many — a cluster like any other — and
must earn its rank from real demand-side evidence rather than from how attractive it sounds.
