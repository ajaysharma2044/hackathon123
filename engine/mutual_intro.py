"""
Mutual-opt-in introduction flow + transaction liquidity (docs/talent/transaction-flow.md,
docs/venture/transaction-flow.md; Parts XX-XXI, XXXIX, LXI).

An employer/investor can express interest, but NO contact information is disclosed until BOTH sides
opt in. The participant/team always controls the introduction. This module also tracks funnel
liquidity honestly: an introduction is NOT a successful transaction (Part LXI).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import compliance

# Talent funnel (Part XX) and venture funnel (Part XXXIX), as ordered stages.
TALENT_FUNNEL = ["NEED", "SEARCH", "PACKET_VIEWED", "PARTICIPANT_INTEREST", "MUTUAL_OPT_IN",
                 "INTRODUCTION", "INTERVIEW", "OFFER", "HIRE"]
VENTURE_FUNNEL = ["THESIS", "DISCOVERY", "PACKET_VIEWED", "INVESTOR_INTEREST", "MUTUAL_OPT_IN",
                  "INTRODUCTION", "MEETING", "FOLLOW_ON"]


@dataclass
class IntroRequest:
    scope: str                     # EMPLOYER | INVESTOR | DESIGN_PARTNER | ...
    counterparty: str              # company/fund id (soft ref)
    subject_id: str                # participant_id or venture_id
    counterparty_opted_in: bool = True     # the requester expressed interest
    subject_opted_in: bool = False         # the participant/team has NOT yet accepted
    subject_visible: bool = False          # subject opted this scope visible at all

    def __post_init__(self):
        if self.scope not in compliance.VISIBILITY_SCOPES:
            raise ValueError(f"unknown scope {self.scope!r}")

    @property
    def both_opted_in(self) -> bool:
        return self.counterparty_opted_in and self.subject_opted_in and self.subject_visible

    def contact_releasable(self) -> bool:
        """Contact details may be released ONLY on mutual opt-in. No exceptions, no scraping."""
        return self.both_opted_in

    def accept(self):
        """The subject (participant/team) accepts the introduction."""
        self.subject_opted_in = True
        return self

    def decline(self):
        self.subject_opted_in = False
        return self


def release_contact(req: IntroRequest, contact: str):
    """Return the contact ONLY if both sides opted in; otherwise raise. This is the single choke point
    that prevents any contact disclosure without mutual consent."""
    if not req.contact_releasable():
        raise PermissionError("Contact cannot be released without mutual opt-in (both sides + subject "
                              "made this scope visible).")
    return contact


def funnel_liquidity(counts: dict, kind="talent") -> dict:
    """Report conversion across the funnel WITHOUT equating an introduction with a transaction.
    counts: {stage: n}. Returns per-stage counts + the honest caveat."""
    stages = TALENT_FUNNEL if kind == "talent" else VENTURE_FUNNEL
    report = {s: counts.get(s, 0) for s in stages}
    report["_note"] = ("An introduction is not a hire/deal. Downstream stages are only recorded when "
                       "the participant/team voluntarily shares the outcome.")
    return report
