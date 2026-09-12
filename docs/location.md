# Location Decision

**Status: open.** Miami was explored first and produced useful research, but the city is not
settled. This document is the framework for deciding, and what the research so far implies.

## What does not depend on location

Most of the work already done is city-independent. Worth stating so it doesn't get re-litigated:

- Everything in [research-pricing.md](research-pricing.md) — the LF rate-card template, the
  $27K student-access trap, panel-replacement and qualified-lead floors
- Everything in [measurement.md](measurement.md) — brokered API keys, the one-primary-experiment
  constraint, operational definitions
- Everything in [economics.md](economics.md) — the attention/access/answers/outcomes ladder
- The competitive picture in [research-findings.md](research-findings.md) and
  [asset-monetization.md](asset-monetization.md)
- **The room-block mechanics** in [logistics-revenue.md](logistics-revenue.md) — IATA TIDS,
  commissions, comp-room ratios, rebates, attrition clauses, meal and keycard sponsorship. These
  are industry-standard everywhere. Only the GMCVB incentive and the Florida hurricane program
  are Miami-specific.

What *is* location-dependent: travel cost, housing cost, venue cost, which DMO incentive applies,
sponsor proximity, and weather risk.

## The central tension

```
CHEAPEST LOCATIONS                    BEST-FOR-SPONSORS LOCATIONS
university town, summer dorms         SF Bay Area, NYC, Seattle
$18K housing, free venue              $65K+ housing, expensive venue
no sponsor can drop by                sponsors walk in with 8 engineers
```

**The cheapest places are the worst for sponsors, and the best for sponsors are the most
expensive.** Any location decision is a position on that tradeoff.

For a business whose second-year revenue depends on sponsors having *seen* the thing work,
sponsor proximity is worth more than it looks on a spreadsheet. A sponsor who sends a VP and
eight engineers as mentors is a sponsor who renews. A sponsor who received a PDF is not.

## The six criteria, weighted

| Criterion | Why it matters | Weight |
|---|---|---|
| **Travel cost** | 200 flights is the largest single line. Bus-reachable schools cost ~$40 instead of ~$400. | High |
| **Sponsor proximity** | Drives renewal, mentor quality, and whether the research buyer sees the instrument work. | **High** |
| **Housing cost** | Seasonality and dorm availability swing this 3x+ ($18K vs $65K). | High |
| **Venue (in-kind possible?)** | Worth $30–45K and is the first credibility signal. | Medium |
| **DMO / CVB incentive** | Every city has one; second-tier cities compete harder for room nights. | Low–Medium |
| **Risk** | Weather, hurricane season, contract exposure. | Medium |

## Candidate comparison

Directional. Every cell needs a real quote before it's a decision.

| | Travel | Sponsors | Housing | Venue | Risk |
|---|---|---|---|---|---|
| **NYC** | ~60% of target schools bus/train-reachable | Very high | Expensive year-round | Sponsor offices plausible | Low |
| **Boston / Cambridge** | Northeast bus-reachable; MIT/Harvard local | High | Summer dorms available | University space plausible | Low |
| **SF Bay Area** | Stanford/Berkeley local; Northeast flies | **Highest** | Most expensive | Sponsor offices very plausible | Low |
| **Miami** | Everyone flies; poor hub for target schools | Low | **Cheapest in summer (~$200/nt)** | Paid; no in-kind found | Hurricane (mitigated) |
| **University town, summer** | Everyone flies | Lowest | **Cheapest overall** | Often free | Low |

### The Miami research, kept for the record

Genuinely useful findings if Miami stays in contention:

- **August ~$200/night vs February ~$455** — a ~$150K swing on 600 room nights
- **GMCVB pays $3–5 per occupied room night**, but only June–September and **only if the RFP goes
  through GMCVB before any hotel** — book direct and it's forfeited
- **VISIT FLORIDA "Cover Your Event"** — free named-hurricane cancellation coverage, $100–200K
  sublimits
- **Miami-Dade TDC grants explicitly exclude conferences** — that path is closed
- **The LAB Miami** ~$18K for three days vs Miami Beach Convention Center at **$119,400**
- eMerge Americas is March 2–4 2027 — better used as a sales trip than as an event date

The honest weakness: **Miami is a poor hub for this particular population.** Nearly every target
school flies, nobody buses, and sponsor office density is low compared to NYC or the Bay. The
cheap hotels are real, but they're offsetting a travel bill that a Northeast location largely
avoids.

## The resolution worth testing first

The tension above has a specific answer that gets most of both sides:

> **A university campus in or adjacent to a major sponsor city, in summer.**

Summer dorm housing at university rates, university or sponsor venue in-kind, and sponsors close
enough to show up in person. Candidates: Columbia or NYU (NYC), MIT or Harvard (Boston),
Stanford or Berkeley (Bay Area).

This is worth pricing before anything else, because if it works it removes the tradeoff instead
of splitting it. The open questions are whether a university will host an external organizer's
event, at what rate, and what the summer dorm terms actually are — none of which is published
anywhere, so it means phone calls.

One caution: a university host that is also a *source* of participants creates a selection
problem — a Cornell-run event at Cornell will over-recruit Cornell. Worth deciding deliberately
rather than by default.

## What to do next on this

1. Pick 3 candidate cities and get **real quotes** — venue, group ADR, catering per person
2. Price 200 flights from the actual target-school list for each candidate (this is a spreadsheet
   exercise, and it likely decides the question on its own)
3. Call each candidate's CVB and ask what incentive exists for ~600 summer room nights
4. Ask 2–3 target sponsors directly: *does location change whether you'd send people?* Their
   answer is worth more than any of the above
5. Call university conference-services offices about summer dorm + venue packages for an external
   organizer

Item 4 is the one most likely to be skipped and the one most likely to decide correctly.

---

# Calendar: Three Constraints That Conflict

This generalizes to any city, and it's sharper than the earlier August recommendation.

```
GRANT MONEY wants        June – September     (CVB/DMO incentives target the summer need period)
HURRICANES forbid        August – October     (96% of major hurricane days, if coastal/southern)
STUDENTS are unavailable mid-June – late Aug   (elite CS students are at internships)
```

**These cannot all be satisfied.** My earlier "mid-to-late August" recommendation assumed
internships had ended — they run to late August, so the window is narrower than I said, and in a
hurricane-exposed city August is also the riskiest month.

The internship conflict is the one to weight most heavily. **A summer date that collides with
internships is fatal for recruiting MIT/Stanford/Berkeley/CMU students** — the entire premise of
the panel. Grant money that costs you the cohort is not worth taking.

**Revised ranking of windows:**

1. **Late October / early November** — hurricane climatology drops sharply after mid-October,
   hotel rates are shoulder/low, students are in session, and it lands before December holiday
   pricing. Forfeits summer grant windows, which the analysis above says is the right trade.
2. **Late February / early March** — negligible weather risk, and in Miami specifically it sits
   adjacent to eMerge Americas. Peak hotel season is the cost.
3. **Late August, immediately before semester** — still workable if internships have ended, but
   tight, and bad in any hurricane-exposed city.
4. ~~July–early September~~ — **rule out.** Maximum grant eligibility, minimum hotel cost, and it
   collides with internships. The money doesn't compensate.

# Findings That Apply Anywhere

## Tourism grants require public access — design for it

Miami-Dade TDC and Miami Beach VCA both require funded events be **open and accessible to the
public**. A closed, invitation-only elite hackathon fails that test, and this requirement is
standard across destination-marketing grant programs, not a Miami quirk.

**The fix is cheap: bolt on a marketed, publicly-accessible demo day or expo.** It satisfies the
grant requirement, and it's independently good — it's the sponsor-facing showcase and the press
moment. Design it in from the start rather than retrofitting it to qualify.

## Venue technical minimums (MLH, for 200 hackers)

| | |
|---|---|
| **Power** | **2.5 outlets per hacker = 500 outlets** |
| **Wifi** | **4 devices per hacker = 800 concurrent devices** |
| Also | Secure equipment storage, security, liability insurance, accessible entry |

These are routinely underbudgeted and are a common cause of a miserable event.

## Attendees cannot sleep at the venue

Per MLH's guidance it is **against fire code** to let attendees sleep at a hackathon venue.
Events run "work overnight, no official sleeping." This means hotel rooms or a separate
designated rest space **regardless of venue choice** — so the room block is not optional, which
in turn keeps the [logistics-revenue.md](logistics-revenue.md) opportunities live in any city.

It also disqualifies venues with fixed operating hours. The LAB Miami, for instance, is 8 AM–9 PM
only.

## ⚠️ Food costs much less than budgeted

MLH's published benchmarks: **food $8–10 per person per meal**, snacks $10/person, t-shirts $5–8,
charter buses $3,500 each.

For 200 hackers across ~7 meals that is roughly **$13,000–$16,000** — against the $30–48K in
[funding.md](funding.md). That estimate was built from conference catering rates, which are
several times hackathon rates. **Corrected below.**

## VCs give judges, not cash

MLH's own sponsor page names **zero VC firms** — only corporates. VCs show up at hackathons as
judges, mentors, and keynote speakers, not as cash line items.

**Ask VCs for judges and a named prize. Ask AI/cloud vendors and quant firms for money.**

## Quant firms are an underrated target

Citadel and Citadel Securities run the **Data Open** datathon and **Terminal** (algorithmic
tower-defense), both explicitly elite-university student competitions, with Correlation One. Jane
Street, Two Sigma, Hudson River Trading and Jump run comparable programs.

**This is campus-recruiting budget spent on exactly this population, by firms that already
believe in the format.** A far easier ask than philanthropy, and they compete directly with big
tech for the same students — which makes access valuable rather than nice-to-have.

# Miami — Detailed Findings

Kept in full, because the city remains a live candidate and the research is specific.

**The strongest argument for Miami: the flagship vacancy.** `miamihackweek.com` now self-describes
as *"Miami Hack Week — The Archives | 2021–2024"* — past tense. ShellHacks at FIU is the only
large event left. **There is no flagship Miami builder hackathon right now.**

**The strongest argument against: the ecosystem has visibly contracted.** CIC Miami is closed and
delisted. Venture Café Miami returns HTTP 410 Gone. Tech Equity Miami's domain lapsed and now
resolves to an offshore gambling site. Techstars has no Florida programs in 2026. a16z closed its
Miami Beach office in May 2023 — though it leased CityPlace Tower in West Palm Beach in September
2026 for the $1.18B American Dynamism fund, opening early 2027.

**Miami companies don't write big hackathon checks.** ShellHacks has **1,400+ hackers, 40+
sponsors, and only $20,000 in total prizes** — and its sponsor list is dominated by *national*
tech (AWS, Google, Microsoft, Nvidia, Netflix, Waymo, Ford, Chevron), not Miami employers. Budget
on national sponsors; treat Miami companies as upside.

**Knight Foundation has exited tech and entrepreneurship** — current program areas are Journalism,
Arts, Information & Society, and Community Impact. Legacy relationship money persists (they
sponsor ShellHacks and are an eMerge founding partner), but don't build a budget on them.

### Corrections to earlier assumptions

| | |
|---|---|
| Blockchain.com | **Not Miami.** HQ London, US HQ Dallas |
| Assurant | HQ Atlanta, but a top-billed ShellHacks sponsor with South Florida operations |
| Kaseya | Miami HQ, but layoffs through early 2026 including ~150 Miami staff; missed its 3,400-job commitment |
| Magic Leap | Valuation fell $6.4B → $450M; original device end-of-lifed Dec 2024. Not viable |
| Nearpod | Acquired by Renaissance Learning 2021. A subsidiary product, not a sponsor |
| Venture Miami | **No longer exists** — absorbed into the City of Miami's Dept. of Economic Innovation and Development. Director Keith Carswell |

### Grant reality

| Source | Realistic | Key terms |
|---|---:|---|
| Miami-Dade TDC | up to **$35,000** | 1:1 match, reimbursement basis, ~6 months to payment, **excludes conferences**, requires public access |
| Miami Beach VCA | up to **$35,000** | Max ¼ of project budget, **4:1 funding ratio**, cash prizes NOT reimbursable, event must be in Miami Beach, org incorporated ≥1 year |
| GMCVB | ~$1,500 cash + housing support | $3–5/room night, Jun 1–Sep 30 travel only, RFP must go to GMCVB first |
| City of Miami EID | ~$50K discretionary | $800K deployed across 15+ events. No published RFP |

### Venues with published rates

| Venue | Capacity | Price | Overnight |
|---|---|---|---|
| **FIU Graham Center** | 900 theater / 500 banquet | **All bays $2,400 + tax** | External rentals weekends only — but ShellHacks runs 1,400 hackers overnight here as a student org. **Co-host, don't rent** |
| **UM Shalala** | 800 theater / 432 banquet | Combined **$5,000**; full complex $7,000 | Policy not published; rate card dated 2022 |
| The LAB Miami | max 254 | $750/hr, 3-hr min | **8 AM–9 PM only** — disqualified |
| Mana Wynwood | 6,000 | $20,000–$40,000 | Massively oversized |

### Best Miami targets

**Citadel / Citadel Securities** — Miami HQ (830 Brickell and Southeast Financial Center),
already a **"Global Sponsor" of eMerge Americas**, and already runs elite-student competitions.
The single best corporate target in the city.

**Blackstone** — Miami tech hub, ~250 employees, already a ShellHacks sponsor, and the Blackstone
Charitable Foundation funds MDC's LaunchPad. Two independent doors.

**FIU is the strongest operational partner** — the Knight Foundation School of Computing runs
ShellHacks, Florida's largest hackathon. Co-hosting imports the only proven 1,000+-person
hackathon operation in the state *and* unlocks the overnight-capable venue at internal rates.

**eMerge Americas 2027 is March 2–4** (full week Feb 27–Mar 5), 20,000+ attendees, **1,000+
investors**. They run their own 500-developer hackathon on Feb 27 — **partner, don't compete.**
Contact: Dan Cole, Senior Director of Partner Relations.

**⚠️ Note:** this research recommended Hack Club HCB fiscal sponsorship at 7%. **HCB is teen-only
(13–18) and college students are not eligible** — see [procurement.md](procurement.md). The Miami
Foundation offers fiscal sponsorship as an alternative (EIN 65-0350357).

### 2027 date conflicts

eMerge Americas **Mar 2–4** (+ their hackathon Feb 27) · Ultra Music Festival **Mar 26–28**
(swallows downtown) · Art Basel **~Dec 3–5** (most expensive week of the year) · F1 Miami GP early
May · ShellHacks late September.
