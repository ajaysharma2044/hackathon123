-- Builder Network — economic-laboratory extension (v002)
-- Adds the micro-economy layer: choice sets, resource/incentive flows, sponsor economics, and the
-- question-VOI scoring table. See docs/research-data-model.md ("Compressed Economic Laboratory")
-- and docs/research-modules.md ("Question-VOI"). All flow records reuse the tri-temporal + consent
-- envelope of evidence_event (schema/001_core.sql).

-- Choice ≠ Preference: record what was actually AVAILABLE, not just what was chosen.
create table choice_set (
  choice_set_id  uuid primary key,
  subject_participant uuid references participant,
  subject_team   uuid references team,
  decision_point text not null,                 -- e.g. "database selection @ hour 3"
  occurred_at    timestamptz not null,
  context_snapshot jsonb not null,              -- project_type, time_remaining, team_size, track
  chosen_option_id uuid                         -- fk added after options table
);
create table choice_set_option (
  option_id      uuid primary key,
  choice_set_id  uuid references choice_set,
  product_id     uuid,                          -- references product (schema 001)
  reachability   text not null,                 -- OFFERED | REQUIRED | KNOWN | DISCOVERABLE
  incentive_attached jsonb,                     -- {credits: 100} | {bounty: 500} | null
  prior_familiarity text,                       -- NONE | SOME | USED_BEFORE  (self-reported)
  switching_cost_from_current text
);
alter table choice_set add constraint fk_chosen foreign key (chosen_option_id) references choice_set_option;
-- Enables P(choose X | X, competitorA, competitorB, ..., context) — the quantity a sponsor wants.

-- Resource flows: time, compute, credits, bounties, prizes — the "transaction" in the economic graph.
create table economic_transaction (
  txn_id         uuid primary key,
  subject_participant uuid references participant,
  subject_team   uuid references team,
  product_id     uuid,
  sponsor_id     uuid,
  resource_kind  text not null,                 -- TIME_MIN | COMPUTE | CREDITS | BOUNTY | PRIZE | API_CALLS
  amount         numeric,
  unit           text,
  occurred_at    timestamptz not null,
  observed_at    timestamptz not null,
  available_at   timestamptz not null,
  consent_scope  text[] not null
);

-- Incentives offered (so incentive -> activation -> retention is reconstructable, and varyable).
create table incentive (
  incentive_id   uuid primary key,
  product_id     uuid, sponsor_id uuid,
  kind           text not null,                 -- CREDIT | BOUNTY | PRIZE | FREE_TIER | MENTOR_HOURS
  amount         numeric, currency text,
  offered_to     text,                          -- ALL | TRACK:x | ARM:y  (supports randomized arms)
  offered_at     timestamptz
);

-- Sponsor-side economics: inputs and observable outputs (SponsorROI decomposed, not faked).
create table sponsor_economics (
  sponsor_id     uuid primary key,
  event_id       uuid,
  cash_paid numeric, credits_supplied numeric, engineer_hours numeric, workshop_hours numeric,
  bounty_total numeric, prize_total numeric, participants_exposed int,
  participants_activated int, meaningful_users int, projects_shipped int,
  retained_7d int, retained_30d int, retained_90d int,
  design_partner_leads int, recruiting_leads int, follow_on_conversations int
  -- No single fake ROI number; components stay visible.
);

-- Question-VOI scoring (docs/research-modules.md). Dimensions kept SEPARATE — never one score.
create table research_question_score (
  question_id    uuid primary key,
  question_text  text not null,
  owning_company uuid,                          -- references company (schema 001), the decision owner
  economic_decision_size int, current_uncertainty int, existing_research_spend int,
  internal_data_blind_spot int, hackathon_naturalness int, behavior_observability int,
  experimental_feasibility int, longitudinal_value int, repeatability int, buyer_authority int,
  hackathon_advantage int,                      -- min(naturalness, blind_spot); the kill gate
  opportunity numeric,                          -- 0 if hackathon_advantage below floor
  voi_ceiling_note text,                        -- rational price CEILING, not observed WTP
  wtp_observed numeric,                         -- UNKNOWN until a signed number exists
  verdict text,                                 -- KILL | WEAK | CANDIDATE | PURSUE
  scored_by_model text, scored_at timestamptz
);
