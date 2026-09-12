"""
Temporal core — the master primitive that turns the static event DB into a time-aware dynamic system
(docs/temporal/temporal-model.md; Parts I, II, VI, VIII of the temporal spec).

Static thinking:   Actor + Action -> Outcome
Dynamic thinking:  PriorState_t -> Context_t -> OpportunitySet_t -> Trigger_t -> ChoiceSet_t ->
                   Decision_t -> Action_t -> Intervention_t -> Artifact_t -> ImmediateOutcome_t ->
                   NextState_{t+1} -> DelayedOutcome_{t+k}

This module holds the FOUR CLOCKS, the point-in-time information-set rule (built on capture.py's
tri-temporal EvidenceEvent — NOT a reimplementation), event-sourced state derivation, and duration
metrics. No prediction may use an event whose available_at is after the prediction time.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# ------------------------------------------------------------------ I. FOUR CLOCKS (never conflated)
class Clock(str, Enum):
    EVENT = "EVENT"          # minute/hour during Event 1: minute 0 -> hour 3 -> submission
    PROJECT = "PROJECT"      # idea -> architecture -> prototype -> failure -> pivot -> demo
    LIFECYCLE = "LIFECYCLE"  # pre-event -> event -> 7d -> 30d -> 90d -> later outcomes
    MARKET = "MARKET"        # product launch -> pricing change -> AI trend -> recruiting cycle

# The ordered stages of the master primitive (Part I). An episode is reconstructable through these.
PRIMITIVE_CHAIN = ("PriorState", "Context", "OpportunitySet", "Trigger", "ChoiceSet", "Decision",
                   "Action", "Intervention", "Artifact", "ImmediateOutcome", "NextState",
                   "DelayedOutcome")

@dataclass(frozen=True)
class Stamp:
    """A timestamp is meaningless without its clock. Carrying the clock prevents conflating event-time
    (hour 4) with lifecycle-time (day 30)."""
    clock: Clock
    at: datetime
    def __post_init__(self):
        if not isinstance(self.clock, Clock):
            raise TypeError("Stamp.clock must be a Clock — do not conflate the four clocks")

# ------------------------------------------------------------- II. POINT-IN-TIME INFORMATION SET
def information_set(events, as_of: datetime, avail=lambda e: e.available_at):
    """{ e : available_at(e) <= as_of }. The ONLY events a model/prediction made at `as_of` may use.
    This is the transaction-time clause of capture.py's query gate, isolated so any temporal model can
    reuse it. Consent is layered separately via capture.CaptureStore.query — this is leakage control,
    not disclosure control."""
    return [e for e in events if avail(e) <= as_of]

def assert_no_future_leakage(used_events, as_of: datetime, avail=lambda e: e.available_at):
    """Raise if any event used by an as-of-`as_of` computation was not yet available. The single most
    important temporal invariant — backtests and predictions must not cheat with future knowledge."""
    leaked = [e for e in used_events if avail(e) > as_of]
    if leaked:
        raise ValueError(f"temporal leakage: {len(leaked)} event(s) with available_at > {as_of} "
                         f"used in an as-of-{as_of} computation")
    return True

# ---------------------------------------------------------------------- VI. EVENT SOURCING
def derive_state(events, as_of: datetime, reducer, initial,
                 order=lambda e: e.occurred_at, avail=lambda e: e.available_at):
    """Derived state is a fold over the IMMUTABLE event log — never hand-edited (Part VI). Uses only
    events available by `as_of` (point-in-time), applied in occurred_at order. reducer(state, event)
    -> state."""
    state = initial
    for e in sorted(information_set(events, as_of, avail), key=order):
        state = reducer(state, e)
    return state

# ---------------------------------------------------------------------- VIII. DURATION METRICS
def duration(t_start, t_end):
    """Minutes between two stamps/datetimes, or None if either is missing (missing is VALID, never 0)."""
    if t_start is None or t_end is None:
        return None
    a = t_start.at if isinstance(t_start, Stamp) else t_start
    b = t_end.at if isinstance(t_end, Stamp) else t_end
    return (b - a).total_seconds() / 60.0

# Canonical named duration metrics (Part VIII). Each is anchored on two event types; absent anchor -> None.
DURATION_METRICS = {
    "TimeToFirstSuccess":   ("EVENT_START", "FIRST_SUCCESS"),
    "TimeToActivation":     ("FIRST_USE", "ACTIVATED"),
    "TimeToIntegration":    ("FIRST_USE", "INTEGRATED"),
    "TimeToMentor":         ("MENTOR_REQUEST", "MENTOR_ARRIVED"),
    "MentorWait":           ("MENTOR_REQUEST", "MENTOR_ARRIVED"),
    "BlockedDuration":      ("BLOCK_BEGAN", "BLOCK_RESOLVED"),
    "TimeToRecovery":       ("INTERVENTION_END", "FIRST_SUCCESS"),
    "TimeToPivot":          ("BLOCK_BEGAN", "PIVOT"),
    "TimeToPrototype":      ("EVENT_START", "PROTOTYPE"),
    "TimeToSubmissionReady":("EVENT_START", "SUBMISSION_READY"),
    "TimeToAbandonment":    ("FIRST_USE", "ABANDONED"),
    "TimeToContinuation":   ("SUBMISSION", "CONTINUATION"),
}

def time_metrics(typed_events):
    """typed_events: list of (event_type, datetime). Returns every DURATION_METRIC computable from the
    first occurrence of each anchor; missing anchors yield None (never a fabricated 0)."""
    first = {}
    for et, t in typed_events:
        tt = t.at if isinstance(t, Stamp) else t
        if et not in first or tt < first[et]:
            first[et] = tt
    return {name: duration(first.get(a), first.get(b)) for name, (a, b) in DURATION_METRICS.items()}
