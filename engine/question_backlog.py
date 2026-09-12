"""
The live research question backlog (docs/research-ops/analytic-memos.md, Part XI).

A research question is not fixed at event start. New questions EMERGE from the evidence ("why do
experienced users ignore the starter templates?") and old ones saturate or get contradicted. This
is a dynamic priority queue with a disciplined lifecycle so the war room always knows what to chase
next and what is already answered enough.

Lifecycle:
    OPEN → PRIORITIZED → ANSWERED_PARTIALLY → SATURATED
                     ↘ DEPRIORITIZED
    any → CONTRADICTED  (new evidence undercuts a prior answer; reopens attention)

Rules enforced:
  * SATURATED/DEPRIORITIZED questions stop consuming sampling priority — but CONTRADICTED evidence
    can reopen a saturated question (saturation is provisional, not permanent).
  * Emergent questions are first-class and carry their emergence time, so the final report can show
    which questions the event itself surfaced.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

OPEN, PRIORITIZED, ANSWERED_PARTIALLY, SATURATED, DEPRIORITIZED, CONTRADICTED = (
    "OPEN", "PRIORITIZED", "ANSWERED_PARTIALLY", "SATURATED", "DEPRIORITIZED", "CONTRADICTED")

ACTIVE = frozenset({OPEN, PRIORITIZED, ANSWERED_PARTIALLY, CONTRADICTED})  # still worth sampling toward
# Legal transitions. Saturation is reopenable via CONTRADICTED; that is the only way back.
_TRANSITIONS = {
    OPEN: {PRIORITIZED, DEPRIORITIZED, ANSWERED_PARTIALLY, CONTRADICTED},
    PRIORITIZED: {ANSWERED_PARTIALLY, SATURATED, DEPRIORITIZED, CONTRADICTED},
    ANSWERED_PARTIALLY: {SATURATED, PRIORITIZED, CONTRADICTED, DEPRIORITIZED},
    SATURATED: {CONTRADICTED},
    DEPRIORITIZED: {PRIORITIZED, OPEN, CONTRADICTED},
    CONTRADICTED: {PRIORITIZED, ANSWERED_PARTIALLY, OPEN},
}


@dataclass
class QItem:
    question_id: str
    text: str
    client: str = ""
    engine: str = ""
    priority: int = 0
    status: str = OPEN
    is_emergent: bool = False
    emerged_at: datetime = None
    evidence_needed: str = ""
    sample_needed: str = ""


class Backlog:
    def __init__(self):
        self.items: dict = {}

    def add(self, item: QItem):
        self.items[item.question_id] = item
        return item

    def add_emergent(self, question_id, text, now, priority=1, **kw):
        """A question the evidence surfaced mid-event."""
        return self.add(QItem(question_id, text, priority=priority, status=PRIORITIZED,
                              is_emergent=True, emerged_at=now, **kw))

    def transition(self, question_id, to_status):
        it = self.items[question_id]
        if to_status not in _TRANSITIONS[it.status]:
            raise ValueError(f"illegal transition {it.status} -> {to_status} for {question_id}")
        it.status = to_status
        return it

    def contradict(self, question_id):
        """New evidence undercuts this question's prior answer — reopen it for attention."""
        it = self.items[question_id]
        it.status = CONTRADICTED           # always legal: a finding can be contradicted from any state
        it.priority = max(it.priority, 2)  # bump it up; a contradiction is high-signal
        return it

    def top(self, n: int = 5) -> list:
        """The next questions to chase: active only, highest priority first."""
        active = [it for it in self.items.values() if it.status in ACTIVE]
        return sorted(active, key=lambda it: (-it.priority, it.question_id))[:n]

    def emergent(self) -> list:
        return sorted((it for it in self.items.values() if it.is_emergent),
                      key=lambda it: it.emerged_at or datetime.min)
