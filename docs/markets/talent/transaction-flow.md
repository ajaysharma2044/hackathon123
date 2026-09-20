# Transaction Flow — Funnel, Mutual Opt-In, Paid Projects, Pipeline (Parts XX–XXIII)

How an employer's interest becomes a real interaction — and the honest accounting that keeps an
introduction from being mistaken for a hire. Implemented in `engine/mutual_intro.py` and
`engine/opportunity_market.py`, stored in `employer_interest`, `mutual_intro`, `employment_outcome`,
and `paid_project`.

Vocabulary: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**;
⚠️ unverified. Missing ≠ bad.

## The talent funnel (Part XX)

`mutual_intro.TALENT_FUNNEL`, in order:

```
NEED → SEARCH → PACKET_VIEWED → PARTICIPANT_INTEREST → MUTUAL_OPT_IN
     → INTRODUCTION → INTERVIEW → OFFER → HIRE
```

The first five stages are things the platform can observe (a search ran, a packet was viewed, both
sides opted in). The last four — `INTRODUCTION` onward, and especially `INTERVIEW / OFFER / HIRE` —
are **outcomes only the participant/employer can report**, and the code never fabricates them.

## Mutual opt-in — the contact choke point (Parts XX–XXI)

An employer can express interest, but **no contact is released until both sides opt in**. This is
`mutual_intro.IntroRequest`:

```python
@property
def both_opted_in(self) -> bool:
    return self.counterparty_opted_in and self.subject_opted_in and self.subject_visible
```

Three conditions, all required:

1. `counterparty_opted_in` — the employer expressed interest (defaults true when a request is made).
2. `subject_opted_in` — the participant **accepted** (defaults **false**; set true only by
   `.accept()`).
3. `subject_visible` — the participant made this scope visible at all.

`release_contact(req, contact)` is "the single choke point that prevents any contact disclosure
without mutual consent" — it raises `PermissionError` unless `contact_releasable()` (i.e.
`both_opted_in`) is true. There is no other path to a contact detail: no scraping, no exceptions. The
`mutual_intro` table carries `both_opted_in boolean not null default false`, so the database default
is also "not releasable."

The flow across the tables:

```
employer_interest (participant_response: PENDING → ACCEPTED/DECLINED)
   └─ on ACCEPTED → IntroRequest.accept() sets subject_opted_in
        └─ both_opted_in ⇒ release_contact() ⇒ mutual_intro row (both_opted_in=true, introduced_at)
             └─ employment_outcome (transaction, happened, participant_shared)
```

The participant always controls the introduction — the module docstring: "The participant/team always
controls the introduction."

## Introduction ≠ hire — funnel liquidity (Part XXIII / Part LXI)

`funnel_liquidity(counts, kind="talent")` reports per-stage counts across the funnel **without**
equating an introduction with a transaction. It attaches an honest caveat verbatim:

> "An introduction is not a hire/deal. Downstream stages are only recorded when the participant/team
> voluntarily shares the outcome."

`test_talent_venture.py` pins both properties: the report contains all `TALENT_FUNNEL` stages, and the
`_note` contains "not a hire." This matters because the temptation in any recruiting funnel is to
count intros as placements — the code refuses to, and the `employment_outcome.participant_shared`
column (default false) means an outcome is only recorded "if participant chooses to share." An unshared
outcome is genuinely unknown, not assumed positive or negative.

## The paid-project market (Part XXII)

A relationship shouldn't end when an employer spots an interesting team. `docs/products.md`:
"Hackathon → PaidFollowOnProject." In code this is the `PAID_PROJECT` visibility scope
(`compliance.VISIBILITY_SCOPES`) and the `paid_project` table:

```
paid_project(company_id, participant_id, scope_of_work, duration_weeks, ip_terms,
             compensation_note,  status)
```

`compensation_note` is "clarified before continuation (Part LXI)" (SQL comment) — terms are settled
before work starts, not after. Evidence produced by a paid continuation carries
`source_kind = PAID_CONTINUATION` and `type ∈ {CONTINUATION, PAID_CONTINUATION}`, and the
`CONTINUATION_30D` activity fans out to `HiringValue`/`VentureValue` **only** on the relevant opt-in
(`opportunity_market.ACTIVITY_FANOUT`).

Legal shape (from `docs/recruiting-legal.md` and `opportunity_market.MONETIZATION`):

- `PAID_PROJECT_FACILITATION` is **NEEDS_LEGAL** — "clarify IP + worker classification before
  facilitating paid work."
- Never put a candidate on your payroll (design rule 6 — the line into staffing / PEO licensing).
- IP ownership and contractor classification "should be settled in the participant agreement before
  the first one happens" (`docs/products.md`).

Pricing comparable: $10K–$50K per team continuation (`docs/products.md`, explicitly "illustrative, not
validated pricing"). WTP: **UNKNOWN.**

## Event → employment pipeline (Part XXI)

The full pipeline, from a naturally-produced activity to a possible job, tying the modules together:

```
build activity (repo/demo)                         work_evidence.WorkEvidence
   └─ fan_out(activity, opted_scopes)              opportunity_market.fan_out
        └─ HiringValue lights up ONLY if EMPLOYER opted-in
             └─ evidence_for_scope(EMPLOYER)       work_evidence.evidence_for_scope
                  └─ retrieve(job, views)          talent_matching.retrieve   (opt-in gated)
                       └─ decomposed match         talent_matching.match      (no overall_score)
                            └─ employer_interest → IntroRequest.accept  → MUTUAL_OPT_IN
                                 └─ release_contact()                    → INTRODUCTION
                                      └─ INTERVIEW / paid_project        → employment_outcome
                                           (recorded only if participant_shared)
```

Every transition is opt-in or participant-controlled, and the terminal states (interview, offer, hire,
paid project) are outcomes the platform records only when voluntarily reported. `dedup_revenue`
(`opportunity_market.py`) ensures that even when one project spawns several transactions, the same
economic value is counted once — an introduction inflating into a phantom pipeline is impossible by
construction.

## Cross-market transaction vocabulary

The `opportunity_transaction` enum (SQL) names the legitimate outcomes an intro can lead to:
`INTERVIEW, JOB, INTERNSHIP, PAID_PROJECT, DESIGN_PARTNERSHIP, RD_CONTINUATION, CUSTOMER_INTRO,
VC_INTRO, ACCELERATOR_INTRO`. `employment_outcome.transaction` draws from it — but `happened` and
`participant_shared` remain the honest gates on whether any of it is real and known.
