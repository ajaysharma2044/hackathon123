# Cornell Audience Map

**SEED sweep — NON-EXHAUSTIVE. Full run PENDING.** This is a first, bounded pass (16 Firecrawl
calls, 2026-09-12) to map the *structure* of Cornell's student builder population for a
Cornell-only hackathon. It maps who exists and roughly how many — not who will pay.

**Repeatable method (for the full run):** Firecrawl `search` to discover, then `scrape` the
primary Cornell pages (IRP factbook, Duffield active-project-teams roster, Bowers CIS, eLab,
BigRed//Hacks, individual team sites). Throttle ~15s. Log every raw output. Extend per-team
membership counts and per-department enrollment (currently mostly UNKNOWN). Raw evidence:
`scratchpad/cornell_dossier.md`.

> **Evidence ≠ Claim ≠ Hypothesis ≠ Decision.** A retrieved URL is Evidence. "Cornell has 2,000+
> CIS majors" is a Claim (cited). "AI/ML builders are the most commercially legible segment" is a
> Hypothesis. "Target them for the pilot" would be a Decision — and this document authorizes none.

**Tags:** **KNOWN** = on a primary/official page retrieved this sweep · **LIKELY** = derived or
self-reported/secondary · **UNKNOWN** = not verified. **⚠️** = figure is unverified/derived.

Scope discipline: population *structure* only. No private/personal data, no protected traits, no
covert student rankings.

---

## Denominator (institution)

| Level | Figure | Tag | Source |
|---|---|---|---|
| Cornell undergrad (Ithaca), fall 2024 | ~**16,128** | KNOWN | [Wikipedia relaying Cornell IRP](https://en.wikipedia.org/wiki/Cornell_University); authority [IRP factbook](https://irp.dpb.cornell.edu/university-factbook/student-enrollment) (data in Tableau, not scrapeable) |
| College of Engineering | ~800 first-years/yr → ⚠️ ~3,000–3,200 undergrad (derived) | first-years KNOWN; total LIKELY | [Duffield admissions](https://www.duffield.cornell.edu/admissions/) |
| Bowers CIS (CS + Info Sci + Stats/DS) | **2,000+** undergraduate majors | KNOWN | [Bowers milestone](https://bowers.cornell.edu/news-stories/cornell-bowers-cis-hits-milestone-2000-majors) |
| Cornell Tech (NYC) | Graduate-only (MEng/MBA/LLM); **de-weight** for Ithaca undergrad event | KNOWN | [Cornell Tech masters](https://tech.cornell.edu/programs/masters-programs/) |

The realistically *accessible* pool for a Cornell-Ithaca hackathon is a few thousand technical
undergrads (Engineering + Bowers CIS overlap), concentrated further into the ~hundreds who
already self-select into project teams, clubs, and hackathons.

---

## Audience taxonomy

Each segment: approx accessible population (or UNKNOWN); strengths; weaknesses; weekend build;
the corporate audience it **resembles**; the audience it **emphatically does NOT** resemble;
and what NOT to use it for.

### 1. TechnicalBuilder (generalist SWE) — Bowers CIS core
- **Population:** subset of **2,000+ CIS majors** (KNOWN combined; CS-only split UNKNOWN). Feeder orgs: [Cornell AppDev](https://www.cornellappdev.com/), [Hack4Impact](https://www.cornellh4i.org/).
- **Strengths:** full-stack web/mobile, ship fast, comfortable with APIs/SDKs.
- **Weaknesses:** thin on production ops, security, scale, enterprise procurement realities.
- **Weekend build:** working web/mobile app, API integration demo, a functional MVP.
- **Resembles:** a vendor's *developer-relations top-of-funnel* (students evaluating SDKs/APIs).
- **Does NOT resemble:** a paying engineering buyer, a platform team running production at scale, or an enterprise procurement decision-maker.
- **Do NOT use for:** inferring enterprise purchase intent, security/compliance signal, or willingness-to-pay.

### 2. AI-ML — Cornell Data Science + Bowers AI/DS
- **Population:** [Cornell Data Science](https://cornelldata.science/subteams) = **92 members** (KNOWN), 4 subteams incl. ML Engineering + a compute cluster; plus DS/Stats share of CIS majors (UNKNOWN split).
- **Strengths:** model building, data pipelines, applied ML; the most *commercially legible* skill right now.
- **Weaknesses:** research/notebook bias; evaluation rigor, deployment, and data-governance maturity vary.
- **Weekend build:** trained/fine-tuned model demo, RAG/agent prototype, data-driven analytics tool.
- **Resembles:** early-career ML-tool *evaluators* — a plausible dev-tools/AI-infra top-of-funnel.
- **Does NOT resemble:** an ML platform buyer, an MLOps team, or anyone signing an AI-infra contract.
- **Do NOT use for:** claiming enterprise AI demand or productionization competence.

### 3. ORIE-Optimization — operations research
- **Population:** UNKNOWN (no headcount retrieved). Dept exists: [Cornell ORIE](https://www.duffield.cornell.edu/orie/).
- **Strengths:** optimization, simulation, probability, stats — quantitative modeling.
- **Weaknesses:** less software-shipping muscle; fewer polished front-ends in 48h.
- **Weekend build:** scheduling/routing optimizer, simulation, a quantitative decision tool.
- **Resembles:** analytics/operations-modeling *interns*.
- **Does NOT resemble:** an operations-software buyer or a supply-chain enterprise account.
- **Do NOT use for:** validating demand for optimization software.

### 4. ECE-Hardware / Robotics — Engineering project teams
- **Population:** UNKNOWN per team. **~25 active engineering project teams** (KNOWN roster): [active-project-teams](https://www.duffield.cornell.edu/student-project-teams/active-project-teams/) — CUAUV, CU Autonomous Drone, Combat Robotics, Cornell Cup Robotics, Mars Rover, Rocketry, Racing/Baja/Hyperloop/Electric Vehicles, Design Build Fly, ChemE Car, SensTech, etc.
- **Strengths:** embedded systems, controls, mechatronics, disciplined multi-semester engineering.
- **Weaknesses:** hardware iteration is slow; a 48h window favors software; team cultures are project-locked.
- **Weekend build:** sensor/embedded demo, a controls prototype, a constrained hardware hack.
- **Resembles:** hardware/embedded R&D *talent pool*.
- **Does NOT resemble:** an industrial/hardware procurement buyer or a manufacturing account.
- **Do NOT use for:** fast-turnaround software demand signal, or hardware WTP.

### 5. Product-Design — DTI / AppDev / IS
- **Population:** [Cornell DTI](https://www.cornelldti.org/) self-reports **~50+** PMs/designers/devs/BAs across **8 projects** (LIKELY, [LinkedIn](https://www.linkedin.com/company/cornelldti)); AppDev teaches Product Design + iOS/Android/Backend courses; plus Information Science majors (share UNKNOWN).
- **Strengths:** product thinking, UX/UI, cross-functional teaming, shippable apps.
- **Weaknesses:** community-impact framing over commercial framing; monetization is not their instinct.
- **Weekend build:** polished product MVP with real UX, campus-utility apps.
- **Resembles:** early product/design *talent* and PM top-of-funnel.
- **Does NOT resemble:** a product-org buyer or a design-tool enterprise account.
- **Do NOT use for:** B2B product-market-fit or pricing signal.

### 6. Quant — Quant Fund / Algo Trading / CDS Quant subteam
- **Population:** [Cornell Quant Fund](https://cornellquantfund.org/) runs a competition drawing **150+ students** (KNOWN; membership UNKNOWN); [CATC](https://www.cornellalgo.com/); CDS Quant Finance subteam.
- **Strengths:** probability, statistical learning, market microstructure, backtesting; already sponsor-courted (Jump Trading, IMC).
- **Weaknesses:** finance-specific; narrow domain transfer.
- **Weekend build:** trading strategy/backtester, market data tool, quant game.
- **Resembles:** quant-finance/HFT *recruiting* pipeline (a real, proven sponsor demand in that niche).
- **Does NOT resemble:** a generalist enterprise-software buyer.
- **Do NOT use for:** anything outside quant-finance recruiting/brand.

### 7. Founder — Entrepreneurship ecosystem
- **Population:** [eLab](https://www.elabstartup.com/) accelerates **~8–12 companies/yr** ($5,000 investment, founded 2008) (KNOWN); [Entrepreneurship at Cornell](https://eship.cornell.edu/) ecosystem; [Blackstone LaunchPad](https://www.linkedin.com/company/blackstone-launchpad-at-cornell) ($4.5M grant, 2015; reach UNKNOWN); [Rev hardware accelerator](https://www.revithaca.com/prototyping-hardware-accelerator/).
- **Strengths:** venture framing, pitching, willingness to commercialize — the segment closest to *thinking about value capture*.
- **Weaknesses:** tiny N; early-stage; not enterprise operators.
- **Weekend build:** a venture pitch + prototype, not just a tech demo.
- **Resembles:** a *deal-flow / recruiting* audience for VCs, accelerators, founder-recruiters.
- **Does NOT resemble:** an enterprise buyer, or a proxy for corporate purchasing behavior.
- **Do NOT use for:** modeling how a company decides to buy anything.

---

## Which subpopulations plausibly create commercial value — as HYPOTHESES

1. **AI-ML (CDS + Bowers DS)** — the most *legible* skill to would-be sponsors right now; plausible dev-tools/AI-infra recruiting + brand top-of-funnel. **Hypothesis, not demand.**
2. **Quant** — the one segment with *already-demonstrated* sponsor pull (Jump, IMC courting the Trading Competition). Narrow but real.
3. **Founder / eLab** — the only cohort natively oriented toward value capture; useful as VC/accelerator deal-flow, tiny N.
4. **TechnicalBuilder (CIS core)** — largest accessible pool; classic dev-relations funnel, but the *least differentiated* commercially.

---

## 3–5 best-evidenced Cornell strengths (KNOWN)

1. **Deep, broad technical builder base** — 2,000+ CIS majors + a large engineering college. [Bowers](https://bowers.cornell.edu/news-stories/cornell-bowers-cis-hits-milestone-2000-majors)
2. **An unusually dense, institutionalized project-team culture** — ~25 active engineering teams on the official roster. [Duffield](https://www.duffield.cornell.edu/student-project-teams/active-project-teams/)
3. **A structured AI/ML org with real infra** — Cornell Data Science, 92 members, own compute cluster. [CDS](https://cornelldata.science/subteams)
4. **A proven, sponsor-attractive quant scene** — Quant Fund + 150-student competition backed by Jump/IMC. [Quant Fund](https://cornellquantfund.org/)
5. **A mature entrepreneurship pipeline** — eLab (8–12 ventures/yr since 2008), EaC, Blackstone LaunchPad, Rev. [eLab](https://www.elabstartup.com/)
6. **A large, established hackathon channel** — BigRed//Hacks, 400+ students, 48h. [BigRed//Hacks](https://www.bigredhacks.com/)

---

## What this seed CAN and CANNOT support

**CAN:** describe the *structure* of the population — which technical segments exist at Cornell,
roughly how many, what they can credibly build in a weekend, and which subpopulations are
*hypothetically* commercially interesting and why.

**CANNOT:**
- **It does NOT establish that any company will pay.** Demand-side willingness-to-pay is **UNKNOWN** and remains the **gating unknown**. Nothing here is a demand signal.
- **"Cornell students are elite" is marketing, not a commercial thesis.** Prestige is not a reason a sponsor pays; this document deliberately refuses that framing.
- **Student behavior's predictive validity for enterprise contexts is itself UNKNOWN** and must be *tested, not assumed*. A student evaluating an SDK is not an enterprise buyer, and no arrow from one to the other is established here.
- Several counts remain **UNKNOWN** (CS-vs-IS-vs-Stats split; ORIE/ECE/MechE/AEP/Math/Econ/Dyson enrollment; most per-team membership; total students reached by EaC/Blackstone; current status of "CU Air" and "Cornell Autonomous Bicycle", not on the current roster).

---

*Seed sweep: 16 Firecrawl calls, 2026-09-12. Raw evidence: `scratchpad/cornell_dossier.md`.*
