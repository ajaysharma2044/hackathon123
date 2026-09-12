"""
Survival / hazard for time-to-event (docs/temporal/survival.md; Parts XIII, XIV).

Kaplan-Meier with right-censoring, hand-rolled (statsmodels is not in the stack). Models time until:
abandonment, switching, completion, mentor request, retention loss, project continuation. This is
DESCRIPTIVE — a survival curve is not a causal effect; keep the two separate. Also a minimal temporal
point-process view (arrival intensity + bursts) without over-engineering Event 1.
"""
from __future__ import annotations
import numpy as np

CAUSAL_WARNING = "Descriptive survival only. A curve is not an effect; do not read causation into it."
SURVIVAL_EVENTS = ("ABANDONMENT", "SWITCH", "COMPLETION", "MENTOR_REQUEST", "RETENTION_LOSS",
                   "CONTINUATION")

def kaplan_meier(durations, observed):
    """durations: time-to-event-or-censor; observed: 1 if the event happened, 0 if right-censored.
    Returns (times, survival_prob) step function. n small -> wide uncertainty (report n)."""
    d = np.asarray(durations, float); o = np.asarray(observed, int)
    order = np.argsort(d); d, o = d[order], o[order]
    n = len(d); at_risk = n; S = 1.0
    times, surv = [], []
    for t in np.unique(d):
        deaths = int(((d == t) & (o == 1)).sum())
        censor = int(((d == t) & (o == 0)).sum())
        if at_risk > 0 and deaths > 0:
            S *= (1 - deaths / at_risk)
        times.append(float(t)); surv.append(float(S))
        at_risk -= (deaths + censor)
    return {"times": times, "survival": surv, "n": n, "_note": CAUSAL_WARNING}

def median_survival(km):
    """First time survival drops to <= 0.5, or None if the curve never reaches it (heavy censoring)."""
    for t, s in zip(km["times"], km["survival"]):
        if s <= 0.5:
            return t
    return None

def event_intensity(timestamps_minutes, bucket=30):
    """XIV. Arrival intensity per time bucket (e.g. mentor requests / 30 min). Flags bursts as buckets
    whose count exceeds mean + 2*std. Minimal on purpose — a full Hawkes process is not warranted yet."""
    if not timestamps_minutes:
        return {"buckets": {}, "bursts": [], "_note": "no arrivals"}
    ts = np.asarray(timestamps_minutes, float)
    edges = np.arange(0, ts.max() + bucket, bucket)
    counts, _ = np.histogram(ts, bins=edges)
    mu, sd = counts.mean(), counts.std()
    bursts = [int(edges[i]) for i, c in enumerate(counts) if sd > 0 and c > mu + 2 * sd]
    return {"buckets": {int(edges[i]): int(c) for i, c in enumerate(counts)},
            "bursts": bursts, "mean": float(mu), "std": float(sd)}
