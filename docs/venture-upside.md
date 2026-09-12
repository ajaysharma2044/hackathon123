# Venture Upside

Whether to take equity in teams formed at the event. **Recommendation: no.** The research is
unusually clear, and there is a precedent that settles it.

## The finding: nobody has ever done this

**No hackathon or student-event organizer has ever successfully taken equity by virtue of
participation.** Not as a failed experiment — essentially nobody has tried.

| Company | Origin | Outcome | Organizer captured |
|---|---|---|---|
| **GroupMe** | TechCrunch Disrupt Hackathon, 2010 | Acquired by Skype 2011, reported ~$80M | **Zero.** No equity, no warrant, no ROFR |
| **Zapier** | Credited to Startup Weekend 2011 (contested) | Multi-billion | **Zero** |
| **buildspace** | 125,000 builders, $10M from a16z | Shut down 2024 | **Zero — took equity in nothing they made** |

buildspace is the cautionary case: the largest builder network ever assembled, enormous
top-of-funnel, captured none of it, then wound down.

## What equity actually costs to take

Every program taking 5–10% writes a real check and runs a real program:

| Program | Money | Equity | Duration |
|---|---:|---:|---|
| South Park Commons | $1,000,000 | 7% | ongoing |
| Y Combinator | $500,000 | 7% | 3 months |
| Techstars | $220,000 | 5% | 3 months |
| Antler | $100–250K | 6–12% | 3–6 months |
| Entrepreneur First | €90K–$250K | ~10% | 3–6 months |
| **43North** | **$1,000,000** | **5% via warrant** | + 12-month relocation |

> **Nobody takes meaningful equity for a three-day event. There is no market price for it
> because there is no market.**

Two corrections to common assumptions:

- **Z Fellows is not "$10K for 1%."** It's $10K on a SAFE at a **$1B valuation cap** —
  effectively ~0.001%, economically a grant.
- **Terms are moving founder-friendly, not the reverse.** YC takes no ROFR. SPC states
  explicitly: *"the SPC Fund has no right to invest in any company you start."* AI Grant and Neo
  use uncapped SAFEs. A new event entering with an equity term moves against the market at the
  moment it has the least leverage.

43North is the one real precedent — and note it wears **one hat only**. It doesn't sell research
about its portfolio and doesn't recruit out of it.

## The Carta precedent — the argument that settles this

In January 2024, Carta's Liquidity arm used confidential cap-table data to cold-contact
shareholders about selling shares without the issuing companies' knowledge. Linear's CEO went
public after Carta approached one of their angels — a family member whose investment was never
published.

CEO Henry Ward exited the business entirely, and his reasoning is the exact argument here:

> *"Because we have the data, if we are trading secondaries, people will always worry that we
> are using the data, even if we are not. So we have decided to prioritize trust, and exit the
> secondary trading business."*

The revenue he killed: **secondaries $3M**, against **cap table $250M** and **fund admin $100M**.
He killed the small conflicted line to protect the large trust-dependent one.

**Map it directly:**

```
Carta cap table ($250M, trust-dependent)  ←→  the measurement/research platform
Carta secondaries ($3M, conflicted)       ←→  event equity
```

If builders believe the behavioral instrumentation feeds an investment decision — or a sponsor
report about them personally — **the instrumentation stops producing honest behavior. And the
honest behavior is the entire product.**

The measurement platform and an equity stake are in direct tension, and the measurement platform
is worth far more.

## The four hats problem

Taking equity means wearing all of these at once:

1. **Equity holder** in teams
2. **Seller of research** about those same teams to sponsors
3. **Recruiter** placing those builders into sponsor jobs
4. **Fiduciary to LPs** if there's a fund

Named conflicts that follow:

- Instrumentation shows Team B struggling with Sponsor X's API while you hold equity in Team B's
  competitor. Any sponsor who thinks about this for thirty seconds discounts the report.
- You control admissions, mentors, stage time, and judging. Holding equity in outcomes makes
  every one of those decisions self-dealing-adjacent.
- **Students cannot be accredited investors** (net worth >$1M excluding residence, or income
  >$200K/yr). So your LPs would be the same sponsors you're selling research to — sponsor
  "research" becomes investor communication.
- [data-model.md](data-model.md) already commits to opt-in, aggregate-only, minimum cell size. An
  investment vehicle creates standing temptation to look at individual data for a non-consented
  purpose. Once it's *possible*, participants assume it's happening — Ward's point exactly.

## The participant-relations arithmetic

A blanket 1–2% term across 200 attendees means 200 signatures, 200 negotiations with parents,
lawyers, and university counsel — to reach maybe 3–5 companies that ever incorporate and perhaps
one that matters.

**You would be taxing exactly the people the model depends on attracting**, for an expected value
a single SPV could capture later at lower cost. The top decile has the most alternatives and the
most advisors telling them not to sign.

Additional friction: contracts with **minors are voidable** (elite student events include
under-18s), F-1/J-1 students face business-involvement restrictions, and a university-hosted,
university-funded event is precisely the fact pattern where university IP policy exceptions get
argued.

## What to do instead

### 1. Post-hoc SPVs — the cheapest credible path

| Platform | All-in cost |
|---|---|
| **Sydecar** | 2% of capital, floor $2,500, cap $12,500, + $2,000 regulatory → **~$4,500 minimum**. Takes no carry. |
| **AngelList** | $8,000 setup + $2,000 regulatory. Fees capped at 10% of raise. |

No fund to raise, no Exempt Reporting Adviser obligation, and **no equity term in the participant
agreement at all.** You earn the right to invest by being useful and you pay market price.

This captures nearly all the realistic upside — you were never going to win a competitive round
on the strength of having hosted the hackathon — at close to zero trust cost.

### 2. An optional, priced investment track

A **$25K–$50K prize structured as a standard post-money SAFE** the winning team may accept *or
decline*, with a cash-only alternative. That converts equity from a tax into a product.

### 3. Sell VCs referrals with memos — the one cleanly priced product

The best-fitting number in this research:

| | |
|---|---:|
| Republic — per referred startup | **$2,500** |
| Calm Company — referral without a memo | **$2,000** |
| Calm Company — **referral with an investment memo** | **$5,000** |

**A written memo roughly doubles the price — and a structured findings memo is precisely what
this model already manufactures.** You are building the exact artifact that commands the premium.

VC deal-flow context: scout carry runs 2.5–10% of the carry pool; PitchBook costs **$31,875/year
average** (range $20K–$124K), which is the ceiling for a VC data subscription.

**VCs pay small money for access and real money for allocation.** They believe they already have
access. $10–50K event sponsorship is real and fast — VC decision cycles beat corporate ones — but
don't sell contractual first-look.

## ⚠️ The broker-dealer line

**Transaction-based compensation paid by an investor for introductions is the classic trigger for
broker registration under Exchange Act §15(a).** Carry on a deal you sourced is also compensation
tied to the transaction.

The SEC **proposed** a conditional finders exemption in October 2020. **It was never adopted.
There is no federal finder exemption today.**

```
SAFE:     flat sponsorship fees, flat annual subscriptions, flat referral retainers
NOT SAFE: per-deal success fees paid by an investor
```

If you want deal-level upside, take it **from the company** (warrant or SAFE) or **as an
investor** (your own SPV) — never as a fee from the VC. This is precisely why "scout fund"
vehicles exist: the payout becomes an investment return rather than a transaction fee.

## The rule

**The event and research company takes no equity in participants.** If venture upside is wanted
later, it lives in a separate vehicle with a separate decision-maker and three firewalls:

1. No non-public event data reaches the investment vehicle
2. The vehicle has no role in selection or judging
3. Both facts disclosed in writing to participants and sponsors up front

South Park Commons is the template to copy: **expectation and access, not entitlement.**

## Sources

[YC deal](https://www.ycombinator.com/deal) ·
[Techstars terms](https://www.techstars.com/investment-terms) ·
[South Park Commons FAQ](https://www.southparkcommons.com/faq/) ·
[43North FAQ](https://43north.org/faq/) ·
[Carta exits secondaries](https://techcrunch.com/2024/01/08/after-taking-credibility-hit-carta-announces-it-is-exiting-the-secondaries-business-we-have-decided-to-prioritize-trust/) ·
[GroupMe / Disrupt](https://techcrunch.com/2012/05/11/from-disrupt-ny-to-a-43-million-skype-acquisition-groupme-tells-all/) ·
[MLH Terms](https://www.mlh.com/terms) ·
[Sydecar pricing](https://www.sydecar.io/pricing) ·
[AngelList SPV pricing](https://www.angellist.com/pricing/spvs) ·
[SEC accredited investor](https://www.sec.gov/resources-small-businesses/capital-raising-building-blocks/accredited-investor) ·
[SEC proposed finders exemption (never adopted)](https://www.sec.gov/newsroom/press-releases/2020-248) ·
[Teten on scout compensation](https://teten.com/vc-scout-job-compensation-career-economics/) ·
[PitchBook pricing](https://www.vendr.com/buyer-guides/pitchbook) ·
[Neo terms](https://techcrunch.com/2026/02/19/ali-partovis-neo-looks-to-upend-the-accelerator-model-with-low-dilution-terms/)
