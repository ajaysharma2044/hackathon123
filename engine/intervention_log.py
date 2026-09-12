"""
The event-adaptation log (docs/research-ops/event-adaptation.md, Parts XV–XVI).

The event SHOULD adapt when the evidence says so — add database mentors when twelve teams are stuck,
clarify a misread challenge, open office hours. But every material change must be logged WITH its
validity impact, so we never forget the environment changed under a running study.

Invariants enforced here:
  1. EVERY INTERVENTION IS TIMESTAMPED. Construction without `occurred_at` fails.
  2. THE STUDY SPINE IS PROTECTED. An INVALIDATING change (a pre-registered treatment, primary
     outcome, or stopping rule) is refused unless it was pre-specified before the event.
  3. BEFORE/AFTER IS RECOVERABLE. For any affected research question, `split_point` returns the
     timestamp that divides the pre- and post-intervention populations, so analysis can condition
     on it instead of pretending the change never happened.

What may adapt freely vs what is locked is encoded in ADAPTABLE / LOCKED below.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

NONE, OPERATIONAL, CONFOUNDING, INVALIDATING = "NONE", "OPERATIONAL", "CONFOUNDING", "INVALIDATING"

# Part XVI — what can change without research-control discipline vs what is locked mid-study.
ADAPTABLE = frozenset({
    "mentor_allocation", "office_hours", "clarify_instructions", "operational_support",
    "food_logistics", "research_interview_targets", "question_backlog", "research_sampling",
})
LOCKED = frozenset({            # changing these mid-study invalidates it unless pre-specified
    "core_randomized_treatment", "product_exposure_assignment", "credit_amount", "challenge_rules",
    "evaluation_metric", "primary_outcome", "stopping_rule", "study_definition",
})


class ValidityViolation(Exception):
    pass


@dataclass
class Intervention:
    intervention_id: str
    occurred_at: datetime                 # INVARIANT 1 — always timestamped
    reason: str
    evidence: str                         # what signal prompted it
    affected_population: str
    change: str
    target: str                           # the knob being turned (checked against ADAPTABLE/LOCKED)
    validity_impact: str = OPERATIONAL
    research_questions_affected: tuple = ()
    expected_effect: str = ""
    pre_specified: bool = False           # was this change written into the protocol in advance?
    reversible: bool = True

    def __post_init__(self):
        if not isinstance(self.occurred_at, datetime):
            raise ValueError("an intervention must carry a concrete occurred_at timestamp")
        if self.validity_impact not in (NONE, OPERATIONAL, CONFOUNDING, INVALIDATING):
            raise ValueError(f"bad validity_impact {self.validity_impact}")


class InterventionLog:
    def __init__(self):
        self._log: list = []

    def log(self, iv: Intervention) -> Intervention:
        """Record an intervention, refusing a LOCKED-knob change that was not pre-specified."""
        if iv.target in LOCKED and not iv.pre_specified:
            raise ValidityViolation(
                f"'{iv.target}' is part of the study spine; changing it mid-event invalidates the "
                f"study unless pre-specified (event-adaptation.md Part XVI). Intervention refused.")
        if iv.target in LOCKED and iv.pre_specified and iv.validity_impact != INVALIDATING:
            # a pre-specified spine change is at least confounding; don't let it be mislabeled NONE
            iv.validity_impact = INVALIDATING
        self._log.append(iv)
        return iv

    def split_point(self, question_id: str) -> Optional[datetime]:
        """The earliest intervention time affecting this question — the before/after boundary."""
        times = [iv.occurred_at for iv in self._log if question_id in iv.research_questions_affected]
        return min(times) if times else None

    def affecting(self, question_id: str) -> list:
        return [iv for iv in self._log if question_id in iv.research_questions_affected]

    def all(self) -> list:
        return sorted(self._log, key=lambda iv: iv.occurred_at)
