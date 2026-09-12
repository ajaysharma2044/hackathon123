"""
Episode reconstruction — the master object (docs/temporal/episodes.md; Parts VII, VIII, LXX, LXXI).

The unit of the system is not a row, it is an EPISODE: an actor trying to achieve a goal, from a prior
state, with an opportunity set, under constraints, after prior events, who makes a decision, receives
an intervention, produces an artifact, and reaches a next state — with 7/30/90-day delayed outcomes.
An Event is a set of Episodes linked over time. Reconstructed from the immutable event log; never
hand-edited. Reuses temporal_core (point-in-time, durations) and context_envelope.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from temporal_core import information_set, time_metrics, duration
from context_envelope import ContextEnvelope, OpportunitySet, context_at, opportunity_at

@dataclass
class Episode:
    actors: list                              # participant/team ids
    start_time: datetime
    end_time: datetime = None
    prior_state: str = None
    goal: str = None
    context: ContextEnvelope = None
    opportunity_set: OpportunitySet = None
    trigger: str = None
    choice_set: list = field(default_factory=list)
    decision: str = None
    action: str = None
    intervention: str = None
    artifact: str = None
    immediate_outcome: str = None
    explanation: str = None                   # LXX: proposed mechanism
    alternative_explanations: list = field(default_factory=list)  # LXX: rival mechanisms, kept explicit
    next_state: str = None
    delayed_outcomes: dict = field(default_factory=dict)  # {"7d":..., "30d":..., "90d":...}
    evidence_links: list = field(default_factory=list)    # event_ids backing every field above
    thick_description: str = None             # LXXI: qualitative context for high-signal episodes

    def duration_min(self):
        return duration(self.start_time, self.end_time)

def reconstruct_episode(events, entity, start: datetime, end: datetime, goal=None, as_of=None):
    """Build an Episode for `entity` over [start,end] from the immutable event stream. If `as_of` is
    given, only events available by then are used (point-in-time reconstruction — Part LVI/LXX). The
    episode's typed events drive the duration metrics; unknown fields stay None (missing is valid)."""
    as_of = as_of or end
    pool = [e for e in information_set(events, as_of)
            if getattr(e, "subject_participant", None) == entity
            and start <= e.occurred_at <= end]
    pool.sort(key=lambda e: e.occurred_at)
    typed = [(e.event_type, e.occurred_at) for e in pool]
    ep = Episode(actors=[entity], start_time=start, end_time=end, goal=goal,
                 context=context_at(events, entity, as_of),
                 opportunity_set=opportunity_at(events, entity, as_of),
                 evidence_links=[e.event_id for e in pool])
    # fill chain slots from the first event of each kind, when present
    def first(et):
        for e in pool:
            if e.event_type == et:
                return e
        return None
    if first("TRIGGER"):     ep.trigger = first("TRIGGER").payload.get("what")
    if first("DECISION"):    ep.decision = first("DECISION").payload.get("what")
    if first("INTERVENTION"):ep.intervention = first("INTERVENTION").payload.get("what")
    if first("ARTIFACT"):    ep.artifact = first("ARTIFACT").payload.get("what")
    ep._time_metrics = time_metrics(typed)     # attached for convenience
    return ep

def episode_durations(episode: Episode, events=None):
    """The Part-VIII duration metrics for an episode (TimeToMentor, BlockedDuration, ...)."""
    return getattr(episode, "_time_metrics", None) or {}

@dataclass
class EventTimeline:
    """Event = { Episodes linked over time } (Part VII)."""
    episodes: list = field(default_factory=list)
    def add(self, ep: Episode): self.episodes.append(ep); return self
    def ordered(self):
        return sorted(self.episodes, key=lambda e: e.start_time)
    def for_actor(self, entity):
        return [e for e in self.ordered() if entity in e.actors]
