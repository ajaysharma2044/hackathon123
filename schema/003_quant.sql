-- Builder Network — quantitative decision layer (v003)
-- Belief state, distributions with provenance, buyer latent state, VOI evaluations, event designs,
-- Monte Carlo results, study positions, and the calibration/prediction ledger.
-- See docs/quant-engine.md. Engine: engine/{beliefs,monte_carlo,voi,portfolio,calibration,event_optimizer}.py
-- INVARIANT: no uncertain business quantity is stored as a bare number. It is a distribution with
-- provenance and a status (OBSERVED | ASSUMED | UNKNOWN). UNKNOWN cannot be silently sampled.

create type belief_status as enum ('OBSERVED','ASSUMED','UNKNOWN');
create type dist_family   as enum ('POINT','UNIFORM','BETA','NORMAL','LOGNORMAL','TRIANGULAR_SCENARIO','CATEGORICAL');

create table belief (
  belief_id      uuid primary key,
  name           text not null,                 -- e.g. "close.anthropic", "wtp.stripe", "attendance.rate"
  family         dist_family,                   -- null iff status=UNKNOWN
  params         jsonb,                          -- {a,b} | {mu,sigma} | {bear,base,bull} | ...
  status         belief_status not null,
  source         text not null, reason text not null, confidence real,
  calibration_status text default 'UNCALIBRATED',
  created_at timestamptz, available_at timestamptz, last_updated_at timestamptz
);

-- Evidence updates (Bayesian where justified). Reliability-weighted; a signed deal >> a comparable.
create table evidence_update (
  update_id      uuid primary key,
  belief_id      uuid references belief,
  evidence_kind  text not null,                 -- SIGNED_COMMERCIAL|DIRECT_OBSERVATION|EMPIRICAL_RATE|
                                                --  BUYER_STATED|EXTERNAL_COMPARABLE|EXPERT_PRIOR|MODEL_ESTIMATE
  reliability_weight real not null,
  successes real, failures real,                -- for Beta-Binomial rate updates
  note text, applied_at timestamptz
);

-- Business hypotheses with prior/posterior + falsification threshold (extends schema/001 hypothesis).
create table business_hypothesis (
  hypothesis_id  uuid primary key,
  statement      text not null,
  prior_belief_id uuid references belief,
  posterior_belief_id uuid references belief,
  falsification_threshold text not null,
  decision_relevance text, model_version text, updated_at timestamptz
);

-- Latent buyer state (docs/quant-engine.md Part 4). Each dimension a belief, updated by signals.
create table buyer_state (
  company_id     uuid primary key,              -- references company (schema 001)
  pain uuid, urgency uuid, mandate_strength uuid, decision_value uuid, blind_spot uuid,
  hackathon_advantage uuid, budget uuid, champion_strength uuid, procurement_friction uuid,
  research_habit uuid, price_sensitivity uuid, time_to_decision uuid, renewal_potential uuid,
  -- each column references belief(belief_id); close prob & contract value derived from these
  p_close_belief uuid references belief, contract_value_belief uuid references belief,
  updated_at timestamptz
);

-- Value of Information evaluations (should we research more, or act?).
create table voi_evaluation (
  voi_id         uuid primary key,
  question       text not null,                 -- the uncertainty being resolved
  action_set     jsonb,                          -- candidate actions
  evpi numeric, evsi numeric, sample_size int, research_cost numeric, net_voi numeric,
  recommendation text,                           -- 'GATHER_EVIDENCE' | 'ACT_NOW' | 'ABANDON'
  model_version text, evaluated_at timestamptz
);

-- Event designs as decision vectors + their Monte Carlo economic results.
create table event_design (
  design_id      uuid primary key, name text,
  decision_vector jsonb not null,               -- n_builders, duration_h, free_choice_share, ...
  is_hard_constraint_feasible boolean
);
create table event_scenario_result (
  result_id      uuid primary key,
  design_id      uuid references event_design,
  scenario       text,                           -- bear|base|bull|custom
  experience real, research_info real, longterm real,
  econ_mean numeric, econ_p5 numeric, econ_p95 numeric, p_breakeven real,
  var95 numeric, cvar95 numeric, on_pareto_frontier boolean,
  assumptions_ref text,                          -- pointer to docs/quant-assumptions.md version
  model_version text, computed_at timestamptz
);

-- Study portfolio positions (docs/quant-engine.md Part 19).
create table study_position (
  study_id       uuid primary key,
  name text, category text, exp_value numeric, info_value numeric,
  participant_minutes numeric, researcher_hours numeric, conflicts text[],
  selected_in_design uuid references event_design
);

-- Calibration ledger (Part 17). Predictions are never overwritten; outcomes resolve them.
create table prediction (
  prediction_id  uuid primary key,
  key text not null,                             -- what is being predicted (deal id, attendance, ...)
  predicted_prob real, lower real, upper real,   -- point + interval
  input_snapshot jsonb, model_version text not null,
  predicted_at timestamptz not null,
  actual_outcome real, evaluated_at timestamptz  -- null until resolved
);
-- Brier / log-loss / ECE / interval-coverage computed over resolved rows in engine/calibration.py.
