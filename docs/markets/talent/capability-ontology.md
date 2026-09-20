# The Capability Ontology + Artifact→Capability Evidence (Parts VI–VIII)

How the system describes *what a participant has experience in* — without ever claiming mastery,
seniority, intelligence, or future performance. Implemented in `engine/capability_graph.py`, backed
by the `capability` and `profile_capability_evidence` tables in `schema/010_talent_venture.sql`.

Vocabulary: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**;
⚠️ for unverified. Missing ≠ bad.

## The ontology (Part VI)

`capability_graph.CAPABILITY_ONTOLOGY` maps each top-level capability to its subskills. It is
extensible by design — the docstring notes "add nodes without touching consumers." The full set as it
exists in code:

```
BACKEND      → API_DESIGN, AUTH, PERSISTENCE, QUEUES, CACHING, DEPLOYMENT
FRONTEND     → UI, STATE_MGMT, PERFORMANCE, ACCESSIBILITY
MOBILE       → IOS, ANDROID, CROSS_PLATFORM
ML           → TRAINING, EVALUATION, INFERENCE, DATA_PIPELINES
LLM          → PROMPTING, AGENTS, RAG, EVAL_HARNESS, FINE_TUNING
DATA_ENGINEERING → ETL, STREAMING, WAREHOUSE, ORCHESTRATION
DATA_SCIENCE → STATISTICS, CAUSAL_INFERENCE, VISUALIZATION
OPTIMIZATION → LP_MIP, HEURISTICS, SIMULATION
ORIE         → STOCHASTIC_MODELING, SUPPLY_CHAIN, SCHEDULING
QUANT        → MARKET_MODELING, BACKTESTING, RISK
SECURITY     → APPSEC, CRYPTO, RED_TEAM
DEVOPS       → CI_CD, OBSERVABILITY, IAC
CLOUD        → AWS, GCP, AZURE, SERVERLESS
DATABASES    → SQL, NOSQL, VECTOR, INDEXING
DISTRIBUTED_SYSTEMS → CONSENSUS, SHARDING, LOW_LATENCY
HARDWARE     → PCB, FIRMWARE, SIGNAL
EMBEDDED     → RTOS, SENSORS, CONTROL
ROBOTICS     → PERCEPTION, CONTROLS, AUTONOMY
PRODUCT      → DISCOVERY, SPEC, USER_RESEARCH
DESIGN       → UX, UI_DESIGN, PROTOTYPING
RESEARCH     → EXPERIMENT_DESIGN, WRITEUP
```

Helpers: `all_capabilities()`, `subskills(capability)`, and `is_capability(code)` — the last returns
true for either a top-level code or any subskill, and is what `job_requirements.JobRequirement`
uses to reject an unknown required capability. In the SQL, `capability.parent_code` encodes the same
parent→subskill relationship (e.g. BACKEND → API_DESIGN).

## Artifact → capability evidence mapping (Part VII)

`capability_graph.TECH_TO_CAPABILITY` maps a technology to a `(capability, subskill)` pair. Presence
of a technology in an artifact **supports experience**, not skill level. The mapping as it exists:

```
fastapi/flask/django → (BACKEND, API_DESIGN)   postgres/postgresql → (DATABASES, SQL)
redis → (BACKEND, CACHING)                      docker/kubernetes → (DEVOPS, IAC)
react/nextjs → (FRONTEND, UI)                   pytorch/tensorflow → (ML, TRAINING)
langchain → (LLM, AGENTS)                       llamaindex → (LLM, RAG)
gurobi/ortools → (OPTIMIZATION, LP_MIP)         simpy → (OPTIMIZATION, SIMULATION)
spark → (DATA_ENGINEERING, ETL)                 kafka → (DATA_ENGINEERING, STREAMING)
aws → (CLOUD, AWS)  gcp → (CLOUD, GCP)          pinecone → (DATABASES, VECTOR)
```

`capabilities_from_technologies(techs)` runs the mapping. Two behaviors are load-bearing:

1. Every result is tagged `"support_kind": "ARTIFACT_SUPPORTED"` with a human note (`"artifact uses
   {t}"`). `test_talent_venture.py` asserts "all tech-derived evidence is artifact-supported."
2. **Unknown technologies are silently skipped, never counted against anyone.** The test
   `capabilities_from_technologies(["FastAPI","Postgres","Redis","unknown_tool"])` confirms
   `unknown_tool` produces no evidence and no penalty ("unknown tech is skipped, never penalized").
   This is the ontology-level expression of *missing ≠ bad*.

## SELF_REPORTED vs ARTIFACT_SUPPORTED (Part VI)

The two support kinds are kept **distinct**, never merged:

- `capabilities_from_technologies(...)` → `support_kind: "ARTIFACT_SUPPORTED"`, note "artifact uses …"
- `self_reported_capability(code)` → `support_kind: "SELF_REPORTED"`, note "self-reported; not
  artifact-verified"

`test_talent_venture.py` pins the distinction: `self_reported_capability("BACKEND")["support_kind"]`
is `"SELF_REPORTED"`. In matching, this distinction has teeth —
`ParticipantEvidenceView.artifact_caps()` returns only the `ARTIFACT_SUPPORTED` capabilities, so
`talent_matching.match` can report `artifact_relevance` separately from overall `capability_coverage`
(which counts all caps). An employer sees which capabilities are backed by an artifact and which are
merely claimed — and the two are never blended into one number.

The SQL enforces the same: `profile_capability_evidence.support_kind` is `SELF_REPORTED |
ARTIFACT_SUPPORTED`, and the table carries a pointed comment: "deliberately NO proficiency_level /
score column: experience evidence, not a rating."

## Artifact evidence ≠ mastery / seniority (Part VIII)

The module docstring is unambiguous: "Artifact evidence supports EXPERIENCE IN an area — it never
proves mastery, seniority, intelligence, or future performance." An artifact using PyTorch supports
"has experience with ML training"; it does not support "is a senior ML engineer," "is smart," or
"will perform well." Those would be:

- **Person scores** — blocked by `compliance.FORBIDDEN_SCORES` / `assert_not_a_person_score`
  (`intelligence`, `person_quality`, etc.).
- **Predictions of future performance** — outside the evidence model entirely; the schema has no
  place to store one.

There is no proficiency level, star rating, or seniority tier anywhere in the ontology, the mapping,
or the storage. The most a capability record ever asserts is: *this artifact used this technology, so
there is experience here.* Seniority, mastery, and aptitude are questions the system is built to
refuse.

## Storage and extensibility

The ontology is backed by two tables in `schema/010_talent_venture.sql`:

- `capability(capability_id, code, parent_code, name)` — `code` is unique (BACKEND, ML, …) and
  `parent_code` encodes the subskill relationship (BACKEND → API_DESIGN), the SQL mirror of
  `CAPABILITY_ONTOLOGY`.
- `profile_capability_evidence(participant_id, capability_code, evidence_id, support_kind, note,
  captured_at)` — links a capability to the `work_evidence` row that supports experience in it, tagged
  `SELF_REPORTED | ARTIFACT_SUPPORTED`. Its FK `evidence_id references work_evidence` keeps every
  capability claim traceable to an actual artifact.

Extensibility is a first-class property. The `CAPABILITY_ONTOLOGY` docstring says "add nodes without
touching consumers," and `TECH_TO_CAPABILITY` says "Extend freely." Because consumers call
`is_capability`, `subskills`, and `capabilities_from_technologies` rather than hard-coding the set,
adding a technology (say a new LLM framework → `(LLM, AGENTS)`) or a whole capability requires no
change to matching, requirements, or storage code. `JobRequirement.__post_init__` picks up new
capabilities automatically through `is_capability`.

## Capabilities vs domains — two separate axes

The ontology describes *what kind of work* (capability); it does not describe *the problem area*
(domain). `JobRequirement` and `ParticipantEvidenceView` both carry `domains` as a separate free field,
matched on its own `domain_relevance` dimension in `talent_matching.match`. In the repo's ML-infra
test the capability is `ML`/`BACKEND` while the domain is `"ml_infra"` — distinct axes that score
independently. The ontology is deliberately not overloaded to carry problem domains.

## Worked example (from `test_talent_venture.py`)

```python
caps = cg.capabilities_from_technologies(["FastAPI", "Postgres", "Redis", "unknown_tool"])
```

produces artifact-supported evidence for `{BACKEND, DATABASES}` (FastAPI→BACKEND/API_DESIGN,
Postgres→DATABASES/SQL, Redis→BACKEND/CACHING), each tagged `ARTIFACT_SUPPORTED`. The test asserts
all three properties at once: the right capabilities appear, every entry is artifact-supported, and
`unknown_tool` is silently skipped rather than penalized. `cg.subskills("BACKEND")` includes
`API_DESIGN`, confirming the ontology carries subskills and is queryable.

## How it feeds the market

```
project artifact (dependency manifest / declared stack)
   └─ capabilities_from_technologies ──▶ [{capability, subskill, support_kind: ARTIFACT_SUPPORTED, note}]
participant self-report
   └─ self_reported_capability ─────────▶  {capability, support_kind: SELF_REPORTED, note}
        │
        └─▶ ParticipantEvidenceView.capabilities
               ├─ all_caps()      → drives capability_coverage
               └─ artifact_caps() → drives artifact_relevance (a distinct dimension)
```

The ontology is the vocabulary; the support-kind tag keeps claimed and demonstrated experience
separate all the way through to the employer-facing match. No node in the ontology, no cell in the
tech map, and no column in either table carries a proficiency level, seniority, or score — the
strongest assertion the whole subsystem can make is "there is experience here."
