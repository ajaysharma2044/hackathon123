"""python3 test_value_engines.py"""
import numpy as np
from value_engines import (expected_max_of_n, effective_mean_quality, value_of_failure, rd_value,
                           optimal_teams, RDProblem, rd_fit, activation_value, product_dev_value,
                           min_detectable_effect)
P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# R&D: the two Boudreau/Lakhani forces produce an INTERIOR optimum, and it's LARGER for high uncertainty.
ck("max-of-N increases with N (parallel path)", expected_max_of_n(1,0.4,20) > expected_max_of_n(1,0.4,3))
ck("effort dilutes as teams grow (rivalry)", effective_mean_quality(40) < effective_mean_quality(3))
ck("value of failure grows with more losing teams", value_of_failure(20) > value_of_failure(5))
n_hi, v_hi, _ = optimal_teams(uncertainty=0.9)
n_lo, v_lo, _ = optimal_teams(uncertainty=0.15)
ck("optimal team count is larger for HIGH-uncertainty problems", n_hi > n_lo)
ck("optimal team count is an interior optimum, not the max (n*<60)", 1 <= n_hi < 60)
# The rd_value curve is non-monotonic (rises then the dilution+cost bite) for low uncertainty.
_, _, curve_lo = optimal_teams(0.15)
vals = [v for _, v in curve_lo]
ck("low-uncertainty value curve is non-monotonic (interior peak)", np.argmax(vals) < len(vals) - 1)
# Fit gate: low uncertainty -> INFERIOR (one team beats a crowd).
v, why = rd_fit(RDProblem(uncertainty=0.2, parallelizable=0.9, prototypeable_in_event=0.9, evaluable=0.9, needs_deep_domain=0.2))
ck("low-uncertainty problem judged INFERIOR for a hackathon", v == "inferior")
v2, _ = rd_fit(RDProblem(uncertainty=0.8, parallelizable=0.9, prototypeable_in_event=0.8, evaluable=0.8, needs_deep_domain=0.2))
ck("high-uncertainty parallelizable problem judged advantageous", v2 == "advantageous")
v3, _ = rd_fit(RDProblem(uncertainty=0.8, parallelizable=0.9, prototypeable_in_event=0.8, evaluable=0.8, needs_deep_domain=0.9))
ck("domain/equipment-heavy problem judged INFERIOR", v3 == "inferior")

# Activation: retained users fall out of the funnel; cost-per-retained comparable to CAC.
av = activation_value(120, {"activation":0.7,"meaningful":0.6,"integration":0.5,"retain30":0.6,"retain90":0.5},
                      value_per_retained90=2000, cost=40000, cac_benchmark=500)
ck("activation funnel retains fewer than exposed", av["retained90"] < 120)
ck("activation reports whether it beats paid-marketing CAC", "beats_paid_marketing" in av)

# Product-dev: coverage saturates in team count (variation value, not max-of-N).
pd_small = product_dev_value(5, 0.6, 500000, 0.4)
pd_big = product_dev_value(25, 0.6, 500000, 0.4)
ck("product-dev coverage rises with teams but saturates", pd_big["coverage"] > pd_small["coverage"] and pd_big["coverage"] < 1.0)

# Experimentation: 200 builders split into arms can only detect large effects (honest power).
mde = min_detectable_effect(n_per_arm=60)
ck("MDE at ~60/arm is large (only big effects detectable)", 0.1 < mde < 0.35)

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
