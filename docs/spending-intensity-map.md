# Spending-Intensity Map — Ranked Wars, Evidence-First

> Ranked output of `engine/spend_intensity.py` (`spend_intensity.rank_categories`). Concept in
> [economic-arms-races.md](economic-arms-races.md); the gaps inside these wars in
> [structural-gap-map.md](structural-gap-map.md); the full 20-gap ranking in
> [high-value-gap-ranking.md](high-value-gap-ranking.md). Raw cited evidence:
> `scratchpad/sweep_dossier.md`.

**Governing rule:** *Evidence != Claim != Hypothesis != Decision.* Every dollar figure is **real,
supply/market-side** evidence with a cited URL. The intensity dimensions are **ordinal readings of
that supply-side evidence** — they measure how hot the war is, **not** whether anyone will pay us.
No buyer was contacted: demand-side WTP is **UNKNOWN** and is the gating unknown. A rational value
ceiling is **not** observed WTP. Status: **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**. ⚠️ = secondary
or not primary-verifiable.

---

## How this ranking works (and refuses to cheat)

`spend_intensity.rank_categories` orders wars on a **decomposed tuple**, never a single collapsed
score (the engine's explicit rule against hiding a weak dimension). The ordering is
**evidence-gated** — a war cannot rank on spend it cannot show:

```
key = ( EVIDENCE_ORDER.index(evidence_strength),   # 1. how real is the evidence — LEADS
        economic_value,                            # 2. size of the prize
        competitive_intensity,                     # 3. spending-war heat
        cost_of_failure,                           # 4. cost of failure
        decision_urgency,                          # 5. urgency
        hackathon_fit )                            # 6. our structural advantage
```

`EVIDENCE_ORDER` (weakest→strongest): `HYPOTHETICAL → INFERRED_JOB_POST → PUBLIC_STATEMENT →
REGULATORY_FILING → PROGRAM_ANNOUNCEMENT → BUYER_STATED → SIGNED_COMMERCIAL`. **This sweep tops out
at PROGRAM_ANNOUNCEMENT.** There is zero `BUYER_STATED` and zero `SIGNED_COMMERCIAL` evidence *by
design* — no buyer was contacted — which is exactly why every ranking below is a ranking of
**spend intensity**, not of demand.

Money magnitudes are `beliefs.Belief` objects defaulting to UNKNOWN
(`SpendCategory.current_annual_spend`). A war with UNKNOWN magnitude is not deleted — it is flagged
as needing evidence and **cannot outrank** an evidenced war on numbers it cannot produce.

Ordinals: **NONE / LOW / MED / HIGH** (0..3).

---

## The map (evidence-first, then decomposed dimensions)

| War | Cited annual spend / magnitude | Evidence strength | Competitive intensity | Cost of failure | Urgency | Hackathon fit | Note |
|---|---|---|---|---|---|---|---|
| **Enterprise AI ROI / transformation** | JPM **$2B/yr** AI (in $19.8B tech); McKinsey 28% of firms >10% ICT | PUBLIC_STATEMENT | HIGH | HIGH | HIGH | HIGH | Explicit stated bottleneck — Dimon: ROI *"difficult to quantify."* Sharpest wedge. |
| **Drug-discovery R&D productivity** | **$2.2B/drug** (>$3.5B elsewhere) | PUBLIC_STATEMENT / REG FILING | HIGH | HIGH | MED | MED | Huge cost base; fit limited by domain-expertise depth. |
| **Airline IROPS / disruption recovery** | Southwest **$1.3B** IT; meltdown ~$1.1B + $140M penalty | PUBLIC_STATEMENT | MED | HIGH | HIGH | HIGH | Buyer-tied dollars; CRISIS_SIMULATION fits well. |
| **Retail returns / reverse-logistics** | NRF **$890B** returns (2024); UPS–Happy Returns deal | PROGRAM_ANNOUNCEMENT | MED | MED–HIGH | MED | MED | Most surprising *non-technical* battleground. |
| **Developer adoption & platform lock-in** | AWS Activate **$8B** credits (to $200K/startup) | PROGRAM_ANNOUNCEMENT | HIGH | MED | MED | HIGH | Best natural fit; but premium WTP historically capped ⚠️ (sponsorship economics). |
| **Enterprise AI compute buildout** | Microsoft **$80B** FY25 capex | PUBLIC_STATEMENT | HIGH | HIGH | MED | LOW | Macro attribution; low fit. |
| **Insurance claims cycle-time & leakage** | Bain **$100B** GenAI-in-claims (estimate); Allstate 5–7d→<24h ⚠️ | PROGRAM_ANNOUNCEMENT | MED | HIGH | MED | MED | Size is a consultancy estimate, not buyer outlay. |
| **Cyber-security spend** | Gartner **$212B** (2025), +15.1% | PROGRAM_ANNOUNCEMENT | HIGH | HIGH | MED | MED | Market-level; no single desperate buyer captured. |
| **CPG media incrementality** | P&G **+40% ad ROI**, ~$7.1B ad spend | REGULATORY_FILING | HIGH | MED–HIGH | MED | MED | Filing-grade evidence; agencies conflicted. |
| **Manufacturing rate-ramp assurance** | Boeing **~$1B/month** loss (2024); 737 <38/mo | PUBLIC_STATEMENT | MED | HIGH | HIGH | MED | Domain + safety-confidentiality limited. |
| **Media pre-greenlight retention** | Netflix **$18B** content (2025) | PUBLIC_STATEMENT | HIGH | MED–HIGH | MED | LOW | Our cohort ≠ their audience. |
| **PE portfolio value-creation** | Blackstone **~$200M** impact (self-reported ⚠️) | PROGRAM_ANNOUNCEMENT | MED | MED | MED | MED | Self-reported; needs independent proof. |
| **Bank agentic-AI output quality** | Goldman **12,000** engineers; GSAI Assistant | PUBLIC_STATEMENT | MED | MED–HIGH | MED | MED | Regulated-workflow confidentiality. |
| **Hospital demand-matched staffing** | Travel-nurse market **~$14.2B** (2025) | PUBLIC_STATEMENT | MED | MED–HIGH | MED | MED | Regulated; domain expertise. |
| **AI-native drug hit-rate validation** | Recursion earnings; Eroom cost base | REGULATORY_FILING | MED | HIGH | LOW | MED | Long outcome latency. |
| **Fintech high-LTV acquisition (CAC)** | Chime ~$1.4B marketing, CAC ~$356 > ARPU ⚠️ | PUBLIC_STATEMENT (secondary ⚠️) | HIGH | MED | MED | MED | Best figure is analyst/LinkedIn, not a filing. |
| **Defense autonomy generalization** | Anduril **$20B** Army contract ⚠️ | PROGRAM_ANNOUNCEMENT (secondary ⚠️) | MED | HIGH | MED | MED | Clearances / ITAR / access. |
| **Grid interconnection speed** | NextEra **15 GW** (→30) by 2035 | PUBLIC_STATEMENT | MED | HIGH | MED | LOW | Regulatory bottleneck; may be un-hackathon-able. |
| **Big-tech capex→adoption certainty** | Microsoft **$80B** FY25 (as attribution problem) | PUBLIC_STATEMENT | HIGH | HIGH | MED | LOW | Macro, hard to attribute. |
| **AI-talent compensation** | Meta **$300M/4yr** per hire | PUBLIC_STATEMENT | HIGH | HIGH | HIGH | LOW | **Loudest war, lowest fit — deliberately de-ranked.** |
| **Federal hard-problem breakthroughs** | Challenge.gov / DARPA prizes — **UNKNOWN** | PROGRAM_ANNOUNCEMENT | MED | MED | LOW | HIGH | Magnitude UNKNOWN; competes with HeroX/XPRIZE. |
| **Supply-chain resilience** | Maersk qualitative — **magnitude UNKNOWN** ⚠️ | PROGRAM_ANNOUNCEMENT | MED | MED–HIGH | MED | MED | No buyer-tied $ retrieved; WTP UNKNOWN. |

---

## The honest ranking

The composite the message specifies — **money + urgency + scarcity + gap + hackathon fit +
accessible buyer**, evidence-first and de-ranking big wars where our fit is weak — produces this
top tier (consistent with [high-value-gap-ranking.md](high-value-gap-ranking.md)):

1. **Enterprise AI ROI / transformation.** The biggest *confirmed, buyer-tied recurring* spend
   with an **explicitly stated bottleneck** (Dimon on record). Money **HIGH**, urgency **HIGH**,
   scarcity **HIGH**, fit **MED–HIGH**. A neutral party holds a structural advantage no vendor has.
   The sharpest wedge — but fit is not a slam dunk (confidentiality + external validity are the real
   risks).
2. **Drug-discovery R&D productivity.** Enormous cost base (Eroom), a genuine
   independent-parallel-search gap. De-ranked below #1 only because **fit is MED** (domain-expertise
   depth); strongest as an *augmented* environment with domain experts embedded.
3. **Operations under shocks — airline / manufacturing / logistics.** Big buyer-tied dollars
   (Southwest $1.3B, Boeing ~$1B/mo) and the **CRISIS_SIMULATION** archetype fits unusually well.
   Data access and domain are the constraints.
4. **Retail returns / reverse-logistics.** $890B, operations-shaped, clear ops buyer, good
   simulation/optimization fit. The most surprising *non-technical* battleground.
5. **Developer adoption & neutral choice data.** Highest *natural* fit, strong evidence — but
   correctly demoted to fifth because premium WTP is historically **CONTRADICTED** by sponsorship
   comparables ([STATE.md](STATE.md)). Kept because fit + evidence are strong even if the price is
   doubtful.

**Deliberately de-ranked: the AI-talent compensation war** (Meta $300M/4yr) — loudest by dollars,
but **hackathon fit LOW**. It sorts high on evidence, economic_value, and urgency, and then
`hackathon_fit` (the last term in the ordering key) correctly sinks it against wars we can actually
fill. The message forbids forcing "elite builders" to be the answer, so it is not.

---

## Which wars are SOFT (say so plainly)

The ranking above is only honest if the weak evidence is named, not buried:

- **Supply-chain resilience — magnitude UNKNOWN.** Maersk publicly prioritizes *"resilient,
  multimodal, tech-enabled supply chains"*
  ([Maersk](https://www.maersk.com/insights/resilience/2024/06/25/resilience-and-innovation)), but
  **no hard buyer-tied dollar figure was retrieved.** `current_annual_spend` stays an UNKNOWN
  Belief; per `rank_categories` this war **cannot outrank** any evidenced war on magnitude. The war
  is real *qualitatively*; its WTP is not established here. ⚠️
- **Fintech CAC — best figure is secondary.** Chime *"spent about $1.4 billion on marketing, 35% of
  revenue"*, CAC ~$356 vs. ARPU ~$212–245 — but the source is an analyst/LinkedIn post
  ([Mikula](https://www.linkedin.com/posts/jasonmikula_from-22-24-chime-spent-about-14-billion-activity-7328508544947793921-G_wO)),
  **not a filing**. It ranks as PUBLIC_STATEMENT with a ⚠️; treat the dollar figure as provisional.
- **Insurance $100B is a consultancy estimate** (Bain), not a buyer-tied outlay; Allstate's <24h
  claim is a secondary blog ⚠️.
- **PE ~$200M, Defense $20B, Allstate cycle-time** — all secondary or self-reported ⚠️.
- **Grid / big-tech capex / federal prizes** — real spend but **fit LOW** (or magnitude UNKNOWN for
  prizes); they belong on the map, not near the top.

---

## The "$100K / $500K / never>$20K" test on the top wars

`spend_intensity.spend_rationale` runs each war through the message's rationale test — *why would a
rational buyer spend a lot on this?* — and returns a structured answer that **asserts no WTP**. The
readings for the top tier:

- **Enterprise AI ROI.** `why_care_at_100k` = attributable AI ROI. `what_makes_a_higher_number_rational`
  = cost_of_failure **HIGH**, cost_of_delay **HIGH**, value_of_winning **HIGH**. `economic_surface_exists`
  = **True** (economic_value & competitive_intensity both HIGH). `spend_evidenced` = **True** ($2B/yr).
  A $500K number is *rational* against a multi-billion budget — but the `note` holds: **WTP UNKNOWN**.
- **Drug discovery.** Surface **exists**, spend **evidenced** ($2.2–3.5B/drug). A high number is
  rational on cost_of_failure **HIGH** — yet the AI-uplift is UNKNOWN, so this is a *ceiling*, not a
  price.
- **Airline IROPS.** Surface **exists**, spend **evidenced** ($1.3B). `budget_this_would_replace` =
  IT/ops modernization. High number rational on cost_of_delay **HIGH** (8% of revenue at risk).
- **Developer adoption.** Surface **exists**, spend **evidenced** ($8B credits) — but the comparable
  budget this replaces is *sponsorship*, whose ceiling is **CONTRADICTED** as low. The rationale test
  says a high number is *possible*; the comparables say it is *unlikely* here.

In every case `economic_surface_exists` being True is **not** willingness to pay. The function exists
precisely to keep that line visible: *"Existence of a large surface != willingness to pay."*

---

## The reading the whole map shares

Every dimension above is a reading of **supply-side** evidence: organizations demonstrably spend to
win these outcomes. **Not one column establishes demand-side willingness-to-pay for our
environment.** A `value_of_winning=HIGH` or `cost_of_failure=HIGH` reading is a **rational value
ceiling** — what the outcome is worth to them — and the engine keeps it distinct from observed WTP
on purpose (`spend_rationale.note`: *"Existence of a large surface != willingness to pay. WTP stays
UNKNOWN until a signed check."*).

> **Bottom line:** the spend is real, large, and rankable. Whether that spend redirects toward what
> we sell is **UNKNOWN** — the gating unknown — and the next step is a demand-side falsification
> attempt with buyers, not more supply-side ranking.
