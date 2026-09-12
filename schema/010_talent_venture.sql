-- 010_talent_venture.sql
-- ============================================================================
-- TALENT MARKET + VENTURE MARKET — opt-in downstream consumers of naturally
-- produced event work-evidence. NOT a recruiting product bolted on the side.
--
-- Non-negotiable, enforced by convention here and by code in engine/work_evidence.py:
--   * THREE data levels kept separate: A event-operations (never individually
--     disclosed), B aggregate research (population/team, not a dossier),
--     C opt-in professional discoverability (participant explicitly makes
--     defined work-evidence visible to employers / investors / design partners).
--   * NO person scores of any kind: no hireability, founder-quality, personality,
--     intelligence, or protected/sensitive-trait inference. The work-evidence
--     GRAPH is the product, never a score.
--   * Employer/investor visibility is a SEPARATE opt-in per scope; no contact
--     disclosure without mutual opt-in. Missing evidence is never negative.
--   * Every professional claim is traceable to an artifact + source + consent.
--
-- Composes with 001-009. Reuses participant/team/project/artifact from 001 (does
-- NOT duplicate them). Same conventions: snake_case, uuid PKs, timestamptz.
-- ============================================================================


-- ---------------------------------------------------------------------------
-- CONTROLLED VOCABULARIES
-- ---------------------------------------------------------------------------

-- The three data levels (Part I). A field/record is tagged with the highest level
-- it may ever reach; C requires an explicit, scope-specific opt-in.
create type data_level as enum (
    'A_EVENT_OPERATIONS',            -- run the event; never individually disclosed externally
    'B_AGGREGATE_RESEARCH',          -- population/team-level; not an individual dossier
    'C_OPT_IN_PROFESSIONAL'          -- participant chose to expose defined work-evidence
);

-- Separate opt-in visibility scopes (Part LI). Each is independent; none implied by another.
create type visibility_scope as enum (
    'EMPLOYER', 'INVESTOR', 'DESIGN_PARTNER', 'PAID_PROJECT', 'PUBLIC_PORTFOLIO'
);

-- Legitimate professional evidence types (Part III). No trait/quality types exist.
create type evidence_type as enum (
    'ROLE_OWNERSHIP', 'PROJECT_ARTIFACT', 'CODE_ARTIFACT', 'DESIGN_ARTIFACT', 'MODEL_ARTIFACT',
    'DATA_ARTIFACT', 'OPTIMIZATION_ARTIFACT', 'HARDWARE_ARTIFACT', 'DOCUMENTATION', 'DEMO',
    'TECHNICAL_DECISION', 'EXPERIMENT', 'BENCHMARK', 'PROBLEM_DOMAIN', 'TOOL_EXPERIENCE',
    'TEAM_SELECTED_CONTRIBUTION', 'SELF_REPORTED_CONTRIBUTION', 'CONTINUATION', 'PAID_CONTINUATION',
    'OPEN_SOURCE_CONTRIBUTION'
);

-- Evidence reliability SOURCE (Part XLIX). Stored separately; NOT auto-ranked into a score.
create type evidence_source_kind as enum (
    'SELF_REPORTED', 'TEAM_CONFIRMED', 'ARTIFACT_OBSERVED', 'PUBLIC_REPO',
    'PAID_CONTINUATION', 'LONGITUDINAL_OBSERVED'
);

-- Evidence epistemic status for venture material claims (Part XXXIV).
create type claim_status as enum ('OBSERVED', 'SELF_REPORTED', 'ASSUMED', 'UNKNOWN');

-- Cross-market transaction types (Part XLIV).
create type opportunity_transaction as enum (
    'INTERVIEW', 'JOB', 'INTERNSHIP', 'PAID_PROJECT', 'DESIGN_PARTNERSHIP',
    'RD_CONTINUATION', 'CUSTOMER_INTRO', 'VC_INTRO', 'ACCELERATOR_INTRO'
);


-- ---------------------------------------------------------------------------
-- WORK-EVIDENCE GRAPH (Parts II-IV, IX) — the product itself, not a score
-- ---------------------------------------------------------------------------

-- Opt-in team declaration of who owned what (Part X). Participants CONFIRM their own
-- record; ownership is NEVER inferred from commit counts (Part XI).
create table project_role (
    project_role_id       uuid primary key,
    project_id            uuid,               -- references project (001)
    participant_id        uuid,               -- references participant (001)
    workstream            text not null,      -- e.g. BACKEND, MODEL, FRONTEND, PRODUCT, HARDWARE
    declared_by_team      boolean default false,
    confirmed_by_participant boolean default false,
    note                  text
);

-- A single piece of professional evidence, always traceable, always consented.
create table work_evidence (
    evidence_id           uuid primary key,
    participant_id        uuid,               -- references participant (001); null for team-level
    team_id               uuid,               -- references team (001)
    project_id            uuid,               -- references project (001)
    type                  evidence_type not null,
    source_kind           evidence_source_kind not null,
    artifact_ref          text,               -- references artifact (001) or a URL
    verification_method   text,
    consent_scope         visibility_scope[], -- which opt-ins expose this; empty = level A/B only
    data_level            data_level not null default 'A_EVENT_OPERATIONS',
    confidence            real check (confidence >= 0 and confidence <= 1),
    is_public             boolean default false,
    participant_confirmed boolean default false,
    occurred_at           timestamptz,
    captured_at           timestamptz not null default now()
);


-- ---------------------------------------------------------------------------
-- CAPABILITY ONTOLOGY + ARTIFACT->CAPABILITY EVIDENCE (Parts VI-VIII)
-- ---------------------------------------------------------------------------

create table capability (
    capability_id         uuid primary key,
    code                  text not null unique,     -- BACKEND, ML, OPTIMIZATION, ...
    parent_code           text,                     -- for subskills (BACKEND -> API_DESIGN)
    name                  text not null
);

-- Maps a piece of evidence to a capability it SUPPORTS EXPERIENCE IN (not mastery).
create table profile_capability_evidence (
    id                    uuid primary key,
    participant_id        uuid,               -- references participant (001)
    capability_code       text not null,      -- references capability.code
    evidence_id           uuid references work_evidence,
    support_kind          text not null,      -- SELF_REPORTED | ARTIFACT_SUPPORTED
    note                  text,               -- e.g. "repo uses FastAPI + Postgres + Redis"
    -- deliberately NO proficiency_level / score column: experience evidence, not a rating
    captured_at           timestamptz not null default now()
);


-- ---------------------------------------------------------------------------
-- OPT-IN PROFESSIONAL PROFILE (Part V) — level C only
-- ---------------------------------------------------------------------------

create table professional_profile (
    participant_id        uuid primary key,   -- references participant (001)
    display_name          text,
    school                text,
    program               text,
    graduation_year       int,
    portfolio_url         text,
    github_url            text,
    linkedin_url          text,
    website_url           text,
    desired_roles         text[],
    desired_industries    text[],
    desired_employment_type text,
    location_preference   text,
    -- NO fields for protected/sensitive attributes; work_authorization only if the
    -- participant volunteers it and is stored as free text they control.
    work_authorization    text,
    updated_at            timestamptz not null default now()
);

-- Per-scope visibility switches (Part LI). Absence = not visible. Revocable any time.
create table professional_visibility (
    participant_id        uuid not null,      -- references participant (001)
    scope                 visibility_scope not null,
    is_visible            boolean not null default false,
    granted_at            timestamptz,
    revoked_at            timestamptz,
    primary key (participant_id, scope)
);


-- ---------------------------------------------------------------------------
-- TALENT MARKET (Parts XII-XXIV)
-- ---------------------------------------------------------------------------

create table job_requirement (
    job_id                uuid primary key,
    company_id            uuid,               -- references company (001)
    title                 text,
    job_family            text,
    work_type             text,               -- INTERNSHIP | NEW_GRAD | FULL_TIME | CONTRACT
    location              text,
    employment_type       text,
    hiring_manager        text,
    -- NO sensitive-attribute columns, by design
    posted_at             timestamptz
);

create table job_capability_requirement (
    job_id                uuid not null references job_requirement,
    capability_code       text not null,      -- references capability.code
    importance            int check (importance between 0 and 3),  -- desired, not a filter on people
    primary key (job_id, capability_code)
);

-- A retrieval match, kept DECOMPOSED (Part XIII) — never a single candidate score.
create table talent_match (
    match_id              uuid primary key,
    job_id                uuid references job_requirement,
    participant_id        uuid,               -- references participant (001)
    capability_coverage   int check (capability_coverage between 0 and 3),
    artifact_relevance    int check (artifact_relevance between 0 and 3),
    domain_relevance      int check (domain_relevance between 0 and 3),
    technology_overlap    int check (technology_overlap between 0 and 3),
    role_preference_fit   int check (role_preference_fit between 0 and 3),
    location_fit          int check (location_fit between 0 and 3),
    availability_fit      int check (availability_fit between 0 and 3),
    -- explicitly NO overall_score column
    generated_at          timestamptz not null default now()
);

create table talent_match_evidence (
    match_id              uuid not null references talent_match,
    evidence_id           uuid not null references work_evidence,
    why                   text,               -- the human-readable reason this evidence supports the match
    primary key (match_id, evidence_id)
);

-- Employer expresses interest; participant must accept before any contact (Parts XX-XXI).
create table employer_interest (
    interest_id           uuid primary key,
    job_id                uuid references job_requirement,
    participant_id        uuid,               -- references participant (001)
    expressed_at          timestamptz not null default now(),
    participant_response  text,               -- PENDING | ACCEPTED | DECLINED
    responded_at          timestamptz
);

create table mutual_intro (
    intro_id              uuid primary key,
    scope                 visibility_scope not null,   -- EMPLOYER or INVESTOR ...
    participant_id        uuid,               -- references participant (001)
    counterparty          text,               -- company_id or investor_id (soft ref)
    both_opted_in         boolean not null default false,
    introduced_at         timestamptz,
    note                  text
);

create table employment_outcome (
    outcome_id            uuid primary key,
    intro_id              uuid references mutual_intro,
    transaction           opportunity_transaction,
    happened              boolean,
    participant_shared    boolean default false,   -- only recorded if participant chooses to share
    note                  text,
    occurred_at           timestamptz
);

create table paid_project (
    paid_project_id       uuid primary key,
    company_id            uuid,               -- references company (001)
    participant_id        uuid,               -- references participant (001)
    scope_of_work         text,
    duration_weeks        int,
    ip_terms              text,
    compensation_note     text,               -- clarified before continuation (Part LXI)
    status                text
);


-- ---------------------------------------------------------------------------
-- VENTURE MARKET (Parts XXIX-XLII)
-- ---------------------------------------------------------------------------

create table venture_profile (
    venture_id            uuid primary key,
    team_id               uuid,               -- references team (001)
    project_id            uuid,               -- references project (001)
    problem               text,
    why_problem           text,
    prototype_ref         text,
    demo_ref              text,
    market_hypothesis     text,
    capital_seeking       text,               -- only if voluntarily provided
    desired_investor_type text,
    fundraising_status    text,
    -- material claims carry status (Part XXXIV) via venture_claim below
    updated_at            timestamptz not null default now()
);

-- Investor visibility for a venture is its own opt-in (Part LI / XXXIX).
create table venture_visibility (
    venture_id            uuid not null references venture_profile,
    scope                 visibility_scope not null,   -- typically INVESTOR
    is_visible            boolean not null default false,
    granted_at            timestamptz,
    revoked_at            timestamptz,
    primary key (venture_id, scope)
);

-- Every material venture claim is epistemically tagged (Observed/Self-reported/Assumed/Unknown).
create table venture_claim (
    claim_id              uuid primary key,
    venture_id            uuid not null references venture_profile,
    statement             text not null,
    status                claim_status not null default 'UNKNOWN',
    evidence_id           uuid references work_evidence,
    note                  text
);

create table fund (
    fund_id               uuid primary key,
    name                  text,
    stage                 text,               -- PRE_SEED | SEED | SERIES_A | ...
    check_size            text,
    sectors               text[],
    geography             text,
    thesis                text,
    source_url            text                -- public fund data only
);

create table investor (
    investor_id           uuid primary key,
    fund_id               uuid references fund,
    name                  text,
    role                  text,               -- GP | PARTNER | PRINCIPAL | ASSOCIATE | PLATFORM | SCOUT
    public_profile_url    text
);

create table startup_attribute (
    venture_id            uuid not null references venture_profile,
    attribute             text not null,      -- STAGE | SECTOR | TECHNICAL_DOMAIN | CAPITAL_NEED | GEOGRAPHY
    value                 text,
    status                claim_status default 'SELF_REPORTED',
    primary key (venture_id, attribute)
);

-- Venture<->fund retrieval match, decomposed; never a founder-quality score (Part XXXIII).
create table venture_match (
    match_id              uuid primary key,
    venture_id            uuid references venture_profile,
    fund_id               uuid references fund,
    stage_fit             int check (stage_fit between 0 and 3),
    sector_fit            int check (sector_fit between 0 and 3),
    check_size_fit        int check (check_size_fit between 0 and 3),
    geography_fit         int check (geography_fit between 0 and 3),
    thesis_fit            int check (thesis_fit between 0 and 3),
    technical_domain_fit  int check (technical_domain_fit between 0 and 3),
    continuation_evidence int check (continuation_evidence between 0 and 3),
    -- explicitly NO founder_score / overall_score
    generated_at          timestamptz not null default now()
);

create table venture_match_evidence (
    match_id              uuid not null references venture_match,
    evidence_id           uuid not null references work_evidence,
    why                   text,
    primary key (match_id, evidence_id)
);

create table investor_interest (
    interest_id           uuid primary key,
    fund_id               uuid references fund,
    venture_id            uuid references venture_profile,
    expressed_at          timestamptz not null default now(),
    team_response         text,               -- PENDING | ACCEPTED | DECLINED
    responded_at          timestamptz
);

create table venture_intro (
    intro_id              uuid primary key,
    venture_id            uuid references venture_profile,
    fund_id               uuid references fund,
    both_opted_in         boolean not null default false,
    introduced_at         timestamptz
);

create table venture_outcome (
    outcome_id            uuid primary key,
    intro_id              uuid references venture_intro,
    transaction           opportunity_transaction,   -- VC_INTRO | ACCELERATOR_INTRO | ...
    happened              boolean,
    team_shared           boolean default false,
    note                  text,
    occurred_at           timestamptz
);
