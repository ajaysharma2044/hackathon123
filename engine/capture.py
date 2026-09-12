"""
Reference implementation of the two hardest correctness properties in the capture system:

  1. POINT-IN-TIME CORRECTNESS  — an "as of D" query may only use evidence that was available
     (available_at <= D); retention/survival runs on occurred_at, never observed_at, so
     survey-lag does not corrupt time-to-event.  (docs/research-data-model.md, "three clocks")

  2. CONSENT ENFORCED AT QUERY TIME — visibility for a purpose is resolved from the append-only
     consent ledger as-of query time, so a revocation takes effect without deleting anything;
     AGGREGATE_RESEARCH is aggregate-only (min cell size), and only the *_DISCOVERABILITY scopes
     may ever produce individual-grain output.  (docs/capture-system.md, Part 7)

Pure stdlib, no external deps. This is a reference/enforcement kernel, not a production store —
it exists so the invariants are executable and testable (engine/test_capture.py), not asserted
only in prose. Fabricating a real sponsor integration would be worse than this honest stub.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Optional

# --- consent taxonomy (mirrors schema/001_core.sql) ---------------------------------------------
ALL_SCOPES = {
    "CORE_EVENT", "AGGREGATE_RESEARCH", "PRODUCT_TELEMETRY", "QUALITATIVE_RESEARCH",
    "LONGITUDINAL_FOLLOWUP", "RECRUITING_DISCOVERABILITY", "VC_DISCOVERABILITY",
    "DESIGN_PARTNER_DISCOVERABILITY", "PUBLIC_MEDIA", "ANONYMIZED_PUBLICATION", "LONGITUDINAL_LINKAGE",
}
# The ONLY scopes that may yield individual-grain output to an external party:
INDIVIDUAL_DISCLOSURE_OK = {
    "RECRUITING_DISCOVERABILITY", "VC_DISCOVERABILITY", "DESIGN_PARTNER_DISCOVERABILITY",
}
# Aggregate-only scopes: never individual grain to a sponsor.
AGGREGATE_ONLY = {"AGGREGATE_RESEARCH", "ANONYMIZED_PUBLICATION"}
DEFAULT_MIN_CELL = 8   # min-cell-size suppression (docs/data-model.md "aggregate-only has teeth")


@dataclass(frozen=True)
class EvidenceEvent:
    event_id: str
    event_type: str
    subject_participant: Optional[str]
    occurred_at: datetime          # VALID time — when the behavior happened
    observed_at: datetime          # when first recorded (may be >> occurred_at for self-report)
    available_at: datetime         # TRANSACTION time — when queryable; drives "as of D"
    consent_scope: frozenset       # scope(s) this was collected under
    is_self_report: bool
    product_id: Optional[str] = None
    confidence: float = 1.0
    superseded_by: Optional[str] = None
    payload: dict = field(default_factory=dict)

    def __post_init__(self):
        assert self.occurred_at <= self.available_at, "occurred_at must be <= available_at"
        assert 0.0 <= self.confidence <= 1.0


@dataclass(frozen=True)
class ConsentRecord:
    participant_id: str
    scope: str
    action: str                    # "GRANT" | "REVOKE"
    effective_at: datetime         # when the participant's choice takes effect


class ConsentLedger:
    """Append-only. Effective consent is computed as-of a query time, so revocation takes effect
    on the next query with no deletion."""
    def __init__(self):
        self._records: list[ConsentRecord] = []

    def record(self, r: ConsentRecord):
        assert r.scope in ALL_SCOPES, f"unknown scope {r.scope}"
        assert r.action in ("GRANT", "REVOKE")
        self._records.append(r)

    def effective(self, participant_id: str, scope: str, as_of: datetime) -> bool:
        """Latest GRANT/REVOKE for (participant, scope) with effective_at <= as_of wins."""
        latest = None
        for r in self._records:
            if r.participant_id == participant_id and r.scope == scope and r.effective_at <= as_of:
                if latest is None or r.effective_at >= latest.effective_at:
                    latest = r
        return latest is not None and latest.action == "GRANT"


class CaptureStore:
    def __init__(self, ledger: ConsentLedger):
        self.ledger = ledger
        self._events: list[EvidenceEvent] = []

    def append(self, e: EvidenceEvent):
        self._events.append(e)          # immutable, append-only; corrections use superseded_by

    # --- the query gate: point-in-time + consent, together -------------------------------------
    def query(self, purpose: str, as_of: datetime, include_superseded: bool = False
              ) -> list[EvidenceEvent]:
        """Return events usable for `purpose` as-of `as_of`.
        Enforces: (a) available_at <= as_of  (no future knowledge leaks backward);
                  (b) the row was collected under a scope covering `purpose`;
                  (c) the participant's effective consent for `purpose` at `as_of` is GRANT
                      (revocation enforced here, at query time, not by deletion)."""
        assert purpose in ALL_SCOPES, f"unknown purpose {purpose}"
        out = []
        for e in self._events:
            if e.available_at > as_of:                         # (a) point-in-time
                continue
            if not include_superseded and e.superseded_by is not None:
                continue
            if purpose not in e.consent_scope:                 # (b) collected under this scope
                continue
            if e.subject_participant is not None and not self.ledger.effective(
                    e.subject_participant, purpose, as_of):    # (c) still consented at query time
                continue
            out.append(e)
        return out

    def individual_disclosure(self, purpose: str, as_of: datetime) -> list[EvidenceEvent]:
        """Individual-grain output to an external party. Allowed ONLY for the *_DISCOVERABILITY
        scopes; refused for aggregate-only scopes even if rows exist."""
        if purpose not in INDIVIDUAL_DISCLOSURE_OK:
            raise PermissionError(
                f"{purpose} may not produce individual-grain output; it is aggregate-only")
        return self.query(purpose, as_of)

    def aggregate(self, purpose: str, as_of: datetime, cell_key,
                  min_cell: int = DEFAULT_MIN_CELL) -> dict:
        """Aggregate counts by cell_key(event)->cell, suppressing cells with distinct-participant
        n < min_cell. Refuses to run for a scope that permits only individual disclosure? No — any
        scope can be aggregated; the point is aggregate is the ONLY sponsor output for AGGREGATE_ONLY.
        Returns {cell: n} with small cells replaced by None (suppressed)."""
        counts: dict = {}
        for e in self.query(purpose, as_of):
            cell = cell_key(e)
            counts.setdefault(cell, set()).add(e.subject_participant)
        return {c: (len(s) if len(s) >= min_cell else None) for c, s in counts.items()}


def retention_events(events: Iterable[EvidenceEvent], event_type: str, day_buckets, t0: datetime):
    """Survival bucketing on OCCURRED_AT, not observed_at. A reuse that occurred on day 9 but was
    learned via a day-30 survey belongs in the day-9 bucket. Using observed_at here would silently
    push every self-reported reuse into a later bucket and corrupt the curve."""
    from collections import Counter
    buckets = Counter()
    for e in events:
        if e.event_type != event_type:
            continue
        day = (e.occurred_at - t0).days     # <-- occurred_at is the survival axis
        for b in day_buckets:
            if day <= b:
                buckets[b] += 1
    return dict(buckets)
