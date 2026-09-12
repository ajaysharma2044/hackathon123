"""
The evidence graph (docs/research-ops/evidence-graph.md, Parts XXV–XXVII).

Every client-facing claim must trace back to evidence — and must enumerate the evidence AGAINST it,
not only the evidence for it. This is the structural defence against confirmation bias and against an
LLM silently converting raw comments into facts.

A Claim carries signed evidence (SUPPORTS / CONTRADICTS) and a record of whether a deliberate
negative-case search was performed. The gate `can_promote` refuses to turn a Claim into a published
Finding unless:
  1. it has at least one supporting evidence item, AND
  2. a disconfirmation search was actually run (a NegativeCase was recorded — found or not), AND
  3. if contradictory evidence exists, confidence has been lowered to reflect it.

`trace` returns the full provenance so any claim remains auditable end to end:
    RawQuote → Observation → Code → Theme → Claim → (Finding) → Recommendation
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

SUPPORTS, CONTRADICTS = "SUPPORTS", "CONTRADICTS"
LOW, MED, HIGH = "LOW", "MED", "HIGH"
_ORDER = {LOW: 0, MED: 1, HIGH: 2}


@dataclass
class EvidenceRef:
    polarity: str          # SUPPORTS | CONTRADICTS
    ref_kind: str          # observation | evidence_event | interview_excerpt | mentor_interaction
    ref_id: str
    note: str = ""


@dataclass
class NegativeCase:
    disconfirming_question: str     # "what evidence would make this explanation wrong?"
    searched_segment: str
    found: Optional[bool] = None    # None = search still open; True = a counterexample exists


@dataclass
class Claim:
    claim_id: str
    statement: str
    interpretation: str = ""
    confidence: str = LOW
    status: str = "PROPOSED"                 # PROPOSED | SUPPORTED | CONTRADICTED | RETIRED
    evidence: list = field(default_factory=list)      # list[EvidenceRef]
    negative_cases: list = field(default_factory=list)  # list[NegativeCase]

    def add_evidence(self, ref: EvidenceRef):
        self.evidence.append(ref)
        # A contradicting item can never leave the claim at HIGH without an explicit re-justification.
        if ref.polarity == CONTRADICTS and _ORDER[self.confidence] > _ORDER[MED]:
            self.confidence = MED

    def supporting(self):   return [e for e in self.evidence if e.polarity == SUPPORTS]
    def contradicting(self): return [e for e in self.evidence if e.polarity == CONTRADICTS]

    def disconfirmation_searched(self) -> bool:
        """True once at least one negative-case search has actually been carried out (resolved)."""
        return any(nc.found is not None for nc in self.negative_cases)

    def can_promote(self) -> tuple:
        """May this Claim become a published Finding? Returns (ok, reason)."""
        if not self.supporting():
            return False, "no supporting evidence"
        if not self.negative_cases:
            return False, "no negative-case search was even planned (confirmation-bias guard)"
        if not self.disconfirmation_searched():
            return False, "negative-case search is still open — run it before promoting"
        # If a counterexample was found, the claim must not be promoted at HIGH.
        if any(nc.found for nc in self.negative_cases) and self.confidence == HIGH:
            return False, "a disconfirming case exists but confidence is still HIGH — lower it first"
        return True, "ok"

    def trace(self) -> dict:
        """Full provenance for auditing — supporting, contradicting, and the disconfirmation search."""
        return {
            "claim": self.statement,
            "confidence": self.confidence,
            "supporting": [(e.ref_kind, e.ref_id) for e in self.supporting()],
            "contradicting": [(e.ref_kind, e.ref_id) for e in self.contradicting()],
            "negative_cases": [(nc.searched_segment, nc.found) for nc in self.negative_cases],
        }


@dataclass
class Recommendation:
    text: str
    decision_implication: str
    claim_id: Optional[str] = None
    finding_id: Optional[str] = None
    confidence: str = LOW

    def __post_init__(self):
        if self.claim_id is None and self.finding_id is None:
            raise ValueError("a recommendation must rest on a Claim or a Finding — never free-floating")
