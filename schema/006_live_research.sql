-- Builder Network — LIVE RESEARCH OPERATING SYSTEM schema (v006)
-- Postgres flavor. The event-embedded, adaptive, low-friction research layer that runs DURING
-- Event 1. See docs/research-ops/* for the operating model; correctness invariants are executable
-- in engine/live_research.py, research_triggers.py, adaptive_questions.py, adaptive_sampling.py,
-- mentor_routing.py, question_backlog.py, team_trajectory.py, evidence_graph.py, burden_budget.py,
-- intervention_log.py (+ their tests).
--
-- EXTENDS schema/001_core.sql. Reuses its enums (consent_scope, source_kind, evidence_level) and
-- its tables (participant, team, project, event, track, challenge, sponsor, product, opportunity,
-- research_question, qualitative_observation, theme, theme_assignment, evidence_link, finding,
-- follow_up, consent_event). Nothing here is redefined; new objects only.
--
-- GOVERNING INVARIANTS (same spine as 001, specialized for live ops):
--   (1) OBSERVED FACT ≠ INTERPRETATION. A field note stores them in separate columns; an
--       interpretation is never written into the fact column. (Part III)
--   (2) A CLAIM MUST ENUMERATE BOTH supporting AND contradictory evidence before it can be
--       promoted; confidence is a labeled field, never an unbacked adjective. (Part XXVII)
--   (3) EVERY EVENT INTERVENTION IS TIMESTAMPED and carries its validity_impact. (Part XV/XVI)
--   (4) PARTICIPANT BURDEN IS A BUDGET, not a hope — every research touch is a debit row. (Part XVII)
--   (5) NO PERSON SCORE, NO PROTECTED-TRAIT INFERENCE. There is deliberately no quality/employability/
--       personality column anywhere in this file. Observations describe behavior-in-context only. (Part XXXV)
--   (6) Consent is enforced at query time from the 001 ledger; live rows carry consent_scope[] too.

------------------------------------------------------------------------------------------------
-- FIELD RESEARCHER PROGRAM  (Part II) — staffing, shifts, coverage
------------------------------------------------------------------------------------------------
create type researcher_role as enum (
  'FIELD_RESEARCHER',      -- circulates a zone, logs observations, runs short interviews
  'LEAD_RESEARCHER',       -- owns synthesis for a cluster of zones; writes analytic memos
  'INTERVIEWER',           -- runs the deeper triggered/sampled interviews
  'NOTE_SYNTHESIS',        -- codes raw notes → codes/themes in the war room
  'DATA_STEWARD',          -- consent, burden ledger, provenance integrity (no interpretation duty)
  'RESEARCH_OPS_LEAD'      -- runs the war room, the backlog, and sampling allocation
);
create table researcher (
  researcher_id   uuid primary key,
  display_name    text not null,
  role            researcher_role not null,
  trained_codebook_version text,            -- must be set before they may log a coded observation
  affiliation     text,                     -- neutral | sponsor-engineer (conflict flag, see mentor)
  is_neutral      boolean not null default true
);
create table research_shift (
  shift_id        uuid primary key,
  researcher_id   uuid references researcher not null,
  event_id        uuid references event not null,
  starts_at       timestamptz not null,
  ends_at         timestamptz not null,
  zone            text,                      -- physical/logical area they cover this shift
  is_overnight    boolean not null default false,
  check (starts_at < ends_at)
);
create table research_assignment (          -- the coverage map (Part XXI): who watches whom
  assignment_id   uuid primary key,
  researcher_id   uuid references researcher not null,
  team_id         uuid references team not null,
  tier            text not null,            -- PRIMARY | SECONDARY | ROAMING
  last_observed_at  timestamptz,            -- drives "neither ignored nor over-interrupted"
  last_prompted_at  timestamptz,
  last_interviewed_at timestamptz,
  open_trigger_count int not null default 0
);

------------------------------------------------------------------------------------------------
-- FIELD NOTE SYSTEM  (Part III) — observation with FACT ≠ INTERPRETATION enforced by structure
------------------------------------------------------------------------------------------------
create type evidence_status as enum ('RAW','CORROBORATED','CONTRADICTED','SUPERSEDED');
create table observation (
  observation_id  uuid primary key,
  researcher_id   uuid references researcher not null,
  event_id        uuid references event not null,
  occurred_at     timestamptz not null,     -- VALID time (when the observed behavior happened)
  observed_at     timestamptz not null,     -- when the researcher recorded it
  available_at    timestamptz not null,     -- TRANSACTION time (queryable); drives "as of D"
  subject_team    uuid references team,
  subject_participant uuid references participant,   -- grain is usually TEAM, not person
  location        text,
  context         text,                      -- track, stage, team_size, time-remaining snapshot
  -- THE CORE SPLIT (Invariant 1): three distinct columns, never collapsed --------------------
  observed_event  text not null,             -- what was SEEN/HEARD, behaviorally, no inference
  direct_quote    text,                      -- verbatim words, if any (quotation marks in source)
  researcher_interpretation text,            -- the researcher's reading — explicitly labeled as such
  alternative_interpretation text,           -- a competing reading the researcher must also consider
  -- ------------------------------------------------------------------------------------------
  decision_being_made text,                  -- the choice in flight, if this is a decision moment
  tools_or_approaches text[],                -- products/approaches involved
  prior_state     text,
  current_state   text,
  outcome         text,
  trigger_type    text,                      -- mirrors critical_incident.trigger_type (code-versioned taxonomy, not an FK)
  linked_artifact text,
  follow_up_needed boolean not null default false,
  confidence      real not null default 0.7 check (confidence >= 0 and confidence <= 1),  -- <1: inferred
  evidence_status evidence_status not null default 'RAW',
  consent_scope   consent_scope[] not null,
  superseded_by   uuid references observation,
  linked_qual_id  uuid references qualitative_observation,  -- if a quote becomes a raw qual row
  check (num_nonnulls(subject_team, subject_participant) >= 1)
);
create index on observation (subject_team, occurred_at);
create index on observation (trigger_type);
create index on observation (available_at);

------------------------------------------------------------------------------------------------
-- CRITICAL INCIDENT ENGINE  (Part IV) — the versioned trigger taxonomy + detected instances
------------------------------------------------------------------------------------------------
create table incident_type_registry (       -- taxonomy is versioned, like event_type_registry
  trigger_type    text not null,            -- TOOL_SWITCH | ABANDONMENT | REPEATED_HELP_REQUEST ...
  version         int  not null,
  detector        text not null,            -- TELEMETRY | MENTOR | OBSERVER | CHECKPOINT | ARTIFACT | SELF
  ask_question    boolean not null,         -- does this trigger fire a micro-prompt?
  default_prompt_id uuid,                   -- fk set after prompt rows exist
  needs_researcher_followup boolean not null default false,
  participant_burden_sec int not null default 0,   -- expected burden the response costs the participant
  commercial_value text not null,           -- HIGH | MED | LOW — why we care
  primary key (trigger_type, version)
);
create table critical_incident (            -- a detected instance of a trigger
  incident_id     uuid primary key,
  trigger_type    text not null,
  trigger_version int  not null,
  detected_by     text not null,            -- which detector fired
  detected_at     timestamptz not null,
  subject_team    uuid references team,
  subject_participant uuid references participant,
  observation_id  uuid references observation,     -- the note that recorded it, if observer-detected
  evidence_event_id uuid references evidence_event, -- the telemetry row, if telemetry-detected
  prompt_fired    boolean not null default false,
  resolved        boolean not null default false,
  consent_scope   consent_scope[] not null,
  foreign key (trigger_type, trigger_version) references incident_type_registry(trigger_type, version)
);
create index on critical_incident (trigger_type, detected_at);

------------------------------------------------------------------------------------------------
-- ADAPTIVE QUESTION ENGINE  (Part V) — branching question trees + fired prompts
------------------------------------------------------------------------------------------------
create table question_tree (                -- a reusable module: TECHNOLOGY_CHOICE, RD_FAILURE, ...
  tree_id         uuid primary key,
  module          text not null,            -- technology_choice | rd_failure | product_dev | activation ...
  version         int not null default 1,
  root_question_id uuid                     -- fk set after question rows exist
);
create table question (                     -- one node in a tree; reusable across modules
  question_id     uuid primary key,
  tree_id         uuid references question_tree,
  text            text not null,
  answer_kind     text not null,            -- MULTI_CHOICE | SHORT_TEXT | VOICE | SCALE | BRANCH_ONLY
  is_leading_audited boolean not null default false,  -- passed the leading-question review (Part V)
  max_burden_sec  int not null default 30
);
create table question_branch (              -- edge: from a parent answer to the next question
  branch_id       uuid primary key,
  from_question_id uuid references question not null,
  match_answer    text not null,            -- the answer value (or '*' default) that selects this edge
  to_question_id  uuid references question,  -- null = terminal
  rationale       text                      -- why this branch exists (keeps trees auditable)
);
create table prompt (                       -- a micro-prompt INSTANCE actually shown (Part XIX)
  prompt_id       uuid primary key,
  question_id     uuid references question not null,
  subject_team    uuid references team,
  subject_participant uuid references participant,
  incident_id     uuid references critical_incident,   -- the trigger that fired it, if any
  fired_at        timestamptz not null,
  answered_at     timestamptz,
  answer_text     text,
  answer_choice   text,
  skipped         boolean not null default false,       -- skippable is mandatory
  burden_sec      int not null default 0,               -- debited to participant_burden
  consent_scope   consent_scope[] not null
);
alter table incident_type_registry add constraint fk_default_prompt
  foreign key (default_prompt_id) references prompt;

------------------------------------------------------------------------------------------------
-- STRUCTURED CHECKPOINTS  (Part VI) + INTERVIEWS  (targeted, sampled, triggered)
------------------------------------------------------------------------------------------------
create table checkpoint (                   -- START | MIDPOINT | END | FOLLOWUP, minimal + incentive-tied
  checkpoint_id   uuid primary key,
  kind            text not null,            -- START | MIDPOINT | END | FOLLOWUP_7 | FOLLOWUP_30 | FOLLOWUP_90
  subject_team    uuid references team,
  subject_participant uuid references participant,
  occurred_at     timestamptz not null,
  observed_at     timestamptz not null,
  available_at    timestamptz not null,
  payload         jsonb not null,           -- the ≤5 structured answers
  burden_sec      int not null default 0,
  consent_scope   consent_scope[] not null
);
create table interview (                    -- a deeper, sampled/triggered conversation (Part VIII)
  interview_id    uuid primary key,
  interviewer_id  uuid references researcher,
  subject_team    uuid references team,
  subject_participant uuid references participant,
  sampling_reason text not null,            -- why THIS subject now (from adaptive_sampling)
  sampling_segment text,                    -- ADOPTER | NON_ADOPTER | SWITCHER | ABANDONER | R&D_FAILURE ...
  started_at      timestamptz not null,
  ended_at        timestamptz,
  burden_sec      int not null default 0,
  recorded        boolean not null default false,  -- only with explicit consent
  consent_scope   consent_scope[] not null
);
create table interview_excerpt (            -- raw transcript fragment; immutable, kept beside any code
  excerpt_id      uuid primary key,
  interview_id    uuid references interview not null,
  quote           text not null,            -- the participant's actual words
  starts_sec      int, ends_sec int,
  linked_qual_id  uuid references qualitative_observation
);

------------------------------------------------------------------------------------------------
-- QUALITATIVE CODING PIPELINE  (Part XXV) — code layer sits between raw text and theme
------------------------------------------------------------------------------------------------
-- theme + theme_assignment live in 001. A `code` is the finer-grained layer UNDER a theme:
--   RawQuote → Observation → Code → Subtheme → Theme → Pattern → Finding  (each with provenance)
create table code (
  code_id         uuid primary key,
  codebook_version text not null,
  label           text not null,            -- e.g. friction:auth_setup:docs_missing
  subtheme        text,                     -- groups codes into a subtheme
  theme_id        uuid references theme,     -- a code rolls up to a theme (a HYPOTHESIS, not truth)
  definition      text not null
);
create table coding_assignment (            -- applies a code to a raw unit; LLM label + human gate
  coding_id       uuid primary key,
  code_id         uuid references code not null,
  qual_id         uuid references qualitative_observation,
  excerpt_id      uuid references interview_excerpt,
  observation_id  uuid references observation,
  model_version_id text references model_version,      -- if AI first-pass (Part XXVI)
  human_review_state text not null default 'UNREVIEWED', -- UNREVIEWED | CONFIRMED | REJECTED | EDITED
  confidence      real check (confidence >= 0 and confidence <= 1),
  check (num_nonnulls(qual_id, excerpt_id, observation_id) = 1)  -- exactly one raw anchor
);

------------------------------------------------------------------------------------------------
-- LIVE RESEARCH QUESTION BACKLOG  (Part XI) — lifecycle state over 001's research_question
------------------------------------------------------------------------------------------------
create type backlog_status as enum (
  'OPEN','PRIORITIZED','ANSWERED_PARTIALLY','SATURATED','DEPRIORITIZED','CONTRADICTED'
);
create table research_question_backlog (    -- one live row per research_question (001) during the event
  question_id     uuid references research_question primary key,
  client          text,                     -- which buyer/engine cares (separate graph, aggregate only)
  engine          text,                     -- research | rd | product_dev | activation
  priority        int not null default 0,   -- higher = sample toward this next
  status          backlog_status not null default 'OPEN',
  evidence_needed text,
  sample_needed   text,                      -- which segment/coverage gap would move it
  emerged_at      timestamptz not null,      -- initial questions and emergent ones are both here
  is_emergent     boolean not null default false,
  updated_at      timestamptz not null
);

------------------------------------------------------------------------------------------------
-- ANALYTIC MEMOS  (Part XIV) — evolving research state, NOT findings
------------------------------------------------------------------------------------------------
create table analytic_memo (
  memo_id         uuid primary key,
  author_id       uuid references researcher,
  written_at      timestamptz not null,
  question_id     uuid references research_question,
  emerging_pattern text not null,
  supporting_evidence text not null,         -- pointers/counts, never a bare assertion
  contradictory_evidence text not null,      -- REQUIRED field — a memo without this is rejected
  possible_explanation text,
  alternative_explanations text,
  what_we_still_need text,
  who_to_interview text,
  next_question   text,
  confidence      text not null,             -- LOW | MED | HIGH (labeled, honest)
  status          text not null default 'EVOLVING'  -- EVOLVING | STABLE | RETIRED
);

------------------------------------------------------------------------------------------------
-- EVIDENCE GRAPH  (Part XXVII) — claims trace to evidence; contradictions are first-class
------------------------------------------------------------------------------------------------
create table claim (                        -- a client-facing statement UNDER CONSTRUCTION
  claim_id        uuid primary key,
  question_id     uuid references research_question,
  statement       text not null,
  interpretation  text,                      -- the causal/associational reading, hedged
  confidence      text not null default 'LOW',  -- LOW | MED | HIGH; starts LOW
  status          text not null default 'PROPOSED',  -- PROPOSED | SUPPORTED | CONTRADICTED | RETIRED
  promoted_to_finding uuid references finding,  -- a claim becomes a Finding only through the 001 gate
  created_at      timestamptz not null,
  updated_at      timestamptz not null
);
create table claim_evidence (               -- supporting AND contradictory, same table, signed
  claim_id        uuid references claim not null,
  polarity        text not null,            -- 'SUPPORTS' | 'CONTRADICTS'
  observation_id  uuid references observation,
  evidence_event_id uuid references evidence_event,
  interview_excerpt_id uuid references interview_excerpt,
  mentor_interaction_id uuid,               -- fk below
  note            text,
  check (polarity in ('SUPPORTS','CONTRADICTS')),
  check (num_nonnulls(observation_id, evidence_event_id, interview_excerpt_id, mentor_interaction_id) >= 1)
);
create index on claim_evidence (claim_id, polarity);
create table negative_case (                -- Part XIII: the deliberate disconfirmation search
  negative_case_id uuid primary key,
  claim_id        uuid references claim not null,
  disconfirming_question text not null,     -- "what evidence would make this explanation wrong?"
  searched_segment text not null,           -- where we went looking for the counterexample
  found           boolean,                  -- null = search open; true = counterexample exists
  evidence_ref    text,
  recorded_at     timestamptz not null
);

------------------------------------------------------------------------------------------------
-- MENTOR SYSTEM  (Parts VII–IX) — support first, evidence second, confounder tracked
------------------------------------------------------------------------------------------------
create type mentor_intensity as enum ('NONE','LIGHT','MODERATE','HEAVY');  -- defined operationally in engine
create table mentor (
  mentor_id       uuid primary key,
  display_name    text not null,
  category        text not null,            -- GENERAL | FRONTEND | BACKEND | INFRA | DB | AI_ML | AGENTS
                                            --  | DATA | ORIE_OPT | ECE | HARDWARE | ROBOTICS | PRODUCT
                                            --  | DESIGN | DOMAIN | COMPANY_ENGINEER
  affiliation     text,                     -- neutral | <sponsor name>
  is_company_engineer boolean not null default false,   -- the confounder flag (Part VIII)
  sponsor_id      uuid references sponsor
);
create table support_request (              -- the queue (Part IX): operations data first
  request_id      uuid primary key,
  subject_team    uuid references team,
  subject_participant uuid references participant,
  opened_at       timestamptz not null,
  category        text not null,            -- problem category → routes to a mentor category
  priority        int not null default 0,
  assigned_mentor uuid references mentor,
  assigned_at     timestamptz,
  resolved_at     timestamptz,
  resolution_state text                     -- RESOLVED | UNRESOLVED | ESCALATED | WITHDRAWN
);
create table mentor_interaction (           -- the lightweight log (Part VII): target ≤20s to fill
  mentor_interaction_id uuid primary key,
  mentor_id       uuid references mentor not null,
  request_id      uuid references support_request,
  subject_team    uuid references team,
  occurred_at     timestamptz not null,
  observed_at     timestamptz not null,
  available_at    timestamptz not null,
  category        text,
  problem         text,                      -- short
  tool            text,
  state           text,                      -- what state the team was in
  question_asked  text,
  intervention    text,                      -- what the mentor did
  intensity       mentor_intensity not null default 'LIGHT',  -- the confounder measure
  duration_min    int,
  outcome         text,
  follow_up       boolean not null default false,
  research_flag   boolean not null default false,  -- "this is worth a researcher's attention"
  consent_scope   consent_scope[] not null
);
alter table claim_evidence add constraint fk_mentor_interaction
  foreign key (mentor_interaction_id) references mentor_interaction;
create index on mentor_interaction (mentor_id, occurred_at);
create index on support_request (category, resolved_at);

------------------------------------------------------------------------------------------------
-- EVENT ADAPTATION  (Parts XV–XVI) — every material change is logged WITH its validity impact
------------------------------------------------------------------------------------------------
create type validity_impact as enum (
  'NONE',           -- logistics/food; no research effect
  'OPERATIONAL',    -- mentor allocation, office hours; populations before/after differ operationally
  'CONFOUNDING',    -- changes something a study measures; before/after must be split
  'INVALIDATING'    -- touches a pre-registered treatment/outcome/stopping-rule — forbidden unless pre-specified
);
create table event_intervention (
  intervention_id uuid primary key,
  event_id        uuid references event not null,
  occurred_at     timestamptz not null,      -- INVARIANT 3: always timestamped
  reason          text not null,
  evidence        text not null,             -- what signal prompted it (ties to war-room views)
  affected_population text not null,         -- who experiences the change
  change          text not null,
  expected_effect text,
  research_questions_affected uuid[],        -- research_question ids whose before/after must split
  validity_impact validity_impact not null,
  decided_by      uuid references researcher,
  reversible      boolean not null default true
);
create index on event_intervention (event_id, occurred_at);

------------------------------------------------------------------------------------------------
-- TEAM STORY  (Parts XXII–XXIV) — the decision trajectory as a first-class object
------------------------------------------------------------------------------------------------
create table team_trajectory (              -- one per team; assembled from episodes, re-derivable
  trajectory_id   uuid primary key,
  team_id         uuid references team not null,
  model_version_id text references model_version,   -- DERIVED: never hand-edited, always re-derivable
  assembled_at    timestamptz not null
);
create type trajectory_kind as enum ('DECISION','RD_REASONING','PRODUCT_JOURNEY');
create table decision_episode (             -- an ordered node on a trajectory
  episode_id      uuid primary key,
  trajectory_id   uuid references team_trajectory not null,
  seq             int not null,             -- order along the arc
  kind            trajectory_kind not null,
  phase           text not null,            -- PROBLEM_SELECTED | INITIAL_PLAN | TOOL_SET | BLOCKER
                                            --  | HELP | DECISION | SWITCH | PIVOT | ARTIFACT | OUTCOME | CONTINUATION
  behavior        text,                     -- what happened (observed)
  explanation     text,                     -- the "why" (qual, labeled, hedged)
  -- R&D reasoning fields (kind=RD_REASONING): hypothesis → experiment → result → interpretation
  hypothesis      text, why_hypothesis text, experiment text, result text, assumption_failed text,
  -- product-journey fields (kind=PRODUCT_JOURNEY): expectation → friction → workaround → switch
  expectation     text, friction text, workaround text, switched_to text,
  mentor_interaction_id uuid references mentor_interaction,
  artifact_state  text,
  evidence_event_ids uuid[],                 -- provenance to raw
  observation_ids  uuid[],
  unique (trajectory_id, seq)
);

------------------------------------------------------------------------------------------------
-- PARTICIPANT BURDEN BUDGET  (Part XVII) — every research touch is a debit (INVARIANT 4)
------------------------------------------------------------------------------------------------
create type burden_channel as enum (
  'APPLICATION','BASELINE','CHECKPOINT','MICRO_PROMPT','INTERVIEW','MENTOR_LOG_IMPACT',
  'FOLLOWUP','DIARY','ARTIFACT_SUBMISSION'
);
create table participant_burden (           -- append-only ledger; the budget is computed from it
  burden_id       uuid primary key,
  participant_id  uuid references participant not null,
  channel         burden_channel not null,
  seconds         int not null check (seconds >= 0),
  occurred_at     timestamptz not null,
  prompt_id       uuid references prompt,
  interview_id    uuid references interview,
  checkpoint_id   uuid references checkpoint
);
create index on participant_burden (participant_id);
-- The per-participant cap (default ~18 explicit research-minutes, docs/research-ops/participant-burden.md)
-- and the prompt-rate governor are enforced in engine/burden_budget.py, not by a column here.

------------------------------------------------------------------------------------------------
-- INTERRUPTION POLICY  (Part XVIII) — context-aware "is now an OK moment?"
------------------------------------------------------------------------------------------------
create type interrupt_state as enum (
  'DO_NOT_INTERRUPT','MICRO_PROMPT_OK','SHORT_INTERVIEW_OK','DEEP_INTERVIEW_OK'
);
create table team_interrupt_window (        -- current (or scheduled) interruptibility of a team
  team_id         uuid references team not null,
  as_of           timestamptz not null,
  state           interrupt_state not null,
  reason          text,                     -- 'near deadline' | 'meal break' | 'post-switch' | 'judging'
  primary key (team_id, as_of)
);

------------------------------------------------------------------------------------------------
-- RECOMMENDATIONS  (Part XXVII tail) — a recommendation must point at a claim/finding
------------------------------------------------------------------------------------------------
create table recommendation (
  recommendation_id uuid primary key,
  finding_id      uuid references finding,   -- a recommendation rests on a published Finding…
  claim_id        uuid references claim,      -- …or an in-progress Claim (clearly marked)
  text            text not null,
  decision_implication text,
  confidence      text not null default 'LOW',
  created_at      timestamptz not null,
  check (num_nonnulls(finding_id, claim_id) >= 1)   -- never a free-floating recommendation
);

------------------------------------------------------------------------------------------------
-- PARTICIPANT-EXPERIENCE FEEDBACK  (Part XXVIII) — the research system evaluates ITSELF
------------------------------------------------------------------------------------------------
create table experience_pulse (             -- the event is measured from the participant side
  pulse_id        uuid primary key,
  participant_id  uuid references participant,
  occurred_at     timestamptz not null,
  fun             int, freedom int, mentor_usefulness int, flow int,   -- 1..5, all optional
  research_felt_intrusive boolean,
  felt_watched    boolean,
  prompts_annoying boolean,
  free_text       text,
  consent_scope   consent_scope[] not null
);
