"""
Participant opportunity hub + value fan-out + monetization legality (docs/talent/transaction-flow.md,
docs/venture/legal-policy.md; Parts XLIII-XLsix, LXIII-LXV, XL).

One naturally-produced activity (a repo, a demo, a mentor request) can serve MANY value surfaces —
but hiring/venture surfaces light up ONLY with the participant's per-scope opt-in. The participant hub
(Part XLV) gathers every opportunity in one place so monetization is participant-POSITIVE. And a hard
legality guard blocks investment success fees until securities counsel confirms (Parts XL, LXIII).
"""
from __future__ import annotations
import compliance

# The multiplier vector, extended with HiringValue + VentureValue (Part LXIV). Kept as a VECTOR,
# never auto-summed.
VALUE_SURFACES = ["ParticipantValue", "OperationalValue", "ResearchValue", "CommercialValue",
                  "HiringValue", "VentureValue", "CompoundingValue"]

# Which value surfaces an activity can serve, and which require a participant opt-in scope (Part XLVI).
# (surface, required_scope_or_None)
ACTIVITY_FANOUT = {
    "REPO_SUBMISSION": [("ParticipantValue", None), ("ResearchValue", None), ("CommercialValue", None),
                        ("CompoundingValue", None), ("HiringValue", "EMPLOYER"), ("VentureValue", "INVESTOR")],
    "PROJECT_DEMO": [("ParticipantValue", None), ("ResearchValue", None), ("CommercialValue", None),
                     ("HiringValue", "EMPLOYER"), ("VentureValue", "INVESTOR")],
    "MENTOR_REQUEST": [("ParticipantValue", None), ("OperationalValue", None), ("ResearchValue", None),
                       ("CommercialValue", None)],   # never a hiring/venture signal — support, not evidence-for-sale
    "CONTINUATION_30D": [("ResearchValue", None), ("CompoundingValue", None),
                         ("HiringValue", "EMPLOYER"), ("VentureValue", "INVESTOR")],
}

# Participant hub opportunity categories (Part XLV).
HUB_CATEGORIES = ["EmployerInterest", "InvestorInterest", "DesignPartnerInterest",
                  "PaidProjectOpportunities", "ContinuationGrants", "AcceleratorInterest"]

# Monetization legality (Parts XL, LXIII). Investment success fees are FORBIDDEN until counsel clears.
MONETIZATION = {
    "EVENT_SPONSORSHIP": ("ALLOWED", "standard event sponsorship"),
    "RECRUITING_PARTNERSHIP": ("NEEDS_LEGAL", "placement/success fees may implicate employment-agency law (see recruiting-legal.md)"),
    "TALENT_ACCESS_SUBSCRIPTION": ("ALLOWED", "access/subscription, not per-hire — the safer structure"),
    "PAID_PROJECT_FACILITATION": ("NEEDS_LEGAL", "clarify IP + worker classification before facilitating paid work"),
    "INVESTOR_SUBSCRIPTION": ("ALLOWED", "subscription to opt-in discovery / intelligence"),
    "VENTURE_INTELLIGENCE": ("ALLOWED", "aggregate venture-trend intelligence"),
    "INVESTMENT_SUCCESS_FEE": ("FORBIDDEN_UNTIL_COUNSEL", "taking a % of capital raised can be broker-dealer activity (securities law); do NOT until counsel confirms"),
    "PLACEMENT_SUCCESS_FEE": ("NEEDS_LEGAL", "per-hire success fees are legal but commercially weak and regulated; validate first"),
}


def fan_out(activity: str, opted_scopes: dict = None) -> list:
    """The value surfaces a single activity serves, gated by opt-in. Hiring/venture surfaces appear
    only if the participant opted into that scope. Returns surface names."""
    opted_scopes = opted_scopes or {}
    if activity not in ACTIVITY_FANOUT:
        raise ValueError(f"unknown activity {activity!r}")
    out = []
    for surface, scope in ACTIVITY_FANOUT[activity]:
        if scope is None or compliance.individual_disclosure_allowed(opted_scopes, scope):
            out.append(surface)
    return out


def participant_opportunity_hub(interests_by_category: dict) -> dict:
    """One place showing every opportunity surfaced FOR the participant; they choose what to pursue.
    interests_by_category: {HUB_CATEGORY: [items]}. Unknown categories rejected."""
    for k in interests_by_category:
        if k not in HUB_CATEGORIES:
            raise ValueError(f"unknown hub category {k!r}")
    hub = {c: interests_by_category.get(c, []) for c in HUB_CATEGORIES}
    hub["_control"] = "The participant chooses which opportunities to pursue; nothing is auto-shared."
    return hub


def assert_monetization_allowed(kind: str) -> str:
    """Raise for monetization that is forbidden until legal review; return the status otherwise."""
    if kind not in MONETIZATION:
        raise ValueError(f"unknown monetization kind {kind!r}")
    status, note = MONETIZATION[kind]
    if status == "FORBIDDEN_UNTIL_COUNSEL":
        raise PermissionError(f"{kind}: {note}")
    return status


def dedup_revenue(economic_events) -> float:
    """A project can lead to many transactions, but the same economic value is not double-counted
    (Part XLIII). economic_events: list of {id, amount}. Sums each unique id once."""
    seen, total = set(), 0.0
    for e in economic_events:
        if e["id"] not in seen:
            seen.add(e["id"]); total += e.get("amount", 0.0)
    return total
