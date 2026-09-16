---
title: "Hackathon123 -- Comparable Events Dataset (Sourced)"
type: reference
created: 2026-09-14
tags: [hackathon123, research, dataset, hackathon-benchmarks, sponsorship, comparable-events]
ai-first: true
status: research
confidence: mixed
related-notes:
  - "[[hackathon123 MOC]]"
  - "[[hackathon-benchmarks-trends]]"
  - "[[qualitative-data-collection-methods]]"
sources:
  - "mlh.com, news.mlh.io, sponsor.mlh.io, github.com/MLH -- ecosystem scale + demographics"
  - "devpost.com, info.devpost.com -- platform scale + 2026 AI trends"
  - "hackberkeley.org, realityhackatmit.com, events.linuxfoundation.org (CNCF), upop.mit.edu -- sponsorship prospectuses (PDF)"
  - "SHRM 2025/2026, NACE 2024/2025 (via secondary), getraffi.ai, stealthagents.com -- recruiting cost benchmarks"
  - "pennapps devpost, Microsoft Imagine Cup, Bolt/dev.to -- prize pools"
---

**Related:** [[hackathon123 MOC]] · [[hackathon-benchmarks-trends]] · [[qualitative-data-collection-methods]]

# Hackathon123 -- Comparable Events Dataset (Sourced)

## For future Claude

The sourced quantitative dataset for the hackathon123 comparable-events run (2026-09-14): real benchmark data on the hackathon ecosystem, sponsorship economics, prize pools, recruiting-cost anchors, and (in the roster sections) individual elite/premium events. Built to design our own ~200-elite event and to arm sponsor sales calls with numbers that survive scrutiny. Every datapoint carries a retrieved source URL + as-of date + confidence tag; undisclosed values are UNKNOWN, never invented. Cross-cluster patterns and the pitch-facing brief live in [[hackathon-benchmarks-trends]]; qualitative-capture methods in [[qualitative-data-collection-methods]].

> [!important] Sourcing standard (read before quoting any number)
> Confidence: **stated** = published by the source org itself · **high** = reputable/peer-reviewed, corroborated · **medium** = single secondary / market-research-mill / vendor blog · **speculation** = inference or uncorroborated single source. Undisclosed values are UNKNOWN (never invented); labeled estimates are kept separate from facts. Assembled during the 2026-09-14 overnight run; source infrastructure note: Firecrawl was rate-limited/quota-exhausted this session (HTTP 429/402), so figures were gathered via WebSearch/WebFetch + direct PDF reads -- several sponsor pages that were JS-heavy or 502'd could not be read and are marked UNKNOWN.

---

## Section A -- Ecosystem and scale (MLH / Devpost)

The macro baseline: how big the collegiate hackathon world is, who participates, and whether it is growing.

**MLH (Major League Hacking) -- event and participant volume**
- **2025 Season: 184 hackathons + programs, 150,000+ hackers.** (news.mlh.io, 2025-07-08, stated) https://news.mlh.io/welcome-to-the-2026-hackathon-season-07-08-2025
- **2026 Season: 200+ student hackathons planned.** (same source, stated)
- Historical baseline: **220 hackathons / 78,000+ participants in AY 2018-2019** (Hardin 2021, ACM ToCE 21(2), citing MLH data, medium). doi.org/10.1145/3433168
- 2019-2020: 1,200+ events (hackathons + workshops + meetups + conferences combined), +20% YoY (news.mlh.io State of the League 2020, stated). https://news.mlh.io/the-state-of-the-league-2020-09-08-2020
- Homepage hero stats (current, mlh.com, 2026-09-14, stated): "1000+ Annual Events", "100 Countries", "5,000,000+ Developers" -- the 5M figure almost certainly reflects the Feb-2026 MLH acquisition of DEV(dev.to), not hackathon participants; not comparable to the season figures.

> [!note] MLH scale claims vary ~10x by page (different denominators)
> 150,000/season (flow) vs 500,000+ "members" (sponsor.mlh.io) vs 1,000,000+ cumulative "hacker community" incl. "1 in every 3 CS grads has attended an MLH Member Event" (github.com/MLH/mlh-policies, 2026-05-22, stated) vs 5,000,000+ "Developers" (post-DEV-acquisition). Use 150K/season as the hackathon-flow number.

**MLH -- participant demographics** (thin; newest MLH-published figures are 6 years old)
- **~39-40% female or non-binary / ~60-61% male** (up 18% YoY from 2019). news.mlh.io State of the League, 2019-2020 season (published 2020-09-08), stated; corroborated by a 2021 TechTogether analysis.
- Race/ethnicity (2019-2020): 4% Black/African, 7% Latino (same source, stated).
- Student floor policy: **>=80% of attendees must be students** (any level: middle school through recent grad). github.com/MLH/mlh-policies, 2026-05-22, stated.
- Year-in-school split: **UNKNOWN** (never published in aggregate). First-timer share ecosystem-wide: **UNKNOWN** (single-event proxy only: Hack the North "as many as 1/3 first-time," not MLH-wide).

**Devpost -- platform scale**
- Community size: **6,000,000+ builders** (info.devpost.com/product/public-hackathons, stated) vs **4,000,000+** on another Devpost marketing page (same-day retrieval) -- Devpost's own pages disagree; discrepancy unresolved.
- All-time hackathons hosted / all-time prize money: **UNKNOWN** (never published; only a live homepage snapshot of currently-listed hackathons by category exists -- not a lifetime total).
- Devpost 2026 AI Trends Report (real dated primary source): enterprise AI hackathons +83% YoY; agentic-AI ~1-in-4 submissions; repeat participants (7+) ship to production at 2.2x first-timers. https://info.devpost.com/research/ai-trends-report-2026 (2026, stated).

**Market size (hackathon-management-software)** -- three vendor estimates converge ~$1.2-1.4B today, all medium confidence, none independently audited:
- $1.37B (2026) -> $3.98B by 2035, 12.56% CAGR (Business Research Insights)
- $1.21B (2024) -> $6.12B by 2033, 18.6% CAGR (Growth Market Reports)
- $1.28B (2025) -> $3.5B by 2035, 10.6% CAGR (WiseGuyReports)
- A LinkedIn-Pulse "$5.143B by 2031 / 15.1% CAGR" post could not be attributed to a named firm -- speculation, do not use.

---

## Section B -- Sponsorship ladders (what sponsors actually pay)

### Elite collegiate hackathons (public prospectuses)

**Cal Hacks 13.0 (Hackathons at Berkeley)** -- 3,000+ hackers, 300 universities, Oct 23-25 2026, Palace of Fine Arts SF. Source: https://hackberkeley.org/sponsorship.pdf (2026-09-14, stated).

| Tier | Price | Key benefits |
|---|---|---|
| Bronze | $10,000 | Booth, resume book, logo, social, Slack channel, host a tech prize, 50-min API workshop, present on stage |
| Silver | $20,000 | All Bronze + 1-min opening-ceremony stage time |
| Golden Bear | $35,000 | 2x booth, private coffee-chat room, dedicated email blast, co-host activity, 3-min stage |
| Anchor | $50,000 | 3x booth, pre-event workshop, 10-min stage, top co-host branding, name a room |

Past partners: Anthropic, AppLovin, Amazon/Annapurna Labs, Y Combinator, Visa, Postman, Snap AR, Windsurf. (num_sponsors: UNKNOWN exact.)

**MIT Reality Hack** (XR/AR/VR; collegiate-adjacent). Source: https://www.realityhackatmit.com/rhsponsorship-101 (2026-09-14, stated).

| Tier | Price | Key benefits |
|---|---|---|
| Network | $3,000 | Expo table, judging seat |
| Growth | $7,500 | Host a workshop; teams built around sponsor tech |
| Expansion | $15,000 | Host a prize category; more workshops/talks |
| Enterprise | $30,000 | Resume access / recruitment assistance; panelist slot |
| Impact | $65,000 | Photo/video priority; host a networking night; keynote |
| Maximum Visibility | $95,000 | Top branding; custom lounge/media booth; marquee sponsorship |

A la carte: Hack-to-Market $5K-$15K; scholarship donations $500-$5K; engagement boosters (VIP dinners, installations) $3K-$15K. **$95K is the highest confirmed single-tier hackathon-style price in this dataset.**

### Developer-conference comps (pricing ceilings, NOT hackathons)

**KubeCon + CloudNativeCon (CNCF / Linux Foundation), 2026.** Source: https://events.linuxfoundation.org/wp-content/uploads/2025/11/sponsor-cncf-2026_110625.pdf (stated).
- Flagship NA/EU (10,000-12,000 attendees): Diamond **$235,000 / $282,000** (member/non-member) · Platinum $144,000 / $172,800 · Gold $84,000 / $100,800 · Silver $29,500 / $35,400 · Start-up/End-User/Non-profit $12,000. 250+ sponsors/exhibitors at NA 2024.
- Regional (India/Japan/China, 1,000-3,000 attendees): Diamond $125,000 / $150,000 · Platinum $60,000 / $72,000 · Gold $35,000 / $42,000 · Silver $18,000 / $21,600 · Start-up $6,000. Same playbook, price scales ~with attendee count.
- Small co-located summits: Observability Summit NA (~200 attendees) Diamond $25,000 -> Start-up $5,000; Maintainer Summit EU (~300) Supporter $25,000 -> breaks $5,000.
- A la carte add-ons (t-shirt, lanyards, coffee bar, private room, Wi-Fi, recording) cluster $2,500-$40,000 at every size -- a secondary revenue ladder.

**MIT UPOP corporate sponsorship** (university recruiting program comp). Source: https://upop.mit.edu/wp-content/uploads/2024/07/2024-2025-Corporate-Sponsorship-Details.pdf (stated). Local onsite event $1,500 · workshop prizes $1,500 · networking event $2,500 · signature event $5,000 · **Annual Corporate Partner $15,000**.

### Email-gated (no public pricing found -- structural, not a research gap)
HackMIT (sponsor.hackmit.org 502'd 3x; ~1,200 hackers flown in for 2026, tier names Platinum/Gold/Silver/Bronze only), PennApps (351 hackers at PennApps XXIV; no current prospectus public), HackGT, MHacks, Hack the North, PyCon US/PSF 2026 (prospectus exists at python.org/psf/prospectus2026/ but PDF path unresolved), React Summit/GitNation, AI Engineer (bespoke, Sponsorships@ai.engineer). All route sponsors to a "contact us" email. **Named student hackathons keep pricing private; nonprofit-run conferences (CNCF, PSF) publish it** -- an asymmetry worth noting for positioning.

---

## Section C -- Recruiting-cost and prize-pool benchmarks

### Recruiting cost anchors (the sponsorship-ROI argument)
- **Cost-per-hire, SHRM average: $5,475 non-exec / $35,879 exec** (2025 SHRM Benchmarking, direct-spend only). medium (via interviewcost.com citing SHRM).
- **Cost-per-hire, SHRM median: $1,300 non-exec / $15,000 exec** (SHRM 2026, n=4,657, survey Nov 2025-Jan 2026). medium.
- **Tech/software median CPH: $9,000 (range $6,500-$14,000)** (SHRM 2025 + Aptitude Research 2024, via getraffi.ai). medium.
- **University/campus CPH: ~$6,275** (33% above the ~$4,700 all-hire avg); **median university-recruiting budget ~$114,000** (NACE 2024/2025 -- naceweb.org 403'd on 4 fetches; figures repeated by 2+ secondary sources naming the NACE report; primary wording unverified). medium.
- **Third-party recruiter fee: ~20-25% of first-year salary (~$20,000 on a $100K hire)** -- the classic "why a $10K-$50K hackathon sponsorship beats a placement fee" anchor, from "Hackonomics 101" (Komissarouk, MHacks co-founder); medium.com 403'd, figure via search summary -- **verify before putting on a deck.**
- Startup CPH: $25,000-$38,000 all-in for a contingency-recruiter $130K SWE; general range $4,000-$28,000 (stealthagents.com). medium.

> [!warning] Do NOT reuse these unverified marketing claims
> "55% lower cost-per-hire" fintech case study (no named company/method), "4.2 qualified hires/event," and "$300B global economic value from hackathons" (eventflare.io, no methodology) -- all vendor-marketing, uncorroborated. Flagged so they do not leak into sponsor materials.

### Prize pools (bimodal)
- Elite student-run: **PennApps XXIV $32,810** (351 hackers; top prizes were hardware, not cash). devpost, stated. Typical elite-collegiate range ~**$10,000-$50,000** total across tracks (derived from Cal Hacks tech-prize tiers unlocking at $10K, Reality Hack prize category at $15K, PennApps confirmed). medium.
- Corporate/VC-backed online: **Bolt "World's Largest Hackathon" 2025 $1,000,000+** (76,246 registrants; dev.to, stated); VietBUIDL 2025 "$4M" (single source, medium); HackMoney 2026 "~$56K" (speculation, uncorroborated).
- Student startup competition (not a weekend hackathon): **Microsoft Imagine Cup 2025 grand prize $100,000** + $25,000 x2 runners-up (stated).
- Organizer-side cost to HOST (distinct from sponsor revenue): ~$15,000-$25,000 typical small/mid event, up to $1M+ large; agency programs <$50K self-serve / $50K-$200K managed regional / >$200K multi-market (angelhack.com, eventflare.io; medium).

---

## Gaps and low-confidence flags (Sections A-C)

- MLH: no demographic data newer than Sept 2020; year-in-school and ecosystem-wide first-timer share are true UNKNOWNs; aggregate school count UNKNOWN (only "100 countries"); Hacker Census runs but results not self-published; MLH's own partner pricing is custom/opaque by design.
- Devpost: 4M vs 6M community discrepancy unresolved; no lifetime hackathon/prize totals; the ~$5.6M/282-hackathon homepage figure is a live snapshot, not cumulative.
- Market-size reports are template-driven market-research-mill outputs, not audited -- treat ~$1.2-1.4B as indicative.
- HackMIT/PennApps/HackGT/MHacks/Hack the North/PyCon/React Summit/AI Engineer sponsorship prices: not public (email-gated or fetch-blocked) -- do not estimate.
- NACE and Hackonomics figures rest on fetch-blocked primaries (403) -- verify before external use.
- CNCF 2026 prospectus has an internal date inconsistency (Nov 10-12 SLC vs an Oct 26 LA co-located line) -- stale template artifact, flagged not resolved.
- Firecrawl was down all session (429/402); a re-run with a working key may recover the fetch-blocked prospectuses (HackMIT, PennApps, PyCon).

## Section D -- Elite collegiate events (roster)

Nine flagship US/Canada collegiate hackathons, most-recent completed edition (as of 2026-09-14; several 2026 editions are upcoming, not yet run). At this tier the reliably-public dimensions are **attendance, sponsor count, and prize pool**; budgets, per-head cost, selectivity ratios, and outcomes are almost never disclosed (see caveats). Attendance marked "~" is medium-confidence (organizer/press framing or marketing copy); plain figures are Devpost-registered or press-confirmed actuals.

| Event (most recent) | Attendees | Selectivity | Travel/Housing/Food | Sponsors | Prize pool | Primary source |
|---|---|---|---|---|---|---|
| TreeHacks 2026 (Stanford) | **1,096** (invite-only) | **~6.7%** (15,000 apps -> ~1,000) | **T + H + F** (stated) | **29+** (OpenAI, Google, Anthropic, NVIDIA, YC, Cloudflare, Modal, Vercel, Visa) | **3-way: $150K site / $500K press / $1.03M Devpost-itemized (incl. in-kind); 2025 = $200K** | treehacks-2026.devpost.com; stanforddaily.com 2026-02-15 |
| Cal Hacks 12.0 2025 (Berkeley) | **~3,000** (2x the prior 1,750) | UNK | F + on-site mattresses; travel UNK | **60** | **~$200,000** | dailycal.org 2025-10-27 |
| Hack the North 2025 (Waterloo) | 1,000+ | UNK | UNK | UNK (Cohere, Ollama, HUD tracks) | UNK (track prizes only) | uwaterloo.ca 2025-09-18 |
| HackMIT 2025 | ~1,000+ (evergreen figure) | UNK | travel reimbursed ~$200 (2022 policy); on-site H+F (hist.) | **42+** (Anthropic, Cerebras, Jane St, HRT, Citadel, D.E. Shaw, Scale, YC, Vercel) | **$100K+** (4 tracks) | archive.hackmit.org/2025 |
| HackGT 12 2025 (Georgia Tech) | 910 | UNK | **partial travel** (reimbursement pool) | UNK (Capital One, HRT, OpenAI, Perplexity) | UNK ($4K+ cash + hardware) | hackgt-12.devpost.com |
| HackHarvard 2025 | 528 | UNK | F (medium); rest UNK | UNK (Google, ElevenLabs, Cloudflare, Capital One) | non-cash only (18 prizes) | hackharvard-2025.devpost.com |
| HackPrinceton 2025 | ~500-600 | UNK | UNK | UNK | UNK | hackprinceton.com (search synth) |
| MHacks 2025 (Michigan) | **380** actual (vs ~750-1,000 target) | UNK | UNK | UNK (Ford, Snap, Fetch.ai, Google) | **$39,050 cash** + hardware | mhacks-2025.devpost.com |
| PennApps XXVI 2025 (UPenn) | 257 Devpost (~500 site claim) | UNK (hist. ~42% at PennApps XX, 2019) | on-site rest areas + F; travel UNK | **9+** (MLH, Capital One, Cerebras, Bloomberg, D.E. Shaw, Pear VC) | non-cash (23 prizes) | pennapps-xxvi.devpost.com |

### Key sourced figures, conflicts, and confidence
- **Selectivity is essentially undisclosed except TreeHacks 2026: 15,000 applications -> ~1,000 accepted = ~6.7%** (stanforddaily.com 2026-02-15, high). PennApps' only ratio (~30%, ~708 accepted) is historical (PennApps X, ~2013-14) and must not be used for the current event. This is the biggest hole for benchmarking "how selective should a ~200-person event be."
- **Confirmed attendance clusters 250-3,000**, driven by admission philosophy, not prestige: PennApps 257, MHacks 380, HackHarvard 528, HackGT 910, then the 1,000+ tier (Hack the North, TreeHacks, HackMIT) up to Cal Hacks ~3,000. **Pre-event target figures run 2-3x actual** (MHacks marketed 750-1,000+, registered 380) -- never quote a pre-event number as actual.
- **Full provisioning (travel+housing+food) is used as a headline draw where offered**, confirmed only for TreeHacks ("we take care of meals, travels, and lodging") and Cal Hacks (meals/mattresses/showers/hygiene kits; on-site sleeping, not hotels). HackGT runs a partial travel-reimbursement applicant pool. For the other 6, provisioning is UNKNOWN (silence, not "no").
- **Prize pools span ~$4K to $500K with no consistent cash-vs-total convention:** MHacks $39,050 cash (stated); Cal Hacks ~$200K; TreeHacks $150K-guarantee vs $500K post-event-press (unresolved -- press figure likely includes in-kind API/cloud credits at face value); HackHarvard and PennApps award **zero cash** (hardware/gift cards only). Any sponsor-facing prize comparison must specify cash vs total-with-credits.
- **Frontier AI labs (OpenAI, Anthropic, Google/Gemini, Cohere, Perplexity) appear as named sponsors across most events with retrievable rosters** (TreeHacks, Cal Hacks, HackGT, Hack the North) -- direct evidence AI labs are already courting this exact population; useful for sponsor framing.
- **"World's largest collegiate hackathon" is a contested, self-applied label** -- both Cal Hacks and TreeHacks claim it while measuring different things (raw attendance ~3,000 vs selective invite ~1,000 off 15,000 apps). A community ELO site (hackelo.com, single-source/medium) ranks Cal Hacks, HackMIT, Hack the North, TreeHacks as the top-4 peer tier.
- **Prize-pool numbers are inflated by in-kind credits at face value -- always separate cash from total.** TreeHacks 2026 is the clearest case: $150K (evergreen site tagline) vs $500K (press headline) vs **$1,030,875 (Devpost-itemized)** -- the last sums cash + in-kind at face value (a $200K equity-free Human Capital fellowship, Cloudflare credit tiers up to ~$350K, an Interaction Co. $100K bonus). Actual cash grand prizes were modest: 1st $12,000 / 2nd $8,000. TreeHacks 2025's pool was $200K. A sponsor comparing raw "prize pools" without the cash-vs-credits distinction is misled by ~5-7x.
- **HackMIT's sponsor mix skews quant/HFT + AI lab -- a distinct recruiting-buyer segment.** 42+ sponsors in 2025 led by Jane Street, Hudson River Trading, Citadel, D.E. Shaw (elite-recruiting-driven finance firms) alongside Anthropic/Cerebras/Scale/YC -- direct evidence HFT/quant firms pay to access elite student builders, a buyer segment separate from dev-tool sponsors. HackMIT runs its own submission platform ("Plume"), not Devpost; hackmit.devpost.com is frozen on 2013 (693 people / $15K) -- do not use as current data.
- **PennApps is a cautionary contraction data point.** Once billed "the world's largest collegiate hackathon" at stadium scale (Wells Fargo Center, the 76ers arena), the most recent edition (XXVI, 2025) registered only 257 on Devpost at the engineering school -- evidence that even a flagship, first-mover collegiate hackathon can shrink dramatically. Directly relevant to the "how durable / how big" question for our own event.

### Gaps and low-confidence flags (Section D)
- budget_total and per_attendee_cost: **zero disclosures anywhere** across all 9 -- structural, this class of data is simply not public at this tier.
- applications/accepted: only TreeHacks 2026 has a real current ratio; every other selectivity cell is UNKNOWN.
- Sponsorship tier pricing per event: real only for Cal Hacks (Bronze $10K, partial -- full ladder in Section B); **HackPrinceton has a real but unparsed prospectus PDF (hackprinceton.com/images/sponsors/HackPrinceton S25 Prospectus.pdf)** -- the single best remaining lead for tier pricing, a human should open it.
- HackMIT/Hack the North/HackGT current sites are JS-rendered SPAs that returned only titles to WebFetch (Firecrawl was rate-limited) -- their live-cycle detail is UNKNOWN; retry with a JS-capable scraper or fetch the Devpost mirrors.
- Corroboration: only TreeHacks (press + official site) and Hack the North attendance (institutional) meet the >=2-source bar; all other headline numbers rest on a single retrieved source -- provisional pending a second citation.
- outcomes (startups founded, hiring): unverified for all 9; none publish it.

## Section E -- Outcomes research and developer-intelligence market (sourced evidence)

Not event rows -- the academic/industry evidence for (a) why a premium high-difficulty contest is defensible, (b) real post-event outcome baselines, (c) that companies pay for developer intelligence, and (d) the strongest candidate flagship research question. Two hallucination risks were caught and excluded (see caveats).

### E.1 Innovation-contest and hackathon-outcome research
- **Boudreau, Lacetera & Lakhani (2011), "Incentives and Problem Uncertainty in Innovation Contests," Management Science 57(5):843-863** -- on TopCoder data: adding competitors has two opposing effects -- effort dilution (dominates for LOW-uncertainty problems) vs a parallel-path/extreme-value effect (dominates for HIGH-uncertainty problems, where more competitors raises net performance). Basis for positioning a premium, high-difficulty elite contest. https://pubsonline.informs.org/doi/10.1287/mnsc.1110.1322 (high). Precursor HBS WP 09-041 (2008) states the mechanism + IV identification. Commonly cited N=9,661 contests (medium-high; published text paywalled).
- **Nolte, Chounta & Herbsleb (2020), "What Happens to All These Hackathon Projects?" PACM HCI 4(CSCW2):145** -- 78 Devpost hackathons: **35.3% of projects had >=1 GitHub commit after the event, 17.06% by day 6, ~3.5-5% still active at 5 months.** Team skill diversity cut long-term discontinuation hazard 71%; continuation-prediction model 76% accurate. https://dl.acm.org/doi/10.1145/3415216 (stated). The outcome-tracking baseline for a 7/30/90 continuation metric.
- **Medina Angarita & Nolte (2021)** -- founders attend to learn/prototype for an existing idea; pre-existing entrepreneurial motivation predicts founding; no population conversion rate (medium). Springer HCII.
- **Moe et al. (2022, HICSS-55)** -- corporate hackathons raise productivity via engagement/collaboration/learning; virtual hackathons risk MORE isolation unless designed against it (medium). https://arxiv.org/abs/2112.05528
- Hawthorne/observation effect: recognized general SE validity threat, but **no hackathon-specific quantification exists** (would have to be generated by our own event). speculation.
- Hackathon-as-hiring stats (40% of companies use them, 55% lower cost-per-hire, 80% higher satisfaction): **vendor marketing only, no disclosed methodology** -- do NOT present as fact.

### E.2 Developer-intelligence market -- does anyone actually pay?
- **SlashData** -- 30,000+ developers surveyed annually across 168 countries; running Developer Economics since 2010 (26th+ edition); clients incl. Google/Microsoft/Intel/Amazon/Meta. https://www.slashdata.co/about (stated). Proof that syndicated developer research is a ~20-year funded category.
- **Zoom acquired Common Room (2026-07-02, terms undisclosed)** for upstream buyer/developer intelligence; customers incl. Anthropic, Atlassian, Notion, Okta, Snowflake. A public company buying a developer-intelligence platform -- verified, not rumor. https://news.zoom.com/zoom-to-acquire-common-room-bringing-buyer-intelligence-to-its-ai-revenue-platform/ (stated). Common Room raised ~$52M (2021, high); ~$15M ARR est. 2024 (medium). (A "$266.8M" price on a low-quality aggregator is contradicted by primary sources -- EXCLUDED.)
- **Reo.Dev -- $11.3M Series A (2026-07-17, Elevation Capital)** atop $4M seed + $1.2M pre-seed, specifically for developer buying-signal intelligence; 100M+ engineer profiles, 200+ customers (NVIDIA, LangChain, ElevenLabs). https://finance.yahoo.com/technology/ai/articles/reo-dev-raises-11-3-130000758.html (stated).
- **Orbit (cautionary)** -- raised ~$19-21M (a16z seed 2020, Coatue $15M Series A 2021); **acquired by Postman 2024-04 and standalone product sunset within 90 days.** Category is real but intelligence products can get absorbed into platforms rather than persisting standalone. https://blog.postman.com/announcing-postman-has-acquired-orbit/ (stated).
- **"Dark funnel"** is a vendor term (6sense), not academic. Verifiable underpinning: **Gartner (632 B2B buyers, fielded Aug-Sep 2024): 61% prefer a fully rep-free buying experience** (73% avoid irrelevant outreach). https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-sales-survey-finds-61-percent-of-b2b-buyers-prefer-a-rep-free-buying-experience (stated). Use the 61% figure; the recycled "17% of time with vendors" / "70-80% pre-contact" Gartner stats could NOT be verified to a primary page -- do not use.

### E.3 AI-on-developer productivity -- the candidate flagship question (genuinely contested)
- **METR (2025): experienced OSS devs 19% SLOWER with AI tools** (CI +2% to +39%), despite forecasting 24% faster and self-reporting 20% faster. N=16, 246 issues, within-subject RCT, Cursor Pro + Claude 3.5/3.7. https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ (stated).
- **METR follow-up (2026-02-24): raw estimates flip toward speedup but METR calls it "an unreliable signal"** -- 30-50% of devs refused non-AI tasks; optimistic devs increasingly declined; pay cut $150->$50/hr. N=57. https://metr.org/blog/2026-02-24-uplift-update/ (stated). The question is LIVE and contested, not settled -- ideal flagship framing.
- Contradicting speedup RCTs: **Google internal RCT ~21% faster** (N=96, https://arxiv.org/abs/2410.12944, stated); **GitHub Copilot RCT 55.8% faster** on a greenfield JS task (N=95 Upwork freelancers, https://arxiv.org/abs/2302.06590, stated). Likely resolution = task/codebase-familiarity dependence (itself a testable angle).
- Team-level double-edge: **DORA 2024: -7.2% delivery stability, -1.5% throughput** with more AI (medium); **Uplevel (N=800): +41% bug rate, no cycle-time gain** (medium); **Microsoft "Dear Diary" RCT: no significant telemetry change, positive sentiment** (medium). A clean "AI = faster" story is not supported -- build the nuance into the research question.

### Gaps and low-confidence flags (Section E)
- Boudreau N=9,661 corroborated by secondary sources; published text paywalled, not read in full (medium-high).
- No methodology-disclosed hackathon->startup or ->hiring conversion rate exists; all such figures are vendor marketing (flagged, not reported).
- No hackathon-specific Hawthorne quantification exists.
- Common Room total funding inconsistent ($52M vs $52.9-104.9M across aggregators); "$266.8M" acquisition price EXCLUDED as contradicted by primary sources (caught hallucination).
- Gartner "17%/70-80%" figures unverifiable to primary -- excluded; 61% rep-free is verified.
- DORA/Uplevel/Microsoft-N and Orbit Series A rest on secondary sources (primaries gated) -- medium.
- Caught misattribution: a "24%/20%" figure was wrongly attributed to the Google RCT by search synthesis; it belongs to METR -- corrected/excluded.

## Section F -- Premium / AI-builder events (roster, the direct competitor set)

The events most like a planned premium elite builder event. Key finding up front: **the premium AI-builder space is crowded, and the frontier labs who would be hackathon123's sponsors (Anthropic, OpenAI, Mistral) already run their own free, application-gated hackathons at large scale** -- so "premium elite event" alone is table stakes, already occupied by Cerebral Valley and AGI House. This sharpens the white-space question toward the *research/measurement instrument*, not the event. ~20 events researched; the ~14 most decision-relevant below.

| Event (most recent) | Type | Size / selectivity | Ticket price | Sponsor model | Prize pool | Source |
|---|---|---|---|---|---|---|
| **Cerebral Valley AI Summit** (Nov 2026 SF upcoming) | premium invite conf | **200-350, invite-only** | **$199 / $1,299 / $2,999** | ~11 sponsors (Nov'25), inquiry-priced | N/A (talks) | newcomer.co; cerebralvalley.com |
| Cerebral Valley hackathon series | AI-builder | per-event 150-1,000+, app-gated (Opus 4.6: 500/13,000 ~3.8%) | free | sponsor/enterprise fees | $7K-$35K examples | cerebralvalley.ai |
| **AI Engineer World's Fair 2026** | AI-builder conf | **6,000+**, open ticket | **$299 / $1,499 / $1,999 / $2,399** | **7 tiers, ~261 logos** (100 expo) | Startup Battlefield (no cash) | ai.engineer/worldsfair/2026 |
| AI Engineer Summit 2025 (NYC) | premium invite conf | sold out, **invite-only** ("highly curated") | UNK tiers | 4 tiers, ~23 sponsors | endorsed side hackathon | ai.engineer/summit/2025 |
| AI Engineer NY 2026 (finance vertical) | AI-builder conf | 1,000+, open | UNK | Presenting/Plat/Gold/Silver | N/A | ai.engineer/nyc/2026 |
| AGI House SF | premium invite hacker house | ~15k community list; 80+ hackathons since '22 | free RSVP | 38 backers (labs + VCs) | in-kind GPU | agihouse.ai |
| AGI House (Hillsborough, LLC) | premium invite | 100+ at events; **$15K/mo residency** | UNK | 23 backers | UNK | agihouse.org (+ trademark suit) |
| HF0 Residency | premium invite accelerator | **10 teams/cohort**, <=0.01% claimed | N/A (equity) | LP-funded | N/A ($1M/5% hist.) | hf0.com |
| South Park Commons | premium invite community | ~175 active / 1,300+ alumni | **fee-free** | self-funded via own VC fund | N/A | southparkcommons.com |
| YC "Full Stack" hackathon (Jan 2026) | AI-builder | **250**, app-gated (no travel reimb.) | free | 3 (Supabase, Stripe, Brex) | YC interview + prizes | events.ycombinator.com |
| YC Agents Hackathon (Aug 2025) | AI-builder | limited, invite-only | free | 6 (Anthropic, OpenAI, Vercel) | **$65K/$80K (conflict)** | luma.com/pz27h0xy |
| **Anthropic "Built with Opus 4.7" (Apr 2026)** | AI-builder (lab) | **500 from 20,000+ (~2.5%)** | free | sole host (via Cerebral Valley) | **$100K credits + $500/participant** | edtechinnovationhub.com |
| **OpenAI Build Week (Jul 2026)** | AI-builder (lab) | **46,703 registered**, open | free | sole host (Devpost) | **$100K cash** | openai.devpost.com |
| **Mistral Worldwide Hackathon (2026)** | AI-builder (lab) | **1,000+ from 7,000 (~14%), 7 cities** | free | 14 partners | **$200K+ + a hire at Mistral** | worldwide-hackathon.mistral.ai |

### Key sourced figures and distinctive trends
- **Ticket pricing exists only in the conference sub-cluster, never the hackathons.** CV AI Summit $199-$2,999 and AI Engineer WF 2026 $299-$2,399 both scale price ~5-8x with seniority (Leadership/VP tiers). Every hackathon here -- Cerebral Valley's series, all lab hackathons, AGI House, YC -- is **free**, monetized on the sponsor side or (for labs) not monetized at all (recruiting/marketing spend).
- **"Premium" = selectivity, not price.** Invite/application gates with low-single-digit acceptance even when free: Anthropic Opus 4.7 500/20,000 (~2.5%), Cerebral Valley Opus 4.6 500/13,000 (~3.8%). A collegiate hackathon's gate is registration; here it is a competitive application even at $0.
- **Sponsorship tiers are named but almost never priced publicly** -- inquiry-only (sponsorships@ai.engineer; newcomer@newcomer.co), a "call for pricing" posture, unlike collegiate MLH-style rate cards. AI Engineer WF 2026 has 7 tiers (Presenting/Labs/Platinum/Gold/Silver/Bronze/Supporting) across ~261 logos, all prices withheld.
- **Lab hackathons scaled 3-8x in prize pool + applicants in ~2-3 years.** Anthropic: $30,500 / 145 attendees (London Nov 2023) -> $100K + $250K-in-credits / 500-from-20,000 (Apr 2026). Mistral: one unofficial SF hackathon (2024) -> 7-city, 1,000+ builder, $200K+ "Worldwide" (2026). AI Engineer brand: 500 (2023) -> 6,000+ (2026).
- **Size is decoupled from selectivity here** (unlike collegiate, where they move together): an event can be huge AND selective (Anthropic 20K apps, Mistral 7 cities) or tiny AND selective (HF0 10 teams, CV Summit 200). Mass-virtual lab hackathons still hit five figures (OpenAI Build Week 46,703).
- **Two organizer archetypes:** (1) media/community brands -- Cerebral Valley, AI Engineer -- monetize via tickets + inquiry-priced sponsorship + enterprise/recruiting services on a recurring event platform; (2) lab-as-host -- Anthropic/OpenAI/Mistral/Scale run single-sponsor hackathons (num_sponsors 0-1) as pure developer-marketing/recruiting, usually outsourcing production to Cerebral Valley or Devpost.
- **Brand fragmentation and turf wars** are a real feature: two legally distinct "AGI House" entities in active federal trademark litigation (N.D. Cal. 3:25-cv-05773), and the Cerebral Valley hackathon series vs the Cerebral Valley AI Summit are separate entities sharing only a nickname. A crowded, contested naming landscape -- relevant to hackathon123's own (still-unchosen) name.

> [!important] Strategic read for hackathon123
> The single most decision-relevant comp is the **Cerebral Valley AI Summit** (premium, invite-only, 200-350 people, $199-$2,999 tickets + sponsorship, deals seeded there) -- it already occupies the "premium elite AI event" position. Combined with lab-run hackathons pulling 13,000-20,000 applicants for free, this confirms the [[hackathon123-council-verdict]] finding: the event itself is table stakes; the defensible white space is the **rigorous causal + longitudinal research instrument fused onto the elite panel**, which none of these run.

### Gaps and low-confidence flags (Section F)
- **No sponsorship price list found for ANY event** in this cluster (all inquiry-only) -- the biggest hole for competitive pricing; direct outreach to sponsorships@ai.engineer / newcomer@newcomer.co would be needed for real figures.
- AI Engineer attendee counts conflict across its own sources (WF 2024: 2,000 vs 3,000+; WF 2025: 2,000-4,000) -- treat AIE's historical attendance as directional.
- Internal prize-pool inconsistencies on primary pages: YC Agents Hackathon $65K (title) vs $80K (body); OpenAI Build Week $100K (4 sources) vs a discarded $160K AI-summary artifact.
- AGI House sites carry contradictory stats (12 vs 13 unicorn founders; ~$1T vs $1.89T) and a retracted $75M-investment attribution -- flagged, not resolved.
- Scale AI hackathons are the weakest-sourced (primary URLs dead; snippet-only), apparently dormant since 2024.
- HF0 current deal terms no longer public ($1M/5% is 2023-era); acceptance-rate "<=0.01%" is secondary/unconfirmed.
- Excluded unsourced claims: AI Engineer "~9 FTE / $9M+ revenue" (untraceable); fabricated AI Engineer NY 2026 ticket prices (bad LLM extraction, verified false).
- Firecrawl was rate-limited/quota-exhausted the entire session; all figures via WebSearch/WebFetch -- a re-run with a working key may surface inquiry-only PDFs.
