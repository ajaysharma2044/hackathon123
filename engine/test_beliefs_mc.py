"""python3 engine/test_beliefs_mc.py — belief provenance, UNKNOWN discipline, Bayesian update, MC risk."""
import numpy as np
from beliefs import (beta, scenario, unknown, update_beta, RateObservation, BeliefLedger,
                     UNKNOWN, OBSERVED, EVIDENCE_WEIGHT)
from monte_carlo import simulate, correlated_bernoulli
P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# UNKNOWN cannot be sampled or simulated.
u = unknown("wtp_acme", "no data", "no buyer has quoted a price")
ck("UNKNOWN has status UNKNOWN", u.status == UNKNOWN)
try:
    simulate(lambda s, rng: s["wtp_acme"], {"wtp_acme": u}); ck("simulate blocks UNKNOWN", False)
except ValueError as e:
    ck("simulate refuses UNKNOWN input (no invented number)", "UNKNOWN" in str(e))

# Beta-Binomial update, reliability-weighted: a signed deal moves beliefs far more than a comparable.
prior_a, prior_b = 2, 8                       # prior close-rate ~ 20%, weak
signed = update_beta(prior_a, prior_b, [RateObservation(3, 7, "SIGNED_COMMERCIAL")])
comparable = update_beta(prior_a, prior_b, [RateObservation(3, 7, "EXTERNAL_COMPARABLE")])
ck("signed evidence moves posterior mean more than a comparable",
   signed.mean() > comparable.mean() > (prior_a/(prior_a+prior_b)))
ck("signed evidence flips status to OBSERVED", signed.status == OBSERVED)
ck("comparable stays ASSUMED", comparable.status != OBSERVED)
ck("evidence weights ordered signed>comparable", EVIDENCE_WEIGHT["SIGNED_COMMERCIAL"] > EVIDENCE_WEIGHT["EXTERNAL_COMPARABLE"])

# Monte Carlo returns a distribution with tail risk, not a point.
# Toy: profit = revenue - 150k fixed cost, revenue = sum of 5 independent deals ~ close*value.
close = beta("close", 3, 7, "ASSUMED", "scenario")           # ~30%
def model(s, rng):
    n = len(s["close"])
    closes = correlated_bernoulli(np.full(5, s["close"].mean()), n, rho=0.0, rng=rng)  # 5 indep deals
    value = 60000  # assumed contract value
    return closes.sum(axis=1) * value - 150000
res = simulate(model, {"close": close}, n=20000, seed=1)
summ = res.summary()
ck("MC returns a spread (p95 > p5)", summ["p95"] > summ["p5"])
ck("P(break-even) is a probability in [0,1]", 0.0 <= res.prob_gt(0) <= 1.0)
ck("CVaR <= VaR (worse tail mean)", res.cvar(0.95) <= res.var(0.95))

# Correlation increases dispersion vs independence (concentration risk is real).
def model_rho(rho):
    def m(s, rng):
        n = len(s["close"])
        cl = correlated_bernoulli(np.full(5, 0.3), n, rho=rho, rng=rng)
        return cl.sum(axis=1) * 60000 - 150000
    return m
indep = simulate(model_rho(0.0), {"close": close}, n=40000, seed=2).summary()["std"]
corr  = simulate(model_rho(0.6), {"close": close}, n=40000, seed=2).summary()["std"]
ck("correlated deals have higher revenue variance than independent", corr > indep)

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
