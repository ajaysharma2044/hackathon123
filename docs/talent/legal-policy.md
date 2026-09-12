# Legal & Policy — Constraints the Talent Market Is Built Around

This document maps the legal constraints in `docs/recruiting-legal.md` to the code that enforces them.
Nothing here is derived independently — every legal claim is cited to `docs/recruiting-legal.md`,
which cites primary sources; every enforcement claim is cited to a symbol in `engine/`.

Vocabulary: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**;
⚠️ unverified/secondary. Missing ≠ bad.

## 1. FCRA — first-hand-observation safe harbor

**The constraint** (`docs/recruiting-legal.md`): if you compile information about students and sell it
to employers for hiring decisions, you may become a **consumer reporting agency** (15 U.S.C.
§1681a(f)), and a "consumer report" (§1681a(d)) includes anything bearing on "character, general
reputation, personal characteristics, or mode of living" for employment. The **safe harbor**
(§1681a(d)(2)(A)(i)) excludes a report "solely as to transactions or experiences between the consumer
and the person making the report." Crossing into CRA status triggers permissible-purpose, employer
certification, §1681e(b) accuracy, §1681i dispute, §1681g disclosure, and adverse-action duties.
Precedent: **FTC v. Spokeo, $800,000 civil penalty** (C.D. Cal., 2012).

```
✅ OUTSIDE FCRA   What you directly observed at your own event
❌ INSIDE FCRA    GitHub history · past projects · references · prior events · longitudinal history
```

**The code enforcement.** The A/B/C data levels (`compliance.DATA_LEVELS`; SQL `data_level` enum) are
the firewall. `WorkEvidence.visible_to(scope)` exposes evidence to an employer only when
`data_level == "C_OPT_IN_PROFESSIONAL"`, and Level C carries only first-hand event evidence.
Longitudinal / third-party data lives at Level B (aggregate research) and can never be individually
disclosed. The `professional_profile` table stores `work_authorization` only as participant-controlled
free text and has "NO fields for protected/sensitive attributes." **Status: KNOWN** (the constraint is
sourced to statute; the enforcement is in code).

## 2. Never emit a score — LL144 / EU AI Act / UGESP

**The constraint** (`docs/recruiting-legal.md`): a single rule keeps you outside three regimes at once.

- **NYC Local Law 144** covers an automated employment decision tool producing a "simplified output"
  — score, tag, classification, ranking — that substantially assists hiring (three-prong test,
  6 RCNY §5-300); applies to employers *and employment agencies*; requires annual bias audit, public
  posting, 10 days' notice.
- **EU AI Act Annex III(4)** classifies recruitment/candidate evaluation as high-risk, effective
  **August 2, 2026**, extraterritorial; Article 6(3)'s procedural safe harbor does not cover
  profiling; "human in the loop" is not a reliable escape hatch.
- **UGESP 29 CFR 1607.16** defines a "selection procedure" broadly enough to catch a ranked list,
  shortlist, badge, or tier; the four-fifths rule (29 CFR 1607.4(D)) then applies.

Also live: **Illinois HB 3773** (eff. Jan 1, 2026; bars ZIP as a proxy); **Colorado AI Act** (delayed
to June 30, 2026); **Illinois AI Video Interview Act** (820 ILCS 42). ⚠️ The EEOC's May 2023 AI
technical-assistance document has been removed from eeoc.gov, but the underlying statute and UGESP are
unchanged and enforceable.

> "Publish artifacts and human-written narrative. Never a score, ranking, tier, or classification."

**The code enforcement.** No score exists, by construction:
- `compliance.FORBIDDEN_SCORES` + `assert_not_a_person_score` block hireability, employability,
  personality, intelligence, `candidate_score`, `overall_candidate_score`, grit, coachability.
- `talent_matching.match` returns **no `overall_score`** (inline comment: "retrieval/matching, not a
  verdict"); `talent_match` table has "explicitly NO overall_score column."
- `retrieve` does not rank or threshold; `explain` ends "This is evidence-based retrieval, not a
  hiring recommendation."
- `FORBIDDEN_CONTRIBUTION_METRICS` blocks any ranking by commits/LOC/hours/mentor-requests.

**Status: KNOWN** (constraint sourced; the system emits no simplified output anywhere).

## 3. Title VII employment-agency status

**The constraint** (`docs/recruiting-legal.md`): 42 U.S.C. §2000e(c) defines an employment agency as
anyone "regularly undertaking **with or without compensation** to procure employees for an employer."
A free event that regularly connects students to employers can be a Title VII employment agency —
charging a fee does not create the exposure; it already exists. No case law was found applying this to
a student event or online talent platform — legally untested, which "cuts both ways."

**Design response** (rule 7): assume employment-agency status regardless and keep selection records.
The code keeps decomposed, traceable match records (`talent_match` + `talent_match_evidence` with a
`why` per evidence) rather than opaque decisions — consistent with keeping defensible selection
records while emitting no selection *procedure*. **Status: LIKELY** the status applies; **UNKNOWN**
whether any court would so hold (untested).

## 4. Who-pays licensing — never take a dollar from a student

**The constraint** (`docs/recruiting-legal.md`): most state employment-agency statutes target agencies
charging **jobseekers**.

- **California** Civ. Code §1812.501 — agency acts for a fee "to be paid… by a jobseeker."
- **Massachusetts** G.L. c.140 §46A — excludes a firm "none of whose fees or charges are paid… by any
  applicant for employment."
- **New York** GBL §171 — recognizes an "employer fee paid employment agency"; NYC DCWP confirms
  employer-fee-paid agencies placing professionals are exempt from the NYC license; GBL §171 also
  exempts bona fide nonprofit educational/charitable organizations.

> "Never take a dollar from a student. That is the trigger in nearly every state."

41 states require an employment-services license; 9 do not (DE, GA, ID, MD, MS, MO, OH, PA, SD).
**You must comply with the state where the worker is placed** — MIT/Stanford/Berkeley/CMU students get
placed in CA, NY, MA, WA. An unlicensed agency's fee contract is generally void and unenforceable.

**The code enforcement.** The employer is always the paying side. The participant-facing surfaces are
purely benefit: `participant_opportunity_hub` ("nothing is auto-shared"), `participant_side_matches`
("this is FOR the participant"), and the fan-out always includes `ParticipantValue`. There is no code
path that charges a participant. **Status: KNOWN.**

## 5. Placement / success-fee caution — `opportunity_market.MONETIZATION`

**The constraint** (`docs/recruiting-legal.md`): "The per-hire fee: legal, but commercially dead."
Every marketplace that pioneered per-hire pricing for engineers is gone or converted (Hired, Vettery,
Triplebyte); the student market never used per-hire fees; Parker Dewey charges **no conversion fee**
and sells subscription ($5,000 pilot, $7,500–$15,000/yr); no elite student community charges a
per-hire fee across seven checked. Contingency norm if unavoidable: flat **$5K–$20K/hire**,
employer-paid, licensed in placement states.

**The code enforcement.** `opportunity_market.MONETIZATION` encodes exactly these statuses:

| Kind | Status | Note (verbatim) |
|---|---|---|
| `TALENT_ACCESS_SUBSCRIPTION` | **ALLOWED** | "access/subscription, not per-hire — the safer structure" |
| `EVENT_SPONSORSHIP` | **ALLOWED** | "standard event sponsorship" |
| `RECRUITING_PARTNERSHIP` | **NEEDS_LEGAL** | "placement/success fees may implicate employment-agency law (see recruiting-legal.md)" |
| `PLACEMENT_SUCCESS_FEE` | **NEEDS_LEGAL** | "per-hire success fees are legal but commercially weak and regulated; validate first" |
| `PAID_PROJECT_FACILITATION` | **NEEDS_LEGAL** | "clarify IP + worker classification before facilitating paid work" |
| `INVESTMENT_SUCCESS_FEE` | **FORBIDDEN_UNTIL_COUNSEL** | "taking a % of capital raised can be broker-dealer activity (securities law); do NOT until counsel confirms" |

`assert_monetization_allowed(kind)` **raises `PermissionError`** for `FORBIDDEN_UNTIL_COUNSEL` and
returns the status otherwise — a hard code gate, not a comment. (The forbidden case is investment
success fees, a venture-side concern; on the talent side the success-fee kinds are NEEDS_LEGAL, i.e.
allowed only after validation.) **Status: KNOWN** for the code behavior; the commercial claim that
per-hire pricing is "dead" is sourced to `recruiting-legal.md`.

## 6. High-impact fairness guardrail — no autonomous decision, no protected traits

Recruiting is a high-impact domain: an error can deny someone a job. The system's guardrails match
that stakes level:

- **No autonomous hiring decision.** The system retrieves and explains evidence; it never decides. No
  `overall_score`, no ranking, `explain` disclaimer, and design rule 5 ("The sponsor makes and
  documents every hiring decision"). A human is always the decision-maker — and, per the EU AI Act
  note, the point is not to lean on "human in the loop" as a shield but to genuinely never emit the
  simplified output that would make the tool the decider.
- **No protected traits.** `SENSITIVE_ATTRIBUTES` (race, gender, religion, disability, age, veteran
  status, socioeconomic, and more) are never collected, inferred, or used. `assert_no_sensitive` vets
  every `JobRequirement` field at construction and every profile/job schema. ZIP-as-a-proxy (Illinois
  HB 3773) is avoided because location enters only as a coarse participant-provided
  `location_preference`, never a demographic proxy.
- **Missing ≠ bad.** `neutral_when_missing` and `missing = None` in matching guarantee absence is
  never a penalty — an important fairness property, since data gaps correlate with disadvantage.

**Status: KNOWN** for enforcement. **WTP for the whole talent product remains UNKNOWN** — legality is
necessary, not sufficient; only a signed check settles demand (`docs/STATE.md`).

## Source of truth

All legal claims: `docs/recruiting-legal.md` (which links primary sources — 15 U.S.C. §1681a, FTC v.
Spokeo, 42 U.S.C. §2000e, 29 CFR 1607, EU AI Act Annex III/Art. 6, NYC LL144, CA §1812.501, MA c.140
§46A, NY GBL §171, Parker Dewey, Wellfound). All enforcement claims: `engine/compliance.py`,
`engine/talent_matching.py`, `engine/work_evidence.py`, `engine/opportunity_market.py`,
`engine/job_requirements.py`, `engine/mutual_intro.py`, `schema/010_talent_venture.sql`.
