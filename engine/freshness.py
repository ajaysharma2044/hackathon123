"""
Evidence freshness & decay (docs/temporal/freshness.md; Parts XXIV, XXV, LIX).

Every claim has a shelf life. A 2026 Claude-vs-Gemini tool preference may be stale by 2028; eHub room
capacity persists until the facility changes. We mark age and validity window BY CLAIM TYPE — we do
NOT silently discard old evidence, and we do NOT assume exponential decay unless a half-life is
actually grounded. Freshness weights company intelligence (LIX): a new launch outranks a 3-year-old
strategy article, but the old one is aged, not deleted.
"""
from __future__ import annotations
from datetime import datetime

# XXIV. Validity windows by claim type (days). half_life=None means "decay shape UNKNOWN — do not
# assume exponential". These are grounded orderings (venue persists >> company strategy), not precise
# constants; the numbers are ASSUMED and flagged as such.
FRESHNESS_POLICY = {
    "venue_fact":            {"validity_days": 3650, "half_life": None, "basis": "persists until facility change"},
    "cornell_culture":       {"validity_days": 730,  "half_life": None, "basis": "moderately persistent"},
    "tool_preference":       {"validity_days": 180,  "half_life": 120,  "basis": "can change quickly (model releases)"},
    "company_strategy":      {"validity_days": 365,  "half_life": 180,  "basis": "possibly short-lived"},
    "product_pricing":       {"validity_days": 180,  "half_life": None, "basis": "changes on vendor cadence"},
    "recruiting_cycle":      {"validity_days": 365,  "half_life": None, "basis": "annual seasonality"},
    "participant_capability":{"validity_days": 365,  "half_life": None, "basis": "artifact-anchored; grows, doesn't expire"},
}
_ASSUMED = "validity_days are ASSUMED orderings, not measured constants"

def freshness(claim_type, observed_at: datetime, now: datetime):
    """Age in days + a FRESH/AGING/STALE status against the claim's validity window. Never discards —
    STALE means 'mark and down-weight', not 'delete'."""
    pol = FRESHNESS_POLICY.get(claim_type)
    if pol is None:
        return {"status": "UNKNOWN_POLICY", "age_days": None, "_note": "no freshness policy for this claim type"}
    age = (now - observed_at).days
    vd = pol["validity_days"]
    status = "FRESH" if age <= vd * 0.5 else ("AGING" if age <= vd else "STALE")
    return {"claim_type": claim_type, "age_days": age, "validity_days": vd, "status": status,
            "basis": pol["basis"], "_note": _ASSUMED}

def decay_weight(claim_type, observed_at: datetime, now: datetime):
    """Multiplicative weight in (0,1]. Exponential ONLY when a half-life is grounded for this claim
    type; otherwise return None (weight UNKNOWN) rather than inventing a decay curve (Part XXV)."""
    pol = FRESHNESS_POLICY.get(claim_type)
    if pol is None or pol["half_life"] is None:
        return {"weight": None, "_note": "half-life not grounded; do NOT assume exponential decay"}
    age = (now - observed_at).days
    import math
    return {"weight": 0.5 ** (age / pol["half_life"]), "half_life_days": pol["half_life"]}
