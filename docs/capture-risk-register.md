# Capture Risk Register

Every risk in the capture system, classified and mitigated. Severity × likelihood → priority.
`[HR]` items are hard boundaries: not mitigated, not built.

## Methodological

| Risk | Sev | Mitigation | Status |
|---|---|---|---|
| **Underpowered claims at n≈200** presented as findings | High | One well-powered primary study; secondaries observational; evidence-level cap enforced (L1/L2 for most modules); CIs in every finding | Designed ([measurement.md](measurement.md)) |
| **Metric-dial risk** — `activation`/`first-value` tuned post-hoc until the report looks good | High | Operational definitions + `FIRST_VALUE_REACHED` sponsor-defined and **pre-registered** in the `experiment`/`hypothesis` record with `pre_registered_at` timestamp | Encoded (schema) |
| **Theme-frequency ≠ predictive** conflation ("top complaints = top problems") | High | `ThemeFrequency` (L1) is a distinct object from a `Finding` that a theme predicts an outcome (L2+, tested). The system must be able to conclude "pricing complaints frequent but do NOT predict churn; auth friction DOES" | Designed (Part 5) |
| **Silence misread as abandonment** | Med | `TOOL_ABANDONED` is triangulated (brokered silence + checkpoint + dependency delta), never asserted from one source; `confidence<1.0` | Designed |
| **Future-knowledge leakage** into as-of features/decisions | High | `available_at ≤ decision_time` enforced + tested | **Tested** ([engine](../engine/test_capture.py)) |
| **Survey-lag corrupts retention** | High | Survival on `occurred_at`, not `observed_at` | **Tested** |
| **Selection/Hawthorne/prize contamination** read as clean signal | High | Every study states `generalizability_boundary` (schema NOT NULL); context_snapshot on every episode; Part 13 bias model | Encoded |
| **Multi-study contamination** (competing products in one event) | High | Study Compatibility Graph; competitive studies never co-scheduled (Part 16) | Designed |

## Privacy

| Risk | Sev | Mitigation | Status |
|---|---|---|---|
| **Re-identification via small cells** | High | Min-cell-size suppression on every sponsor-facing aggregate | **Tested** |
| **Scope creep** — data used beyond collected purpose | High | Consent enforced at query time by `purpose`; `AGGREGATE_RESEARCH`/`ANONYMIZED_PUBLICATION` are aggregate-only | **Tested** |
| **Request/response bodies captured by the proxy** | High | Proxy stores metadata only (timing/endpoint/status); bodies only for a specific disclosed study with explicit consent; `DataRetentionRule` TTL | Designed (Part 3) |
| **Brokered key outlives consent** | Med | Key destroyed on `PRODUCT_TELEMETRY` revocation | Designed |
| **Individual data leaks to a sponsor** | High | `individual_disclosure()` allowed only for `*_DISCOVERABILITY`; refused for aggregate-only | **Tested** |
| **PII in URL params / cross-service** | Med | Standard: never place personal data in query strings; no data to endpoints suggested by third parties | Policy |

## Legal

| Risk | Sev | Mitigation | Status |
|---|---|---|---|
| **FCRA**: candidate artifact becomes a "consumer report" | High | Work-evidence records contain **first-hand event observation only** — no GitHub history, no Club OS longitudinal data, no third-party data ([recruiting-legal.md](recruiting-legal.md)) | Boundary |
| **NYC LL144 / EU AI Act**: emitting a score = regulated assessment tool | High `[HR]` | **Never emit a score, ranking, tier, or classification** of a person. Structural — no such output object exists in the schema | Boundary |
| **Title VII** employment-agency status ("with or without compensation") | Med | Assume the status; keep selection records; the event connects but does not rank | Boundary |
| **FERPA / GDPR / state privacy** on student longitudinal data | High | Consent scopes + legal read before Event 1 (open item, [data-model.md](data-model.md)); `deletion_tombstone` for erasure | Open — needs counsel |
| **UBIT** if a research deliverable routes through a 501(c)(3) | Med | Two-entity structure; deliverable disclosed to any fiscal sponsor; CPA ([procurement.md](procurement.md)) | Open — needs CPA |
| **ITAR / US-person** limits for defense-category studies | Med | Defense modules priced on US-person headcount; segmented track; hands-on hardware/data off-limits to non-US-persons ([innovation-budget.md](innovation-budget.md)) | Designed |

## Participant experience

| Risk | Sev | Mitigation | Status |
|---|---|---|---|
| **"Flown here to be experimented on"** — the golden-goose failure | High | Research-minutes budget per participant; capture is invisible-but-disclosed or value-adding; the front end must independently be one of the best builder events they can attend ([monetization-map.md](monetization-map.md) extraction frontier) | Designed (Part 14) |
| **Checkpoint fatigue** | Med | ≤60s, ≤5 questions, ~6-hourly, tied to something they want (mentor booking/meals); post-error micro-prompts fire at the natural moment | Designed |
| **Required-exposure resentment** | Med | Required tasks disclosed in challenge terms up front; never covert; ≥1 fully unconstrained track preserved | Designed |
| **Interview burden** | Low | Stratified 30–40, not 200 | Designed |

## Data quality

| Risk | Sev | Mitigation | Status |
|---|---|---|---|
| **Self-report vs observed conflated** | High | `is_self_report` on every event; never merged silently | Encoded |
| **Duplicate / replayed telemetry** | Med | `source_record_id` idempotency | Encoded |
| **LLM theme drift** | Med | `model_version` + `human_review_state` on every assignment; raw text preserved | Encoded |
| **Checkpoint non-response bias** (non-responders are the interesting ones) | High | Incentive-tie; stratified interviews deliberately over-sample never-activated; state the bias in the report | Designed |
| **Follow-up response bias** at 30/90d | High | Incentivized waves; response-bias limitation stated in every retention finding | Boundary |

## Integration

| Risk | Sev | Mitigation | Status |
|---|---|---|---|
| **Sponsor won't provision brokered telemetry** | High | Then they buy activation counts, not research — a stated tier boundary, not a favor to chase | Policy |
| **Proxy can't see SDK/local traffic** | High | Honest capture-mode table (Part 3); fall back to artifact + self-report; never claim telemetry we don't have | `[UNKNOWN]` documented |
| **Competitor telemetry unobtainable** | High | The unconstrained-baseline + switch-away signal come from checkpoints + dependency files, explicitly not telemetry | `[UNKNOWN]` documented |
| **Sponsor telemetry schema varies per product** | Med | `SponsorTelemetryContract.permitted_fields` + a per-product mapper to the neutral schema; mapper is versioned | Designed |

## The hard boundaries (Part 20 — never built, regardless of revenue)

1. No keystroke logging, screen/desktop capture, camera/attention monitoring, or private-message
   scraping. 2. No personality, intelligence, protected-trait, or "quality" inference. 3. No secret
   employability or founder scores/rankings. 4. No raw participant-level data reused for a different
   commercial purpose without explicit scope. 5. No fabricated integrations, prices, demand, or
   statistical power. 6. Revenue never optimized at the cost of participant experience. 7. UNKNOWN
   stays UNKNOWN.
