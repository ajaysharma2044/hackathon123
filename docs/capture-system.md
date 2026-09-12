# Capture System

The complete architecture for observing — with consent and methodological discipline — how elite
builders choose, reject, switch, and stick with tools, and what happens after. Built on
[research-data-model.md](research-data-model.md); every capture method is classified.

**Classification keys used throughout:**
`[PROVEN]` strong precedent, technically straightforward · `[PLAUSIBLE]` strong analog, unvalidated
for our system · `[EXPERIMENTAL]` needs testing · `[HIGH-RISK]` privacy/legal/methodological/
participant-experience danger. And epistemic status: `KNOWN / LIKELY / UNKNOWN / CONTRADICTED /
UNTESTED`.

## First principles

1. **Capture through systems people intentionally use, not surveillance of the person.** Prefer
   brokered credentials, event-system actions, submitted artifacts, and short embedded prompts.
   **No keystroke logging, no desktop/screen monitoring, no camera analysis, no private-message
   scraping, no hidden tracking.** These are `[HIGH-RISK]` and out of scope permanently, not just
   for Event 1.
2. **Disclosed even when invisible.** A participant may not *feel* the brokered-key telemetry, but
   they were told exactly what it measures. Invisible-but-disclosed is the target quadrant of the
   extraction frontier ([monetization-map.md](monetization-map.md)); invisible-and-undisclosed is
   forbidden.
3. **Minimum necessary form.** For every field: what research question does it answer, which buyer
   could value it, can it be derived later instead, and what is the least sensitive form that still
   answers the question. If it fails all of these, it is not collected.
4. **SAID and DID are different evidence.** Self-report and observed behavior are captured on
   separate axes (`is_self_report`) and never silently merged.
5. **Absence of behavior ≠ inability.** Every capturable behavior is paired with the `Opportunity`
   that was offered, so "didn't use the mentor" is distinguishable from "was never offered one."

## Architecture (data flow)

```
       PEOPLE INTENTIONALLY USE                    WE OFFER / OBSERVE
   ┌──────────────────────────────┐        ┌──────────────────────────────┐
   │ sponsor products (brokered    │        │ checkpoints  observer logs    │
   │ keys) · event app · repo/     │        │ interviews · mentor notes ·   │
   │ deploy · opt-in integrations  │        │ opportunities offered         │
   └──────────────┬───────────────┘        └───────────────┬──────────────┘
                  │ raw, idempotent, source-tagged          │
                  ▼                                         ▼
        ┌─────────────────────  RAW EVIDENCE STORE  ─────────────────────┐
        │  EvidenceEvent (tri-temporal, consent-tagged, provenance)      │
        │  QualitativeObservation (raw text kept forever)                │
        │  ProductUsageEvent (raw sponsor telemetry, pre-mapping)        │
        │  ConsentGrant / ConsentRevocation ledger                       │
        └───────────────────────────────┬───────────────────────────────┘
                                         │ consent-scoped, point-in-time
                                         ▼
        DERIVED LAYER  → episodes · funnels · switching matrix · themes · states · factors
                                         │ provenance + model_version
                                         ▼
        RESEARCH ENGINE  → question → hypothesis → pre-registered test → finding (L1–L4)
                                         │ min-cell-size, aggregate-only enforcement
                                         ▼
        SPONSOR DELIVERABLE (aggregate) │ PARTICIPANT-OPT-IN DISCLOSURE (individual) │ PUBLIC REPORT
```

The consent-scoped, point-in-time query gate ([engine/capture.py](../engine/capture.py)) sits
between raw and everything downstream. Nothing reaches a sponsor without passing it.

## Participant lifecycle capture

### Phase A — Application `[PLAUSIBLE]`

The application is a research instrument *and* a selection instrument, and those two purposes
must not contaminate each other. Field-by-field discipline (Part 2 of the brief), abbreviated:

| Field | Research question it answers | Form | Verdict |
|---|---|---|---|
| Prior projects (structured: repo + role + stack) | baseline capability; later validates selection rubric | structured, not free text | **Required** |
| Current tool/AI-coding stack | the *pre-existing familiarity* covariate — essential to separate adoption from retention | multi-select + "other" | **Required** |
| Infrastructure stack | infra-selection baseline | multi-select | **Optional** |
| School / major / year | stratification, generalizability boundary | structured | **Required** |
| Founder / career interest | routes VC vs recruiting discoverability later | structured, non-binding | **Optional** |
| Track/challenge preference | assignment + a neutral research signal | ranked | **Required** |
| Prior team relationships | the prior-collaboration graph (a real VC signal) | names/handles, opt-in | **Optional** |
| "What are you building outside this event" | intent + a leading-indicator signal | short free text | **Optional** |
| "What problems do you care about" | can act as a *neutral research instrument* without touching selection | short free text | **Optional, research-only** |
| Demographics / protected traits | — | — | **Do NOT collect for research.** Only what a fairness audit of selection legally requires, siloed from the research store |

**Neutral-instrument design:** the "what problems do you care about / what would you build with
$X" questions are scored **only** by the research pipeline, never surfaced to selection reviewers,
so they cannot bias admission. This gives an early, large-n (all applicants, not just the 200)
signal on what elite students reach for — captured before anyone is selected, invisible as
research to the applicant. `[EXPERIMENTAL]` — the firewall between research-scoring and selection
must be real (separate stores, separate access) or it is worthless.

### Phase B — Selection / pre-event baseline `[PROVEN]`

Capture the **SAID** state before the event so it can be compared to the **DID** state during it.
This SAID/DID gap is first-class, not a footnote.

- stated tool preferences, product familiarity (Likert), intended project type, baseline workflow
- prior-collaboration graph (from application, opt-in)
- **current startup/project state** — the day-0 anchor for the 30/90-day continuation measure
- baseline attitudes toward AI-assisted coding (the AI-productivity module's pre-measure)

All stored as `EvidenceEvent(is_self_report=true, source_kind=SURVEY)`. The whole value is that
they are timestamped *before* exposure, so later divergence is measurable.

### Phase C — Arrival / onboarding `[PROVEN for event-system, PLAUSIBLE for product]`

Formalized as event streams (see taxonomy, [Part 4 / schema](../schema/001_core.sql)):
`PRODUCT_EXPOSED → PRODUCT_ACCOUNT_CREATED → ONBOARDING_STARTED → FIRST_VALUE_REACHED`, plus
`ERROR_ENCOUNTERED`, `HELP_REQUESTED`, `TOOL_ABANDONED`. The onboarding funnel and time-to-first-
value come from here. Event-system events (workshop attendance, key issuance) are `[PROVEN]`;
product-side onboarding events need brokered keys or sponsor cooperation (Part 3).

### Phase D — Active building `[MIXED — see per-stream classification]`

The highest-value window. Captured **only** through the allowed channels:

| Stream | Method | Class |
|---|---|---|
| Tool selected / activated / used / feature used | brokered API keys → `ProductUsageEvent` | `[PLAUSIBLE]` for sponsor products; `[UNKNOWN]` for competitors (off our property) |
| Error / retry / abandonment | brokered API telemetry (server-side truth) | `[PLAUSIBLE]` |
| **Tool switched / returned** | checkpoint "what are you using now" (6-hourly) + dependency manifest at submit + brokered-key silence | `[EXPERIMENTAL]` — the hardest signal; triangulated, never asserted from one source |
| Task created/accepted/completed, blocker | event-app kanban (opt-in) + checkpoint self-report | `[PLAUSIBLE]` |
| Artifact created / deployed / submitted | submitted repo, deploy URL, commit history, dependency file | `[PROVEN]` |
| Team formed / roles / handoffs / persistence | event-app team state + checkpoint | `[PLAUSIBLE]`; prior-collab from application |
| Mentor / sponsor-engineer sessions | booking system + structured mentor note | `[PROVEN]` for occurrence, `[PLAUSIBLE]` for content |
| Researcher observation | trained observer logs against the codebook | `[PLAUSIBLE]`; always `confidence<1.0`, `is_self_report=false` but inferred |
| Context (time, stage, track, incentives, team size, prior familiarity) | derived from registry + snapshotted onto episodes | `[PROVEN]` |

**Explicitly excluded (`[HIGH-RISK]`, never built):** desktop/IDE keystroke capture, screen
recording, camera/attention monitoring, Slack/Discord DM scraping, any always-on background agent.

## Brokered product instrumentation (Part 3) — the highest-value system

The mechanism that turns `tool_switched` from a guess into server-side ground truth.

```
Participant requests sponsor tool access THROUGH our system
        → we issue a participant/team-scoped BrokeredCredential
        → traffic flows either via a thin proxy OR the sponsor's own per-key telemetry export
        → permitted events map through a SponsorTelemetryContract into our neutral schema
        → raw lands in ProductUsageEvent; mapped lands in EvidenceEvent
```

Objects: `BrokeredCredential`, `ProductUsageEvent`, `SponsorTelemetryContract`, `TelemetryField`,
`DataRetentionRule` (all in [schema/001_core.sql](../schema/001_core.sql)).

### What is realistically capturable — honest per-mode read

| Capture mode | What it yields | Class | Notes |
|---|---|---|---|
| **API proxy we run** (we mint the key, traffic passes through us) | request timestamps, endpoint, status, error class, cadence, silence | `[PLAUSIBLE]` | Works for HTTP APIs (model APIs, Stripe test, MongoDB Atlas Data API). **Does not work** for SDKs that talk directly to the sponsor, local tools, or anything not routed through us |
| **Sponsor per-key telemetry export** (they mint via our request, share events for our keys) | activation, first-value, feature flags, retention on their side | `[PLAUSIBLE]`, contract-dependent | Requires the `SponsorTelemetryContract` to be a term of the research tier ([measurement.md](measurement.md)). A sponsor who won't provision this buys activation counts, not research |
| **Artifact inspection** (dependency manifest, imports, deploy target) | what was *actually* wired in, independent of self-report | `[PROVEN]` | The honest cross-check on both proxy and self-report |
| **Local/desktop tools** (e.g. a local coding assistant) | almost nothing without invasive capture | `[HIGH-RISK]/[UNKNOWN]` | We do **not** instrument these locally. Fall back to checkpoint self-report + artifact traces |
| **Competitor products** | nothing server-side (not our property) | `[UNKNOWN]` | The `unconstrained baseline` and switching-*away* signal come from checkpoints + dependency files, never telemetry |

### The distinctions the instrumentation must preserve

```
API_CALL           a request happened
   ≠ MEANINGFUL_USE  the call was part of building something real (not a tutorial ping / retry storm)
EXPOSURE           the product was put in front of them / required
   ≠ ACTIVATION      they reached first successful value (FIRST_VALUE_REACHED, sponsor-defined)
   ≠ VALUE           they used it in the shipped project (artifact confirms)
   ≠ RETENTION       they used it again, unprompted, after the event (7/30/90, off our property)
```

`MEANINGFUL_USE` is a **derived, versioned** classification (heuristic: calls tied to a project
artifact, above a cadence floor, not in the tutorial window) — never raw, always `confidence<1.0`.
`FIRST_VALUE_REACHED` must be **defined by the sponsor per product before the event** and pinned in
the `Experiment` record, or the funnel is a dial (see [measurement.md](measurement.md) operational
definitions).

**Security/privacy guardrails on brokering:** keys are per-participant and revocable; the proxy
stores metadata (timing, endpoint, status), **never request/response bodies** unless a specific
disclosed study needs them and the participant consented; `DataRetentionRule` sets a hard TTL on
raw telemetry; a brokered key is destroyed on `PRODUCT_TELEMETRY` revocation.

## Capturing the "why" (Part 5)

Telemetry gives WHAT; without WHY it is a shape with no mechanism. The qualitative architecture
links a quote to the exact behavioral event.

```
EvidenceEvent  TOOL_SWITCHED @ 16:32 (product=A→B)
      │  evidence_link (same episode + explicit link)
      ▼
QualitativeObservation  "auth setup took too long and my teammate already knew B"  [raw text kept]
      │  ThemeAssignment (model_version, human_review_state)
      ▼
Theme  friction:authentication_setup (severity:high, stage:onboarding)   ← a HYPOTHESIS, not truth
```

Mechanisms, by burden (lightest first): 20-second checkpoint prompts, **post-event triggered
micro-prompts** (fired right after a detected switch/error — the highest-signal, lowest-burden
moment), post-project retrospectives, stratified structured interviews, team retrospectives,
mentor notes, observer field notes, 7/30/90 follow-up interviews.

Objects: `QualitativeObservation` (raw text, immutable), `Theme` (codebook entry), `ThemeAssignment`
(label + `model_version` + `human_review_state`), `InterviewExcerpt`, and `evidence_link` (quote↔event).

**LLM themes are labels, not ground truth.** Stored beside the raw text with the model version and
a human-review flag. The pipeline must be able to discover that *"pricing complaints are frequent
but do NOT predict churn, while auth friction DOES"* — which requires theme frequency and outcome
prediction to be **separate, testable quantities**, never conflated into "top complaints = top
problems." This is a first-class capability, encoded as: `ThemeFrequency` (descriptive, L1) is a
different object from a `Finding` that a theme predicts an outcome (L2+, tested).

## Opportunity & context modeling (Part 10)

Every offer is recorded as an `Opportunity` with a response, so behavior is never read as ability
alone:

```
Opportunity(kind ∈ {TOOL_EXPOSURE, MENTOR_SESSION, LEADERSHIP_ROLE, RECRUITER_INTRO,
                    VC_INTRO, DESIGN_PARTNER_INTRO}, offered_at, offered_to, context_snapshot)
   → response ∈ {ACCEPTED, DECLINED, IGNORED, EXPIRED, WITHDRAWN}
```

Conceptual model, encoded as an analysis constraint (not a stored belief):

```
ObservedBehavior = f(Ability, Opportunity, Context, MotivationState, Noise)
```

**We do not infer stable traits.** No personality, intelligence, "quality," or protected-trait
inference — structurally forbidden ([capture-risk-register.md](capture-risk-register.md), Part 20).
Context (`context_snapshot`) travels with every episode: project type, track, team composition,
event stage, prize incentives, sponsor exposure, prior experience, prior product familiarity,
support received, challenge difficulty, time remaining. A finding that ignores context is a
finding about our event, not about the tool.

## Consent as a system (Part 7)

The scopes are enumerated in [research-data-model.md](research-data-model.md). The **ledger** is
append-only `ConsentGrant`/`ConsentRevocation` events; **effective consent** is computed as-of
query time; enforcement is at **query time** in [engine/capture.py](../engine/capture.py), tested
in [engine/test_capture.py](../engine/test_capture.py).

Requirements, and how each is met:

| Requirement | Mechanism |
|---|---|
| Explicit, understandable | Per-scope opt-in at registration + just-in-time re-prompts (e.g. before a recruiter intro) |
| Revocable | `ConsentRevocation` event; next scoped query excludes the participant |
| Timestamped, versioned | Every grant references a `consent_text_version` |
| Enforced at query time | Query carries a `purpose`; the gate resolves effective consent from the ledger, not the row's stored scope |
| No downstream use beyond scope | `AGGREGATE_RESEARCH` cannot emit individual grain; `*_DISCOVERABILITY` is the only individual-disclosure path |
| Revocation ≠ silent history rewrite | Published `Finding`s snapshot the consent state and n at publish time (provenance); re-runs respect current consent. A withdrawn participant drops from future cuts but does not falsify a past, already-delivered report |
| Legal deletion | A `deletion_tombstone` removes raw payload while keeping a non-identifying audit shell, satisfying GDPR/FERPA erasure without corrupting counts already published in aggregate |

**Already-delivered recruiting evidence on revocation:** defined policy (per [data-model.md](data-model.md)
open item) — on `RECRUITING_DISCOVERABILITY` revocation, the `WorkEvidenceRecord` is withdrawn from
the discovery surface immediately; evidence a specific employer already downloaded is out of our
control and the consent text says so plainly. This must be a stated term, decided before Event 1.

## The extraction frontier, as a budget (Part 14)

Every capture mechanism carries four scores (`ResearchValue`, `ParticipantBurden`, `ExperienceImpact`,
`PrivacyRisk`) and a per-participant **research-minutes budget**. Conceptually
`CaptureEfficiency = ExpectedInformationGain / ParticipantBurden` — used to rank, not to blindly
maximize. Full budget model and the "never feel experimented on" rule are in
[event1-instrumentation-plan.md](event1-instrumentation-plan.md) and enforced in Part 16's capacity model.

---

# Organic In-Flow Feedback Capture

The goal: get their feedback on *everything*, continuously, while they build — but embedded so
naturally it never feels like a survey. The design rule that makes this safe:

> **Subtle means low-friction and well-timed. It never means covert.** Every mechanism below is
> disclosed at consent. "Track as much as possible" is bounded, always, by the research-minutes
> budget, the consent scopes, and the hard no-surveillance boundaries
> ([capture-risk-register.md](capture-risk-register.md)). Organic is a UX property, not a
> loophole. There is no hidden capture in this system, ever.

## The core trick: capture things they were going to do anyway

The best in-flow capture is not *added* to the builder's flow — it *is* the flow, lightly
structured. Ranked by burden (lowest first):

| Mechanism | What it captures | Why it's organic (value to the builder) | Class |
|---|---|---|---|
| **Instrument the help they seek** | friction type/severity/stage, in the moment | they asked a mentor/sponsor engineer *because they wanted help* — the interaction they sought IS the data; a trained mentor logs it against the codebook | `[PL]` |
| **Artifacts they write anyway** | actual stack, decisions, what shipped | commit messages, PR descriptions, README, dependency manifest — zero prompts, honest record | `[P]` |
| **`/blocked` (or a reaction) in the event chat** | the blocker + timestamp | one word both **summons a mentor** and logs the blocker — it helps them *right now* | `[PL]` |
| **Doc/tool reactions** (🔥 helped / 😕 confusing) | per-artifact sentiment, ambient | one tap; a legitimate way to vent friction on a bad doc; sponsors love per-page signal | `[E]` |
| **Post-moment micro-prompt** (fired by telemetry) | the "why" behind a detected error/switch/stall | appears *in the tool they're already in*, at the freshest moment, one line, skippable, budgeted | `[E]` |
| **The 20-second "rubber duck" voice note** | rich qualitative, unprompted-feeling | framed as rubber-duck debugging — talking through a stuck point genuinely helps builders think; transcribed + themed | `[E]` |
| **Checkpoint reframed as mentor-matching** | what/tools/blocker/stuck-level | the answer *routes them to a relevant mentor or a meal/slot* — it buys them something, so it isn't a tax | `[PL]` |
| **The demo/pitch as a structured interview** | what built, tools, hardest part, what they'd change | they were pitching anyway; the prompts structure the exit qualitative into the thing they already do | `[P]` |
| **Team retro template** | team decisions, coordination, tool choices | good teams retro anyway; a light template captures it | `[PL]` |
| **Observer floaters** | ethnographic friction at scale | the builder just experiences a friendly expert wandering by | `[PL]` |

## The timing principle: capture at the moment of freshest signal

A survey at the end asks people to *remember* why they switched at hour 14. An in-flow prompt
fired by the `TOOL_SWITCHED`/`ERROR_ENCOUNTERED` event asks them **while it's still on their
screen** — higher signal, lower burden, and it feels relevant rather than random. The brokered-key
telemetry is what makes this possible: the *what* (detected server-side) triggers the *why* (one
tap, in context). This is the qualitative↔behavioral link ([Part 5 above]) operating in real time,
not reconstructed after the fact.

## The frequency governor (so "as much as possible" doesn't become "too much")

Every participant carries a **research-minutes budget** and a **prompt-rate limit**. The system
spends the budget on the highest-`CaptureEfficiency` moments (a fresh switch/error) and stays
silent otherwise. A builder in deep flow who hasn't hit friction gets *no* prompts — the absence
of a prompt is itself correct behavior. The budget is the mechanism that keeps the golden goose
alive: a participant should end the weekend having spent maybe 15–20 minutes on all research
combined, most of it feeling like help they wanted.

## What "track as much as possible" does and does not mean here

**Does:** ambient, disclosed, low-tap signals on things they already touch (docs, tools, help,
artifacts, pitches); telemetry-triggered micro-prompts at the freshest moment; rich voluntary
qualitative (voice notes) framed as an aid.

**Does not:** keystroke/screen capture, DM scraping, always-on recording, attention monitoring,
or any prompt cadence that turns the build into a study. Those remain `[HR]` boundaries regardless
of how much signal they'd yield — because the front end staying genuinely excellent is worth more
than any one weekend's data ([monetization-map.md](monetization-map.md) extraction frontier).
