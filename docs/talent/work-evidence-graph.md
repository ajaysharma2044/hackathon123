# The Work-Evidence Graph (Parts II–XI)

What the event produces that a resume cannot: a **graph of evidence with provenance**, never a
hidden person score. This document describes the graph as implemented in `engine/work_evidence.py`
and `schema/010_talent_venture.sql`.

Vocabulary: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**;
⚠️ for unverified. Missing ≠ bad.

## Why a graph and not a score

The module docstring states the design: "This models that evidence as a traceable GRAPH — never a
hidden person score." Every professional claim is traceable to an artifact + source + consent
(`schema/010_talent_venture.sql` header). The system produces decomposed, explainable evidence —
`compliance.assert_not_a_person_score` exists specifically to raise if any code ever tries to emit a
`candidate_score`, `hireability`, or similar.

## Evidence types (Part III)

`work_evidence.EVIDENCE_TYPES` — 20 legitimate professional evidence types, mirrored exactly in the
SQL `evidence_type` enum:

```
ROLE_OWNERSHIP, PROJECT_ARTIFACT, CODE_ARTIFACT, DESIGN_ARTIFACT, MODEL_ARTIFACT,
DATA_ARTIFACT, OPTIMIZATION_ARTIFACT, HARDWARE_ARTIFACT, DOCUMENTATION, DEMO,
TECHNICAL_DECISION, EXPERIMENT, BENCHMARK, PROBLEM_DOMAIN, TOOL_EXPERIENCE,
TEAM_SELECTED_CONTRIBUTION, SELF_REPORTED_CONTRIBUTION, CONTINUATION, PAID_CONTINUATION,
OPEN_SOURCE_CONTRIBUTION
```

Note what is **absent**: there is no trait, quality, personality, or aptitude type. The SQL comment
is explicit — "No trait/quality types exist." `WorkEvidence.__post_init__` raises `ValueError` on any
type outside this tuple, so an ad-hoc "grit" or "star performer" type cannot be recorded at all.

## Provenance — the source-kind axis (Part XLIX)

Every `WorkEvidence` carries a `source_kind` from `compliance.EVIDENCE_SOURCE_KINDS`:

```
SELF_REPORTED, TEAM_CONFIRMED, ARTIFACT_OBSERVED, PUBLIC_REPO, PAID_CONTINUATION, LONGITUDINAL_OBSERVED
```

The SQL comment on the `evidence_source_kind` enum states the rule: source is "Stored separately; NOT
auto-ranked into a score." Reliability of a source is visible to a human reader and is **never**
folded into a numeric confidence verdict about the person. `WorkEvidence.confidence` exists as a real
in [0,1], but it is a per-evidence field with a check constraint — never aggregated across evidence
into a candidate rating, and never exposed as such by any function in the module.

The full `WorkEvidence` record (dataclass and `work_evidence` table):

| Field | Role |
|---|---|
| `type` | one of `EVIDENCE_TYPES` |
| `source_kind` | one of `EVIDENCE_SOURCE_KINDS` |
| `participant_id` / `team_id` / `project_id` | graph edges into 001-core entities |
| `artifact_ref` | link to the artifact (traceability) |
| `verification_method` | how it was checked |
| `consent_scope` | which visibility scopes expose it (empty ⇒ Level A/B only) |
| `data_level` | A / B / C; default `A_EVENT_OPERATIONS` |
| `is_public` / `participant_confirmed` | disclosure + confirmation flags |

## Role ownership — team-declared AND participant-confirmed (Parts X–XI)

`ProjectRole` is an **opt-in ownership record**. Its `is_valid` property is the whole point:

```python
@property
def is_valid(self) -> bool:
    return self.declared_by_team and self.confirmed_by_participant
```

Both conditions are required. The team declares who owned what; the participant must confirm their
own record. `test_talent_venture.py` pins this: a `ProjectRole` that is `declared_by_team=True` but
not confirmed has `is_valid is False`. Ownership is therefore never assigned to someone without their
confirmation, and never inferred from activity.

## Why commit counts are refused (Part XI)

`work_evidence.FORBIDDEN_CONTRIBUTION_METRICS`:

```python
FORBIDDEN_CONTRIBUTION_METRICS = ("lines_of_code", "commit_count", "hours_online", "mentor_requests")
```

These are named explicitly "so the guardrail tests can assert the system exposes no ranking over
them." `contribution_summary(roles, evidence_list)` returns only confirmed workstreams and the set of
evidence types present — plus a `note` stating contribution is "described by confirmed role ownership
+ artifacts, never ranked by lines of code, commits, hours online, or mentor requests." There is no
code path that sorts, scores, or ranks participants by any of the four.

Two of these deserve emphasis:

- **Commit count / lines of code** reward volume and disadvantage the person who wrote the hard 40
  lines, refactored, or drove design. Ranking on them would manufacture a false contribution
  hierarchy.
- **Mentor requests** are *support*, not evidence for sale. `opportunity_market.ACTIVITY_FANOUT`
  routes `MENTOR_REQUEST` to `ParticipantValue`, `OperationalValue`, `ResearchValue`, `CommercialValue`
  — and pointedly **never** to `HiringValue` or `VentureValue`. Asking for help must never become a
  hiring signal.

## Missing ≠ bad (Part L)

`contribution_summary` returns `confirmed_workstreams: []` with the inline note "empty is fine —
missing != bad." `evidence_for_scope` simply omits evidence a participant did not opt into: "Missing
evidence simply is not returned — it is NEVER converted into a negative signal." The absence of
evidence is never a penalty anywhere in the graph.

## Claim vs evidence rendering (Part IV)

`render_claim(ev, participant_label, detail)` renders evidence as an **evidence-with-provenance
statement**, never a trait judgement. The verb is chosen from the source kind:

| `source_kind` | verb phrase |
|---|---|
| `SELF_REPORTED` | "states" |
| `TEAM_CONFIRMED` | "was recorded by the team as" |
| `ARTIFACT_OBSERVED` | "has an artifact showing" |
| `PUBLIC_REPO` | "has a public repo showing" |
| `PAID_CONTINUATION` | "was engaged for paid continuation involving" |
| `LONGITUDINAL_OBSERVED` | "was observed at follow-up to have" |

The output template always opens with "{label} opted to disclose {evidence type}; …" — consent is
part of the sentence.

**Good (produced by the code):**
> "Ajay opted to disclose role ownership; Ajay was recorded by the team as the backend workstream
> (FastAPI/Postgres)."

**Bad (the code will never produce, and the docstring names as the anti-pattern):**
> "Ajay is an excellent backend engineer."

`test_talent_venture.py` asserts the good shape directly: the rendered claim contains "opted to
disclose" and does **not** contain "excellent". The distinction — descriptive evidence vs a quality
verdict — is also the legal line in `docs/recruiting-legal.md` ("Publish artifacts and human-written
narrative. Never a score, ranking, tier, or classification").

## The graph, end to end

```
project ──ProjectRole (declared_by_team ∧ confirmed_by_participant)──▶ participant
   │
   └─ WorkEvidence { type ∈ EVIDENCE_TYPES, source_kind ∈ EVIDENCE_SOURCE_KINDS,
                     artifact_ref, verification_method, consent_scope, data_level, confidence }
          │
          ├─ render_claim ──▶ evidence-with-provenance sentence (never a trait verdict)
          ├─ evidence_for_scope(EMPLOYER) ──▶ only opted, Level-C evidence
          └─ contribution_summary ──▶ { confirmed_workstreams, evidence_types_present, note }
                                       (never ranked by FORBIDDEN_CONTRIBUTION_METRICS)
```

The product is the graph. There is no score node, by construction.
