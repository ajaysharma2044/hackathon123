"""
Shared compliance guardrails for the talent + venture markets (docs/talent/legal-policy.md,
docs/venture/legal-policy.md; Parts I, IV, XXVI, XLIX, L, LI, LXXIV).

These are the invariants the whole opportunity layer is built to preserve, centralized so every
module imports the SAME definitions and the guardrail test-suite can assert them once:

- THREE data levels stay separate (A event-ops / B aggregate research / C opt-in professional).
- NO person scores of any kind (hireability, founder-quality, personality, intelligence, ...).
- NO protected/sensitive attribute is ever collected, inferred, or used to rank/exclude.
- Missing evidence is NEVER negative (missing != bad; no-activity != inability).
- Individual professional disclosure requires an explicit, per-scope opt-in.
"""
from __future__ import annotations

# Data levels (Part I) — kept separate; C requires explicit per-scope opt-in.
DATA_LEVELS = ("A_EVENT_OPERATIONS", "B_AGGREGATE_RESEARCH", "C_OPT_IN_PROFESSIONAL")

# Independent opt-in visibility scopes (Part LI). None implies another.
VISIBILITY_SCOPES = ("EMPLOYER", "INVESTOR", "DESIGN_PARTNER", "PAID_PROJECT", "PUBLIC_PORTFOLIO")

# Evidence source kinds (Part XLIX) — stored separately, NOT auto-collapsed into a score.
EVIDENCE_SOURCE_KINDS = ("SELF_REPORTED", "TEAM_CONFIRMED", "ARTIFACT_OBSERVED", "PUBLIC_REPO",
                         "PAID_CONTINUATION", "LONGITUDINAL_OBSERVED")

# Protected / sensitive attributes — never collected, inferred, or used (Parts XXVI, LXXIV).
SENSITIVE_ATTRIBUTES = frozenset({
    "race", "ethnicity", "color", "national_origin", "nationality", "citizenship",
    "gender", "sex", "sexual_orientation", "gender_identity",
    "religion", "creed", "political", "politics",
    "disability", "medical", "health", "mental_health", "genetic",
    "family", "marital_status", "pregnancy", "children", "caregiver",
    "age", "date_of_birth", "veteran_status", "socioeconomic", "income", "class",
})

# Person-score concepts that must never be produced (Parts IV, XXVI, XXIX, LXXIV).
FORBIDDEN_SCORES = frozenset({
    "hireability", "hireability_score", "employability", "employability_score",
    "founder_quality", "founder_score", "personality", "personality_score",
    "intelligence", "intelligence_score", "iq", "person_quality", "quality_score",
    "candidate_score", "overall_candidate_score", "grit", "coachability",
})


def assert_no_sensitive(field_names) -> bool:
    """Raise if any field name is (or contains) a sensitive attribute. Used to vet profile/job schemas
    before they are accepted."""
    for f in field_names:
        key = str(f).strip().lower()
        if key in SENSITIVE_ATTRIBUTES or any(s in key for s in SENSITIVE_ATTRIBUTES):
            raise ValueError(f"Sensitive attribute {f!r} may never be collected, inferred, or used.")
    return True


def assert_not_a_person_score(name: str) -> bool:
    """Raise if `name` looks like a forbidden person score. The system produces decomposed, explainable
    evidence matches — never a single opaque candidate/founder score."""
    key = str(name).strip().lower().replace(" ", "_")
    if key in FORBIDDEN_SCORES or any(bad in key for bad in ("hireab", "employab", "founder_q",
                                                             "personality", "intelligence", "person_quality")):
        raise ValueError(f"{name!r} is a forbidden person score — never compute or expose it.")
    return True


def neutral_when_missing(value):
    """Missing evidence is neutral, never negative (Part L). Returns 'UNKNOWN' for missing input so no
    downstream code can treat absence as a penalty."""
    if value is None or value == "" or value == []:
        return "UNKNOWN"
    return value


def individual_disclosure_allowed(visibility: dict, scope: str) -> bool:
    """Level-C gate: an individual may be exposed to a scope ONLY with an explicit, non-revoked opt-in
    for that exact scope. Absence defaults to not visible."""
    if scope not in VISIBILITY_SCOPES:
        raise ValueError(f"unknown visibility scope {scope!r}")
    return bool(visibility.get(scope, False))
