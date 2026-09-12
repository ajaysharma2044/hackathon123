-- Builder Network — EVENT OPERATIONS schema (v007)
-- Postgres flavor. The organizational + logistical machinery that RUNS Event 1 (the front end),
-- and the edges that tie it to the research layer. See docs/event-ops/* for the operating model;
-- runnable structure is in engine/staffing_model.py, engine/judging_assignment.py, engine/org_graph.py.
--
-- EXTENDS schema/001_core.sql (event, team, participant, project, sponsor, product) and
-- schema/006_live_research.sql (mentor, support_request, researcher, research_shift). Nothing here
-- is redefined; new objects only. The research org is modeled in 006; this file models the EVENT
-- org and the ops↔research correlation edges (role_dependency).
--
-- GUIDING FACTS (sourced — see docs/event-ops/prior-hackathons.md):
--   * Organizer teams (MLH): Lead + Logistics, Finance/Sponsorship, Marketing, Operations; extended
--     committees add Tech/AV, Design, Participant Experience, Judging & Awards, Mentorship, Safety.
--   * Judges needed J = ceil(P*n*t / T): projects × rounds × minutes-per-project / total-judging-minutes
--     (MLH default n=3 rounds, t=4 min). Science-fair format; stack-rank top-3 (3/2/1) to de-bias judges.
--   * Mentor models: vertical (per-team) / horizontal (pool) / mixed; newcomer groups ~1:2–1:6.
--   * Premium fly-in (TreeHacks/Cal Hacks): funded travel, selective admission, accepted≈attend.

------------------------------------------------------------------------------------------------
-- ORGANIZATION  (the committee structure + the people who hold roles)
------------------------------------------------------------------------------------------------
create type org_layer as enum (
  'ORGANIZER',    -- directors + committee heads who plan and run the event
  'CREW',         -- paid/lead staff executing a domain day-of (AV, F&B lead, logistics crew)
  'MENTOR',       -- technical help (modeled in 006.mentor; referenced here)
  'JUDGE',        -- evaluates submissions
  'VOLUNTEER',    -- shift-based day-of help (check-in, floaters, runners)
  'RESEARCH',     -- the live-research org (modeled in 006.researcher; referenced here)
  'PARTICIPANT'   -- the builders (modeled in 001.participant; referenced here)
);
create type org_unit_code as enum (
  'EXECUTIVE','LOGISTICS','FINANCE_SPONSORSHIP','MARKETING','OPERATIONS','TECH_AV','DESIGN',
  'PARTICIPANT_EXPERIENCE','JUDGING_AWARDS','MENTORSHIP','SAFETY','RESEARCH'
);
create table org_unit (
  unit_code       org_unit_code primary key,
  description     text not null,
  head_role_id    uuid                       -- fk set after staff_role rows exist (the committee head)
);

create table staff_role (                     -- the role CATALOG (a definition, not a person)
  role_id         uuid primary key,
  name            text not null,              -- e.g. 'Event Director', 'Logistics Lead', 'AV Crew'
  layer           org_layer not null,
  unit_code       org_unit_code references org_unit,
  reports_to      uuid references staff_role, -- the org chart edge (null = top)
  is_paid         boolean not null default false,
  staffing_note   text                        -- how the count is derived (ratio/formula); see staffing_model.py
);
alter table org_unit add constraint fk_unit_head foreign key (head_role_id) references staff_role;

create table staff (                          -- a human holding an organizer/crew/volunteer/judge role
  staff_id        uuid primary key,
  event_id        uuid references event not null,
  display_name    text not null,
  role_id         uuid references staff_role not null,
  affiliation     text,                       -- 'cornell' | 'sponsor:<name>' | 'vendor' | 'external'
  is_neutral      boolean not null default true,  -- false for a sponsor employee (conflict flag)
  coc_acknowledged_at timestamptz             -- code-of-conduct acknowledgement (required to work)
);

------------------------------------------------------------------------------------------------
-- SHIFTS & COVERAGE  (who is on, when, where — the run-of-show staffing)
------------------------------------------------------------------------------------------------
create table ops_shift (                       -- a general event shift (research_shift lives in 006)
  shift_id        uuid primary key,
  event_id        uuid references event not null,
  role_id         uuid references staff_role,
  starts_at       timestamptz not null,
  ends_at         timestamptz not null,
  zone            text,
  min_headcount   int not null default 1,      -- coverage floor for this shift
  is_overnight    boolean not null default false,
  check (starts_at < ends_at)
);
create table shift_assignment (
  shift_id        uuid references ops_shift not null,
  staff_id        uuid references staff not null,
  checked_in_at   timestamptz,                 -- did they actually show for the shift
  primary key (shift_id, staff_id)
);

------------------------------------------------------------------------------------------------
-- JUDGING  (science-fair + finals; see engine/judging_assignment.py, docs/event-ops/judging-system.md)
------------------------------------------------------------------------------------------------
create table judge (
  judge_id        uuid primary key,
  event_id        uuid references event not null,
  display_name    text not null,
  expertise       text[],                      -- categories they can judge (AI, infra, design, ...)
  affiliation     text,                        -- 'neutral' | 'sponsor:<name>'
  is_sponsor_judge boolean not null default false,  -- judges a sponsor/category prize specifically
  coc_acknowledged_at timestamptz
);
create table submission (                      -- a team's judged artifact (Devpost-style entry)
  submission_id   uuid primary key,
  team_id         uuid references team not null,
  project_id      uuid references project,
  event_id        uuid references event not null,
  table_number    text,                        -- science-fair station
  repo_url        text, deploy_url text, devpost_url text,
  category_tags   text[],                       -- which prizes/categories it competes for
  submitted_at    timestamptz
);
create table judging_round (
  round_id        uuid primary key,
  event_id        uuid references event not null,
  kind            text not null,               -- SCIENCE_FAIR | FINALS | SPONSOR_CATEGORY
  rounds_per_project int not null default 3,    -- MLH default n=3
  minutes_per_project int not null default 4,   -- MLH default t=4 (2 demo + 1 Q + 1 travel)
  total_minutes   int not null                  -- T: the judging window
);
create table judging_assignment (              -- judge × submission × round (the rotation)
  assignment_id   uuid primary key,
  round_id        uuid references judging_round not null,
  judge_id        uuid references judge not null,
  submission_id   uuid references submission not null,
  conflict_blocked boolean not null default false,  -- true if judge is conflicted (own team/sponsor)
  unique (round_id, judge_id, submission_id)
);
create table judging_score (                   -- stack-rank points, NOT absolute scores (de-bias)
  assignment_id   uuid references judging_assignment primary key,
  rank_in_batch   int,                          -- 1/2/3 within what this judge saw
  points          int,                          -- 3/2/1 mapped from rank (normalizes strict/lenient judges)
  rubric          jsonb,                        -- optional per-criterion notes (tech/creativity/impact/...)
  recorded_at     timestamptz
);
create table prize (
  prize_id        uuid primary key,
  event_id        uuid references event not null,
  name            text not null,
  kind            text not null,               -- GRAND | CATEGORY | SPONSOR | R&D_CHALLENGE
  sponsor_id      uuid references sponsor,
  ip_terms        text                          -- decided BEFORE the event (see recruiting-legal.md)
);
create table prize_award (
  prize_id        uuid references prize not null,
  team_id         uuid references team not null,
  rank            int,
  primary key (prize_id, team_id)
);

------------------------------------------------------------------------------------------------
-- LOGISTICS  (venue, food, travel, resources, tasks — docs/event-ops/logistics.md)
------------------------------------------------------------------------------------------------
create table logistics_task (                  -- the checklist; each task owned by a unit, time-offset
  task_id         uuid primary key,
  event_id        uuid references event not null,
  unit_code       org_unit_code references org_unit not null,
  title           text not null,
  due_offset_days int not null,                 -- days relative to event start (negative = before)
  status          text not null default 'OPEN', -- OPEN | IN_PROGRESS | DONE | BLOCKED
  owner_staff     uuid references staff,
  blocking        boolean not null default false  -- is this on the critical path?
);
create table venue_resource (                  -- power, wifi, tables, rooms, AV — with capacity
  resource_id     uuid primary key,
  event_id        uuid references event not null,
  kind            text not null,               -- POWER_STRIP | WIFI_AP | HACK_TABLE | WORKSHOP_ROOM
                                               --  | SLEEP_ROOM | AV_KIT | HARDWARE_LAB | SIGNAGE
  quantity        int not null,
  capacity_each   int,                          -- e.g. seats per table, devices per AP
  note            text
);
create table meal_service (                    -- F&B schedule; dietary coverage is mandatory
  meal_id         uuid primary key,
  event_id        uuid references event not null,
  label           text not null,               -- 'Fri dinner' | 'Sat 2am snack'
  served_at       timestamptz not null,
  headcount       int not null,
  vendor          text,
  dietary_options text[] not null default '{}'  -- vegetarian/vegan/gluten-free/halal/kosher
);
create table travel_grant (                    -- the premium fly-in: funded, admission-blind
  grant_id        uuid primary key,
  participant_id  uuid references participant not null,
  event_id        uuid references event not null,
  region          text,                         -- regional caps (Cal Hacks model)
  amount          numeric,
  status          text not null default 'OFFERED',  -- OFFERED | ACCEPTED | REIMBURSED | DECLINED
  -- NOTE: travel-grant decisions are made AFTER admission and must not bias selection
  --       (admission-blind, per docs/event-ops/prior-hackathons.md).
  affects_admission boolean not null default false check (affects_admission = false)
);

------------------------------------------------------------------------------------------------
-- SAFETY  (code of conduct + incident handling — a participant-experience hard requirement)
------------------------------------------------------------------------------------------------
create table safety_incident (
  incident_id     uuid primary key,
  event_id        uuid references event not null,
  occurred_at     timestamptz not null,
  kind            text not null,               -- COC_VIOLATION | MEDICAL | FACILITIES | SECURITY
  severity        text not null,               -- LOW | MED | HIGH | CRITICAL
  reported_to     uuid references staff,        -- the Safety lead / on-call organizer
  resolution      text,
  -- Safety incidents are OPERATIONS data. They are NOT research data and never enter a client
  --   deliverable or any participant research record. (firewall — see role_dependency below)
  is_research     boolean not null default false check (is_research = false)
);

------------------------------------------------------------------------------------------------
-- THE CORRELATION GRAPH  (how every role ties to every other — engine/org_graph.py)
------------------------------------------------------------------------------------------------
-- This is the structural answer to "show how it is all tied together": a typed edge between two
-- roles/units. It spans BOTH the event org and the research org (006), so the ops↔research
-- interlock is a first-class, queryable object rather than prose.
create type dependency_kind as enum (
  'REPORTS_TO',     -- org-chart hierarchy
  'HANDOFF',        -- one role hands work to another (registration → participant-experience)
  'DEPENDS_ON',     -- one role cannot function without another (judging → submissions from ops)
  'ESCALATES_TO',   -- problem escalation (volunteer → safety lead)
  'STAFFS',         -- supplies people to (sponsorship → sponsor mentors/judges)
  'FEEDS_RESEARCH', -- an ops role that generates research evidence (mentor → mentor_interaction)
  'CONSTRAINED_BY'  -- a research rule binds an ops role (any role → burden budget / consent gate)
);
create table role_dependency (
  edge_id         uuid primary key,
  from_role       text not null,               -- role or unit name (free-form to span both orgs)
  to_role         text not null,
  kind            dependency_kind not null,
  description     text not null,
  is_cross_layer  boolean not null default false  -- true when it crosses the ops↔research boundary
);
create index on role_dependency (kind);
create index on role_dependency (is_cross_layer);
