"""python3 test_voi_portfolio_calib.py"""
import numpy as np
from voi import evpi, evsi_beta, net_voi
from portfolio import Study, select
from calibration import brier, ece, calibration_curve, PredictionLedger
P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# VOI: GO/NO-GO on a $280k event; GO util = theta*Value - Cost, NO-GO = 0. theta=anchor close prob.
VALUE, COST = 900000, 280000
actions = ["GO", "NOGO"]
def util(a, theta): return (theta * VALUE - COST) if a == "GO" else np.zeros_like(np.asarray(theta, float))
prior = np.random.default_rng(3).beta(2, 6, size=40000)        # ~25% close belief
ev_perfect = evpi(prior, actions, util)
ck("EVPI is non-negative", ev_perfect >= 0)
small = evsi_beta(2, 6, m=3, actions=actions, util=util)
big   = evsi_beta(2, 6, m=40, actions=actions, util=util)
ck("EVSI increases with sample size (40 interviews > 3)", big >= small - 1e-6)
ck("EVSI <= EVPI (imperfect info can't beat perfect)", big <= ev_perfect + 1e-6)
ck("NetVOI subtracts cost", abs(net_voi(big, 15000) - (big - 15000)) < 1e-6)

# Bug-1 pin: under NONLINEAR (convex) utility the act-now baseline must be max_a E[util] over the
# prior draws, not a plug-in at the prior mean; otherwise the Jensen gap makes EVSI exceed EVPI.
Vc, Fc = 100000.0, 27000.0                                        # invest pays V*theta^2 - F (convex)
cvx_actions = ["invest", "pass"]
def cvx_util(a, theta):
    theta = np.asarray(theta, float)
    return (Vc * theta**2 - Fc) if a == "invest" else np.zeros_like(theta)
cvx_prior = np.random.default_rng(0).beta(2, 2, size=80000)       # theta~Beta(2,2): mean .5, E[t^2]=.30
cvx_evpi = evpi(cvx_prior, cvx_actions, cvx_util)
cvx_tol = max(1.0, 0.02 * cvx_evpi)
cvx_ev0 = evsi_beta(2, 2, m=0, actions=cvx_actions, util=cvx_util)
cvx_ev5 = evsi_beta(2, 2, m=5, actions=cvx_actions, util=cvx_util)
cvx_ev20 = evsi_beta(2, 2, m=20, actions=cvx_actions, util=cvx_util)
ck("EVSI(0)==0 under convex utility (no observations, no value)", cvx_ev0 == 0.0)
ck("EVSI(5) within [0, EVPI] under convex utility", -1e-6 <= cvx_ev5 <= cvx_evpi + cvx_tol)
ck("EVSI(20) within [0, EVPI] under convex utility (imperfect can't beat perfect)",
   -1e-6 <= cvx_ev20 <= cvx_evpi + cvx_tol)
ck("EVSI is non-decreasing in sample size under convex utility", cvx_ev20 >= cvx_ev5 - cvx_tol)

# Portfolio: 4 studies, two in the SAME competitive category (can't coexist), a capacity limit.
studies = [
    Study("anthropic_ai", 120000, 40000, 1200, 60, "ai_coding"),
    Study("cursor_ai",     110000, 30000, 1200, 60, "ai_coding"),   # same category -> exclusive with above
    Study("stripe_pay",     80000, 20000,  900, 40, "payments"),
    Study("datadog_obs",    70000, 25000,  800, 40, "observability"),
]
res = select(studies, participant_minute_budget=3000, researcher_hour_capacity=140, info_weight=1.0)
ck("portfolio never selects two studies in the same competitive category",
   not ("anthropic_ai" in res["selected"] and "cursor_ai" in res["selected"]))
ck("portfolio respects capacity (feasible slack >= 0)", res["slack"]["participant_minutes_left"] >= 0)
ck("portfolio picks a positive-value set", res["value"] > 0)

# Calibration: a well-calibrated forecaster beats an overconfident one on ECE.
rng = np.random.default_rng(5); n = 4000
p_true = rng.uniform(0, 1, n); y = (rng.uniform(0, 1, n) < p_true).astype(float)   # perfectly calibrated
p_over = np.clip((p_true - 0.5) * 2 + 0.5, 0, 1)                                    # pushed to extremes
ck("well-calibrated forecaster has low ECE", ece(p_true, y) < 0.05)
ck("overconfident forecaster has worse ECE", ece(p_over, y) > ece(p_true, y))
led = PredictionLedger()
for i in range(10): led.record(f"deal{i}", 0.7, "v1", "2027-01-01")
for i in range(7): led.resolve(f"deal{i}", 1.0)
for i in range(7, 10): led.resolve(f"deal{i}", 0.0)
ev = led.evaluate()
ck("prediction ledger evaluates resolved predictions (70% pred, 70% realized)", ev["n"] == 10 and ev["brier"] < 0.25)

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
