# Historical Program Dataset

Structured records behind [historical-structural-analysis.md](historical-structural-analysis.md).
Numbers are tagged; **UNKNOWN is used, never a fabricated figure.** This is a first cut from repo
evidence + the innovation-contest literature; the full ~60-program sweep is staged (needs web
research the current environment can't fully run — firecrawl CLI/key absent, WebSearch budget-limited).

Fields: program · organizer · type · participants · selection · problem structure · economics
(with tag) · IP/follow-on · output · what happened · failure mode · source-quality.

| Program | Type | Economics (tagged) | Output / result | Failure mode | Src |
|---|---|---|---|---|---|
| DARPA Grand/Urban/Robotics/SubT | Prize tournament | purses $1M–$3.5M [O] | autonomous-driving breakthrough (later industry) | slow, costly to run; winner≠product | fed data |
| NASA / Luminary Labs vehicles | Prize (run for hire) | $2.8M–$15M contracts; $100M ceiling [O] | staged tech prizes | ops cost ≈ purse | USAspending |
| XPRIZE | Foundation prize | rev $31.4M; **op cost ≈ purse** [O] | milestone prizes | expensive to operate | 990 |
| InnoCentive / Wazoku | Open-innovation market | avg award ~$20K, some >$100K [O]; seeker posting fee reported $15–35K [O] | scored solutions to posted problems | needs scorable objective; solver≠implementer | repo/press |
| Topcoder | Crowdsourcing market | $100K single NASA challenge; $200K+ enterprise [O] | algorithms/software | productionization gap | Harvard case |
| Kaggle | Data-science contests | sponsored custom; majors $200K–$1M [O] | models/leaderboard | narrow to ML; overfit-to-metric | repo |
| Accenture/DLA Gen-AI hackathon | Enterprise hackathon (delivered) | **$1.27M** [O] | delivered build event | — | fed data |
| Enterprise hackathon (contractor) | Hackathon-as-a-service | $28–68K logistics / $240–300K series / $600K–2.5M delivered [O] | event + varying delivery | logistics-only = low value | fed data |
| IDEO | Innovation consulting | federal engagements $0.5M–$3M [O] | design/prototype work | premium senior labor | fed data |
| SRC | University R&D consortium | **~$2.28M/member/yr** [O]; 255 scholar hires 2024 [O] | pre-competitive chip R&D | narrow to member interests | annual report |
| MIT Media Lab | Affiliate consortium | ~$560K/member [O] | research + IP access | — | repo |
| Stanford HAI | Affiliate w/ directed wallet | $1M / $5M tiers, $400K wallet [O] | research tokens + access | — | brochure |
| LF Research | Sponsored research | $25K–$95K+ studies; slots $50/15/5K [O] | commissioned reports | — | prospectus |
| Forrester TEI / IDC | Commissioned marketing research | $50K–$250K+; verified $271,929 one study, $2.8M program [O] | branded ROI study | built on the vendor's own customers | USAspending/Vendr |
| Expert networks (GLG etc.) | Access marketplace | $1,000–$1,400/call, ~73% margin [O] | expert calls | — | repo |
| Omnibus (SSRS/Researchscape) | Multi-client survey | $1,000/question, confidential per client [O] | shared-fieldwork data | — | rate cards |
| ETHGlobal | Crypto hackathon | sponsor tracks $10–20K; $225K–$525K prize pools [O]; $350M+ raised by teams [O] | prototypes + ecosystem | crypto-specific | site |
| MassChallenge | Zero-equity accelerator | ~$150–300K/corporate partner implied [O] | startup cohort | — | 990 |
| YC / EF / Antler | Accelerators | YC $500K/7%; EF/Antler $90–250K/6–12% [O] | funded companies | — | repo |
| Cerebral Valley | Premium AI-builder event | tickets $199–$2,999 + sponsorships [O] | event + deals | — | repo |
| Reality Hack (MIT) | Premium hackathon | tiers to $65–95K; $5K = travel+housing for 4 [O] | event + scholarships | — | prospectus |
| Cal Hacks / HackMIT / etc. | Collegiate hackathons | ladders $500–$80K; HackMIT $250K/70 sponsors [O] | event + recruiting | commodity attention | prospectuses |
| On Deck / buildspace | Builder communities | On Deck $2,990 tuition; buildspace $3–5M ARR sponsorships [O] | community | novelty wore off; wound down | letters |

**Quantitative lesson that survives the tags:** the six-figure-plus comparables are **delivered R&D
(Accenture $1.27M), commissioned research (Forrester $50–250K), university research consortia
($0.5–2.3M), and directed-wallet affiliate programs**. The sub-$50K comparables are **logistics-only
hackathons, ordinary sponsorship, and expert calls.** The gap between them is *attached deliverable +
IP/research layer* — exactly the archetype-2/3 + directed-wallet spine.

## Staged next pass (needs web research)

The full dataset (Part II fields: implementation_rate, renewal_signal, measured_outcome, failure_mode
per program across ~60 programs) requires a firecrawl/web sweep the current environment can't fully
run. It is the clearly-marked next research task; the structure above holds the schema it fills.
