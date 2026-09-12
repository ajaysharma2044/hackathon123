"""
Specialized commercial value engines (docs/*-engine.md). Each answers: does a hackathon hold an
advantage for THIS use, what is the value structure, and when is the format INFERIOR. Distinct
engines because the economics differ. numpy/scipy. All coefficients ASSUMED (quant-assumptions.md).

Epistemic tags on outputs: 'advantageous' | 'inferior' | 'no_fit' are STRUCTURAL verdicts from the
inputs; every dollar figure is a rational CEILING from assumed bands, never observed WTP.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy import stats

# ---------------------------------------------------------------------------------------------
# R&D ENGINE — parallel-search value with the Boudreau/Lacetera/Lakhani two-force structure.
#   Force 1 (parallel path / max-of-N): more teams -> higher chance one finds an extreme solution.
#   Force 2 (effort dilution / rivalry): more teams -> each exerts less effort (mean quality drops).
#   Extreme-value force dominates for HIGH-uncertainty problems; dilution dominates for LOW.
#   Source: Boudreau, Lacetera & Lakhani, "Incentives and Problem Uncertainty in Innovation
#   Contests," Management Science 2011 (verified via web search; see docs/rd-engine.md).
# ---------------------------------------------------------------------------------------------
RD_A = {"mu0": 1.0, "base_sigma": 0.35, "effort_elasticity": 0.18, "value_scale": 400000,
        "per_team_cost": 3000, "failure_elim_per_team": 0.06, "search_value": 250000}

def expected_max_of_n(mu, sigma, n, draws=20000, seed=0):
    """E[max of n i.i.d. Normal draws] — the parallel-path value. Grows in n, with diminishing returns."""
    rng = np.random.default_rng(seed)
    return float(rng.normal(mu, sigma, size=(draws, max(int(n), 1))).max(axis=1).mean())

def effective_mean_quality(n):
    """Mean team quality after effort dilution: mu(n) = mu0 * n^(-elasticity). Declines with rivalry."""
    return RD_A["mu0"] * (max(int(n), 1) ** (-RD_A["effort_elasticity"]))

def value_of_failure(n, winners=1):
    """Non-winning teams eliminate parts of the search space -> information value (assumed)."""
    losers = max(int(n) - winners, 0)
    return RD_A["search_value"] * (1 - (1 - RD_A["failure_elim_per_team"]) ** losers)

def rd_value(n, uncertainty, winners=1):
    """Total expected R&D value at n teams: best-solution value (max-of-N of diluted-effort quality)
    + failure/elimination info - team cost. `uncertainty` in [0,1] scales solution-quality variance."""
    sigma = RD_A["base_sigma"] * (0.4 + 1.6 * uncertainty)   # high uncertainty -> fat tails -> max-of-N matters
    best = expected_max_of_n(effective_mean_quality(n), sigma, n)
    return RD_A["value_scale"] * best + value_of_failure(n, winners) - RD_A["per_team_cost"] * n

def optimal_teams(uncertainty, n_max=60):
    """The interior optimum — NOT 'more is better'. Returns (n*, value, full curve)."""
    curve = [(n, rd_value(n, uncertainty)) for n in range(1, n_max + 1)]
    n_star, v_star = max(curve, key=lambda t: t[1])
    return n_star, v_star, curve

@dataclass
class RDProblem:
    uncertainty: float          # 0..1 (how unclear the best approach is)
    parallelizable: float       # 0..1 (can many teams attack independently?)
    prototypeable_in_event: float  # 0..1 (can a meaningful attempt fit in 48-72h?)
    evaluable: float            # 0..1 (is there a clear evaluation function?)
    needs_deep_domain: float    # 0..1 (requires scarce specialist knowledge/equipment?)

def rd_fit(p: RDProblem):
    """Structural verdict. Hackathon is INFERIOR for low-uncertainty, non-parallelizable, or
    domain/equipment-heavy problems (one focused expert team beats a crowd there)."""
    if p.uncertainty < 0.35:
        return "inferior", "low uncertainty: one focused team's effort beats a diluted crowd (Boudreau/Lakhani)"
    if p.parallelizable < 0.4 or p.prototypeable_in_event < 0.4 or p.evaluable < 0.4:
        return "inferior", "not parallelizable / not prototypeable in-event / not cleanly evaluable"
    if p.needs_deep_domain > 0.7:
        return "inferior", "needs scarce specialist knowledge or equipment a builder crowd lacks"
    return "advantageous", "high-uncertainty, parallelizable, prototypeable, evaluable: max-of-N wins"


# ---------------------------------------------------------------------------------------------
# ACTIVATION ENGINE — exposure -> activation -> meaningful use -> integration -> 30/90d retention.
#   Value = incremental RETAINED users x value/retained, benchmarked against paid-marketing CAC.
#   The embedded high-VOI research question: do credits create retention or subsidize activation?
# ---------------------------------------------------------------------------------------------
def activation_funnel(exposed, rates: dict):
    """rates: exposure->activation->meaningful->integration->retain30->retain90 (each a fraction)."""
    stages = ["activation", "meaningful", "integration", "retain30", "retain90"]
    n = exposed; out = {"exposed": exposed}
    for s in stages:
        n *= rates[s]; out[s] = n
    return out

def activation_value(exposed, rates, value_per_retained90, cost, cac_benchmark=None):
    funnel = activation_funnel(exposed, rates)
    retained = funnel["retain90"]
    gross = retained * value_per_retained90
    out = {"funnel": funnel, "retained90": retained, "gross_value": gross, "net_value": gross - cost,
           "effective_cost_per_retained": (cost / retained) if retained else float("inf")}
    if cac_benchmark:
        out["beats_paid_marketing"] = out["effective_cost_per_retained"] < cac_benchmark
    return out


# ---------------------------------------------------------------------------------------------
# PRODUCT-DEVELOPMENT ENGINE — value of VARIATION (many independent prototypes reveal the solution
#   space, feature demand, integration patterns) AND value of CONVERGENCE (independent teams
#   choosing X is a strong signal). Different from R&D: the buyer wants the DISTRIBUTION, not the max.
# ---------------------------------------------------------------------------------------------
def product_dev_value(n_teams, diversity, decision_value, p_decision_changes, per_team_cost=2500):
    """Information value about a product decision. Saturates in n (you learn the space, then repeat).
    diversity in [0,1] raises the information per team; convergence is captured by low variance later."""
    coverage = 1 - np.exp(-0.25 * n_teams * (0.4 + 0.6 * diversity))   # solution-space coverage, saturating
    info_value = decision_value * p_decision_changes * coverage
    return {"coverage": float(coverage), "info_value": float(info_value),
            "net_value": float(info_value - per_team_cost * n_teams)}


# ---------------------------------------------------------------------------------------------
# EXPERIMENTATION ENGINE — power for a randomized arm inside the event (credits, docs, onboarding).
# ---------------------------------------------------------------------------------------------
def min_detectable_effect(n_per_arm, base_rate=0.4, power=0.8, alpha=0.05):
    """Two-proportion MDE (absolute pp) at given per-arm n. Honest about what 200 builders can detect."""
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    p = base_rate
    return float((z_a + z_b) * np.sqrt(2 * p * (1 - p) / n_per_arm))


# ---------------------------------------------------------------------------------------------
# SPONSORSHIP ENGINE — traditional branding/recruiting. High certainty, LOW VOI. Priced by
#   published comparables (event-comps.md), not by information value. Included for completeness;
#   it is the floor product, not the differentiated one.
# ---------------------------------------------------------------------------------------------
SPONSOR_COMPARABLES = {  # published ladders (event-comps.md); ASSUMED mapping to our 200-person event
    "activation_track": (5000, 25000), "title": (30000, 80000), "recruiting_access": (5000, 27000),
    "meal_or_logistics": (2000, 15000)}
def sponsorship_value(tier): return SPONSOR_COMPARABLES.get(tier, (0, 0))
