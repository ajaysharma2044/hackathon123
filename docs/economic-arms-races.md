# Economic Arms Races — Map the Wars Already Being Fought

> The concept behind `engine/spend_intensity.py`. Companion to
> [spending-intensity-map.md](spending-intensity-map.md) and
> [structural-gap-map.md](structural-gap-map.md); ranked output in
> [high-value-gap-ranking.md](high-value-gap-ranking.md). Raw cited evidence:
> `scratchpad/sweep_dossier.md`.

**Governing rule:** *Evidence != Claim != Hypothesis != Decision.* Every dollar figure below is
**real, supply/market-side** evidence — a buyer spending, a market size, a filing — traceable to a
cited URL in the dossier. **Every structural gap named here is a HYPOTHESIS.** No buyer was
contacted, so there is **no observed willingness-to-pay anywhere in this document.** A rational
value ceiling (what winning is worth) is **not** observed WTP. Status vocabulary:
**KNOWN / LIKELY / UNKNOWN / CONTRADICTED**. ⚠️ marks any figure that is secondary or not
independently verifiable at a primary source.

---

## The inversion

The old research asked *"who could benefit from what we do?"* — a question that always finds a
yes, because someone can always benefit from anything. That is confirmation, not discovery
([STATE.md](STATE.md)).

The arms-race lens inverts it, and this is the whole idea encoded in `spend_intensity.py`'s module
docstring — **"Spend first, company second"**:

> **Do not look for who could benefit. Find a market where organizations are ALREADY spending
> aggressively to win an economically important outcome — a spending war — and then find the one
> gap inside that war our environment can fill.**

The spend is the evidence that the outcome matters. It is bankable, cited, and already happening,
so we are not guessing whether the pain is real. What stays a hypothesis is the *gap* — the thing
the desperate spender **cannot buy today** — and, above everything, whether they would pay **us**
to close it. That last quantity is **UNKNOWN** and is the gating unknown for every war on this
page.

Two disciplines carry over from the rest of the engine and are enforced in code:

- **Money magnitudes are beliefs, default UNKNOWN** (`spend_intensity.SpendCategory.current_annual_spend`,
  a `beliefs.Belief`). A war is not disqualified for having UNKNOWN spend, but it **cannot be ranked
  above an evidenced war on spend it cannot show** (`spend_intensity.rank_categories` leads on
  `evidence_strength`).
- **A desperation SIGNAL is not an opportunity by itself.** High comp, a huge contract, a new R&D
  unit — `spend_intensity.DesperationSignal.counts_as_opportunity` returns `False` until the signal
  is tied to a concrete `linked_gap`. Loud spend with no fillable gap is just noise.

---

## Reading each war: the decomposed dimensions

Each war below is one `spend_intensity.SpendCategory`. Its intensity is read on the ordinal
dimensions `INTENSITY_DIMS` (0..3 = **NONE / LOW / MED / HIGH**), kept **decomposed** — never
collapsed into one score, per the engine's explicit rule. The readings shown are:

- **DesiredOutcome** — the outcome money is being spent to win (`desired_outcome`)
- **competitive intensity** — how many players are fighting (`competitive_intensity`)
- **cost of failure** — what losing costs (`cost_of_failure`)
- **value of winning** — what winning is worth (`value_of_winning`)
- **scarcity** — how unpurchasable the missing piece is (`scarcity`)
- **urgency** — how time-pressured the decision is (`decision_urgency`)
- **hackathon fit** — our environment's structural advantage in *this* war (`hackathon_fit`)

Every ordinal below is a reading of **supply-side** evidence. None of them measures demand for our
environment; `value_of_winning=HIGH` is a rational ceiling, not a price anyone has agreed to pay.

### The "$100K / $500K / never>$20K" test (`spend_intensity.spend_rationale`)

Before any war is taken seriously, it runs through the rationale test the message specifies —
*why would a rational buyer spend $100K, or $500K, or never more than $20K, on this?* The function
returns a structured, honest answer and, critically, **asserts no WTP**:

- `why_care_at_100k` = the DesiredOutcome itself
- `what_makes_a_higher_number_rational` = `cost_of_failure`, `cost_of_delay`, `value_of_winning`
  (all still just ordinal readings of the surface)
- `economic_surface_exists` = `economic_value >= MED AND competitive_intensity >= MED`
- `spend_evidenced` = is the annual-spend Belief anything other than UNKNOWN?
- `note`: *"Existence of a large surface != willingness to pay. WTP stays UNKNOWN until a signed
  check."*

So a war can pass the rationale test — big surface, high cost of failure — and its WTP is **still
UNKNOWN**. The test tells us where a high number *could* be rational, never that it *is* achievable.

---

## The confirmed spending wars

Ordered as in [high-value-gap-ranking.md](high-value-gap-ranking.md); do not re-rank here.

### 1. Enterprise AI ROI / transformation — **CONFIRMED**

- **DesiredOutcome:** attributable proof that AI spend actually makes the workforce faster/cheaper.
- **Evidence:** JPMorgan *"spends $2 billion a year on developing artificial intelligence
  technology"* inside a $19.8B tech budget
  ([Bloomberg](https://www.bloomberg.com/news/articles/2025-10-07/jpmorgan-s-dimon-says-ai-cost-savings-now-matching-money-spent));
  BofA *"plans to spend around $14 billion on technology this year"*
  ([BI](https://www.businessinsider.com/jpmorgan-tech-budget-ai-20-billion-jamie-dimon-2026-2));
  28% of firms spend *"more than 10 percent of...ICT [budget] on AI"*
  ([McKinsey](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)).
- **DesperationSignal:** `EXEC_MANDATE` + `STATED_BOTTLENECK` — Dimon on record that returns are
  *"difficult to quantify."*
- **Dimensions:** competitive intensity **HIGH** · cost of failure **HIGH** · value of winning
  **HIGH** · scarcity **HIGH** (no vendor can grade its own tool) · urgency **HIGH** · hackathon fit
  **HIGH**.
- **Gap (HYPOTHESIS):** cannot buy a *neutral causal* read on whether AI actually makes their people
  faster.
- **Rationale test:** economic surface **exists**; spend **evidenced**; a $500K number would be
  rational *if* the read genuinely de-risked a multi-billion budget — but **WTP UNKNOWN**.

### 2. Drug-discovery R&D productivity — **CONFIRMED**

- **DesiredOutcome:** earlier truth on which targets/molecules will fail, before the clinic burns
  the budget.
- **Evidence:** *"development costs for a single drug now average $2.2 billion"*
  ([CPHI](https://www.cphi.com/europe/insights/the-r-and-d-productivity-crisis-understanding-the-challenge/)),
  with a >$3.5B figure elsewhere; Recursion building an AI-native platform, *"moving from proving
  that AI can participate in drug discovery"*
  ([Recursion IR](https://ir.recursion.com/news-releases/news-release-details/recursion-reports-fourth-quarter-and-full-year-2025-financial)).
- **DesperationSignal:** `STATED_BOTTLENECK` + `NEW_RND_FACILITY`.
- **Dimensions:** competitive intensity **HIGH** · cost of failure **HIGH** · value of winning
  **HIGH** · scarcity **HIGH** · urgency **MED** · hackathon fit **MED** (domain-expertise depth is
  the limiter).
- **Gap (HYPOTHESIS):** cannot buy 30 *independent* target/approach explorations, fast; and cannot
  buy *external* validation that an AI hit-rate beats traditional discovery.
- **Rationale test:** enormous surface; the AI-uplift itself is **UNKNOWN**, so value-of-winning is
  a ceiling, not observed WTP.

### 3. Airline IROPS / disruption recovery — **CONFIRMED**

- **DesiredOutcome:** real-time optimal re-accommodation of passengers under cascading constraints.
- **Evidence:** Southwest *"investing $1.3 billion in more modern IT systems"*
  ([Cirium](https://www.cirium.com/thoughtcloud/redefining-reliability-how-southwest-became-north-americas-most-on-time-airline/))
  after a 2022 meltdown that cost ~$1.1B + a $140M DOT penalty; Delta hit ~$500M by the 2024
  CrowdStrike outage ([OutageCost](https://outagecost.com/by-industry/airline)).
- **DesperationSignal:** `MISSED_TARGET` + `BUDGET_INCREASE` (large capex after a failure).
- **Dimensions:** competitive intensity **MED** · cost of failure **HIGH** · value of winning
  **HIGH** · scarcity **MED–HIGH** · urgency **HIGH** · hackathon fit **HIGH** (the
  CRISIS_SIMULATION archetype fits unusually well).
- **Gap (HYPOTHESIS):** vendors sell scheduling, not stress-tested recovery *policy*.
- **Rationale test:** buyer-tied dollars are strong; data access and confidentiality are the real
  limits, not surface size.

### 4. Retail returns / reverse-logistics — **CONFIRMED**

- **DesiredOutcome:** stop paying to move goods backward — ideally reduce return *volume*, not just
  handle it cheaper.
- **Evidence:** *"total returns projected to reach $890 billion in 2024"*
  ([NRF](https://nrf.com/media-center/press-releases/nrf-and-happy-returns-report-2024-retail-returns-total-890-billion));
  UPS acquired Happy Returns to own the network
  ([UPS](https://about.ups.com/us/en/newsroom/press-releases/customer-first/ups-to-acquire-hr.html));
  Walmart *"invest nearly $14 billion in automation...supply chain"*
  ([Manufacturing.net](https://www.manufacturing.net/e-commerce/video/21295217/walmart-to-invest-14b-in-automation-supply-chain)).
- **DesperationSignal:** `LARGE_ACQUISITION` + `STATED_BOTTLENECK`.
- **Dimensions:** competitive intensity **MED** · cost of failure **MED–HIGH** · value of winning
  **HIGH** · scarcity **MED** · urgency **MED** · hackathon fit **MED**.
- **Gap (HYPOTHESIS):** cannot buy *pre-purchase* prediction of which orders will be returned;
  logistics only handles returns after they happen.
- **Rationale test:** the most *non-technical* battleground on the board — operations-shaped, clear
  ops buyer, but WTP still **UNKNOWN**.

### 5. Developer adoption & platform lock-in — **CONFIRMED**

- **DesiredOutcome:** durable developer retention, and honest data on greenfield tool choice.
- **Evidence:** AWS *"provided over $8 billion in promotional credits to startups globally"*
  (up to $200K/startup)
  ([AWS](https://aws.amazon.com/aws-startups/learn/applying-for-aws-activate-credits-a-step-by-step-guide/)).
- **DesperationSignal:** `STARTUP_CREDIT_PROGRAM`.
- **Dimensions:** competitive intensity **HIGH** · cost of failure **MED** · value of winning
  **MED–HIGH** · scarcity **MED–HIGH** · urgency **MED** · hackathon fit **HIGH** (highest natural
  fit of any war).
- **Gap (HYPOTHESIS):** cannot buy proof credits *cause* retention vs. subsidize churn; vendors see
  only their own funnel.
- **Rationale test:** the old thesis. Fit is best-in-class, but premium WTP is historically
  **capped** at sponsorship economics ([STATE.md](STATE.md)) — a rational ceiling that comparable
  pricing suggests is *low*, not high.

### 6. Enterprise AI compute buildout — **CONFIRMED**

- **DesiredOutcome:** capacity ahead of demand that converts to durable adoption.
- **Evidence:** Microsoft *"spend $80 billion on AI data centers in FY 2025"*
  ([CNBC](https://www.cnbc.com/2025/01/03/microsoft-expects-to-spend-80-billion-on-ai-data-centers-in-fy-2025.html)).
- **DesperationSignal:** `BUDGET_INCREASE` (capex surge).
- **Dimensions:** competitive intensity **HIGH** · cost of failure **HIGH** · value of winning
  **HIGH** · scarcity **LOW** · urgency **MED** · hackathon fit **LOW**.
- **Gap (HYPOTHESIS):** cannot buy certainty that capex converts to durable enterprise adoption —
  but this is a macro attribution problem, hard for our environment to touch (fit LOW).

### 7. Insurance claims cycle-time & leakage — **CONFIRMED (size = estimate)**

- **DesiredOutcome:** faster claims *and* detection of silent overpayment.
- **Evidence:** Bain, *"The $100 Billion Opportunity for Generative AI in P&C Claims"*
  ([Bain](https://www.bain.com/insights/100-billion-dollar-opportunity-for-generative-ai-in-p-and-c-claims-handling/));
  Allstate ⚠️ *"compress the estimating cycle from five-to-seven days down to under 24 hours"*
  ([Perspective](https://getperspective.ai/blog/allstate-s-ai-claims-strategy-what-quickfoto-claim-and-conversational-ai-mean-for-the-industry) —
  secondary).
- **DesperationSignal:** `STATED_BOTTLENECK` + `EXEC_MANDATE`.
- **Dimensions:** competitive intensity **MED** · cost of failure **HIGH** · value of winning
  **HIGH** · scarcity **HIGH** · urgency **MED** · hackathon fit **MED**.
- **Gap (HYPOTHESIS):** cannot buy ground-truth on leakage they *never detect*; STP speed increases
  undetected leakage. The $100B is a **consultancy estimate**, not a buyer-tied outlay.

### 8. Cyber-security spend — **CONFIRMED (market-level)**

- **DesiredOutcome:** proof that spend reduces breach probability.
- **Evidence:** *"projected to total $212 billion in 2025, an increase of 15.1%"*
  ([Gartner](https://www.gartner.com/en/newsroom/press-releases/2024-08-28-gartner-forecasts-global-information-security-spending-to-grow-15-percent-in-2025)).
- **DesperationSignal:** `BUDGET_INCREASE` (sustained).
- **Dimensions:** competitive intensity **HIGH** · cost of failure **HIGH** · value of winning
  **HIGH** · scarcity **MED–HIGH** · urgency **MED** · hackathon fit **MED** (RED_TEAM_ARENA).
- **Gap (HYPOTHESIS):** cannot buy proof spend actually reduces breach probability; vendors sell
  tools, not neutral efficacy evidence. No single desperate buyer captured — market-level only.

### 9. Media pre-greenlight retention — **CONFIRMED**

- **DesiredOutcome:** know before greenlight whether a title will drive retention.
- **Evidence:** Netflix *"content spending, set to hit $18 billion in 2025"*, CFO says *"not
  anywhere near a ceiling"*
  ([Variety](https://variety.com/2025/digital/news/netflix-content-spending-2025-ceiling-cfo-1236328510/)).
- **DesperationSignal:** `BUDGET_INCREASE` (very high recurring spend).
- **Dimensions:** competitive intensity **HIGH** · cost of failure **MED–HIGH** · value of winning
  **HIGH** · scarcity **MED** · urgency **MED** · hackathon fit **LOW** (our behavioral cohort ≠
  their audience).
- **Gap (HYPOTHESIS):** cannot buy pre-greenlight certainty a title drives retention; data teams see
  only post-hoc.

### Other confirmed wars mapped in the dossier

Same structure, lower fit or softer evidence — full readings in
[high-value-gap-ranking.md](high-value-gap-ranking.md) rows 7–20:

- **CPG media incrementality** — P&G *"Advertising return on investment has improved nearly 40%"*,
  ~$7.1B ad spend ([P&G AR2024](https://us.pg.com/annualreport2024/fueled-by-productivity/)). Gap:
  causal incremental-media read vs. correlation (agencies are paid on spend).
- **Manufacturing rate-ramp assurance** — Boeing *"lost nearly a billion dollars a month in 2024"*,
  737 capped <38/mo ([BBC](https://www.bbc.com/news/articles/cz7erzxr9vpo)). Gap: predictive
  assurance a rate increase won't reintroduce defects.
- **Bank agentic-AI output quality** — Goldman *"oversees a 12,000-person engineering team"*, GSAI
  Assistant deployed ([BI](https://www.businessinsider.com/goldman-sachs-marco-argenti-cio-interview-ai-engineers-careers-2025-9)).
  Gap: a trusted measure of agentic-AI output quality in regulated workflows.
- **PE portfolio value-creation proof** — Blackstone ⚠️ *"delivering an estimated $200 million of
  bottom line impact"* ([Blackstone](https://www.blackstone.com/investing-in-ai/) — self-reported).
  Gap: independent causal proof the value-creation is real.
- **Hospital demand-matched staffing** — travel-nurse market *"projected to decline 16% to $14.2
  billion"* ([SIA](https://www.staffingindustry.com/news/global-daily-news/after-pandemic-boom-travel-nursing-finds-new-footing)).
  Gap: demand-matched staffing that avoids premium agency spend.
- **Grid interconnection speed** — NextEra *"build 15 gigawatts of new power generation for data
  center hubs by 2035"* ([CNBC](https://www.cnbc.com/2025/12/08/nextera-to-build-15-gigawatts-power-data-centers-google.html)).
  Gap: interconnection speed the grid physically can't deliver — a regulatory bottleneck, likely
  un-hackathon-able (fit LOW).
- **Defense autonomy generalization** — Anduril ⚠️ *"$20 billion, sole-source contract"*
  ([Overt Defense](https://www.overtdefense.com/2026/03/24/u-s-army-awards-anduril-20-billion-ai-battlefield-tech-contract/)).
  Gap: assurance autonomous systems generalize outside test conditions. Access/ITAR-gated.
- **Federal hard-problem breakthroughs** — Challenge.gov / DARPA prize model
  ([Challenge.gov](https://www.challenge.gov/)). Gap: solutions to problems whose answer doesn't
  exist yet; magnitude **UNKNOWN**.

---

## The war we deliberately DID NOT chase

- **AI-talent compensation war** — Meta *"pay packages of up to $300 million over four years"*
  ([WIRED](https://www.wired.com/story/mark-zuckerberg-meta-offer-top-ai-talent-300-million/)).
  This is the **loudest war by dollars** in the entire sweep. It is also the one where our
  environment holds **low structural fit** (hackathon fit **LOW**): we are not a senior-researcher
  recruiter, and *"measure which researchers move the frontier vs. price-signal noise"* is not a
  hackathon-shaped problem. Per `DesperationSignal.counts_as_opportunity`, a `HIGH_COMP` signal we
  cannot tie to a fillable gap **does not count as an opportunity**. Loud ≠ ours.

---

## What this map is, and is not

**It is:** a cited, decomposed map of where economically important spending wars are *already*
underway — the supply/market side. For 9 of 10 candidate wars the spend is **KNOWN**.

**It is not:** evidence that any buyer will pay for our environment. Every gap above is a
**HYPOTHESIS**; every intensity reading is supply-side; `value_of_winning=HIGH` is a rational
ceiling, not a price. Demand-side WTP is **UNKNOWN** — the gating unknown — and the only thing that
moves it is a signed check ([STATE.md](STATE.md)). The next move is not more supply-side scraping;
it is a falsification attempt against WTP with real buyers.
