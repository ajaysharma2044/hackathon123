# Quant Assumptions Ledger

**Read this before quoting any number the engine produces.** Every value here is an **ASSUMPTION**,
not a measurement. They exist so the machinery can run; they are deliberately labeled so no output
is mistaken for evidence. The worked example ([event-optimizer.md](event-optimizer.md)) is only as
real as this ledger — which is to say, it is a *structured hypothesis*, not a forecast.

> If a number below matters to a decision, the correct next step is to **resolve it with evidence**
> (a buyer interview, a pilot, a real quote), not to trust the engine's output. The VOI engine tells
> you which ones are worth resolving.

## Effect-model coefficients ([engine/event_optimizer.py](../engine/event_optimizer.py) `A`)

All ASSUMED. Sources are judgement + directional signals from the repo, never fitted to data.

| Coefficient | Value | Basis (all ASSUMED) |
|---|---|---|
| experience base | 5.0 / 10 | midpoint anchor |
| +funded travel · +premium hotel | +1.5 · +1.2 | table-stakes at the top of this market (event-comps.md) |
| +free-choice weight (experience) | +1.5 × share | builders value autonomy |
| mentor saturation (k, max) | 6.0, +2.0 | diminishing returns on mentor density |
| research-burden penalty | −0.06 / min over 18 | the golden-goose constraint (monetization-map.md) |
| burden comfort minutes | 18 | research-minutes a builder "won't notice" |
| info power exponent | 0.5 | sublinear statistical power in n (measurement.md) |
| info free-choice weight | ×(1+1.4·share) | unconstrained surface is the unique asset |
| info follow-up multiplier | ×1.35 | 90-day retention data is the differentiator |
| contamination penalty | ×0.5 if free-choice<0.25 & sponsors≥4 | competitive-study contamination |
| **WTP research elasticity** | **0.6** (clip 0.55–1.9) | **the thesis, made economic: better research → higher WTP.** Pure assumption |

## Cost assumptions (ASSUMED)

| Line | Value | Note |
|---|---|---|
| fixed (venue/ops/staff) | $120,000 | needs real quotes (funding.md flags this) |
| per builder (food/materials) | $350 | MLH benchmark direction |
| travel per builder | $400 | stipend model (funding.md) |
| premium hotel per builder | $600 | 3 nights |
| per mentor | $500 | |
| continuation grants | $50,000 | optional |
| **scholarship coverage** (bear/base/bull) | **0.30 / 0.60 / 0.90** | fraction of travel+hotel **sponsor-funded** (Reality Hack model). **The single most important cost assumption** |

## Revenue / buyer assumptions (ASSUMED — and mostly UNKNOWN in reality)

| Quantity | Band (bear/base/bull) | Status |
|---|---|---|
| research-sponsor close probability | 0.10 / 0.25 / 0.45 | **UNKNOWN in reality** — no signed deals. Scenario band only |
| research contract value | $40K / $75K / $150K | rational ceilings (the-quote.md), **not observed WTP** |
| ancillary revenue (activation + logistics) | $30K / $80K / $180K | activation tiers + logistics recovery (economics.md, logistics-revenue.md) |
| deal correlation ρ | 0.3 | ASSUMED; independence is the alternative — sensitivity shown |
| VOI prior (anchor close) | Beta(2,6) ≈ 25% | ASSUMED belief for the GO/NO-GO VOI example |

## The honest headline from these assumptions

Under the **base** scenario, Event 1 (Design B, 200 builders) has an **expected contribution of
about −$109K** with a **16% probability of break-even**; it turns positive only in the **bull**
scenario (+$35K, 51% break-even). **Whether the event makes money is, under current assumptions, a
bet on WTP being in the bull region — and WTP is UNKNOWN.** That is not a reason for despair; it is
the precise statement of what must be de-risked before spending, and it is exactly what the VOI
engine says to resolve first (see [event-optimizer.md](event-optimizer.md)).

## Which assumptions have the highest value to resolve (ranked by sensitivity)

1. **Research close probability × contract value** — moves expected contribution from −$180K (bear)
   to +$35K (bull). This is the WTP question; resolve via pre-sell/pilot. Highest priority.
2. **Scholarship coverage fraction** — a $120K swing on cost (0.3→0.9). Resolve via sponsor conversations.
3. **WTP research elasticity** — whether better research actually raises price. Resolve via a paid pilot's renewal/upsell.
4. **Ancillary revenue** — activation + logistics. Partly resolvable from published rate cards + GMCVB.

Everything below these is second-order. **Do not add precision to the effect coefficients before
resolving 1–4** — it would be false precision on a model whose main uncertainty lives in the WTP bands.
