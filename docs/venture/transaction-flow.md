# Transaction Flow — The Venture Funnel and Mutual Introduction

How interest becomes an introduction, and why an introduction is deliberately **not** treated as a
deal. Described from `engine/mutual_intro.py` and the `investor_interest` / `venture_intro` /
`venture_outcome` tables in `schema/010_talent_venture.sql`. House discipline: **Evidence ≠ Claim ≠
Hypothesis ≠ Decision**; status **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**.

One-line invariants: **no contact release without mutual opt-in**, and **an introduction is not a
deal.**

---

## The VENTURE_FUNNEL (Part XXXIX)

`mutual_intro.VENTURE_FUNNEL` is the ordered set of stages:

```python
VENTURE_FUNNEL = ["THESIS", "DISCOVERY", "PACKET_VIEWED", "INVESTOR_INTEREST", "MUTUAL_OPT_IN",
                  "INTRODUCTION", "MEETING", "FOLLOW_ON"]
```

Read left to right, these map to the rest of the venture market:

| Stage | What happens | Where |
|---|---|---|
| THESIS | fund states stage/sector/geo/thesis | `fund_graph.Fund` |
| DISCOVERY | opt-in ventures matched to the thesis | `venture_matching.discover` |
| PACKET_VIEWED | investor reads an evidence packet | [investor-evidence-packets.md](investor-evidence-packets.md) |
| INVESTOR_INTEREST | fund expresses interest | `investor_interest` table (`team_response` PENDING) |
| MUTUAL_OPT_IN | team also opts in | `IntroRequest.both_opted_in` |
| INTRODUCTION | contact released | `mutual_intro.release_contact`; `venture_intro` table |
| MEETING | they meet | recorded only if the team shares |
| FOLLOW_ON | later-round outcome | `venture_outcome` table (`team_shared`) |

The funnel deliberately separates DISCOVERY (a match exists) from INVESTOR_INTEREST (a fund acted)
from MUTUAL_OPT_IN (the team accepted) from INTRODUCTION (contact released). Each is its own stage
precisely so none is silently equated with the next.

---

## Mutual introduction — the single choke point

`mutual_intro.IntroRequest` models a pending introduction and holds three booleans:

```python
counterparty_opted_in: bool = True    # the requester (fund) expressed interest
subject_opted_in: bool = False        # the team has NOT yet accepted
subject_visible: bool = False         # the team opted this scope visible at all
```

Contact can be released only when **all three** are true:

```python
@property
def both_opted_in(self):
    return self.counterparty_opted_in and self.subject_opted_in and self.subject_visible

def contact_releasable(self):
    """Contact details may be released ONLY on mutual opt-in. No exceptions, no scraping."""
    return self.both_opted_in
```

The team controls its side through `IntroRequest.accept()` (sets `subject_opted_in = True`) and
`IntroRequest.decline()` (sets it back to `False`). The scope itself is validated against
`compliance.VISIBILITY_SCOPES` in `__post_init__`.

The **only** function that returns a contact is `mutual_intro.release_contact`:

```python
def release_contact(req, contact):
    if not req.contact_releasable():
        raise PermissionError("Contact cannot be released without mutual opt-in (both sides + "
                              "subject made this scope visible).")
    return contact
```

This is the single choke point. There is no other path to a contact detail in the venture market.
Absent mutual opt-in it raises `PermissionError`. The schema mirrors the gate:
`venture_intro.both_opted_in boolean not null default false`, and `introduced_at` is null until the
introduction actually happens.

### No private contact dump

The fund graph holds only public links (`fund_graph.Investor.public_profile_url`,
`Fund.source_url`; see [fund-graph.md](fund-graph.md)), and the venture profile holds no investor
contact fields. There is nowhere to bulk-export contacts from, and the one release function gates on
mutual consent. This is the operational form of the Carta trust lesson in
[venture-upside.md](../venture-upside.md): the moment participants believe their data can be used
without consent, the honest behavior that is the whole product stops.

---

## Introduction ≠ deal (Part LXI)

`mutual_intro.funnel_liquidity` reports conversion across the funnel **without** equating an
introduction with a transaction:

```python
def funnel_liquidity(counts, kind="talent"):
    stages = TALENT_FUNNEL if kind == "talent" else VENTURE_FUNNEL
    report = {s: counts.get(s, 0) for s in stages}
    report["_note"] = ("An introduction is not a hire/deal. Downstream stages are only recorded "
                       "when the participant/team voluntarily shares the outcome.")
    return report
```

Called with `kind="venture"` it walks `VENTURE_FUNNEL` and attaches the honest caveat as `_note`.
Two things follow:

1. **An INTRODUCTION count is not a FOLLOW_ON count.** The funnel keeps them as separate stages and
   the note forbids collapsing them. Reporting "we made N introductions" says nothing about deals.
2. **Downstream stages are self-reported.** MEETING and FOLLOW_ON are recorded only when the team
   *chooses* to share — `venture_outcome.team_shared boolean default false`, and the outcome row
   exists only if `team_shared` is set. The platform does not assert deal outcomes it cannot see.

This is the same honesty STATE.md applies to the whole business: an introduction, like a job
posting that "measures activation," is a leading indicator, not proof of a transaction. Do not
oversell the funnel.

---

## The interest → outcome tables

- `investor_interest` — a fund expresses interest in a venture; `team_response` is PENDING /
  ACCEPTED / DECLINED. Interest alone releases nothing.
- `venture_intro` — created on mutual opt-in; `both_opted_in` and `introduced_at` gate the actual
  introduction.
- `venture_outcome` — an optional, team-shared record of what happened (`transaction` is a
  `opportunity_transaction` such as `VC_INTRO` / `ACCELERATOR_INTRO`; `team_shared` must be set).

No row in this chain takes a fee, computes a score, or moves money — those are out of scope for the
code and, for success fees, forbidden (see [legal-policy.md](legal-policy.md);
`opportunity_market.assert_monetization_allowed("INVESTMENT_SUCCESS_FEE")` raises).

---

## What the transaction flow is NOT

- **Not a contact marketplace.** Contact releases only through `release_contact`, only on mutual
  opt-in; otherwise `PermissionError`.
- **Not a deal tracker that infers outcomes.** Downstream stages are team-shared only
  (`funnel_liquidity` note; `venture_outcome.team_shared`).
- **Not a transaction with a take.** No success fee, no carry, no per-deal fee anywhere in the
  flow — the §15(a) broker-dealer line ([venture-upside.md](../venture-upside.md)).
- **Not automatic.** The team must `accept()`; interest never auto-converts to an introduction.

---

## Summary

The venture transaction flow is a staged funnel (`VENTURE_FUNNEL`) with one contact choke point
(`release_contact`, gated by `IntroRequest.both_opted_in`) and one honesty rule
(`funnel_liquidity`: an introduction is not a deal; downstream stages are team-shared only). It
releases no contact without mutual opt-in and asserts no outcome it cannot see — consistent with
the trust-first posture the venture-upside research recommends.
