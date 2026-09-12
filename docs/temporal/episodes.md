# The Episode — the master object

`engine/episode.py`. The unit of the system is not a row, it is an **Episode**: an actor trying to
achieve a goal, from a prior state, with an opportunity set, under constraints, after prior events, who
makes a decision, receives an intervention, produces an artifact, and reaches a next state — with
7/30/90-day delayed outcomes.

```
Episode
├── actors, start_time, end_time
├── prior_state, goal
├── context (ContextEnvelope)   ├── opportunity_set (OpportunitySet)
├── trigger → choice_set → decision → action → intervention → artifact → immediate_outcome
├── explanation + alternative_explanations   (the proposed mechanism AND its rivals)
├── next_state
├── delayed_outcomes {7d, 30d, 90d}
├── evidence_links   (every field traces to immutable event ids)
└── thick_description   (qualitative context for high-signal episodes)
```

**An Event is a set of Episodes linked over time** (`EventTimeline`).

## Reconstruction is point-in-time

`reconstruct_episode(events, entity, start, end, as_of)` builds an Episode from the **immutable** event
stream — never hand-edited. If `as_of` is given, only events available by then are used. This is what
makes an "as of submission" reconstruction honest: a **day-30 retention outcome (available_at day 30)
is invisible to a submission-time reconstruction** (verified in `test_temporal.py`). The same episode
reconstructed later, with more available, legitimately shows more — because the information set grew,
not because we cheated.

## Duration metrics fall out of the episode

`episode_durations()` exposes the `time_metrics` — TimeToMentor, BlockedDuration, TimeToRecovery,
TimeToPivot, TimeToActivation, … — anchored on the episode's typed events. See
[temporal-model.md](temporal-model.md) for the worked 44-min / 14-min example.
