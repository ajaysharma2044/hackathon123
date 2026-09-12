"""
Context envelope + dynamic context + opportunity set (docs/temporal/context.md; Parts III, IV, V,
XXXI, XXXII of the temporal spec).

Context is a FUNCTION OF TIME, C_i(t), not a static profile — a participant is "ORIE student, no team"
at hour 0 and "optimization owner on an AI team" at hour 7. Missing values are VALID. The opportunity
set O_i(t) (what resources/support were available when an output was produced) must be attached so an
achievement is never read without it — but O_i(t) is NEVER converted into a socioeconomic or
person-quality score. Reuses compliance for the sensitive/person-score guards.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import compliance
from temporal_core import information_set

# III. The context-envelope fields. All optional; missing is valid.
CONTEXT_FIELDS = ("EventPhase", "ProjectPhase", "TimeRemaining", "CurrentGoal", "CurrentMilestone",
                  "CurrentWorkstream", "CurrentBlocker", "RoleStructure", "CapabilityCoverage",
                  "ResourcesAvailable", "ComputeAvailable", "MentorAvailability",
                  "RecentMentorIntervention", "PeerExposure", "SponsorExposure", "ChallengeContext",
                  "PrizeContext", "CreditContext", "PhysicalZone", "ChoiceSet", "PriorAttempts",
                  "PriorToolExposure", "RelevantExperience", "PrecedingEvents", "Consent",
                  "EvidenceStatus")

# XXXII. Legitimate starting-point context — direct, relevant, NEVER socioeconomic/protected proxies.
LEGITIMATE_STARTING_CONTEXT = ("prior_relevant_coursework", "prior_project_experience",
                               "prior_tool_experience", "prior_domain_experience", "time_using_technology")

@dataclass
class ContextEnvelope:
    """C_i(t) at one instant. Every field optional; neutral_when_missing keeps absence neutral."""
    fields: dict = field(default_factory=dict)
    def get(self, name):
        if name not in CONTEXT_FIELDS:
            raise KeyError(f"unknown context field {name!r}")
        return compliance.neutral_when_missing(self.fields.get(name))
    def as_vector(self):
        return {k: compliance.neutral_when_missing(self.fields.get(k)) for k in CONTEXT_FIELDS}

def context_at(context_events, entity, as_of: datetime,
               subject=lambda e: e.subject_participant):
    """IV. Reconstruct dynamic context C_i(t): fold the entity's context-change events available by
    `as_of` (point-in-time) into the latest value per field. context_events carry payload={field:value}."""
    env = {}
    for e in sorted([e for e in information_set(context_events, as_of) if subject(e) == entity],
                    key=lambda e: e.occurred_at):
        for k, v in e.payload.items():
            if k in CONTEXT_FIELDS:
                env[k] = v
    return ContextEnvelope(env)

@dataclass
class OpportunitySet:
    """V. Resources/capabilities/support available to an actor at time t. Interpret output only WITH
    this — but never as a ranking of the person."""
    resources: set = field(default_factory=set)      # e.g. {"GPU","MENTOR_ORIE","TEAMMATE_FRAMEWORK"}
    at: datetime = None

def opportunity_at(events, entity, as_of: datetime,
                   subject=lambda e: e.subject_participant):
    """Reconstruct O_i(t): the set of GRANT/REVOKE-style resource-availability events for the entity
    available by `as_of`. payload={'resource':name,'available':bool}."""
    have = set()
    for e in sorted([e for e in information_set(events, as_of) if subject(e) == entity],
                    key=lambda e: e.occurred_at):
        r = e.payload.get("resource")
        if r is None:
            continue
        have.add(r) if e.payload.get("available", True) else have.discard(r)
    return OpportunitySet(resources=have, at=as_of)

def assert_opportunity_not_scored(obj) -> bool:
    """V/XXXII guard: refuse to collapse an OpportunitySet or starting context into a single
    'advantage'/'potential'/quality score. Achievement is read WITH opportunity, never divided by it."""
    name = str(obj).strip().lower()
    for bad in ("advantage_score", "potential_score", "opportunity_score", "quality", "socioeconomic",
                "ses", "privilege_score"):
        if bad in name:
            raise ValueError(f"{obj!r}: opportunity/context must not become a person score")
    return True

def vet_starting_context(field_names) -> bool:
    """XXXII: starting-point context may capture only direct relevant experience; reject sensitive/
    socioeconomic fields via compliance."""
    compliance.assert_no_sensitive(field_names)   # raises on age/income/class/etc.
    return True
