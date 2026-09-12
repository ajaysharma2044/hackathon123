"""
The team story (docs/research-ops/team-trajectories.md, Parts XXII–XXIV).

Every team should end the event with a reconstructed arc:

  TEAM CREATED → PROBLEM SELECTED → INITIAL PLAN → TOOL SET → FIRST APPROACH → BLOCKER → HELP
    → DECISION → SWITCH/PIVOT → SECOND APPROACH → ARTIFACT → OUTCOME → POST-EVENT CONTINUATION

This is a DERIVED object (like behavioral_episode in 001): assembled from raw evidence + observations
+ mentor interactions, carrying a model_version, and re-derivable — never hand-edited. Two invariants:
  * PROVENANCE REQUIRED. Every episode must cite at least one raw source (evidence_event or
    observation); an episode with no provenance is rejected. This keeps the story traceable.
  * RE-DERIVABLE. assemble() is a pure function of its inputs — running it twice on the same raw
    episodes yields the identical ordered arc, so a story is cheap to throw away and rebuild.

Three trajectory kinds share the structure: DECISION (default), RD_REASONING (hypothesis→result→
interpretation→next), and PRODUCT_JOURNEY (expectation→friction→workaround→switch→continued-use).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

DECISION, RD_REASONING, PRODUCT_JOURNEY = "DECISION", "RD_REASONING", "PRODUCT_JOURNEY"

# The canonical decision phases, in order — used to sanity-check/normalize an arc.
PHASES = ("PROBLEM_SELECTED", "INITIAL_PLAN", "TOOL_SET", "FIRST_APPROACH", "BLOCKER", "HELP",
          "DECISION", "SWITCH", "PIVOT", "SECOND_APPROACH", "ARTIFACT", "OUTCOME", "CONTINUATION")


@dataclass
class Episode:
    seq: int
    phase: str
    kind: str = DECISION
    behavior: Optional[str] = None           # the observed "what"
    explanation: Optional[str] = None        # the qualitative "why" (hedged, labeled)
    mentor_interaction_id: Optional[str] = None
    artifact_state: Optional[str] = None
    # R&D fields
    hypothesis: Optional[str] = None
    result: Optional[str] = None
    assumption_failed: Optional[str] = None
    # product-journey fields
    expectation: Optional[str] = None
    friction: Optional[str] = None
    workaround: Optional[str] = None
    switched_to: Optional[str] = None
    # provenance — at least one must be non-empty
    evidence_event_ids: tuple = ()
    observation_ids: tuple = ()

    def has_provenance(self) -> bool:
        return bool(self.evidence_event_ids) or bool(self.observation_ids)


@dataclass
class Trajectory:
    team_id: str
    model_version: str
    episodes: list = field(default_factory=list)

    def story(self) -> list:
        """Render the arc as an ordered list of (phase, behavior, explanation) for the report."""
        return [(e.phase, e.behavior, e.explanation) for e in self.episodes]

    def transitions(self) -> list:
        return [(self.episodes[i].phase, self.episodes[i + 1].phase)
                for i in range(len(self.episodes) - 1)]


def assemble(team_id: str, raw_episodes: list, model_version: str) -> Trajectory:
    """Pure, re-derivable assembly. Sorts by seq, enforces provenance, rejects a hand-edited arc
    (duplicate seq numbers). Raising on a provenance-free episode keeps the story traceable to raw."""
    seqs = [e.seq for e in raw_episodes]
    if len(seqs) != len(set(seqs)):
        raise ValueError("duplicate seq numbers — a trajectory must be a clean ordered arc")
    for e in raw_episodes:
        if not e.has_provenance():
            raise ValueError(
                f"episode seq={e.seq} ({e.phase}) has no provenance — every node must cite a raw "
                f"evidence_event or observation (team-trajectories.md)")
    ordered = sorted(raw_episodes, key=lambda e: e.seq)
    return Trajectory(team_id, model_version, ordered)
