"""
Monte Carlo simulation + risk metrics. Runs a model over sampled Beliefs and returns a
DISTRIBUTION of outcomes (mean, median, percentiles, tail risk) — never a single point estimate.
Refuses to run if any input is UNKNOWN. (docs/quant-engine.md, Parts 7 & 20)
"""
from __future__ import annotations
import numpy as np
from beliefs import Belief, UNKNOWN


def correlated_bernoulli(probs, n, rho, rng):
    """Correlated closes/attendance via a Gaussian copula with a shared latent factor. rho in [0,1).
    Independence (rho=0) is the default assumption; correlation matters when a category-wide demand
    shock moves several buyers together (docs/quant-engine.md, Part 21)."""
    probs = np.atleast_1d(np.asarray(probs, float))
    k = probs.shape[0]
    common = rng.standard_normal((n, 1))
    idio = rng.standard_normal((n, k))
    z = np.sqrt(rho) * common + np.sqrt(1 - rho) * idio      # corr(z_i, z_j) = rho
    thresh = np.array([_ppf(p) for p in probs])
    return (z < thresh).astype(float)                        # P(z<thresh_i) = probs_i

def _ppf(p):
    from scipy.stats import norm
    return norm.ppf(np.clip(p, 1e-9, 1 - 1e-9))


class MCResult:
    def __init__(self, out, inputs): self.out = np.asarray(out, float); self.inputs = inputs
    def summary(self):
        o = self.out
        return {"mean": float(o.mean()), "median": float(np.median(o)),
                "p5": float(np.percentile(o, 5)), "p25": float(np.percentile(o, 25)),
                "p75": float(np.percentile(o, 75)), "p95": float(np.percentile(o, 95)),
                "std": float(o.std())}
    def prob_gt(self, t): return float((self.out > t).mean())
    def prob_lt(self, t): return float((self.out < t).mean())
    def percentile(self, p): return float(np.percentile(self.out, p))
    def var(self, alpha=0.95):
        """Value at Risk: the alpha-worst outcome (here, low tail of profit)."""
        return float(np.percentile(self.out, (1 - alpha) * 100))
    def cvar(self, alpha=0.95):
        """Conditional VaR / expected shortfall: mean of the worst (1-alpha) tail."""
        q = np.percentile(self.out, (1 - alpha) * 100)
        tail = self.out[self.out <= q]
        return float(tail.mean()) if tail.size else float(q)


def simulate(model, params: dict[str, Belief], n=50000, seed=7):
    """model(samples: dict[name->np.array]) -> np.array of outcomes."""
    unknown = [k for k, b in params.items() if b.status == UNKNOWN]
    if unknown:
        raise ValueError(f"Cannot simulate: UNKNOWN inputs must be resolved to scenario bands first: "
                         f"{unknown}. (docs/quant-assumptions.md)")
    rng = np.random.default_rng(seed)
    samples = {k: b.sample(n, rng) for k, b in params.items()}
    return MCResult(model(samples, rng), samples)
