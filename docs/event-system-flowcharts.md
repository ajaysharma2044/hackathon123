# Event System Flowcharts

Four diagrams that let a technical investor understand the company at a glance. Mermaid renders on
GitHub and in artifacts natively.

## A. Master system flow — problem → event → evidence → revenue → better event

The kill gate is explicit: if a hackathon holds no advantage over a panel/telemetry/Gartner, the
question dies ([research-modules.md](research-modules.md) HackathonAdvantage).

```mermaid
flowchart TD
  M[Expensive corporate problem] --> Q[Strategic / product mandate]
  Q --> U[Unanswered question]
  U --> G{Can a hackathon answer<br/>this unusually well?}
  G -- No --> K[KILL: a panel / telemetry /<br/>Gartner answers it better]
  G -- Yes --> S[Design study] --> E[Modify event format]
  E --> X1[10/10 builder experience]
  E --> X2[Real economic environment]
  E --> X3[Sponsor inputs: cash, credits,<br/>APIs, bounties, mentors]
  X1 & X2 & X3 --> B[Builders actually build]
  B --> BEH[Choose · switch · get stuck · ship · abandon]
  BEH --> DATA[Behavior + economic data:<br/>telemetry · qualitative · artifacts]
  DATA --> FU[7 / 30 / 90 days: did behavior persist?]
  FU --> QE[Quant engine: causal tests · choice models ·<br/>survival · VOI · calibration]
  QE --> ANS["Enterprise answer:<br/>this changed your decision by ..."]
  ANS --> REV[Enterprise $: research · R&D mandate · annual partner]
  REV --> NEXT[Better next event:<br/>travel · hotel · food · mentors · grants]
  NEXT --> APP[Better builders apply] --> BETTER[Better research]
  BETTER -.reinforces.-> X1
```

## B. Participant experience flow — every stage a lever, a capture point, a risk

```mermaid
flowchart LR
  A[Application] --> AC[Acceptance] --> TR[Travel<br/>funded] --> HO[Hotel] --> AR[Arrival]
  AR --> TF[Team formation] --> BU[Build] --> HE[Help sought] --> FS[Food / social]
  FS --> DE[Demo / pitch] --> FU[7/30/90 follow-up] --> AL[Alumni network]
  classDef cap fill:#e8f4ff,stroke:#4a90d9;
  classDef exp fill:#eaffea,stroke:#4caf50;
  class A,HE,BU,DE,FU cap
  class TR,HO,FS,AL exp
  HE -.capture: friction, in the moment they wanted help.-> BU
  DE -.capture: the pitch IS the exit interview.-> FU
  BU -.capture: artifacts + dependency manifest.-> DE
```
*Blue = capture opportunity (organic, disclosed); green = experience lever. Each stage also carries a
trust risk — over-prompting, perceived surveillance — governed by the research-minutes budget.*

## C. Event economy flow — the compressed micro-economy

```mermaid
flowchart TD
  subgraph IN[Sponsors / organizers provide]
    direction LR
    C1[cash] & C2[credits] & C3[compute] & C4[prizes] & C5[mentors] & C6[travel/infra]
  end
  IN --> ALLOC[Builders allocate scarce budget:<br/>time · attention · skill · tool choice · compute · team effort]
  ALLOC --> CREATE[Creates: usage · transactions · artifacts ·<br/>behavior · teams · projects]
  CREATE --> PROD[Produces: research · product intelligence ·<br/>R&D · design partners · talent · startups · category intelligence]
  PROD --> VAL[Enterprise value / revenue]
  VAL -.funds better inputs.-> IN
```

## D. Quant decision loop — how beliefs become decisions and back

```mermaid
flowchart LR
  EV[Evidence] --> PR[Prior<br/>distribution + provenance]
  PR --> PO[Posterior<br/>Beta-Binomial, reliability-weighted]
  PO --> SC[Scenario simulation<br/>Monte Carlo · bear/base/bull · tail risk]
  SC --> OP[Optimization<br/>Pareto · portfolio · constraints]
  OP --> DEC[Decision<br/>+ VOI: research more or act?]
  DEC --> OUT[Outcome]
  OUT --> CAL[Calibration<br/>Brier · log-loss · ECE]
  CAL --> EV
```

## The loop to obsess over

Diagram A's dotted return edge is the whole company:

```
research revenue → funds a better builder experience → attracts a better cohort
→ produces better research → commands higher enterprise WTP → funds a better experience → ↺
```

Which links are **evidenced** vs **hypotheses** (be honest): "better experience → better cohort" is
LIKELY (selective events draw talent — HackMIT's 5% admit rate). "Better research → higher WTP" is a
HYPOTHESIS (the `wtp_research_elasticity` assumption in [quant-assumptions.md](quant-assumptions.md))
— it is the single most important link to validate, and it is UNKNOWN until a paid pilot renews at a
higher price.
