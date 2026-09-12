-- 011_multi_sided.sql
-- ============================================================================
-- MULTI-SIDED VALUE LAYER — one event, many stakeholders, positive-sum by design.
--
-- The question this schema is built to answer:
--   "How do we design ONE event so the SAME natural activities create maximum
--    value across MANY different stakeholders WITHOUT those stakeholders
--    destroying each other's value?"
--
-- This is NOT "a hackathon + sponsors." It is a multi-sided market whose supply
-- side (participants doing what they'd naturally do — build, ask for help, demo,
-- reflect) produces artifacts that FAN OUT to many demand sides (product clients,
-- research buyers, employers, investors, design partners, the participants
-- themselves). The design job is mechanism design: pick the set of event
-- mechanics that pushes the whole system toward the Pareto frontier of
-- stakeholder utilities, subject to HARD participant-experience floors that
-- revenue can never buy through.
--
-- Non-negotiable invariants (enforced by engine/mechanism_design.py,
-- engine/value_matrix.py, engine/multiuse_assets.py and test_multi_sided.py):
--   * Participant-experience FLOORS are hard constraints, not tradeable weights.
--     A design that violates a floor is INFEASIBLE regardless of its revenue.
--   * Utility is a VECTOR per stakeholder, never collapsed to one score. We rank
--     designs by Pareto dominance; Nash welfare (Σ log(U_s − floor_s)) is only a
--     tie-breaker among floor-respecting designs, and is −∞ at/below any floor.
--   * The SAME artifact may serve multiple sides, but each individual-grain reuse
--     needs the participant's explicit per-scope opt-in (aggregate grain is free).
--   * One contract's value is attributed across the components that produced it by
--     Shapley share — no economic event is double-counted.
--   * No person scores; no protected/sensitive attributes; missing == UNKNOWN.
--
-- Composes with 001-010. Reuses participant/team/project/artifact (001),
-- economic_event/opportunity_transaction (002/010), consent + data-level
-- conventions (001/010). Does NOT duplicate them. snake_case, uuid PKs, timestamptz.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- STAKEHOLDER SIDES — the many sides of the market. Participants are a side too,
-- and a privileged one (their floors bind the whole system).
-- ----------------------------------------------------------------------------
create type stakeholder_kind as enum (
    'PARTICIPANTS', 'TEAMS', 'PRODUCT_CLIENTS', 'RESEARCH_BUYERS', 'EMPLOYERS',
    'INVESTORS', 'DESIGN_PARTNERS', 'SPONSORS', 'MENTORS', 'UNIVERSITY',
    'ORGANIZER', 'ECOSYSTEM', 'FUTURE_PARTICIPANTS', 'FIELD_OF_KNOWLEDGE'
);

create table stakeholder_side (
    side_id          uuid primary key,
    kind             stakeholder_kind not null,
    label            text not null,
    is_supply_side   boolean not null default false,   -- produces artifacts vs. consumes value
    pays             boolean not null default false,    -- is this a side we can charge?
    -- utility DIMENSIONS this side cares about, stored as a vector, never summed
    utility_dims     text[] not null,
    -- HARD floor dimensions for this side (usually only PARTICIPANTS/TEAMS have any)
    hard_floor_dims  text[] not null default '{}',
    note             text
);

-- ----------------------------------------------------------------------------
-- EVENT MECHANICS — the primitive activities a design is assembled from
-- (open_build_track, mentor_request, demo, exit_interview, sponsor_keynote, ...).
-- A concrete event design is a SUBSET of these.
-- ----------------------------------------------------------------------------
create table event_mechanic (
    mechanic_id      uuid primary key,
    key              text unique not null,       -- 'demo', 'mentor_request', ...
    label            text not null,
    is_participant_native boolean not null,        -- would participants do this anyway?
    -- participant attention this mechanic consumes, ordinal NONE|LOW|MED|HIGH
    participant_minutes_cost text not null default 'NONE',
    note             text
);

-- ----------------------------------------------------------------------------
-- VALUE MATRIX U[mechanic, side] — how much value a mechanic creates for a side.
-- Ordinal (NEG..HIGH) + an evidence tag so we never launder an assumption as a
-- fact. Mirrors engine/value_matrix.py::U so schema and engine cannot drift.
-- ----------------------------------------------------------------------------
create table mechanic_value_cell (
    mechanic_id      uuid references event_mechanic,
    side_id          uuid references stakeholder_side,
    value_ordinal    text not null,              -- NEG | NONE | LOW | MED | HIGH
    evidence_tag     text not null,              -- O observed | I inferred | H hypothesis | U unknown
    primary key (mechanic_id, side_id)
);

-- COST/BURDEN matrix C[mechanic, resource] — burdens kept SEPARATE from value so a
-- cost can never be quietly booked as a benefit.
create table mechanic_cost_cell (
    mechanic_id      uuid references event_mechanic,
    resource         text not null,              -- participant_minutes | mentor_time | research_burden | organizer_ops | sponsor_pressure | cash
    cost_ordinal     text not null,              -- NONE | LOW | MED | HIGH
    primary key (mechanic_id, resource)
);

-- ----------------------------------------------------------------------------
-- CONFLICT MATRIX — pairs of mechanics that destroy each other's value
-- (e.g. a sponsored bounty track contaminating the open, research-valid build
-- track). The frontend-distortion gate reads this.
-- ----------------------------------------------------------------------------
create table mechanic_conflict (
    mechanic_a       uuid references event_mechanic,
    mechanic_b       uuid references event_mechanic,
    kind             text not null,     -- DISTORTION | ATTENTION | TRUST | VALIDITY
    severity         text not null,     -- LOW | MED | HIGH | BLOCKING
    why              text,
    primary key (mechanic_a, mechanic_b)
);

-- SUPER-ADDITIVE SYNERGY — pairs where doing both is worth more than the sum
-- (demo + exit_interview → far richer product/research signal). Γ term.
create table mechanic_synergy (
    mechanic_a       uuid references event_mechanic,
    mechanic_b       uuid references event_mechanic,
    bonus_ordinal    text not null,     -- LOW | MED | HIGH
    accrues_to       text[] not null,   -- which sides get the super-additive bonus
    why              text,
    primary key (mechanic_a, mechanic_b)
);

-- ----------------------------------------------------------------------------
-- EVENT DESIGN — a named subset of mechanics, scored as a VECTOR of stakeholder
-- utilities. feasible=false when it breaks a participant floor (revenue cannot
-- override). nash_welfare is a tie-break only, NULL/−inf when infeasible.
-- ----------------------------------------------------------------------------
create table event_design (
    design_id        uuid primary key,
    label            text not null,
    mechanic_keys    text[] not null,
    feasible         boolean not null,          -- passes ALL participant floors?
    floor_violations text[] not null default '{}',
    on_pareto_frontier boolean,                  -- non-dominated over stakeholder utilities?
    nash_welfare     double precision,           -- tie-break only; null when infeasible
    computed_at      timestamptz not null default now()
);

create table design_stakeholder_utility (
    design_id        uuid references event_design,
    side_id          uuid references stakeholder_side,
    dimension        text not null,             -- one utility dimension of that side
    value_num        double precision not null, -- decomposed, never summed across dims
    primary key (design_id, side_id, dimension)
);

-- ----------------------------------------------------------------------------
-- MULTI-USE ASSET RIGHTS — one naturally-produced artifact, many downstream uses,
-- each use gated by a consent scope + a grain (individual needs opt-in; aggregate
-- is free). Reuses artifact (001) + consent conventions (010). Mirrors
-- engine/multiuse_assets.py::ASSET_USES.
-- ----------------------------------------------------------------------------
create table asset_use_right (
    asset_use_id     uuid primary key,
    artifact_id      uuid references artifact,   -- from 001_core
    side_id          uuid references stakeholder_side,
    use_label        text not null,              -- 'work_evidence', 'product_signal', ...
    consent_scope    text not null,              -- required opt-in scope (compliance.VISIBILITY_SCOPES) or 'AGGREGATE'
    grain            text not null,              -- 'individual' | 'aggregate'
    granted          boolean not null default false,   -- has the participant granted this scope?
    granted_at       timestamptz
);

-- ----------------------------------------------------------------------------
-- CROSS-SUBSIDY / WHO-PAYS — price each side differently. Records who is charged,
-- who is subsidized, and the direction of subsidy, so the business model is
-- explicit rather than implied. A side can be a payer for one flow and subsidized
-- in another. Never charges the participant supply side to be discovered.
-- ----------------------------------------------------------------------------
create table cross_subsidy_flow (
    flow_id          uuid primary key,
    payer_side_id    uuid references stakeholder_side,
    subsidized_side_id uuid references stakeholder_side,
    pricing_model    text not null,     -- SPONSORSHIP | ACCESS_SUBSCRIPTION | DIRECTED_RESEARCH_WALLET | DESIGN_PARTNER_FEE | FREE
    monetization_kind text,             -- maps to opportunity_market.MONETIZATION key; legality-gated
    rationale        text,
    -- a participant supply side must NEVER be the payer-for-discovery; enforced in code
    charges_supply_for_discovery boolean not null default false
);

-- ----------------------------------------------------------------------------
-- SHAPLEY REVENUE ATTRIBUTION — one contract, split across the artifact
-- components that produced it, summing to the contract value exactly ONCE.
-- Reuses economic_event (002). Mirrors multiuse_assets.attribute_revenue.
-- ----------------------------------------------------------------------------
create table contract_attribution (
    attribution_id   uuid primary key,
    economic_event_id uuid references economic_event,   -- the ONE contract; dedup anchor
    contract_value   numeric not null,
    component        text not null,     -- 'artifact' | 'interview' | 'mentor_log' | 'followup' | ...
    shapley_share    numeric not null,  -- components sum to contract_value; absent components = 0
    primary key (attribution_id, component)
);

-- ----------------------------------------------------------------------------
-- ACCOUNT VALUE GRAPH — one company can be MANY buyers at once (sponsor +
-- research buyer + employer + design partner). We track the account, its
-- separate budgets, and its total relationship value WITHOUT letting one
-- budget's spend be counted as another's.
-- ----------------------------------------------------------------------------
create table account (
    account_id       uuid primary key,
    company_label    text not null,
    note             text
);

create table account_role (
    account_id       uuid references account,
    side_id          uuid references stakeholder_side,   -- the role this account plays
    budget_line      text not null,     -- separate budget the spend comes from
    active           boolean not null default true,
    primary key (account_id, side_id, budget_line)
);

-- ----------------------------------------------------------------------------
-- TRANSACTION MARKET — mutual-opt-in matches between a demand side and a
-- supply-side subject. Reuses the mutual-intro choke point (engine/mutual_intro.py):
-- no contact disclosed without BOTH sides opting in. An intro is NOT a deal.
-- ----------------------------------------------------------------------------
create table market_match (
    match_id         uuid primary key,
    demand_side_id   uuid references stakeholder_side,
    subject_kind     text not null,     -- 'participant' | 'team'
    subject_id       uuid not null,     -- participant/team (soft ref)
    scope            text not null,     -- EMPLOYER | INVESTOR | DESIGN_PARTNER | PAID_PROJECT
    demand_opted_in  boolean not null default true,
    subject_opted_in boolean not null default false,
    subject_visible  boolean not null default false,
    contact_released boolean not null default false,   -- only when all three above true
    matched_at       timestamptz not null default now()
);

-- ----------------------------------------------------------------------------
-- SYSTEM DYNAMICS — flywheels and systemic risks across events, so we can see
-- which loops compound value and which failure could take down several sides at
-- once (e.g. a trust breach cascading through every opt-in market).
-- ----------------------------------------------------------------------------
create table value_loop (
    loop_id          uuid primary key,
    label            text not null,
    kind             text not null,     -- FLYWHEEL | SYSTEMIC_RISK
    sides_involved   text[] not null,
    description      text,
    -- for a risk: which single point of failure triggers it
    single_point_of_failure text
);
