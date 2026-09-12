# Dynamic context and the opportunity set

`engine/context_envelope.py`. Context is **not** a static profile — it is a function of time, `C_i(t)`.

*Hour 0:* ORIE student, no team. *Hour 2:* joins an AI team. *Hour 7:* becomes the optimization owner.
*Hour 15:* learns a new solver. *Day 30:* still building. Interpreting any output requires knowing the
context **at the time the output was produced**.

## ContextEnvelope

`CONTEXT_FIELDS` (26): EventPhase, ProjectPhase, TimeRemaining, CurrentGoal, CurrentMilestone,
CurrentWorkstream, CurrentBlocker, RoleStructure, CapabilityCoverage, ResourcesAvailable,
ComputeAvailable, MentorAvailability, RecentMentorIntervention, PeerExposure, SponsorExposure,
ChallengeContext, PrizeContext, CreditContext, PhysicalZone, ChoiceSet, PriorAttempts,
PriorToolExposure, RelevantExperience, PrecedingEvents, Consent, EvidenceStatus.

**Every field is optional. Missing is valid** — `ContextEnvelope.get()` returns `UNKNOWN` (via
`compliance.neutral_when_missing`) for an absent field, never a penalty. `context_at(events, entity,
as_of)` reconstructs the envelope by folding the entity's context-change events available by `as_of`
(point-in-time).

## The opportunity set O_i(t)

`OpportunitySet` / `opportunity_at(events, entity, as_of)`: the resources, capabilities, and support
available to an actor at time *t* (`{GPU, MENTOR_ORIE, TEAMMATE_FRAMEWORK, ...}`). At hour 3 a
participant may have no GPU, no relevant mentor, an unfamiliar stack; at hour 6 all three arrive.
**An achievement is read *with* its opportunity set, never divided by it.**

## The hard line: opportunity is context, never a score

This is the most dangerous part of the whole system if done wrong. Opportunity/starting context exists
to *interpret* output fairly — it must **never** be collapsed into a socioeconomic, privilege,
"advantage", or "potential" score:

- `assert_opportunity_not_scored(obj)` **raises** on any `advantage_score` / `potential_score` /
  `socioeconomic` / `privilege_score` name.
- `vet_starting_context(fields)` accepts only **direct relevant experience**
  (`LEGITIMATE_STARTING_CONTEXT`: prior coursework, project, tool, domain experience, time-using-tech)
  and **raises** (via `compliance.assert_no_sensitive`) on any sensitive/protected field (age, income,
  class, …).

`schema/012 context_envelope` carries the note in SQL: *no socioeconomic/protected/person-quality
column may ever be added.*
