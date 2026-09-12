"""
Work-evidence graph (docs/talent/work-evidence-graph.md; Parts II-XI).

A hackathon produces work evidence a resume cannot. This models that evidence as a traceable GRAPH —
never a hidden person score. Role ownership is DECLARED by the team and CONFIRMED by the participant,
never inferred from commit counts (Part XI). Every claim renders as evidence-with-provenance, never a
psychological judgement (Part IV).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import compliance

EVIDENCE_TYPES = (
    "ROLE_OWNERSHIP", "PROJECT_ARTIFACT", "CODE_ARTIFACT", "DESIGN_ARTIFACT", "MODEL_ARTIFACT",
    "DATA_ARTIFACT", "OPTIMIZATION_ARTIFACT", "HARDWARE_ARTIFACT", "DOCUMENTATION", "DEMO",
    "TECHNICAL_DECISION", "EXPERIMENT", "BENCHMARK", "PROBLEM_DOMAIN", "TOOL_EXPERIENCE",
    "TEAM_SELECTED_CONTRIBUTION", "SELF_REPORTED_CONTRIBUTION", "CONTINUATION", "PAID_CONTINUATION",
    "OPEN_SOURCE_CONTRIBUTION",
)

# Metrics that must NEVER be used to rank contribution (Part XI). Named so the guardrail tests can
# assert the system exposes no ranking over them.
FORBIDDEN_CONTRIBUTION_METRICS = ("lines_of_code", "commit_count", "hours_online", "mentor_requests")


@dataclass
class ProjectRole:
    """Opt-in ownership record (Part X). Only counts once the participant confirms their own record."""
    participant_id: str
    project_id: str
    workstream: str                       # BACKEND | MODEL | FRONTEND | PRODUCT | HARDWARE | ...
    declared_by_team: bool = False
    confirmed_by_participant: bool = False

    @property
    def is_valid(self) -> bool:
        return self.declared_by_team and self.confirmed_by_participant


@dataclass
class WorkEvidence:
    evidence_id: str
    type: str                             # one of EVIDENCE_TYPES
    source_kind: str                      # one of compliance.EVIDENCE_SOURCE_KINDS
    participant_id: str = None
    team_id: str = None
    project_id: str = None
    artifact_ref: str = None
    verification_method: str = None
    consent_scope: tuple = ()             # visibility scopes that expose this (empty = level A/B only)
    data_level: str = "A_EVENT_OPERATIONS"
    confidence: float = 0.5
    is_public: bool = False
    participant_confirmed: bool = False

    def __post_init__(self):
        if self.type not in EVIDENCE_TYPES:
            raise ValueError(f"unknown evidence type {self.type!r}")
        if self.source_kind not in compliance.EVIDENCE_SOURCE_KINDS:
            raise ValueError(f"unknown source kind {self.source_kind!r}")

    def visible_to(self, scope: str) -> bool:
        """Level-C exposure: visible to a scope only if it is C-level AND that scope was opted in."""
        return self.data_level == "C_OPT_IN_PROFESSIONAL" and scope in self.consent_scope


def render_claim(ev: WorkEvidence, participant_label: str, detail: str) -> str:
    """Render evidence as an evidence-with-provenance statement, NOT a trait judgement (Part IV).
    Good:  'X opted to disclose they owned the backend workstream; the repo contains <detail>.'
    Never: 'X is an excellent backend engineer.'"""
    verb = {"SELF_REPORTED": "states", "TEAM_CONFIRMED": "was recorded by the team as",
            "ARTIFACT_OBSERVED": "has an artifact showing", "PUBLIC_REPO": "has a public repo showing",
            "PAID_CONTINUATION": "was engaged for paid continuation involving",
            "LONGITUDINAL_OBSERVED": "was observed at follow-up to have"}.get(ev.source_kind, "discloses")
    return (f"{participant_label} opted to disclose {ev.type.replace('_', ' ').lower()}; "
            f"{participant_label} {verb} {detail}.")


def evidence_for_scope(evidence_list, scope: str) -> list:
    """Only the evidence a participant opted into exposing for this scope. Missing evidence simply is
    not returned — it is NEVER converted into a negative signal (Part L)."""
    if scope not in compliance.VISIBILITY_SCOPES:
        raise ValueError(f"unknown scope {scope!r}")
    return [e for e in evidence_list if e.visible_to(scope)]


def contribution_summary(roles, evidence_list) -> dict:
    """Summarize a participant's contribution from CONFIRMED roles + evidence — explicitly refusing to
    rank by any forbidden metric (Part XI). Returns role ownership + evidence types, never a score."""
    valid_roles = [r.workstream for r in roles if r.is_valid]
    types = sorted({e.type for e in evidence_list})
    return {
        "confirmed_workstreams": valid_roles,       # empty is fine — missing != bad
        "evidence_types_present": types,
        "note": "Contribution is described by confirmed role ownership + artifacts, never ranked by "
                "lines of code, commits, hours online, or mentor requests.",
    }
