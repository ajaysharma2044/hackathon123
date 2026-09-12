# The Talent Market — Hiring as an Opt-In Downstream Consumer

This document describes the talent market **as it exists in code today**. Every behavioral claim
below is traceable to a symbol in `engine/`; every legal or pricing claim is traceable to a doc
already in this repo. Where the code does not settle a question, it is marked **UNKNOWN** — it is
not guessed.

Vocabulary, held to throughout: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**, statuses
**KNOWN / LIKELY / UNKNOWN / CONTRADICTED**, ⚠️ for anything unverified or secondary. **WTP is
UNKNOWN until a signed check** — a comparable price is a comparable, not observed willingness to
pay.

## The thesis

Hiring is not a product bolted onto the event. It is an **opt-in downstream consumer of
work-evidence the event produces anyway**. The header of `schema/010_talent_venture.sql` states it
directly: "opt-in downstream consumers of naturally produced event work-evidence. NOT a recruiting
product bolted on the side."

A participant builds something at the event. That single activity produces evidence with
provenance. Most of that evidence serves the participant and the research product with no external
disclosure at all. **Only when the participant opts a specific scope visible does any of it reach
an employer.** The default is invisible; visibility is an explicit, revocable, per-scope act.

The code enforces this at three independent choke points:

- `compliance.individual_disclosure_allowed(visibility, scope)` — an individual is exposed to a
  scope **only** with an explicit, non-revoked opt-in for that exact scope; absence defaults to not
  visible.
- `talent_matching.retrieve(job, participant_views)` — returns matches **only** for participants
  where `pv.opted("EMPLOYER")` is true; non-opted participants are never returned.
- `mutual_intro.release_contact(req, contact)` — raises `PermissionError` unless
  `req.contact_releasable()`, which requires the counterparty opted in **and** the subject opted in
  **and** the subject made the scope visible. This is "the single choke point that prevents any
  contact disclosure without mutual consent."

## The three data levels, kept separate

Defined once in `compliance.DATA_LEVELS` and mirrored in the SQL `data_level` enum:

| Level | Symbol value | Meaning | Individual disclosure? |
|---|---|---|---|
| A | `A_EVENT_OPERATIONS` | Run the event | **Never** individually disclosed externally |
| B | `B_AGGREGATE_RESEARCH` | Population / team level | Not an individual dossier |
| C | `C_OPT_IN_PROFESSIONAL` | Participant chose to expose defined work-evidence | Only with per-scope opt-in |

The separation is not advisory. `WorkEvidence.visible_to(scope)` returns true only when
`data_level == "C_OPT_IN_PROFESSIONAL" and scope in self.consent_scope`. A-level and B-level
evidence can never become individually visible to an employer no matter how the scope is set,
because `visible_to` checks the level first.

This separation is also the FCRA firewall. `docs/recruiting-legal.md` establishes that the
recruiting artifact must contain **only first-hand observation of your own event** (the §1681a(d)(2)(A)(i)
transactions-and-experiences safe harbor); longitudinal / third-party history stays in aggregate
research. The A/B/C split is that firewall expressed in the schema — Level C carries only
event-observed evidence, and Level B (longitudinal, aggregate) is structurally barred from
individual disclosure.

## The value fan-out — one artifact, many surfaces

A single naturally-produced activity serves **many** value surfaces at once, but the hiring surface
lights up only on opt-in. This is `opportunity_market.fan_out(activity, opted_scopes)` over
`ACTIVITY_FANOUT`:

```
REPO_SUBMISSION with no opt-in       → ParticipantValue, ResearchValue, CommercialValue, CompoundingValue
REPO_SUBMISSION with {EMPLOYER:True} → ...the above PLUS HiringValue
MENTOR_REQUEST (any opt-in)          → ParticipantValue, OperationalValue, ResearchValue, CommercialValue
                                       (never HiringValue or VentureValue — support, not evidence-for-sale)
```

`VALUE_SURFACES` is deliberately kept as a **vector, never auto-summed** — `HiringValue` sits
alongside `ParticipantValue` and the rest without being collapsed into one number. And
`MENTOR_REQUEST` is pointedly excluded from any hiring/venture surface: asking for help is support,
not a sellable signal. This is the same rule `work_evidence.FORBIDDEN_CONTRIBUTION_METRICS` enforces
on `mentor_requests` (see `work-evidence-graph.md`).

## The integrated graph

```
participant
   └─ joins → team
        └─ builds → project (build)
             └─ produces → ProjectRole (team-declared + participant-confirmed)
             └─ produces → WorkEvidence + artifact (provenance-tagged)
                  └─ mapped → capability evidence (ARTIFACT_SUPPORTED / SELF_REPORTED)
   participant OPT-IN (per scope: EMPLOYER)          ← the gate; default off
        └─ evidence_for_scope(EMPLOYER) becomes retrievable
             └─ employer market: JobRequirement → talent_matching.retrieve → decomposed match
                  └─ employer expresses interest (IntroRequest, counterparty_opted_in)
                       └─ participant accepts (subject_opted_in) → MUTUAL OPT-IN
                            └─ release_contact() → INTRODUCTION
                                 └─ INTERVIEW / paid project   ← never an automated hire
```

Each arrow is a symbol: `evidence_for_scope` (`work_evidence.py`), `retrieve` / `match`
(`talent_matching.py`), `IntroRequest.accept` / `release_contact` (`mutual_intro.py`), the
`TALENT_FUNNEL` stages (`mutual_intro.py`). Critically, a **match is evidence retrieval, never a
hiring decision** — `talent_matching.match` returns no `overall_score` key and `explain()` ends
every output with "This is evidence-based retrieval, not a hiring recommendation."

## Part LXXVI — HIRING research questions 1–10

**Q1. What does a resume miss that event work-evidence captures?**
A resume is a self-authored claim list. The code models the alternative as a **graph of evidence
with provenance**: `WorkEvidence` carries `source_kind` (one of `compliance.EVIDENCE_SOURCE_KINDS`:
`SELF_REPORTED`, `TEAM_CONFIRMED`, `ARTIFACT_OBSERVED`, `PUBLIC_REPO`, `PAID_CONTINUATION`,
`LONGITUDINAL_OBSERVED`), an `artifact_ref`, and a `verification_method`. A resume line "built
backend" becomes, in `render_claim`, "X opted to disclose role ownership; X was recorded by the team
as [the backend workstream]" — team-confirmed, artifact-linked, consented. The missing thing a
resume can't carry is **first-hand, provenance-tagged observation of the actual build**.

**Q2. What does GitHub miss?**
GitHub shows commits, not owned role or confirmed contribution. The code refuses to infer ownership
from commit history: `ProjectRole.is_valid` requires `declared_by_team AND confirmed_by_participant`,
and `commit_count` / `lines_of_code` are named in `FORBIDDEN_CONTRIBUTION_METRICS` precisely so no
ranking is ever built over them. GitHub also crosses the FCRA line — `docs/recruiting-legal.md`
marks "GitHub history · past projects" as **INSIDE FCRA** (third-party, not your own event), so it
must never appear in the candidate artifact. Event evidence stays inside the safe harbor.

**Q3. What does a coding assessment (Karat / CodeSignal / HackerRank) miss?**
An assessment produces a score on a synthetic task. This system produces **no score of any kind** —
`compliance.FORBIDDEN_SCORES` and `assert_not_a_person_score` block `candidate_score`,
`employability`, etc. What it captures instead is real collaborative work: role ownership, a shipped
artifact, technical decisions, a demo — `EVIDENCE_TYPES` in `work_evidence.py`. The assessment
vendors are the direct pricing comps (Q7) precisely because they sell what this deliberately does
not: a number.

**Q4. What is the incremental value over resume + GitHub + assessment combined?**
Observed, consented, artifact-anchored evidence of **how someone actually built inside a real team**,
decomposed across `talent_matching.MATCH_DIMS` (capability coverage, artifact relevance, domain,
technology overlap, role/location/availability fit) — with honest unknowns surfaced, never filled in
as zeros (`missing = None`, `neutral_when_missing`). Whether a buyer *pays* for that increment is
**UNKNOWN** (no signed check; see `docs/STATE.md` — "Will any buyer pay… UNKNOWN. This is the whole
ballgame").

**Q5. Which hiring role values it most?**
See `employer-products.md` Part LIV in full. In short: the **hiring manager** who defined a
challenge and wants to see the work is the most natural buyer of Work Evidence Access; the **recruiter**
values top-of-funnel Role-Specific Search; **university-recruiting** is the weakest fit — `docs/STATE.md`
marks "Will a University Recruiting Lead fund this? **CONTRADICTED** (NACE: ~$2,850/school median
budget)." Which role actually pays is otherwise **UNKNOWN**.

**Q6. Who pays?**
The employer, never the participant. `docs/recruiting-legal.md` design rule 2: "Never charge a
student anything" — the trigger in CA (Civ. Code §1812.501), MA (c.140 §46A), NY (GBL §171) and most
states. And the safer structure is **access/subscription, not per-hire**:
`opportunity_market.MONETIZATION` marks `TALENT_ACCESS_SUBSCRIPTION` **ALLOWED** ("the safer
structure") while `RECRUITING_PARTNERSHIP` and `PLACEMENT_SUCCESS_FEE` are **NEEDS_LEGAL**.

**Q7. What are the pricing comparables?** (comparables only — **not** observed WTP)
From `docs/recruiting-legal.md` real-contract data: Karat **$175,695**; RippleMatch **$68,622 avg**
($40K–$132,600) — "the single most relevant comp"; Handshake TES ~$29,835; CodeSignal $24,394;
Untapped $24,150; HackerRank $13,099. Published seat pricing: Handshake Pro $450/mo; Symplicity
$55/post/school; Wellfound Starter $135/seat/mo. Parker Dewey charges **no conversion fee** and sells
subscription ($5,000 pilot, $7,500–$15,000/yr). Contingency norms: entry-level **10–15%** or flat
**$5K–$20K/hire**. These are comparables; WTP for *this* deliverable is **UNKNOWN**.

**Q8. What must NEVER be shown to employers?**
Any person score (`FORBIDDEN_SCORES`), any sensitive attribute (`SENSITIVE_ATTRIBUTES`), any
contribution ranking by `FORBIDDEN_CONTRIBUTION_METRICS` (lines of code, commits, hours online,
mentor requests), any Level A/B individual data, and any evidence a participant did not opt into for
the `EMPLOYER` scope. Missing evidence is shown as an honest unknown, never as a negative.

**Q9. Is willingness-to-pay known?**
**UNKNOWN.** Every number in Q7 is a comparable price from a published rate card or contract dataset.
`docs/STATE.md` is explicit that all evidence is supply-side and "the specific check is not" proven.
Recruiting has the more quantified adjacent WTP (~$35K cost-to-hire; hackathon hiring ~$5–10K/hire,
~4.2 qualified hires/event — `docs/STATE.md`), which is why it may be the easier first check — but a
check is still unsigned.

**Q10. What legal shape makes it sellable at all?**
Sell access, not outcomes; report only first-hand event observation (FCRA safe harbor); never emit a
score (NYC LL144 / EU AI Act / UGESP); assume Title VII employment-agency status regardless; never
charge a student. See `legal-policy.md` for the full mapping to `recruiting-legal.md`.

## Invariants this market must never violate

- No person / hireability / personality / intelligence score (`FORBIDDEN_SCORES`).
- No sensitive-trait collection, inference, or use (`SENSITIVE_ATTRIBUTES`, `assert_no_sensitive`).
- Missing ≠ bad (`neutral_when_missing`, `missing = None` in matching).
- Commit counts and mentor requests never rank contribution (`FORBIDDEN_CONTRIBUTION_METRICS`).
- Individual disclosure needs a per-scope opt-in (`individual_disclosure_allowed`).
- Employer scope is distinct from investor scope (`VISIBILITY_SCOPES`; none implies another).
- No contact release without mutual opt-in (`release_contact`).
- Matches are retrieval, never hiring decisions (no `overall_score`; `explain` disclaimer).
- The participant must benefit (`participant_opportunity_hub._control`; the fan-out always includes
  `ParticipantValue`).
