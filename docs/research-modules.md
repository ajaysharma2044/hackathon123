# Research Modules & ICP

Reusable research modules, and the ICP framework that decides which to point at whom. Built
pain-first, not company-first.

## The ICP principle (the correction that governs this doc)

> **We are not looking for firms willing to sponsor us. We are looking for firms with an expensive
> unanswered question that our environment is unusually good at answering.**

The ICP is discovered from the problem backward, never from a logo:

```
ICP = Urgent Problem × Cohort Fits × Internal Blind Spot × Budget × Decision Imminence
```

A company name (Anthropic, Stripe, Supabase) is an *example*, never the ICP. Anthropic may be a
*worse* first buyer than a smaller infrastructure company precisely because Anthropic can hire
researchers, recruit participants, and already owns enormous usage data — so the question is not
"would they work with us" but **"what can we observe that they cannot easily observe themselves?"**
For Anthropic that is: developers who *didn't* choose Claude, Claude-vs-competitor under free
choice, and actual output rather than self-report. For a smaller, heavily-competed infrastructure
company with a small research team and a single million-dollar product decision, the *entire*
question may be unobservable internally — which can make them a better first ICP.

### The ICP signal set (kept visible, never collapsed to one score)

A company is a strong ICP when most of these hold — and the dimensions stay separate so we can see
*why* a rich company still isn't a fit:

| Dimension | Strong-fit signal |
|---|---|
| **Developer is the user** | product is an API / infra / devtool / AI / cloud / database / payments primitive |
| **Choice happens early** | developers pick it *before* enterprise procurement takes over |
| **Competitive alternatives exist** | there is something meaningful to observe under free choice |
| **They court builders** | startup program, credits, free tier, hackathons, accelerator |
| **Telemetry has selection bias** | they see their users, not why the others chose a competitor |
| **Actively improving a metric** | activation, first integration, deploy, eval→production, retention |
| **A specific team with money** | Research Ops / UXR / Product Research / Growth / Startup Programs / PMM / Innovation |
| **An upcoming decision** | launch, pricing change, agent product, program redesign, competitive threat, onboarding overhaul |
| **Large economic outcome** | the answer moves a decision worth far more than the study |
| **SubstitutionRisk (inverse)** | their own telemetry / a panel vendor / a CAB does NOT already answer it cheaply |

Encoded as the `ICPProfile` object ([schema/001_core.sql](../schema/001_core.sql)) with each
dimension stored separately: `Pain, Urgency, CohortFit, BlindSpot, DecisionValue, Budget,
BuyerAccess, Repeatability, SubstitutionRisk`. **All UNKNOWN until evidenced** — an ICP profile is
a hypothesis about a buyer, subject to the same Evidence≠Claim discipline as everything else.

### The trigger is the reason to call today

A static target list is weak; a *trigger* makes the pain urgent and dated:

```
NEW PRODUCT / AGENT LAUNCH   → need developer-adoption + real-workflow evidence now
NEW STARTUP PROGRAM          → need to know what actually drives early-stage adoption
COMPETITOR GAINING SHARE     → need switching research (who leaves, why, what triggers it)
ONBOARDING REDESIGN          → need friction diagnosis on the specific funnel
NEW PRICING                  → need willingness / behavior-under-price evidence
EVAL→PROD GAP CALLED OUT     → need the "tested but never shipped" counterfactual
```

`Trigger` is a first-class record (`kind`, `observed_at`, `source_url`, `company_id`, `decays_at`).
"Stripe just shipped X, team Y owns metric Z, their data can't see the counterfactual, our cohort
supplies it" beats "let's email Stripe" — and it has a decay date, so stale triggers drop off.

## The module catalog (pain-first, reusable)

Each module is a **pain**, not a company. A module carries: the question it answers, the ICP
signals it serves, required vs optional data, capture method + class, validity risk, participant
burden, privacy risk, analysis, and the buyer roles that own the metric. **WTP is UNKNOWN for all
of them** until the pre-sell test ([STATE.md](STATE.md)) returns a signed number — comparable
pricing is not proof we can command it (Part 20 rule).

Legend for capture class: `[P]`roven `[PL]`ausible `[E]`xperimental `[HR]`igh-risk.
Evidence level our environment can credibly reach: L1 descriptive · L2 correlational · L3
adjusted/quasi-causal · L4 randomized.

### 1 — Tool-Choice-Under-Free-Choice Module *(the flagship — nobody else can build it)*
- **Pain:** "which tools do developers reach for when unconstrained, and why us vs a competitor?"
- **Serves ICP signals:** BlindSpot (telemetry can't see non-users), CohortFit (builders choose
  naturally while shipping), competitive-alternatives.
- **Required:** unconstrained surface protected (no required tool on ≥1 track); dependency manifests
  `[P]`; checkpoint "what are you using now" `[PL]`; brokered keys for the *sponsor's* product `[PL]`.
- **Optional:** brokered keys for competitors (usually impossible `[UNKNOWN]`).
- **Primary outcome:** unconstrained tool-selection distribution + switching narratives.
- **Ceiling:** **L1/L2.** Descriptive baseline + correlational switch predictors. Not L4 — choice is
  self-selected. This is the single most differentiated module; see Part 19.
- **Buyer:** Product Research / DevRel leadership / PMM.

### 2 — Onboarding-Friction / Time-to-First-Value Module
- **Pain:** "where does setup/onboarding lose people; what's our real time-to-first-value?"
- **Required:** brokered-key event stream (`ONBOARDING_STARTED → FIRST_VALUE_REACHED`, errors) `[PL]`;
  post-error micro-prompts `[PL]`; observer logs `[PL]`. `FIRST_VALUE_REACHED` **sponsor-defined,
  pre-registered.**
- **Primary outcome:** funnel with real drop-off points + median time-lost per friction cluster +
  representative quotes. This is the "38 of 72 stalled at auth, median 41 min" deliverable —
  actionable, needs no inference, **L1**, and worth a contract on its own ([measurement.md](measurement.md)).
- **Buyer:** DevRel / Product / DX Eng lead. Winston Francois sells the priced analog at $20–35K.

### 3 — Eval→Production / "tested but never shipped" Module
- **Pain:** "developers succeed in our sandbox/test mode and never reach production — why?"
- **Serves:** the documented fintech + data-infra blind spot (Stripe publishes the 20% who charged,
  not the 80%; Modern Treasury's KYB latency; [buyer-needs.md](buyer-needs.md)).
- **Required:** brokered test-vs-prod event distinction `[PL]`; artifact deploy target `[P]`;
  post-event retrospective on why-not-prod `[PL]`; 7/30d follow-up `[PL]`.
- **Primary outcome:** the sandbox→production funnel + abandonment reasons. **L1/L2.**
- **Buyer:** Growth / Product / startup-program owner.

### 4 — AI-Productivity / Does-AI-Actually-Help Module *(neutral-party advantage)*
- **Pain:** "does this AI workflow actually improve output, vs self-reported belief?"
- **Serves:** the category-wide admission nobody can self-answer (Anthropic "can't measure";
  Cognition "unsolved"; METR: 19% slower while feeling 20% faster). A neutral party has the
  structural edge no vendor has — no vendor can credibly publish that its own tool slows people.
- **Required:** **randomized** assignment of AI-workflow condition where ethical/feasible `[E]`;
  artifact + task-completion measures `[P]`; matched effort/time on task; blinded outcome coding.
- **Ceiling:** **L3, occasionally L4** on a *narrow* randomizable sub-task (which docs version,
  which assistant path) — the one place our environment can reach quasi-causal. Whole-event AI
  effect stays L2.
- **Buyer:** Product Research / an AI lab's platform research team.

### 5 — Infrastructure-Selection Module
- **Pain:** "which stack do technical founders choose before procurement constrains them?"
- **Required:** dependency manifests `[P]`; project-type context; checkpoint stack declaration `[PL]`.
- **Primary outcome:** stack-selection distribution by project type + switching matrix. **L1/L2.**
- **Buyer:** data/cloud/infra PMM, DevRel, startup program.

### 6 — Switching / Retention Module
- **Pain:** "what triggers a switch, and what makes adoption stick?"
- **Required:** triangulated `TOOL_SWITCHED` (checkpoint + dependency delta + brokered silence) `[E]`;
  post-switch micro-prompt `[PL]`; 7/30/90 follow-up `[PL]`.
- **Primary outcome:** switching matrix with time-to-switch + stated triggers; retention curve.
- **Ceiling:** **L1/L2**; retention is the number no other hackathon produces at all.
- **Buyer:** Growth / PMM / DevRel.

### 7 — API-Integration Module
- **Pain:** "where does our integration path create abandonment, minute by minute?"
- **Required:** brokered-key call sequence + error classes `[PL]`; artifact wiring `[P]`; observer +
  post-error prompt `[PL]`.
- **Primary outcome:** integration funnel + error taxonomy. **L1.**
- **Buyer:** DX Eng / DevRel.

### 8 — Agentic-Workflow / Agent-as-User Module *(new, high-uncertainty)*
- **Pain:** "what does agentic adoption look like in real projects; when the agent is the API
  user, who is the customer and how do we count them?" (Render/Neon/Pinecone open questions.)
- **Required:** brokered-key attribution of agent-initiated vs human-initiated calls `[E]`; artifact
  inspection for agent frameworks `[P]`; qualitative on trust/hand-off `[PL]`.
- **Ceiling:** **L1** (descriptive; the category has no baseline at all). Honest framing: exploratory.
- **Buyer:** AI-infra / devtool product teams.

### 9 — R&D-Challenge Module
- **Pain:** "what technical solutions emerge against our real problem; which approaches repeatedly
  fail?"
- **Required:** sponsor-defined challenge (a disclosed track); artifacts + architecture notes `[P]`;
  mentor/engineer session notes `[PL]`.
- **Primary outcome:** solution-approach taxonomy + failure modes + shortlist of promising prototypes.
  **L1.** This is crowdsourced R&D, not statistics.
- **Buyer:** Innovation / R&D / DevRel.

### 10 — Design-Partner Module
- **Pain:** "which builders would make qualified design partners for our product?"
- **Required:** `DESIGN_PARTNER_DISCOVERABILITY` opt-in `[P]`; first-hand build evidence on the
  product `[P]`. **Individual grain, opt-in only.**
- **Primary outcome:** warm, qualified design-partner intros (people who built on it and chose to
  be introduced). Dodges the FCRA/placement-fee walls of recruiting ([recruiting-legal.md](recruiting-legal.md)).
- **Buyer:** Product / DevRel.

### 11 — Longitudinal-Retention Module
- **Pain:** "does event-time adoption persist at 7/30/90 days?"
- **Required:** `LONGITUDINAL_FOLLOWUP` opt-in `[P]`; brokered-key reuse where product cooperates
  `[PL]`; incentivized follow-up survey `[PL]`.
- **Ceiling:** **L1/L2** with explicit response-bias limitation. The compounding-panel seed.
- **Buyer:** any of the above; also the between-events panel business.

### 12 — Talent-Evidence Module *(extreme caution — [HR] boundary)*
- **Pain:** "which builders demonstrated relevant technical work we could hire?"
- **Allowed:** artifacts, demonstrated work, role on project, project outcomes, `RECRUITING_
  DISCOVERABILITY` opt-in — **first-hand event observation only** (FCRA safe harbor).
- **Forbidden (`[HR]`, structural):** employability scores, secret rankings, personality/protected-
  trait inference. **Never emit a score** (NYC LL144 / EU AI Act — [recruiting-legal.md](recruiting-legal.md)).
- **Output:** descriptive work-evidence records, individual grain, opt-in. Not a ranking.
- **Buyer:** technical employers / quant firms.

### 13 — Startup-Continuation Module *(VC)*
- **Pain:** "which teams/projects persisted, iterated, got users?"
- **Allowed:** `VC_DISCOVERABILITY` opt-in; team persistence, iteration count, users acquired,
  prior-collaboration graph, artifacts. **No "founder score."**
- **Output:** opted-in team-trajectory records. **L1.**
- **Buyer:** VCs / accelerators / scouts (referral-with-memo economics, [venture-upside.md](venture-upside.md)).

## Research-question → data mapping (Part 6, per pain not per company)

Every module row above is a filled instance of this template (stored per engagement):

```
ResearchQuestion · RequiredData · OptionalData · CaptureMethod(+class) · ValidityRisk ·
ParticipantBurden · PrivacyRisk · PossibleAnalysis · EvidenceCeiling(L1–L4) ·
PossibleBuyerRole · CommercialValueHypothesis(UNKNOWN until pre-sell)
```

The point of the template: two different buyers with the *same pain* (onboarding friction on a
payments API vs an agent platform) reuse Module 2's machinery — we build the instrument once and
re-point it, which is what makes multi-client economics possible (Part 16).

## The buyer / ICP evidence graph (Part 17, kept separate from participant data)

```
Company ──1:1── ICPProfile(Pain,Urgency,CohortFit,BlindSpot,DecisionValue,Budget,
   │                        BuyerAccess,Repeatability,SubstitutionRisk — each with evidence + confidence)
   ├──*── Trigger(kind, observed_at, source_url, decays_at)
   ├──*── Buyer(title, department, budget_authority_est)
   │         └──*── PainPoint(statement, source, current_solution, current_spend_est)
   │                   └──0..1── Engagement(module_id, quoted_price, stage, discount_req)
   │                               └──*── Deliverable(what_they_valued, what_they_ignored,
   │                                                  changed_a_decision?)
   │                                         └──0..1── Renewal(interest, size)
   └── lost_reason (when it doesn't close — the most valuable field in the graph)
```

This graph is how Event 1 tells us **which customer class actually pays, which questions have real
WTP, and which modules to keep** — the business-side learning loop, physically separate from any
participant's behavioral data (they meet only inside an aggregate `Finding`).

## The next task this implies: ICP discovery

The engine should populate `ICPProfile` + `Trigger` across **100–300 developer-facing companies**,
scoring the visible dimensions from public evidence (job postings for the owned-metric + team,
changelogs/launches for triggers, published research for existing-research-habit, funding stage
for budget/team-size), then **cluster** to discover the real ICP — which may turn out to be, e.g.,
"50–500-employee Series C–pre-IPO devtool companies mid-onboarding-overhaul," or "public fintech
infra with startup programs," or "AI-coding companies shipping agent products," or something not
yet considered. Each record ends at `WTP: UNKNOWN → NextTest: talk to [role]`.

That is a bounded, high-value research pass — and it is the natural **next** deliverable after this
capture infrastructure lands. It is offered, not auto-run: it is a 100–300-company sweep and should
be a deliberate go, not a reflex (the swarm discipline from this session applies).
