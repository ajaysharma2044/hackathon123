# Venture Market — Founder/VC Discovery as an Opt-In Downstream Consumer

This document describes what is **already built in code**, not a plan. Every behavioral claim
cites `file:symbol`. Every legal claim cites [venture-upside.md](../venture-upside.md). The
house discipline holds throughout: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**, status is
**KNOWN / LIKELY / UNKNOWN / CONTRADICTED**, and **WTP is UNKNOWN** until a signed number
arrives.

---

## The thesis

The venture market is **not** a startup accelerator, a pitch competition, or a sourcing product
bolted onto the side of the event. It is a *downstream, opt-in consumer* of the same
work-evidence graph the event already produces — the same posture the schema states in its header
(`schema/010_talent_venture.sql`: "opt-in downstream consumers of naturally produced event
work-evidence. NOT a recruiting product bolted on the side."). The talent market and the venture
market share one substrate and one set of guardrails (`engine/compliance.py`); the venture market
is simply the `INVESTOR` scope of that substrate.

What that buys us, and what it forbids us, are two halves of the same design:

- A founder/team can make a venture profile visible to investors **only** by an explicit
  `INVESTOR` opt-in (`venture_profile.VentureProfile.investor_visible`, gated in
  `venture_matching.discover`). No opt-in, no discoverability.
- The venture surface of any activity lights up **only** with that opt-in
  (`opportunity_market.fan_out` requires the `INVESTOR` scope for `VentureValue`).
- No founder is ever scored (`compliance.FORBIDDEN_SCORES` includes `founder_quality`,
  `founder_score`; `compliance.assert_not_a_person_score` raises on them).

**Claim (KNOWN, from code):** the venture market reuses the talent substrate and adds three
things — a venture profile, a public-data fund graph, and a decomposed thesis-match — with the
investor scope as a hard gate. **Hypothesis (UNKNOWN):** that anyone will pay for it. Those are
different statements and this repo keeps them apart.

---

## Not every project is a company (Part XXX)

The profile refuses to force startup framing. `venture_profile.VentureProfile.is_company`
defaults to `False`, and the module docstring states it directly: "Not every project is a company
— this does not force startup framing." A weekend project is allowed to be a weekend project.
`continuation_status` can be `STARTUP_FORMED`, but it can equally be `CONTINUED`, `PIVOTED`,
`STOPPED`, or `UNKNOWN` — company-formation is one outcome among several, never the assumed one.

This matters because the alternative — treating every submission as a nascent startup — is
exactly the winner-biased framing the matching layer is built to avoid (see below and
`startup-matching.md`).

---

## Continuation at 30/90 days as a first-class signal (Part XXXVI)

The single most differentiated field is `venture_profile.VentureProfile.continuation_status`
("still building at 30/90 days"). It is a first-class column in the schema
(`venture_profile.venture_id` row is complemented by `startup_attribute` and the `CONTINUATION`
evidence type in `schema/010_talent_venture.sql`), a first-class match dimension
(`venture_matching.MATCH_DIMS` includes `continuation_evidence`), and a first-class fan-out
activity (`opportunity_market.ACTIVITY_FANOUT["CONTINUATION_30D"]`).

The match code scores it explicitly and honestly (`venture_matching.match`):

```
cont_map = {"CONTINUED": 3, "STARTUP_FORMED": 3, "PIVOTED": 2, "STOPPED": 0, "UNKNOWN": None}
```

Note `UNKNOWN` maps to `None`, **not** `0` — missing continuation is neutral, never a penalty
(`compliance.neutral_when_missing`). And `STOPPED` is `0`, not negative — the team that stopped
is not punished, it simply lacks that particular positive signal. This is the honest posture
STATE.md flags as the untested engine of the compounding moat: "Panel retention into 7/30/90-day
tracking is the untested engine of the compounding moat."

**Status:** that continuation *predicts* venture outcomes is a **Hypothesis (UNKNOWN)**, not a
Claim. The code treats it as a signal worth capturing and surfacing, not as proof of anything.

---

## The integrated graph

The venture market composes with, and does not duplicate, the talent substrate:

| Layer | Where | What it holds |
|---|---|---|
| Shared guardrails | `engine/compliance.py` | data levels, visibility scopes, forbidden scores, missing-is-neutral |
| Venture profile | `engine/venture_profile.py`, `venture_profile` table | opt-in team profile, status-tagged claims |
| Fund graph | `engine/fund_graph.py`, `fund` / `investor` tables | public-data funds + investors |
| Match | `engine/venture_matching.py`, `venture_match` table | decomposed thesis fit, no founder score |
| Intro | `engine/mutual_intro.py`, `venture_intro` table | mutual-opt-in contact release |
| Value fan-out | `engine/opportunity_market.py` | one activity → many surfaces, opt-in gated |

The venture tables (`venture_profile`, `venture_visibility`, `venture_claim`, `fund`, `investor`,
`startup_attribute`, `venture_match`, `venture_match_evidence`, `investor_interest`,
`venture_intro`, `venture_outcome`) all reference the shared `team`/`project`/`work_evidence`
records from earlier migrations rather than re-declaring them.

---

## Value fan-out (VentureValue only with INVESTOR opt-in)

`opportunity_market.VALUE_SURFACES` is a **vector**, never auto-summed, and includes
`VentureValue`. The fan-out map (`opportunity_market.ACTIVITY_FANOUT`) pairs each activity with
the surfaces it can serve and the scope each surface requires:

- `REPO_SUBMISSION` → `VentureValue` requires `INVESTOR`
- `PROJECT_DEMO` → `VentureValue` requires `INVESTOR`
- `CONTINUATION_30D` → `VentureValue` requires `INVESTOR`
- `MENTOR_REQUEST` → **no** venture surface at all (comment in code: "never a hiring/venture
  signal — support, not evidence-for-sale")

`opportunity_market.fan_out` enforces the gate through
`compliance.individual_disclosure_allowed`: a surface with a required scope appears only if the
participant opted into that exact scope. A mentor request can never become investor evidence —
asking for help is support, not a sellable signal.

---

## Part LXXVI — VENTURE research questions 11–20

These are open research questions. Each answer separates what the **code already does** from
what remains **UNKNOWN**. None of these is a Decision.

**Q11 — What does a pitch competition or a normal VC sourcing DB (PitchBook, Harmonic, Crunchbase)
miss that this captures?**
Sourcing databases record *claimed* attributes and post-hoc outcomes. This captures **observed
build behavior** (`work_evidence` with `source_kind` in `ARTIFACT_OBSERVED` / `PUBLIC_REPO`) and
**continuation over time** (`continuation_status`), each tagged for epistemic status
(`venture_profile.VentureClaim.status`). A pitch DB shows a deck; this shows what was actually
built and whether the team kept building. STATE.md frames the same edge as "depth (observed causal
behavior) against SlashData's breadth." **Status: LIKELY** as a description of the gap; the value
of the gap to a buyer is **UNKNOWN**.

**Q12 — Is continuation actually useful to an investor?**
Modeled as a first-class signal (`venture_matching.MATCH_DIMS` / `continuation_evidence`), but
whether investors weight it is **UNKNOWN**. The honest note: elite builders are easy to source;
*retention into longitudinal tracking* is the unproven part (STATE.md). Do not oversell.

**Q13 — Do investors care about artifact depth, or only team pedigree?**
The code deliberately refuses to encode pedigree as a score — there is no founder-quality field
anywhere (`compliance.FORBIDDEN_SCORES`). It offers artifact depth instead
(`venture_match_evidence.why` ties a match to concrete `work_evidence`). Whether investors will
act on artifact depth over pedigree is a **Hypothesis (UNKNOWN)**.

**Q14 — Which investors want Cornell / campus-specific sourcing?**
The fund graph can filter by sector, stage, and geography (`fund_graph.funds_in_sector`,
`funds_at_stage`, and `Fund.geography`) but holds **no** "wants-Cornell" attribute today —
[cornell-audience-map.md](../cornell-audience-map.md) maps the *supply* (a few thousand technical
undergrads, hundreds already on project teams) but not investor demand for it. **Status: UNKNOWN**
(no demand-side evidence). Campus-focused pre-seed/seed funds and university-affiliated vehicles
are a **Hypothesis** to test, not a finding.

**Q15 — Who inside the fund owns this workflow — associate, partner, or platform (Part LV)?**
The graph enumerates the roles (`fund_graph.INVESTOR_ROLES` = GP, PARTNER, PRINCIPAL, ASSOCIATE,
PLATFORM, SCOUT) precisely so the buyer question stays explicit. Sourcing/deal-flow work is
typically associate/scout/platform-owned; a partner owns the check. The code does not assume;
`investor.role` is a stored field. **Status: UNKNOWN** which role pays — resolve in buyer
interviews (STATE.md: "we have not spoken to one buyer").

**Q16 — What are the comparables?**
Cited, not derived — [venture-upside.md](../venture-upside.md): Republic pays **$2,500** per
referred startup; Calm Company **$2,000** for a referral, **$5,000** for a referral *with an
investment memo* ("a written memo roughly doubles the price"); PitchBook averages **$31,875/year**
(range $20K–$124K) as the ceiling for a VC data subscription; scout carry runs 2.5–10% of the
carry pool. **Status: KNOWN** (published), but these price *referrals and data*, not this exact
product.

**Q17 — Is the revenue recurring?**
The two structurally-recurring shapes are `INVESTOR_SUBSCRIPTION` and `VENTURE_INTELLIGENCE`, both
marked `ALLOWED` in `opportunity_market.MONETIZATION`. Per-referral fees are transactional and
lumpier. Recurrence is a property of the *subscription* shapes, matching the PitchBook comparable.
**Status: KNOWN** (which shapes recur); whether they retain is **UNKNOWN**.

**Q18 — What can we LEGALLY monetize?**
Enumerated in `opportunity_market.MONETIZATION` and gated by
`opportunity_market.assert_monetization_allowed`. `ALLOWED`: `EVENT_SPONSORSHIP`,
`INVESTOR_SUBSCRIPTION`, `VENTURE_INTELLIGENCE` (and, on the talent side,
`TALENT_ACCESS_SUBSCRIPTION`). See [legal-policy.md](legal-policy.md) for the full treatment.

**Q19 — What must we NEVER sell?**
`INVESTMENT_SUCCESS_FEE` is `FORBIDDEN_UNTIL_COUNSEL`; `assert_monetization_allowed` **raises** on
it. The reason is cited, not invented: "taking a % of capital raised can be broker-dealer activity
(securities law)" — the Exchange Act **§15(a)** line in [venture-upside.md](../venture-upside.md):
"Transaction-based compensation paid by an investor for introductions is the classic trigger for
broker registration." Also never sold: any founder score (none exists) and any non-consented
individual data (`compliance.individual_disclosure_allowed`).

**Q20 — What is the honest posture on the whole thing?**
An introduction is not a deal (`mutual_intro.funnel_liquidity` note: "An introduction is not a
hire/deal"); a match is thesis-based discovery, not an investment recommendation
(`venture_matching.explain`: "This is thesis-based discovery, not an investment recommendation.");
a weekend prototype is not production (`venture_profile.VentureProfile.diligence_note`). **The
category (developer/venture intelligence) is proven; the specific check for THIS product is
UNKNOWN.**

---

## What this document does not claim

- It does not claim any investor has paid, or will pay. **WTP: UNKNOWN.**
- It does not claim continuation predicts success. That is a **Hypothesis**.
- It does not authorize equity, success fees, or any transaction-based compensation — the
  recommendation in [venture-upside.md](../venture-upside.md) is explicitly **against** taking
  equity, and the code enforces the success-fee ban.
