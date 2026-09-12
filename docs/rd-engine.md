# R&D Engine

The most novel engine, and the one with a real academic foundation. Sells **archetype-2 (Parallel
R&D Search)**: many independent teams attack one uncertain problem; the buyer gets the best solution
**plus the value of failure** — the map of what was eliminated. Coded and tested in
[engine/value_engines.py](../engine/value_engines.py) (`rd_value`, `optimal_teams`, `value_of_failure`,
`rd_fit`).

## The economics (Boudreau, Lacetera & Lakhani, *Management Science* 2011)

Two forces as team count `n` rises:

```
Parallel path (max-of-N):  more teams → higher chance one finds an EXTREME-value solution   [pulls value UP]
Effort dilution (rivalry):  more teams → each has lower win-prob → each tries less           [pulls quality DOWN]
```

**Extreme-value dominates for HIGH-uncertainty problems; dilution dominates for LOW.** This produces
an **interior optimal number of teams** — *more is not better* — and a **fit gate**: the format is
inferior for low-uncertainty problems, where one focused expert team beats a diluted crowd.

## The value model (coded)

```
mean_quality(n)   = mu0 · n^(-effort_elasticity)          # rivalry dilutes effort
best(n, σ)        = E[max of n draws ~ Normal(mean_quality(n), σ)]   # parallel path; σ scales with uncertainty
value_of_failure(n) = search_value · (1 − (1−p_elim)^(losers))       # failures eliminate search space
rd_value(n, uncertainty) = value_scale·best(n,σ) + value_of_failure(n) − per_team_cost·n
optimal_teams(uncertainty) = argmax_n rd_value(n, uncertainty)       # the INTERIOR optimum
```

All coefficients ASSUMED ([quant-assumptions.md](quant-assumptions.md)); the *shape* is what matters
and it matches the literature. Verified in tests: optimal `n` is larger for high-uncertainty
problems, the value curve is non-monotonic (interior peak), and value-of-failure rises with losing teams.

## The value of failure — why buyers pay for the losers

If 20 teams try 20 approaches and 14 fail, the failures **cheaply eliminate large regions of the
search space**, and independent **convergence** (several teams reaching the same approach) is a strong
signal that approach is right. The buyer is not just buying the winner — they're buying a **decision
map**: pursue A, abandon B and C, watch D. This is what a single expert team cannot produce, and it
is the R&D engine's distinctive deliverable.

Outputs the buyer receives:
- the best working prototype(s) + a shortlist for follow-on
- an **elimination map**: approaches tried and why they failed (search-space narrowing)
- **convergence signal**: where independent teams agreed
- `P(≥1 useful solution)` and the marginal value of the next team (so they can size the purse)

## The fit gate — when we must decline

`rd_fit(problem)` returns **inferior** (and the matcher will not sell R&D) when:
- **uncertainty < ~0.35** — one focused team beats a diluted crowd (the core Boudreau/Lakhani result)
- **not parallelizable / not prototypeable in 48–72h / no clean evaluation** — the contest structure fails
- **needs deep specialist knowledge or equipment** a builder crowd lacks

This is the discipline that stops us pitching R&D to companies whose problems a hackathon handles
*worse* than their internal team — a mistake a "big budget" would otherwise tempt.

## Pricing (rational ceiling, not WTP)

Comparables ([innovation-budget.md](innovation-budget.md)): a delivered enterprise build event runs
**$600K–$2.5M** (Accenture/DLA $1.27M); prize-challenge operators (Luminary Labs) run **$2.8M–$15M**
vehicles; Topcoder charged **$100K** for one NASA challenge. Our compressed version, packaged as a
**directed R&D wallet** (archetype 9), plausibly ceilings at **$75K–$300K** per challenge track. WTP
**UNKNOWN** until quoted.

## IP and follow-on

Prize-tournament norm: buyer licenses or owns the winning solution; participants keep everything else.
Follow-on is the real upside — a promising team continues under a paid design partnership
([venture-upside.md](venture-upside.md) keeps this clean of equity/conflict). IP terms must be in the
participant agreement *before* the event, disclosed in the challenge (recruiting-legal.md discipline).
