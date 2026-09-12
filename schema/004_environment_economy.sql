-- 004_environment_economy.sql
-- ============================================================================
-- THE GENERALIZATION LAYER.
--
-- Migrations 001-003 model ONE implementation of a deeper primitive: a premium
-- software hackathon whose product is developer research sold to devtools firms.
-- This migration steps up one level of abstraction and models the primitive
-- itself:
--
--   A configurable temporary organization / market composed of high-agency
--   talent, engineered around an expensive problem.
--
-- A hackathon (schema 001-003) becomes ONE row in `environment_archetype`, one
-- talent mix, one buyer class. Nothing here promotes any prior hypothesis to a
-- fact. The load-bearing disciplines from 001-003 are preserved verbatim:
--   (1) no bare number for an uncertain quantity -> a `belief` reference (003)
--       or an explicit status; UNKNOWN is a first-class, valid value.
--   (2) multi-dimensional judgements stay decomposed -> never a single score
--       (mirrors icp_profile, research_question_score, sponsor_economics).
--   (3) every empirical claim about a real company carries provenance
--       (a citation row), or it does not enter the universe.
--
-- Conventions (match 001-003): snake_case, singular table names, no prefixes,
-- uuid PKs named <entity>_id (caller-supplied), timestamptz, jsonb snapshots,
-- text[] tags. Cross-file references to 001-003 tables follow the existing soft
-- convention: a bare uuid column + a `-- references <table> (schema NNN)`
-- comment rather than an enforced cross-file FK. New controlled vocabularies use
-- `create type ... as enum` (style of consent_scope / belief_status).
-- ============================================================================


-- ---------------------------------------------------------------------------
-- CONTROLLED VOCABULARIES
-- ---------------------------------------------------------------------------

-- The problem-solving MODE a problem primarily benefits from (Phase 16). This
-- is the single most important routing variable: mode -> environment shape.
create type problem_mode as enum (
    'DIVERGENCE',        -- many radically different solutions wanted
    'CONVERGENCE',       -- pick the best among known options
    'EXPERIMENTATION',   -- test causal interventions
    'OPTIMIZATION',      -- best allocation / system configuration
    'DISCOVERY',         -- surface unknown opportunities / problems
    'PROTOTYPING',       -- build artifacts / demonstrate feasibility
    'FORECASTING',       -- predict uncertain outcomes
    'SIMULATION',        -- test decisions against scenarios
    'RED_TEAMING',       -- find vulnerabilities / failure modes
    'VENTURE_CREATION',  -- form companies around problem spaces
    'MARKET_DESIGN'      -- design incentives / rules / mechanisms
);

-- What a temporary high-agency organization can be good at (Phase 5). Kept as an
-- enum so capability scores are a decomposed VECTOR per environment, never one
-- number.
create type environment_capability_kind as enum (
    'PARALLEL_SEARCH', 'SOLUTION_DIVERSITY', 'FEEDBACK_SPEED', 'PROTOTYPEABILITY',
    'EXPERIMENTABILITY', 'BEHAVIORAL_REALISM', 'MANIPULABILITY', 'COUNTERFACTUAL_QUALITY',
    'OBSERVABILITY', 'ARTIFACT_VALUE', 'TIME_COMPRESSION', 'INTERDISCIPLINARY_ADVANTAGE',
    'EXTERNAL_TALENT_ADVANTAGE', 'SIMULATION_FEASIBILITY', 'LONGITUDINAL_CAPTURE',
    'EXTERNAL_VALIDITY', 'REPEATABILITY', 'DEFENSIBILITY', 'COST_ADVANTAGE',
    'SPEED_ADVANTAGE', 'VALUE_OF_FAILURE'
);

-- Incentive / market mechanism a design can run (Phase 13). Prizes are NOT the
-- default; they are one option among many.
create type incentive_mechanism as enum (
    'WINNER_TAKE_ALL', 'MULTIPLE_PRIZES', 'BOUNTIES', 'MILESTONE_PAYMENTS',
    'PEER_PREDICTION', 'AUCTION', 'INTERNAL_MARKET', 'RESOURCE_BUDGET',
    'CONTINUATION_CONTRACT', 'PROCUREMENT_OFFER', 'EQUITY', 'REPUTATION_ONLY'
);

-- Physical form of the environment (Phase 12). A weekend in-person event is one
-- point; residencies and distributed multi-week challenges are others.
create type environment_medium as enum (
    'IN_PERSON', 'ONLINE', 'HYBRID'
);

-- Kind of actor in the general economy (Phase 3). Generalizes participant-only
-- modelling.
create type economic_actor_kind as enum (
    'PARTICIPANT', 'TEAM', 'CORPORATION', 'BUSINESS_UNIT', 'SPONSOR', 'BUYER',
    'MENTOR', 'JUDGE', 'DOMAIN_EXPERT', 'INVESTOR', 'VENDOR', 'RECRUITER',
    'CUSTOMER', 'USER', 'GOVERNMENT', 'UNIVERSITY', 'ORGANIZER', 'STARTUP'
);

-- Non-cash resources carry shadow prices, not just cash (Phase 4). This is the
-- catalogue of what flows through the economy.
create type resource_kind as enum (
    'CASH', 'PARTICIPANT_TIME_MIN', 'MENTOR_TIME_MIN', 'DOMAIN_EXPERT_TIME_MIN',
    'COMPUTE_GPU_HR', 'API_CREDITS', 'DATASET_ACCESS', 'CUSTOMER_ACCESS',
    'CAPITAL', 'PRIZE', 'BOUNTY', 'GRANT', 'INTRODUCTION', 'DISTRIBUTION',
    'REPUTATION', 'SOCIAL_CAPITAL', 'WORKSPACE', 'MATERIALS', 'EQUIPMENT',
    'JOB_OPPORTUNITY', 'INVESTMENT_OPPORTUNITY', 'DESIGN_PARTNER_SLOT',
    'PROCUREMENT_OPPORTUNITY', 'IP'
);

-- Evidence strength for a claimed corporate problem. Mirrors the honesty of
-- evidence_level (001) but for demand-side / market evidence. Ordered weakest
-- to strongest; a HYPOTHETICAL row can exist but is quarantined by this tag.
create type demand_evidence_kind as enum (
    'HYPOTHETICAL',        -- invented for a worked example; NOT market evidence
    'INFERRED_JOB_POST',   -- a mandate inferred from a job posting
    'PUBLIC_STATEMENT',    -- earnings call / annual report / exec interview
    'REGULATORY_FILING',   -- 10-K / procurement notice / filing
    'PROGRAM_ANNOUNCEMENT',-- a named innovation / R&D / accelerator program
    'BUYER_STATED',        -- a buyer said it to us directly (cheap-talk discount)
    'SIGNED_COMMERCIAL'    -- a signed pilot / contract for this exact thing
);


-- ---------------------------------------------------------------------------
-- ENVIRONMENT (the primitive E = a configurable temporary organization)
-- ---------------------------------------------------------------------------

-- Registry of environment archetypes (Phase 6). A hackathon is one row.
create table environment_archetype (
    archetype_id   uuid primary key,
    code           text not null unique,        -- e.g. INNOVATION_TOURNAMENT, R_AND_D_ARENA
    name           text not null,
    description    text,
    primary_mode   problem_mode,                -- the mode this archetype serves best
    is_hackathon_like boolean not null default false
);

-- A concrete, configurable environment design. This is the generalization of
-- event_design (003) / event_optimizer.EventDesign. The full 14-tuple decision
-- vector (Talent, Information, Tools, Capital, Incentives, Constraints, Time,
-- Competition, Collaboration, Feedback, Governance, MarketMechanism,
-- PhysicalEnvironment, DigitalEnvironment) lives in decision_vector jsonb so the
-- generator can add knobs without a migration; the columns below are the few we
-- index / constrain on.
create table environment_design (
    environment_design_id uuid primary key,
    archetype_id          uuid references environment_archetype,
    name                  text not null,
    medium                environment_medium not null default 'IN_PERSON',
    n_participants        int,
    duration_hours        numeric,             -- total engineered time (may be weeks)
    has_continuation      boolean default false,  -- 30/60/90-day follow-on phase
    incentive             incentive_mechanism,
    decision_vector       jsonb not null,      -- the full 14-tuple config
    is_feasible           boolean,             -- passes hard constraints (talent/capital/legal)
    model_version_id      text,                -- references model_version (schema 001)
    created_at            timestamptz not null default now()
);

-- Decomposed capability profile of a design (Phase 5). One row per capability;
-- NEVER collapsed to a scalar. `score` is ordinal 0..3 (NONE/LOW/MED/HIGH, the
-- score.py convention). `basis` records whether this is ASSUMED or measured.
create table environment_capability (
    environment_design_id uuid not null references environment_design,
    capability            environment_capability_kind not null,
    score                 int not null check (score between 0 and 3),
    basis                 text not null default 'ASSUMED',  -- ASSUMED | OBSERVED
    note                  text,
    primary key (environment_design_id, capability)
);

-- Talent configuration is a DECISION VARIABLE, modelled at the POPULATION level,
-- never by scoring individuals (Phase 2 / Phase 14). A row is one capability
-- band's share of the configured population.
create table talent_configuration (
    talent_config_id      uuid primary key,
    environment_design_id uuid references environment_design,
    capability_label      text not null,       -- e.g. OR_IE, ML_RESEARCH, DESIGN, DOMAIN_HEALTHCARE
    population_share      numeric check (population_share between 0 and 1),
    experience_band       text,                -- STUDENT | EARLY | SENIOR | MIXED
    scarcity_note         text,                -- how hard to recruit this band
    recruit_cost_belief_id uuid                -- references belief (schema 003); UNKNOWN by default
);


-- ---------------------------------------------------------------------------
-- PROBLEM UNIVERSE (Phases 7-11) — characterized by MECHANICS, not industry
-- ---------------------------------------------------------------------------

-- A real (or explicitly HYPOTHETICAL) expensive problem owned by an organization.
-- Economic magnitudes are belief references (003), never bare numbers; most are
-- UNKNOWN until evidenced. Every real row must have >=1 problem_evidence row.
create table problem (
    problem_id            uuid primary key,
    company_id            uuid,                -- references company (schema 001); null if hypothetical/generic
    industry              text,
    business_unit         text,
    statement             text not null,       -- the expensive problem, in plain language
    mode                  problem_mode,        -- primary problem-solving mode (Phase 16)
    decision_owner        text,                -- the role that owns the decision
    budget_owner          text,                -- the role that owns the budget (may differ)
    current_alternative   text,                -- what they do today (internal team / consultant / ...)
    current_cost_belief_id uuid,               -- references belief (003); UNKNOWN by default
    economic_value_belief_id uuid,             -- references belief (003); value of solving it
    cost_of_wrong_belief_id  uuid,             -- references belief (003); cost of a wrong decision
    missing_evidence      text,                -- what evidence the buyer lacks
    is_hypothetical       boolean not null default false,  -- true = worked example, NOT market evidence
    created_at            timestamptz not null default now()
);

-- Provenance for a real problem (Phase 9). No real problem enters the universe
-- without a citation. Mirrors evidence_link / finding_evidence discipline.
create table problem_evidence (
    evidence_id     uuid primary key,
    problem_id      uuid not null references problem,
    kind            demand_evidence_kind not null,
    source_url      text,
    source_title    text,
    quote           text,                      -- the exact supporting text, where available
    observed_at     timestamptz,               -- when the source was published/observed
    captured_at     timestamptz not null default now()
);

-- The problem MECHANICS vector (Phase 7), persisted as decomposed ordinal dims
-- (0..3), analogous to research_question_score (002). Kept separate; the matcher
-- gates on them, it does not average them.
create table problem_mechanics (
    problem_id              uuid primary key references problem,
    parallelizability       int check (parallelizability between 0 and 3),
    prototypeability        int check (prototypeability between 0 and 3),
    experimentability       int check (experimentability between 0 and 3),
    feedback_latency        int check (feedback_latency between 0 and 3),  -- 0=slow(bad), 3=fast(good)
    simulation_feasibility  int check (simulation_feasibility between 0 and 3),
    behavioral_component    int check (behavioral_component between 0 and 3),
    technical_component     int check (technical_component between 0 and 3),
    creative_component      int check (creative_component between 0 and 3),
    operational_component   int check (operational_component between 0 and 3),
    scientific_component    int check (scientific_component between 0 and 3),
    need_domain_expertise   int check (need_domain_expertise between 0 and 3),
    need_external_perspective int check (need_external_perspective between 0 and 3),
    path_dependence         int check (path_dependence between 0 and 3),
    internal_political_friction int check (internal_political_friction between 0 and 3),
    longitudinal_need       int check (longitudinal_need between 0 and 3),
    repeatability           int check (repeatability between 0 and 3),
    model_version_id        text,
    scored_at               timestamptz not null default now()
);

-- Comparison against the substitute the buyer would otherwise use (Phase 10).
-- We only pursue problems where we have a real STRUCTURAL advantage.
create table substitute_comparison (
    comparison_id   uuid primary key,
    problem_id      uuid not null references problem,
    substitute      text not null,             -- CONSULTING | UNIVERSITY_LAB | KAGGLE | INTERNAL_TEAM | ...
    cost            int check (cost between 0 and 3),
    speed           int check (speed between 0 and 3),
    solution_diversity int check (solution_diversity between 0 and 3),
    behavioral_realism int check (behavioral_realism between 0 and 3),
    external_perspective int check (external_perspective between 0 and 3),
    implementation_likelihood int check (implementation_likelihood between 0 and 3),
    note            text
);

-- Problem x Environment fit (Phase 11). Decomposed; a large budget cannot rescue
-- poor environmental fit (the hard-gate discipline of score.py). on_pareto marks
-- non-dominated (problem, environment) pairs.
create table problem_environment_fit (
    problem_id            uuid not null references problem,
    environment_design_id uuid not null references environment_design,
    parallel_search_advantage int check (parallel_search_advantage between 0 and 3),
    talent_match          int check (talent_match between 0 and 3),
    behavioral_realism    int check (behavioral_realism between 0 and 3),
    observability         int check (observability between 0 and 3),
    prototype_value       int check (prototype_value between 0 and 3),
    counterfactual_quality int check (counterfactual_quality between 0 and 3),
    external_validity     int check (external_validity between 0 and 3),
    fit_gate_passed       boolean,             -- did it clear the structural-advantage gate?
    on_pareto             boolean,
    model_version_id      text,
    primary key (problem_id, environment_design_id)
);


-- ---------------------------------------------------------------------------
-- THE GENERAL ECONOMY (Phase 3-4, 15) — actor -> opportunity -> ... -> outcome
-- ---------------------------------------------------------------------------

create table economic_actor (
    actor_id      uuid primary key,
    kind          economic_actor_kind not null,
    label         text,
    ref_id        uuid,        -- soft link to participant/team/company/... in 001 where applicable
    context       jsonb
);

-- Shadow prices for non-cash resources (Phase 4). The price is a belief (003),
-- default UNKNOWN — we do NOT fabricate a dollar value for a mentor-hour or a
-- customer introduction without evidence.
create table shadow_price (
    shadow_price_id  uuid primary key,
    resource         resource_kind not null,
    environment_design_id uuid references environment_design,  -- prices are context-specific
    price_belief_id  uuid,       -- references belief (003); UNKNOWN by default
    scarcity_note    text,
    status           text not null default 'UNKNOWN'  -- UNKNOWN | ASSUMED | OBSERVED
);

-- A general economic episode: the full chain from opportunity to outcome for one
-- actor. Generalizes choice_set (002) beyond participants+tools. The heavy
-- structure (choice set, resources, incentives) rides in jsonb so the ledger can
-- reconstruct the whole temporary economy without a table per stage.
create table economic_episode (
    episode_id        uuid primary key,
    environment_design_id uuid references environment_design,
    actor_id          uuid references economic_actor,
    opportunity_kind  text,                    -- PROBLEM | PROJECT | TEAM | CONTRACT | BOUNTY | ...
    choice_set        jsonb,                   -- options available (choice != preference)
    resources_available jsonb,                 -- {resource_kind: amount}
    incentives        jsonb,
    decision          text,                    -- what the actor chose
    resource_allocation jsonb,                 -- {resource_kind: amount committed}
    behavior          jsonb,
    occurred_at       timestamptz,
    observed_at       timestamptz,
    available_at      timestamptz,
    consent_scope     text[],
    check (occurred_at is null or available_at is null or occurred_at <= available_at)
);

-- A produced artifact (Phase 3). Software, a business model, a forecast, a
-- policy proposal, a company. Value is a belief (003), default UNKNOWN.
create table artifact (
    artifact_id     uuid primary key,
    episode_id      uuid references economic_episode,
    problem_id      uuid references problem,
    kind            text,                      -- SOFTWARE | PROTOTYPE | STRATEGY | FORECAST | COMPANY | ...
    description     text,
    value_belief_id uuid,                      -- references belief (003)
    created_at      timestamptz not null default now()
);

-- An outcome, including NEGATIVE results, which can themselves be valuable
-- (Phase 17). value_of_negative captures "20 teams tried X and 14 failed ->
-- saves the buyer money."
create table outcome (
    outcome_id      uuid primary key,
    episode_id      uuid references economic_episode,
    problem_id      uuid references problem,
    kind            text,                      -- PERFORMANCE | COST_SAVING | FAILURE | DEPLOYMENT | ...
    is_negative_result boolean not null default false,
    changed_a_decision boolean,                -- the only outcome that matters commercially
    value_belief_id uuid,                      -- references belief (003)
    note            text,
    occurred_at     timestamptz
);


-- ---------------------------------------------------------------------------
-- THE CAPABILITY -> PROBLEM -> ICP GRAPH (Phase 25) + BUSINESS MODEL (Phase 21)
-- ---------------------------------------------------------------------------

-- Edges of the discovery graph:
--   talent_capability -> environment_capability -> problem_mechanic ->
--   corporate_problem -> decision -> buyer -> organization -> contract -> outcome
-- Stored generically so the engine can traverse in both directions
-- (demand -> environment, supply -> opportunity).
create table discovery_edge (
    edge_id     uuid primary key,
    from_kind   text not null,   -- TALENT_CAPABILITY | ENV_CAPABILITY | PROBLEM_MECHANIC | PROBLEM | BUYER | ...
    from_ref    text not null,   -- the node key (enum value, uuid, or label)
    to_kind     text not null,
    to_ref      text not null,
    weight_belief_id uuid,       -- references belief (003); edge strength, UNKNOWN by default
    note        text
);

-- Candidate business models (Phase 21). Sponsorship is ONE row. Dimensions kept
-- decomposed (ordinal 0..3), never collapsed; mirrors the discipline of
-- icp_profile / sponsor_economics.
create table business_model_option (
    business_model_id uuid primary key,
    code            text not null unique,      -- PER_PROBLEM_MANDATE | RESEARCH_ENGAGEMENT | SPONSORSHIP | ...
    name            text not null,
    revenue_potential int check (revenue_potential between 0 and 3),
    gross_margin    int check (gross_margin between 0 and 3),
    repeatability   int check (repeatability between 0 and 3),
    sales_cycle     int check (sales_cycle between 0 and 3),   -- 0=long(bad), 3=short(good)
    scalability     int check (scalability between 0 and 3),
    conflict_risk   int check (conflict_risk between 0 and 3), -- 0=high(bad), 3=low(good)
    participant_alignment int check (participant_alignment between 0 and 3),
    defensibility   int check (defensibility between 0 and 3),
    capital_intensity int check (capital_intensity between 0 and 3),  -- 0=high(bad), 3=low(good)
    note            text
);

-- A candidate ICP is an OUTPUT of problem discovery, not an input (Phase 19).
-- It clusters high-opportunity problems and names the specific buyer/trigger/
-- budget. evidence_strength ties back to how well-sourced the underlying
-- problems are. Nothing here is a committed DECISION.
create table icp_candidate (
    icp_candidate_id  uuid primary key,
    label             text not null,
    company_characteristics text,
    exact_problem     text,
    exact_buyer       text,                    -- the specific executive/role
    trigger           text,                    -- reason to call today
    budget_source     text,
    existing_alternative text,
    why_alternative_fails text,
    why_our_environment_wins text,
    required_talent   text,
    required_environment_design_id uuid references environment_design,
    frequency         text,
    business_model_id uuid references business_model_option,
    potential_contract_shape text,
    evidence_strength demand_evidence_kind,    -- the STRONGEST evidence behind the cluster
    risks             text,
    created_at        timestamptz not null default now()
);

-- Which problems belong to an ICP cluster (many-to-many).
create table icp_problem (
    icp_candidate_id uuid not null references icp_candidate,
    problem_id       uuid not null references problem,
    primary key (icp_candidate_id, problem_id)
);
