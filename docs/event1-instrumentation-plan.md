# Event 1 Instrumentation Plan

What Event 1 actually needs to build, what NOT to build, and the honest answers to the 20
questions. This is the decision doc; the architecture is in [capture-system.md](capture-system.md).

## The minimum viable capture stack

Ordered by information-per-dollar-and-burden. Build top-down; stop when the budget runs out.

| # | Capability | Class | Build? |
|---|---|---|---|
| 1 | **Brokered API keys + proxy/telemetry-contract** for the *primary* sponsor's product | `[PL]` | **Yes — this is the product.** Without it the flagship module is self-report |
| 2 | **Consent ledger + query gate** (the [engine](../engine/capture.py), productionized) | `[P]` | **Yes.** Legal + ethical foundation; everything routes through it |
| 3 | **Structured application intake** (stack, prior projects, track pref) | `[P]` | **Yes.** Cheap, and the pre-existing-familiarity covariate is unrecoverable later |
| 4 | **Event-app event stream** (team formation, submissions, mentor bookings, opportunities offered) | `[P]` | **Yes** |
| 5 | **6-hourly checkpoints** (≤5 Q, tied to an incentive) + **post-error/post-switch micro-prompts** | `[PL]` | **Yes.** The switching timeline + the "why" |
| 6 | **Artifact capture at submit** (repo, deploy, commit history, dependency manifest) | `[P]` | **Yes.** The honest cross-check on all self-report |
| 7 | **Observer logs** (8–12 trained, fixed codebook) | `[PL]` | **Yes.** How qualitative scales to 200 |
| 8 | **Stratified exit interviews** (30–40, over-sampling never-activated) | `[PL]` | **Yes** |
| 9 | **7/30/90-day follow-up** (incentivized) | `[PL]` | **Yes.** The retention data nobody else has |
| 10 | Pre-registration + operational-definition record | `[P]` | **Yes.** Cheap; the credibility gate |

**Do NOT build for Event 1:** desktop/IDE/keystroke capture (`[HR]`, ever); a general ML platform
(descriptive funnels + logistic + survival is the whole toolkit — Part 9); competitor telemetry
(impossible — use dependency files); a bespoke integration per sponsor (build the neutral schema +
one mapper); the experimentation marketplace, VC discovery UI, or category-intelligence product
(all downstream of one report existing); any score/ranking of a person (`[HR]`, ever).

## Multi-client capacity (Part 16) — this is a constrained allocation problem

Do **not** assume 8–12 studies "just fit." Capacity is bounded by finite resources:

```
ParticipantResearchMinutes  ≈ 200 builders × ~60 research-min each ≈ 200 participant-hours
InterviewCapacity           ≈ (researchers × interview-slots) — the true scarce resource
SponsorProductExposure      each required exposure consumes unconstrained surface (the baseline asset)
ResearcherCapacity          observers + interviewers + coders, not participants, bind first
```

A 20-interview study consumes 20 participant-hours; the hard ceiling is **~8–12 parallel
engagements, and researcher headcount binds before participant-minutes do** — which is a *good*
constraint, because scarcity is what justifies premium pricing.

### The Study Compatibility Graph (must exist before selling a second study)

Nodes = studies; edges = `COMPATIBLE | CONFLICTING | DEPENDENT`. Two studies conflict when they
contend for the same required exposure, the same unconstrained surface, or **direct competitive
contamination**:

```
COMPATIBLE     Anthropic AI-coding study  +  Stripe payments-integration study  +  Datadog
               observability study  — different products, different surfaces, no contention
CONFLICTING    Anthropic  +  a competing model API  +  a competing coding assistant  — all want
               the same builders' tool-choice at the same moment; running them together destroys
               each other's "free choice" and the unconstrained baseline
DEPENDENT      a switching study depends on the tool-choice study's exposure design
```

**Rule:** at most one sponsor per directly-competitive product category per event. This is a
selling constraint (you cannot take Anthropic's and a direct competitor's money for the same
event) and a validity constraint. Event research capacity becomes: maximize engagement value
subject to no-conflict + researcher-capacity + unconstrained-surface-floor.

## Business-side capture (Part 17) — learn whether THIS business works

Event 1 instruments the *buyer* too, in the separate business graph
([schema/001_core.sql](../schema/001_core.sql)): lead source, buyer title/department, stated
problem, current solution + spend, budget owner, procurement path, time-to-close, quoted price,
discount requested, deal stage, **lost_reason**, contract size, renewal interest, which
deliverables they valued vs ignored, and whether the research **changed a decision**. This is how
Event 1 reveals which customer class actually pays and which modules have real WTP — the ICP
discovery loop ([research-modules.md](research-modules.md)), grounded in real deals rather than
desk research.

---

# Executive Synthesis — the 20 answers

**1. The 20 highest-value signals to capture at Event 1.**
(1) unconstrained tool-choice distribution; (2) `TOOL_SWITCHED` events + trigger; (3) time-to-
first-value per product; (4) onboarding funnel drop-off points; (5) error/retry patterns
(friction); (6) `FIRST_VALUE_REACHED` timing; (7) dependency manifest at submit (what was actually
used); (8) test-vs-production transition; (9) post-switch "why" micro-prompts; (10) 7/30/90-day
product reuse; (11) project shipped y/n + artifact; (12) 30/90-day project continuation; (13) team
persistence; (14) prior-collaboration graph; (15) opportunity offered→response (exposure, mentor,
intro); (16) pre-event stack/familiarity baseline; (17) SAID-vs-DID divergence; (18) observer-coded
friction (type/severity/stage); (19) stratified exit-interview themes; (20) buyer-side deal signals
(lost_reason, changed-a-decision).

**2. The 10 signals that sound useful but we should NOT collect.** Keystrokes; screen/IDE capture;
camera/attention; private DMs; personality/Big-Five inference; "quality"/employability/founder
scores; protected traits (beyond a siloed legal fairness audit of selection); continuous location;
full request/response bodies by default; anything derivable later (don't collect what a dependency
file or a 30-day survey will reveal).

**3. Captured passively (through systems they intentionally use).** Brokered-key call streams;
event-app actions (team, submission, mentor booking); artifact/dependency inspection; opportunity
offer→response; workshop attendance. All disclosed.

**4. Requires sponsor cooperation.** `FIRST_VALUE_REACHED` definition; per-key telemetry export or
proxy permission; product-side retention signal; the `SponsorTelemetryContract`. No cooperation →
activation counts only, not research.

**5. Requires participant self-report.** Pre-event baseline/attitudes; checkpoint "what are you
using now"; switch/abandon reasons; anything about competitor tools; post-event reuse where the
product can't be instrumented.

**6. Requires qualitative interviews.** The *mechanism* behind a switch; trust breakdown in
AI-generated code; why-not-production; team dynamics; anything where "why" matters and telemetry
only shows "what."

**7. Minimum Event 1 stack.** Items 1–10 above. Brokered keys + consent gate are the irreducible core.

**8. Technically hardest.** Brokered instrumentation that yields *meaningful* (not raw) use across
heterogeneous products, plus a defensible `TOOL_SWITCHED` from triangulated, partial signals.
Competitor-side behavior is not hard — it's impossible server-side, and we say so.

**9. Methodologically weakest.** Internal validity: n≈200, self-selected tracks, Hawthorne, prize-
contaminated free choice. Ceiling is L1/L2 for most modules; L3–L4 only on narrow randomizable
sub-tasks. Sell **depth** (observed causal behavior) against panel vendors' **breadth**; never
oversell generalizability.

**10. The single instrumentation capability worth the most.** **Brokered API keys.** It is the only
clean source of activation timing, friction, abandonment, and switching as server-side truth — it
is the difference between a research product and a survey, and the only defensible answer to the
one signal (`tool_switched`) that carries most of the commercial value.

**11. Sponsor questions we CAN credibly answer at ~200.** Precise friction diagnosis ("N stalled at
step X, median T lost, here's why"); the unconstrained tool-choice baseline; onboarding funnel
shape + drop-off; switching narratives; test→prod abandonment reasons; 7/30/90 retention direction;
directional segment differences.

**12. Questions we CANNOT credibly answer.** Precise effect sizes; small between-segment differences;
anything about the *median* developer (elite-only cohort); population-level market share; five
rigorous parallel studies; any causal claim without a randomized sub-design.

**13. Data dramatically more valuable after 7/30/90 days.** Voluntary reuse/retention; project
continuation; team persistence; startup formation; whether the sponsor product stayed in the stack;
recruiter/VC follow-through. The retention curve is the asset no other hackathon can produce.

**14. Data that could support a year-round research panel.** The consented, profiled, opted-in
participant roster + their demonstrated stack + `LONGITUDINAL_FOLLOWUP` consent → an async research
panel that earns between events. The event is the panel's customer-acquisition cost
([monetization-map.md](monetization-map.md)). Its value compounds; its consent is the gate.

**15. Highest risk of damaging participant trust.** Making the event feel like a study, not a build
weekend; over-frequent checkpoints; any perceived surveillance; a recruiting/VC disclosure the
participant didn't clearly opt into. The research-minutes budget and invisible-but-disclosed
principle exist for exactly this.

**16. Information that must NEVER leave our system at individual level.** Raw telemetry bodies;
cross-product behavior tied to a name; anything under `AGGREGATE_RESEARCH`; any inferred trait. Only
first-hand work evidence, under an explicit `*_DISCOVERABILITY` opt-in, ever leaves at individual grain.

**17. What sponsors receive only in aggregate.** All behavioral research: funnels, switching matrices,
friction diagnoses, retention curves, segment cuts — min-cell-size-suppressed. The report is
aggregate; the exceptions are opted-in individual disclosures the participant controls.

**18. What participants can explicitly opt to share individually.** Their own work evidence to
recruiters (`RECRUITING_DISCOVERABILITY`); team trajectory to VCs (`VC_DISCOVERABILITY`); a
design-partner intro (`DESIGN_PARTNER_DISCOVERABILITY`); media appearance (`PUBLIC_MEDIA`). Each is a
separate, revocable grant.

**19. Preserving independent-research credibility while sponsors pay.** Pre-registered hypotheses +
falsification criteria; sponsor-adjusted methodology (their sponsored exposure removed from their own
counts, per Devpost's precedent); sponsors get instrument review and early access, **not** editorial
control over conclusions (the LF Research line); every finding states limitations + generalizability;
the system can and must publish findings that *contradict* the sponsor's hope. A study that can't
come back negative isn't research.

**20. If forced to keep only 20% of capture — what survives.** Brokered keys for the primary
product; the consent gate; artifact/dependency capture at submit; 6-hourly "what are you using now"
checkpoints; and 30-day follow-up. That five-part core yields the tool-choice baseline, the
switching signal, activation/friction, and retention direction — the entire differentiated
deliverable — at minimal participant burden. Everything else is amplification.

## The one-line test this whole system has to pass

> Can we produce, for one paying buyer's real question, an aggregate finding that is honest about
> its limitations, respects every participant's consent at query time, and could have come back
> negative — from a weekend that the builders would still call one of the best events they attended?

If yes, the thesis in [STATE.md](STATE.md) is real. The capture system is built so the evidence can
tell us whether it is — including telling us no.
