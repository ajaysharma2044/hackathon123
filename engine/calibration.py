"""
Calibration (docs/quant-engine.md, Part 17). NON-NEGOTIABLE: a quant engine earns trust only by
being calibrated. If we say P(close)=70% for 20 accounts, ~14 should close. Pure numpy.
"""
from __future__ import annotations
import numpy as np


def brier(probs, outcomes):
    p, y = np.asarray(probs, float), np.asarray(outcomes, float)
    return float(np.mean((p - y) ** 2))

def log_loss(probs, outcomes, eps=1e-12):
    p, y = np.clip(np.asarray(probs, float), eps, 1 - eps), np.asarray(outcomes, float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

def calibration_curve(probs, outcomes, bins=10):
    p, y = np.asarray(probs, float), np.asarray(outcomes, float)
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    out = []
    for b in range(bins):
        m = idx == b
        if m.any():
            out.append((float(p[m].mean()), float(y[m].mean()), int(m.sum())))
    return out

def ece(probs, outcomes, bins=10):
    """Expected Calibration Error: mean |predicted - observed| weighted by bin count."""
    curve = calibration_curve(probs, outcomes, bins)
    total = sum(c for _, _, c in curve)
    return float(sum(abs(pp - yy) * c for pp, yy, c in curve) / total) if total else 0.0

def interval_coverage(lowers, uppers, actuals):
    lo, hi, a = map(lambda x: np.asarray(x, float), (lowers, uppers, actuals))
    return float(np.mean((a >= lo) & (a <= hi)))


class PredictionLedger:
    """Store predictions with model version + timestamp; never overwrite. Evaluate against outcomes."""
    def __init__(self): self.rows = []
    def record(self, key, prob, model_version, ts, lower=None, upper=None):
        self.rows.append({"key": key, "prob": prob, "model_version": model_version, "ts": ts,
                          "lower": lower, "upper": upper, "outcome": None})
    def resolve(self, key, outcome):
        for r in self.rows:
            if r["key"] == key and r["outcome"] is None: r["outcome"] = outcome; return
    def evaluate(self):
        done = [r for r in self.rows if r["outcome"] is not None]
        if not done: return {"n": 0}
        p = [r["prob"] for r in done]; y = [r["outcome"] for r in done]
        return {"n": len(done), "brier": brier(p, y), "log_loss": log_loss(p, y),
                "ece": ece(p, y, bins=min(10, max(2, len(done)//3)))}
