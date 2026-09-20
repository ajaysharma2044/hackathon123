# The Data Universe — Maximal Capture *Without* Surveillance

> Part V. The goal: capture **as much legitimate signal as possible**, fully structured, while the
> event never *feels like* (or *is*) surveillance. This is a design problem with a clean solution,
> and the repo already carries its first principle ([capture-system.md](capture-system.md)):
> **capture through systems people actually use — not by watching them.**

**Governing rule:** Evidence ≠ Claim ≠ Hypothesis ≠ Decision. Every field below is tagged by how it is
captured; the tag is what keeps "capture everything" on the right side of the line. Enforced in code:
`engine/qualitative.py` (`assert_not_surveillance`, `CAPTURE_HARD_BOUNDARIES`, operational
`BEHAVIOR_DEFINITIONS`) and `engine/capture.py` (consent ledger, aggregate-by-default, min-cell
suppression). Schema: `schema/009_audience_products.sql` (`data_field`, `capture_mode`,
`behavior_definition`).

---

## Why maximal capture here is not surveillance

Surveillance is **covert observation of persons**. We do the opposite on five axes:

1. **Source, not the person.** We read what participants **produce anyway** (repos, dependency
   manifests, submissions) and **tools they opt into** (brokered telemetry) and **interactions they
   start** (help requests) — never their screens, keystrokes, cameras, or private messages.
2. **Consent-first and transparent.** Every scope is granted in an append-only consent ledger
   (`consent_event`, schema 001); capture is disclosed, not hidden. Covert capture is rejected by
   `assert_not_surveillance`.
3. **Value exchange.** Each capture returns something to the participant — a better-matched team, a
   mentor when they're stuck, credits, a portfolio artifact, a job/interview opt-in. Capture that
   only extracts is redesigned or dropped (the "extraction frontier", monetization-map.md).
4. **Aggregate by default, individuals only by explicit opt-in.** Reporting suppresses cells below a
   minimum count (`capture.aggregate`, DEFAULT_MIN_CELL); individual disclosure requires a
   discoverability scope the participant granted.
5. **Outputs, not verdicts about people.** We never infer or emit a person "quality", intelligence,
   employability, personality, or protected-trait score. Those are hard boundaries
   (`CAPTURE_HARD_BOUNDARIES`), never built at any price.

## The five permitted capture modes (there are no covert modes)

| Mode | What it means | Example |
|---|---|---|
| `SELF_REPORTED` | the participant told us | application answers, an exit-interview quote |
| `ARTIFACT_DERIVED` | read off something produced anyway | final dependency manifest, README, submission |
| `BROKERED_TELEMETRY` | a tool they **opted into** emits events | first successful API call (consented, contractual) |
| `ORGANIC_INTERACTION` | an interaction they initiated | a logged mentor/office-hours help request |
| `OPERATIONAL` | event logistics | check-in, room assignment (no behavioral inference) |

## The 14 categories (representative fields — not exhaustive)

Each field in `schema/005 data_field` carries: capture_mode · participant_burden (0=none) · consent
scope · research_value · commercial_value · reliability · privacy_risk (0=none) · retention · engine.

1. **Participant context** — major/field, year, self-reported skill domains, prior tool familiarity,
   builder/founder/research orientation, interest areas. *(SELF_REPORTED, low burden.)* Never:
   personality, intelligence, socioeconomic, protected traits.
2. **Team** — size, formation method, prior relationship, role composition, membership changes,
   division of work. *(SELF_REPORTED + ORGANIC.)*
3. **Problem** — problem selected, mode, reformulations at checkpoints. *(SELF_REPORTED.)*
4. **Choice-set** — options **available / known / considered / tried / rejected / chosen / switched**
   — *choice ≠ preference unless the alternatives are recorded* (schema 002 `choice_set`).
5. **Resource** — time, credits, compute/GPU, API tokens, datasets, mentor/domain-expert minutes,
   hardware. Available vs used vs marginal value (economy.py shadow prices; magnitudes UNKNOWN until
   evidenced).
6. **Behavioral** — the 14 operationally-defined events (EXPOSED … CONTINUED), each with a strict
   trigger and an honest observability confidence (`qualitative.BEHAVIOR_DEFINITIONS`). Never loose.
7. **Economic** — incentives offered/taken, bounties, prizes, transactions (schema 002).
8. **Product-usage** — brokered telemetry from opted-in tools: activation, success/error, reuse.
   *(BROKERED_TELEMETRY, contractual, permitted fields only.)*
9. **Technical** — dependency manifests, APIs integrated, models/DB/cloud/framework selected,
   final stack, removed dependencies, technical pivots. *(ARTIFACT_DERIVED — never claim visibility
   the instrumentation can't provide.)*
10. **Artifact** — repo, README, architecture diagram, prototype, notebook, design/CAD, benchmark,
    pitch/demo. Tag what can be analyzed automatically vs manually.
11. **Qualitative** — the WHY: critical-event prompts, switch/failure-triggered questions, mentor
    field notes, retrospectives, exit interviews, diaries ([qualitative-engine.md](qualitative-engine.md)).
12. **Outcome** — completion, submission, shipped demo, negative results (value of failure),
    decisions changed.
13. **Longitudinal** — opt-in 7/30/90-day continuation, retention, follow-on projects, jobs/ventures.
    *(SELF_REPORTED, explicit opt-in — the compounding-panel signal, and the untested moat engine.)*
14. **Event-operations** — check-in, capacity, room/track, schedule adherence. *(OPERATIONAL.)*

## What we deliberately do NOT capture (hard boundaries)

Keystroke capture · screen recording · camera monitoring · private-message reading · personality /
intelligence / employability inference · protected-trait inference · covert tracking · any person
"quality" score or ranking. These are rejected in code (`CAPTURE_HARD_BOUNDARIES`) regardless of
commercial value.

## The honest limits

- The richest single stream is **brokered telemetry**, and it only exists for tools a sponsor
  instruments and the participant opts into — so coverage is uneven, by design.
- Everything here is **capture capability**, not demand-side value. That a field is capturable does
  **not** mean a buyer will pay for it — WTP stays **UNKNOWN** until a signed check.
- The predictive validity of student behavior for enterprise contexts is itself **UNKNOWN** (see
  [pre-enterprise-window.md](pre-enterprise-window.md)); capturing it cleanly does not make it
  predictive.
