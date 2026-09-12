# Quant Engine

A probabilistic decision system, not a scoring spreadsheet. HIGH/MED/LOW survives only as
human-readable summary; the computational core operates on **distributions with provenance**,
Bayesian updates where justified, Monte Carlo, Value of Information, constrained optimization, and
calibration. Runnable: [engine/](../engine/) (five modules, 54 passing checks across five suites).

## The one rule that separates this from a consulting memo

```
Evidence → Beliefs → Models → Scenarios → Optimization → Decisions → Outcomes → Calibration → Beliefs
```

not `Evidence → opinion → recommendation`. **The LLM is not the numerical authority.** Claude
extracts evidence, proposes hypotheses, classifies, explains, and flags contradictions. **Python
computes** every probability, simulation, optimization, VOI, and calibration number. No belief
appears because Claude thinks it reasonable; if there is no basis, the state is `UNKNOWN`.

## Architecture

```
RAW EVIDENCE ─▶ BELIEF / STATE LAYER (beliefs.py) ──┬─▶ BUYER MODEL   (buyer_state)
   (schema 001/002)   distributions + provenance    ├─▶ STUDY MODEL   (portfolio.py)
                      OBSERVED | ASSUMED | UNKNOWN   └─▶ EVENT MODEL   (event_optimizer.py)
                                                              │
                            SCENARIO ENGINE (monte_carlo.py) ─┤ bear/base/bull, correlation, tail risk
                            VALUE OF INFORMATION (voi.py) ────┤ EVPI / EVSI / NetVOI
                            OPTIMIZATION (portfolio, optimizer) ┘ constrained + multi-objective Pareto
                                        │
                              DECISION (schema 003 decision ledger)
                                        │
                              OUTCOME ─▶ CALIBRATION (calibration.py) ─▶ UPDATE BELIEFS
```

## The belief layer ([engine/beliefs.py](../engine/beliefs.py))

Every uncertain quantity is a `Belief` = a distribution + `Provenance` + a `status`:

- **OBSERVED** — grounded in real data (a signed deal, an actual close rate).
- **ASSUMED** — a scenario band we chose deliberately, documented in
  [quant-assumptions.md](quant-assumptions.md). Legitimate for planning; never confused with data.
- **UNKNOWN** — no basis exists. **Cannot be sampled.** `simulate()` refuses to run with any
  UNKNOWN input and names it. This is how "UNKNOWN stays UNKNOWN" is *enforced*, not just promised —
  most WTP beliefs are UNKNOWN and stay that way until a price is quoted.

Distributions: point, uniform, beta (rates), normal, lognormal (contract values), triangular
scenario (the honest default: bear/base/bull), categorical. Each carries `source, reason,
confidence, calibration_status, created_at, available_at`.

### Bayesian updating — only where it is justified

The single automatic update is **Beta-Binomial conjugate** for rates (close / acceptance /
retention). No fabricated likelihood ratios. Evidence is **reliability-weighted** so the same
"3 of 10" moves beliefs very differently by source:

```
SIGNED_COMMERCIAL 1.00  >  DIRECT_OBSERVATION 0.90  >  EMPIRICAL_RATE 0.80  >
BUYER_STATED 0.45  >  EXTERNAL_COMPARABLE 0.25  >  EXPERT_PRIOR 0.20  >  MODEL_ESTIMATE 0.10
```

A signed $100K deal moves WTP beliefs ~4× more than "a comparable company bought a $100K study,"
and flips the belief's status to OBSERVED. A comparable stays ASSUMED. (Tested.)

## Monte Carlo + risk ([engine/monte_carlo.py](../engine/monte_carlo.py))

Revenue and every economic quantity is a **distribution**, never a point. Outputs: mean, median,
p5/p25/p75/p95, `P(X > threshold)`, `VaR(95%)`, `CVaR(95%)` (expected shortfall). Deals are **not
assumed independent** — a Gaussian-copula shared shock models category-wide demand collapse
(correlation raises variance, tested). Independence is the labeled default when correlation is
UNKNOWN, and sensitivity is shown.

## Value of Information ([engine/voi.py](../engine/voi.py)) — the "stop researching, sell" test

```
EVPI  = value of resolving an uncertainty perfectly
EVSI  = value of a finite sample (m interviews); 0 as m→0, → EVPI as m→∞
NetVOI = EVSI − research cost;  do it only if positive
```

Applied to both what we sell *and* what we should research about ourselves. In the worked example
([event-optimizer.md](event-optimizer.md)) it returns a crisp answer: **~5 buyer interviews is
positive-VOI (+$2.8K), ~10 is marginal, and beyond ~10 more research is net-negative — sell.** This
is the mechanism that ends endless desk research.

## Calibration ([engine/calibration.py](../engine/calibration.py)) — non-negotiable

A quant engine earns trust only by being right about its own uncertainty. Every probabilistic
prediction is logged with model version + timestamp and never overwritten; when outcomes arrive we
compute **Brier score, log loss, calibration curve, ECE, interval coverage.** If we say P(close)=70%
for 20 accounts, ~14 must close or the model is recalibrated. (Well-calibrated vs overconfident
forecasters are distinguished in tests.)

## What the engine is and is not

**Is:** the machinery to reason under uncertainty honestly — distributions, tail risk, VOI,
multi-objective tradeoffs, calibration — so decisions rest on explicit assumptions and sensitivity,
not vibes.

**Is not:** a source of truth about numbers we haven't measured. Its worked-example outputs are
**assumption-driven** ([quant-assumptions.md](quant-assumptions.md)); their value is showing
*which assumption drives the answer* and *what evidence would change it*, not the specific dollar
figures. The engine gets *more* sophisticated only as data justifies it — a simpler model that
predicts equally well always wins.

## Non-negotiables (enforced in code where possible)

No fabricated WTP or probabilities · no fake decimals from HIGH/MED/LOW · UNKNOWN stays UNKNOWN
(sampling refused) · participant experience is a core objective, not a soft constraint · no
surveillance · no person quality/founder/employability scores · activity ≠ causal effect ·
activation ≠ retention · choice ≠ preference unless `ChoiceSet` observed · rational WTP ceiling ≠
observed WTP · provenance on every derived number · every model starts uncalibrated and earns trust.
