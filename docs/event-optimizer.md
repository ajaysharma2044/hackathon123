# Event Optimizer

The event is a **decision vector**, optimized against four objectives that are **not collapsed into
one score**: participant experience, research information value, economic contribution (as a
distribution), and long-term network value. We build the Pareto frontier and show what each design
sacrifices. Engine: [engine/event_optimizer.py](../engine/event_optimizer.py). **Every number below
is assumption-driven — see [quant-assumptions.md](quant-assumptions.md). The output demonstrates the
machinery and the tradeoffs; it is not a forecast.**

## Objectives & hard constraints

**Objectives (maximize, kept separate):** `Experience(X)` (0–10) · `ResearchInformation(X)` ·
`EconomicContribution(X)` (MC distribution) · `LongTermNetworkValue(X)`.

**Hard constraints (not objectives):** participant experience ≥ floor · research-minutes ≤ burden
budget · ≥1 unconstrained free-choice surface · one sponsor per competitive category · consent rules
· cash low-point ≤ working capital · researcher capacity ≥ sold studies · no surveillance · no
person scoring.

## Worked example — three designs (assumption-driven)

```
design                              exp  research  E[contrib]        p5  P(BE)  longT  qmult
A: 120 ultra-premium, few sponsors  9.7      23.0    -105,633  -187,521   0.06   14.9   0.78
B: 200 balanced                     9.2      35.0    -109,037  -248,805   0.16   18.2   1.00
C: 300 sponsor-heavy                8.0      23.5    -147,642  -321,504   0.14   19.4   0.79
```

**All three are Pareto-non-dominated** — each wins a different objective: **A** best experience and
smallest downside; **B** best research information; **C** best long-term (scale). There is no free
lunch, which is the point. Under base assumptions none has positive expected contribution — see the
honest headline below.

### Event 1 revenue as a distribution (Design B, contribution margin)

```
cost @0.6 scholarship (ASSUMED): $300,000  (gross $420,000)
   p5  -$248,805   p25 -$192,035   median -$129,383   mean -$109,037   p75 -$47,294   p95 +$102,080
P(contribution > $0)      0.16      P(> $100K) 0.05     P(> $250K) 0.01
VaR(95%)  -$248,805        CVaR(95%) / expected shortfall  -$265,811
```

The number the business planning must confront: **base-case expected contribution ≈ −$109K, ~16%
chance of break-even.** Revenue is a distribution with real downside, not a "$450K target."

### Robust evaluation (bear / base / bull WTP)

```
bear   E[contrib]= -$179,593   P(break-even)=0.01   CVaR95= -$273,714
base   E[contrib]= -$109,037   P(break-even)=0.16   CVaR95= -$265,811
bull   E[contrib]=  +$34,752   P(break-even)=0.51   CVaR95= -$255,086
```

**The event is a bet that WTP sits in the bull region — and WTP is UNKNOWN.** That is the precise
thing to de-risk before committing capital.

### Value of Information — sell now, or research more?

```
EVPI (perfectly knowing anchor close-prob):  $26,392
 5 buyer interviews:  EVSI $10,802   cost $8,000    NetVOI  +$2,802   ← worth it
10 buyer interviews:  EVSI $15,148   cost $15,000   NetVOI    +$148   ← marginal
20 buyer interviews:  EVSI $19,774   cost $28,000   NetVOI  -$8,226   ← not worth it
```

**~5–10 buyer conversations is the positive-VOI move; beyond that, more research is net-negative.
Then sell.** The engine reaches STATE.md's conclusion quantitatively and independently.

### Event Tweak Engine (one knob at a time, deltas on Design B)

```
tweak                                 d_exp d_research  d_contrib  d_P(BE) d_longT
+2 research sponsors (4->6)            0.00      +10.0    +69,988    +0.18    0.00   ← biggest cash lever
+free-choice (0.40->0.60)            +0.30      +11.0    +16,782    +0.05   +0.59   ← improves ALL FOUR
+mentors (0.10->0.20)                +0.49       0.0    -10,000    -0.01   +0.98
+continuation grants                 +0.60       0.0    -50,000    -0.07   +7.01   ← cash↓, longterm↑↑
over-burden research (18->35 min)    -1.02      +3.5     +5,539    +0.02   -2.02   ← bad trade: kills exp+longterm
-free-choice (0.40->0.20)            -0.30      -22.5   -42,399    -0.13   -0.59   ← contamination; avoid
drop 90d follow-up                    0.00      -9.1    -15,526    -0.05   -5.21   ← never do this
```

### Study portfolio (max value under capacity + one-per-competitive-category)

```
selected: anthropic_ai + stripe_pay + supabase_db   value $357,000
dropped:  cursor_ai (same ai_coding category as anthropic — exclusivity), datadog_obs (capacity)
```

## Executive memo — the 25 answers (assumption-qualified)

1. **Best Event-1 architecture now:** none of A/B/C is dominated; **B (200 balanced) maximizes
   research value, A (120 ultra-premium) minimizes downside.** Under uncertainty the robust choice
   is **A-leaning** until WTP is de-risked, because its cash downside is smallest while WTP is UNKNOWN.
2. **10 highest-leverage knobs:** research-sponsor count, free-choice share, scholarship coverage,
   90-day follow-up, contract value (WTP), mentor density, research-minutes budget, continuation
   grants, builder count, ancillary/logistics revenue.
3. **$1 → most builder experience:** funded travel and mentor density (steep early returns).
4. **$1 → most research value:** protecting free-choice surface and funding 90-day follow-up.
5. **$1 → most revenue:** an additional *non-competing* research sponsor (+$70K/pp break-even +0.18).
6. **Improves all three at once:** **more free-choice surface** (+exp, +research, +contrib, +longterm)
   — the rare win-win-win. And 90-day follow-up (research + longterm at ~no cash cost).
7. **Revenue but damages experience:** adding sponsors past the free-choice floor; over-loading
   research-minutes; over-constraining tracks. The optimizer flags these as negative-experience.
8. **Genuinely value-adding research mechanisms:** instrument the help they sought, the artifacts
   they write, the pitch they give — see [capture-system.md](capture-system.md) organic capture.
9. **Optimal scale under uncertainty:** **120–200.** 300 (C) adds long-term scale but worsens cash
   and experience; not justified until WTP is proven.
10. **Optimal sponsor/category mix:** the portfolio picks **3–4 non-competing categories**; more is
    not better once category-exclusivity and capacity bind.
11. **Unconstrained surface to preserve:** keep `free_choice_share ≥ ~0.4` — below 0.25 with ≥4
    sponsors triggers the contamination penalty that halves research value.
12. **Optimal research-minutes budget:** ~**15–18 min/participant**; past ~25 the experience loss
    dominates the tiny research gain (tweak: +3.5 research for −1.0 experience −2.0 longterm).
13. **Randomize:** credit tiers, onboarding path, docs variant, a narrow AI-workflow sub-task — the
    cheap, fair L3/L4 comparisons ([measurement.md](measurement.md)).
14. **Keep observational:** unconstrained tool choice, greenfield stack selection, switching — self-
    selected, so L1/L2 with stated limits.
15. **Never measure:** keystrokes, screens, DMs, protected traits, any person score.
16. **Spend heavily on:** funded travel/hotel (via scholarships), mentor quality, 90-day follow-up,
    brokered-key instrumentation — they lift experience *and/or* the differentiated research.
17. **Under-spend on:** oversized prize pools, excess sponsors, venue prestige beyond technical needs.
18. **Feels 10/10:** funded logistics + elite mentor density + real freedom to build + a spotlight
    demo + a continuation path — the experience objective peaks at ~9.7 (Design A).
19. **Makes a buyer pay six figures:** a question with high VOI they cannot answer from telemetry,
    delivered as a study that could have come back negative ([question-catalog.md](question-catalog.md)).
20. **Both sides return:** the flywheel — better experience → better cohort → better research →
    higher WTP → funds a better experience (see [event-system-flowcharts.md](event-system-flowcharts.md)).
21. **Event-1 revenue distribution:** base mean ≈ **−$109K**, p95 ≈ **+$102K**, P(break-even) ≈ **16%**.
22. **Downside:** VaR(95%) ≈ **−$249K**, CVaR ≈ **−$266K** — real cash at risk; do not sign
    irreversible contracts exceeding cash in hand ([funding.md](funding.md)).
23. **Highest-VOI next evidence:** the **anchor research close-probability × contract value** (WTP).
    Resolve with ~5–10 buyer conversations / a paid pilot before committing to an owned event.
24. **Build now vs wait:** build the **capture kernel + pre-sell artifact**; **wait** on the owned
    200-person event until WTP is de-risked (Wedge D / partner event is the cheaper first instrument).
25. **Single most important flywheel:** research revenue → funds a better builder experience → attracts
    a better cohort → produces better research → commands higher WTP. Obsess over this loop.

## The through-line

The quant engine, run honestly on assumption bands, says the same thing STATE.md concluded from
evidence: **the owned premium event is marginal-to-negative under current (unvalidated) assumptions,
its whole result hinges on WTP being in the bull region, and the highest-value action is to resolve
that one uncertainty cheaply — ~5–10 buyer conversations — before spending.** The engine's job was
to make that conclusion quantitative, falsifiable, and sensitivity-tested rather than a matter of
opinion. It did.
