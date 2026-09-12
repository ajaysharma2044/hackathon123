"""
The Live Research OS kernel — shared types, the hard structural guards, the client-facing gate,
and the live loop that ties the other engines together.

This module encodes the properties that must hold regardless of which engine touches the data:

  1. OBSERVED FACT ≠ INTERPRETATION. A `FieldNote` keeps the behavioral fact and the researcher's
     reading in separate fields, and forces a competing interpretation to be considered.
     (docs/research-ops/field-note-system.md)
  2. NO PERSON SCORE, NO PROTECTED-TRAIT INFERENCE. `assert_clean(record)` rejects any record that
     carries a quality/employability/personality score or a protected trait — structurally, not by
     policy. (docs/research-ops/live-research-os.md, Part XXXV)
  3. CLIENTS SEE AGGREGATE, NOT RAW. `client_view(...)` emits min-cell-suppressed aggregates and
     refuses to hand a client a raw observation or an unreviewed quote. (Part XXXVI)
  4. THE LIVE LOOP. `LiveResearchOS.observe_then_decide(...)` turns an incident into the next best
     action — notice → ask one good question → (as patterns emerge) deliberately sample confirming
     AND contradictory cases → sharpen the question. (docs/research-ops/live-research-os.md)

Pure stdlib. A reference/enforcement kernel, not a production store — the invariants are executable
so they can be tested (engine/test_live_research_os.py), not merely asserted in prose.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

DEFAULT_MIN_CELL = 8          # min-cell-size suppression, same floor as engine/capture.py

# --- Guard 2: things this system structurally refuses to hold about a person --------------------
# No quality/employability/founder "score"; no personality or intelligence inference; no protected
# trait. These are forbidden KEYS — if a record tries to carry one, construction fails loudly.
FORBIDDEN_SCORE_KEYS = frozenset({
    "person_score", "quality_score", "employability_score", "founder_score", "talent_score",
    "rank", "iq", "intelligence", "personality", "big_five", "competence_score",
})
PROTECTED_TRAIT_KEYS = frozenset({
    "race", "ethnicity", "gender", "sex", "age", "religion", "disability",
    "sexual_orientation", "national_origin", "pregnancy", "veteran_status",
})
FORBIDDEN_KEYS = FORBIDDEN_SCORE_KEYS | PROTECTED_TRAIT_KEYS


def assert_clean(record: dict) -> dict:
    """Reject any record carrying a person-score or protected-trait field. Applied at the door of
    every engine that accepts free-form payloads (observations, mentor notes, episodes)."""
    bad = FORBIDDEN_KEYS & {k.lower() for k in record}
    if bad:
        raise PermissionError(
            f"forbidden field(s) {sorted(bad)}: this system scores no person and infers no "
            f"protected trait (live-research-os.md Part XXXV)")
    return record


# --- Guard 1: the field note, with fact and interpretation kept apart ---------------------------
@dataclass(frozen=True)
class FieldNote:
    observation_id: str
    researcher_id: str
    occurred_at: datetime
    observed_event: str                  # FACT: what was seen/heard, behaviorally. Required.
    subject_team: Optional[str] = None
    subject_participant: Optional[str] = None
    direct_quote: Optional[str] = None   # verbatim words, if any
    researcher_interpretation: Optional[str] = None    # explicitly the researcher's reading
    alternative_interpretation: Optional[str] = None   # a competing reading
    trigger_type: Optional[str] = None
    confidence: float = 0.7              # < 1.0 because an observation is partly inference
    consent_scope: frozenset = frozenset({"QUALITATIVE_RESEARCH"})

    def __post_init__(self):
        if not self.observed_event or not self.observed_event.strip():
            raise ValueError("observed_event (the behavioral fact) is required and cannot be empty")
        if self.subject_team is None and self.subject_participant is None:
            raise ValueError("a field note needs a subject (team or participant)")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be in [0,1]")
        # If an interpretation is offered, a competing one must be considered too (anti-bias).
        if self.researcher_interpretation and not self.alternative_interpretation:
            raise ValueError(
                "an interpretation requires an alternative_interpretation — a single reading with "
                "no competing one is how confirmation bias enters (field-note-system.md)")

    def is_interpretation_free(self) -> bool:
        """True when the note is a pure behavioral fact (the safest kind)."""
        return self.researcher_interpretation is None


# --- Event phases (Part XXXI) -------------------------------------------------------------------
EVENT_PHASES = (
    "PRE_EVENT", "APPLICATION", "ACCEPTANCE", "BASELINE", "ARRIVAL", "CONSENT", "TEAM_FORMATION",
    "ORIENTATION", "BUILD_START", "EARLY_BUILD", "MID_BUILD", "LATE_BUILD", "SUBMISSION", "DEMO",
    "POST_EVENT", "FOLLOWUP_7", "FOLLOWUP_30", "FOLLOWUP_90",
)


# --- Guard 3: the client-facing gate ------------------------------------------------------------
class ClientView:
    """What a paying client may see DURING and after the event. Aggregate, min-cell-suppressed,
    never a raw observation or an unreviewed quote, never an individual participant (except the
    participant's own opted-in discoverability, which does not pass through here)."""

    def __init__(self, min_cell: int = DEFAULT_MIN_CELL):
        self.min_cell = min_cell

    def refuse_raw(self, _obj) -> None:
        raise PermissionError(
            "a client may not receive raw observations, unreviewed quotes, or researcher notes "
            "(live-research-os.md Part XXXVI). Only aggregate findings and promoted claims.")

    def aggregate(self, rows: list, cell_key: Callable, subject_key: Callable) -> dict:
        """Count distinct subjects per cell; suppress cells below min_cell to None."""
        cells: dict = {}
        for r in rows:
            cells.setdefault(cell_key(r), set()).add(subject_key(r))
        return {c: (len(s) if len(s) >= self.min_cell else None) for c, s in cells.items()}


# --- Guard 4: the live loop ---------------------------------------------------------------------
@dataclass
class Action:
    kind: str          # FIRE_PROMPT | MENTOR_NOTE_SUFFICIENT | FLAG_FOR_INTERVIEW | SEEK_NEGATIVE_CASE | SILENT
    detail: dict = field(default_factory=dict)


class LiveResearchOS:
    """The orchestration loop. It does not store data itself — it wires the specialized engines
    (triggers, questions, sampling, backlog, burden) into the single loop that makes this more than
    a post-event survey:

        something happens  →  the system NOTICES (a critical incident)
                           →  asks the RIGHT person ONE good question (if burden + timing allow)
                           →  a pattern emerges (backlog + memos)
                           →  researchers deliberately seek CONFIRMING and CONTRADICTORY cases
                           →  the next question gets smarter
    """

    def __init__(self, triggers, burden, interrupt_state: Callable):
        self.triggers = triggers           # engine.research_triggers registry (routing)
        self.burden = burden               # engine.burden_budget.BurdenBudget
        self.interrupt_state = interrupt_state   # (team, at) -> interrupt_state string

    def observe_then_decide(self, incident: dict, now: datetime) -> Action:
        """Given a detected incident, decide the next action under the burden + timing constraints.
        The routing of WHICH question belongs to research_triggers; this is the gate that decides
        whether we may ask at all right now, and whether a mentor note already suffices."""
        route = self.triggers.route(incident["trigger_type"])
        team = incident.get("subject_team")
        # Timing gate: never interrupt a team that is heads-down or near a deadline.
        state = self.interrupt_state(team, now)
        if route.action == "MENTOR_NOTE_SUFFICIENT":
            return Action("MENTOR_NOTE_SUFFICIENT", {"reason": "mentor log already captures this"})
        if route.action == "FLAG_FOR_INTERVIEW":
            return Action("FLAG_FOR_INTERVIEW", {"segment": route.prompt_key})
        if route.action == "FIRE_PROMPT":
            if state == "DO_NOT_INTERRUPT":
                return Action("SILENT", {"reason": "timing: team is heads-down/near deadline"})
            p = incident.get("subject_participant")
            if p is not None and not self.burden.can_spend(p, "MICRO_PROMPT", route.burden_sec, now):
                return Action("SILENT", {"reason": "participant research-minutes budget spent"})
            return Action("FIRE_PROMPT", {"prompt_key": route.prompt_key, "burden_sec": route.burden_sec})
        return Action("SILENT", {"reason": "no action for this trigger"})
