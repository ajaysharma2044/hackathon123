"""
Value of Information (docs/quant-engine.md, Part 5). The tool that decides whether to research more
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
    Preposterior simulation: draw true theta, draw k~Binomial(m,theta), form posterior mean, pick the
    action that is best under the posterior, score it at the TRUE theta. Average, minus act-now value."""
    rng = np.random.default_rng(seed)
    theta_true = rng.beta(prior_a, prior_b, size=n)
    k = rng.binomial(m, theta_true)
    post_mean = (prior_a + k) / (prior_a + prior_b + m)
    # choose best action under posterior mean (decision), realize utility at true theta
    util_under_post = np.stack([util(a, post_mean) for a in actions])   # [A, n]
    chosen = util_under_post.argmax(axis=0)
    realized = np.stack([util(a, theta_true) for a in actions])
    value_with_sample = realized[chosen, np.arange(n)].mean()
    # act-now baseline: best action under the prior mean
    prior_mean = prior_a / (prior_a + prior_b)
    value_now = max(float(np.mean(util(a, np.full(n, prior_mean)))) for a in actions)
    return float(value_with_sample - value_now)


def net_voi(evsi_value, cost): return float(evsi_value - cost)
