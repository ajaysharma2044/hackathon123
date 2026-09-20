"""
Value of Information (docs/modeling/quant-engine/quant-engine.md, Part 5). The tool that decides whether to research more
or act now — for BOTH the research we sell AND the research we run on ourselves.

EVPI  = E[max_a U(a|theta)]  -  max_a E[U(a|theta)]           (value of resolving theta perfectly)
EVSI  = value of a finite, imperfect sample (m observations)   (0 as m->0, -> EVPI as m->inf)
NetVOI = EVSI - cost                                            (do it only if positive)
"""
from __future__ import annotations
import numpy as np


def evpi(theta_samples, actions, util):
    """util(action, theta_array) -> value array. theta_samples ~ current belief about theta."""
    theta = np.asarray(theta_samples, float)
    per_action = np.stack([util(a, theta) for a in actions])          # [n_actions, n_draws]
    value_with_perfect_info = per_action.max(axis=0).mean()           # know theta, pick best each draw
    value_now = per_action.mean(axis=1).max()                         # pick one best action for all
    return float(value_with_perfect_info - value_now)


def evsi_beta(prior_a, prior_b, m, actions, util, n=20000, seed=11):
    """Sample information from observing m Bernoulli trials of a rate theta ~ Beta(prior_a,prior_b).
    Preposterior simulation: draw true theta, draw k~Binomial(m,theta); the sample-informed decision
    is the action maximizing POSTERIOR EXPECTED utility E_{theta|k}[util] (a Bayes decision, NOT a
    plug-in at the posterior mean), realized at the TRUE theta. Subtract the act-now baseline
    max_a E_theta[util] over the prior draws (NOT util at the prior mean). Both changes matter only
    under nonlinear utility, where a plug-in-at-the-mean baseline understates act-now value via the
    Jensen gap and lets EVSI exceed EVPI; with them, 0 <= EVSI(m) <= EVPI for any utility."""
    if m <= 0:
        return 0.0   # observing zero trials yields no information — EVSI is exactly 0 by definition
    rng = np.random.default_rng(seed)
    theta_true = rng.beta(prior_a, prior_b, size=n)
    k = rng.binomial(m, theta_true)
    # For each possible observed count k (0..m), the posterior is Beta(prior_a+k, prior_b+m-k); pick
    # the action with the highest posterior expected utility on a sample from that posterior.
    best_action_for_k = {}
    for kk in np.unique(k):
        post_theta = rng.beta(prior_a + kk, prior_b + (m - kk), size=8000)
        best_action_for_k[int(kk)] = int(np.argmax([np.mean(util(a, post_theta)) for a in actions]))
    chosen = np.array([best_action_for_k[int(kk)] for kk in k])
    realized = np.stack([util(a, theta_true) for a in actions])        # [A, n]
    value_with_sample = float(realized[chosen, np.arange(n)].mean())
    # act-now baseline: max_a E_theta[util(a, theta)] over the SAME prior draws
    value_now = max(float(np.mean(util(a, theta_true))) for a in actions)
    return float(value_with_sample - value_now)


def net_voi(evsi_value, cost): return float(evsi_value - cost)
