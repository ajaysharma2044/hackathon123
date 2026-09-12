# Business-Model Discovery

The monetization-model layer, implemented in [`engine/business_model.py`](../engine/business_model.py)
(Phase 21) and backed by the `business_model_option` table in
[`schema/004_environment_economy.sql`](../schema/004_environment_economy.sql). This document describes
what the code contains; it invents no behavior and asserts no buyer will pay.

The framing discipline is stated in the module docstring: **sponsorship is ONE row here, not the
frame.** Each model is scored on decomposed ordinal dimensions that are never collapsed to a single
number, and the module returns a Pareto set. This mirrors the "keep the vector" discipline of
`icp_profile` / `sponsor_economics`.

`Evidence != Claim != Hypothesis != Decision` governs the whole module. The ordinal profiles are
labeled **ASSUMED** ratings (the code says so at `business_model.py:BUSINESS_MODELS`); a high score is
a hypothesis about a model's shape, never a claim that revenue exists.

## The pricing rule this module makes executable

The single most important pricing rule in the repo lives here, in the docstring and in
`rational_price_ceiling`:

```
rational WTP ceiling  =  ValueOfDecision  x  P(evidence changes the decision)      (a CEILING)
observed WTP          =  UNKNOWN until a signed check                              (the truth)
```

**These are not the same quantity and the code refuses to conflate them.** The ceiling is the most a
rational buyer *could* pay; observed WTP is what a buyer *did* pay, and it stays UNKNOWN until a signed
check exists. A high ceiling means a buyer COULD rationally pay a lot — it is never evidence they WILL.

`rational_price_ceiling(decision_value, p_change)` (`business_model.py:rational_price_ceiling`):

- Returns **`None`** if `decision_value` is `None` or its status is `UNKNOWN`. It refuses to invent a
  price, exactly as `beliefs.py` refuses to sample an UNKNOWN belief.
- Returns `None` if `decision_value.mean()` is `None` (an unpriced distribution).
- Otherwise returns `float(ev * clamp(p_change, 0, 1))` where `ev = decision_value.mean()` — the
  expected decision value times the (clamped) probability that evidence flips the decision.

The docstring instructs the caller directly: this is a CEILING, not observed WTP, and **the caller
must keep observed WTP UNKNOWN until a signed check**. The function will not hand back a number when
the decision value itself is unevidenced.

## The decomposed dimensions

`BusinessModel` (`business_model.py:BusinessModel`) is a dataclass scored on nine ordinal dimensions,
listed in `DIMS`. Every dimension is oriented so **higher = better**, keeping Pareto dominance
monotonic across the whole vector. Three dimensions are stored in a deliberately inverted-and-renamed
form so the "higher is better" invariant holds:

| Dimension (`DIMS`) | 3 = HIGH means | Note |
|---|---|---|
| `revenue_potential` | more revenue | |
| `gross_margin` | fatter margin | |
| `repeatability` | more repeatable | |
| `sales_cycle_short` | **short** sales cycle | inverted: 3 = short (good) |
| `scalability` | more scalable | |
| `conflict_low` | **low** conflict-of-interest risk | inverted: 3 = low conflict (good) |
| `participant_alignment` | participants well-served, not extracted from | |
| `defensibility` | harder to copy | |
| `capital_light` | **low** capital intensity | inverted: 3 = capital-light (good) |

Ordinal levels are `NONE=0, LOW=1, MED=2, HIGH=3` (`business_model.py`). `BusinessModel.vector()`
returns the labeled dict; `BusinessModel.raw()` returns the integers used for dominance. In schema
004, the inverted dimensions appear under their un-inverted names — `sales_cycle` (0=long/bad),
`conflict_risk` (0=high/bad), `capital_intensity` (0=high/bad) — with the same 0..3 check constraints.

Judgements stay **decomposed**: there is no single score. Sponsorship is one row among twelve, and a
model that is strong on revenue can be weak on defensibility without either fact being averaged away.

## The registry: all twelve models

`BUSINESS_MODELS` (`business_model.py:BUSINESS_MODELS`) holds twelve models. The table below is their
`vector()` output (H=HIGH, M=MED, L=LOW). Columns are abbreviated from `DIMS`: Rev=revenue_potential,
GM=gross_margin, Rep=repeatability, SCS=sales_cycle_short, Scal=scalability, CL=conflict_low,
PA=participant_alignment, Def=defensibility, Cap=capital_light.

| Code | Rev | GM | Rep | SCS | Scal | CL | PA | Def | Cap |
|---|---|---|---|---|---|---|---|---|---|
| SPONSORSHIP | L | M | M | M | L | H | M | L | L |
| RESEARCH_ENGAGEMENT | H | M | M | L | L | H | M | M | M |
| PER_PROBLEM_MANDATE | H | M | M | L | M | H | H | M | M |
| RND_CONTRACT | H | M | M | L | L | M | H | M | M |
| ANNUAL_RETAINER | H | H | H | L | M | H | M | H | M |
| RESEARCH_WALLET | H | M | H | L | M | H | H | M | M |
| PE_PORTFOLIO_CONTRACT | H | H | H | M | M | M | M | H | M |
| LONGITUDINAL_PANEL_SUBSCRIPTION | M | H | H | M | H | H | M | H | M |
| PROTOTYPE_PROCUREMENT | M | M | M | M | M | M | H | M | M |
| TALENT_RECRUITING_ADDON | M | H | H | M | M | M | M | M | H |
| METHODOLOGY_LICENSING | M | H | H | M | H | H | M | L | H |
| VENTURE_CREATION_ECONOMICS | H | H | L | L | L | L | L | M | L |

The `note` on each row carries its cited grounding and its caveat. Notable ones, quoted in brief from
the code:

- **SPONSORSHIP** — "Capped ~$30-50K/sponsor (Cal Hacks $50K/3000). Trivially copyable; the frame the
  reset rejects." It is the low-revenue, low-defensibility row, present precisely so it stops being
  *the frame*.
- **RESEARCH_ENGAGEMENT** — "$25-250K comparables ... WTP-for-THIS cohort still UNKNOWN (caveat #1)."
  The comparables are evidence; the WTP is not.
- **PER_PROBLEM_MANDATE** — "the reset's native shape": a company brings an expensive problem and we
  design the environment. Highest `participant_alignment`.
- **RND_CONTRACT** — federal hackathon-delivery comparables $28K-$2.5M.
- **ANNUAL_RETAINER** — "Recurring is the margin prize, but requires proven repeatable value first."
- **RESEARCH_WALLET** — Stanford HAI mechanic ($400-800K wallet); "needs institutional standing."
- **PE_PORTFOLIO_CONTRACT** — one buyer, many portfolio-company problems, repeated; "a non-obvious
  ICP (Phase 20)."
- **LONGITUDINAL_PANEL_SUBSCRIPTION** — "the compounding-moat play, BUT panel retention is UNKNOWN
  (caveat #6) and standalone intel is weak (caveat #7)."
- **TALENT_RECRUITING_ADDON** — "Proven WTP (RippleMatch ~$69K avg) but FCRA/LL144-constrained:
  access/subscription only, never a score."
- **METHODOLOGY_LICENSING** — scales, but "methodology alone is weakly defensible without the
  proprietary panel/data" (the single LOW-defensibility row besides sponsorship).
- **VENTURE_CREATION_ECONOMICS** — "venture-upside.md recommends AGAINST equity: four-hats conflict,
  Carta precedent. Kept for completeness." It is the only row scoring LOW on both `conflict_low` and
  `participant_alignment`.

## `pareto()`: non-dominated models over the full vector

`pareto(models=None)` (`business_model.py:pareto`) returns the codes of the non-dominated models. A
model `a` dominates `b` when `a.raw()[k] >= b.raw()[k]` on **every** dimension and strictly greater on
at least one. A model survives if no other model dominates it. Because dominance is evaluated over the
whole nine-dimension vector (no averaging), a model can stay on the frontier by being best on a single
dimension — e.g. `METHODOLOGY_LICENSING` and `LONGITUDINAL_PANEL_SUBSCRIPTION` on scalability, or
`TALENT_RECRUITING_ADDON` on capital-lightness — even if it is middling elsewhere.

## `filter_by()`: exclude extractive and conflicted models by floor

`filter_by(min_dims, models=None)` (`business_model.py:filter_by`) returns the codes meeting **every**
ordinal floor in `min_dims`. The docstring's own example excludes extractive/conflicted models:

```python
filter_by({"conflict_low": MED, "participant_alignment": MED})
```

That floor drops `VENTURE_CREATION_ECONOMICS` (both dimensions LOW) — the model the caveats advise
against — and any model that would extract from participants rather than serve them. `filter_by` is a
hard gate, not a weighting: a model that fails one floor is out regardless of how strong it is
elsewhere, mirroring the hard-gate discipline used throughout the engine.

## What the evidence favors, and what it cautions against — without claiming anyone will pay

These read directly off the `note` fields and the caveats they cite. They are statements about model
*shape and grounding*, not about demand.

**Favored by grounding and profile** (strong decomposed profile with cited comparables):

- `PER_PROBLEM_MANDATE` — the reset's native shape; highest participant alignment; a company-owned
  expensive problem is the intended demand surface.
- `RESEARCH_ENGAGEMENT` and `RND_CONTRACT` — real price comparables ($25-250K; $28K-$2.5M federal).
- `ANNUAL_RETAINER`, `RESEARCH_WALLET`, `PE_PORTFOLIO_CONTRACT` — the recurring-revenue / high-margin
  shapes, each explicitly conditioned ("requires proven repeatable value first"; "needs institutional
  standing").

**Cautioned against or constrained:**

- `SPONSORSHIP` — low revenue, trivially copyable; "the frame the reset rejects." Kept as one row, not
  the plan.
- `TALENT_RECRUITING_ADDON` — has *proven* WTP, but is FCRA/LL144-constrained: **access/subscription
  only, never a score.**
- `LONGITUDINAL_PANEL_SUBSCRIPTION` and `METHODOLOGY_LICENSING` — attractive on paper but flagged:
  standalone passive intelligence "is not a business by itself" (caveat #7), panel retention is
  UNKNOWN, and methodology alone is weakly defensible.
- `VENTURE_CREATION_ECONOMICS` — **advised against**: four-hats conflict, Carta precedent; retained
  only for completeness.

Every "favored" statement is about the model's decomposed profile and its cited comparables. None of
it asserts that a buyer will pay: observed WTP stays UNKNOWN until a signed check, and
`rational_price_ceiling` returns `None` rather than a price whenever the decision value is UNKNOWN.
