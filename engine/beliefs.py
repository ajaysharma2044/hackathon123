"""
Belief / state layer: uncertain business quantities as DISTRIBUTIONS WITH PROVENANCE, not point
estimates or fake decimals. (docs/modeling/quant-engine/quant-engine.md)

Discipline enforced here:
- Every Belief carries provenance and a status: OBSERVED | ASSUMED | UNKNOWN.
- UNKNOWN cannot be sampled — it must first be resolved to an ASSUMED scenario band, so no
  invented probability ever silently enters a simulation.
- The only automatic Bayesian update is Beta-Binomial (a justified conjugate for rates:
  close/acceptance/retention). Evidence is reliability-weighted so a SIGNED deal moves beliefs far
  more than a "comparable company bought a $100K study." No fabricated likelihood ratios.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np
from scipy import stats

OBSERVED, ASSUMED, UNKNOWN = "OBSERVED", "ASSUMED", "UNKNOWN"

# Evidence reliability weights (docs/modeling/quant-engine/quant-engine.md, Part 2). Higher = moves beliefs more.
EVIDENCE_WEIGHT = {
    "SIGNED_COMMERCIAL": 1.00,   # a signed deal / paid pilot — the gold standard for WTP
    "DIRECT_OBSERVATION": 0.90,  # e.g. 3 of 10 qualified buyers took a meeting
    "EMPIRICAL_RATE": 0.80,      # our own segment close-rate
    "BUYER_STATED": 0.45,        # a buyer said it in an interview (cheap talk discount)
    "EXTERNAL_COMPARABLE": 0.25, # "a similar company paid $X" — transferability discount
    "EXPERT_PRIOR": 0.20,        # a labeled human prior
    "MODEL_ESTIMATE": 0.10,      # a model's own guess — lowest trust until calibrated
}


@dataclass
class Provenance:
    source: str
    reason: str
    confidence: float                    # [0,1] subjective confidence in the basis
    status: str = ASSUMED                # OBSERVED | ASSUMED | UNKNOWN
    calibration_status: str = "UNCALIBRATED"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    available_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Belief:
    name: str
    dist: object | None                  # a frozen scipy dist, or None if UNKNOWN
    prov: Provenance

    @property
    def status(self): return self.prov.status

    def sample(self, n, rng):
        if self.status == UNKNOWN or self.dist is None:
            raise ValueError(
                f"Belief '{self.name}' is UNKNOWN — resolve to an ASSUMED scenario band before "
                f"simulating. UNKNOWN stays UNKNOWN; it may not silently become a number.")
        return self.dist.rvs(size=n, random_state=rng)

    def mean(self):
        return None if self.dist is None else float(self.dist.mean())

    def interval(self, alpha=0.9):
        return None if self.dist is None else tuple(float(x) for x in self.dist.interval(alpha))


# --- factories (each records provenance explicitly) --------------------------------------------
def _prov(source, reason, confidence, status): return Provenance(source, reason, confidence, status)

def point(name, value, source, reason, confidence=1.0, status=OBSERVED):
    # A near-degenerate point mass (1e-12 width so it still samples). value==0 must CENTER the tiny
    # interval on 0 so mean() is exactly 0; a zero-scale uniform yields NaN (the special case was
    # backwards). Nonzero values keep the original loc=value width.
    scale = 1e-12
    return Belief(name, stats.uniform(loc=value - scale / 2 if value == 0 else value, scale=scale),
                  _prov(source, reason, confidence, status))

def uniform(name, lo, hi, source, reason, confidence=0.5, status=ASSUMED):
    return Belief(name, stats.uniform(loc=lo, scale=hi - lo), _prov(source, reason, confidence, status))

def beta(name, a, b, source, reason, confidence=0.6, status=ASSUMED):
    return Belief(name, stats.beta(a, b), _prov(source, reason, confidence, status))

def normal(name, mu, sigma, source, reason, confidence=0.5, status=ASSUMED):
    return Belief(name, stats.norm(mu, sigma), _prov(source, reason, confidence, status))

def lognormal(name, mu_log, sigma_log, source, reason, confidence=0.5, status=ASSUMED):
    return Belief(name, stats.lognorm(s=sigma_log, scale=np.exp(mu_log)),
                  _prov(source, reason, confidence, status))

def scenario(name, bear, base, bull, source, reason, confidence=0.4, status=ASSUMED):
    """A bear/base/bull triangular band — the honest default when we lack data. Explicitly ASSUMED."""
    c = 0.5 if bull == bear else (base - bear) / (bull - bear)
    return Belief(name, stats.triang(c=min(max(c, 0), 1), loc=bear, scale=max(bull - bear, 1e-9)),
                  _prov(source, reason, confidence, status))

def unknown(name, source, reason):
    """No basis exists. Cannot be sampled until resolved. This is the correct state for most WTP."""
    return Belief(name, None, _prov(source, reason, confidence=0.0, status=UNKNOWN))


# --- Beta-Binomial conjugate update (the only automatic update — it is justified) ---------------
@dataclass
class RateObservation:
    successes: float
    failures: float
    kind: str                            # key into EVIDENCE_WEIGHT

def update_beta(prior_a, prior_b, observations, source="posterior"):
    """Posterior for a rate (close/acceptance/retention). Each observation is reliability-weighted:
    a signed deal counts fully; a comparable is heavily discounted to fractional pseudo-counts.

    Status is OBSERVED only when SIGNED_COMMERCIAL/DIRECT_OBSERVATION evidence contributes at least
    HALF of the total posterior pseudo-count mass (prior + all weighted observations). A lone signed
    observation swamped by comparable-grade mass stays ASSUMED -- otherwise a single signed deal would
    launder a belief that is mostly comparables into OBSERVED, defeating the provenance discipline.
    (This is the mass contract behind icp_discovery.record_wtp_evidence's WTP-tier docstring.)"""
    a, b = float(prior_a), float(prior_b)
    observed_mass = 0.0
    for o in observations:
        w = EVIDENCE_WEIGHT[o.kind]
        a += o.successes * w
        b += o.failures * w
        if o.kind in ("SIGNED_COMMERCIAL", "DIRECT_OBSERVATION"):
            observed_mass += (o.successes + o.failures) * w
    reasons = ", ".join(f"{o.successes:.0f}/{o.successes+o.failures:.0f} [{o.kind}]" for o in observations)
    status = OBSERVED if observed_mass >= 0.5 * (a + b) else ASSUMED
    return beta("posterior", a, b, source, f"Beta-Binomial update: prior Beta({prior_a},{prior_b}) + {reasons}",
                confidence=0.7, status=status)


class BeliefLedger:
    """Named beliefs + business hypotheses with priors, evidence, and posteriors. Provenance-first."""
    def __init__(self): self.beliefs = {}; self.hypotheses = {}
    def set(self, b: Belief): self.beliefs[b.name] = b; return b
    def get(self, name): return self.beliefs[name]
    def unresolved(self):  # what is still UNKNOWN — the honest to-do list, not filled with guesses
        return [n for n, b in self.beliefs.items() if b.status == UNKNOWN]
