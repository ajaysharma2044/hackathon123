# Investor Product Catalog (Part LIII)

The set of investor-facing products the venture market can offer. Each is grounded in the code
that would deliver it and the legal constraints that bound it. **Every legal claim cites
[venture-upside.md](../venture-upside.md).** House discipline: **Evidence ≠ Claim ≠ Hypothesis ≠
Decision**; status **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**; and per the catalog header in
[question-catalog.md](../question-catalog.md), **every WTP below is a rational ceiling, never an
observed price — WTP stays UNKNOWN until a signed number arrives.**

The buyer/user column uses the fund roles modeled in `fund_graph.INVESTOR_ROLES`
(GP/PARTNER/PRINCIPAL/ASSOCIATE/PLATFORM/SCOUT) so Part LV — who inside the fund owns this — stays
explicit.

The monetization legality for each product is enforced in code by
`opportunity_market.assert_monetization_allowed` over `opportunity_market.MONETIZATION`. Two
shapes are `FORBIDDEN`/`NEEDS_LEGAL` and constrain the whole catalog:

- `INVESTMENT_SUCCESS_FEE` → `FORBIDDEN_UNTIL_COUNSEL` (raises). No product may take a % of capital
  raised or any per-deal fee from an investor — the **§15(a) broker-dealer** line in
  [venture-upside.md](../venture-upside.md).
- `INVESTOR_SUBSCRIPTION`, `VENTURE_INTELLIGENCE`, `EVENT_SPONSORSHIP` → `ALLOWED` (flat, not
  transaction-based).

---

## 1. Investor Event Partner

- **Buyer/user (Part LV):** GP / PARTNER (sponsorship budget); PLATFORM executes.
- **Alternative:** sponsoring an existing elite event — STATE.md flags Cerebral Valley already
  runs the premium invite-only version; "the event is table stakes."
- **Deliverable:** branded presence / access at the event; aggregate (not individual) read on the
  builder cohort.
- **Participant benefit:** funds the event; no participant data exposed without opt-in.
- **Comparable (KNOWN):** "$10–50K event sponsorship is real and fast — VC decision cycles beat
  corporate ones" ([venture-upside.md](../venture-upside.md)).
- **Legal constraints:** `EVENT_SPONSORSHIP` is `ALLOWED` in `opportunity_market.MONETIZATION`
  ("standard event sponsorship"). But **do not sell contractual first-look** — venture-upside.md:
  "$10–50K event sponsorship is real and fast… but don't sell contractual first-look." Flat fee
  only, never tied to any deal.
- **WTP:** **UNKNOWN** (comparable ceiling $10–50K).

## 2. Opt-In Startup Discovery

- **Buyer/user:** ASSOCIATE / SCOUT / PLATFORM (sourcing functions).
- **Alternative:** PitchBook/Harmonic/Crunchbase sourcing DBs; a pitch competition.
- **Deliverable:** search over INVESTOR-opted ventures via `venture_matching.discover`, decomposed
  thesis match (`venture_matching.match`), each result explained (`venture_matching.explain`).
- **Participant benefit:** only teams that opted into `INVESTOR` scope appear
  (`VentureProfile.investor_visible`, gated in `discover`); nothing auto-shared.
- **Comparable (KNOWN):** referral pricing — Republic **$2,500**/referred startup; Calm Company
  **$2,000** referral, **$5,000** with a memo ([venture-upside.md](../venture-upside.md)).
- **Legal constraints:** delivered as flat access, not per-deal. A **referral retainer or flat
  subscription is SAFE** (venture-upside.md: "flat sponsorship fees, flat annual subscriptions,
  flat referral retainers"); a **per-deal success fee is NOT** (`INVESTMENT_SUCCESS_FEE` raises).
  A match is "thesis-based discovery, not an investment recommendation" (`explain`).
- **WTP:** **UNKNOWN** (referral comparables $2K–5K).

## 3. Cornell Startup Intelligence

- **Buyer/user:** PLATFORM / PARTNER at campus-focused or university-affiliated funds; scouts.
- **Alternative:** manually monitoring campus demo days, club rosters, BigRed//Hacks.
- **Deliverable:** aggregate intelligence on the Cornell builder population and its venture
  formation, structured from public/opt-in signals; supply mapped in
  [cornell-audience-map.md](../cornell-audience-map.md) (2,000+ Bowers CIS majors; hundreds already
  on project teams).
- **Participant benefit:** aggregate, not a dossier; individual exposure still requires opt-in
  (`compliance.individual_disclosure_allowed`).
- **Comparable (KNOWN):** VC data subscription ceiling — PitchBook **$31,875/yr avg** (range
  $20K–$124K) ([venture-upside.md](../venture-upside.md)).
- **Legal constraints:** `VENTURE_INTELLIGENCE` is `ALLOWED` ("aggregate venture-trend
  intelligence"). Must stay aggregate; no non-consented individual data — the Carta lesson in
  venture-upside.md.
- **WTP:** **UNKNOWN.** *Which* investors want Cornell sourcing (Part LXXVI Q14) is itself
  UNKNOWN — no demand-side evidence.

## 4. Technical Founder Demo

- **Buyer/user:** PRINCIPAL / PARTNER (technical diligence); ASSOCIATE screens.
- **Alternative:** a pitch deck + a founder call; a take-home.
- **Deliverable:** the observed artifact + demo (`venture_profile.prototype_ref` / `demo_ref`) with
  the decomposed technical-domain fit (`venture_matching` `technical_domain_fit`) and the mandatory
  diligence note (`VentureProfile.diligence_note`).
- **Participant benefit:** shows what was actually built, not just claimed; status-tagged so nothing
  is oversold.
- **Comparable (KNOWN):** a memo roughly doubles referral price ($2K→$5K, venture-upside.md) — the
  observed-artifact packet is that memo-grade artifact.
- **Legal constraints:** it is a **deliverable**, not a transaction — sell the artifact, never a
  cut of any resulting deal (`INVESTMENT_SUCCESS_FEE` forbidden). Prototype ≠ production
  (`diligence_note`).
- **WTP:** **UNKNOWN.**

## 5. Follow-On Cohort

- **Buyer/user:** PARTNER / PLATFORM (portfolio and re-up decisions).
- **Alternative:** manually re-checking which teams from last cycle are still alive.
- **Deliverable:** the set of ventures with `continuation_status` in {CONTINUED, PIVOTED,
  STARTUP_FORMED} at follow-up (`venture_profile.continuation_status`; scored in
  `venture_matching.match` via `continuation_evidence`).
- **Participant benefit:** still opt-in; stopping is neutral, never penalized (STOPPED→0, UNKNOWN→
  None in `match`).
- **Comparable:** no clean public comparable; nearest is longitudinal data subscriptions
  (PitchBook ceiling).
- **Legal constraints:** `VENTURE_INTELLIGENCE`/`INVESTOR_SUBSCRIPTION` ALLOWED as flat products;
  no success fee.
- **WTP:** **UNKNOWN.** That continuation is *useful* to investors (Part LXXVI Q12) is a
  **Hypothesis**.

## 6. Longitudinal Discovery

- **Buyer/user:** PLATFORM / PARTNER; subscription owners.
- **Alternative:** re-buying a point-in-time sourcing snapshot each cycle.
- **Deliverable:** recurring visibility into opt-in ventures over 30/90-day horizons — the
  compounding signal built on `continuation_status` and `work_evidence` (`LONGITUDINAL_OBSERVED`
  source kind in `compliance.EVIDENCE_SOURCE_KINDS`).
- **Participant benefit:** opt-in and revocable (`venture_visibility.revoked_at`).
- **Comparable (KNOWN):** PitchBook $31,875/yr avg — recurring data subscription.
- **Legal constraints:** `INVESTOR_SUBSCRIPTION` ALLOWED ("subscription to opt-in discovery /
  intelligence"). Flat/recurring, not per-deal.
- **WTP:** **UNKNOWN.** STATE.md: longitudinal retention is "the untested engine of the compounding
  moat" — the supply-side risk (retaining builders into tracking) is real.

## 7. Sector Pipeline

- **Buyer/user:** PARTNER with a sector thesis; ASSOCIATE/SCOUT sourcing to it.
- **Alternative:** thesis-based cold sourcing across generic DBs.
- **Deliverable:** opt-in ventures filtered to a fund's sector/stage/geography
  (`fund_graph.funds_in_sector`, `funds_at_stage`, `Fund.geography`) then thesis-matched
  (`venture_matching.match`).
- **Participant benefit:** opt-in; decomposed match with unknowns surfaced, "not held against the
  team" (`match` / `explain`).
- **Comparable (KNOWN):** referral + data-subscription comparables above.
- **Legal constraints:** flat subscription/retainer only; a match is discovery, not a
  recommendation (`explain`); no success fee.
- **WTP:** **UNKNOWN.**

---

## The catalog-wide legal boundary

| Monetization shape | Status in `opportunity_market.MONETIZATION` | Basis (venture-upside.md) |
|---|---|---|
| `EVENT_SPONSORSHIP` | ALLOWED | flat sponsorship; don't sell first-look |
| `INVESTOR_SUBSCRIPTION` | ALLOWED | flat annual subscription is SAFE |
| `VENTURE_INTELLIGENCE` | ALLOWED | aggregate intelligence; keep it aggregate (Carta) |
| `INVESTMENT_SUCCESS_FEE` | **FORBIDDEN_UNTIL_COUNSEL** (raises) | §15(a) broker-dealer trigger |

`opportunity_market.assert_monetization_allowed("INVESTMENT_SUCCESS_FEE")` raises a
`PermissionError`. No product in this catalog may be priced as a percentage of capital raised, a
per-deal fee, or carry paid by an investor. If deal-level upside is ever wanted, it must come *from
the company* (SAFE/warrant) or *as an investor* (a separate SPV vehicle) — never as a fee from the
VC ([venture-upside.md](../venture-upside.md), "The broker-dealer line"). See
[legal-policy.md](legal-policy.md).

**Every WTP in this catalog is UNKNOWN.** The comparables are published prices for *adjacent*
products (referrals, data subscriptions, sponsorships), not observed prices for these. Per STATE.md
the entire model still rests on one untested assumption: someone will pay.
