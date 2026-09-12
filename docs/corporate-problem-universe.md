# The Corporate Problem Universe

> **SEED sweep — NON-EXHAUSTIVE.** This is a bounded first pass: **24 named organizations
> across 13 industries**, gathered from a real, cited web-evidence run (~30 Firecrawl
> calls). The full **150-300 organization sweep is PENDING** (method to extend it is at the
> bottom). Treat this as the shape of the map, not the map.

**Governing rule:** *Evidence != Claim != Hypothesis != Decision.*
Every row below is real Evidence (a retrieved URL + an exact quote). Every "structural gap"
is a **HYPOTHESIS**, not an observed need. No buyer was contacted, so there is no
willingness-to-pay anywhere in this document. The rational value ceiling of an outcome is
**not** the same thing as observed WTP.

Status vocabulary used throughout: **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**.
Evidence-strength tags: `PUBLIC_STATEMENT` / `REGULATORY_FILING` / `PROGRAM_ANNOUNCEMENT`
(no `INFERRED_JOB_POST` this pass — we scraped statements/filings/programs, not postings).
⚠️ marks anything not independently verifiable at a primary source.

---

## What a "spending war" is here

An outcome economically important enough that organizations **already spend aggressively** to
win it — signalled by very high comp, mass hiring, large contracts, acquisitions, credit
programs, new R&D units, executive mandates, or publicly stated bottlenecks. The sweep looks
for that spend **and** a structural gap: something the desperate spender plausibly **cannot
buy today**. The gap is always a hypothesis.

---

## The real problems found (each cited)

| Industry | Organization | Spending war (outcome) | Evidence (exact quote) | Source | Magnitude | Strength |
|---|---|---|---|---|---|---|
| AI/cloud | **Meta** | Top AI research talent | "pay packages of up to $300 million over four years" | [WIRED](https://www.wired.com/story/mark-zuckerberg-meta-offer-top-ai-talent-300-million/) | $300M/4yr per hire | `PUBLIC_STATEMENT` |
| AI/cloud | **Microsoft** | AI compute capacity | "spend $80 billion on AI data centers in FY 2025" | [CNBC](https://www.cnbc.com/2025/01/03/microsoft-expects-to-spend-80-billion-on-ai-data-centers-in-fy-2025.html) | $80B FY25 | `PUBLIC_STATEMENT` |
| AI/cloud | **AWS** | Developer lock-in | "provided over $8 billion in promotional credits to startups" | [AWS](https://aws.amazon.com/aws-startups/learn/applying-for-aws-activate-credits-a-step-by-step-guide/) | $8B credits | `PROGRAM_ANNOUNCEMENT` |
| Banking | **JPMorgan** | AI transformation | "spends $2 billion a year on developing artificial intelligence technology" | [Bloomberg](https://www.bloomberg.com/news/articles/2025-10-07/jpmorgan-s-dimon-says-ai-cost-savings-now-matching-money-spent) | $2B/yr; $19.8B tech | `PUBLIC_STATEMENT` |
| Banking | **Bank of America** | Tech modernization | "plans to spend around $14 billion on technology this year" | [BI](https://www.businessinsider.com/jpmorgan-tech-budget-ai-20-billion-jamie-dimon-2026-2) | $14B/yr | `PUBLIC_STATEMENT` |
| Banking | **Goldman Sachs** | Agentic AI in engineering | "oversees a 12,000-person engineering team" | [BI](https://www.businessinsider.com/goldman-sachs-marco-argenti-cio-interview-ai-engineers-careers-2025-9) | 12,000 engineers | `PUBLIC_STATEMENT` |
| Fintech | **Chime** ⚠️ | Customer acquisition cost | "Chime spent about $1.4 billion on marketing, 35% of revenue" | [Mikula/LinkedIn](https://www.linkedin.com/posts/jasonmikula_from-22-24-chime-spent-about-14-billion-activity-7328508544947793921-G_wO) | CAC ~$356 vs ARPU ~$212-245 | `PUBLIC_STATEMENT` |
| Insurance | **P&C sector** (Bain) | Claims cycle-time & leakage | "The $100 Billion Opportunity for Generative AI in P&C Claims" | [Bain](https://www.bain.com/insights/100-billion-dollar-opportunity-for-generative-ai-in-p-and-c-claims-handling/) | $100B (est.) | `PROGRAM_ANNOUNCEMENT` |
| Insurance | **Allstate** ⚠️ | Claims estimating speed | "compress the estimating cycle from five-to-seven days down to under 24 hours" | [Perspective](https://getperspective.ai/blog/allstate-s-ai-claims-strategy-what-quickfoto-claim-and-conversational-ai-mean-for-the-industry) | 5-7d -> <24h | `PUBLIC_STATEMENT` |
| Retail | **Retail sector** (NRF) | Returns / reverse-logistics | "total returns projected to reach $890 billion in 2024" | [NRF](https://nrf.com/media-center/press-releases/nrf-and-happy-returns-report-2024-retail-returns-total-890-billion) | $890B (2024) | `PROGRAM_ANNOUNCEMENT` |
| Logistics | **UPS** | Own reverse-logistics network | "returns have long frustrated shoppers and retailers" | [UPS](https://about.ups.com/us/en/newsroom/press-releases/customer-first/ups-to-acquire-hr.html) | 12,000+ drop-offs | `PROGRAM_ANNOUNCEMENT` |
| Retail | **Walmart** | Supply-chain automation | "invest nearly $14 billion in automation technologies and...supply chain" | [Manufacturing.net](https://www.manufacturing.net/e-commerce/video/21295217/walmart-to-invest-14b-in-automation-supply-chain) | ~$14B | `PUBLIC_STATEMENT` |
| CPG | **Procter & Gamble** | Media / marketing productivity | "Advertising return on investment has improved nearly 40%" | [P&G AR2024](https://us.pg.com/annualreport2024/fueled-by-productivity/) | +40% ROI; >$1B productivity | `REGULATORY_FILING` |
| Airlines | **Southwest** | IROPS disruption recovery | "investing $1.3 billion in more modern IT systems" | [Cirium](https://www.cirium.com/thoughtcloud/redefining-reliability-how-southwest-became-north-americas-most-on-time-airline/) | $1.3B IT; meltdown ~$1.1B | `PUBLIC_STATEMENT` |
| Airlines | **Delta** | IROPS resilience | "$1.1 billion plus a $140 million DOT penalty" (industry outage costs) | [OutageCost](https://outagecost.com/by-industry/airline) | Delta outage ~$500M | `PUBLIC_STATEMENT` |
| Logistics | **Maersk** ⚠️ | Supply-chain resilience | "Resilient, multimodal, tech-enabled supply chains" | [Maersk](https://www.maersk.com/insights/resilience/2024/06/25/resilience-and-innovation) | **UNKNOWN** | `PROGRAM_ANNOUNCEMENT` |
| Manufacturing | **Boeing** | Production ramp / quality | "lost nearly a billion dollars a month in 2024" | [BBC](https://www.bbc.com/news/articles/cz7erzxr9vpo) | ~$1B/mo; 737 <38/mo | `PUBLIC_STATEMENT` |
| Pharma | **Pharma sector** (Eroom) | R&D productivity | "development costs for a single drug now average $2.2 billion" | [CPHI](https://www.cphi.com/europe/insights/the-r-and-d-productivity-crisis-understanding-the-challenge/) | $2.2B-$3.5B/drug | `PUBLIC_STATEMENT` |
| Pharma | **Recursion** | AI-native drug discovery | "moving from proving that AI can participate in drug discovery" | [Recursion IR](https://ir.recursion.com/news-releases/news-release-details/recursion-reports-fourth-quarter-and-full-year-2025-financial) | **UNKNOWN** (pipeline) | `REGULATORY_FILING` |
| Healthcare | **US hospitals** | Clinical labor / nurse staffing | "travel nurse revenue projected to decline 16% to $14.2 billion" | [SIA](https://www.staffingindustry.com/news/global-daily-news/after-pandemic-boom-travel-nursing-finds-new-footing) | $14.2B market | `PUBLIC_STATEMENT` |
| Energy | **NextEra** | Power for AI data centers | "build 15 gigawatts of new power generation for data center hubs by 2035" | [CNBC](https://www.cnbc.com/2025/12/08/nextera-to-build-15-gigawatts-power-data-centers-google.html) | 15-30 GW by 2035 | `PUBLIC_STATEMENT` |
| Media | **Netflix** | Content / engagement | "content spending, set to hit $18 billion in 2025" | [Variety](https://variety.com/2025/digital/news/netflix-content-spending-2025-ceiling-cfo-1236328510/) | $18B (2025) | `PUBLIC_STATEMENT` |
| Private equity | **Blackstone** ⚠️ | AI portfolio value creation | "delivering an estimated $200 million of bottom line impact" | [Blackstone](https://www.blackstone.com/investing-in-ai/) | ~$200M (self-reported) | `PROGRAM_ANNOUNCEMENT` |
| Defense | **Anduril** | Battlefield AI procurement | "$20 billion, sole-source contract to Anduril Industries" | [Overt Defense](https://www.overtdefense.com/2026/03/24/u-s-army-awards-anduril-20-billion-ai-battlefield-tech-contract/) | $20B contract | `PROGRAM_ANNOUNCEMENT` |
| Government | **DARPA / Challenge.gov** | Buy breakthroughs via prizes | "USA.gov lists active federal prize competitions" | [Challenge.gov](https://www.challenge.gov/) | **UNKNOWN** | `PROGRAM_ANNOUNCEMENT` |

Two cross-cutting, market-level confirmations (not single-buyer captures):
**Cyber-security** — "projected to total $212 billion in 2025, an increase of 15.1%"
([Gartner](https://www.gartner.com/en/newsroom/press-releases/2024-08-28-gartner-forecasts-global-information-security-spending-to-grow-15-percent-in-2025)),
`PROGRAM_ANNOUNCEMENT`; and **enterprise AI adoption** — 28% of firms spend "more than 10
percent of their...ICT [budget] on AI"
([McKinsey](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)),
`PROGRAM_ANNOUNCEMENT`.

---

## Spending-war candidates — what the seed can confirm

| Candidate war | Status | Anchor evidence |
|---|---|---|
| AI-talent / compensation | **KNOWN** the spend exists | Meta $300M/4yr |
| Enterprise AI-adoption / transformation | **KNOWN** | JPM $2B/yr; McKinsey 28% >10% ICT |
| Developer adoption & platform lock-in | **KNOWN** | AWS Activate $8B |
| Customer acquisition cost | **LIKELY** (⚠️ secondary source) | Chime $1.4B marketing |
| Cyber-security spend | **KNOWN** (market-level) | Gartner $212B |
| Airline IROPS / disruption-recovery | **KNOWN** | Southwest $1.3B IT |
| Retail returns / reverse-logistics | **KNOWN** | NRF $890B; UPS deal |
| Insurance claims cycle-time / leakage | **KNOWN** (size = estimate) | Bain $100B; Allstate |
| Drug-discovery R&D productivity | **KNOWN** (cost); AI-uplift **UNKNOWN** | Eroom $2.2-3.5B/drug |
| Supply-chain resilience | **UNKNOWN magnitude** | Maersk qualitative only |

Every StructuralGapHypothesis behind these — "cannot buy attributable ROI," "cannot buy
return prediction," "cannot buy leakage they never detect," "cannot buy interconnection
speed" — is a **HYPOTHESIS**. The seed shows spend and states bottlenecks; it does **not**
show that any named buyer would pay us to close the gap.

---

## Sweep method (PENDING full run)

Repeatable procedure to extend this seed to the full 150-300 org universe:

1. **Frame the industry list.** Hold ≥12 industries (the 13 here + adjacents: telecom,
   automotive, agriculture, real estate, semiconductors, gaming). Target ~15-25 orgs each.
2. **One query per (org, battleground).** Template:
   `firecrawl search "<org> <outcome> spend|investment|hiring|contract <year> billion"`.
   Run with the CLI: `FIRECRAWL_API_KEY=… npx -y firecrawl-cli@latest search "<q>"`.
   Throttle ~15s between calls (429s appear above ~3 rapid calls).
3. **Discover then verify.** Use `search` to find the primary source, then `scrape` only
   earnings calls, 10-Ks/annual reports, official program pages, procurement notices, and
   prospectuses. Cap scrapes; snippets from `search` already carry quotable content.
4. **Record every row** with all 11 columns of the master table (see raw dossier). Exact
   quotes ≤15 words. If a number isn't in the retrieved source, write **UNKNOWN** — never
   infer one.
5. **Tag strength** with the four allowed values only; never `SIGNED_COMMERCIAL` or
   `BUYER_STATED` (we have no buyer contact).
6. **Separate desperation-signal type** (comp / hiring / contract / acquisition / credits /
   R&D unit / mandate / stated bottleneck / missed target / procurement / prize / budget).
7. **Keep the raw dossier append-only**; regenerate this polished doc from it.
8. **De-dup and cluster** captures into the ~10 candidate wars; promote a war to **KNOWN**
   only when ≥2 independent buyer-tied sources exist.

Raw evidence for this seed: `scratchpad/sweep_dossier.md` (all rows, per-industry notes,
candidate-war status). ~30 Firecrawl calls used.

---

## What this seed can and cannot support

**It CAN:**
- Map where spending wars **plausibly exist** — the supply/market side. Organizations
  demonstrably pour money into these outcomes (KNOWN for 9 of 10 candidate wars).
- Name concrete, cited **structural-gap hypotheses** worth testing.
- Give a repeatable method to scale to the full universe.

**It CANNOT:**
- Establish that **any buyer will pay for our environment.** Demand-side willingness-to-pay
  is **UNKNOWN** — the gating unknown — because no buyer was contacted.
- Convert a **rational value ceiling** (what an outcome is worth) into **observed WTP.** These
  are different quantities; conflating them would be a category error.
- Prove any structural gap is *real* rather than *hypothesized*. ⚠️ Every gap column is a
  hypothesis until a buyer confirms it.

> **Bottom line:** The spend is real and large. Whether that spend redirects toward what we
> sell is **UNKNOWN** and is the next thing to test — on the demand side, with buyers, not
> with more supply-side scraping.
