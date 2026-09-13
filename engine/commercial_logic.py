"""Commercial semantics and hard gates used by discovery agents.

Separates cash, in-kind face value and actual avoided cost; prevents comparable prices from being
mislabelled as observed WTP; and rejects commercially attractive mechanics that harm the hackathon.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class WTPStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    PRIMARY_VALIDATION_REQUIRED = "PRIMARY_VALIDATION_REQUIRED"
    COMPARABLE = "COMPARABLE"
    DECISION_HYPOTHESIS = "DECISION_HYPOTHESIS"
    OBSERVED = "OBSERVED"

PRIMARY_WTP_EVIDENCE = {"buyer_statement", "signed_loi", "paid_pilot", "signed_sponsorship", "signed_contract"}


@dataclass(frozen=True)
class ValueBundle:
    cash: float = 0.0
    in_kind_face_value: float = 0.0
    actual_cost_avoided: float = 0.0

    def __post_init__(self):
        if min(self.cash, self.in_kind_face_value, self.actual_cost_avoided) < 0:
            raise ValueError("value components cannot be negative")
        if self.actual_cost_avoided > self.in_kind_face_value and self.in_kind_face_value > 0:
            raise ValueError("avoided cost cannot exceed the supplied in-kind face value")


@dataclass(frozen=True)
class PriceEvidence:
    amount: float | None
    status: WTPStatus
    evidence_kind: str | None = None

    def __post_init__(self):
        if self.status == WTPStatus.OBSERVED and self.evidence_kind not in PRIMARY_WTP_EVIDENCE:
            raise ValueError("Observed WTP requires primary buyer/contract evidence")
        if self.status == WTPStatus.UNKNOWN and self.amount is not None:
            raise ValueError("UNKNOWN WTP cannot silently become numeric")


@dataclass(frozen=True)
class Mechanic:
    name: str
    natural_without_payment: bool
    participant_burden: str
    research_contamination: bool = False
    privacy_ok: bool = True
    consent_ok: bool = True

    def admissible(self) -> tuple[bool, str]:
        if not self.natural_without_payment:
            return False, "ARTIFICIAL_ACTIVITY"
        if self.participant_burden.upper() == "HIGH":
            return False, "PARTICIPANT_HARM"
        if self.research_contamination:
            return False, "RESEARCH_CONTAMINATION"
        if not self.privacy_ok or not self.consent_ok:
            return False, "PRIVACY_OR_CONSENT"
        return True, "ADMISSIBLE"


@dataclass(frozen=True)
class ThemeGate:
    teams_can_parallelize: bool
    feasible_48h: bool
    demoable: bool
    student_appeal: bool
    substitute_parity: bool
    anchor_product_exists: bool

    def result(self) -> tuple[bool, list[str]]:
        failures = []
        if not self.teams_can_parallelize:
            failures.append("NO_PARALLEL_SEARCH")
        if not self.feasible_48h:
            failures.append("NOT_48H_FEASIBLE")
        if not self.demoable:
            failures.append("NOT_DEMOABLE")
        if not self.student_appeal:
            failures.append("LOW_PARTICIPANT_APPEAL")
        if self.substitute_parity:
            failures.append("SUBSTITUTE_PARITY")
        if not self.anchor_product_exists:
            failures.append("NO_ANCHOR_PRODUCT")
        return (not failures, failures)
