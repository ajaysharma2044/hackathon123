# Discovery Flowcharts

Mermaid diagrams for the reset. These describe the machine in
[discovery-engine.md](discovery-engine.md); they are architecture, not claims about any buyer.

---

## 1. Master discovery loop

```mermaid
flowchart TD
    TS[Talent supply<br/>configurable mix, population-level] --> ED[Possible environment designs<br/>environment_generator]
    ED --> EC[Environment capabilities<br/>21-dim vector, decomposed]
    EC --> PM[Problem mechanics<br/>mode + 16 dims]
    PM --> PU[Corporate problem universe<br/>evidence-cited, seed + PENDING]
    PU --> FIT[Problem x Environment match<br/>HARD structural-advantage gate]
    FIT --> DV[Economic decision value<br/>belief, default UNKNOWN]
    DV --> BUY[Buyer / budget owner]
    BUY --> ICP[ICP cluster<br/>OUTPUT, ranked by evidence]
    ICP --> CON[Contract / business model]
    CON --> OPT[Optimized environment]
    OPT --> OUT[Outcome + artifacts + failures]
    OUT --> EV[Evidence]
    EV -->|calibration, Bayesian update| BM[Better model]
    BM -.feeds back.-> TS

    FIT -->|no structural edge| KILL[KILL - a substitute does it as well]
    DV -->|UNKNOWN| GE[GATHER_EVIDENCE<br/>the $5-15K falsification test]
```

## 2. Corporate problem flow

```mermaid
flowchart TD
    CO[Company] --> BU[Business unit]
    BU --> MAN[Strategic / operational / R&D mandate]
    MAN --> EP[Expensive problem]
    EP --> DEC[Decision at stake]
    DEC --> NEED[Evidence / artifact needed]
    NEED --> MECH[Problem mechanics + mode]
    MECH --> ENV[Environment required]
    ENV --> TAL[Talent required]
    TAL --> RUN[Experiment / competition / simulation]
    RUN --> ANS[Answer / prototype / negative result]
    ANS --> CHG{Decision changed?}
    CHG -->|yes| VAL[Economic value realized]
    CHG -->|no| LEARN[Learning / eliminated option<br/>value of failure]
```

## 3. The temporary economy

```mermaid
flowchart TD
    subgraph ORG[Organizations provide]
        M1[money] & M2[problems] & M3[data] & M4[customers] & M5[tools] & M6[capital] & M7[domain expertise]
    end
    subgraph PPL[Participants provide]
        P1[time] & P2[skill] & P3[creativity] & P4[judgment] & P5[experimentation]
    end
    ORG --> ALLOC[Environment allocates<br/>resources, information, teams,<br/>incentives, competition, feedback]
    PPL --> ALLOC
    ALLOC --> PROD[Produces<br/>solutions, behavior, transactions,<br/>artifacts, failures, new ventures]
    PROD --> CRE[Creates<br/>decision value, research, IP,<br/>cost savings, new products, revenue]
    CRE -.shadow prices, flow analytics.-> LEDGER[(economy.EconomicLedger<br/>attention / bottlenecks / decisions changed)]
```

## 4. The arms-race overlay (spend × gap × fit)

```mermaid
flowchart TD
    WAR[Spending war<br/>spend_intensity.SpendCategory<br/>spend = belief, default UNKNOWN] --> SIG[Desperation signals<br/>only count when linked to a gap]
    WAR --> GAP[Structural gap<br/>what can't they buy today?]
    GAP --> G1{gap severe?}
    G1 -->|no| NG[NOT A GAP - a substitute covers it]
    G1 -->|yes| G2{do we hold a structural advantage?}
    G2 -->|no| NO[NOT OURS - an existing method fills it]
    G2 -->|yes| REAL[REAL GAP]
    REAL --> OPP[Opportunity = GAP x MONEY x FIT<br/>opportunity_matcher, 12 decomposed dims]
    SIG --> OPP
    OPP --> LIVE{live?<br/>spend & gap & advantage & buyer & participant-fit}
    LIVE -->|no| SKIP[SKIP]
    LIVE -->|yes| DSE[Demand-shaped environment<br/>participant experience = hard constraint]
```
