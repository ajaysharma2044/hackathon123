# Research Data Model

The canonical object model behind the capture system. Extends [data-model.md](data-model.md)
(entities + consent scopes) and [measurement.md](measurement.md) (capture instruments) into a
full, point-in-time-correct, provenance-preserving schema.

**Governing rule, encoded structurally:** `Evidence ≠ Claim ≠ Hypothesis ≠ Decision`. These are
four different layers with one-directional provenance. Raw evidence is immutable; everything
derived points back to the evidence it rests on and carries a `model_version`. You cannot mutate
an observation into a conclusion.

## The four layers

```
BUSINESS / GTM LAYER      Buyer · PainPoint · BuyerDecision · Engagement · Deliverable · Renewal
(separate from            — the Sponsor/Buyer Evidence Graph; never mixed with participant data
 participant research)

DERIVED / INTERPRETATION  BehavioralEpisode · FrictionCoding · ThemeAssignment · ParticipantState_t
(versioned, provenance    Funnel · SwitchingMatrix · WorkEvidenceRecord · TeamTrajectory
 → raw, model_version)    Claim · Finding · Contradiction · Limitation · Recommendation
        ↑ points back to
RAW / EVIDENCE LAYER       EvidenceEvent · QualitativeObservation · Artifact · SurveyResponse
(immutable, append-only,   InterviewExcerpt · ObserverNote · ProductUsageEvent · SystemDecision
 tri-temporal, consent-    ConsentGrant · ConsentRevocation · BrokeredCredential · Opportunity
 tagged)
        ↑ described by
REFERENCE / REGISTRY       Participant · Team · Project · Sponsor · SponsorProduct · Tool ·
(slowly-changing,          ToolCategory · Event · Track · Challenge · ResearchStudy ·
 versioned definitions)    ResearchQuestion · Hypothesis · Experiment · Arm · Factor ·
                           ModelVersion · EventTypeRegistry · ThemeCodebook · TelemetryContract
```

## The research object: `BehavioralEpisode` is derived, not raw

The user is right that the atom is not "a student." But the atom is also not the episode. The
**immutable atom is the `EvidenceEvent`**; the **`BehavioralEpisode` is a derived reconstruction**
— a narrative arc assembled from events, qualitative observations, and opportunity records for a
`(subject, product, window)`. Because it is an interpretation, it lives in the derived layer with
a `model_version` and provenance to every event it spans. Making the episode raw would collapse
Evidence into Claim.

```
BehavioralEpisode (DERIVED)
  subject            participant_id | team_id
  product_id?        the tool/product this episode is about (nullable for tool-agnostic arcs)
  window             [start_occurred_at, end_occurred_at]
  goal               inferred or self-reported; carries confidence + source
  context_snapshot   track, challenge, team_size, event_stage, incentives, prior_familiarity
  opportunity_ids[]  what was OFFERED in this window (exposure, mentor, intro…)
  event_ids[]        the raw EvidenceEvents composing the arc (exposure→action→friction→decision)
  qualitative_ids[]  linked QualitativeObservations ("why")
  outcome            reached_first_value | switched_away | abandoned | shipped_with | ...
  model_version      the assembler version — episodes are re-derivable, never hand-edited
  evidence_level     L1..L4 (almost always L1/L2 at episode grain)
```

Episodes are **cheap to throw away and re-derive** when the assembler improves. Never edit one.

## Reference entities — keep / merge / drop

Audited against the user's suggested list. Decisions and reasons:

| Entity | Verdict | Note |
|---|---|---|
| Participant, Team, Project, Sponsor, SponsorProduct, Tool, ToolCategory | **Keep** | Registry backbone |
| Event, Track, Challenge | **Keep** | Context primitives |
| ResearchStudy, ResearchQuestion, Hypothesis, Experiment | **Keep** | The research spine |
| Treatment, Control | **Merge → `Arm`** | An experiment has ≥1 `Arm`; control is `arm.is_control=true`. Cleaner than two entities |
| Exposure | **Merge → EvidenceEvent** | Exposure is an event (`PRODUCT_EXPOSED`), not a standalone table |
| Opportunity | **Keep (first-class)** | The "absence of behavior ≠ inability" mechanism. Must be a record, not inferred |
| Action, FrictionEvent, HelpRequest, MentorInteraction | **Merge → EvidenceEvent types** | All are event types in the taxonomy; `FrictionCoding` (type/severity/stage) is a *derived* annotation on friction events |
| Artifact, Outcome | **Keep**; Outcome as **derived** | Artifact is raw (submitted repo/deploy); Outcome is an episode field |
| Interview, SurveyResponse, FollowUp | **Keep** | Raw qualitative/self-report; `FollowUp` is a SurveyResponse/InterviewExcerpt with `wave ∈ {7d,30d,90d}` |
| RecruitingOptIn, DesignPartnerOptIn, VCOptIn | **Merge → `ConsentGrant`** | These are just grants of specific scopes. A `DiscoverabilityView` reads them; no separate tables |
| ConsentGrant, ConsentRevocation | **Keep** | The consent ledger. Both are append-only events |
| Decision | **Split → `SystemDecision` + `BuyerDecision`** | System/experiment decisions (the ledger, Part 11) are a different object from a buyer's purchasing decision (business graph). Same name for two things is a bug |
| ResearchFinding, Source, Claim, Factor, ModelVersion | **Keep** | The interpretation + provenance layer |
| BrokeredCredential, ProductUsageEvent, TelemetryContract | **Keep** | Part 3 instrumentation |
| QualitativeObservation, Theme, ThemeAssignment, InterviewExcerpt, BehavioralLink | **Keep**; `BehavioralLink` **merge → episode membership** | The link from a quote to an event is expressed by both belonging to the same episode + an explicit `evidence_link` row |

## The universal EvidenceEvent envelope

Every observed behavior is one immutable row. This is the schema in [schema/001_core.sql](../schema/001_core.sql).

```
event_id            uuid, pk
event_type          fk → EventTypeRegistry(code, version)   -- versioned taxonomy
schema_version      int
subject_participant participant_id?    -- exactly one subject grain is set…
subject_team        team_id?           -- …participant OR team OR project
subject_project     project_id?
product_id          product_id?        -- the tool/product this is about (competitor or sponsor)
sponsor_id          sponsor_id?        -- who, if anyone, this is attributable to
study_id            study_id?
experiment_id       experiment_id?
arm_id              arm_id?
opportunity_id      opportunity_id?    -- the offer this responds to, if any

occurred_at         tstz    -- VALID time: when the behavior happened (survival/retention axis)
observed_at         tstz    -- when a human/system first recorded it (catches survey lag)
available_at        tstz    -- TRANSACTION time: when it became queryable in our store
ingested_at         tstz    -- pipeline bookkeeping

source_kind         enum(BROKERED_API, SPONSOR_TELEMETRY, CHECKPOINT, OBSERVER, ARTIFACT,
                          SURVEY, INTERVIEW, FOLLOWUP, SYSTEM, PARTICIPANT_ACTION)
source              text    -- e.g. "anthropic.messages.v1" | "checkpoint.q3" | "observer.mira"
source_record_id    text    -- idempotency + audit back to the origin system
is_self_report      bool    -- SAID vs DID. First-class, never conflated
confidence          real    -- [0,1]; observer inference and derived-from-silence are < 1.0

consent_scope       enum[]  -- the scope(s) under which this was collected and MAY be used
raw_payload_ref     text    -- pointer to the raw store; the row itself carries no free payload
parser_version      text
superseded_by       event_id?   -- corrections point forward; the original is never mutated
created_at          tstz
```

### The three clocks (why bitemporal isn't enough)

```
occurred_at   ≤   available_at            (you cannot query a behavior before it is stored)
occurred_at   vs  observed_at             (a 30-day survey reveals reuse that occurred at day 9)
available_at  drives  "as of D" queries   (point-in-time correctness: a model trained as-of an
                                           event may only use rows with available_at ≤ D)
```

- **Retention / survival / time-to-event** run on `occurred_at`.
- **Survey-lag correction** uses `observed_at − occurred_at` (self-reports arrive late).
- **Point-in-time feature reconstruction** (for the Decision Ledger and any model) filters
  `available_at ≤ decision_time` so no future knowledge leaks backward. This is enforced and
  tested in [engine/capture.py](../engine/capture.py).

`occurred_at ≠ observed_at ≠ available_at` is a correctness invariant, not documentation.

## Provenance rules (non-negotiable)

1. **Raw is immutable and append-only.** Corrections create a new row with `superseded_by`
   pointing back; the original stays. No `UPDATE` on evidence.
2. **Every derived field carries `model_version` + the `event_id[]` it rests on.** A `Finding`
   that cannot enumerate its supporting evidence is invalid and cannot be published.
3. **Raw text is preserved beside every extracted label.** A `ThemeAssignment` stores the LLM's
   label, `model_version`, `human_review_state`, AND a pointer to the original
   `QualitativeObservation`. The label is a hypothesis; the text is the evidence.
4. **`is_self_report` is always set.** "They said they switched" and "we observed calls stop"
   are different evidence and must never be silently merged.
5. **`confidence < 1.0` for anything inferred** — observer inference, derived-from-silence,
   LLM-coded themes. Only directly logged, unambiguous machine events are `1.0`.

## Consent as data (see [schema/001_core.sql](../schema/001_core.sql) + Part 7)

`ConsentGrant` and `ConsentRevocation` are append-only events in the same ledger. Effective
consent for `(participant, scope)` is computed from the ledger as-of query time — so a revocation
takes effect on the next query without deleting anything. The scopes:

```
CORE_EVENT                 running the event; minimal, required to participate
AGGREGATE_RESEARCH         behavior feeds aggregate, min-cell-size-suppressed sponsor research
PRODUCT_TELEMETRY          brokered-credential usage of a named product is instrumented
QUALITATIVE_RESEARCH       checkpoints, interviews, observer notes may be used in research
LONGITUDINAL_FOLLOWUP      may be contacted at 7/30/90 days
RECRUITING_DISCOVERABILITY opted-in work evidence may be shown to employers (individual grain)
VC_DISCOVERABILITY         team trajectory may be shown to investors (individual/team grain)
DESIGN_PARTNER_DISCOVERABILITY  may be introduced to a sponsor as a design partner
PUBLIC_MEDIA               may appear in photos/recordings/marketing
ANONYMIZED_PUBLICATION     anonymized data may appear in a public "State of…" report
LONGITUDINAL_LINKAGE       event data may be joined to Club OS / prior-event history
```

`AGGREGATE_RESEARCH` never authorizes individual-grain sponsor output. The three `*_DISCOVERABILITY`
scopes are the only ones that permit individual-level disclosure to an outside party, and only for
the opted-in individual's own first-hand work evidence (FCRA constraint — see
[recruiting-legal.md](recruiting-legal.md)).

## What links to what (cardinalities that matter)

- `Participant 1—* Team`-membership `*—1 Team` (a participant can be on ≥1 team across events)
- `Team 1—* Project` (usually 1, but pivots create a second)
- `EvidenceEvent *—1 EventTypeRegistry(code,version)` (taxonomy is versioned; old events keep old codes)
- `Experiment 1—* Arm`; `EvidenceEvent *—0..1 Arm` (arm assignment is itself an event)
- `Opportunity 1—0..* EvidenceEvent` (an offer, and the response events it generated)
- `Finding *—* EvidenceEvent` via `finding_evidence` (the provenance join)
- `Finding 1—* Limitation`, `Finding 0—* Contradiction` (a finding must enumerate both)
- `SystemDecision 1—1 outcome` (evaluated later; the ledger closes the loop)

## Two graphs kept physically separate

The **participant research graph** (everything above) and the **Sponsor/Buyer Evidence Graph**
(Part 17: `Buyer → PainPoint → BuyerDecision → Engagement → Deliverable → Renewal`) share no keys
at the individual-participant grain. A buyer's stated pain and a participant's behavior meet only
inside a `Finding`, in aggregate. This separation is what lets us answer "which customer class
actually pays" without ever turning a participant into a line item in a sales record.

---

# The Hackathon as a Compressed Economic Laboratory

The research object is not `Person → Action`. A hackathon is a temporary micro-economy of
technical builders spending scarce resources under real incentives, and the object model must
record the *economic* structure of each decision, not just the behavior. This extends — does not
replace — the four layers above.

```
Actor → Opportunity → ChoiceSet → Resource → Decision → Transaction → Behavior → Artifact → Outcome
```

Each participant holds a scarce budget and allocates it:

```
Budget_i = Time_i + Attention_i + Skill_i + Compute_i + SocialCapital_i
```

Companies pay to understand *why those allocations happen* — which is a far more valuable question
than "did students like our product."

## `ChoiceSet` is the missing primitive: Choice ≠ Preference

**A chosen product tells you almost nothing unless you know what was actually available to choose
from.** "They used Claude" is not a preference signal unless you know Cursor and Copilot were
equally reachable in that context. So the schema records the choice set, not just the choice:

```
ChoiceSet(i, decision_point)   the alternatives actually available to actor i at that moment
   ├─ options[]                 each with: reachability, incentive attached (credits/bounty),
   │                            prior_familiarity, switching_cost_from_current
   └─ chosen_option             the ChosenProduct_{i,t}
```

Only with `ChoiceSet` can we estimate the quantity a sponsor actually wants —
`P(choose X | X, competitorA, competitorB, …, context)` — instead of a meaningless raw count.
This is stored in `choice_set` / `choice_set_option` ([schema/002_economic.sql](../schema/002_economic.sql))
and is what turns "72 signups" into "chose us 41% of the time when Firebase and Neon were equally
available and unincentivized."

## Price signals are first-class

Economic behavior moves with price, and the event can *vary* price in ways a survey cannot:

```
Price · Credits · FreeTier · Prize · Bounty · SwitchingCost
```

The highest-value version of this: **does a $100 credit create sustained adoption, or only
subsidize temporary activation?** If `Credits↑ ⇒ Activation↑` but `Retention_30d` is flat, a
company learns that millions in startup-credit spend is buying temporary usage — an expensive,
unanswered question. Incentives are recorded per `ChoiceSet` option and per `Opportunity`, so the
incentive→activation→retention chain is reconstructable.

## The interacting economies (recorded, not conflated)

Six economies run at once and the interesting findings live in the *edges* between them:

```
BUILDER   time / attention / tools / teams
PRODUCT   APIs / credits / compute / SaaS adoption
SPONSOR   cash / bounties / engineer-hours / research
TALENT    candidates / recruiter attention / interviews          (opt-in only)
STARTUP   teams / prototypes / users / capital                   (opt-in only)
EVENT     travel / rooms / food / venue / vendors                (logistics-revenue.md)
```

The chain a sponsor cares about crosses several:

```
SponsorCredits → ToolChoice → ProjectStack → ProjectOutcome → 30DayRetention → SponsorRevenue
```

`economic_transaction` records resource flows (time, compute, credits, bounties, prizes) with the
same tri-temporal + consent envelope as behavioral events, so the economic chain is queryable
under the same point-in-time and consent guarantees.

## Sponsor economics are observable too

For every sponsor we record inputs and observable outputs, so `SponsorROI` becomes decomposable
(not a single fake dollar number):

```
inputs:  cash · credits · engineer-hours · workshop-hours · bounty · prize · participants_exposed
outputs: activated · meaningful_users · projects_shipped · retained_7/30/90 · design-partner_leads
         · recruiting_leads (opt-in) · follow-on_conversations
SponsorROI = f(Adoption, Retention, ResearchValue, Talent, DesignPartners, R&DOutput)
```

This is itself a saleable research question — *what is the real ROI of developer-event and
startup-credit spend?* — which the repo already found companies publicly cannot connect to
non-vanity outcomes ([buyer-needs.md](buyer-needs.md)). Stored in `sponsor_economics`.
