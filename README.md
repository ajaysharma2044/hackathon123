# Builder Network

> An elite student hackathon network that doubles as a live product R&D, talent, and
> experimentation platform. Companies sponsor real builder experiences; the backend measures
> what developers choose, build, struggle with, adopt, and keep using — so sponsors get
> decision intelligence instead of logos and résumé books.

**This is not a hackathon company.** It is a live experimentation and decision-intelligence
network built around high-value student builders. The hackathon is the initial interface —
the format that produces dense, measurable, commercially interesting behavior fastest.

## The two-sided model

**Front end** — a genuinely premium builder event. ~200 highly selected builders from MIT,
Stanford, Berkeley, the Ivies, CMU and peers: flown in, housed, fed, given workspace, prizes,
mentors, sponsor tooling, and real problems to build against.

**Back end** — a structured experimentation, recruiting, and R&D network running underneath it,
on explicit opt-in.

The front end has to stand on its own. If it reads as a research study wearing a hackathon
costume, the panel degrades and the data goes with it. The bar is: *"this is one of the best
builder events I could attend."*

```
                         FRONT END
                  PREMIUM BUILDER HACKATHON
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
    BUILDERS              SPONSORS             TRACKS
  200 selected          companies/VCs       sponsor-defined
  students              employers           problem areas
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ↓
                    REAL BUILDING ACTIVITY
                             ↓
                 STRUCTURED EXPERIMENTATION
                             ↓
     ┌───────────────────────┼──────────────────────┐
     │                       │                      │
 PRODUCT RESEARCH      TALENT RESEARCH         MARKET RESEARCH
     │                       │                      │
     └───────────────────────┼──────────────────────┘
                             ↓
                      QUANT ENGINE
                             ↓
                    DECISION INTELLIGENCE
                             ↓
     ┌───────────────────────┼──────────────────────┐
     │                       │                      │
  SPONSORS               RECRUITERS               VCs
```

## The core inversion

A normal sponsor buys logo placement, booth space, a résumé book, an API prize, a workshop.

We ask a different opening question: **what business decision are you trying to make?**

```
SponsorGoal → Unknowns → Hypotheses → ExperimentDesign → Hackathon → Data → Recommendation
```

That is a research consultancy plus an experimentation platform, not an event sponsorship
business. The deliverable is a findings report, not photos.

## What the event observes that a résumé cannot

A résumé says *Python, AI, product, entrepreneurship.* The event shows what they chose to
build, which tools they actually reached for, whether they switched, where they got stuck,
whether they recovered, what shipped, how they worked with teammates, and whether they kept
building after the weekend.

The central measurement distinction:

```
Exposure  ≠  Preference  ≠  Retention
```

Required exposure to a sponsor product, then free tool choice for the rest of the event, then
post-event follow-up. That separates "143 students downloaded our product" from a real
adoption curve.

## The moat

```
Experiment Design
  + Elite Participant Network
  + Longitudinal Behavior
  + Work Evidence
  + Outcome Data
  + Quant Models
```

Hackathons are trivially copyable. The compounding dataset across 20 events — product choices,
projects, teams, tool switches, recruiting interactions, sponsor campaigns, post-event
outcomes — is not.

## Repo map

**Read [docs/STATE.md](docs/STATE.md) first** — the honest synthesis: what we actually know vs.
assumed, the bear case at full strength, and the one untested question (will a buyer pay?) that
gates everything. The docs below are raw material feeding it.

| Path | Contents |
|---|---|
| [docs/STATE.md](docs/STATE.md) | **The standing understanding.** Evidence/claim/hypothesis separation, epistemic status, next test |
| **— Capture & research infrastructure —** | |
| [docs/capture-system.md](docs/capture-system.md) | Architecture, lifecycle, brokered instrumentation, qualitative, consent, opportunity model |
| [docs/research-data-model.md](docs/research-data-model.md) | Canonical entities, the four layers, tri-temporal event envelope, provenance rules |
| [docs/research-modules.md](docs/research-modules.md) | ICP (problem-backward) + the pain-first reusable module catalog |
| [docs/capture-risk-register.md](docs/capture-risk-register.md) | Methodological / privacy / legal / experience / data-quality / integration risks |
| [docs/event1-instrumentation-plan.md](docs/event1-instrumentation-plan.md) | MVP capture stack, study-compatibility capacity model, the 20-question synthesis |
| [docs/question-catalog.md](docs/question-catalog.md) | **The VOI-scored questions** — what a hackathon economy can answer that telemetry/panels can't |
| **— Quant decision engine —** | |
| [docs/quant-engine.md](docs/quant-engine.md) | The probabilistic engine: beliefs, Bayesian updates, Monte Carlo, VOI, calibration |
| [docs/quant-assumptions.md](docs/quant-assumptions.md) | **Read before quoting any engine number** — every assumption, labeled, ranked by resolve-value |
| [docs/event-optimizer.md](docs/event-optimizer.md) | Event as multi-objective optimization: worked 3-design result + the 25-answer memo |
| [docs/event-system-flowcharts.md](docs/event-system-flowcharts.md) | Four Mermaid diagrams: master system, participant, economy, quant loop |
| [docs/event-design-matrix.md](docs/event-design-matrix.md) | Every event feature × experience/data/money/longterm/cost/risk |
| **— Value engines & the company→offer system —** | |
| [docs/historical-structural-analysis.md](docs/historical-structural-analysis.md) | How contests/prizes/hackathons historically created value; the Boudreau/Lakhani R&D result |
| [docs/structural-archetypes.md](docs/structural-archetypes.md) | The 10 recurring structures; which two are both hackathon-advantaged and six-figure |
| [docs/rd-engine.md](docs/rd-engine.md) · [docs/commercial-engines.md](docs/commercial-engines.md) | The specialized engines: R&D value-of-failure, research, activation, product-dev, more |
| [docs/company-opportunity-map.md](docs/company-opportunity-map.md) · [docs/icp-by-engine.md](docs/icp-by-engine.md) | The COMPANY→OFFER generator (routes or says NO FIT); one ICP per engine |
| [docs/top-prospects.md](docs/top-prospects.md) · [docs/go-to-market.md](docs/go-to-market.md) | First-cut prospect list + problem-first outreach theses |
| [docs/event1-design.md](docs/event1-design.md) | **The payoff.** Concrete Event 1 design + the 40-question synthesis |
| [docs/value-engine-flowcharts.md](docs/value-engine-flowcharts.md) | Five Mermaid diagrams: value engine, economy, portfolio, tweak, ICP discovery |
| [docs/historical-program-dataset.md](docs/historical-program-dataset.md) | Structured historical program records (UNKNOWN-honest) |
| **— Live Research Operating System (Event 1) —** | |
| [docs/research-ops/live-research-os.md](docs/research-ops/live-research-os.md) | **Start here.** The master architecture: the 17 layers, the live loop, the human sensor network, the no-go list |
| [docs/research-ops/event1-live-playbook.md](docs/research-ops/event1-live-playbook.md) | **The payoff.** Hour-by-hour timeline, 10 tabletop simulations, MVP-vs-ideal, and the 60-question final synthesis |
| [docs/research-ops/field-researcher-guide.md](docs/research-ops/field-researcher-guide.md) · [field-note-system.md](docs/research-ops/field-note-system.md) | The embedded field-researcher program (methodology, staffing, training, card) + the fact ≠ interpretation note structure |
| [docs/research-ops/critical-incidents.md](docs/research-ops/critical-incidents.md) · [micro-prompts.md](docs/research-ops/micro-prompts.md) · [adaptive-questioning.md](docs/research-ops/adaptive-questioning.md) | The trigger taxonomy → the one-line prompt → the branching interview tree |
| [docs/research-ops/adaptive-sampling.md](docs/research-ops/adaptive-sampling.md) · [negative-case-analysis.md](docs/research-ops/negative-case-analysis.md) · [analytic-memos.md](docs/research-ops/analytic-memos.md) | Who to interview next (negative cases first), deliberate disconfirmation, the live question backlog |
| [docs/research-ops/mentor-system.md](docs/research-ops/mentor-system.md) · [mentor-interventions.md](docs/research-ops/mentor-interventions.md) | Mentors as support + evidence; the vendor-rescue confounder (organic vs assisted success, no causal overclaim) |
| [docs/research-ops/checkpoints.md](docs/research-ops/checkpoints.md) · [interruption-policy.md](docs/research-ops/interruption-policy.md) · [participant-burden.md](docs/research-ops/participant-burden.md) | Minimal checkpoints, context-aware interruption, the ≤18-min research-minutes budget |
| [docs/research-ops/team-trajectories.md](docs/research-ops/team-trajectories.md) · [qualitative-coding.md](docs/research-ops/qualitative-coding.md) · [evidence-graph.md](docs/research-ops/evidence-graph.md) | The team story, the coding pipeline (AI with human gates), and claims that trace to evidence for AND against |
| [docs/research-ops/research-war-room.md](docs/research-ops/research-war-room.md) · [event-adaptation.md](docs/research-ops/event-adaptation.md) · [dashboard-spec.md](docs/research-ops/dashboard-spec.md) | The live ops room, timestamped interventions with validity impact, the dashboard views + client visibility |
| [docs/research-ops/event-phase-plan.md](docs/research-ops/event-phase-plan.md) · [client-protocols.md](docs/research-ops/client-protocols.md) · [consent-design.md](docs/research-ops/consent-design.md) · [longitudinal-followup.md](docs/research-ops/longitudinal-followup.md) | Per-phase research ops, per-client-engine protocols, modular consent, and 7/30/90-day follow-up |
| [docs/research-ops/participant-experience.md](docs/research-ops/participant-experience.md) · [event1-staffing.md](docs/research-ops/event1-staffing.md) | The hard constraint (experience wins) as a measured loop; the staffing architecture by event size |
| [schema/](schema/) · [engine/](engine/) | Typed schema (core + economic + quant + [live-research](schema/006_live_research.sql)) + runnable engines: consent/temporal correctness, VOI kill-filter, beliefs, Monte Carlo, portfolio, calibration, event optimizer, value engines, company→offer matcher, **and the Live Research OS kernel** (triggers, adaptive questions, adaptive sampling, mentor routing, question backlog, team trajectory, evidence graph, burden budget, intervention log) — **152 passing checks across ten suites** |
| [docs/roadmap.md](docs/roadmap.md) | Critical path, owner split, next 30/90 days |
| [docs/economics.md](docs/economics.md) | The full economic surface — attention / access / answers / outcomes |
| [docs/monetization-map.md](docs/monetization-map.md) | Every step monetized, tagged proven/swing, against the extraction frontier |
| [docs/research-findings.md](docs/research-findings.md) | Sourced benchmarks: competitor pricing, Miami costs, market comparables |
| [docs/logistics-revenue.md](docs/logistics-revenue.md) | $30-45K hidden in the room block, F&B, and venue — and how to actually collect it |
| [docs/asset-monetization.md](docs/asset-monetization.md) | What the list, content, research, and credits are worth — and the PyCon price benchmark |
| [docs/buyer-needs.md](docs/buyer-needs.md) | **Open with their unknown.** The real open questions, in the companies' own words |
| [docs/who-pays-for-research.md](docs/who-pays-for-research.md) | **Verified: what firms pay for research now** — named vendors, recurring budgets, the gap |
| [docs/innovation-budget.md](docs/innovation-budget.md) | **The biggest budget line.** The research-wallet mechanic, $150-300K/yr band |
| [docs/the-quote.md](docs/the-quote.md) | **How to price one engagement.** The 45% argument, the itemized quote, the ceiling |
| [docs/target-list.md](docs/target-list.md) | **Named doors.** Companies, contacts, what's dead, and what to do in the next two weeks |
| [docs/procurement.md](docs/procurement.md) | **How to actually get paid.** Champion requirement, the $25K threshold, sponsorship vs. SOW |
| [docs/recruiting-legal.md](docs/recruiting-legal.md) | **Read before building the recruiting product.** FCRA, LL144, EU AI Act, who-pays |
| [docs/event-comps.md](docs/event-comps.md) | Real prospectus ladders from comparable events, and the honest sponsor math |
| [docs/venture-upside.md](docs/venture-upside.md) | Why not to take equity, and the three things to do instead |
| [docs/research-pricing.md](docs/research-pricing.md) | **What to charge.** The LF rate card template, the $27K student-access trap, two defensible floors |
| [docs/location.md](docs/location.md) | **Open decision.** Criteria, candidate comparison, and the resolution worth testing |
| [docs/funding.md](docs/funding.md) | Budget, cost levers, sponsor stack, which budget to sell into, liability |
| [docs/measurement.md](docs/measurement.md) | What specifically to look for, and how to capture it |
| [docs/concept.md](docs/concept.md) | Full concept: experience design, sponsor model, tracks, the Club OS link |
| [docs/data-model.md](docs/data-model.md) | Entities, event taxonomy, consent scoping, temporal semantics |
| [docs/research-framework.md](docs/research-framework.md) | Experiment lifecycle, behavioral funnels, model specs, qualitative coding |
| [docs/products.md](docs/products.md) | The four buyers: sponsors, recruiters, VCs, R&D partners |
| [docs/open-questions.md](docs/open-questions.md) | Decisions that block building |

## Status

Planning Event 1. The binding constraint is the anchor sponsor, and the window is Q4 2026 —
2027 corporate budgets are being set now. See [docs/roadmap.md](docs/roadmap.md).
