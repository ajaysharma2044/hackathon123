-- Builder Network — value-engine + company-offer layer (v004)
-- Backs engine/{value_engines,company_matcher}.py and docs/{structural-archetypes,rd-engine,
-- commercial-engines,company-opportunity-map,icp-by-engine,top-prospects}.md.
-- INVARIANT: the ICP is an OUTPUT (derived from structural fit + evidence), never a stored assumption.
-- Every price is a rational ceiling; wtp_observed stays null until a signed number exists.

create type engine_kind as enum ('RESEARCH','RD','PRODUCT_DEV','ACTIVATION','INNOVATION','SPONSORSHIP','DESIGN_PARTNER');
create type fit_verdict as enum ('ADVANTAGEOUS','INFERIOR','NO_FIT');

-- Historical program dataset (docs/historical-program-dataset.md). UNKNOWN via nulls, never invented.
create table historical_program (
  program_id uuid primary key, name text, organizer text, program_type text,
  year_started int, year_ended int, still_active boolean,
  participant_type text, participant_count int, selection_method text,
  problem_count int, competitive boolean, prize_amount numeric,
  organizer_cost numeric, buyer_fee numeric, research_budget numeric, followon_budget numeric,
  ip_structure text, followon_structure text, participant_compensation text,
  buyer_type text, budget_owner text, output_type text,
  implementation_rate real, renewal_signal text, measured_outcome text, failure_mode text,
  source text, source_quality text, confidence text, epistemic_tag text, notes text
);

-- Structural archetypes (docs/structural-archetypes.md).
create table archetype (
  archetype_id uuid primary key, name text, engine engine_kind,
  input_desc text, mechanism text, output_desc text, buyer text, budget_source text,
  participant_incentive text, ip_model text, followon_model text,
  why_works text, why_fails text, when_hackathon_advantageous text, when_inferior text,
  six_figure_capable boolean
);

-- Company situations + the routed offer (docs/company-opportunity-map.md; engine/company_matcher.py).
create table company_situation (
  situation_id uuid primary key, company_id uuid,   -- references company (schema 001)
  business_unit text, problem text, evidence text, trigger text, decision_owner text,
  budget_owner_candidates text[], current_solution text, why_insufficient text, economic_consequence text,
  developer_facing text, blind_spot text, hackathon_naturalness text, decision_value text,
  budget_signal text, wants_adoption text, participant_fit text,
  problem_uncertainty real, parallelizable real, prototypeable real, evaluable real, needs_deep_domain real,
  captured_at timestamptz
);
create table engine_offer (
  offer_id uuid primary key, situation_id uuid references company_situation,
  engine engine_kind, fit real, verdict fit_verdict,
  price_ceiling_low numeric, price_ceiling_high numeric,   -- rational ceiling, NOT WTP
  wtp_observed numeric,                                    -- null until a signed number exists
  deliverable text, capacity_consumed text, sales_message text, confidence text,
  still_to_learn text, model_version text, generated_at timestamptz
);

-- R&D team-count optimization results (engine/value_engines.py optimal_teams).
create table rd_team_curve (
  problem_id uuid, uncertainty real, n_teams int, expected_value numeric,
  is_optimum boolean, primary key (problem_id, n_teams)
);

-- Multi-engine capacity portfolio (docs/event1-design.md; extends schema/003 event_design).
create table engine_portfolio_selection (
  design_id uuid, engine engine_kind, client_ref text, selected boolean,
  participant_minutes numeric, researcher_hours numeric, category text,
  primary key (design_id, engine, client_ref)
);
