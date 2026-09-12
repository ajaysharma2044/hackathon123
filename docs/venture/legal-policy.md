# Legal Policy — The Critical One

This is the constraint every other venture document defers to. It states, with cited evidence, what
the venture market **must never do** and enumerates the **safer monetization hypotheses to
validate**. Every legal point is cited to [venture-upside.md](../venture-upside.md); the code
enforcement is cited to `file:symbol`. House discipline: **Evidence ≠ Claim ≠ Hypothesis ≠
Decision**; status **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**.

Nothing here is a legal opinion. It is a policy that encodes the repo's own cited research and
routes every uncertain structure to securities counsel before any money changes hands.

---

## The rule, stated first

**The event and research company takes no equity in participants, and takes no transaction-based
compensation from investors.** This is the exact recommendation of
[venture-upside.md](../venture-upside.md) ("The rule": "The event and research company takes no
equity in participants") and it is enforced in code.

---

## 1. The broker-dealer line — §15(a) (CONTRADICTED for success fees)

[venture-upside.md](../venture-upside.md), "The broker-dealer line," states it directly:

> "Transaction-based compensation paid by an investor for introductions is the classic trigger for
> broker registration under Exchange Act §15(a)."

Two consequences from that document, both cited:

- **Carry on a deal you sourced is also transaction-tied compensation.** "Carry on a deal you
  sourced is also compensation tied to the transaction."
- **There is no federal finder exemption today.** "The SEC proposed a conditional finders
  exemption in October 2020. It was never adopted. There is no federal finder exemption today."

The bright line from the same document:

```
SAFE:     flat sponsorship fees, flat annual subscriptions, flat referral retainers
NOT SAFE: per-deal success fees paid by an investor
```

And the escape hatch, if deal-level upside is ever wanted: "take it from the company (warrant or
SAFE) or as an investor (your own SPV) — never as a fee from the VC."

**Status: the legality of taking a % of capital raised / a per-deal fee from an investor is
CONTRADICTED** by cited law — it is the classic §15(a) broker-dealer trigger. Do not do it.

### Code enforcement

`opportunity_market.MONETIZATION` marks it forbidden:

```python
"INVESTMENT_SUCCESS_FEE": ("FORBIDDEN_UNTIL_COUNSEL",
    "taking a % of capital raised can be broker-dealer activity (securities law); "
    "do NOT until counsel confirms"),
```

and `opportunity_market.assert_monetization_allowed` **raises** on it:

```python
def assert_monetization_allowed(kind):
    status, note = MONETIZATION[kind]
    if status == "FORBIDDEN_UNTIL_COUNSEL":
        raise PermissionError(f"{kind}: {note}")
    return status
```

So `assert_monetization_allowed("INVESTMENT_SUCCESS_FEE")` raises a `PermissionError`. The ban is
not advisory; it is a guard any monetization path must pass and cannot.

---

## 2. No equity in participants (CONTRADICTED as a good idea)

[venture-upside.md](../venture-upside.md) is unusually direct: "**Recommendation: no.**" The cited
evidence:

- **Nobody has ever done it.** "No hackathon or student-event organizer has ever successfully taken
  equity by virtue of participation." GroupMe (acquired ~$80M), Zapier (multi-billion), and
  buildspace (125,000 builders, then wound down) each returned **zero** to the organizer.
- **There is no market price.** "Nobody takes meaningful equity for a three-day event. There is no
  market price for it because there is no market."
- **Terms are moving founder-friendly.** YC takes no ROFR; South Park Commons: "the SPC Fund has no
  right to invest in any company you start."
- **The participant-relations arithmetic is negative.** A blanket term across ~200 attendees means
  "200 signatures, 200 negotiations… to reach maybe 3–5 companies that ever incorporate" — "taxing
  exactly the people the model depends on attracting."
- **Structural blockers.** Students generally cannot be accredited investors; contracts with minors
  are voidable; F-1/J-1 students face business-involvement restrictions; university IP policy is
  precisely in play for a university-hosted event.

The code carries no equity mechanism at all — there is no equity, cap-table, or ownership field in
`venture_profile` or any venture table. The absence is the enforcement.

---

## 3. The Carta precedent — why the measurement platform and an equity stake are in tension

[venture-upside.md](../venture-upside.md), "The Carta precedent," is the argument the document says
"settles this." In January 2024 Carta's Liquidity arm used confidential cap-table data to
cold-contact shareholders; CEO Henry Ward exited the secondaries business, in his words:

> "Because we have the data, if we are trading secondaries, people will always worry that we are
> using the data, even if we are not. So we have decided to prioritize trust, and exit the secondary
> trading business."

The cited magnitudes: he killed **secondaries ($3M)** to protect **cap table ($250M)** and **fund
admin ($100M)** — "the small conflicted line to protect the large trust-dependent one." The
document maps it directly onto this business:

```
Carta cap table ($250M, trust-dependent)  ←→  the measurement/research platform
Carta secondaries ($3M, conflicted)       ←→  event equity
```

"If builders believe the behavioral instrumentation feeds an investment decision… the
instrumentation stops producing honest behavior. And the honest behavior is the entire product."

This is why the venture market is built as an **opt-in downstream consumer** with hard data-level
separation (`compliance.DATA_LEVELS`: A event-operations never individually disclosed, B aggregate
research, C opt-in professional) and individual disclosure gated by
`compliance.individual_disclosure_allowed`. The instrumentation must never be believed to feed an
investment decision.

---

## 4. The four-hats conflict

[venture-upside.md](../venture-upside.md), "The four hats problem": taking equity means being at
once (1) an equity holder in teams, (2) a seller of research about those same teams, (3) a recruiter
placing those builders, and (4) a fiduciary to LPs. The document's named conflicts include:
instrumentation showing a team struggling with a sponsor's API while you hold equity in a
competitor; controlling admissions/mentors/judging while holding equity in outcomes
("self-dealing-adjacent"); and — because students cannot be accredited investors — LPs who would be
"the same sponsors you're selling research to," so "sponsor research becomes investor
communication."

The policy response, from the same document: if venture upside is ever pursued, it "lives in a
separate vehicle with a separate decision-maker and three firewalls" — (1) no non-public event data
reaches the vehicle, (2) the vehicle has no role in selection or judging, (3) both facts disclosed
in writing up front. "South Park Commons is the template: expectation and access, not entitlement."

---

## 5. No autonomous investment decisions

The code makes no investment decisions and represents none. `venture_matching.explain` ends every
match with "This is thesis-based discovery, not an investment recommendation," and the match dict
carries no `overall_score` / `founder_score` to act on. There is no auto-invest path, no ranking a
capital-allocation could key off, and no fee that would reward one. A match is a *potentially
relevant introduction* (`venture_matching.explain` opening line), full stop. See
[startup-matching.md](startup-matching.md).

---

## 6. No founder scoring

`compliance.FORBIDDEN_SCORES` includes `founder_quality`, `founder_score`, plus personality,
intelligence, and general person-quality scores. `compliance.assert_not_a_person_score` raises on
any name matching `founder_q`, `personality`, `intelligence`, `person_quality`, etc. No venture
table has a founder-score column (`venture_match` comment: "explicitly NO founder_score /
overall_score"). Selling a founder rating is impossible by construction, not merely discouraged.

---

## Safer monetization hypotheses to VALIDATE

These are the shapes marked `ALLOWED` in `opportunity_market.MONETIZATION` — the flat, non-
transaction-based structures the §15(a) line permits. They are **Hypotheses to validate**, not
proven revenue. **WTP for every one is UNKNOWN** (STATE.md: the whole model still rests on one
untested assumption — someone will pay).

| Hypothesis | Code status | Cited comparable / basis (venture-upside.md) |
|---|---|---|
| **Event sponsorship** | `EVENT_SPONSORSHIP` = ALLOWED | "$10–50K event sponsorship is real and fast"; but "don't sell contractual first-look" |
| **Investor subscription** | `INVESTOR_SUBSCRIPTION` = ALLOWED | flat annual subscription is SAFE; PitchBook $31,875/yr avg (range $20K–$124K) is the data-subscription ceiling |
| **Venture intelligence** | `VENTURE_INTELLIGENCE` = ALLOWED | aggregate venture-trend intelligence; keep aggregate (the Carta lesson) |
| **Program partnership / referrals** | flat referral retainer is SAFE | Republic $2,500/referral; Calm Company $2,000, or $5,000 with a memo — "a memo roughly doubles the price" |
| **Post-hoc SPV** (separate vehicle) | not a platform fee | Sydecar ~$4,500 min, no carry; AngelList $8K + $2K, fees capped 10% of raise — "the cheapest credible path," "no equity term in the participant agreement at all" |

Each of these is flat/aggregate/subscription — none is a per-deal fee paid by an investor, so none
trips the §15(a) trigger. The SPV, if ever used, is a *separate vehicle* that earns the right to
invest and pays market price — "you earn the right to invest by being useful and you pay market
price" ([venture-upside.md](../venture-upside.md)).

**These are validated by a signed check, not by this document.** STATE.md's discipline applies:
pitch named buyers, try to close a small paid pilot; no commitment in ~4 weeks weakens the thesis.

---

## What to NEVER sell (the hard list)

1. **Investment success fees / a % of capital raised / carry paid by the VC** —
   `INVESTMENT_SUCCESS_FEE` raises; §15(a) broker-dealer trigger ([venture-upside.md](../venture-upside.md)).
2. **Equity taken by virtue of participation** — recommended against, no market price, negative
   participant-relations arithmetic (venture-upside.md).
3. **Any founder/person score** — `compliance.FORBIDDEN_SCORES` / `assert_not_a_person_score`.
4. **Contractual first-look / guaranteed allocation to sponsors** — "don't sell contractual
   first-look" (venture-upside.md).
5. **Non-consented individual data** — `compliance.individual_disclosure_allowed` gates every
   individual disclosure; aggregate must stay aggregate (the Carta lesson).
6. **Private/scraped contact data** — the fund graph is public-data-only (`fund_graph` docstring);
   contact releases only on mutual opt-in (`mutual_intro.release_contact`).

---

## Decision status

**DECISION: none committed.** This policy forbids the unsafe structures and lists the safe ones to
test; it commits to no product, price, or vehicle. Per STATE.md and
[venture-upside.md](../venture-upside.md), the category may be real but the specific check is
**UNKNOWN**, and any deal-level upside — if ever pursued — belongs in a separate vehicle with a
separate decision-maker and the three firewalls, cleared by securities counsel first.
