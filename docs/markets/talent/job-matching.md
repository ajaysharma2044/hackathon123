# Job Matching — Decomposed, Explainable, Bidirectional Retrieval (Parts XII–XVI, XLVII, L)

Matching in this system is **evidence retrieval, never a hiring decision**. It produces a decomposed,
explainable set of dimensions with honest unknowns — never a single opaque candidate score.
Implemented in `engine/job_requirements.py` and `engine/talent_matching.py`, stored in the
`job_requirement`, `talent_match`, and `talent_match_evidence` tables.

Vocabulary: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**;
⚠️ unverified. Missing ≠ bad (and here, literally `None`).

## The requirement graph (Part XII)

`job_requirements.JobRequirement` is structural: `title`, `company`, `job_family`, `work_type`
(`INTERNSHIP | NEW_GRAD | FULL_TIME | CONTRACT`), `location`, `required_capabilities`
(capability_code → importance 0..3), `domains`, `technologies`.

Two guards run in `__post_init__`:

1. `compliance.assert_no_sensitive(...)` over **every** structured field — required capabilities,
   domains, technologies, job family, work type. A requirement mentioning any `SENSITIVE_ATTRIBUTE`
   raises `ValueError`. The docstring: requirements "are a retrieval target, never a filter that
   excludes people on protected traits."
2. Each required capability must satisfy `capability_graph.is_capability(cap)` or it raises —
   requirements speak the shared ontology.

`desired_capabilities()` returns capabilities with importance ≥ 1. Importance is "desired, not a hard
exclusion on people" (SQL comment on `job_capability_requirement.importance`).

## The participant view

`talent_matching.ParticipantEvidenceView` holds `opted_scopes` (scope → bool), `capabilities`,
`domains`, `technologies`, `desired_roles`, `location_preference`, `availability`. Key methods:

- `opted(scope)` → `compliance.individual_disclosure_allowed(self.opted_scopes, scope)`.
- `all_caps()` → every capability (self-reported + artifact-supported).
- `artifact_caps()` → only `ARTIFACT_SUPPORTED` capabilities — so demonstrated experience is scored
  separately from merely-claimed experience.

## The decomposed match (Parts XIII–XIV)

`talent_matching.MATCH_DIMS` — seven dimensions, no aggregate:

```
capability_coverage, artifact_relevance, domain_relevance, technology_overlap,
role_preference_fit, location_fit, availability_fit
```

`match(job, pv)` computes each as an ordinal 0–3 (via `_ordinal`) or **`None`** when the input is
missing. The return dict carries the seven dimensions, a `why` list of human reasons, an `unknowns`
list — and, by explicit design, **no `overall_score` key**. The inline comment says it outright:
"deliberately NO 'overall_score' key — retrieval/matching, not a verdict." The `talent_match` table
mirrors this: seven bounded integer columns and "explicitly NO overall_score column."

### Missing = None, never 0 (Part L)

This is the sharpest correctness point. When a signal is absent, the dimension is `None` and a note is
appended to `unknowns` — it is **not** scored 0:

```python
if pv.desired_roles:
    role_fit = 3 if <role matches title/family> else 0
else:
    role_fit = None; unknowns.append("role preference not provided")
```

Same for `location_fit` and `availability_fit`. Coverage/artifact/domain/technology dimensions are
`None` when the *job* specifies nothing to match against (e.g. `cov = ... if desired else None`).
Absence is surfaced honestly and never converted into a penalty — the module docstring: "Missing
evidence is neutral (None), never a penalty (Part L)."

## Explainability (Part XIV)

`explain(m)` renders "why this person appeared": the `why` reasons, then the honest unknowns prefixed
"Unknown (not held against the candidate):", and a closing line that is non-negotiable:

> "This is evidence-based retrieval, not a hiring recommendation."

The `talent_match_evidence` table carries a `why` text per evidence row, so every match dimension is
traceable back to the specific `work_evidence` that supports it.

## Retrieval, not ranking (Part XLVII / Part XXI)

`retrieve(job, participant_views)` returns matches **only** for participants where
`pv.opted("EMPLOYER")` is true — "Never returns non-opted participants." It does not sort, threshold,
or rank; it returns the decomposed match for each opted-in participant and lets the human read the
evidence. Refusing to emit a ranked list is also the legal requirement: a ranked shortlist is a UGESP
"selection procedure" and an LL144 "simplified output" (`docs/recruiting-legal.md`).

## Bidirectional matching (Part XV)

`participant_side_matches(pv, jobs)` runs the same `match` in the other direction — which jobs fit
this participant's demonstrated work. It works **even if the participant has not opted into EMPLOYER
visibility**, because "this is FOR the participant." Direction 1 (employer → candidates) is gated by
opt-in; direction 2 (candidate → jobs) is always available to the participant. The participant is
never worse off for exploring.

## Worked simulation — ML Infra Intern (from `test_talent_venture.py`)

The repo's own test builds and runs this match. Reproduced faithfully:

```python
job = JobRequirement("j1", "ML Infra Intern", job_family="ML Infrastructure",
                     required_capabilities={"ML": 3, "BACKEND": 2}, domains=("ml_infra",),
                     technologies=("pytorch", "docker"))

pv  = ParticipantEvidenceView("p1", opted_scopes={"EMPLOYER": True},
        capabilities=({"capability": "ML",      "support_kind": "ARTIFACT_SUPPORTED"},
                      {"capability": "BACKEND",  "support_kind": "ARTIFACT_SUPPORTED"}),
        domains=("ml_infra",), technologies=("pytorch", "docker"),
        desired_roles=("infrastructure", "ml infra"),
        location_preference="Remote", availability="Summer 2027")

m = tm.match(job, pv)
```

Walking the dimensions:

- `desired = {ML, BACKEND}`; `pv.all_caps() = {ML, BACKEND}` → coverage fraction 1.0 →
  `capability_coverage = 3`. (Test: "full-coverage match scores capability coverage HIGH.")
- `pv.artifact_caps() = {ML, BACKEND}` → `artifact_relevance = 3`. (Test: "artifact relevance is
  scored.")
- `domains`: `{ml_infra} ∩ {ml_infra}` = 1.0 → `domain_relevance = 3`.
- `technologies`: `{pytorch, docker} ∩ {pytorch, docker}` = 1.0 → `technology_overlap = 3`.
- `role_preference_fit`: "ml infra" ∈ "ml infra intern ml infrastructure" → **3**.
- `location_fit`: job has no location, `pv` has "Remote" → **3**.
- `availability_fit`: `pv.availability` set → **3**.
- `why` has ≥ 2 entries (covers ML/BACKEND, artifact-supported experience, role match).
- `unknowns`: empty here — all inputs were provided.

`explain(m)` therefore reads (paraphrasing the generated lines):

```
Match for job j1, participant p1:
  • opted-in evidence covers capabilities: ['BACKEND', 'ML']
  • artifact-supported experience in: ['BACKEND', 'ML']
  • candidate opted into roles matching 'ML Infra Intern'
  This is evidence-based retrieval, not a hiring recommendation.
```

The correct reading of this output is: **"relevant evidence exists; consider for review"** — not
"hire this person." There is no score, no rank, no verdict. `retrieve(job, [pv])` returns exactly this
one candidate because `pv` opted into `EMPLOYER`; a participant who had not opted in would not appear
at all, and their absence would carry no negative meaning.

Contrast a sparser participant: had `pv` omitted `location_preference` and `availability`, those two
dimensions would be `None`, listed under `unknowns` as "not held against the candidate," and the other
five dimensions would be unaffected — missing stays neutral.
