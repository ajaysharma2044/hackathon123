-- 005_audience_products.sql
-- ============================================================================
-- THE CORNELL AUDIENCE + PRODUCT + EVENT-1 OPERATING LAYER.
--
-- Event 1 is CORNELL-ONLY: a highly selective, exceptionally good Cornell
-- hackathon. This layer models the specific audience (Cornell student
-- subpopulations), what is uniquely valuable about them (cohort advantage,
-- gated), the full data + qualitative capture surface (maximal legitimate
-- capture WITHOUT surveillance), the commercial product universe (with kill
-- gates), gap-first company research, demand-driven participant selection and
-- team formation, the event-mechanism library, the commercial portfolio, and
-- the client deliverable catalog.
--
-- Composes with 001-004. Same conventions: snake_case, singular tables, uuid
-- PKs named <entity>_id, timestamptz, jsonb snapshots, text[] tags. Uncertain
-- magnitudes are belief references (schema 003) or carry an explicit status;
-- UNKNOWN is valid. Multi-dimensional judgements stay DECOMPOSED, never one
-- score. Every claim about a real company/segment carries provenance.
--
-- HARD ETHICAL BOUNDARIES (carried from capture-risk-register.md, enforced by
-- convention here and in code): NO individual "quality"/intelligence/
-- employability/personality/protected-trait inference or scoring; NO covert
-- capture (keystroke/screen/camera/DM); capture is population-structure +
-- consented + value-exchanged, never surveillance.
-- ============================================================================


-- ---------------------------------------------------------------------------
-- CONTROLLED VOCABULARIES
-- ---------------------------------------------------------------------------

-- The 14 data-universe categories (Part V). Every capturable field belongs to one.
create type data_category as enum (
    'PARTICIPANT_CONTEXT', 'TEAM', 'PROBLEM', 'CHOICE_SET', 'RESOURCE', 'BEHAVIORAL',
    'ECONOMIC', 'PRODUCT_USAGE', 'TECHNICAL', 'ARTIFACT', 'QUALITATIVE', 'OUTCOME',
    'LONGITUDINAL', 'EVENT_OPERATIONS'
);

-- How a field is captured — the axis that separates "not surveillance" from surveillance.
-- SELF_REPORTED / ARTIFACT_DERIVED / BROKERED_TELEMETRY (opt-in tool the participant uses) /
-- ORGANIC_INTERACTION (help request, mentor note) / OPERATIONAL (logistics). No covert modes exist.
create type capture_mode as enum (
    'SELF_REPORTED', 'ARTIFACT_DERIVED', 'BROKERED_TELEMETRY', 'ORGANIC_INTERACTION', 'OPERATIONAL'
);

-- The insight chain (Part VII). Each level is a DISTINCT row type; never collapsed.
create type insight_level as enum (
    'RAW_QUOTE', 'OBSERVATION', 'CODE', 'THEME', 'PATTERN', 'INTERPRETATION', 'RECOMMENDATION'
);

-- Which internal engine consumes a field/asset/product.
create type engine_kind as enum (
    'RESEARCH', 'PRODUCT_DEVELOPMENT', 'RND_PARALLEL_SEARCH', 'ACTIVATION', 'EXPERIMENTATION',
    'SPONSORSHIP', 'DESIGN_PARTNER', 'TALENT', 'QUALITATIVE', 'CAPTURE', 'DECISION'
);

-- Operational behavioral-event vocabulary (Part V behavioral), with strict definitions in code.
create type behavior_event_kind as enum (
    'EXPOSED', 'CONSIDERED', 'ACTIVATED', 'USED', 'REUSED', 'INTEGRATED', 'FAILED', 'ABANDONED',
    'SWITCHED', 'ASKED_FOR_HELP', 'PIVOTED', 'COMPLETED', 'SUBMITTED', 'CONTINUED'
);


-- ---------------------------------------------------------------------------
-- PART I/II — CORNELL AUDIENCE + COHORT ADVANTAGE
-- ---------------------------------------------------------------------------

-- A Cornell student subpopulation, modelled at the POPULATION level (never individuals).
create table audience_segment (
    segment_id            uuid primary key,
    code                  text not null unique,      -- e.g. AI_ML, ORIE_OPTIMIZATION, ECE_HARDWARE, QUANT
    name                  text not null,
    accessible_population_est int,                   -- approx reachable count at Cornell; null = UNKNOWN
    population_status     text not null default 'UNKNOWN',  -- KNOWN | LIKELY | UNKNOWN (of the estimate)
    skills                text[],
    typical_tools         text[],
    buildable_24_48_72    text,                       -- what they can credibly build in a weekend
    strengths             text,
    weaknesses            text,
    resembles_corporate   text,                       -- which corporate audience they resemble
    not_resembles         text,                       -- which they emphatically do NOT resemble
    do_not_use_for        text
);

-- Provenance for a segment's factual claims (population sizes, program existence).
create table audience_evidence (
    evidence_id   uuid primary key,
    segment_id    uuid not null references audience_segment,
    source_url    text,
    source_title  text,
    quote         text,
    observed_at   timestamptz,
    evidence_strength text                            -- KNOWN | LIKELY | UNKNOWN / ⚠️ unverified
);

-- CohortAdvantage = StudentSpecificity x CornellCapabilityFit x Naturalness x BuyerBlindSpot x
-- AlternativeDifficulty (Part II). DECOMPOSED ordinal 0..3; a HARD gate, not an average: if the exact
-- output is obtainable from a normal panel/consultant/the company's own users, the product is killed.
create table cohort_advantage (
    cohort_advantage_id   uuid primary key,
    product_id            uuid,                       -- references product (below); the advantage is per product
    segment_id            uuid references audience_segment,
    student_specificity   int check (student_specificity between 0 and 3),
    cornell_capability_fit int check (cornell_capability_fit between 0 and 3),
    naturalness           int check (naturalness between 0 and 3),   -- occurs naturally in a hackathon?
    buyer_blind_spot      int check (buyer_blind_spot between 0 and 3),
    alternative_difficulty int check (alternative_difficulty between 0 and 3),  -- how hard to get elsewhere
    gate_passed           boolean,                    -- fails if any essential dim is below floor
    note                  text
);


-- ---------------------------------------------------------------------------
-- PART III — PRE-ENTERPRISE DECISION WINDOW (a HYPOTHESIS to test, not assume)
-- ---------------------------------------------------------------------------

create table pre_enterprise_window (
    category              text primary key,           -- a technology/tool/workflow category
    path_dependence       int check (path_dependence between 0 and 3),   -- does an early choice lock in?
    habit_formation       int check (habit_formation between 0 and 3),
    reset_on_entry        int check (reset_on_entry between 0 and 3),     -- 3 = fully reset once at a firm (bad)
    predictive_validity   text not null default 'UNKNOWN',  -- KNOWN | LIKELY | UNKNOWN | CONTRADICTED
    evidence_note         text
);


-- ---------------------------------------------------------------------------
-- PART IV — EVENT ASSET UNIVERSE
-- ---------------------------------------------------------------------------

create table event_asset (
    asset_id              uuid primary key,
    name                  text not null,
    how_generated         text,
    who_values_it         text,
    why_they_value_it     text,
    why_hard_elsewhere    text,
    cohort_advantage_note text,
    required_participants text,
    required_event_design text,
    required_instrumentation text,
    possible_buyer        text,
    possible_budget_belief_id uuid,                   -- references belief (003); UNKNOWN by default
    evidence_strength     text default 'HYPOTHETICAL',
    risks                 text,
    unknowns              text
);


-- ---------------------------------------------------------------------------
-- PART V — DATA UNIVERSE (maximal legitimate capture, NOT surveillance)
-- ---------------------------------------------------------------------------

-- Every field we could legitimately capture. The capture_mode + consent_required + privacy_risk
-- columns are what keep "capture everything" on the right side of surveillance.
create table data_field (
    field_id              uuid primary key,
    category              data_category not null,
    name                  text not null,
    raw_or_derived        text,                       -- RAW | DERIVED
    capture_mode          capture_mode not null,
    how_collected         text,
    when_collected        text,                       -- APPLICATION | ONSITE | CHECKPOINT | POST | 7D | 30D | 90D
    participant_burden    int check (participant_burden between 0 and 3),  -- 0 = zero burden (good)
    consent_required      text[],                     -- consent_scope values (schema 001)
    research_value        int check (research_value between 0 and 3),
    commercial_value      int check (commercial_value between 0 and 3),
    reliability           int check (reliability between 0 and 3),
    bias_note             text,
    privacy_risk          int check (privacy_risk between 0 and 3),  -- 0 = none (good)
    retention_policy      text,
    which_engine          engine_kind,
    is_hard_boundary_violation boolean not null default false  -- must always be false to be buildable
);

-- Operational definition of each behavioral event (Part V insists these not be loose).
create table behavior_definition (
    kind                  behavior_event_kind primary key,
    definition            text not null,              -- the exact operational trigger
    capture_mode          capture_mode not null,
    observable_confidence int check (observable_confidence between 0 and 3)  -- can instrumentation really see it?
);


-- ---------------------------------------------------------------------------
-- PART VI/VII — QUALITATIVE ENGINE + INSIGHT CHAIN
-- ---------------------------------------------------------------------------

-- A qualitative collection method (critical-event prompt, exit interview, 30-day diary, ...).
create table qualitative_method (
    method_id             uuid primary key,
    code                  text not null unique,
    name                  text not null,
    timing                text,                       -- APPLICATION | START | MICRO | SWITCH_TRIGGERED | POST | 7D | 30D | 90D
    signal_quality        int check (signal_quality between 0 and 3),
    participant_burden    int check (participant_burden between 0 and 3),
    bias_note             text,
    sample_size_needed    int,
    best_question_format  text,
    which_engine          engine_kind
);

-- Critical-event sampling frame: which participant/team types to deliberately sample (not just winners).
create table sampling_frame (
    frame_id              uuid primary key,
    label                 text not null,              -- ADOPTER | NON_ADOPTER | SWITCHER | ABANDONER | WINNER | LOSER | ...
    rationale             text,
    target_n              int
);

-- The insight chain (Part VII): each node is one insight_level, with one-directional provenance to
-- the evidence it rests on. RAW_QUOTE/OBSERVATION link to qualitative_observation or evidence_event
-- (schema 001); higher levels link to lower ones. NEVER collapse levels.
create table insight_node (
    node_id               uuid primary key,
    level                 insight_level not null,
    statement             text not null,
    study_id              uuid,                       -- references research_study (001)
    confidence            real check (confidence >= 0 and confidence <= 1),
    interpretation_status text default 'DRAFT',       -- DRAFT | REVIEWED | CLIENT_READY
    model_version_id      text
);

-- Provenance edges of the insight chain (a RECOMMENDATION must trace to PATTERNs to CODEs to QUOTEs).
create table insight_edge (
    parent_node_id        uuid not null references insight_node,   -- the higher-level claim
    child_node_id         uuid not null references insight_node,   -- the evidence it rests on
    primary key (parent_node_id, child_node_id)
);

-- Competing explanations attached to an INTERPRETATION (Part VII forbids single-cause claims).
create table alternative_explanation (
    alt_id                uuid primary key,
    interpretation_node_id uuid not null references insight_node,
    explanation           text not null,
    ruled_out             boolean default false,
    note                  text
);


-- ---------------------------------------------------------------------------
-- PART VIII/IX/XXI — COMMERCIAL PRODUCT UNIVERSE + KILL GATES + CATALOG
-- ---------------------------------------------------------------------------

create table product (
    product_id            uuid primary key,
    name                  text not null,
    engine                engine_kind,
    buyer_problem         text,
    cohort_advantage_note text,
    buyer                 text,
    budget_belief_id      uuid,                       -- references belief (003)
    current_alternative   text,
    hard_to_replicate_why text,
    event_mechanism       text,
    participant_segment   text,
    team_count            int,
    duration              text,
    inputs                text,
    captured_data         text[],
    qualitative_methods   text[],
    artifacts             text[],
    outputs               text[],
    deliverable           text,
    capacity_consumed     text,
    cost_est              numeric,
    price_comparable      text,                       -- cited comparable (research-pricing.md etc.)
    value_ceiling_belief_id uuid,                     -- references belief (003); a CEILING, not WTP
    wtp_status            text not null default 'UNKNOWN',  -- always UNKNOWN until a signed check
    evidence_strength     text default 'HYPOTHETICAL',
    risks                 text,
    is_killed             boolean not null default false,
    kill_reason           text
);

-- The 10 product kill gates (Part IX). A product survives only if EVERY gate passes.
create table product_kill_gate (
    product_id            uuid not null references product,
    gate_number           int not null check (gate_number between 1 and 10),
    gate_question         text not null,
    passed                boolean,
    note                  text,
    primary key (product_id, gate_number)
);

-- Per-product ICP (Part XII): there is no universal ICP.
create table product_icp (
    product_id            uuid not null references product,
    industry              text,
    company_size          text,
    business_model        text,
    technical_maturity    text,
    problem_type          text,
    trigger               text,
    decision_owner        text,
    budget_owner          text,
    spend_signal          text,
    cohort_fit            int check (cohort_fit between 0 and 3),
    urgency               int check (urgency between 0 and 3),
    existing_alternative  text,
    gap_severity          int check (gap_severity between 0 and 3),
    primary key (product_id, industry)
);


-- ---------------------------------------------------------------------------
-- PART XI — GAP-FIRST COMPANY RESEARCH (v2, Cornell-fit aware)
-- ---------------------------------------------------------------------------

create table company_gap (
    company_gap_id        uuid primary key,
    company_id            uuid,                       -- references company (001); null if generic
    company_name          text,
    business_unit         text,
    strategic_priority    text,
    specific_problem      text,
    evidence_url          text,
    economic_magnitude_belief_id uuid,               -- references belief (003)
    current_spend_belief_id uuid,                    -- references belief (003)
    current_solution      text,
    current_vendor        text,
    why_current_fails     text,
    decision_owner        text,
    budget_owner          text,
    trigger               text,
    cornell_cohort_fit    int check (cornell_cohort_fit between 0 and 3),
    hackathon_fit         int check (hackathon_fit between 0 and 3),
    best_product_id       uuid references product,
    price_comparable      text,
    wtp_status            text not null default 'UNKNOWN',
    confidence            text default 'UNKNOWN',     -- KNOWN | LIKELY | UNKNOWN
    reason_to_reject      text,                       -- Part XI: no fit may remain unchallenged
    evidence_strength     text default 'HYPOTHETICAL'
);


-- ---------------------------------------------------------------------------
-- PART XIII/XIV — DEMAND-DRIVEN PARTICIPANT SELECTION + TEAM FORMATION
-- ---------------------------------------------------------------------------

-- Application field registry (Part XIII) — capability/interest, never sensitive traits.
create table application_field (
    field_id              uuid primary key,
    prompt                text not null,
    answer_type           text,                       -- TEXT | MULTI | LINK | SCALE | BOOL
    feeds_segment         text,                       -- which audience_segment it helps classify
    is_sensitive          boolean not null default false  -- must be false to be included
);

-- Demand-driven segment targets: the cohort portfolio REQUIRED by the sold commercial modules.
create table participant_target (
    target_id             uuid primary key,
    portfolio_id          uuid,                       -- references commercial_portfolio (below)
    segment_code          text not null,
    target_count          int,
    reason                text                        -- which module/product demands this segment
);

create table team_formation_method (
    method_id             uuid primary key,
    code                  text not null unique,       -- SELF_SELECTED | ALGO_ASSISTED | RANDOM | PREFORMED | SKILL_COMPLEMENTARY | CHALLENGE_SPECIFIC
    description           text,
    when_to_use           text,
    evidence_note         text
);


-- ---------------------------------------------------------------------------
-- PART XVI/XVII — EVENT-MECHANISM LIBRARY + TWEAK VARIABLES
-- ---------------------------------------------------------------------------

create table event_mechanism (
    mechanism_id          uuid primary key,
    code                  text not null unique,
    name                  text not null,
    purpose               text,
    which_engine          engine_kind,
    what_it_changes       text,
    expected_benefit      text,
    known_risk            text,
    participant_burden    int check (participant_burden between 0 and 3),
    commercial_value      int check (commercial_value between 0 and 3),
    research_validity     int check (research_validity between 0 and 3),
    implementation_cost   int check (implementation_cost between 0 and 3),   -- 0 = cheap (good)
    operational_complexity int check (operational_complexity between 0 and 3), -- 0 = simple (good)
    historical_comparable text,
    evidence_strength     text default 'HYPOTHETICAL'
);


-- ---------------------------------------------------------------------------
-- PART XV/XVIII/XXII — EVENT-1 MODULE, PORTFOLIO, DELIVERABLES
-- ---------------------------------------------------------------------------

-- One client engagement, generated by the module generator (Part XV).
create table event_module (
    module_id             uuid primary key,
    client                text,
    problem               text,
    product_id            uuid references product,
    why_cornell           text,
    target_participants   text,
    target_team_count     int,
    team_composition      text,
    duration              text,
    resources             jsonb,                      -- {resource_kind: amount}
    tools                 text[],
    dataset               text,
    credits               text,
    compute               text,
    mentors               text,
    domain_experts        text,
    company_staff         text,
    information_provided   text,
    information_withheld   text,
    incentives            text,
    prize                 text,
    ip_structure          text,
    data_capture          text[],
    qualitative_plan      text,
    artifact_requirements text,
    evaluation            text,
    follow_up             text,
    deliverable           text,
    capacity_consumed     text,
    participant_burden    int check (participant_burden between 0 and 3),
    risks                 text,
    confidence            text default 'UNKNOWN',
    unknowns              text
);

-- The commercial portfolio chosen for an event (Part XXII): which subset of modules to run under
-- hard constraints (participant-experience floor, open-build floor, capacities, conflicts, consent).
create table commercial_portfolio (
    portfolio_id          uuid primary key,
    event_id              uuid,                       -- references event (001)
    n_participants        int,
    open_build_floor      real,                       -- min fraction of unconstrained building
    experience_floor      real,                       -- min participant-experience score (hard constraint)
    selected_module_ids   uuid[],
    constraints_snapshot  jsonb,
    total_value_note      text,
    model_version_id      text,
    created_at            timestamptz not null default now()
);

-- Client deliverable component catalog (Part XX).
create table deliverable_component (
    component_id          uuid primary key,
    code                  text not null unique,       -- EXECUTIVE_SUMMARY | DECISION_MEMO | SWITCHING_MAP | FAILURE_TAXONOMY | ...
    name                  text not null,
    what_it_answers       text,
    buyer_valued          int check (buyer_valued between 0 and 3),  -- how much buyers actually value it
    requires_qualitative  boolean default false,
    requires_artifacts    boolean default false
);
