-- 013_agentic.sql
-- ============================================================================
-- AGENTIC OS — the Governor-driven layer that turns the decision engine into an
-- autonomous system. The core loop:
--   UNKNOWN -> VOI -> AgentTask -> Research -> Evidence -> NodeUpdate -> Reoptimize
--
-- Persists the node GRAPH, the AGENTS + their permissions, the TASK queue, every
-- agent RUN, DECISION, and APPROVAL (append-only), and the recursive decomposition
-- edges. Discipline carried from the rest of the repo: a node is never fabricated
-- (UNKNOWN/QUOTE/PRIMARY/NEEDS_RESEARCH are honest statuses); external actions are
-- permission-gated and require a human approval before execution.
--
-- Composes with 001-012. Reuses the tri-temporal evidence spine (001/006/012) and
-- consent/compliance conventions. snake_case, uuid PKs, timestamptz.
-- ============================================================================

create type node_status as enum (
    'UNKNOWN', 'RESOLVING', 'RESOLVED', 'DECOMPOSED',
    'NEEDS_RESEARCH', 'QUOTE', 'PRIMARY', 'BLOCKED'
);
create type agent_permission as enum ('AUTONOMOUS_READ', 'NEEDS_APPROVAL');
create type task_state as enum ('QUEUED', 'RUNNING', 'DONE', 'NEEDS_APPROVAL', 'FAILED');

-- ---------------------------------------------------------------------------
-- AGENT REGISTRY — the agents the Governor can dispatch, and what they may do.
-- ---------------------------------------------------------------------------
create table agent (
    agent_id        uuid primary key,
    name            text unique not null,        -- 'grounding','cost','pricing','sponsor_discovery',...
    kind            text not null,               -- AUTONOMOUS | DISCOVERY | COGNITION | EXTERNAL_ACTION
    permission      agent_permission not null,
    reuses_engine   text,                        -- which existing module it wraps (node_scraper, event_optimizer, ...)
    description     text
);

-- ---------------------------------------------------------------------------
-- NODE GRAPH — every question the system is trying to answer, with provenance.
-- ---------------------------------------------------------------------------
create table node (
    node_id         uuid primary key,
    run_id          uuid,                        -- which governor run this belongs to (nullable for library nodes)
    key             text not null,               -- 'cost','pricing','battle_fintech',...
    question        text not null,
    resolver_agent  text references agent(name),
    status          node_status not null default 'UNKNOWN',
    value           jsonb,                       -- resolved value (null until RESOLVED)
    provenance      text,                        -- source/agent + date, or the human next-step for QUOTE/PRIMARY
    voi             double precision default 0,  -- value of resolving it (prioritization)
    -- point-in-time provenance for the resolution
    resolved_at     timestamptz,
    available_at    timestamptz
);

-- decomposition + dependency edges (recursive node graph)
create table node_edge (
    parent_id       uuid references node,
    child_id        uuid references node,
    kind            text not null,               -- 'DECOMPOSES_INTO' | 'DEPENDS_ON'
    primary key (parent_id, child_id, kind)
);

-- ---------------------------------------------------------------------------
-- TASK QUEUE + AGENT RUNS — the Governor's work items and their execution log.
-- ---------------------------------------------------------------------------
create table agent_task (
    task_id         uuid primary key,
    run_id          uuid,
    node_id         uuid references node,
    agent_name      text references agent(name),
    permission      agent_permission not null,
    state           task_state not null default 'QUEUED',
    created_at      timestamptz not null default now()
);

create table agent_run (
    agent_run_id    uuid primary key,
    task_id         uuid references agent_task,
    node_id         uuid references node,
    agent_name      text references agent(name),
    result_kind     text,                        -- Evidence | Decompose | Defer | RequestAction
    started_at      timestamptz not null default now(),
    finished_at     timestamptz,
    detail          jsonb
);

-- ---------------------------------------------------------------------------
-- APPEND-ONLY LOGS — decisions and approvals. Never updated in place.
-- ---------------------------------------------------------------------------
create table decision_log (
    decision_id     uuid primary key,
    run_id          uuid,
    node_id         uuid references node,
    decision        text not null,               -- RESOLVED | DECOMPOSED | DEFER->NEEDS_RESEARCH | REOPTIMIZE_...
    detail          jsonb,
    at              timestamptz not null default now()
);

-- external actions require a human approval before they may execute
create table approval_gate (
    approval_id     uuid primary key,
    run_id          uuid,
    task_id         uuid references agent_task,
    node_id         uuid references node,
    action          text not null,               -- 'send sponsor/venue outreach email'
    payload         jsonb,
    state           text not null default 'AWAITING_HUMAN_APPROVAL',  -- AWAITING | APPROVED | REJECTED
    requested_at    timestamptz not null default now(),
    decided_at      timestamptz,
    decided_by      text
    -- NOTE: even APPROVED, the actual external send stays a human step (safety); the framework records intent.
);

-- ---------------------------------------------------------------------------
-- GOVERNOR RUN — one execution of the pipeline (e.g. the one-button Cornell run).
-- ---------------------------------------------------------------------------
create table governor_run (
    run_id          uuid primary key,
    goal            text not null,               -- 'What hackathon should we host at Cornell?'
    started_at      timestamptz not null default now(),
    finished_at     timestamptz,
    n_resolved      integer,
    n_open          integer,                     -- NEEDS_RESEARCH + QUOTE + PRIMARY
    n_awaiting_approval integer
);
