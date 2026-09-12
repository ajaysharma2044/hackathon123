-- Builder Network — ADAPTIVE TEAM PERFORMANCE + RESCUE ENGINE schema (v008)
-- Postgres flavor. The live system that maximizes useful contribution opportunity from EVERY
-- participant and EVERY team, by detecting at-risk teams early and adapting the ENVIRONMENT around
-- them. See docs/team-rescue/* ; runnable core in engine/team_state.py, rescue_engine.py,
-- critical_path.py, event_control.py (+ tests).
--
-- EXTENDS 001_core.sql (team, participant, project, event), 006_live_research.sql (mentor,
-- support_request, mentor_interaction, researcher, burden budget), 007_event_ops.sql (staff,
-- venue_resource). Nothing redefined; new objects only.
--
-- THE OBJECTIVE (encoded structurally):  maximize useful contribution opportunity.
-- THE ANTI-OBJECTIVE (forbidden by design):  this is NOT a system that scores which student is
--   "lazy". There is deliberately NO individual productivity/quality/work-ethic/employability score
--   anywhere in this file. State is TEAM-LEVEL; contribution is captured as voluntary OWNERSHIP, not
--   graded output. No keystrokes, no screen/camera/DM surveillance. (docs/team-rescue/firewalls-and-ethics.md)
--
-- INVARIANTS:
--   (1) TEAM STATE IS A VECTOR, never auto-collapsed into one team score. (Part I)
--   (2) NO INDIVIDUAL SCORE. Contribution is self-reported ownership; imbalance is a team-level pulse. (Parts XII, LIII)
--   (3) EVERY INTERVENTION RECORDS state_before → intervention → state_after → outcome → experience,
--       and never asserts causality from mere precedence. (Parts LV, LVI)
--   (4) PERFORMANCE/RESEARCH FIREWALL. Rescue uses OPERATIONAL state; research uses CONSENTED
--       evidence; the two purposes are separate and rescue state never ranks/excludes a participant. (Part XLVI)
--   (5) FAIRNESS. A paying client cannot buy priority over the minimum support floor every team gets. (Parts XVII, LVII, LIX)

------------------------------------------------------------------------------------------------
-- TEAM STATE  (Part I–II) — the decomposed vector + low-burden observables
------------------------------------------------------------------------------------------------
create type project_archetype as enum (
  'AI_APP','DEVELOPER_TOOL','HARDWARE','OPTIMIZATION','SIMULATION','DATA_PROJECT',
  'CONSUMER_APP','RESEARCH_PROTOTYPE','RD_CHALLENGE','DESIGN_PROTOTYPE'
);
create type team_lifecycle as enum (   -- Part XXX state machine
  'FORMING','PLANNING','BUILDING','BLOCKED','PIVOTING','INTEGRATING','TESTING','POLISHING',
  'SUBMISSION_READY','DONE'
);
create type progress_flag as enum ('EARLY','ON_TRACK','AT_RISK');  -- NOT good/bad team (Part VII)

create table team_state (              -- one row per (team, as_of); the VECTOR, never one score
  team_id        uuid references team not null,
  as_of          timestamptz not null,
  archetype      project_archetype,
  lifecycle      team_lifecycle not null,
  -- the decomposed vector (Part I). Kept as labeled dims in jsonb so it is NEVER silently summed:
  --   goal_clarity, problem_quality, scope_fit, capability_coverage, role_coverage, task_ownership,
  --   technical_progress, artifact_progress, blocker_severity, mentor_need, decision_latency,
  --   team_coordination, workload_balance, energy, confidence, time_remaining, submission_readiness
  dims           jsonb not null,
  milestone_index int not null default 0,   -- M0..M8 (Part VI)
  progress       progress_flag,             -- derived label from the expected-progress envelope (Part VII)
  model_version_id text references model_version,   -- derived, re-derivable; never hand-edited
  primary key (team_id, as_of)
  -- NOTE: there is intentionally no `team_score` column. A team is a vector + a risk LABEL. (Invariant 1)
);
create table team_pulse (              -- the one-tap, low-burden self-report (Part II, LIII)
  pulse_id       uuid primary key,
  team_id        uuid references team not null,
  occurred_at    timestamptz not null,
  state          text,                      -- BUILDING|BLOCKED|PIVOTING|TESTING|POLISHING|NEED_HELP
  contribution   text,                      -- YES_ALL_HAVE_WORK | SOMEONE_NEEDS_TASK | OVERLOADED_ROLE | NEED_DIFFERENT_SKILL
  energy         int check (energy between 1 and 5),
  burden_sec     int not null default 0     -- debited to the participant burden budget (006)
);

------------------------------------------------------------------------------------------------
-- MILESTONES & EXPECTED-PROGRESS ENVELOPE  (Parts VI–VII, XXXVI)
------------------------------------------------------------------------------------------------
create table team_milestone (
  team_id        uuid references team not null,
  milestone      text not null,             -- M0..M8
  reached_at     timestamptz,               -- null = not yet
  source         text,                      -- 'pulse' | 'artifact' | 'taskboard' (captured via tools they use)
  primary key (team_id, milestone)
);
create table progress_envelope (            -- expected milestone window per archetype (assumption → learned)
  archetype      project_archetype not null,
  time_fraction  real not null,             -- fraction of build time elapsed [0,1]
  expected_min_milestone int not null,      -- the milestone a typical team of this archetype has reached by then
  is_learned     boolean not null default false,  -- false = assumption; true = calibrated from event data
  primary key (archetype, time_fraction)
);

------------------------------------------------------------------------------------------------
-- PROJECT DEFINITION & SCOPE  (Parts IV–V, XVIII)
------------------------------------------------------------------------------------------------
create table project_definition (           -- short, early; NOT a formal pitch (Part IV)
  team_id        uuid references team primary key,
  what           text, who_for text, core_challenge text,
  success_if     text,                       -- what must work to count as successful
  can_cut        text,                        -- what is droppable
  feasible_in_event boolean,                  -- can the core be built in time?
  captured_at    timestamptz
);
create table scope_assessment (              -- RequiredWork vs RemainingTime vs Capability (Part V, XVIII)
  assessment_id  uuid primary key,
  team_id        uuid references team not null,
  as_of          timestamptz not null,
  required_work  real, feasible_work real,    -- comparable units (story-points/hours estimate)
  verdict        text,                         -- OVER_SCOPED | WELL_MATCHED | UNDER_SCOPED
  recommendation text                          -- reduce/reuse/narrow/reset  |  stretch/extend/test
);

------------------------------------------------------------------------------------------------
-- BLOCKERS & THE NO-DEAD-TEAM LADDER  (Parts III, VIII, IX)
------------------------------------------------------------------------------------------------
create type blocker_type as enum (
  'TECHNICAL_BLOCKER','SCOPE_PROBLEM','TEAM_ROLE_GAP','COORDINATION','PRODUCT_CONFUSION',
  'DEPENDENCY_FAILURE','RESOURCE_SHORTAGE','MOTIVATION','DOMAIN_KNOWLEDGE','OTHER'
);
create table blocker (
  blocker_id     uuid primary key,
  team_id        uuid references team not null,
  type           blocker_type not null,
  severity       text not null,              -- LOW | MED | HIGH | CRITICAL
  required_skill text,
  blocked_since  timestamptz not null,
  resolved_at    timestamptz,
  escalation_level int not null default 0 check (escalation_level between 0 and 6),
  detected_by    text                        -- pulse | mentor | observer | telemetry | taskboard
);
-- Escalation ladder (Part III): 0 none · 1 resource/docs · 2 mentor · 3 specialist mentor
--   · 4 short team diagnosis · 5 scope reduction/architecture reset · 6 restructuring/optional merge.
-- Objective: MINIMIZE preventable blocked time without interrupting teams making progress.

------------------------------------------------------------------------------------------------
-- RESCUE INTERVENTIONS  (Parts IX, XXXIII, LV–LVI) — the feedback loop, counterfactual-disciplined
------------------------------------------------------------------------------------------------
create table rescue_intervention (
  intervention_id uuid primary key,
  team_id        uuid references team not null,
  occurred_at    timestamptz not null,
  diagnosis      blocker_type,
  action         text not null,              -- NOTHING|RESOURCE|MENTOR|SPECIALIST|DIAGNOSIS|SCOPE_RESET
                                             --  |QUICK_WIN|REMATCH|CHALLENGE_LEVEL|BREAK|COMPANY_ENGINEER
  reason         text not null,
  state_before   jsonb,                       -- the team_state vector before
  state_after    jsonb,                       -- the team_state vector after (for learning)
  outcome        text,
  participant_experience text,
  -- Invariant 3: we record that the intervention PRECEDED the outcome; we do NOT store a causal
  --   claim. Causal language is reserved for experiments/quasi-experiments. (Part LVI)
  causal_claim   boolean not null default false check (causal_claim = false),
  mentor_interaction_id uuid references mentor_interaction
);

------------------------------------------------------------------------------------------------
-- ROLES, OWNERSHIP, WORKLOAD, CRITICAL PATH  (Parts XI–XIV, LIII)
------------------------------------------------------------------------------------------------
create table role_coverage (                 -- needed capabilities per team; coverage only, no ranking
  team_id        uuid references team not null,
  capability     text not null,              -- backend|frontend|ml|data|orie|hardware|product|design|domain
  covered        boolean not null,
  overloaded     boolean not null default false,
  primary key (team_id, capability)
);
create table contribution_ownership (        -- voluntary "what am I primarily owning" (Part XII)
  team_id        uuid references team not null,
  participant_id uuid references participant not null,
  owns           text,                        -- backend|model|frontend|data|hardware|ux|research|optimization|demo|other
  updated_at     timestamptz,
  primary key (team_id, participant_id)
  -- If a participant has no ownership, the TEAM gets a lightweight prompt ("does anyone need a
  --   clearer workstream?"). We never label an individual a free-rider. (Invariant 2)
);
create table team_task (                     -- lightweight tasks → a DAG for critical-path (Part XIV)
  task_id        uuid primary key,
  team_id        uuid references team not null,
  title          text,
  owner_capability text,
  duration_est_min int,
  status         text not null default 'TODO',  -- TODO | DOING | DONE | BLOCKED
  uncertainty    text                            -- LOW|MED|HIGH
);
create table task_dependency (               -- edge: task depends on prerequisite
  task_id        uuid references team_task not null,
  depends_on     uuid references team_task not null,
  primary key (task_id, depends_on)
);

------------------------------------------------------------------------------------------------
-- REMATCHING, MERGES, SWITCHES  (Parts X, XIX, XX) — all VOLUNTARY, never automatic
------------------------------------------------------------------------------------------------
create table capability_request (            -- a team voluntarily surfaces a needed skill (Part X)
  request_id     uuid primary key,
  team_id        uuid references team not null,
  capability     text not null,
  opened_at      timestamptz not null,
  mentor_routed  boolean not null default false,
  surfaced_to_board boolean not null default false,   -- voluntary collaboration board (never auto-assign)
  resolved_at    timestamptz
);
create table rematching_pool (               -- a participant seeking a team (Part XX)
  participant_id uuid references participant primary key,
  event_id       uuid references event not null,
  offers_capabilities text[],
  entered_at     timestamptz not null,
  rematched_team uuid references team
);
create table team_merge_suggestion (         -- suggested only if BOTH teams opt in (Part XIX)
  suggestion_id  uuid primary key,
  team_a         uuid references team not null,
  team_b         uuid references team not null,
  rationale      text,
  a_opted_in     boolean not null default false,
  b_opted_in     boolean not null default false,
  -- a merge can only proceed when both opted in (enforced in engine, surfaced here)
  status         text not null default 'SUGGESTED'   -- SUGGESTED | DECLINED | MERGED
);

------------------------------------------------------------------------------------------------
-- EVENT-WIDE: BOTTLENECKS, WASTE, RESOURCES, SCHEDULE  (Parts XVI–XVII, XLII–XLIV, LIX–LXVII)
------------------------------------------------------------------------------------------------
create table resource_pool (                 -- scarce resources to allocate (Part XVII, LVII)
  resource_id    uuid primary key,
  event_id       uuid references event not null,
  kind           text not null,              -- MENTOR:<cat> | GPU | COMPUTE | EQUIPMENT | ROOM | DOMAIN_EXPERT | COMPANY_ENGINEER
  capacity       int not null
);
create table resource_allocation (
  allocation_id  uuid primary key,
  resource_id    uuid references resource_pool not null,
  team_id        uuid references team not null,
  amount         int not null,
  as_of          timestamptz not null,
  -- Fairness (Invariant 5): allocation first satisfies a per-team minimum floor; only surplus is
  --   prioritized. A commercial client cannot buy below-floor priority over basic participant support.
  is_below_floor_override boolean not null default false check (is_below_floor_override = false)
);
create table event_bottleneck (              -- the current binding constraint (Theory of Constraints, Part LXII–LXIII)
  bottleneck_id  uuid primary key,
  event_id       uuid references event not null,
  as_of          timestamptz not null,
  kind           text not null,              -- mentor expertise | compute | api | capability | food | room | docs | submission
  demand         int, capacity int,
  recommended_action text
);
create table waste_item (                    -- the waste map (Part LXI)
  waste_id       uuid primary key,
  event_id       uuid references event not null,
  as_of          timestamptz not null,
  kind           text not null,              -- BLOCKED_HOURS | UNUSED_MENTOR | UNUSED_COMPUTE | EMPTY_WORKSHOP
                                             --  | DUPLICATED_WORK | IDLE_CAPABILITY | EXCESS_QUEUE | UNUSED_ROOM
  amount         real, unit text
);
create table blocked_time_log (              -- THE KEY EVENT-1 METRIC: Preventable Blocked Minutes (Part XXXVII, LX)
  log_id         uuid primary key,
  team_id        uuid references team not null,
  minutes        int not null check (minutes >= 0),
  cause          text not null,              -- DOCUMENTATION|TOOL_FAILURE|MENTOR_SHORTAGE|CAPABILITY_GAP
                                             --  |RESOURCE_SHORTAGE|SCOPE_ISSUE|OPERATIONS|INFORMATIVE_FAILURE
  preventable    boolean not null,           -- INFORMATIVE_FAILURE (a real algorithm/hypothesis failure) is NOT preventable
  occurred_at    timestamptz not null
);

------------------------------------------------------------------------------------------------
-- ADAPTIVE SCHEDULE / WORKSHOPS / SIDE QUESTS  (Parts XXVI–XXVII, XLII–XLIII)
------------------------------------------------------------------------------------------------
create table adaptive_clinic (               -- a workshop run ONLY because demand emerged (Part XLIII)
  clinic_id      uuid primary key,
  event_id       uuid references event not null,
  topic          text not null,              -- e.g. 'auth'
  triggered_by   text,                        -- e.g. '30% of teams hit auth blocker'
  scheduled_at   timestamptz, duration_min int
);
create table side_quest (                    -- optional extension for teams that finish early (Part XXVII)
  quest_id       uuid primary key,
  event_id       uuid references event not null,
  challenge_level text,                       -- BASE | ADVANCED | FRONTIER (Part XXVI)
  title          text, description text
);
