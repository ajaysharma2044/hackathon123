"""
Qualitative + insight engine (docs/qualitative-engine.md, docs/qualitative-writing-engine.md,
docs/data-universe.md; Parts V-VII).

Telemetry tells us WHAT; companies pay for WHY. This engine (a) gives every behavioral event a strict
OPERATIONAL definition tied to an allowed capture mode, (b) enforces critical-event sampling (not just
winners), and (c) builds a fully TRACEABLE insight chain that refuses to overclaim causation.

MAXIMAL CAPTURE, NOT SURVEILLANCE (the design rule): we capture as much as possible by pulling from
things participants PRODUCE ANYWAY (artifacts), TOOLS THEY OPT INTO (brokered telemetry), and NATURAL
FRICTION (help requests) — under consent, aggregate-by-default, min-cell suppression (engine/capture.py).
There are only five permitted capture modes and none is covert. The CAPTURE_HARD_BOUNDARIES below are
NEVER built regardless of commercial value.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# ---- capture discipline (what keeps "capture everything" from being surveillance) ----
PERMITTED_CAPTURE_MODES = (
    "SELF_REPORTED",        # the participant told us (application, prompt, interview)
    "ARTIFACT_DERIVED",     # read off something they produced anyway (repo, manifest, submission)
    "BROKERED_TELEMETRY",   # a tool they OPTED INTO emits events (consented, contractual)
    "ORGANIC_INTERACTION",  # a real interaction they initiated (help request, mentor chat)
    "OPERATIONAL",          # event logistics (check-in, room), no personal behavioral inference
)
# Never built, at any price (capture-risk-register.md Part 20).
CAPTURE_HARD_BOUNDARIES = (
    "KEYSTROKE_CAPTURE", "SCREEN_RECORDING", "CAMERA_MONITORING", "PRIVATE_MESSAGE_READING",
    "PERSONALITY_INFERENCE", "INTELLIGENCE_INFERENCE", "EMPLOYABILITY_SCORE",
    "PROTECTED_TRAIT_INFERENCE", "COVERT_TRACKING", "PERSON_QUALITY_SCORE",
)


def assert_not_surveillance(capture_mode: str, covert: bool = False, boundary: str = None):
    """Guard: raises if a capture would be covert, use a disallowed mode, or hit a hard boundary.
    This is how 'capture as much as possible' stays on the right side of surveillance."""
    if covert:
        raise ValueError("Covert capture is forbidden — capture must be consented and transparent.")
    if capture_mode not in PERMITTED_CAPTURE_MODES:
        raise ValueError(f"Capture mode {capture_mode!r} is not permitted (not one of {PERMITTED_CAPTURE_MODES}).")
    if boundary in CAPTURE_HARD_BOUNDARIES:
        raise ValueError(f"{boundary} is a hard boundary — never built regardless of commercial value.")
    return True


# ---- operational behavioral definitions (Part V: 'do not define them loosely') ----
@dataclass(frozen=True)
class BehaviorDefinition:
    kind: str
    definition: str
    capture_mode: str
    observable_confidence: int   # 0..3: can our instrumentation really see it?

BEHAVIOR_DEFINITIONS = {
    "EXPOSED": BehaviorDefinition("EXPOSED", "A required-exposure surface for product X was presented (brokered credential issued or workshop attended).", "BROKERED_TELEMETRY", 3),
    "CONSIDERED": BehaviorDefinition("CONSIDERED", "Product X appears in the team's recorded choice_set as KNOWN/OFFERED but not yet used.", "SELF_REPORTED", 2),
    "ACTIVATED": BehaviorDefinition("ACTIVATED", "First successful authenticated call/build with product X (brokered telemetry status=success).", "BROKERED_TELEMETRY", 3),
    "USED": BehaviorDefinition("USED", ">= N successful interactions with product X within one work window.", "BROKERED_TELEMETRY", 3),
    "REUSED": BehaviorDefinition("REUSED", "Product X used in more than one distinct work window.", "BROKERED_TELEMETRY", 3),
    "INTEGRATED": BehaviorDefinition("INTEGRATED", "Product X present in the final submitted dependency manifest/artifact.", "ARTIFACT_DERIVED", 3),
    "FAILED": BehaviorDefinition("FAILED", "An attempted activation/integration with error status and no subsequent success.", "BROKERED_TELEMETRY", 2),
    "ABANDONED": BehaviorDefinition("ABANDONED", "Product X was USED earlier but is absent from the final artifact AND had no interaction in the final window.", "ARTIFACT_DERIVED", 2),
    "SWITCHED": BehaviorDefinition("SWITCHED", "Product X ABANDONED AND a competing product Y in the same category INTEGRATED.", "ARTIFACT_DERIVED", 2),
    "ASKED_FOR_HELP": BehaviorDefinition("ASKED_FOR_HELP", "A help request (mentor/office-hours/organic) referencing product X was logged.", "ORGANIC_INTERACTION", 2),
    "PIVOTED": BehaviorDefinition("PIVOTED", "The team's recorded problem/approach changed materially at a checkpoint.", "SELF_REPORTED", 2),
    "COMPLETED": BehaviorDefinition("COMPLETED", "A working demo/artifact was produced.", "ARTIFACT_DERIVED", 3),
    "SUBMITTED": BehaviorDefinition("SUBMITTED", "A final submission was recorded.", "OPERATIONAL", 3),
    "CONTINUED": BehaviorDefinition("CONTINUED", "Opt-in evidence of activity on the project after the event ended.", "SELF_REPORTED", 1),
}


# ---- critical-event sampling (Part VI: do NOT interview only winners) ----
SAMPLING_FRAMES = ["ADOPTER", "NON_ADOPTER", "SWITCHER", "ABANDONER", "WINNER", "LOSER",
                   "HIGH_PERFORMING_TEAM", "FAILED_TEAM", "UNUSUAL_STACK", "COMMON_STACK",
                   "MAJOR_PIVOT", "SURPRISING_OUTCOME"]

def sampling_plan(target_per_frame: int = 3) -> dict:
    """A balanced qualitative sampling plan. The most valuable evidence is often WHY someone did NOT
    choose a product — so non-adopters/switchers/abandoners are first-class, not an afterthought."""
    return {frame: target_per_frame for frame in SAMPLING_FRAMES}


# ---- the insight chain (Part VII): RAW_QUOTE -> OBSERVATION -> CODE -> THEME -> PATTERN ->
#      INTERPRETATION -> RECOMMENDATION. Each level distinct; provenance one-directional. ----
LEVELS = ["RAW_QUOTE", "OBSERVATION", "CODE", "THEME", "PATTERN", "INTERPRETATION", "RECOMMENDATION"]
_LEVEL_RANK = {lvl: i for i, lvl in enumerate(LEVELS)}


@dataclass
class InsightNode:
    node_id: str
    level: str
    statement: str
    children: list = field(default_factory=list)          # lower-level nodes this rests on
    alternatives: list = field(default_factory=list)      # competing explanations (for INTERPRETATION)
    confidence: float = 0.5

    def add_child(self, child: "InsightNode"):
        if _LEVEL_RANK[child.level] >= _LEVEL_RANK[self.level]:
            raise ValueError(f"A {self.level} may only rest on strictly lower levels, not {child.level}.")
        self.children.append(child); return child


def traces_to_raw(node: InsightNode) -> bool:
    """A client-facing claim must trace down to at least one RAW_QUOTE or OBSERVATION."""
    if node.level in ("RAW_QUOTE", "OBSERVATION"):
        return True
    return any(traces_to_raw(c) for c in node.children)


def interpretation_valid(node: InsightNode) -> bool:
    """An INTERPRETATION is valid only if it (a) traces to raw evidence AND (b) carries at least one
    competing explanation (Part VII forbids single-cause claims)."""
    if node.level != "INTERPRETATION":
        return traces_to_raw(node)
    return traces_to_raw(node) and len(node.alternatives) >= 1


def write_claim(node: InsightNode) -> str:
    """Render a client-facing sentence. Refuses causal overclaiming: an INTERPRETATION whose
    alternatives are not all ruled out is phrased as 'MAY be a contributor', never 'X causes Y'."""
    if node.level == "INTERPRETATION":
        if not node.alternatives:
            raise ValueError("Refusing to write an interpretation with no competing explanations listed.")
        unresolved = [a for a in node.alternatives if not getattr(a, "ruled_out", False)] \
            if node.alternatives and hasattr(node.alternatives[0], "ruled_out") else node.alternatives
        hedge = "MAY be a meaningful contributor to" if unresolved else "appears to drive"
        return f"{node.statement} {hedge} the observed outcome (see alternatives: {len(node.alternatives)})."
    return node.statement
