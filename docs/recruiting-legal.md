# Recruiting: Structure and Legal Constraints

The recruiting product is real money — but its design is dictated by four bodies of law, and one
of them contradicts part of the original concept. Read this before building the work-evidence
product described in [products.md](products.md).

## The finding that changes the product: FCRA

If you compile information about students and sell it to employers for hiring decisions, **you
may become a consumer reporting agency.**

**15 U.S.C. §1681a(f)** — a CRA is anyone who *"for monetary fees, dues, or on a cooperative
nonprofit basis, regularly engages... in the practice of assembling or evaluating... information
on consumers for the purpose of furnishing consumer reports to third parties."*

**§1681a(d)** — a consumer report includes any communication bearing on *"character, general
reputation, personal characteristics, or mode of living"* used for employment purposes.

### The safe harbor, and it is narrow

**§1681a(d)(2)(A)(i):** a report containing information *"solely as to transactions or experiences
between the consumer and the person making the report"* is **not** a consumer report.

```
✅ OUTSIDE FCRA    What you directly observed at your own event
                   — what they built, what they used, what shipped, how the team worked

❌ INSIDE FCRA     GitHub history · past projects · references · peer reviews
                   prior events · Club OS longitudinal history · any third-party data
```

**This directly constrains two things already in the concept:**

1. **[concept.md](concept.md) §7 proposes Club OS as the before/during/after longitudinal layer.**
   Feeding pre-event campus history into a recruiting product crosses the line — it is no longer
   solely your own transactions and experiences. Longitudinal data is fine for *aggregate
   research*; it is not fine inside a candidate-level artifact sold to an employer.
2. **[measurement.md](measurement.md) proposes capturing structured application evidence** — past
   projects, work samples, current stack. Fine as research covariates. **Not** fine as recruiting
   material handed to a sponsor.

Crossing into CRA status triggers permissible-purpose rules, employer certification, consumer
disclosure and authorization, §1681e(b) accuracy procedures, §1681i dispute and reinvestigation
duties, §1681g file disclosure, and pre-adverse/adverse action notices.

**Precedent: FTC v. Spokeo — $800,000 civil penalty** (C.D. Cal., June 2012) for marketing
consumer profiles to employers and recruiters without FCRA compliance.

**The fix is clean:** the recruiting artifact contains only first-hand observation of your own
event. Everything else stays in the aggregate research product.

## Never emit a score

This keeps you out of three separate regimes at once.

**NYC Local Law 144** covers an automated employment decision tool producing a **"simplified
output"** — score, tag, classification, ranking — that substantially assists or replaces
discretionary hiring. The three-prong test (6 RCNY §5-300) catches you if the output is relied on
solely, **weighted more than any other criterion**, or used to overrule other factors. Applies to
employers *and employment agencies*. Requires annual independent bias audit, public posting, and
10 business days' notice to candidates.

**EU AI Act Annex III(4)** classifies recruitment and candidate evaluation as high-risk,
effective **August 2, 2026**, and it is **extraterritorial** — it applies where the output is used
in the EU regardless of where you sit. Article 6(3) offers a safe harbor for narrow procedural or
preparatory tasks, but **profiling of natural persons is always high-risk**. The Commission's
draft guidelines are explicit:

> *"Even where a human recruiter or manager remains formally responsible for the final decision,
> an AI system may still be high-risk if the AI system's output heavily influences which
> candidates advance."*

**"Human in the loop" is not a reliable escape hatch** under either regime.

**UGESP 29 CFR 1607.16** defines a "selection procedure" as *"any measure, combination of
measures, or procedure used as a basis for any employment decision"* — broad enough to capture a
ranked list, a shortlist, a badge, or a tier. The four-fifths rule (29 CFR 1607.4(D)) then
applies: a selection rate below 80% of the highest group's rate is evidence of adverse impact.

> **Publish artifacts and human-written narrative. Never a score, ranking, tier, or
> classification.** That single rule keeps you outside LL144's "simplified output," outside EU
> AI Act "evaluation of candidates," and outside UGESP's "selection procedure."

Also relevant: **Illinois HB 3773** took effect January 1, 2026 (bars AI with discriminatory
effect in employment, bars ZIP code as a proxy, requires notice). The **Colorado AI Act** was
delayed to June 30, 2026. The **Illinois AI Video Interview Act** (820 ILCS 42) requires notice,
explanation, and consent before AI analysis of video interviews.

⚠️ The EEOC's May 2023 AI technical assistance document **has been removed from eeoc.gov** and no
AI guidance appears in their guidance index. The underlying statute and UGESP regulation are
unchanged and remain enforceable, including by private plaintiffs.

## Title VII applies whether you charge or not

**42 U.S.C. §2000e(c)** defines an employment agency as anyone *"regularly undertaking **with or
without compensation** to procure employees for an employer."*

**A free event that regularly connects students to employers can be a Title VII employment
agency.** Charging a fee does not create this exposure — it already exists. Assume the status and
keep selection records accordingly.

No case law was found applying Title VII employment-agency status to a student event or online
talent platform. Legally untested, which cuts both ways.

## The per-hire fee: legal, but commercially dead

**Standard contingency rates**

| Segment | Fee |
|---|---|
| **Entry-level** | **10–15%** of first-year salary |
| Mid-level SWE | 20–25% |
| Senior / hard-to-fill | 25–30% |
| **Flat fee per hire** | **$5,000–$20,000** |
| Replacement guarantee | 60–90 days standard |

Entry-level prices *below* mid-level precisely because supply is abundant — the core economic
problem with this model for a student event.

**Every marketplace that pioneered per-hire pricing for engineers is gone or converted:**

| | Historical model | Status |
|---|---|---|
| Hired | 15% of first-year salary, 90-day guarantee | converted |
| Vettery | 15%, or $995/mo + $9,500/hire | converted |
| Triplebyte | ~25% (never officially published) | **triplebyte.com now fails TLS validation** |

**The student market never used per-hire fees at all.** The clearest signal: **Parker Dewey**, the
leading college micro-internship marketplace, charges **no conversion fee whatsoever** when an
employer hires a student full-time. Their model is subscription — $5,000 pilot, $7,500–$15,000/yr.

Handshake, RippleMatch, Symplicity, 12twenty, Untapped, Forage, and CodePath are all subscription
or per-post. Only **Wellfound Autopilot** ($500/month per role + 10% placement fee) survives as a
published hybrid.

**No elite student community charges a per-hire fee.** Checked directly across seven
organizations — Z Fellows, Contrary, On Deck/ODF, CodePath, MLH, Kleiner Perkins Fellows, and
Interact. Every one monetizes through fund economics (carry), nonprofit/philanthropic funding, or
contact-sales sponsorship. **The absence of any published placement-fee model across all seven is
itself the finding.**

## What the market actually pays — real contract data

| Platform | Median / avg annual contract | Range |
|---|---:|---|
| **Karat** | **$175,695** | — |
| **RippleMatch** | **$68,622** avg | $40,000–$132,600 |
| Handshake TES | ~$29,835 | $10,000–$250,000+ |
| CodeSignal | $24,394 | $8,000–$66,742 |
| Untapped | $24,150 | $18,200–$34,451 |
| HackerRank | $13,099 | $4,508–$45,861 |

**RippleMatch at $68,622 average is the single most relevant comp** — a student recruiting
platform, selling access, at exactly the price point the research tier targets. It is evidence
that companies pay mid-five-figures annually for structured access to early-career technical
talent.

Published pricing: Handshake Pro **$450/mo**; Symplicity **$55/post/school**, Pro from $329/mo;
Wellfound Starter **$135/seat/mo**.

## Who pays is the legal trigger

Most state employment-agency statutes are consumer-protection laws aimed at agencies charging
**jobseekers**.

- **California** Civ. Code §1812.501 — an employment agency acts for a fee *"to be paid...**by a
  jobseeker**"*
- **Massachusetts** G.L. c.140 §46A — expressly excludes *"a firm none of whose fees or charges
  are paid either directly or indirectly by any applicant for employment"*
- **New York** GBL §171 — recognizes an *"employer fee paid employment agency"*; NYC DCWP confirms
  employer-fee-paid agencies placing professional applicants are **exempt from the NYC license**.
  GBL §171 also exempts organizations under the exclusive control of a bona fide nonprofit
  educational or charitable institution — potentially relevant to the 501(c)(3) question.

> **Never take a dollar from a student.** That is the trigger in nearly every state, and it also
> brings fee caps, mandatory written contracts, signed receipts, deposit rules, and bonding.

**41 states require an employment services license; 9 do not** (DE, GA, ID, MD, MS, MO, OH, PA,
SD). Initial fees $0–$3,054, averaging ~$550.

**You must comply with the state where the worker is placed**, not where you are incorporated.
MIT/Stanford/Berkeley/CMU students get placed in CA, NY, MA, and WA — so Florida's permissiveness
would not have saved you anyway.

**The commercial consequence of getting it wrong:** an unlicensed agency's fee contract is
generally **void and unenforceable**. You could not sue a sponsor who refused to pay.

Florida note: no state employment-agency license is required, but **employee leasing / PEO** is
licensed ($250 + $900–1,500 biennial, $50,000 minimum net worth). Avoid by never putting
candidates on your payroll. Florida's talent-agency statute doesn't apply — it defines "artist"
as performers, musicians, and models.

## The eight design rules

1. **Sell access, not outcomes.** Subscription or sponsorship sidesteps the "procuring employment
   for a fee" hook and matches where the entire market has landed.
2. **Never charge a student anything.** The trigger in CA, MA, NY and most states.
3. **Report only first-hand observation of your own event.** The FCRA transactions-and-experiences
   exclusion. No third-party data in candidate artifacts.
4. **Publish artifacts and human narrative. Never a score, ranking, tier, or classification.**
5. **The sponsor makes and documents every hiring decision.** Mirror Wellfound's disclaimers:
   not a party, not a joint employer, no control over the manner or means of work.
6. **Never put a candidate on your payroll** — that is the line into staffing.
7. **Assume Title VII employment-agency status regardless** and keep selection records.
8. If a success fee is unavoidable, make it a **flat per-hire fee ($5K–$20K)**, employer-paid
   only, and get licensed in the placement states — or accept the contract may be unenforceable.

## Sources

[15 U.S.C. §1681a](https://www.law.cornell.edu/uscode/text/15/1681a) ·
[FTC v. Spokeo](https://www.ftc.gov/legal-library/browse/cases-proceedings/1023163-spokeo-inc) ·
[FTC employer guidance](https://www.ftc.gov/business-guidance/resources/using-consumer-reports-what-employers-need-know) ·
[42 U.S.C. §2000e](https://www.law.cornell.edu/uscode/text/42/2000e) ·
[29 CFR 1607.16](https://www.law.cornell.edu/cfr/text/29/1607.16) ·
[29 CFR 1607.4](https://www.law.cornell.edu/cfr/text/29/1607.4) ·
[EU AI Act Annex III](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3) ·
[EU AI Act Art. 6](https://artificialintelligenceact.eu/article/6/) ·
[NY Comptroller LL144 audit](https://www.osc.ny.gov/state-agencies/audits/2025/12/02/enforcement-local-law-144-automated-employment-decision-tools) ·
[Illinois HB 3773](https://www.duanemorris.com/alerts/illinois_enacts_artificial_intelligence_law_focused_employment_practices_0824.html) ·
[Colorado SB 24-205](https://leg.colorado.gov/bills/sb24-205) ·
[CA Civ. Code §1812.501](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1812.501) ·
[MA G.L. c.140 §46A](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleXX/Chapter140/Section46a) ·
[NYC DCWP](https://www.nyc.gov/site/dca/businesses/license-checklist-employment-agency.page) ·
[Harbor Compliance 50-state](https://www.harborcompliance.com/employment-services-license) ·
[Parker Dewey pricing](https://www.parkerdewey.com/pricing) ·
[Wellfound pricing](https://wellfound.com/recruit/pricing) ·
[Vendr: RippleMatch](https://www.vendr.com/buyer-guides/ripplematch) ·
[Vendr: Karat](https://www.vendr.com/marketplace/karat)
