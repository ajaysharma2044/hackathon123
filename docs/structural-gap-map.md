# Structural-Gap Map — "What Can't the Buyer Buy Today?"

> Output of `engine/gap_finder.py` run over the wars in
> [economic-arms-races.md](economic-arms-races.md) /
> [spending-intensity-map.md](spending-intensity-map.md). Ranked in
> [high-value-gap-ranking.md](high-value-gap-ranking.md). Raw cited evidence:
> `scratchpad/sweep_dossier.md`.

**Governing rule:** *Evidence != Claim != Hypothesis != Decision.* The spend in each war is **real,
supply/market-side** evidence. **Every "they cannot buy…" cell is a HYPOTHESIS** — a structural-gap
guess, not an observed buyer need. No buyer was contacted; demand-side WTP is **UNKNOWN** (the
gating unknown), and a rational value ceiling is **not** observed WTP. Status:
**KNOWN / LIKELY / UNKNOWN / CONTRADICTED**. ⚠️ = secondary evidence.

---

## The two-gate REAL test

`gap_finder.StructuralGap.is_real_gap` fires only when **both** gates clear the floor
(`GAP_ADVANTAGE_FLOOR = MED`):

```
REAL_GAP  ⟺  gap_severity >= MED   AND   hackathon_advantage >= MED
```

`StructuralGap.verdict()` returns one of three, and the order of the checks matters:

- **NOT_A_GAP** — `gap_severity < MED`: an existing substitute already covers this well. (A large
  market does *not* upgrade a gap; a well-served problem is not a gap however big the money.)
- **NOT_OURS** — severity clears but `hackathon_advantage < MED`: a real gap, but our environment
  holds no structural advantage at filling it.
- **REAL_GAP** — both clear: genuinely unmet **and** structurally suited to our environment.

`gap_severity` and `hackathon_advantage` are kept **decomposed** — never averaged into one score
(the same discipline as `score.py`'s HackathonAdvantage). Ordinals: **NONE / LOW / MED / HIGH**.
`hackathon_advantage` mirrors the `HAdv` column in
[high-value-gap-ranking.md](high-value-gap-ranking.md).

---

## The map

| War | They CAN buy | They CANNOT buy (HYPOTHESIS) | Closest substitute | Gap severity | Our advantage | Verdict | Scarce asset |
|---|---|---|---|---|---|---|---|
| **Enterprise AI ROI** (JPM $2B/yr; Dimon: *"difficult to quantify"*) | vendor benchmarks, internal pilots, consultants | a *neutral causal* read on whether AI actually makes their people faster | conflicted vendor claims / self-serving internal pilot | HIGH | HIGH | **REAL_GAP** | `NEUTRAL_CAUSAL_EVIDENCE` |
| **Drug discovery** (Eroom $2.2–3.5B/drug) | one internal team on one path; CROs | 30 *independent* target/approach explorations, fast | CONSULTING (advises, doesn't wet-lab search) | HIGH | MED | **REAL_GAP** | `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH` |
| **Airline IROPS** (Southwest $1.3B IT) | scheduling software, IT modernization | real-time optimal re-accommodation policy, stress-tested under cascading shocks | vendors sell scheduling, not tested recovery policy | HIGH | HIGH | **REAL_GAP** | `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH` |
| **Retail returns** (NRF $890B; UPS deal) | cheaper reverse logistics (Happy Returns) | *pre-purchase* prediction of which orders will be returned | logistics handles returns; none reduce *volume* | MED | MED | **REAL_GAP** | `CROSS_DISCIPLINARY_SOLUTION_SEARCH` |
| **Insurance claims leakage** (Bain $100B; Allstate ⚠️) | STP speed, claims-automation vendors | ground-truth on leakage they *never detect* (silent overpayment) | vendors optimize speed, not truth | HIGH | MED | **REAL_GAP** | `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH` |
| **Developer adoption** (AWS $8B credits) | their own funnel telemetry | proof credits *cause* retention; greenfield choice data on devs who chose a rival | vendor sees only its own users (Datadog admits skew) | MED–HIGH | HIGH | **REAL_GAP** | `GREENFIELD_DEVELOPER_DECISION_DATA` |
| **Manufacturing rate-ramp** (Boeing ~$1B/mo) | consultants, QA vendors | predictive assurance a rate increase won't reintroduce defects | consultants advise; can't run parallel line simulations | HIGH | MED | **REAL_GAP** | `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH` |
| **AI-drug hit-rate** (Recursion; Eroom) | the AI-drug co's own self-report | *external* validation that AI hit-rate beats traditional | self-reported by the interested party; no neutral benchmark | HIGH | MED | **REAL_GAP** | `NEUTRAL_CAUSAL_EVIDENCE` |
| **PE value-creation** (Blackstone ~$200M ⚠️) | the fund's internal claim | *causal* proof AI value-creation is real, not correlation | claimed internally; LPs want independence | MED | MED | **REAL_GAP** | `NEUTRAL_CAUSAL_EVIDENCE` |
| **CPG media incrementality** (P&G +40% ROI) | agencies, MMM vendors | causal incremental-media read vs. correlation | agencies conflicted (paid on spend) | HIGH | MED | **REAL_GAP** | `NEUTRAL_CAUSAL_EVIDENCE` |
| **Cyber spend efficacy** (Gartner $212B) | security tools, pen-tests | proof spend actually reduces breach probability | vendors sell tools, not neutral efficacy evidence | MED–HIGH | MED | **REAL_GAP** | `NEUTRAL_CAUSAL_EVIDENCE` |
| **Bank agentic-AI quality** (Goldman 12,000 eng) | internal metrics | trusted measure of agentic-AI output quality in regulated flows | internal metrics self-serving; regulators want independence | MED–HIGH | MED | **REAL_GAP** | `NEUTRAL_CAUSAL_EVIDENCE` |
| **Hospital staffing** ($14.2B travel-nurse) | agency nurses (premium) | demand-matched staffing that avoids premium agency spend | vendors supply nurses; none redesign the demand-match | MED–HIGH | MED | **REAL_GAP** | `CROSS_DISCIPLINARY_SOLUTION_SEARCH` |
| **Fintech high-LTV CAC** (Chime ~$1.4B ⚠️) | ad-platform optimization | find high-LTV users *before* paying blended CAC | ad platforms optimize clicks, not LTV | MED | MED | **REAL_GAP** ⚠️ | `UNBIASED_COMPETITIVE_CHOICE_DATA` |
| **Defense autonomy** (Anduril $20B ⚠️) | test-range trials, primes | assurance autonomy generalizes outside test conditions | primes can't self-certify neutrally; range ≠ field | HIGH | MED | **REAL_GAP** ⚠️ | `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH` |
| **Logistics disruption foresight** (Maersk ⚠️, magnitude UNKNOWN) | reactive tracking tools | forward visibility of disruptions before they hit | tools react; none give tested forward policy | MED | MED | **REAL_GAP** ⚠️ (magnitude UNKNOWN) | `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH` |
| **Federal breakthroughs** (Challenge.gov) | procurement, existing prize platforms | solutions to problems whose answer doesn't exist yet | HeroX / XPRIZE already run prizes | HIGH | HIGH | **REAL_GAP** (crowded) | `EXTERNAL_RND_EXPLORATION` |
| **Media pre-greenlight** (Netflix $18B) | post-hoc audience analytics | pre-greenlight prediction a title drives retention | data teams see post-hoc; our cohort ≠ audience | MED | **LOW** | **NOT_OURS** | — |
| **Grid interconnection** (NextEra 15 GW) | more generation capacity | interconnection speed the grid physically can't deliver | a regulatory/process bottleneck, not a search problem | HIGH | **LOW** | **NOT_OURS** | — |
| **Big-tech capex→adoption** (Microsoft $80B) | internal demand forecasts | certainty capex converts to durable adoption | internal forecasts self-serving; macro attribution | MED | **LOW** | **NOT_OURS** | — |
| **AI-talent compensation** (Meta $300M/4yr) | recruiters, comp packages | a *measure* of which researchers move the frontier vs. price-signal noise | recruiting exists; frontier-attribution does not | HIGH | **LOW** | **NOT_OURS** | — |
| **Enterprise AI compute** (Microsoft $80B) | data-center capacity | certainty the capacity converts to adoption | (same as capex→adoption) | LOW–MED | LOW | **NOT_A_GAP / NOT_OURS** | — |

⚠️ rows rest on secondary or magnitude-UNKNOWN evidence; their verdicts are provisional (see
[spending-intensity-map.md](spending-intensity-map.md), "Which wars are SOFT").

---

## What the two gates threw out (and why that is the point)

The killed verdicts are the map's most useful output — they stop us chasing loud wars we cannot
serve:

- **AI-talent compensation → NOT_OURS.** The loudest war by dollars (Meta $300M/4yr). The gap is
  *severe* — nobody can buy a measure of which researchers actually move the frontier — but our
  `hackathon_advantage` is **LOW**: we are not a senior-researcher recruiter and frontier-attribution
  is not hackathon-shaped. Severity alone never makes a gap ours. This is exactly the de-rank the
  message demanded, produced by the gate rather than by taste.
- **Grid interconnection → NOT_OURS.** A HIGH-severity gap that is a *regulatory/physical*
  bottleneck, not a search problem — no structural advantage for our environment.
- **Big-tech capex→adoption / AI compute → NOT_OURS / NOT_A_GAP.** Macro attribution problems;
  internal forecasts are self-serving but our edge is LOW.
- **Media pre-greenlight → NOT_OURS.** Real gap, but our behavioral cohort is not their mass
  audience, so `hackathon_advantage` is LOW.

A large market does **not** rescue any of these. `is_real_gap` never reads magnitude — only severity
and our advantage — which is the codified refusal to let a big number launder a gap we can't fill.

---

## The recurring scarce asset

Run `gap_finder.assets_in_play` over the REAL gaps and one asset dominates the count. Across
Enterprise AI ROI, AI-drug hit-rate, PE value-creation, CPG incrementality, cyber efficacy, and
bank agentic-AI quality, the "cannot buy" cell is the **same thing worded six ways**:

> **Buyers spend billions and cannot buy neutral, independent, causal proof that their spend
> actually works** — because no incumbent can be trusted to grade its own homework, and every
> internal pilot is self-serving.

This is the dossier's central finding and the #1 structural gap in
[high-value-gap-ranking.md](high-value-gap-ranking.md). A neutral party running *observed parallel
experimentation* can, in principle, produce that evidence in a way a conflicted vendor or a
self-serving internal pilot structurally **cannot**. The scarce asset is **not** "elite student
access" — the message forbids assuming that, and the evidence points elsewhere.

**Honest note on the enum.** `gap_finder.CANDIDATE_ASSETS` does **not yet contain a literal
`NEUTRAL_CAUSAL_EVIDENCE` member** — the closest existing entries are
`UNBIASED_COMPETITIVE_CHOICE_DATA`, `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH`, and
`EXTERNAL_RND_EXPLORATION`. The recurring scarce asset the evidence surfaces is an *implied*
candidate the list should carry explicitly; until it does, the six "neutral causal proof" gaps above
are tagged `NEUTRAL_CAUSAL_EVIDENCE` here and map to the three existing members as their nearest
kin. The other REAL gaps split across the enum as tagged:

- `INDEPENDENT_PARALLEL_TECHNICAL_SEARCH` — drug discovery, airline IROPS, insurance leakage,
  manufacturing, defense autonomy, logistics foresight.
- `GREENFIELD_DEVELOPER_DECISION_DATA` / `UNBIASED_COMPETITIVE_CHOICE_DATA` — developer adoption,
  fintech high-LTV.
- `CROSS_DISCIPLINARY_SOLUTION_SEARCH` — retail returns, hospital staffing.
- `EXTERNAL_RND_EXPLORATION` — federal breakthroughs.

---

## How the REAL gaps rank among themselves

`gap_finder.rank_gaps` orders gaps on a decomposed tuple, **evidence-first**, with killed gaps
sinking to the bottom:

```
key = ( is_real_gap,                              # REAL gaps float above NOT_OURS / NOT_A_GAP
        EVIDENCE_ORDER.index(evidence_strength),  # then how real the evidence is
        gap_severity,                             # then how unmet
        hackathon_advantage )                     # then our structural edge
```

So a REAL_GAP on secondary evidence (fintech CAC ⚠️, defense autonomy ⚠️, logistics foresight ⚠️)
sorts **below** a REAL_GAP on a filing or a PROGRAM_ANNOUNCEMENT, even at equal severity — the same
evidence-gating discipline as `spend_intensity.rank_categories`. `real_gaps` is the simple filter to
"the ones worth pursuing" (both gates pass); `rank_gaps` then orders the whole set with the four
NOT_OURS gaps parked at the end.

**Worked verdict — Enterprise AI ROI.** `gap_severity = HIGH` (no vendor can be neutral about its own
tool; internal pilots are self-serving; METR showed devs 19% slower while *feeling* faster) clears
the MED floor. `hackathon_advantage = HIGH` (a neutral party running parallel human+AI arms has an
edge no vendor structurally has) clears it too. Both gates pass →
**REAL_GAP** — "genuinely unmet and structurally suited to our environment." It tops `rank_gaps`
because it also carries the strongest severity and a stated-bottleneck citation. Contrast
**AI-talent compensation**: `gap_severity = HIGH` clears, but `hackathon_advantage = LOW` fails the
second gate → `verdict()` short-circuits to **NOT_OURS** before severity can rescue it.

---

## What this map is, and is not

**It is:** a two-gate filter that separates *real, fillable* gaps from loud wars where we hold no
edge, and it names the one scarce asset that recurs across the winners.

**It is not:** evidence anyone will pay. Every "cannot buy" cell is a **HYPOTHESIS** — the sweep
shows spend and states bottlenecks, but it does **not** show any named buyer would pay us to close
the gap. A REAL_GAP verdict means *"unmet and ours to attempt,"* not *"sold."* Demand-side WTP stays
**UNKNOWN**, and the only thing that moves it out of UNKNOWN is a signed check ([STATE.md](STATE.md)).
