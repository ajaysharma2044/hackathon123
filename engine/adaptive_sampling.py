"""
Adaptive sampling (docs/research-ops/adaptive-sampling.md).

We do not pre-select every interview. Who we talk to next is driven by the live evidence: which
open question has the biggest gap, which segment is uncovered, and — critically — which active
explanation has NOT yet been tested against a disconfirming case.

Two properties are enforced, not just hoped for:
  1. NEGATIVE-CASE PRESERVATION (anti-confirmation-bias). For every live explanation the system is
     forming, the sampler will insist on scheduling a disconfirming segment before it lets the
     explanation accumulate only-confirming evidence. (Part XIII)
  2. BURDEN-AWARE, NOT EXTRACTIVE. The sampler skips participants who are over budget or in a
     DO_NOT_INTERRUPT window, and prefers lightly-burdened, available subjects. It never optimises
     for extracting the most from one person. (Part XII/XVII)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable

# Sampling segments (Part XII). Each explanation implies a confirming and a disconfirming segment.
SEGMENTS = (
    "ADOPTER", "NON_ADOPTER", "CHOOSER", "NON_CHOOSER", "SWITCHER", "NON_SWITCHER", "ABANDONER",
    "SUCCESSFUL_TEAM", "FAILED_TEAM", "HIGH_MENTOR_SUPPORT", "LOW_MENTOR_SUPPORT",
    "UNEXPECTED_USE_CASE", "COMMON_USE_CASE", "OUTLIER", "RD_WINNER", "RD_FAILURE",
    "RD_CONVERGENT", "RD_DIVERGENT",
)

# For an explanation, the segment that would CONFIRM it vs the one that could FALSIFY it.
# e.g. "auth friction causes abandonment": confirm with ABANDONER (had auth friction), falsify by
# looking for NON_SWITCHER who ALSO hit auth friction but stayed, or ABANDONER with no auth friction.
DISCONFIRMING = {
    "ADOPTER": "NON_ADOPTER", "SWITCHER": "NON_SWITCHER", "ABANDONER": "SUCCESSFUL_TEAM",
    "SUCCESSFUL_TEAM": "FAILED_TEAM", "HIGH_MENTOR_SUPPORT": "LOW_MENTOR_SUPPORT",
    "UNEXPECTED_USE_CASE": "COMMON_USE_CASE", "RD_WINNER": "RD_FAILURE", "CHOOSER": "NON_CHOOSER",
}


@dataclass
class Candidate:
    participant_id: str
    team_id: str
    segments: frozenset            # which segments this candidate belongs to
    available: bool = True         # interrupt window allows a short interview
    interviewed: bool = False


@dataclass
class Explanation:
    """A live hypothesis the research is forming (mirrors evidence_graph.Claim, but for sampling)."""
    text: str
    confirming_segment: str
    confirming_n: int = 0          # interviews gathered that could confirm
    disconfirming_n: int = 0       # interviews gathered that could falsify (negative cases)
    target_each: int = 3           # how many of each before we consider it tested


@dataclass
class SamplePlan:
    participant_id: str
    segment: str
    reason: str                    # why THIS person now — always explicit
    polarity: str                  # CONFIRM | DISCONFIRM | COVERAGE


class Sampler:
    def __init__(self, burden, now, interrupt_ok: Callable = None):
        self.burden = burden                       # BurdenBudget
        self.now = now
        self.interrupt_ok = interrupt_ok or (lambda pid: True)

    def _eligible(self, c: Candidate) -> bool:
        return (c.available and not c.interviewed and self.interrupt_ok(c.participant_id)
                and not self.burden.is_over_half(c.participant_id))

    def suggest_next(self, explanations: list, candidates: list,
                     coverage_gaps: list = None) -> Optional[SamplePlan]:
        """Pick the single highest-value next interview.

        Priority order:
          1. NEGATIVE CASES FIRST — any live explanation short of its disconfirming quota pulls a
             disconfirming candidate, so an explanation never hardens on confirming evidence alone.
          2. then fill confirming evidence for under-tested explanations,
          3. then close a coverage gap (a segment with no data yet).
        Always burden- and availability-aware; returns None if nothing is appropriate right now."""
        coverage_gaps = coverage_gaps or []

        # 1. disconfirmation deficit — the anti-confirmation-bias guarantee
        for ex in explanations:
            if ex.disconfirming_n < ex.target_each:
                seg = DISCONFIRMING.get(ex.confirming_segment)
                pick = self._pick(candidates, seg)
                if pick:
                    return SamplePlan(pick.participant_id, seg,
                                      f"seek a case that could FALSIFY: '{ex.text}'", "DISCONFIRM")

        # 2. confirming deficit
        for ex in explanations:
            if ex.confirming_n < ex.target_each:
                pick = self._pick(candidates, ex.confirming_segment)
                if pick:
                    return SamplePlan(pick.participant_id, ex.confirming_segment,
                                      f"add evidence on: '{ex.text}'", "CONFIRM")

        # 3. coverage gaps
        for seg in coverage_gaps:
            pick = self._pick(candidates, seg)
            if pick:
                return SamplePlan(pick.participant_id, seg, f"uncovered segment: {seg}", "COVERAGE")
        return None

    def _pick(self, candidates: list, segment: Optional[str]) -> Optional[Candidate]:
        if segment is None:
            return None
        for c in candidates:
            if segment in c.segments and self._eligible(c):
                return c
        return None
