# Fund Graph — Investors and Funds from Public Data Only

The structural graph of funds and investors the venture market matches against. Described from
`engine/fund_graph.py` and the `fund` / `investor` tables in `schema/010_talent_venture.sql`.
House discipline: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; status **KNOWN / LIKELY / UNKNOWN
/ CONTRADICTED**.

---

## Public data only (Parts XXXII, LVIII)

The module docstring is explicit (`engine/fund_graph.py`): "Structural fund + investor records
built from public fund websites, announcements, portfolios, and public professional profiles. **No
private or scraped contact data.**" The `Fund.source_url` field is described in-code as "public
source, required for any real fund row," and `Investor.public_profile_url` holds only a public
profile link. There is no email, phone, or private-contact column on either record — contact only
ever flows through the mutual-intro choke point (`mutual_intro.release_contact`; see
[transaction-flow.md](transaction-flow.md)).

This is the same principle the Carta precedent teaches in [venture-upside.md](../venture-upside.md):
using data people did not consent to expose destroys the trust the whole platform depends on. The
fund graph is built from what funds publish about themselves, nothing more.

---

## `Fund` (`fund_graph.Fund`, `fund` table)

```python
@dataclass
class Fund:
    fund_id: str
    name: str
    stage: str = "SEED"
    check_size: str = ""
    sectors: tuple = ()
    geography: str = ""
    thesis: str = ""
    source_url: str = ""   # public source, required for any real fund row
```

`__post_init__` validates `stage` against `fund_graph.STAGES = ("PRE_SEED", "SEED", "SERIES_A",
"SERIES_B", "GROWTH")` and raises `ValueError` on anything else. The `fund` table mirrors the
fields (`name`, `stage`, `check_size`, `sectors text[]`, `geography`, `thesis`, `source_url` —
"public fund data only").

The fund is described along the dimensions an investor actually filters on:

- **stage** — where in the lifecycle they invest (`STAGES`)
- **sector** — `sectors` tuple / `text[]`
- **check size** — `check_size` free text (coarse today; the match layer notes "refine with real
  check sizes")
- **geography** — `geography`
- **thesis** — `thesis` free text, used for technical-domain matching in
  `venture_matching.match` (`tech.lower() in fund.thesis.lower()`)

---

## `Investor` (`fund_graph.Investor`, `investor` table)

```python
@dataclass
class Investor:
    investor_id: str
    fund_id: str
    name: str = ""
    role: str = "ASSOCIATE"
    public_profile_url: str = ""
```

`__post_init__` validates `role` against `fund_graph.INVESTOR_ROLES` and raises otherwise. The
`investor` table stores `fund_id` (FK to `fund`), `name`, `role`, and `public_profile_url`.

### `INVESTOR_ROLES` and who owns the workflow (Part LV)

```python
INVESTOR_ROLES = ("GP", "PARTNER", "PRINCIPAL", "ASSOCIATE", "PLATFORM", "SCOUT")
```

These roles exist as first-class vocabulary precisely so the "who inside the fund is the buyer"
question stays explicit rather than assumed (Part LV: associate vs partner vs platform):

- **GP / PARTNER** — own the *check* and the thesis. The economic decision-maker.
- **PRINCIPAL** — often owns deal execution and later-stage sourcing.
- **ASSOCIATE / SCOUT** — typically own *sourcing and deal-flow* — the top of the funnel where a
  discovery product plugs in.
- **PLATFORM** — owns portfolio/community services and, at many funds, sourcing tooling and
  subscriptions.

**Claim (KNOWN, from code):** the role vocabulary is modeled. **Hypothesis (UNKNOWN):** which
role actually pays for opt-in discovery. STATE.md is blunt that no buyer has been spoken to yet —
this is resolved in interviews, not asserted here. The likely first buyers of a subscription/
intelligence product are platform and associate/scout functions; the partner owns the eventual
check. That ordering is a hypothesis to test.

---

## Query helpers

Two structural filters exist today (`engine/fund_graph.py`):

```python
def funds_in_sector(funds, sector):  return [f for f in funds if sector in f.sectors]
def funds_at_stage(funds, stage):    return [f for f in funds if f.stage == stage]
```

They are deliberately simple set filters over public attributes — no ranking of funds, no scoring
of investors, no opaque "best fund for you" verdict. Geography is filterable directly via
`Fund.geography`; check-size and thesis matching happen in the match layer
(`venture_matching.match`), not here.

---

## Worked example

```python
from fund_graph import Fund, Investor, funds_in_sector, funds_at_stage

funds = [
    Fund(fund_id="f1", name="Seed Infra Fund", stage="SEED",
         sectors=("Infrastructure", "DevTools"), geography="US",
         thesis="developer infrastructure and observability",
         source_url="https://f1.vc/thesis"),          # public source required for a real row
    Fund(fund_id="f2", name="Growth Health Fund", stage="GROWTH",
         sectors=("HealthTech",), geography="EU", source_url="https://f2.vc"),
]

investors = [
    Investor(investor_id="i1", fund_id="f1", name="A. Scout", role="SCOUT",
             public_profile_url="https://linkedin.com/in/ascout"),   # public profile only
    Investor(investor_id="i2", fund_id="f1", name="P. Partner", role="PARTNER"),
]

funds_in_sector(funds, "DevTools")   # -> [f1]
funds_at_stage(funds, "SEED")        # -> [f1]
```

Constructing `Fund(..., stage="ANGEL")` raises `ValueError` (not in `STAGES`); `Investor(...,
role="ADVISOR")` raises (not in `INVESTOR_ROLES`). The helpers filter over public attributes and
return plain lists — no ranking, no fund score, no investor score.

## What the fund graph is NOT

- **Not a scraped contact database.** No private contact fields exist; `source_url` /
  `public_profile_url` are the only link fields, both public.
- **Not a ranking of investors.** No investor score, no fund score. The helpers filter; they do
  not rank.
- **Not a demand signal.** The graph maps which funds *exist* at a stage/sector/geography. Whether
  any of them *wants* Cornell/campus sourcing (Part LXXVI Q14) is **UNKNOWN** — the fund record
  holds no "wants-campus-sourcing" attribute, and [cornell-audience-map.md](../cornell-audience-map.md)
  maps only the supply side.

---

## Summary

The fund graph is a public-data-only structural map: `Fund` (stage/sector/check/geo/thesis, with a
required public `source_url`) and `Investor` (role from `INVESTOR_ROLES`, public profile link),
filtered by `funds_in_sector` / `funds_at_stage`. It names investor roles explicitly so the
buyer-ownership question (Part LV) is answered by evidence, not assumption, and it holds no private
contact data — consistent with the trust argument in [venture-upside.md](../venture-upside.md).
