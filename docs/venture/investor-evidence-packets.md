# Investor Evidence Packets (Part XXXIV)

What an investor actually receives about an opt-in venture, and how its contents are separated by
epistemic status so nothing is oversold. Described from `engine/venture_profile.py`,
`engine/venture_matching.py`, and the `venture_claim` / `startup_attribute` / `venture_match` /
`venture_match_evidence` tables in `schema/010_talent_venture.sql`. House discipline: **Evidence ≠
Claim ≠ Hypothesis ≠ Decision**; status **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**.

---

## What a packet is

A packet is the assembled, INVESTOR-scope view of one venture: the opt-in profile, its
status-tagged claims, its structural attributes, the decomposed thesis match to the investor's
fund, the supporting evidence behind that match, and the mandatory diligence note. It is built only
for ventures where `VentureProfile.investor_visible` is `True` (and `venture_visibility` records the
`INVESTOR` scope). It is the "memo-grade" artifact the referral comparable prices at a premium
([venture-upside.md](../venture-upside.md): a memo roughly doubles a referral's price).

Crucially, a packet is **not** a score and **not** a recommendation. It carries no founder rating
(none exists — `compliance.FORBIDDEN_SCORES`), and the match it contains ends at "potentially
relevant introduction" (`venture_matching.explain`).

---

## Packet contents

| Section | Source (code / schema) | Nature |
|---|---|---|
| Problem & build | `VentureProfile.problem`, `.prototype_ref`, `.demo_ref`; `venture_profile` table | team-supplied + observed artifacts |
| Structural attributes | `VentureProfile.attributes` (STAGE/SECTOR/TECHNICAL_DOMAIN/CAPITAL_NEED/GEOGRAPHY); `startup_attribute` table | each row status-tagged (`claim_status`, default SELF_REPORTED) |
| Material claims | `VentureProfile.claims` (`VentureClaim`); `venture_claim` table | each carries OBSERVED/SELF_REPORTED/ASSUMED/UNKNOWN + optional `evidence_id` |
| Continuation | `VentureProfile.continuation_status`; `CONTINUATION` evidence type | CONTINUED/STOPPED/PIVOTED/STARTUP_FORMED/UNKNOWN |
| Thesis match | `venture_matching.match` → `venture_match` table | decomposed dims, no overall score |
| Match evidence | `venture_match_evidence.why` → `work_evidence` | the concrete artifact behind each reason |
| Diligence note | `VentureProfile.diligence_note` | mandatory limitation string |
| Known-unknowns | `match()["unknowns"]`; UNKNOWN-status claims | stated gaps, "not held against the team" |

---

## Observed / Self-reported / Assumed / Unknown, clearly separated

The packet's defining property is that **every material claim is separated by how we know it**.
This is enforced, not stylistic:

- `venture_profile.CLAIM_STATUS = ("OBSERVED", "SELF_REPORTED", "ASSUMED", "UNKNOWN")` and
  `VentureClaim.__post_init__` raises on anything else — a claim cannot exist without a status.
- `VentureProfile.material_claims_ok` asserts every claim carries a status before the packet is
  considered well-formed.
- The `venture_claim` table has `status claim_status not null default 'UNKNOWN'`; `startup_attribute`
  has `status claim_status default 'SELF_REPORTED'`.

A well-formed packet therefore reads as four separated buckets, never a blended narrative:

```
OBSERVED       (artifact we saw / public repo)
  • "demo runs end-to-end"                     evidence_id → work_evidence(ARTIFACT_OBSERVED)
  • "repo is public and builds"                evidence_id → work_evidence(PUBLIC_REPO)

SELF-REPORTED  (team said it; no independent artifact)
  • "in conversations with 3 design partners"  (no evidence_id)
  • SECTOR = Infrastructure                     startup_attribute (SELF_REPORTED)

ASSUMED        (working inference — challenge it)
  • "targets mid-market" (derived from the problem statement, not stated)

UNKNOWN        (not established — neutral, not negative)
  • revenue: UNKNOWN
  • CAPITAL_NEED: not provided
```

The mapping to the shared vocabulary: OBSERVED corresponds to evidence with `source_kind` in
`compliance.EVIDENCE_SOURCE_KINDS` = ARTIFACT_OBSERVED / PUBLIC_REPO / LONGITUDINAL_OBSERVED;
SELF_REPORTED to SELF_REPORTED / TEAM_CONFIRMED. The packet keeps source and status **separate and
un-collapsed** — exactly as the schema comment insists: evidence source is "stored separately; NOT
auto-ranked into a score."

---

## The known-unknowns section

A packet must state what it does not know. This is generated automatically, not left to the
reader's inference:

- **Match unknowns:** `venture_matching.match` accumulates an `unknowns` list (e.g. "stage not
  provided", "sector not provided", "geography not provided") for every dimension that scored
  `None`. `venture_matching.explain` renders them under "Unknown (not held against the team)."
- **UNKNOWN-status claims:** any `VentureClaim` with `status == "UNKNOWN"` (the default) is a
  standing known-unknown.
- **Neutral, never negative:** `compliance.neutral_when_missing` returns `"UNKNOWN"` for empty
  input; `_eq_fit` returns `None` (not `0`) for missing data. A gap is displayed as a gap, never
  converted into a low score.

This is the internal-validity honesty STATE.md keeps at full strength, applied per venture:
directional evidence with explicit limits, not a certification.

---

## The mandatory diligence note (Part XXXV)

Every packet carries `VentureProfile.diligence_note` verbatim:

> "Artifacts are weekend-prototype evidence, not production readiness. Observed vs self-reported vs
> assumed vs unknown are tagged per claim; treat unknowns as unknown."

The note is not optional and not editable per venture — it is a method return, so it travels with
the profile wherever the packet goes. It encodes two invariants at once: **prototype ≠ production**,
and **status tags are load-bearing — treat unknowns as unknown.**

---

## What a packet is NOT

- **Not a founder score / ranking.** No such field exists (`compliance.FORBIDDEN_SCORES`,
  `assert_not_a_person_score`).
- **Not an investment recommendation.** The embedded match ends at "potentially relevant
  introduction" and states "not an investment recommendation" (`venture_matching.explain`).
- **Not contact information.** A packet exposes the opt-in profile and evidence, never contact
  details — those release only on mutual opt-in through `mutual_intro.release_contact` (see
  [transaction-flow.md](transaction-flow.md)).
- **Not a dossier of non-consented data.** Individual exposure requires the INVESTOR opt-in
  (`compliance.individual_disclosure_allowed`); aggregate stays aggregate (the Carta lesson,
  [venture-upside.md](../venture-upside.md)).

---

## Where the packet sits in the funnel

A packet is the artifact viewed at the `PACKET_VIEWED` stage of `mutual_intro.VENTURE_FUNNEL`
(`THESIS → DISCOVERY → PACKET_VIEWED → INVESTOR_INTEREST → MUTUAL_OPT_IN → INTRODUCTION → MEETING →
FOLLOW_ON`). It is built after DISCOVERY (`venture_matching.discover` returned this venture for the
fund) and it is what an investor reads *before* expressing interest. Critically, viewing a packet
releases **no contact detail** — that happens only later, at INTRODUCTION, through
`mutual_intro.release_contact` on mutual opt-in (see [transaction-flow.md](transaction-flow.md)).
So a packet is safe to surface to an opted-in-venture's matched funds: it exposes the evidence graph,
never a way to reach the team without their acceptance.

The packet also inherits the funnel's honesty rule: it supports a *potentially relevant
introduction*, not a deal. Its embedded match ends with "not an investment recommendation," and any
downstream outcome (MEETING, FOLLOW_ON) is recorded only if the team shares it
(`venture_outcome.team_shared`).

## Summary

An investor evidence packet is a status-separated evidence bundle (OBSERVED / SELF-REPORTED /
ASSUMED / UNKNOWN, each enforced by `CLAIM_STATUS` and `material_claims_ok`), plus a decomposed
thesis match with its supporting `work_evidence`, plus an auto-generated known-unknowns section,
plus the mandatory `diligence_note`. It is the memo-grade artifact the venture-upside comparables
price at a premium — and it is explicitly not a score, not a recommendation, and not a contact
dump.
