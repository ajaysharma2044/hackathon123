"""
The critical-incident engine (docs/research-ops/critical-incidents.md).

A hackathon generates its own research signal: a switch, an abandonment, a repeated help request,
a failed integration. Each such moment is a TRIGGER. This module is the versioned taxonomy of
triggers and the routing rule for each one:

    detected  →  who detects it  →  is a question even warranted?  →  which micro-prompt
              →  or is a mentor note already enough  →  or does it need a researcher interview?

Design rule (kept honest): most triggers do NOT fire a participant-facing question. The default is
silence. We only spend a participant's attention where the signal is high and freshest, and where a
passive channel (mentor note, artifact, telemetry) does not already capture it. Ordinal
`commercial_value` is why we care; `burden_sec` is what the answer costs the participant.
"""
from __future__ import annotations
from dataclasses import dataclass

# Detectors — who/what notices the trigger.
TELEMETRY, MENTOR, OBSERVER, CHECKPOINT, ARTIFACT, SELF = (
    "TELEMETRY", "MENTOR", "OBSERVER", "CHECKPOINT", "ARTIFACT", "SELF")

# Routed actions.
FIRE_PROMPT = "FIRE_PROMPT"                       # show a micro-prompt at the fresh moment
MENTOR_NOTE_SUFFICIENT = "MENTOR_NOTE_SUFFICIENT" # the mentor log already captures the "why"
FLAG_FOR_INTERVIEW = "FLAG_FOR_INTERVIEW"         # too rich for a prompt — queue a deeper interview
OBSERVE_ONLY = "OBSERVE_ONLY"                     # log it; ask nothing


@dataclass(frozen=True)
class Trigger:
    trigger_type: str
    detector: str
    action: str
    prompt_key: str        # which micro-prompt / interview segment (see adaptive_questions)
    needs_followup: bool
    burden_sec: int        # expected participant cost of the response (0 if no participant ask)
    commercial_value: str  # HIGH | MED | LOW
    version: int = 1


def _t(tt, det, act, pk, fu, b, cv):
    return Trigger(tt, det, act, pk, fu, b, cv)

# The taxonomy. Every trigger from the brief (Part IV) plus discovered ones, each with its routing.
TRIGGERS = {t.trigger_type: t for t in [
    # --- tool/product decisions: the commercial core -------------------------------------------
    _t("TOOL_CONSIDERATION", OBSERVER, OBSERVE_ONLY, "technology_choice", False, 0, "MED"),
    _t("TOOL_SELECTION",     TELEMETRY, FIRE_PROMPT, "tool_choice_reason", False, 20, "HIGH"),
    _t("TOOL_REJECTION",     CHECKPOINT, FIRE_PROMPT, "why_not_shortlist", False, 20, "HIGH"),
    _t("SWITCH",             TELEMETRY, FIRE_PROMPT, "switch_reason", True, 20, "HIGH"),
    _t("ABANDONMENT",        TELEMETRY, FIRE_PROMPT, "abandon_reason", True, 20, "HIGH"),
    _t("PROBLEM_CHANGE",     CHECKPOINT, FIRE_PROMPT, "pivot_reason", True, 20, "MED"),
    _t("MAJOR_PIVOT",        OBSERVER, FLAG_FOR_INTERVIEW, "pivot", True, 0, "HIGH"),
    _t("ARCHITECTURE_CHANGE", OBSERVER, OBSERVE_ONLY, "architecture", False, 0, "MED"),
    # --- help + friction: route to support first, capture as byproduct -------------------------
    _t("HELP_REQUEST",         MENTOR, MENTOR_NOTE_SUFFICIENT, "help", False, 0, "MED"),
    _t("REPEATED_HELP_REQUEST", MENTOR, FLAG_FOR_INTERVIEW, "repeated_friction", True, 0, "HIGH"),
    _t("TECHNICAL_FAILURE",    TELEMETRY, FIRE_PROMPT, "expected_what", False, 20, "HIGH"),
    _t("DOCUMENTATION_FAILURE", SELF, FIRE_PROMPT, "doc_looking_for", False, 20, "HIGH"),
    _t("MENTOR_DEPENDENCY",    MENTOR, OBSERVE_ONLY, "dependency", True, 0, "HIGH"),
    _t("RESOURCE_CONSTRAINT",  CHECKPOINT, OBSERVE_ONLY, "resource", False, 0, "MED"),
    # --- outcomes: successes, completions, surprises -------------------------------------------
    _t("UNEXPECTED_SUCCESS",   OBSERVER, FLAG_FOR_INTERVIEW, "unexpected", False, 0, "MED"),
    _t("UNEXPECTED_USE_CASE",  OBSERVER, FLAG_FOR_INTERVIEW, "unexpected_use", True, 0, "HIGH"),
    _t("PRODUCT_WORKAROUND",   OBSERVER, FIRE_PROMPT, "workaround", False, 20, "HIGH"),
    _t("FEATURE_REQUEST",      SELF, OBSERVE_ONLY, "feature", False, 0, "MED"),
    _t("PROTOTYPE_COMPLETION", ARTIFACT, OBSERVE_ONLY, "completion", False, 0, "LOW"),
    _t("NON_COMPLETION",       ARTIFACT, FIRE_PROMPT, "non_completion", False, 20, "MED"),
    # --- R&D-specific ---------------------------------------------------------------------------
    _t("RD_HYPOTHESIS_FAILURE", OBSERVER, FLAG_FOR_INTERVIEW, "rd_failure", True, 0, "HIGH"),
    _t("RD_CONVERGENCE",       OBSERVER, OBSERVE_ONLY, "rd_converge", False, 0, "HIGH"),
    _t("RD_DIVERGENCE",        OBSERVER, OBSERVE_ONLY, "rd_diverge", False, 0, "HIGH"),
    # --- incentives / credits -------------------------------------------------------------------
    _t("CREDIT_USE",           TELEMETRY, FIRE_PROMPT, "credit_effect", False, 15, "HIGH"),
    _t("CREDIT_IGNORE",        TELEMETRY, FIRE_PROMPT, "credit_ignore", False, 15, "HIGH"),
    # --- team + continuation --------------------------------------------------------------------
    _t("TEAM_CHANGE",          OBSERVER, OBSERVE_ONLY, "team", False, 0, "LOW"),
    _t("CONTINUATION_DECISION", SELF, FIRE_PROMPT, "continuation", True, 20, "HIGH"),
]}


class TriggerRegistry:
    """Thin wrapper so LiveResearchOS can `.route(trigger_type)` and get a routing decision."""

    def __init__(self, triggers: dict = None):
        self.triggers = triggers if triggers is not None else TRIGGERS

    def route(self, trigger_type: str) -> Trigger:
        if trigger_type not in self.triggers:
            # Unknown trigger is observed, never asked about — we do not improvise a prompt.
            return Trigger(trigger_type, OBSERVER, OBSERVE_ONLY, "", False, 0, "LOW")
        return self.triggers[trigger_type]

    def high_value_asks(self) -> list:
        """The triggers that both warrant a participant question AND carry high commercial value —
        the ones the war room watches for (docs/research-ops/research-war-room.md)."""
        return sorted(
            [t for t in self.triggers.values()
             if t.action in (FIRE_PROMPT, FLAG_FOR_INTERVIEW) and t.commercial_value == "HIGH"],
            key=lambda t: t.trigger_type)
