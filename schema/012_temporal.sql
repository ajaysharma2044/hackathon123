-- 012_temporal.sql
-- ============================================================================
-- TEMPORAL + CONTEXT + PROCESS-TRACING LAYER — turn the static event DB into a
-- time-aware dynamic system.
--
-- The shift: from  Actor + Action -> Outcome  to
--   PriorState_t -> Context_t -> OpportunitySet_t -> Trigger_t -> ChoiceSet_t ->
--   Decision_t -> Action_t -> Intervention_t -> Artifact_t -> ImmediateOutcome_t
--   -> NextState_{t+1} -> DelayedOutcome_{t+k}
--
-- Time is not "add timestamps". It changes interpretation, prediction, causal
-- reasoning, allocation, pricing, evidence validity, and professional/venture
-- evidence. Non-negotiables enforced by engine/ + test_temporal.py:
--   * FOUR CLOCKS never conflated: EVENT / PROJECT / LIFECYCLE / MARKET.
--   * TRI-TEMPORAL, point-in-time truth: a model as-of t may use only rows with
--     available_at <= t. No future leakage (reuses 001/006 evidence tri-temporal).
--   * Missing context is VALID (never back-filled, never penalised).
--   * Opportunity set is context for interpreting output — NEVER a socioeconomic
--     or person-quality score.
--   * Counterfactuals only where identified; never invented from a single case.
--   * Evidence has freshness; old evidence is aged and down-weighted, not deleted.
--
-- Composes with 001-011. Reuses participant/team/project/artifact (001), the
-- tri-temporal evidence columns (001/006), consent (001/010), mentor/intervention
-- concepts (007). snake_case, uuid PKs, timestamptz.
-- ============================================================================

-- The four clocks, as an enum every temporal row is stamped against.
create type clock_kind as enum ('EVENT', 'PROJECT', 'LIFECYCLE', 'MARKET');

-- ---------------------------------------------------------------------------
-- TEMPORAL STATE — a derived state snapshot for an entity at a point on a clock.
-- Derived by folding the immutable event log (event sourcing); never hand-edited.
-- ---------------------------------------------------------------------------
create table temporal_state (
    state_id        uuid primary key,
    entity_kind     text not null,          -- 'participant' | 'team' | 'project'
    entity_id       uuid not null,
    clock           clock_kind not null,
    as_of           timestamptz not null,   -- the point on that clock
    state_label     text,                   -- FORMING | BUILDING | BLOCKED | ...
    -- the state VECTOR (GoalClarity, Scope, CapabilityCoverage, Progress, ...)
    state_vector    jsonb,
    -- tri-temporal provenance of the derivation
    occurred_at     timestamptz not null,
    observed_at     timestamptz not null,
    available_at    timestamptz not null,   -- point-in-time key: a model as-of t needs this <= t
    derived_from    uuid[]                  -- the immutable event ids folded in
);

-- ---------------------------------------------------------------------------
-- CONTEXT ENVELOPE — the ContextEnvelope fields at an instant. All nullable;
-- missing is valid. Context is a FUNCTION OF TIME (one row per meaningful change).
-- ---------------------------------------------------------------------------
create table context_envelope (
    context_id      uuid primary key,
    entity_kind     text not null,
    entity_id       uuid not null,
    as_of           timestamptz not null,
    event_phase     text,
    project_phase   text,
    time_remaining_min integer,
    current_goal    text,
    current_milestone text,
    current_workstream text,
    current_blocker text,
    role_structure  jsonb,
    capability_coverage jsonb,
    resources_available text[],
    compute_available text,
    mentor_availability text,
    recent_mentor_intervention boolean,
    peer_exposure   text[],
    sponsor_exposure text[],
    challenge_context text,
    physical_zone   text,
    prior_attempts  integer,
    prior_tool_exposure text[],
    relevant_experience text[],             -- XXXII: direct relevant experience ONLY
    consent_state   jsonb,
    evidence_status text,
    available_at    timestamptz not null    -- point-in-time
    -- NOTE: no socioeconomic / protected / person-quality column may ever be added here.
);

-- ---------------------------------------------------------------------------
-- OPPORTUNITY STATE — O_i(t): resources/support available to an actor at t.
-- Interpret achievement WITH this. Never collapsed into an advantage score.
-- ---------------------------------------------------------------------------
create table opportunity_state (
    opportunity_id  uuid primary key,
    entity_kind     text not null,
    entity_id       uuid not null,
    as_of           timestamptz not null,
    resources       text[] not null default '{}',   -- {GPU, MENTOR_ORIE, TEAMMATE_FRAMEWORK, ...}
    available_at    timestamptz not null
);

-- CHOICE STATE — the ChoiceSet available at t (what the actor could have chosen).
create table choice_state (
    choice_id       uuid primary key,
    entity_kind     text not null,
    entity_id       uuid not null,
    as_of           timestamptz not null,
    choice_set      text[] not null,
    chosen          text,
    available_at    timestamptz not null
);

-- RESOURCE STATE — event-level resource availability over time (mentors, rooms, compute, engineers).
create table resource_state (
    resource_id     uuid primary key,
    resource_kind   text not null,          -- 'mentor' | 'room' | 'compute' | 'company_engineer'
    as_of           timestamptz not null,
    quantity_available numeric,
    quantity_demanded numeric               -- for temporal reallocation (XLVI)
);

-- ---------------------------------------------------------------------------
-- EPISODE — the master object. An Event is a set of episodes linked over time.
-- ---------------------------------------------------------------------------
create table episode (
    episode_id      uuid primary key,
    start_time      timestamptz not null,
    end_time        timestamptz,
    prior_state     text,
    goal            text,
    context_id      uuid references context_envelope,
    opportunity_id  uuid references opportunity_state,
    trigger         text,
    decision        text,
    action          text,
    intervention    text,
    artifact_id     uuid,                   -- references artifact (001)
    immediate_outcome text,
    explanation     text,                   -- proposed mechanism (process tracing)
    alternative_explanations text[],        -- rival mechanisms kept explicit
    next_state      text,
    thick_description text,                 -- LXXI: high-signal qualitative context
    available_at    timestamptz not null
);

create table episode_actor (
    episode_id      uuid references episode,
    entity_kind     text not null,
    entity_id       uuid not null,
    role            text,
    primary key (episode_id, entity_id)
);

create table episode_event (
    episode_id      uuid references episode,
    evidence_event_id uuid not null,        -- references the immutable evidence log (001/006)
    seq             integer not null,       -- ORDER matters: sequence is a variable
    event_type      text not null,
    occurred_at     timestamptz not null,
    primary key (episode_id, evidence_event_id)
);

create table intervention_episode (
    intervention_id uuid primary key,
    episode_id      uuid references episode,
    kind            text not null,          -- MENTOR | SCOPE_CUT | PIVOT_NUDGE | COMPANY_ENGINEER
    requested_at    timestamptz,
    arrived_at      timestamptz,            -- latency = arrived - requested (XV)
    ended_at        timestamptz,
    state_at_intervention text,             -- effect depends on state + timing (XV)
    time_remaining_min integer
);

-- DELAYED OUTCOMES — the lifecycle-clock tail (7/30/90d). Kept separate rows so a
-- point-in-time query at submission cannot see a day-30 outcome.
create table delayed_outcome (
    outcome_id      uuid primary key,
    episode_id      uuid references episode,
    horizon         text not null,          -- '7d' | '30d' | '90d'
    outcome_label   text,
    voluntarily_shared boolean not null default false,
    occurred_at     timestamptz,
    observed_at     timestamptz,
    available_at    timestamptz not null
);

-- ---------------------------------------------------------------------------
-- STATE TRANSITION — observed transitions (for transition-probability estimation
-- only after enough data; sparse rows stay descriptive).
-- ---------------------------------------------------------------------------
create table state_transition (
    transition_id   uuid primary key,
    entity_kind     text not null,
    entity_id       uuid not null,
    from_state      text not null,
    to_state        text not null,
    at              timestamptz not null,
    trigger_event   uuid                    -- the evidence event that triggered it
);

-- TIME METRIC — a named duration for an episode/entity (TimeToMentor, BlockedDuration, ...).
create table time_metric (
    metric_id       uuid primary key,
    entity_kind     text not null,
    entity_id       uuid not null,
    episode_id      uuid references episode,
    metric_name     text not null,          -- TimeToFirstSuccess | MentorWait | ...
    value_minutes   numeric,                -- NULL when the anchoring events are absent (valid)
    computed_at     timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- TRAJECTORY — the whole ordered evolution of an entity (tau = S0,A0,S1,...).
-- ---------------------------------------------------------------------------
create table trajectory (
    trajectory_id   uuid primary key,
    entity_kind     text not null,
    entity_id       uuid not null,
    clock           clock_kind not null,
    archetype       text,                   -- descriptive PROJECT shape; NOT a personality label
    domain          text                    -- 'learning' | 'venture' | 'rd' | 'product' | NULL
);

create table trajectory_event (
    trajectory_id   uuid references trajectory,
    seq             integer not null,
    kind            text not null,          -- 'STATE' | 'ACTION'
    label           text not null,
    at              timestamptz,            -- NULL where unobserved (missing is valid)
    primary key (trajectory_id, seq)
);

-- ---------------------------------------------------------------------------
-- PREDICTION SNAPSHOT — every prediction stored with its as-of information set,
-- so it can be scored later WITHOUT leakage (Parts LVI, LVII, LVIII).
-- ---------------------------------------------------------------------------
create table prediction_snapshot (
    prediction_id   uuid primary key,
    target          text not null,          -- 'team_failure' | 'mentor_demand' | 'retention' | ...
    entity_kind     text,
    entity_id       uuid,
    prediction_time timestamptz not null,   -- as-of time; may use only available_at <= this
    horizon         text,                   -- '1h' | '6h' | 'submission' | '7d' | '30d' | '90d'
    predicted_value jsonb,
    uncertainty     jsonb,
    model_version   text,
    information_cutoff timestamptz not null, -- must equal the max available_at actually used
    realized_value  jsonb,                  -- filled in later, at evaluation time
    realized_at     timestamptz
);

-- ---------------------------------------------------------------------------
-- TEMPORAL CLAIM + FRESHNESS — evidence with a shelf life (XXIV, XXV, LIX).
-- ---------------------------------------------------------------------------
create table freshness_policy (
    claim_type      text primary key,       -- venue_fact | tool_preference | company_strategy | ...
    validity_days   integer not null,
    half_life_days  integer,                -- NULL => decay shape UNKNOWN; do not assume exponential
    basis           text
);

create table temporal_claim (
    claim_id        uuid primary key,
    claim_type      text references freshness_policy,
    statement       text not null,
    observed_at     timestamptz not null,
    last_validated_at timestamptz,
    -- freshness/decay are COMPUTED from the policy at read time, never frozen into a number here
    source          text,
    evidence_tag    text                    -- O observed | I inferred | H hypothesis | U unknown
);

-- ---------------------------------------------------------------------------
-- CLIENT DECISION DEADLINE — time-sensitive VOI (XXVI, XXVII, LX, LXII).
-- ---------------------------------------------------------------------------
create table client_decision_deadline (
    deadline_id     uuid primary key,
    account_id      uuid,                   -- references account (011)
    decision        text not null,
    decision_deadline timestamptz not null,
    trigger_at      timestamptz,            -- buying-trigger timing (LX)
    contact_window  tstzrange,
    budget_window   tstzrange,
    -- deliverable horizon must fit before the deadline (LXII); enforced in temporal_voi.py
    max_deliverable_horizon text
);

-- ---------------------------------------------------------------------------
-- MACRO CONTEXT SNAPSHOT — the MARKET clock frozen per event, so history keeps its
-- context (LXVI cohort effects, LXVIII seasonality, LXIX macro snapshot).
-- ---------------------------------------------------------------------------
create table macro_context_snapshot (
    snapshot_id     uuid primary key,
    event_id        uuid,                   -- references event (001/007)
    captured_at     timestamptz not null,
    technology_environment jsonb,           -- major model/product releases at the time
    economic_environment jsonb,
    academic_calendar_state text,           -- semester / prelims / recruiting / break
    major_cornell_events text[],
    note            text
);
