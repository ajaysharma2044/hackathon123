# Startup Matching — Decomposed Thesis Fit, Discovery, and Explanation

How a venture is matched to a fund. Described from `engine/venture_matching.py` and the
`venture_match` / `venture_match_evidence` tables in `schema/010_talent_venture.sql`. House
discipline: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; status **KNOWN / LIKELY / UNKNOWN /
CONTRADICTED**.

The one-line invariant: **matches are thesis-based DISCOVERY, never investment recommendations, and
there is no founder score.**

---

## Decomposed thesis match, never a founder score (Part XXXIII)

`venture_matching.match(venture, fund)` returns a **dict of independent dimensions**, never a
single number. The dimensions (`venture_matching.MATCH_DIMS`):

```python
MATCH_DIMS = ["stage_fit", "sector_fit", "check_size_fit", "geography_fit", "thesis_fit",
              "technical_domain_fit", "continuation_evidence"]
```

The returned dict carries each dimension plus `why` (human-readable reasons) and `unknowns`, and
the code comment states the omission by design: "no founder_score / overall_score, by design." The
`venture_match` schema table matches this exactly — a column per dimension with `check (… between 0
and 3)` and the comment "explicitly NO founder_score / overall_score."

This is the same decomposition the talent side uses (`talent_match`: "kept DECOMPOSED — never a
single candidate score"). The refusal to sum is enforced by absence: there is no field to hold a
total, in code or in schema.

### How each dimension is scored (and why missing ≠ zero)

`match` uses a small equality helper, `venture_matching._eq_fit`:

```python
def _eq_fit(a, b):
    if not a or not b:
        return None            # unknown, not zero
    return 3 if str(a).lower() == str(b).lower() else 0
```

The critical line is `return None` for missing input — **unknown is distinct from a zero fit**
(`compliance.neutral_when_missing`). Per dimension:

- **stage_fit** — `_eq_fit(attr["STAGE"], fund.stage)` → 3 / 0 / None.
- **sector_fit** — 3 if the venture sector is in `fund.sectors`; `0` if a sector is given but
  doesn't match; `None` if no sector given.
- **geography_fit** — `_eq_fit(attr["GEOGRAPHY"], fund.geography)`.
- **technical_domain_fit** — 3 if the domain appears in the fund thesis; else `1` if a domain is
  given; `None` if none.
- **thesis_fit** — 2 if the technical domain is in the fund thesis; else `None`.
- **check_size_fit** — `None` if no `CAPITAL_NEED`; else a coarse `2` ("refine with real check
  sizes").
- **continuation_evidence** — `{"CONTINUED": 3, "STARTUP_FORMED": 3, "PIVOTED": 2, "STOPPED": 0,
  "UNKNOWN": None}`. STOPPED is 0 (no positive signal), UNKNOWN is None (neutral).

Every `None` becomes an entry in the `unknowns` list ("stage not provided", etc.), and the
explanation states these are "not held against the team." Missing evidence is never a penalty.

---

## Discovery covers winners AND non-winners (Part XXXVII)

`venture_matching.discover(fund, ventures)`:

```python
def discover(fund, ventures):
    """Investor discovery: all INVESTOR-opted ventures, matched — winners and non-winners alike."""
    return [match(v, fund) for v in ventures if v.investor_visible]
```

The filter is `v.investor_visible` — **the INVESTOR opt-in, and nothing else**. There is no filter
on prize, rank, judge score, or "winner" status. This is the winner-bias guard the whole system
insists on: STATE.md warns that the interesting outcomes may live in teams that did not win, and the
module docstring states discovery "covers ALL opt-in projects meeting the query, not only winners."

Two gates, and only two:
1. **Opt-in** — `investor_visible` must be `True` (Part XXXIX; `venture_visibility` table).
2. **Query fit** — the decomposed `match` dimensions describe fit; they do not exclude.

A non-winning team that opted in is fully discoverable. A winning team that did not opt in is not.
Opt-in dominates outcome.

---

## Explanation, not recommendation

`venture_matching.explain(m)` renders a match as prose that is careful about what it is:

```
Potentially relevant introduction: venture <id> <-> fund <id>
  • sector '<x>' in fund sectors
  • ...
  Unknown (not held against the team): stage not provided; ...
  This is thesis-based discovery, not an investment recommendation.
```

Two invariants are literally in the output strings:
- It opens with **"Potentially relevant introduction"** — not "invest," not "strong founder," not
  a rank.
- It closes with **"This is thesis-based discovery, not an investment recommendation."**

And when no reasons are found, it says so honestly: "(thesis overlap unclear from provided
evidence)" rather than inventing a rationale.

---

## Worked example — seed infra venture × seed infra fund

Given a venture and a fund (public data):

```python
from fund_graph import Fund
from venture_profile import VentureProfile
import venture_matching

fund = Fund(fund_id="f1", name="Example Seed Fund", stage="SEED",
            sectors=("Infrastructure", "DevTools"), geography="US",
            thesis="developer infrastructure and observability tooling",
            source_url="https://example.vc/thesis")   # public source required

v = VentureProfile(venture_id="v1", investor_visible=True,      # explicit INVESTOR opt-in
                   continuation_status="CONTINUED",             # still building at follow-up
                   attributes={"STAGE": "SEED", "SECTOR": "Infrastructure",
                               "TECHNICAL_DOMAIN": "developer infrastructure",
                               "GEOGRAPHY": "US", "CAPITAL_NEED": "yes"})

m = venture_matching.match(v, fund)
# m == {stage_fit: 3, sector_fit: 3, check_size_fit: 2, geography_fit: 3,
#       thesis_fit: 2, technical_domain_fit: 3, continuation_evidence: 3,
#       why: ["sector 'Infrastructure' in fund sectors",
#             "stage 'SEED' matches fund stage",
#             "technical domain 'developer infrastructure' matches fund thesis",
#             "still building at follow-up (CONTINUED)"],
#       unknowns: []}
#   — no founder_score, no overall_score

print(venture_matching.explain(m))
```

Renders:

```
Potentially relevant introduction: venture v1 <-> fund f1
  • sector 'Infrastructure' in fund sectors
  • stage 'SEED' matches fund stage
  • technical domain 'developer infrastructure' matches fund thesis
  • still building at follow-up (CONTINUED)
  This is thesis-based discovery, not an investment recommendation.
```

The output ends at **"potentially relevant introduction,"** decomposed and explained. It never
says "invest," never ranks the team, and never emits an overall number. If `GEOGRAPHY` had been
omitted, `geography_fit` would be `None` and the render would add "Unknown (not held against the
team): geography not provided" — a stated gap, not a deduction.

---

## Technical diligence layer (Part XXXV: prototype ≠ production)

`technical_domain_fit` and the observed artifacts (`VentureProfile.prototype_ref` / `demo_ref`)
give an investor a technical read that a deck cannot — but the read is bounded. Every packet built
on a match carries `VentureProfile.diligence_note`:

> "Artifacts are weekend-prototype evidence, not production readiness. Observed vs self-reported vs
> assumed vs unknown are tagged per claim; treat unknowns as unknown."

So the technical layer says "here is what was built and how it maps to the fund's thesis," tagged by
`VentureClaim.status` (OBSERVED vs SELF_REPORTED vs ASSUMED vs UNKNOWN), and explicitly **not**
"this is production-ready." A high `technical_domain_fit` is thesis alignment, not a maturity
grade.

---

## What matching is NOT

- **Not a founder score.** No `founder_score` / `overall_score` in code or schema; the module
  imports `compliance` and abides by `FORBIDDEN_SCORES` / `assert_not_a_person_score`.
- **Not winner-biased.** `discover` filters on opt-in only, not rank (Part XXXVII).
- **Not a recommendation.** `explain` says so in its last line, every time.
- **Not a penalty for missing data.** `_eq_fit` returns `None`, not `0`; unknowns are listed as
  "not held against the team."

**Status:** the mechanics above are **KNOWN** (in code). Whether the match predicts a good
investment is **UNKNOWN** and outside what the code claims — it surfaces thesis overlap, nothing
more.
