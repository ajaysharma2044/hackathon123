# Roadmap — Event 1

**Team:** 2 people at Cornell. `AJ` — qualitative, creative. `AM` — technical.
Every task has exactly one owner. On a two-person team, shared ownership means unowned.

**Target:** ~200 selected builders, flown in, housed, fed. Mid-to-late August 2027.
See [funding.md](funding.md) for why that date and what it costs.

## The critical path

One thing gates everything else.

```
ANCHOR SPONSOR
      ↓
money exists → venue and housing can be contracted
      ↓        → applications can open
      ↓        → the primary research question is defined
      ↓        → the instrumentation has something to instrument
```

Without an anchor sponsor there is no event, no research question to design around, and nothing
for the platform to capture. Everything downstream is blocked on it, and nothing downstream
substitutes for it.

**The deadline that matters: corporate budgets for 2027 are being set right now, Q4 2026.**
An anchor conversation starting after January 2027 is selling into money that is already
allocated. The window is the next ~12 weeks.

That has an uncomfortable implication for a two-person team where one person is technical: for
the next quarter, the technical work is *not* the critical path. Build only what the sponsor
conversation needs.

## Working backward

```
Sep–Dec 2026    anchor sponsor conversations        ← we are here
Jan–Mar 2027    close anchor, open the rest of the stack
Mar 2027        venue + housing contracts (go/no-go on cash in hand)
Apr 2027        applications open
Jun 2027        applications close, selection
Jul 2027        travel booking, instrumentation dry run
Aug 2027        event
Aug–Nov 2027    follow-up waves, analysis, report
```

## Division of labor

### AJ — demand, experience, meaning

| | |
|---|---|
| **Sponsor development** | The whole pipeline. 60–100 qualified conversations to close 11. This is a job, not a task. |
| Research question design | Turning a sponsor's business goal into a falsifiable hypothesis. |
| Participant experience | The event must be genuinely excellent — this is what protects the panel. |
| Builder recruitment & selection | Who gets in, and the rubric. |
| Interview protocol + observer codebook | Including training the 8–12 floaters. |
| Qualitative coding | Free text → structured friction records. |
| The report | Findings that read as research, not as a recap. |
| Brand, narrative, name | |

### AM — capture, structure, analysis

| | |
|---|---|
| **Brokered API key system** | The highest-value instrument. See [measurement.md](measurement.md#1-brokered-api-keys--do-this). |
| Event stream + consent enforcement | Scoped, revocable, enforced at query time. |
| Registration + application intake | Structured fields, not free text — selection data must be analyzable later. |
| Checkpoint capture | The 6-hour instrument, and its compliance mechanics. |
| Follow-up system | 7/30/90. Where retention data comes from. |
| Analysis pipeline | Funnels, segment cuts, minimum cell size enforcement. |
| Club OS linkage | Shared data layer, or sibling with a join key. |

### Unowned — assign these

Budget ownership, venue, food, insurance, university approvals, legal review, entity formation.
Genuinely nobody's right now. Entity formation in particular blocks contract signing, and
contract signing has personal liability attached — see
[funding.md](funding.md#do-not-personally-guarantee-anything).

## Next 30 days

Weighted toward the sponsor window, because it closes.

| # | Task | Owner |
|---|---|---|
| 1 | Build the anchor sponsor pitch: their unknown first, our event second | AJ |
| 2 | Target list — 25 companies, named individual per company (DevRel lead / university recruiting lead, not `sponsorships@`) | AJ |
| 3 | Work the Cornell warm-intro surface: eLab, Cornell Tech, faculty, alumni | AJ |
| 4 | Cost the event for real — quotes for venue, housing, food in the two candidate cities | AJ |
| 5 | Pick the date and the city | AJ + AM |
| 6 | Form the entity — blocks every contract | AJ |
| 7 | Spec the brokered API key system; confirm it's feasible with 2–3 target sponsors' APIs | AM |
| 8 | Stand up the schema; load it | AM |
| 9 | Decide Club OS: shared data layer or sibling + join key | AM |
| 10 | Build one thing that makes the pitch concrete — a sample findings report on invented data | AJ + AM |

Item 10 is worth more than it looks. You are selling a deliverable nobody has seen. A mocked
report, clearly labeled as illustrative, converts a conversation about an idea into a
conversation about a product.

## Days 30–90

| # | Task | Owner |
|---|---|---|
| 11 | Run the sponsor pipeline. This is the quarter's real work. | AJ |
| 12 | Write the consent document — six scopes, plain language | AJ |
| 13 | Legal read: student data, post-event tracking, international participants | AJ |
| 14 | Build registration + consent capture | AM |
| 15 | Build brokered key issuance | AM |
| 16 | Structured application intake | AM |
| 17 | Once anchor is close: define the primary question, pre-register hypothesis, write funnel definitions | AJ + AM |

## Do not build yet

Experimentation marketplace, VC team discovery, multi-event category intelligence, anything
predictive, any general-purpose platform. All real, all downstream of Event 1 producing a report.

The failure mode for a technical co-founder on a project like this is building the beautiful
version of the platform during the quarter when the only thing that mattered was getting a
company to say yes.
