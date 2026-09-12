# Consent Architecture

Participant-friendly, modular consent for the live research OS (Parts XXXIV–XXXV of
[live-research-os.md](live-research-os.md)). This is the document that makes the master doc's one
hard constraint — *the experience wins* — legible to the person being researched. Consent here is
**data**, not a signature: it is an append-only ledger enforced at query time in
[`capture.py`](../../engine/capture.py), and the exact scopes are defined in
[`001_core.sql`](../../schema/001_core.sql) and [research-data-model.md](../research-data-model.md).

> **The test:** a participant should be able to read the whole consent surface in a few minutes,
> know exactly what leaves the room and what never does, and change their mind at any time without
> having to delete their weekend. If they can't, the design failed — not the participant.

## Tiered, modular consent mapped to the exact scopes

Consent is not one checkbox. It is a tier of required event operation plus a set of *independent*
opt-ins, each mapped to one scope. A participant can grant aggregate research and decline every
discoverability scope, or vice versa, and the event experience is identical.

```
TIER 0 — REQUIRED TO PARTICIPATE
  CORE_EVENT              running the event: registration, teams, judging, safety. Minimal. Not research.

TIER 1 — RESEARCH (opt-in, independent toggles)
  AGGREGATE_RESEARCH      your behavior feeds AGGREGATE, min-cell-suppressed findings (never you alone)
  PRODUCT_TELEMETRY       your brokered-key use of a NAMED product is instrumented (disclosed per product)
  QUALITATIVE_RESEARCH    checkpoints / observer notes / interviews may be used in research
  (artifact analysis)     your submitted repo / deploy / dependency manifest may be analyzed — a
                          QUALITATIVE_RESEARCH + AGGREGATE_RESEARCH use, flagged at submission

TIER 2 — FOLLOW-UP (opt-in)
  LONGITUDINAL_FOLLOWUP   we may contact you at 7 / 30 / 90 days (longitudinal-followup.md)

TIER 3 — INDIVIDUAL-GRAIN DISCLOSURE (opt-in, just-in-time re-prompted, the only scopes that
                                      ever expose YOU to an outside party — your own work only)
  RECRUITING_DISCOVERABILITY        employers may see your opted-in first-hand work evidence
  VC_DISCOVERABILITY                investors may see your team's trajectory
  DESIGN_PARTNER_DISCOVERABILITY    a sponsor may be introduced to you as a design partner

TIER 4 — MEDIA / PUBLICATION / LINKAGE (opt-in)
  PUBLIC_MEDIA            you may appear in photos / recordings / marketing
  ANONYMIZED_PUBLICATION  anonymized data may appear in a public "State of…" report
  LONGITUDINAL_LINKAGE    event data may be joined to Club OS / prior-event history
  (recorded interviews)   a QUALITATIVE_RESEARCH interview is recorded only with a separate yes
```

## What each participant is told, in plain language

The UX is **short, plain, and just-in-time** — not a 20-page legalistic wall. One clear screen per
tier at the moment it becomes relevant, plus re-prompts at the sharpest moments (below).

| Scope | What is collected | Why | Who receives what |
|---|---|---|---|
| CORE_EVENT | identity, team, submission | run the event | organizers only |
| AGGREGATE_RESEARCH | behavioral events | find patterns across the cohort | clients, **aggregate-only, n≥8** |
| PRODUCT_TELEMETRY | calls/errors/timing for a named product | activation & friction, server-side | that product's client, **aggregate** |
| QUALITATIVE_RESEARCH | checkpoint answers, notes, interviews | the "why" behind behavior | clients, as **coded, human-gated** excerpts, aggregate |
| follow-up | 7/30/90-day responses | retention — the thing no one else has | clients, **aggregate** |
| *_DISCOVERABILITY | **your own** work evidence | opt-in intros you control | the specific outside party **you** approve |
| PUBLIC_MEDIA | photos / recordings | marketing | public |
| ANONYMIZED_PUBLICATION | anonymized data | public report | public, **de-identified** |

### What is NOT collected (say it plainly, up front)

Nothing on the no-go list, ever. This is not a limitation participants have to discover — it is
stated on the first consent screen, because *knowing what you are safe from* is what lets the rest
feel low-stakes.

### Aggregate vs may-be-linked-to-you

```
ALWAYS AGGREGATE, NEVER YOU ALONE         MAY BE LINKED TO YOUR ARTIFACTS / YOU
  AGGREGATE_RESEARCH (min cell 8)           the three *_DISCOVERABILITY scopes (your own work,
  PRODUCT_TELEMETRY → client reports         you opt in, you approve each intro)
  QUALITATIVE_RESEARCH → coded findings      PUBLIC_MEDIA (you, by definition)
  ANONYMIZED_PUBLICATION                     recorded interviews (separate yes)
```

`AGGREGATE_RESEARCH` and `ANONYMIZED_PUBLICATION` are **aggregate-only**
([`capture.py`](../../engine/capture.py) `AGGREGATE_ONLY`): the store will *refuse* to emit
individual-grain output for them even if rows exist. Only the `*_DISCOVERABILITY` scopes
(`INDIVIDUAL_DISCLOSURE_OK`) can produce individual output, and only of the participant's own
first-hand work (the FCRA constraint — [recruiting-legal.md](../recruiting-legal.md)).

## The no-go capture list (default-prohibited, permanently)

```
keystroke logging · continuous screen recording · private-message (DM) capture · covert/secret audio
personality inference · intelligence inference · employability / quality / founder scoring
protected-trait inference · covert monitoring of any kind · individual sponsor dossiers on participants
```

None of this is built, none of it is a toggle a client can buy, and none of it is unlocked by any
consent scope. `assert_clean` ([live-research-os.md](live-research-os.md)) rejects any record that
tries to carry a person score or a protected-trait field; there is deliberately no such column
anywhere in [`006_live_research.sql`](../../schema/006_live_research.sql). Anything here would
require an independent ethical + legal review clearing a specific, disclosed, consented use — and
nothing in Event 1 needs any of it.

## Just-in-time re-prompts (not a one-time wall)

The legalistic failure mode is a huge up-front form nobody reads. Instead, consent is confirmed at
the **freshest, highest-stakes moment**, in one line:

```
before a recruiter / VC / design-partner intro is surfaced   → "Share this project with <party>? yes / no"
before an interview is recorded                              → "OK to record this? you can stop anytime"
before a quote could appear in a public report               → "OK to quote you (anonymized)?"
```

A just-in-time yes is itself a `GRANT` row in the ledger; it is revocable like any other.

## Enforcement: the query-time gate and revocation without deletion

Consent is **not** enforced by deleting data when someone opts out. It is enforced every single
time the data is queried, from the append-only ledger, as-of query time — so a revocation takes
effect on the *next* query with nothing erased ([`capture.py`](../../engine/capture.py),
`ConsentLedger.effective` + `CaptureStore.query`):

```
query(purpose, as_of):
  (a) available_at <= as_of        -- point-in-time: no future knowledge leaks backward
  (b) purpose in row.consent_scope -- collected under a scope covering this purpose
  (c) ledger.effective(subject, purpose, as_of) == GRANT   -- STILL consented at query time
```

Revocation is a `REVOKE` row with an `effective_at`; the latest action for `(participant, scope)`
wins. The raw evidence stays immutable and append-only (corrections use `superseded_by`, never
`UPDATE`). A **deletion tombstone** marks a row as withdrawn from all future queries without
mutating the audit trail — the ledger must be able to prove *what was true when*, which hard
deletion would destroy. Revocation is therefore prospective by construction.

## Revocation of already-delivered discoverability evidence — stated plainly

This is the one honest limit, and participants are told it before they opt in:

```
GOING FORWARD   revoking RECRUITING_DISCOVERABILITY (or VC / DESIGN_PARTNER) stops ALL future
                disclosure immediately — no new recruiter sees your work, no new intro is made.

ALREADY SHARED  a report already delivered to an employer, or an intro already made, cannot be
                un-sent — it left our system. We cannot claw a PDF back out of a recruiter's inbox.
```

We do not pretend otherwise. What we control — future queries, future intros, future reports — we
stop the instant you revoke. What already left, we are honest that we cannot recall. This is why
the discoverability scopes are **opt-in, per-party, and just-in-time re-prompted**: so the
irreversible step is never taken without a fresh, specific yes at the moment it happens.
