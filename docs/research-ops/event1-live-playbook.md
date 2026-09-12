# Event 1 Live Playbook & Final Synthesis

The operational playbook for running the [live research OS](live-research-os.md) at Event 1, a
hour-by-hour walk-through from the participant's seat, ten tabletop simulations, the minimum-viable-
vs-ideal split, and the **60-question final synthesis** the brief requires. Everything here assumes
the [WTP gate](../event1-design.md) has been passed and a sold study has sized the event.

## The 72 hours, from the participant's seat

The acceptance test is the participant's experience. Here is the weekend as *they* feel it — with
the research that is actually happening, most of it invisible or help-shaped.

```
  HOUR   PARTICIPANT EXPERIENCE                      RESEARCH HAPPENING (mostly invisible)
  ─────  ──────────────────────────────────────────  ──────────────────────────────────────────
  PRE    fill a short application; a baseline survey   baseline SAID state, stack, familiarity
         a week before (~4 min, at home)               (ambient — before the weekend)
  0      arrive, check in, consent (plain, modular)    consent ledger populated (consent-design.md)
  1–2    team formation, orientation, pick a problem   START checkpoint (~1 min, routes to a mentor)
         get brokered keys for sponsor tools           team baseline; choice-set begins forming
  2–10   BUILD. long uninterrupted block.              telemetry passive; observers roam; mentors
         help on tap, good food                        help + log lightly. NO prompts unless a
                                                        high-signal switch/error fires one.
  10     a switch happens (tool A→B)                   telemetry detects it → ONE micro-prompt at
                                                        the fresh moment: "main reason you switched?"
  12     MID checkpoint (tied to the next meal)        ~1 min; the "what are you using now" delta
  12–30  BUILD. debugging, a pivot, a blocker          /blocked summons a mentor; mentor note logs
         mentor rescues the auth setup                  the friction + intensity (a confounder flag)
  30     a field researcher watches for a minute,      a short contextual interview IF this team was
         asks one question about the pivot              sampled and is in a SHORT_INTERVIEW_OK window
  30–60  BUILD. completion pressure, feature cutting   observers catch the final-architecture choices
  ~60    (sampled subset) a 12-min exit interview      the deeper "why"; over-samples never-activated
  66     SUBMIT repo + deploy                           artifact + dependency manifest (honest record)
  68     DEMO / pitch (structured prompts)             the demo IS the END retrospective-interview
  72     close. prizes. "that was an amazing event."   the pulse: was research intrusive? felt watched?
  +7/+30/+90  a check-in on your project (incentivized) retention, continuation, switching — the asset
```

**The count for a typical participant:** a baseline, ~3 checkpoints (each tied to something they
wanted), maybe ~2 well-timed prompts, and — only for a sampled subset — one exit interview. A
handful of explicit touches across 72 hours, inside long build blocks. That is the target.

## The war room, hour by hour (the research side)

```
  ARRIVAL→BUILD-START   stand up the boards; confirm telemetry + consent flowing; seed the backlog
                         with the sold studies' questions (question_backlog.py)
  EVERY ~6 HOURS        a synthesis pass: leads turn the shift's notes into codes → emerging themes;
                         write an analytic memo (analytic-memos.md); re-prioritize the backlog
  ON EACH HIGH-SIGNAL   route() the incident; fire a prompt or flag an interview; the sampler names
   INCIDENT              WHO to talk to next, negative cases FIRST (adaptive-sampling.md)
  CONTINUOUSLY          watch mentor-queue depth + experience pulse; log any event intervention with
                         its validity impact (event-adaptation.md)
  LATE BUILD→DEMO       shift from capture to the deeper sampled interviews of the already-decided
  POST                  assemble team trajectories; build the claim/evidence graph; schedule follow-up
```

This is the live loop from [live-research-os.md](live-research-os.md) running on a clock.

## Ten tabletop simulations

Dry-run the operation against the scenarios that will actually happen (Part XLIII).

| # | Scenario | How the system responds |
|---|---|---|
| **A** | 15 teams need AI mentors at once | `queue_depths` shows the AI_ML spike → Mentor Lead adds capacity / opens office hours; logged as an OPERATIONAL intervention. Routing picks least-loaded mentors ([mentor-system.md](mentor-system.md)). |
| **B** | 8 teams switch away from one database | war room sees the switching-matrix cell spike → fire post-switch prompts at the fresh moment; sampler schedules switchers **and** non-switchers who hit the same friction but stayed (negative case). |
| **C** | A company engineer is rescuing every team | each rescue logged as a `mentor_interaction` with HEAVY intensity + vendor flag; their product's "success" is split into `VENDOR_RESCUED_SUCCESS` vs `ORGANIC_SUCCESS` ([mentor-interventions.md](mentor-interventions.md)) — not reported as organic. |
| **D** | Researchers are interrupting too often | `prompts_annoying`/`felt_watched` rise on the pulse → tighten the burden cap, widen the prompt gap, pull observer density ([participant-burden.md](participant-burden.md)); logged. |
| **E** | An emerging pattern contradicts the client's hypothesis | the memo records it as an honest finding; the [evidence graph](evidence-graph.md) assembles supporting + contradicting evidence; the pre-registered falsification criteria mean we report it — findings can come back negative. |
| **F** | Challenge rules need clarification midway | clarify the *instructions* (ADAPTABLE) — but `challenge_rules` as a study spine is LOCKED; if the change is material, split before/after and log it INVALIDATING unless pre-specified ([event-adaptation.md](event-adaptation.md)). |
| **G** | A team produces an unexpected high-value use case | `UNEXPECTED_USE_CASE` trigger → flag for a deeper interview + a 7/30/90 follow-up priority ([longitudinal-followup.md](longitudinal-followup.md)). |
| **H** | A participant withdraws research consent | a `ConsentRevocation` event; next scoped query excludes them (query-time enforcement, nothing deleted); already-published aggregates keep their provenance snapshot ([consent-design.md](consent-design.md)). |
| **I** | 5 teams fail using the same approach | the R&D failure map: cluster the `RD_HYPOTHESIS_FAILURE` incidents by which assumption failed; this *is* the commercial value ([team-trajectories.md](team-trajectories.md)). |
| **J** | Researchers disagree about interpretation | the disagreement is preserved — the field note's `alternative_interpretation`, competing claims in the evidence graph, and the memo's "alternative explanations" field. We do not force consensus; we sample to resolve it. |

## Minimum viable vs ideal research OS

```
MINIMUM VIABLE (Event 1 — mostly disciplined humans + a spreadsheet)
  ✔ consent gate (exists: engine/capture.py)         ✔ brokered keys for the primary product
  ✔ a field-note form enforcing fact ≠ interpretation ✔ a ≤20-second mentor log
  ✔ trigger→prompt routing run by a human war room    ✔ a per-participant burden tally
  ✔ START/MID/END checkpoints                         ✔ stratified exit interviews
  ✔ 7/30-day follow-up                                ✔ pre-registration + operational definitions

IDEAL (by Event 3–4 — the engines become software)
  ✚ telemetry-fired in-app micro-prompts              ✚ a live war-room dashboard (dashboard-spec.md)
  ✚ the adaptive sampler suggesting the next interview ✚ the evidence graph as software
  ✚ AI-assisted first-pass coding with human gates    ✚ the 90-day panel as a standing product
```

The [engines in this repo](../../engine/) are the reference implementation of the *invariants* — the
burden cap, the fact/interpretation split, the promotion gate, the timestamped interventions — so the
software, when built, is built against tested correctness properties rather than prose.

---

# The 60-question final synthesis

Direct answers. Where a number appears it is illustrative; WTP remains UNKNOWN ([STATE.md](../STATE.md)).

**1. What exactly should a field researcher do?** Circulate an assigned zone (plus roaming), observe
natural team interaction, record critical incidents and decisions, run short in-the-moment
interviews, route help, and bring it to war-room synthesis — keeping fact separate from
interpretation ([field-researcher-guide.md](field-researcher-guide.md)).

**2. How many do we need?** ~1 field researcher per ~25–30 participants for primary coverage, plus
leads/interviewers/steward. For Event 1 at 150–200: ~5–8 field researchers, ~13–18 research staff
total ([event1-staffing.md](event1-staffing.md)).

**3. What should they record?** The standardized field note: observed fact, direct quote,
decision-in-flight, tools involved, prior→current state, outcome, a labeled interpretation **and** a
competing one, context, confidence ([field-note-system.md](field-note-system.md)).

**4. What should they never record?** Screens, keystrokes, private messages, covert audio, protected
traits, or any person score. When unsure, don't — ask a lead.

**5. How should they approach a team?** "Mind if I watch for a minute? Ignore me." Ask about the
thing happening *now*, one question, let silence work, never finish the participant's story.

**6. When should they interrupt?** After a switch, after help resolves, after submission, at a meal,
or in a booked slot — and only if the team is in a `MICRO_PROMPT_OK`+ window and under burden
([interruption-policy.md](interruption-policy.md)).

**7. When should they absolutely not interrupt?** Minutes before a deadline, mid-debug, during
judging, a critical hardware test, while presenting, or during sleep hours.

**8. Highest-value event triggers?** `SWITCH`, `ABANDONMENT`, `TOOL_SELECTION`/`TOOL_REJECTION`,
`TECHNICAL_FAILURE`, `DOCUMENTATION_FAILURE`, `CREDIT_USE`/`CREDIT_IGNORE`, `UNEXPECTED_USE_CASE`,
`CONTINUATION_DECISION`, and the interview-only `MAJOR_PIVOT`/`REPEATED_HELP`/`RD_HYPOTHESIS_FAILURE`
([critical-incidents.md](critical-incidents.md)).

**9. Micro-prompts after each trigger?** One line, at the fresh moment: switch→"main reason you
switched?", failure→"what did you expect to happen?", credit→"did the credit affect your choice?"
([micro-prompts.md](micro-prompts.md)).

**10. What requires a deeper interview?** Rich, non-reducible moments: major pivots, repeated
friction, R&D failures, unexpected use cases, and sampled outcome segments ([adaptive-questioning.md](adaptive-questioning.md)).

**11. How should questions branch?** As explicit, auditable trees: each answer selects the next
question (switch→setup_friction→documentation→"what were you looking for?"), bounded by a burden cap
([adaptive-questioning.md](adaptive-questioning.md), [`adaptive_questions.py`](../../engine/adaptive_questions.py)).

**12. How do mentors fit into research?** They help first; the help interaction is the capture. A
help request reveals a blocker; repeated requests reveal systemic friction ([mentor-system.md](mentor-system.md)).

**13. What should mentors log?** Team, category, problem, tool, state, question, intervention,
intensity, outcome, follow-up, research-flag — in ≤~20 seconds ([mentor-system.md](mentor-system.md)).

**14. How do we keep mentor burden tiny?** A ≤20-second structured log, mostly taps; most fields
optional; the log buys the mentor nothing-but-one-tap and the research everything.

**15. Product success vs mentor-assisted success?** Operational intensity (NONE/LIGHT/MODERATE/
HEAVY) + a vendor flag split outcomes into `ORGANIC`/`ASSISTED`/`VENDOR_RESCUED` — a **stratification,
not a causal claim** ([mentor-interventions.md](mentor-interventions.md)).

**16. How should the mentor queue work?** Problem category → routed mentor category → priority →
least-loaded available mentor → capture → resolution; aggregate queue depths are the ops view
([`mentor_routing.py`](../../engine/mentor_routing.py)).

**17. What is the research war room?** The live operations room that turns raw observations into
emerging understanding *during* the event, and drives the next question ([research-war-room.md](research-war-room.md)).

**18. What should it show?** Active teams, blockers, switching events, product usage, mentor demand,
the trigger + interview queues, emerging themes, negative cases, and candidate follow-ups — team/
event-level, never participant surveillance ([dashboard-spec.md](dashboard-spec.md)).

**19. How often should researchers synthesize?** Every ~6 hours (shift cadence): notes → codes →
themes → a memo → a re-prioritized backlog ([analytic-memos.md](analytic-memos.md)).

**20. How should new questions be created?** Emergent questions enter the backlog with their
emergence time and get prioritized; a contradiction can reopen a saturated question
([`question_backlog.py`](../../engine/question_backlog.py)).

**21. How should adaptive sampling work?** Pick the next interview by evidence gap — negative cases
first, then confirming deficits, then coverage gaps — burden- and availability-aware
([adaptive-sampling.md](adaptive-sampling.md)).

**22. How do we deliberately find negative cases?** For every explanation, ask "what would make this
wrong?" and sample the disconfirming segment before the explanation hardens ([negative-case-analysis.md](negative-case-analysis.md)).

**23. How do we prevent confirmation bias?** Structurally: fact≠interpretation at capture, a required
competing interpretation, negative-case sampling, and a promotion gate that refuses a claim without a
completed disconfirmation search ([evidence-graph.md](evidence-graph.md)).

**24. How do we track evolving team reasoning?** The team trajectory: an ordered, re-derivable arc of
decision episodes with provenance to raw ([team-trajectories.md](team-trajectories.md)).

**25. How do we capture R&D failure properly?** The R&D reasoning trajectory — hypothesis→experiment
→result→which assumption failed→next — because the value is the failed paths + why ([team-trajectories.md](team-trajectories.md)).

**26. How do we capture product switching properly?** Triangulated `SWITCH` detection (telemetry
silence + dependency delta + checkpoint delta) + a fresh-moment "why" prompt + the switching matrix.

**27. What does a team story look like?** PROBLEM→PLAN→TOOL SET→APPROACH→BLOCKER→HELP→DECISION→
SWITCH/PIVOT→SECOND APPROACH→ARTIFACT→OUTCOME→CONTINUATION, each node carrying behavior + explanation
+ evidence ([team-trajectories.md](team-trajectories.md)).

**28. How do we turn notes into themes?** RawQuote→Observation→Code→Subtheme→Theme, with the raw
text kept beside every label and human review of LLM codes ([qualitative-coding.md](qualitative-coding.md)).

**29. How do we turn themes into claims?** A claim assembles supporting **and** contradictory evidence
for a theme; frequency (descriptive) is kept distinct from a tested prediction ([evidence-graph.md](evidence-graph.md)).

**30. How does every claim remain traceable?** Each claim enumerates its evidence both ways; `trace`
walks it back to raw; it cannot promote to a Finding without that provenance ([`evidence_graph.py`](../../engine/evidence_graph.py)).

**31. Where can AI help?** Transcription, first-pass coding, theme suggestion, contradiction
detection, quote↔event linking, friction clustering, trajectory summarizing, missing-evidence and
follow-up suggestion ([qualitative-coding.md](qualitative-coding.md)).

**32. Where must humans stay in the loop?** AI must not invent statements, infer personality, score
people, infer protected traits, convert speculation to fact, or erase contradictory evidence — all
gated by human review.

**33. How should participant burden be measured?** As an append-only ledger of explicit research
seconds per participant, by channel ([participant-burden.md](participant-burden.md), [`burden_budget.py`](../../engine/burden_budget.py)).

**34. What burden is acceptable?** ≤~18 explicit research-minutes per participant across the event, a
starting cap to be tuned from the pulse — past ~25 min the experience loss dominates.

**35. How should live event adaptation work?** Adapt operations freely, log every material change
with its validity impact, and split before/after for affected questions ([event-adaptation.md](event-adaptation.md)).

**36. Which interventions invalidate research?** Changing a locked study-spine knob mid-event —
treatment assignment, credit amount, challenge rules, evaluation metric, primary outcome, stopping
rule — unless pre-specified ([`intervention_log.py`](../../engine/intervention_log.py)).

**37. What can change freely?** Mentor allocation, office hours, instruction clarifications,
operational support, food/logistics, interview targets, the backlog, and sampling.

**38. How should every intervention be recorded?** Timestamped, with reason, evidence, affected
population, change, expected effect, affected questions, and validity impact — construction without a
timestamp fails.

**39. What should happen at start/midpoint/end?** START: intended project, problem, tools, prior
familiarity, key uncertainty. MID: what changed, blocker, surprise, switch, pivot. END: what shipped/
changed/failed/worked, what you'd do differently, what you'd keep ([checkpoints.md](checkpoints.md)).

**40. What at 7/30/90 days?** Project continuation, tool retention/switching, team/startup
continuation, product reuse, new blockers, continuation reasons — on `occurred_at`, incentivized
([longitudinal-followup.md](longitudinal-followup.md)).

**41. How use Cornell's same-campus advantage?** Participants stay reachable for in-person follow-up
and a standing panel — the retention engine other events can't run ([longitudinal-followup.md](longitudinal-followup.md)).

**42. What should clients see live?** Aggregate module progress, help categories, active-team count,
challenge progress, artifact previews, scheduled observation ([client-protocols.md](client-protocols.md)).

**43. What should clients NEVER see?** Individual participant surveillance, private researcher notes,
raw unreviewed quotes, or any ability to interfere in research ([dashboard-spec.md](dashboard-spec.md)).

**44. How should consent work?** Modular, plain-language, per-scope opt-in with just-in-time
re-prompts; enforced at query time from an append-only ledger; revocable without deletion
([consent-design.md](consent-design.md)).

**45. Field researchers useful not annoying?** They route help, surface broken resources, and find
stuck teams — so their presence is welcome; every ask is well-timed and budgeted.

**46. Mentors useful not bureaucratic?** Help first, log in ≤20 seconds, mostly taps; the log never
gets between the mentor and the team.

**47. Best staffing structure?** Separate Event and Research Directors, a conflict-free data steward,
a client lead shielding research, and field researchers sized to coverage ([event1-staffing.md](event1-staffing.md)).

**48. What software must exist before Event 1?** The consent gate (exists) and brokered keys. Little
else is strictly required.

**49. What can be done manually for Event 1?** The war room, trigger routing, sampling, the backlog,
the burden tally, and coding — a disciplined process plus a spreadsheet.

**50. Minimum viable research OS?** Consent gate + brokered keys + a fact≠interpretation note form +
a ≤20s mentor log + human-run trigger routing + checkpoints + stratified exit interviews + 7/30-day
follow-up.

**51. Ideal version?** In-app telemetry-fired prompts, a live dashboard, the adaptive sampler, the
evidence graph as software, AI-assisted coding with human gates, and the 90-day panel as a product.

**52. Richest qualitative data?** Fresh-moment "why" at a real switch/failure, deep interviews on
pivots/failures/unexpected uses, the demo-as-interview, and 30/90-day continuation interviews.

**53. Mechanisms that harm the event?** Covert capture, person-scoring, cadence that taxes the build,
un-opted-in recruiting/VC disclosure, and badly-timed prompts — all excluded regardless of data value.

**54. What will companies pay most for?** The invisible-to-telemetry answers: why non-choosers didn't
choose, whether credits retain or just activate, where integration breaks, and the R&D failure map
([question-catalog.md](../question-catalog.md)).

**55. Strongest evidence?** Triangulated behavior — brokered-key telemetry + dependency manifest +
observed switch + the participant's fresh-moment "why" — cross-checked against the artifact.

**56. Hardest-to-obtain-elsewhere qualitative outputs?** Observed decision mechanisms on non-customers
and the counterfactual, the failed-R&D-path map, and true post-event retention with the "why".

**57. How should the final report integrate the evidence?** Lead with friction diagnosis + the
unconstrained baseline; behavioral funnels + switching matrices next; qualitative mechanism and team
stories as the "why"; stats and honest limitations in the appendix ([client-protocols.md](client-protocols.md), [measurement.md](../measurement.md)).

**58. What would falsify our research-method thesis?** If the rich capture produces nothing a panel/
telemetry couldn't, if burden ruins the experience, or if the instrumentation is seen to compromise
authenticity ([STATE.md](../STATE.md)).

**59. What should we test during Event 1?** The real research-minutes tolerance, whether brokered-key
instrumentation works at scale, actual retention curves, and whether the live loop produces sharper
questions than a post-event survey would.

**60. What does the actual Event 1 live playbook look like?** The hour-by-hour timeline, war-room
cadence, and ten simulations at the top of this document — run the minimum-viable OS by hand, measure
the experience relentlessly, and let the first real findings tell us what to build in software next.

---

## The final standard

> An **amazing hackathon for participants** AND an **exceptionally rich, traceable, adaptive research
> environment for clients** — and when they conflict, the participant wins. The research is mostly
> created by natural building, natural decisions, natural help requests, real failures, real
> switches, and real artifacts; smart timing, short questions, field researchers, mentor
> observations, targeted interviews, adaptive sampling, and longitudinal follow-up turn that into an
> understanding of *why*. That is the whole system.
