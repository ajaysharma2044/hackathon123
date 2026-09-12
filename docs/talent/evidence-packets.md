# The Talent Evidence Packet (Part XVII) + Work-Sample Advantage (Part XVIII)

What an employer actually receives when a participant opts in: a **packet of consented, provenance-
tagged work-evidence** — and, deliberately, nothing else. This document describes the packet as it is
assembled from the code, and the specific advantage the work-sample form has over a resume, LinkedIn,
GitHub, or LeetCode.

Vocabulary: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**;
⚠️ unverified. Missing ≠ bad.

## What the packet contains (Part XVII)

The packet is not a single object with a hidden interior; it is assembled from code constructs, each
of which is individually gated and human-readable:

| Packet section | Source in code | Gate |
|---|---|---|
| Professional profile | `professional_profile` table (display_name, school, program, grad year, portfolio/github/linkedin URLs, desired roles/industries, location preference) | Level C only |
| Per-scope visibility | `professional_visibility` (scope, is_visible, granted_at, revoked_at) | Absence = not visible; revocable any time |
| Opted work-evidence | `work_evidence.evidence_for_scope(evidence, "EMPLOYER")` | Level-C **and** `EMPLOYER` in `consent_scope` |
| Confirmed roles | `work_evidence.ProjectRole` where `is_valid` (team-declared ∧ participant-confirmed) | Participant confirmation required |
| Rendered claims | `work_evidence.render_claim(ev, label, detail)` | Provenance sentence, never a verdict |
| Capability evidence | `capability_graph` output + `profile_capability_evidence` | `SELF_REPORTED` vs `ARTIFACT_SUPPORTED` kept distinct |
| Contribution summary | `work_evidence.contribution_summary(roles, evidence)` | Never ranked by forbidden metrics |

`evidence_for_scope` is the packet's front door: it returns only evidence whose `visible_to("EMPLOYER")`
is true — i.e. `data_level == "C_OPT_IN_PROFESSIONAL"` and `"EMPLOYER" in consent_scope`. Evidence the
participant did not opt into is simply absent from the packet; its absence is never a signal.

A concrete packet, in the shape `render_claim` and `contribution_summary` actually produce (echoing
the illustrative candidate in `docs/products.md`):

```
CANDIDATE (opted into EMPLOYER visibility)
  Profile:  SWE roles · [school/program from professional_profile] · portfolio URL
  Confirmed workstreams:  [BACKEND]                         ← ProjectRole.is_valid only
  Evidence (opted, provenance-tagged):
    • "opted to disclose role ownership; was recorded by the team as the backend workstream"   [TEAM_CONFIRMED]
    • "opted to disclose demo; has an artifact showing a working deployment"                    [ARTIFACT_OBSERVED]
    • "opted to disclose technical decision; has an artifact showing the auth integration"      [ARTIFACT_OBSERVED]
  Capability evidence:
    • BACKEND / API_DESIGN   ARTIFACT_SUPPORTED  ("artifact uses FastAPI")
    • DATABASES / SQL        ARTIFACT_SUPPORTED  ("artifact uses Postgres")
  Contribution note:  "described by confirmed role ownership + artifacts, never ranked by
                       lines of code, commits, hours online, or mentor requests."
```

## What the packet deliberately does NOT contain — no hidden behavioral dossier

The packet has no interior the participant can't see. Specifically excluded, by construction:

- **No person score.** `compliance.FORBIDDEN_SCORES` + `assert_not_a_person_score` block hireability,
  employability, personality, intelligence, `candidate_score`, grit, coachability. None can be
  computed, so none can be in the packet.
- **No sensitive attributes.** `SENSITIVE_ATTRIBUTES` are never collected or inferred; the
  `professional_profile` table has "NO fields for protected/sensitive attributes" (SQL comment).
  `work_authorization` exists only as free text the participant volunteers and controls.
- **No contribution ranking.** `FORBIDDEN_CONTRIBUTION_METRICS` (lines of code, commit count, hours
  online, mentor requests) never appear and never order anything.
- **No Level A/B individual data.** Event-operations and aggregate-research data cannot be
  individually disclosed — `WorkEvidence.visible_to` checks `data_level` first, so only Level-C
  evidence can ever reach an employer.
- **No third-party / longitudinal history.** FCRA confines the packet to first-hand event observation
  (`docs/recruiting-legal.md`: GitHub history, prior events, Club OS longitudinal history are all
  INSIDE FCRA and stay out of the candidate artifact). `LONGITUDINAL_OBSERVED` evidence exists as a
  source kind but belongs to aggregate research, not the individual employer packet.

The packet is exactly the union of what the participant opted to disclose, rendered as human-readable
evidence. There is no shadow profile behind it.

## The packet is revocable and per-scope

Two properties keep the packet under the participant's continuous control:

- **Revocable.** `professional_visibility` carries `granted_at` and `revoked_at`; the SQL comment reads
  "Absence = not visible. Revocable any time." Once a scope is revoked, `individual_disclosure_allowed`
  returns false and `evidence_for_scope("EMPLOYER")` returns nothing — the packet closes.
- **Per-scope, independent.** `compliance.VISIBILITY_SCOPES` are `EMPLOYER, INVESTOR, DESIGN_PARTNER,
  PAID_PROJECT, PUBLIC_PORTFOLIO`, and the docstring states "None implies another." Opting into an
  employer packet does **not** create an investor packet. Because `WorkEvidence.visible_to` checks
  `scope in self.consent_scope`, the same underlying evidence can be in the employer packet and absent
  from the investor packet — the participant decides evidence by evidence, scope by scope. The
  employer scope and the investor scope are genuinely distinct products with distinct packets.

## What the source kinds mean inside the packet

Each evidence line's `source_kind` tells the employer how strong the provenance is, in plain terms
(via `render_claim`'s verb), without being collapsed into a number:

| `source_kind` | Reader should understand |
|---|---|
| `SELF_REPORTED` | the participant states this; not independently confirmed |
| `TEAM_CONFIRMED` | the team recorded this (e.g. a confirmed `ProjectRole`) |
| `ARTIFACT_OBSERVED` | there is an artifact showing it, observed at the event |
| `PUBLIC_REPO` | shown in a public repo the participant chose to surface |
| `PAID_CONTINUATION` | arose from paid follow-on work (Part XXII) |
| `LONGITUDINAL_OBSERVED` | follow-up observation — belongs to aggregate research, kept out of the individual FCRA-scoped packet |

The reader weighs provenance themselves; the system never does it for them.

## The participant sees their own packet

There is no employer view the participant lacks. `talent_matching.participant_side_matches(pv, jobs)`
lets the participant run matching on their own evidence against jobs — and it "works even if the
participant has not opted into EMPLOYER visibility… this is FOR the participant." Combined with the
`participant_opportunity_hub` (which gathers every surfaced opportunity and states "nothing is
auto-shared"), the participant always has at least as much visibility into their packet as any
employer. The packet is a shared artifact, not a one-way dossier.

## Work-sample advantage vs the four alternatives (Part XVIII)

Why observed work-evidence is a different category of signal from each incumbent artifact:

| Artifact | What it is | What it misses | What the packet adds |
|---|---|---|---|
| **Resume** | Self-authored claim list | No provenance; unverifiable | `source_kind` provenance, `artifact_ref`, `verification_method`, team confirmation |
| **LinkedIn** | Self-authored network profile | Same self-report problem, plus endorsements are social, not observed | First-hand event observation with consent recorded in the sentence (`render_claim` opens "opted to disclose …") |
| **GitHub** | Commit history | Commits ≠ owned role; crosses FCRA line as third-party data | Confirmed `ProjectRole` ownership (not inferred from commits — `FORBIDDEN_CONTRIBUTION_METRICS`), inside the FCRA safe harbor |
| **LeetCode / coding assessment** | A score on a synthetic task | A number, no real collaboration, and a regulated "simplified output" | Real collaborative build — `EVIDENCE_TYPES` (role ownership, technical decisions, demo, benchmark) — and **no score at all** (`FORBIDDEN_SCORES`) |

The through-line: the incumbents are either **self-reported** (resume, LinkedIn), **decontextualized**
(GitHub commits, which the code refuses to rank), or **a score** (LeetCode/Karat/CodeSignal, which the
code refuses to emit — and which, as `docs/recruiting-legal.md` establishes, drags an assessment tool
into NYC LL144 / EU AI Act / UGESP the moment it exists). The packet is the one form that is observed,
consented, artifact-anchored, and score-free.

`docs/products.md` states the contrast plainly — a work-evidence pool ("built backend for a 3-person
product; shipped working deployment in 22 hours; owned auth integration; artifact available; opted
in") against "CS student, 3.8 GPA, Python." The employer still makes the hiring decision; the packet
supplies evidence of actual work, "not a score and not a ranking."

## Whether employers pay for the packet

**UNKNOWN.** The work-sample advantage is a design fact; buyer willingness to pay for it is not
established. `docs/STATE.md` marks recruiting as Cluster C ("Recruiting is easy; knowing who can
actually build is hard… real, but crowded — Karat, CodeSignal, HackerRank — and FCRA-constrained")
and notes recruiting may be the easier first check (~$35K cost-to-hire; hackathon hiring ~$5–10K/hire).
A comparable price is not observed WTP; only a signed check settles it.
