# Value Engine Flowcharts

The five diagrams from Part XXII. Mermaid renders on GitHub natively.

## 1. Master hackathon value engine — company problem → revenue

```mermaid
flowchart TD
  P[Company problem] --> ES{Engine selection:<br/>does a hackathon hold an advantage?}
  ES -- no advantage --> KILL[NO FIT: a panel / telemetry /<br/>consultant / internal team is better]
  ES -- Research --> MR[Research module]
  ES -- R&D --> MRD[R&D challenge track]
  ES -- Product-Dev --> MP[Product beta arena]
  ES -- Activation --> MA[Activation arm]
  MR & MRD & MP & MA --> RA[Resource allocation:<br/>participant-min · researcher-hrs · unconstrained surface]
  RA --> ACT[Participant activity:<br/>choose · build · switch · ship · abandon]
  ACT --> EVI[Artifact + evidence:<br/>telemetry · qualitative · prototypes]
  EVI --> DEL[Buyer deliverable:<br/>findings · funnel · prototypes+failure-map]
  DEL --> REV[Revenue: research · R&D wallet · activation · sponsorship]
```

## 2. Event economy — the compressed micro-economy

```mermaid
flowchart LR
  A[Actors: builders · teams · sponsors · mentors · VCs · recruiters] --> O[Opportunities offered]
  O --> C[ChoiceSets: what was actually available]
  C --> R[Resources: time · attention · compute · credits · mentor-min]
  R --> D[Decisions under scarcity]
  D --> T[Transactions: usage · credits · bounties · prizes]
  T --> AR[Artifacts: prototypes · repos · deploys]
  AR --> OUT[Outcomes: adoption · retention · teams · startups · findings]
  OUT -.funds better inputs.-> A
```

## 3. Engine portfolio → shared event capacity → optimal portfolio

```mermaid
flowchart TD
  E1[Research] & E2[Product-Dev] & E3[R&D] & E4[Innovation] & E5[Activation] & E6[Sponsorship] --> CAP
  CAP[Shared event capacity:<br/>participant-min · researcher-hrs · unconstrained surface · categories] --> OPT
  OPT["Constrained optimizer:<br/>max value s.t. capacity + one-per-competitive-category<br/>+ free-choice floor + experience floor"] --> SEL[Optimal 3-4 non-competing engagements]
  SEL -.more sponsors is NOT better.-> OPT
```

## 4. Tweak engine — change one thing, see all deltas

```mermaid
flowchart LR
  CUR[Current event design X] --> INT[Intervention: Δx<br/>e.g. +2 sponsors, +free-choice, -burden]
  INT --> CF[Counterfactual: objectives at X+Δx]
  CF --> D1[Δ Research value]
  CF --> D2[Δ Product / R&D value]
  CF --> D3[Δ Participant experience]
  CF --> D4[Δ Revenue / contribution]
  CF --> D5[Δ Cost / complexity / risk]
  D1 & D2 & D3 & D4 & D5 --> DEC[Decision:<br/>Pareto-improving? or a deliberate tradeoff]
```

## 5. ICP discovery — structure → company → offer

```mermaid
flowchart TD
  H[Historical structure] --> PM[Problem mechanics:<br/>uncertainty · parallelizable · blind-spot · observable?]
  PM --> EF{Engine fit +<br/>HackathonAdvantage gate}
  EF -- no --> NF[NO FIT]
  EF -- yes --> BU[Buyer + budget owner]
  BU --> TR[Trigger: why now]
  TR --> CO[Company match]
  CO --> OF["Offer: engine · module · participants · deliverable ·<br/>price ceiling · sales message · WTP UNKNOWN"]
```

## The loop the whole system serves

```
research/R&D revenue → funds a better builder experience → attracts a better cohort
→ produces better/uniquer evidence → commands higher enterprise WTP → funds a better experience → ↺
```

Evidenced link: better experience → better cohort (**LIKELY**). Hypothesis link: better research →
higher WTP (**the `wtp_research_elasticity` assumption** — the single most important thing to validate,
UNKNOWN until a pilot renews at a higher price).
