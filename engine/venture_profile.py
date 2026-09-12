"""
Founder/team venture profile (docs/venture/founder-team-profile.md; Parts XXX, XXXI, XXXIV-XXXVI).

Opt-in team profile for investor discovery. Every MATERIAL claim carries an epistemic status
(OBSERVED / SELF_REPORTED / ASSUMED / UNKNOWN). A weekend prototype is never presented as production
readiness (Part XXXV). Not every project is a company — this does not force startup framing (Part XXX).
Continuation (still building at 30/90 days) is a first-class signal (Part XXXVI); winning is NOT
required (winner bias avoided, Part XXXVII).
"""
from __future__ import annotations
from dataclasses import dataclass, field

CLAIM_STATUS = ("OBSERVED", "SELF_REPORTED", "ASSUMED", "UNKNOWN")


@dataclass
class VentureClaim:
    statement: str
    status: str = "UNKNOWN"
    evidence_ref: str = None

    def __post_init__(self):
        if self.status not in CLAIM_STATUS:
            raise ValueError(f"unknown claim status {self.status!r}")


@dataclass
class VentureProfile:
    venture_id: str
    team_id: str = ""
    project_id: str = ""
    problem: str = ""
    prototype_ref: str = ""
    demo_ref: str = ""
    attributes: dict = field(default_factory=dict)   # STAGE/SECTOR/TECHNICAL_DOMAIN/CAPITAL_NEED/GEOGRAPHY -> value
    claims: list = field(default_factory=list)        # VentureClaim
    investor_visible: bool = False                     # explicit INVESTOR opt-in
    continuation_status: str = "UNKNOWN"               # CONTINUED | STOPPED | PIVOTED | STARTUP_FORMED | UNKNOWN
    is_company: bool = False                            # not every project is a company

    def material_claims_ok(self) -> bool:
        """Every material claim must carry a status (never a bare assertion)."""
        return all(c.status in CLAIM_STATUS for c in self.claims)

    def diligence_note(self) -> str:
        """The mandatory limitation note (Part XXXV)."""
        return ("Artifacts are weekend-prototype evidence, not production readiness. Observed vs "
                "self-reported vs assumed vs unknown are tagged per claim; treat unknowns as unknown.")
