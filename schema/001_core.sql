-- Builder Network — core research capture schema (v001)
-- Postgres flavor. See docs/research-data-model.md for the object model and docs/capture-system.md
-- for the architecture. Correctness invariants enforced in engine/capture.py + tests.
--
-- LAYERS:  registry (definitions) → raw evidence (immutable) → derived (versioned) → business graph
-- INVARIANTS: (1) raw is append-only, corrections use superseded_by; (2) occurred_at ≠ observed_at
--   ≠ available_at; (3) consent enforced at query time from the ledger; (4) every derived row cites
--   its evidence + model_version; (5) no individual-grain sponsor output except *_DISCOVERABILITY.

------------------------------------------------------------------------------------------------
-- REGISTRY / REFERENCE
------------------------------------------------------------------------------------------------
create table event_type_registry (          -- the versioned universal taxonomy (Part 4)
  code            text not null,
  version         int  not null,
  category        text not null,            -- lifecycle | exposure | usage | choice | work | team
                                            --  | research | opportunity | followup | outcome
  is_self_reportable boolean not null default false,
  description     text,
  primary key (code, version)
);

create table participant (
  participant_id  uuid primary key,
  cohort_stratum  text,                     -- technical | founder | product | designer | business
  experience_band text,                     -- for stratification, NOT a quality score
  club_os_ref     text                      -- only usable under LONGITUDINAL_LINKAGE scope
);
create table team    (team_id uuid primary key, event_id uuid not null);
create table project (project_id uuid primary key, team_id uuid references team, event_id uuid);
create table sponsor (sponsor_id uuid primary key, name text not null);
create table tool_category (tool_category_id uuid primary key, name text not null);
create table product (                       -- a tool/product under observation (sponsor OR competitor)
  product_id       uuid primary key,
  name             text not null,
  tool_category_id uuid references tool_category,
  owned_by_sponsor uuid references sponsor   -- null = competitor / neutral tool
);
create table event     (event_id uuid primary key, name text, starts_at timestamptz, ends_at timestamptz);
create table track     (track_id uuid primary key, event_id uuid references event, sponsor_id uuid, is_unconstrained boolean not null default false);
create table challenge (challenge_id uuid primary key, track_id uuid references track, sponsor_id uuid);

create table research_study (
  study_id        uuid primary key,
  sponsor_id      uuid references sponsor,
  title           text,
  target_population text,                    -- Part 13: generalizability is mandatory
  observed_population text,
  sampling_frame  text,
  known_biases    text,
  generalizability_boundary text not null    -- a study cannot be created without stating this
);
create table research_question (question_id uuid primary key, study_id uuid references research_study, text text not null);
create table hypothesis (
  hypothesis_id   uuid primary key,
  question_id     uuid references research_question,
  statement       text not null,
  pre_registered_at timestamptz,            -- pre-registration is a timestamp, not a vibe
  falsification_criteria text not null      -- Part 8: what would prove this wrong
);
create table experiment (experiment_id uuid primary key, hypothesis_id uuid references hypothesis, version int not null);
create table arm (                           -- merges Treatment+Control (data-model.md audit)
  arm_id uuid primary key, experiment_id uuid references experiment,
  is_control boolean not null default false, assignment_is_randomized boolean not null default false
);

create table model_version (model_version_id text primary key, kind text, created_at timestamptz);
create table factor (                        -- the factor registry (Part 9); starts EXPERIMENTAL
  factor_id       text primary key,
  definition      text not null,
  hypothesis      text,
  available_at_rule text not null,           -- when this factor becomes known relative to an entity
  entity          text not null,             -- participant | team | project | product
  permitted_uses  text[] not null,           -- which consent scopes / purposes may use it
  privacy_note    text,
  missingness_policy text not null,
  expected_direction text,
  outcome_target  text,
  status          text not null default 'EXPERIMENTAL',  -- EXPERIMENTAL→VALIDATED→RETIRED
  version         int not null default 1
);

------------------------------------------------------------------------------------------------
-- CONSENT LEDGER  (append-only; effective consent computed as-of query time — Part 7)
------------------------------------------------------------------------------------------------
create type consent_scope as enum (
  'CORE_EVENT','AGGREGATE_RESEARCH','PRODUCT_TELEMETRY','QUALITATIVE_RESEARCH',
  'LONGITUDINAL_FOLLOWUP','RECRUITING_DISCOVERABILITY','VC_DISCOVERABILITY',
  'DESIGN_PARTNER_DISCOVERABILITY','PUBLIC_MEDIA','ANONYMIZED_PUBLICATION','LONGITUDINAL_LINKAGE'
);
create table consent_event (
  consent_event_id uuid primary key,
  participant_id   uuid references participant not null,
  scope            consent_scope not null,
  action           text not null,            -- 'GRANT' | 'REVOKE'
  consent_text_version text not null,
  effective_at     timestamptz not null,     -- when the participant's choice takes effect
  recorded_at      timestamptz not null      -- when we stored it
);
-- Only these scopes may ever produce individual-grain output to an external party:
--   RECRUITING_DISCOVERABILITY, VC_DISCOVERABILITY, DESIGN_PARTNER_DISCOVERABILITY.
-- AGGREGATE_RESEARCH is aggregate-only (min cell size). Enforced in engine/capture.py.

create table deletion_tombstone (            -- legal erasure without corrupting published aggregates
  participant_id uuid references participant, requested_at timestamptz, executed_at timestamptz,
  scope_of_erasure text
);

------------------------------------------------------------------------------------------------
-- RAW EVIDENCE  (immutable, append-only, tri-temporal, consent-tagged)
------------------------------------------------------------------------------------------------
create type source_kind as enum (
  'BROKERED_API','SPONSOR_TELEMETRY','CHECKPOINT','OBSERVER','ARTIFACT',
  'SURVEY','INTERVIEW','FOLLOWUP','SYSTEM','PARTICIPANT_ACTION'
);
create table evidence_event (
  event_id         uuid primary key,
  event_type       text not null,
  event_type_ver   int  not null,
  schema_version   int  not null default 1,
  subject_participant uuid references participant,
  subject_team     uuid references team,
  subject_project  uuid references project,
  product_id       uuid references product,
  sponsor_id       uuid references sponsor,
  study_id         uuid references research_study,
  experiment_id    uuid references experiment,
  arm_id           uuid references arm,
  opportunity_id   uuid,                     -- fk added below
  occurred_at      timestamptz not null,     -- VALID time (survival/retention axis)
  observed_at      timestamptz not null,     -- when first recorded (catches survey lag)
  available_at     timestamptz not null,     -- TRANSACTION time (drives "as of D" queries)
  ingested_at      timestamptz not null,
  source_kind      source_kind not null,
  source           text not null,
  source_record_id text,                     -- idempotency + audit
  is_self_report   boolean not null,         -- SAID vs DID, never conflated
  confidence       real not null default 1.0 check (confidence >= 0 and confidence <= 1),
  consent_scope    consent_scope[] not null, -- scope(s) this was collected under
  raw_payload_ref  text,                     -- pointer to raw store; NO bodies inline by default
  parser_version   text,
  superseded_by    uuid references evidence_event,   -- corrections point forward; original kept
  created_at       timestamptz not null,
  foreign key (event_type, event_type_ver) references event_type_registry(code, version),
  check (num_nonnulls(subject_participant, subject_team, subject_project) >= 1),
  check (occurred_at <= available_at)        -- cannot query a behavior before it is stored
);
create index on evidence_event (subject_participant, occurred_at);
create index on evidence_event (available_at);          -- point-in-time query path
create index on evidence_event (product_id, event_type);

create table opportunity (                   -- Part 10: absence of behavior ≠ inability
  opportunity_id uuid primary key,
  kind           text not null,              -- TOOL_EXPOSURE | MENTOR_SESSION | LEADERSHIP_ROLE
                                             --  | RECRUITER_INTRO | VC_INTRO | DESIGN_PARTNER_INTRO
  offered_to_participant uuid references participant,
  offered_to_team uuid references team,
  offered_at     timestamptz not null,
  response       text,                       -- ACCEPTED | DECLINED | IGNORED | EXPIRED | WITHDRAWN
  responded_at   timestamptz,
  context_snapshot jsonb not null            -- track, stage, team_size, incentives, prior_familiarity
);
alter table evidence_event add constraint fk_opp foreign key (opportunity_id) references opportunity;

-- Brokered instrumentation (Part 3)
create table brokered_credential (
  credential_id uuid primary key, participant_id uuid references participant, team_id uuid references team,
  product_id uuid references product, issued_at timestamptz, revoked_at timestamptz
);
create table sponsor_telemetry_contract (
  contract_id uuid primary key, sponsor_id uuid references sponsor, product_id uuid references product,
  capture_mode text not null,                -- PROXY | SPONSOR_EXPORT | ARTIFACT_ONLY
  permitted_fields text[] not null, retention_ttl_days int not null, signed_at timestamptz
);
create table product_usage_event (           -- raw sponsor/proxy telemetry BEFORE mapping to schema
  usage_id uuid primary key, credential_id uuid references brokered_credential,
  contract_id uuid references sponsor_telemetry_contract,
  occurred_at timestamptz not null, observed_at timestamptz not null, available_at timestamptz not null,
  endpoint text, status_class text, raw_ref text, mapped_event_id uuid references evidence_event
);

-- Qualitative (Part 5): raw text kept forever, beside every extracted label
create table qualitative_observation (
  qual_id uuid primary key, subject_participant uuid references participant, subject_team uuid references team,
  occurred_at timestamptz not null, observed_at timestamptz not null, available_at timestamptz not null,
  source_kind source_kind not null, raw_text text not null, consent_scope consent_scope[] not null
);
create table theme (theme_id uuid primary key, codebook_version text not null, label text not null,
  dimension text);                           -- e.g. friction:authentication_setup
create table theme_assignment (
  qual_id uuid references qualitative_observation, theme_id uuid references theme,
  model_version_id text references model_version, human_review_state text not null default 'UNREVIEWED',
  confidence real, primary key (qual_id, theme_id)
);
create table evidence_link (                 -- quote ↔ behavioral event (the "why" ↔ "what" join)
  qual_id uuid references qualitative_observation, event_id uuid references evidence_event,
  primary key (qual_id, event_id)
);

------------------------------------------------------------------------------------------------
-- DERIVED / INTERPRETATION  (versioned; provenance → raw)
------------------------------------------------------------------------------------------------
create table behavioral_episode (            -- DERIVED reconstruction; never hand-edited
  episode_id uuid primary key, subject_participant uuid, subject_team uuid, product_id uuid references product,
  window_start timestamptz, window_end timestamptz, goal text, goal_confidence real,
  outcome text, context_snapshot jsonb, model_version_id text references model_version,
  event_ids uuid[] not null, qualitative_ids uuid[]
);
create table participant_state (             -- point-in-time state (Part 9); as-of a timestamp
  participant_id uuid references participant, as_of timestamptz, state jsonb,
  model_version_id text references model_version, primary key (participant_id, as_of, model_version_id)
);

-- Research engine outputs (Part 8): raw → observation → claim → hypothesis → test → finding
create type evidence_level as enum ('L1_DESCRIPTIVE','L2_CORRELATIONAL','L3_QUASI_CAUSAL','L4_RANDOMIZED');
create table finding (
  finding_id uuid primary key, question_id uuid references research_question,
  statement text not null, evidence_level evidence_level not null,
  is_experimental boolean not null,          -- observational vs experimental design
  sample_size int, uncertainty text,         -- CI/credible interval, honestly
  model_version_id text references model_version,
  consent_snapshot jsonb not null,           -- consent state + n at publish time (revocation-proof provenance)
  published_at timestamptz
);
create table finding_evidence (              -- the provenance join: a finding MUST enumerate its evidence
  finding_id uuid references finding, event_id uuid references evidence_event,
  primary key (finding_id, event_id)
);
create table finding_limitation   (finding_id uuid references finding, text text not null);
create table finding_contradiction (finding_id uuid references finding, contradicting_finding_id uuid, note text);

-- The decision ledger (Part 11): closes the loop between recommendation and outcome
create table system_decision (
  decision_id uuid primary key, decision_type text, decision_time timestamptz not null,
  entity text, study_id uuid references research_study,
  context_snapshot jsonb, factor_snapshot jsonb, model_version_id text references model_version,
  candidate_actions jsonb, recommended_action text, chosen_action text,
  who_chose text, accepted boolean, override_reason text,
  prediction jsonb, uncertainty text, actual_outcome jsonb, evaluated_at timestamptz
);

-- Follow-up (Part 12)
create table follow_up (
  follow_up_id uuid primary key, participant_id uuid references participant, wave text not null, -- 7d|30d|90d
  method text not null,                      -- AUTO | SURVEY | INTERVIEW
  occurred_at timestamptz, observed_at timestamptz, available_at timestamptz,
  responded boolean, consent_scope consent_scope[] not null
);

------------------------------------------------------------------------------------------------
-- BUSINESS / BUYER GRAPH  (Part 17 + ICP — PHYSICALLY SEPARATE from participant data)
------------------------------------------------------------------------------------------------
create table company (company_id uuid primary key, name text not null, category text, employee_band text, funding_stage text);
create table icp_profile (                   -- dimensions kept visible, never collapsed to one score
  company_id uuid references company primary key,
  pain text, urgency text, cohort_fit text, blind_spot text, decision_value text,
  budget text, buyer_access text, repeatability text, substitution_risk text,
  each_dim_confidence jsonb,                  -- every dimension carries evidence + confidence; default UNKNOWN
  updated_at timestamptz
);
create table trigger (                        -- the reason to call today; decays
  trigger_id uuid primary key, company_id uuid references company,
  kind text not null, observed_at timestamptz, source_url text, decays_at timestamptz
);
create table buyer (buyer_id uuid primary key, company_id uuid references company, title text, department text, budget_authority_est text);
create table pain_point (pain_id uuid primary key, buyer_id uuid references buyer, statement text, source text, current_solution text, current_spend_est text);
create table engagement (
  engagement_id uuid primary key, buyer_id uuid references buyer, module_id text,
  quoted_price numeric, stage text, discount_requested numeric, lost_reason text,
  changed_a_decision boolean, wtp_observed numeric   -- UNKNOWN until a real number appears
);
create table deliverable (deliverable_id uuid primary key, engagement_id uuid references engagement, what_valued text, what_ignored text);
create table renewal (engagement_id uuid references engagement primary key, interest text, size numeric);
