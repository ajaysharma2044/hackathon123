# Open Questions

Decisions that block building. Revised after the research wave — answered questions are marked
and kept for the record, since knowing what's settled matters as much as knowing what isn't.

## ✅ Answered by research

| # | Question | Answer |
|---|---|---|
| 3 | Minimum sponsor deliverable that's honest at this sample size | LF Research sells a **150-complete study for $25,000** — below a 200-person cohort. See [research-pricing.md](research-pricing.md) |
| 5 | How many sponsors at what size clears the budget | **~$310K from 15 relationships, none above $55K.** Revised stack in [funding.md](funding.md) |
| 6 | Who is the first sponsor conversation with | **A UX Research Director or Field Marketing Manager** — they hold budget at the right size and already have a vendor path. Not a University Recruiting Lead, who cannot fund this. See [procurement.md](procurement.md) |
| 8 | How is `tool_switched` actually captured | **Broker the sponsor's API keys through your registration.** Server-side ground truth instead of self-report. Make it a term of the research tier. See [measurement.md](measurement.md) |
| — | Should we take equity in teams | **No.** Post-hoc SPVs (~$4,500 all-in) and VC referral memos ($2–5K each) instead. See [venture-upside.md](venture-upside.md) |
| — | Should we charge participants | **No.** Nobody credible at the elite end does; On Deck charged $2,990 and is the one that collapsed. See [event-comps.md](event-comps.md) |

## 🔴 Blocking — decide these first

**1. Where, and when.**
Location is open again. The framework and candidate comparison are in [location.md](location.md).
The resolution worth pricing first: **a university campus in or adjacent to a major sponsor city,
in summer** — dorm housing, in-kind venue, sponsors close enough to attend. Pricing 200 flights
from the real target-school list for 3 candidate cities probably decides this on its own.

**2. Entity structure — and it's now harder than it looked.**
A 501(c)(3) unlocks tax-deductible payments, foundation grants, and easier procurement. But the
IRS qualified-sponsorship safe harbor requires **no substantial return benefit beyond logo
acknowledgement** — and a research report delivered to a sponsor is exactly such a benefit,
likely creating unrelated business income. Many fiscal sponsors will refuse it outright.
Hack Club HCB is teen-only and unavailable. **Needs a CPA before anything is formed.**
See [procurement.md](procurement.md).

**3. Who is the named champion at each target company?**
You cannot self-register as a vendor at Twilio, Cisco, Microsoft, Datadog, or MongoDB — an
internal employee must initiate. **Finding the champion is the longest pole in the entire
process**, longer than legal, security, or banking. This is a research task that should start
before the pitch is finished.

**4. Will sponsors actually broker API keys through you?**
The single highest-value instrument depends on it. Confirm feasibility with 2–3 target sponsors'
APIs before designing the measurement around it. If they won't, the switching data reverts to
self-report and the research product is meaningfully weaker.

**5. What is the unconstrained-surface floor?**
If sponsors buy required exposure on every track, there is no control condition anywhere and the
research product collapses. Needs a stated, defended minimum before the first sponsor negotiation
— because it will be negotiated.

## 🟡 Needed before the event

**6. Operational definitions: `activation`, `meaningful action`, `repeated use`, `retention_30d`.**
These are decisions, not observations. Write them before the event or they become dials that get
turned until the report looks good. See [measurement.md](measurement.md).

**7. Legal review — now well-scoped, still required.**
The research sharpened this considerably: FCRA constrains the recruiting artifact to first-hand
observation only; NYC LL144, the EU AI Act and UGESP all turn on whether you emit a score;
Title VII employment-agency status attaches "with or without compensation"; and licensing depends
on the state where a candidate is *placed*, not where you incorporate. All in
[recruiting-legal.md](recruiting-legal.md). A lawyer still needs to read it.

**8. What does revocation do to already-delivered evidence?**
If a participant withdraws recruiting consent at day 45, what happens to what a sponsor already
received? Define before the first recruiting deliverable ships.

**9. Minimum cell size for sponsor-facing segment cuts.**
Enforces the aggregate-only promise instead of merely asserting it.

**10. Participant agreement: IP and paid follow-on work.**
Who owns what a team builds? What is the status of a $10–50K follow-on engagement — contractor,
grant, or investment? Settle before the first one happens.

## 🟢 Architectural

**11. Club OS — and FCRA now constrains the answer.**
Shared data layer, or sibling with a join key? New wrinkle: feeding pre-event campus history into
a *recruiting* artifact crosses the FCRA line. It remains fine as an aggregate research covariate.
That distinction has to be enforced in the schema, not in policy.

**12. Does the platform exist for event #1, or does event #1 run on forms and spreadsheets?**
Still genuinely open. Building the full event-stream system before running an event means modeling
a process nobody has performed. The counter-argument: the brokered-key system is the product
differentiator and probably can't be faked.

**13. Build vs. buy for the event stream.**
Off-the-shelf analytics covers a lot early. The custom parts are the experiment record, consent
scoping, and bitemporal handling.

## ⚪ Minor

**14. The repo is still `hackathon123`.** The thesis is explicitly that this is not a hackathon
company. Worth renaming once there's a real name.
