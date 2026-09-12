# Getting Paid

How large tech companies actually pay small vendors. This determines deal structure more than
price does.

## The three findings that matter most

### 1. You cannot self-register as a vendor. You need an internal champion.

Every large tech company with a public supplier page requires an **internal employee** to
initiate onboarding:

> **Twilio:** *"All new Suppliers receive onboarding requests from a Twilio representative."*
> **Cisco:** *"All new supplier requests must be initiated by a Cisco representative."*
> **Microsoft:** its procurement page *"is a resource only and not an application process."*

**No amount of paperwork readiness substitutes for a champion.** Finding the internal sponsor is
the longest pole in the entire process — longer than legal, security, or banking.

### 2. Sell it as a sponsorship, not a research SOW — the cash timing is completely different

Same dollars, radically different curve:

| | Sponsorship | Services PO |
|---|---|---|
| When you're paid | **Before or at the event** | Net 60–90 **in arrears**, after 3-way match |
| IP negotiation | None | Weeks to months |
| Procurement | Often skipped — **only 47% of brands have any procurement resource on sponsorship** | Always |
| Budget source | Marketing (~12% of brand marketing budget is sponsorship by design) | Varies, often requires a line item that doesn't exist |

**The single most useful artifact found in this research** — Atlassian's own sponsor agreement:

> One invoice under $20K. **Two equal invoices at $20K+.** Full payment before the conference.

Other verified sponsorship terms: FS-ISAC net 30, *due on receipt if contracted within 45 days of
the event*. ICTD, Techno Security, NAMA: **50% with contract, balance on a fixed date.**

> **A 50/50 ask isn't scrappy — it's what major tech companies already put on their own paper.**

This directly solves the working-capital gap flagged in [funding.md](funding.md): venue deposits
come due before sponsor money arrives *only if you sell services*. Sponsorship pays up front.

### 3. Price the first engagement at $25K–$50K. A Director signs it.

The enterprise delegation ladder (consultancy template data, tightly convergent):

| Role | Enterprise ($100M+ rev) |
|---|---:|
| Manager | up to $10,000 |
| **Director** | **up to $50,000** |
| VP | up to $250,000 |
| C-suite | up to $1,000,000 |

Where the gates trip:

- **PO required:** commonly $5,000+
- **Legal review:** most-cited trigger **$25,000** — *but* data processing, IP licenses, and
  long-term commitments get legal review **at any dollar value**
- **Competitive bidding:** $25,000–$50,000
- **Security / vendor-risk review: NOT dollar-gated.** This is the key correction. It keys on
  data sensitivity, not contract value. Microsoft's SSPA covers all suppliers processing personal
  data with the rule: *"work cannot start until this is complete."*

Sales-cycle reality: $5–25K closes in 30–90 days; $25–100K in 90–180 days; $100K+ in 3–9 months.

**$25K–$50K is the widest gap between money raised and friction incurred.** Above $100K you buy a
VP signature, formal procurement, competitive bidding, and full legal review.

⚠️ **Never slice a $100K engagement into four $25K invoices.** That is invoice splitting, it
violates essentially every corporate procurement policy, auditors specifically flag "related
purchases from the same supplier each just under threshold," and getting caught burns the
relationship permanently. A genuinely smaller first engagement is the legitimate version.

## The structural move on data

Design the engagement so **you never receive client data and never hand back raw participant
data.** Recruit participants yourself, keep data in your own environment, deliver only
aggregated, de-identified findings.

This can drop you from *"processor handling personal data"* — full security review, DPA,
possible work-start blocker — to *"consultant delivering a report."* It aligns exactly with the
consent architecture in [data-model.md](data-model.md) and the FCRA constraints in
[recruiting-legal.md](recruiting-legal.md).

⚠️ No source confirmed any specific company accepts this framing. Confirm with the sponsor early.

**Do not attempt SOC 2 Type II.** Observation period 3–12 months, first-year cost $20,000–$50,000
— more than the deal and slower than the work.

## Verified payment terms

| Company | Terms |
|---|---|
| **Datadog** | Net 60. **"No Purchase Order — No Pay."** Must invoice within 60 days of delivery. Text-based PDF only. **Will not accept external signature platforms.** |
| **MongoDB** | **Net 75** from receipt. Coupa. Pro-buyer terms: uncapped indemnity, no liability cap. |
| **Twilio** | Net 60 (PO terms) / net 60–90 (supplier page). *"Does not typically approve annual pre-payments."* Background checks on all personnel at supplier expense. |
| **Microsoft** | Net 60, or net 10 less 2%. Clock starts at acceptance **and** a correct undisputed invoice. |
| **Cisco** | **Net 90**, paid **monthly** — a net-90 invoice can land at 100–120 days. |
| **Intel** | Net 90 default |
| **Google** | 15 days for eligible diverse suppliers |

**Get the PO number before doing any work.** Under no-PO-no-pay an invoice without one is
rejected on arrival, not queried — and fixing it requires *your buyer* to raise a requisition
retroactively.

**On a services PO, a first-time vendor will not get a deposit.** What works is **milestone
structuring** — tranches tied to named deliverables. The recognized precedent is the
industry-sponsored research agreement at **50% on execution / 50% on final report**, which
universities use as standard. That's the shape to borrow.

**Contract to cash: realistically 4–8 months.**

⚠️ The widely-quoted APQC "3-day onboarding median" measures only keying a supplier into the ERP
after everything else is done. Don't plan against it.

## The 501(c)(3) complication

⚠️ **This changes the nonprofit plan sketched in [research-findings.md](research-findings.md).**

The IRS definition of a qualified sponsorship payment requires **"no arrangement or expectation
that the person will receive any substantial return benefit other than the use or
acknowledgement of the name or logo."** Benefits ≤2% of the payment are disregarded.

Logo placement and value-neutral description = acknowledgement, fine.
**A research report delivered to the sponsor = substantial return benefit.**

Routed through a 501(c)(3), the research engagement is likely **unrelated business income
taxable to the sponsor organization**, and many fiscal sponsors will simply refuse it. Disclose
the deliverable up front and get a CPA.

An **unrestricted gift** genuinely is the lightest path — Google's academic awards run this way,
median $50–60K, up to $100K. **But a gift cannot carry deliverables, deadlines, or IP rights.**
You cannot promise a report and call it a gift.

### Two shortcuts that don't work

❌ **Hack Club HCB is teen-only.** Its eligibility page requires groups *"led and primarily run by
teenagers (ages 13 to 18)"* and states HCB is *"exclusively focused on teen-led organizations."*
**College students are not eligible**, despite HCB being routinely recommended for student
hackathons. (This corrects the note in [event-comps.md](event-comps.md).)

❌ **MLH does not act as a contracting or payment intermediary** for a local event's own sponsors.
Its own guide tells organizers: *"When a sponsor says yes, invoice them immediately. Create a
contract."*

### What does work

✅ **The university is the natural contracting entity.** MLH's own legal guidance directs student
orgs to their school. Universities are already approved vendors, already carry event insurance,
and already invoice sponsors. Cost is indirect recovery — Harvard charges **68.5% MTDC** for
industry-sponsored research, 34% for other sponsored activity, and a **15% minimum on gifts**.

✅ **Fiscal sponsorship:** Model A 8–15%, Model C 3–10%. Options: **Hack+** (student-focused),
**Players Philanthropy Fund** (~6%), Social Good Fund, Open Collective.

✅ **Pilot under the card threshold, then onboard properly** for the follow-on with a champion
who has already seen the work.

## Insurance — cheap, but budget the loop

Standard for service and event vendors: **$1M per occurrence / $2M aggregate.** Venues demand
more — LA Convention Center requires $1M/$5M plus a $4M umbrella. Twilio's PO terms add
professional liability $1M and **cyber $1M if processing their data.**

All-in cost for a two-person entity handling participant data: **~$1,500–$4,000/year.** One-day
event GL runs $49–$300.

**Cost isn't the problem — the paperwork loop is.** "Certificate holder" is *not* the same as
**additional insured**, and that is the #1 COI rejection. Contracts also demand **waiver of
subrogation** and **"primary and non-contributory"** wording. Budget **2–3 iterations**, and note
deadlines are hard: Northwestern requires the COI 10 business days out and states that without it
*"the event will not be able to take place."*

Also: legal name must **exactly match the IRS record for the EIN.** A DBA mismatch triggers a
CP2100 → "B" notice → **24% backup withholding on all future payments**, and is a common cause of
a silently stalled vendor setup. Have a bank letter on institution letterhead ready.

## Timing — and where we are right now

Annual planning runs **3–6 months before fiscal year start.**

| Company | FY end | Status, Sept 2026 |
|---|---|---|
| Datadog · Twilio · Figma · Amazon/AWS | Dec 31 | **FY2026 Q4 approaching + CY2027 planning** |
| **MongoDB** | **Jan 31** | FY2027 Q3 — ⚠️ FY label runs a year *ahead* |
| Microsoft · Atlassian | June 30 | FY2027 Q1 — **fresh budget, urgency framing won't land** |
| NVIDIA · Salesforce · Snowflake | late Jan | FY2027 Q3 |
| Apple | late Sept | FY2026 ends within days |
| Oracle May 31 · Cisco late July · Adobe ~Nov 30 | | |

⚠️ **Anthropic, Stripe, and Vercel are private — no filings, no verifiable FY end. Just ask.**

**Right now is unusually good timing.** Datadog, Twilio, Figma and AWS are simultaneously heading
into Q4 flush *and* CY2027 planning — the one moment of the year when both the "spend it now" and
the "get in next year's budget" plays are live at the same company.

Best windows: the buyer's **Q4, weeks 6–2 before close** (land before quarter-end close, not
during it), and their **Sept–Nov planning window** for a next-year line item.
Worst: the buyer's **Q1** (budgets finalized but unreleased), late December (procurement and legal
are out — exactly your bottleneck), and the 2–3 weeks after each quarter end.

⚠️ **Credibility warning on "use it or lose it":** the rigorous evidence is *government only*
(Liebman & Mahoney, AER 2017: last-week federal spending is 4.9× the weekly average). Every
corporate budget-flush statistic found was a vendor blog. The mechanism is real; don't cite 4.9%
figures as corporate.

## Donations are the slowest cold path, not the fastest

Big-tech corporate foundations are largely **invitation-only**:

- **Salesforce Foundation:** grants *"accepted on an invitation-only basis"*; *"not able to
  respond to unsolicited funding inquiries"*
- **Adobe:** must be **invited to apply by an active Adobe employee**; window March–April only
- **Cisco:** LOI year-round, full proposals invitation-only, **up to one business quarter** just
  to review an LOI

Timelines run 4–12 weeks for local grants, 3–6 months for strategic ones.

## The four moves

1. **Sell it as a sponsorship, not a research SOW.** Pays before the event, no IP negotiation,
   often skips procurement entirely, and Atlassian's own contract gives you the 50/50 precedent.
2. **Price the first engagement at $25K–$50K.** A Director signs it.
3. **Never touch participant data the client could claim.** Data access, not dollar value,
   triggers the security review that can block work from starting at all.
4. **Contract through an entity that's already a vendor** — the university or a fiscal sponsor —
   and get the PO number before doing any work.

## Sources

[Twilio supplier info](https://www.twilio.com/en-us/legal/supplier-code-of-conduct/supplier-information) ·
[Twilio PO terms](https://www.twilio.com/en-us/legal/po-terms) ·
[Datadog vendor help](https://www.datadoghq.com/vendor-help/) ·
[MongoDB vendor FAQ](https://www.mongodb.com/legal/vendors/faq) ·
[Microsoft SSPA](https://www.microsoft.com/en-us/procurement/sspa) ·
[Atlassian sponsor agreement](https://www.atlassian.com/dam/jcr:80ffbaa7-034d-49e3-b23b-67dd8c36e58f) ·
[FS-ISAC sponsor terms](https://www.fsisac.com/event-sponsor-terms-and-conditions) ·
[IRS qualified sponsorship payments](https://www.irs.gov/charities-non-profits/advertising-or-qualified-sponsorship-payments) ·
[HCB eligibility](https://help.hcb.hackclub.com/en/articles/15409923-who-can-apply-for-fiscal-sponsorship) ·
[MLH sponsorship process](https://guide.mlh.com/general-information/getting-sponsorship/the-5-step-mlh-sponsorship-process) ·
[LACC insurance requirements](https://www.laconventioncenter.com/assets/doc/EventInsuranceRequirements-June2015.pdf) ·
[Tallyfy approval limits](https://tallyfy.com/approval-limits-matrix-template/) ·
[Lattice purchasing policy](https://lattice.com/templates/sample-corporate-purchasing-policy) ·
[GSA micro-purchase threshold](https://smartpay.gsa.gov/guidance-and-audits/smart-bulletins/002/)
