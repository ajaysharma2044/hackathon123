# Event Phase Plan — Research Ops, Phase by Phase

**Part XXXI of the [Live Research Operating System](live-research-os.md).**

The same research OS behaves differently at each moment of the event. A prompt that is welcome at
hour 2 is an intrusion at hour 70; a question that is cheap before anyone has built anything is
expensive once teams are in deep flow. This doc walks the event phase by phase and says, for each:
**what matters, what data, what questions, who captures it, how much burden, and what must NEVER
happen.**

The phase names are the `EVENT_PHASES` tuple in
[`live_research.py`](../../engine/live_research.py) — use them exactly:

```
 PRE_EVENT · APPLICATION · ACCEPTANCE · BASELINE          (before anyone arrives)
 ARRIVAL · CONSENT · TEAM_FORMATION · ORIENTATION         (the door)
 BUILD_START · EARLY_BUILD · MID_BUILD · LATE_BUILD       (the 72h)
 SUBMISSION · DEMO · POST_EVENT                           (the close)
 FOLLOWUP_7 · FOLLOWUP_30 · FOLLOWUP_90                   (the compounding asset)
```

> The binding constraint governs every phase: **the experience wins.** Burden is a budget
> (≤~18 explicit research-minutes per participant across the whole weekend,
> [participant-burden.md](participant-burden.md)), spent heaviest where it is cheapest and freshest
> — the edges of the event — and near-zero in deep build.

## PRE_EVENT / APPLICATION / ACCEPTANCE / BASELINE

Before anyone arrives, the research cost to the participant is near-zero because the instruments
*are* the application and selection they were doing anyway ([capture-system.md](../capture-system.md)
Phases A/B).

- **What matters?** The SAID baseline — stated stack, prior familiarity, intended project, prior
  collaboration graph — captured *before* exposure so later divergence is measurable. This is the
  adoption-vs-retention covariate.
- **What data?** Structured application fields; baseline survey (`EvidenceEvent` `is_self_report=true,
  source_kind=SURVEY`); team-prep intentions. Stored with `consent_scope[]`.
- **What questions?** What do elite builders reach for unprompted? What is their pre-existing product
  familiarity? (The "what would you build" item is a **neutral research instrument**, scored only by
  the research pipeline, never by selection reviewers.)
- **Who captures it?** The application/registration system; `DATA_STEWARD` owns consent integrity.
- **How much burden?** LOW — it is the admission flow; `channel = APPLICATION | BASELINE` debits.
- **What must NEVER happen?** No protected-trait collection for research; demographics siloed from
  the research store. The research-vs-selection firewall must be real or the neutral instrument is
  worthless.

## ARRIVAL / CONSENT / TEAM_FORMATION / ORIENTATION

The door. This is where consent is made real and where the prior-collaboration graph at t0 is
fixed.

- **What matters?** Informed, per-scope, revocable consent; who teamed with whom; the t0 team
  baseline (problem intent, intended tools).
- **What data?** `consent_event` ledger grants; `TEAM_FORMATION` episodes; `checkpoint` kind=START
  (problem, plan, intended tools, prior-collaboration graph).
- **What questions?** What do teams *intend* to build and with what, before reality intervenes?
  (Baseline for every later switch/pivot comparison.)
- **Who captures it?** Check-in staff + event app; `DATA_STEWARD` for consent; `FIELD_RESEARCHER`
  observing team formation.
- **How much burden?** LOW–MED; the START checkpoint is ≤5 structured answers, incentive-tied.
- **What must NEVER happen?** No capture before consent is recorded; no default-on scopes. A
  participant who declines a scope is simply excluded from that scope's queries at query time.

## BUILD_START

- **What matters?** Problem selection, initial architecture, tool consideration — the first
  commercial-core decisions.
- **What data?** `TOOL_CONSIDERATION` (OBSERVE_ONLY), `TOOL_SELECTION` (FIRE_PROMPT,
  `tool_choice_reason`, 20s), `TOOL_REJECTION` (`why_not_shortlist`), brokered-key activation events,
  START-checkpoint deltas.
- **What questions?** What did they choose, and *why that over the alternative they named*? What did
  they consider and reject?
- **Who captures it?** `TELEMETRY` (brokered keys) fires selection prompts; `OBSERVER` logs
  consideration; the war room routes ([critical-incidents.md](critical-incidents.md)).
- **How much burden?** MED — a couple of 20s prompts at a genuinely fresh moment; skippable.
- **What must NEVER happen?** No prompt during a team's first heads-down architecture push if the
  interrupt window says `DO_NOT_INTERRUPT`. Choice capture ≠ nudging the choice.

## EARLY_BUILD

- **What matters?** First integrations, first failures, first help requests — friction surfaces
  here.
- **What data?** `TECHNICAL_FAILURE` / `DOCUMENTATION_FAILURE` (FIRE_PROMPT, 20s), `HELP_REQUEST`
  (MENTOR_NOTE_SUFFICIENT — the note is enough), mentor interactions with `intensity`.
- **What questions?** What did they expect vs what happened? What were they looking for in the docs?
  Where is the friction concentrated (auth? DB? deploy?)?
- **Who captures it?** `MENTOR` (help-first, logs as byproduct, ≤20s note); `TELEMETRY` for the
  failure triggers; `FIELD_RESEARCHER` roaming.
- **How much burden?** LOW–MED; most help is captured passively via the mentor note, no participant
  ask.
- **What must NEVER happen?** Help must never be withheld or delayed to "get the data." The mentor's
  first job is the participant's wait time ([mentor-system.md](mentor-system.md)).

## MID_BUILD

- **What matters?** Pivots, switching, resource constraints, the deeper problems — the richest
  research window.
- **What data?** `SWITCH` (`switch_reason`, followup), `ABANDONMENT` (`abandon_reason`, followup),
  `PROBLEM_CHANGE` / `MAJOR_PIVOT` (FLAG_FOR_INTERVIEW), `RD_HYPOTHESIS_FAILURE`,
  `REPEATED_HELP_REQUEST` (FLAG_FOR_INTERVIEW), `RESOURCE_CONSTRAINT` (OBSERVE_ONLY).
- **What questions?** What pushed the switch? What made them abandon an approach? Where did the R&D
  hypothesis fail? (The DB-switch matrix and failed-approach counts from
  [research-war-room.md](research-war-room.md) live here.)
- **Who captures it?** `TELEMETRY` fires switch/abandon prompts; `INTERVIEWER` runs flagged
  interviews; the war room synthesizes into memos every ~3–4h.
- **How much burden?** MED, carefully metered — this is where the burden budget is most at risk.
  Flagged interviews only when the interrupt window is `SHORT_INTERVIEW_OK` or better.
- **What must NEVER happen?** No stacking prompts on a team mid-switch; the MIDPOINT checkpoint is
  still ≤5 items. Deep flow with no friction gets *no* prompts — absence of a prompt is correct.

## LATE_BUILD

- **What matters?** Completion pressure, feature-cutting, final architecture — what survives contact
  with the deadline.
- **What data?** `ARCHITECTURE_CHANGE` (OBSERVE_ONLY), `NON_COMPLETION` (`non_completion`, 20s),
  artifact state snapshots, `PRODUCT_WORKAROUND`.
- **What questions?** What got cut and why? What did the final architecture settle on? What did they
  work around rather than solve?
- **Who captures it?** `ARTIFACT` detectors (repo/deploy); `OBSERVER`; light telemetry.
- **How much burden?** LOW — teams are in crunch; `team_interrupt_window` is mostly
  `DO_NOT_INTERRUPT` near the deadline. Capture shifts to passive artifact signals.
- **What must NEVER happen?** No interruptions near the deadline. This is the phase where the
  interrupt policy matters most; research yields to the crunch.

## SUBMISSION

- **What matters?** Artifact collection (the honest cross-check on all self-report) and the
  retrospective framed as the thing they were doing anyway.
- **What data?** Submitted repo, deploy URL, commit history, dependency manifest (`[PROVEN]`
  artifact evidence); `checkpoint` kind=END; team retro template.
- **What questions?** What did they *actually* wire in (vs what they said)? What was the hardest
  part? What would they change?
- **Who captures it?** `ARTIFACT` ingestion; the demo/retro structured as an interview
  ([capture-system.md](../capture-system.md)).
- **How much burden?** MED — but it is the retro they would do anyway, lightly structured; `channel
  = ARTIFACT_SUBMISSION | CHECKPOINT`.
- **What must NEVER happen?** Self-report is never taken as ground truth where an artifact can
  verify it; the dependency manifest is the arbiter of "did they really use it."

## DEMO

- **What matters?** The pitch as a structured exit interview; judging; scheduled client
  observation.
- **What data?** Demo content (what built, tools, hardest part, what they'd change); judging
  outcomes; client-observation windows (scheduled, disclosed).
- **What questions?** The full team story close-out — what shipped, with what, and the narrative of
  why.
- **Who captures it?** `INTERVIEWER` structures the pitch prompts; clients observe only on a
  **scheduled, disclosed** basis.
- **How much burden?** LOW — they were presenting anyway.
- **What must NEVER happen?** Clients never conduct surveillance, never see raw researcher notes or
  unreviewed quotes, and never interfere ([client-protocols.md](client-protocols.md),
  [dashboard-spec.md](dashboard-spec.md) Part XXXVI). Observation is aggregate-oriented and
  scheduled, not roaming over individuals.

## POST_EVENT

- **What matters?** Exit interview, the handoff to follow-up, the continuation anchor.
- **What data?** Stratified exit interviews (by segment: ADOPTER / NON_ADOPTER / SWITCHER /
  ABANDONER / R&D_FAILURE); end-of-event synthesis into team trajectories and the claim/evidence
  graph.
- **What questions?** What did they learn? What will they keep using? (The day-0 anchor for the
  30/90-day continuation measure.)
- **Who captures it?** `INTERVIEWER` (sampled via [adaptive-sampling.md](adaptive-sampling.md));
  `LEAD_RESEARCHER` owns synthesis.
- **How much burden?** MED — exit interviews are the single largest explicit debit; the budget is
  checked before scheduling.
- **What must NEVER happen?** No conflating "said they'll keep using it" with retention — retention
  is measured later, off our property, not asserted at exit.

## FOLLOWUP_7 / FOLLOWUP_30 / FOLLOWUP_90

The retention asset no other hackathon has ([longitudinal-followup.md](longitudinal-followup.md)).

- **What matters?** Whether the product use *continued* unprompted; what continued of the project
  itself.
- **What data?** `checkpoint` kinds `FOLLOWUP_7 | FOLLOWUP_30 | FOLLOWUP_90`; `CONTINUATION_DECISION`
  trigger (`continuation`, 20s); opt-in artifact re-check.
- **What questions?** Did they retain the tool? Did the project live? Why / why not? (EXPOSURE ≠
  ACTIVATION ≠ VALUE ≠ RETENTION — retention is the only thing these phases can measure.)
- **Who captures it?** `INTERVIEWER` + async follow-up; `DATA_STEWARD` re-checks consent at each
  wave (revocation drops the participant from future cuts).
- **How much burden?** LOW per wave; `channel = FOLLOWUP`, spaced so it never feels like a standing
  obligation.
- **What must NEVER happen?** No follow-up of a participant who revoked the relevant scope; consent
  is re-resolved at query time for every wave, not assumed from registration.

## The shape of burden across the event

```
 burden ^                                                            exit
 spent  │  baseline                                              interview
 (illus)│   ▓▓        build-start    mid-build                    ▓▓▓
        │   ▓▓  ░       ▓▓      ░░     ▓▓          late-build       ▓▓▓   followups
        │   ▓▓  ░  ░    ▓▓  ░   ░░  ░  ▓▓   ░   ░    · (quiet) ·     ▓▓▓   ░   ░   ░
        └──────────────────────────────────────────────────────────────────────────►
          PRE  ARRIVAL  B_START  EARLY   MID        LATE      SUBMIT/DEMO   7 / 30 / 90
 Heaviest at the EDGES (cheap, fresh); near-silent in LATE_BUILD crunch. The total across
 the whole arc stays under the ≤~18-minute budget (participant-burden.md). Illustrative.
```

The phases differ, but the rule does not: spend explicit attention at the freshest, cheapest
moments, stay silent in deep flow, and never let the research outweigh the weekend.
