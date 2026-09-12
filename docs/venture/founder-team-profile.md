# Founder / Team Venture Profile

The opt-in team profile that makes a venture discoverable to investors. Described from code
(`engine/venture_profile.py`, `venture_profile` / `venture_claim` / `startup_attribute` in
`schema/010_talent_venture.sql`). House discipline: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**;
status **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**; **WTP UNKNOWN**.

---

## What it is (Parts XXXI, XXXIV)

`venture_profile.VentureProfile` is the level-C, INVESTOR-scope artifact a team may *choose* to
expose. It is not created by inference and it is not on by default. The defining fields
(`venture_profile.VentureProfile`):

| Field | Meaning | Default |
|---|---|---|
| `venture_id` | identity | required |
| `team_id`, `project_id` | soft refs to shared records | `""` |
| `problem`, `prototype_ref`, `demo_ref` | what they built | `""` |
| `attributes` | STAGE / SECTOR / TECHNICAL_DOMAIN / CAPITAL_NEED / GEOGRAPHY → value | `{}` |
| `claims` | list of `VentureClaim`, each status-tagged | `[]` |
| `investor_visible` | the explicit INVESTOR opt-in | **`False`** |
| `continuation_status` | CONTINUED / STOPPED / PIVOTED / STARTUP_FORMED / UNKNOWN | `"UNKNOWN"` |
| `is_company` | not every project is a company | **`False`** |

Two defaults carry the whole ethic. `investor_visible=False` means **no discoverability without
an explicit opt-in** — `venture_matching.discover` filters on exactly this flag, and the
`venture_visibility` table records the per-scope switch with `granted_at` / `revoked_at` so it is
revocable. `is_company=False` means the profile never forces startup framing (Part XXX): a
weekend project is allowed to remain a weekend project.

The schema profile (`venture_profile` table) carries a few more optional columns —
`market_hypothesis`, `capital_seeking` ("only if voluntarily provided"), `desired_investor_type`,
`fundraising_status` — none required, all team-supplied. There is **no** founder-name-scoring
column, no pedigree field, no quality rating anywhere in the table.

---

## Claim-status tagging (Part XXXIV)

Every **material** claim carries an epistemic status. This is the single most important property
of the profile and it is enforced in two places.

In code, `venture_profile.CLAIM_STATUS = ("OBSERVED", "SELF_REPORTED", "ASSUMED", "UNKNOWN")` and
`venture_profile.VentureClaim.__post_init__` raises `ValueError` on any status outside that set —
you cannot construct a claim without a valid status. `VentureProfile.material_claims_ok` asserts
that *every* claim carries one:

```python
def material_claims_ok(self) -> bool:
    """Every material claim must carry a status (never a bare assertion)."""
    return all(c.status in CLAIM_STATUS for c in self.claims)
```

In the schema, the `venture_claim` table has `status claim_status not null default 'UNKNOWN'`, the
`claim_status` enum is exactly `('OBSERVED', 'SELF_REPORTED', 'ASSUMED', 'UNKNOWN')`, and each
claim can point at supporting evidence via `evidence_id references work_evidence`. The
`startup_attribute` table likewise carries a `status claim_status default 'SELF_REPORTED'` per
attribute.

### What the four statuses mean, in practice

- **OBSERVED** — backed by an artifact the system saw (`work_evidence.source_kind` in
  `ARTIFACT_OBSERVED` / `PUBLIC_REPO`). Example: "the repo compiles and the demo runs."
- **SELF_REPORTED** — the team said it; no independent artifact. Example: "we have three design
  partners." Default for `startup_attribute`.
- **ASSUMED** — a working inference the reader should challenge. Example: "targets the enterprise
  segment" derived from the pitch, not stated.
- **UNKNOWN** — not established. The default (`VentureClaim.status = "UNKNOWN"`;
  `venture_claim.status default 'UNKNOWN'`). Missing is neutral, never negative
  (`compliance.neutral_when_missing`).

The invariant that separates this from a normal sourcing profile: a bare assertion cannot enter
the material record. If it is material, it is tagged. **Status: KNOWN** (enforced in code + schema).

---

## The mandatory diligence limitation note (Part XXXV)

`venture_profile.VentureProfile.diligence_note` returns a fixed, non-optional limitation string
that must travel with the profile:

> "Artifacts are weekend-prototype evidence, not production readiness. Observed vs self-reported
> vs assumed vs unknown are tagged per claim; treat unknowns as unknown."

This encodes the invariant **a weekend prototype is NOT production readiness**. The profile is
evidence of a build under weekend constraints, not a product-maturity certification. Any packet
that surfaces this profile carries the note (see [investor-evidence-packets.md](investor-evidence-packets.md)).

**Why it is mandatory, not advisory:** the internal-validity caveats STATE.md keeps at full
strength — "n≈200, Hawthorne, prize-contaminated free choice… directional leading-indicator
behavioral signal on an early-adopter cohort, not representative market research" — apply at the
individual venture level too. Overselling a weekend prototype as production readiness loses the
sophisticated investor in one meeting, exactly as overselling generalizability loses the
sophisticated research buyer.

---

## What the profile is NOT

- **Not a founder score.** There is no hireability, founder-quality, personality, or intelligence
  field. `compliance.FORBIDDEN_SCORES` names `founder_quality` / `founder_score` explicitly, and
  `compliance.assert_not_a_person_score` raises on any name matching `founder_q`, `personality`,
  `intelligence`, etc. The product is the status-tagged evidence graph, never a rating.
- **Not a protected-attribute record.** `compliance.assert_no_sensitive` (over
  `compliance.SENSITIVE_ATTRIBUTES`) rejects any field name that is or contains a protected trait;
  the schema notes "NO fields for protected/sensitive attributes."
- **Not on by default.** `investor_visible=False`; discovery filters it out until the team opts in.
- **Not auto-collected.** Ownership is confirmed, never inferred (`project_role` table:
  `confirmed_by_participant`); the same posture applies to the venture record.

---

## Continuation as a profile field, not a verdict

`continuation_status` is a stored fact about whether the team kept building, not a judgment. Its
allowed values (`CONTINUED | STOPPED | PIVOTED | STARTUP_FORMED | UNKNOWN`) include `STOPPED`
without penalty and `UNKNOWN` as the neutral default. The matching layer maps `STOPPED → 0` and
`UNKNOWN → None` (`venture_matching.match`) — a stopped team simply lacks a positive continuation
signal; it is not marked down. Whether continuation is predictive is a **Hypothesis (UNKNOWN)**;
the profile only records it.

---

## Worked example

```python
from venture_profile import VentureProfile, VentureClaim

v = VentureProfile(
    venture_id="v1",
    team_id="t1", project_id="p1",
    problem="ETL observability for small data teams",
    prototype_ref="repo://v1", demo_ref="video://v1",
    attributes={"STAGE": "PRE_SEED", "SECTOR": "DevTools",
                "TECHNICAL_DOMAIN": "data infrastructure"},   # status held in startup_attribute
    claims=[
        VentureClaim("demo runs end-to-end", status="OBSERVED", evidence_ref="work_evidence://a1"),
        VentureClaim("in talks with 3 design partners", status="SELF_REPORTED"),
        VentureClaim("targets mid-market", status="ASSUMED"),
        VentureClaim("current revenue", status="UNKNOWN"),
    ],
    investor_visible=True,          # explicit INVESTOR opt-in — without this, discover() skips it
    continuation_status="CONTINUED",
    is_company=False,               # still just a project; not forced into startup framing
)

assert v.material_claims_ok()       # True — every claim carries a status
print(v.diligence_note())           # the mandatory limitation note travels with the profile
```

Constructing a `VentureClaim` with an invalid status (e.g. `status="STRONG"`) raises `ValueError`
in `__post_init__` — a bare or invented status cannot enter the record. Setting `investor_visible`
to its default `False` would make this venture invisible to `venture_matching.discover` no matter
how strong its claims are: opt-in dominates.

## Summary

The founder/team profile is an opt-in, status-tagged, non-scored evidence record. Its two
load-bearing defaults (`investor_visible=False`, `is_company=False`), its per-claim status
enforcement (`material_claims_ok`, the `claim_status` enum), and its mandatory diligence note
(`diligence_note`) together make it a discovery artifact that cannot quietly become a founder
rating or a production-readiness claim.
