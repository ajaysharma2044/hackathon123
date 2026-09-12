"""
Mentor routing + the support-success confounder (docs/research-ops/mentor-system.md,
docs/research-ops/mentor-interventions.md).

Mentors exist to HELP participants — that is the primary job, and the routing here optimises the
participant's wait time, not the research. The research value is a byproduct: a help request reveals
a blocker, a repeated request reveals systemic friction, and a company engineer rescuing every team
reveals a confounder we must not mistake for organic product success.

Two functions matter most:
  * route_request — assign the right mentor category fast; keep per-category queues visible (this is
    OPERATIONS data first, research evidence second).
  * support_intensity / classify_success — separate "succeeded with little help" from "succeeded only
    after heavy expert (often vendor) intervention", WITHOUT claiming causality. We label; we do not
    estimate an effect. (Part VIII)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# problem category → mentor category routing (Part IX)
ROUTING = {
    "auth": "BACKEND", "api_integration": "BACKEND", "database": "DB", "data_modeling": "DB",
    "infra": "INFRA", "deploy": "INFRA", "cloud": "CLOUD", "frontend": "FRONTEND", "ui": "DESIGN",
    "model": "AI_ML", "agent": "AGENTS", "ml": "AI_ML", "optimization": "ORIE_OPT",
    "hardware": "HARDWARE", "robotics": "ROBOTICS", "product": "PRODUCT", "domain": "DOMAIN",
    "general": "GENERAL",
}


@dataclass
class Mentor:
    mentor_id: str
    category: str
    is_company_engineer: bool = False       # the confounder flag
    affiliation: str = "neutral"
    active_load: int = 0                     # how many open requests assigned right now


@dataclass
class SupportRequest:
    request_id: str
    team_id: str
    problem_category: str
    opened_at: object
    priority: int = 0
    assigned_mentor: Optional[str] = None
    resolution_state: Optional[str] = None


def route_request(req: SupportRequest, mentors: list) -> Optional[Mentor]:
    """Assign the least-loaded available mentor in the routed category; fall back to GENERAL.
    Returns the chosen mentor (and mutates its load), or None if no mentor fits."""
    want = ROUTING.get(req.problem_category, "GENERAL")
    pool = [m for m in mentors if m.category == want] or [m for m in mentors if m.category == "GENERAL"]
    if not pool:
        return None
    chosen = min(pool, key=lambda m: m.active_load)
    chosen.active_load += 1
    req.assigned_mentor = chosen.mentor_id
    return chosen


def queue_depths(requests: list) -> dict:
    """Open-request count per routed mentor category — the war-room operations view (Part X)."""
    depths: dict = {}
    for r in requests:
        if r.resolution_state in (None, "UNRESOLVED", "ESCALATED"):
            cat = ROUTING.get(r.problem_category, "GENERAL")
            depths[cat] = depths.get(cat, 0) + 1
    return depths


# --- the confounder: operational intensity definition (Part VIII) -------------------------------
def support_intensity(duration_min: int, num_touches: int, solved_by_mentor: bool) -> str:
    """Operational, not subjective. HEAVY means the mentor effectively did the hard part.
       NONE   : no mentor touch
       LIGHT  : a single short touch (<10 min, 1 touch)
       MODERATE: repeated or longer help, team still drove
       HEAVY  : long and/or many touches AND the mentor resolved the blocker for them."""
    if num_touches == 0:
        return "NONE"
    if num_touches == 1 and duration_min < 10 and not solved_by_mentor:
        return "LIGHT"
    if solved_by_mentor and (duration_min >= 20 or num_touches >= 3):
        return "HEAVY"
    return "MODERATE"


@dataclass
class SuccessLabel:
    outcome: str            # the team's outcome (e.g. "shipped_with_product_X")
    intensity: str          # NONE | LIGHT | MODERATE | HEAVY
    vendor_assisted: bool   # was the heavy help from a company engineer for their own product?
    label: str              # ORGANIC_SUCCESS | ASSISTED_SUCCESS | VENDOR_RESCUED_SUCCESS
    caveat: str             # the honest non-causal caveat, carried with the label


def classify_success(outcome: str, intensity: str, is_company_engineer: bool) -> SuccessLabel:
    """Separate organic success from mentor-assisted success. This is a LABEL for stratified
    reporting — 'success with no help' vs 'success after heavy expert support' — NOT a causal claim.
    We never say the help caused the success; we only refuse to report them as the same thing."""
    vendor_assisted = is_company_engineer and intensity in ("MODERATE", "HEAVY")
    if intensity in ("NONE", "LIGHT"):
        label = "ORGANIC_SUCCESS"
    elif vendor_assisted:
        label = "VENDOR_RESCUED_SUCCESS"
    else:
        label = "ASSISTED_SUCCESS"
    return SuccessLabel(
        outcome, intensity, vendor_assisted, label,
        caveat="stratification only; not a causal estimate of the help's effect")
