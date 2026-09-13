-- 014_economic_discovery.sql
-- Persistent economy graph + research provenance for the Run-2 Agentic OS.
-- Never overwrites earlier migration history.

CREATE TABLE IF NOT EXISTS research_evidence (
    evidence_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    resolver TEXT NOT NULL,
    claim TEXT NOT NULL,
    value_json TEXT,
    source_url TEXT NOT NULL,
    source_title TEXT,
    source_type TEXT NOT NULL,
    research_mode TEXT NOT NULL CHECK (research_mode IN ('SESSION_ASSISTED','SELF_CONTAINED')),
    observed_at TEXT NOT NULL,
    ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS economic_entity (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    canonical_key TEXT NOT NULL,
    attrs_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'UNKNOWN',
    stop_reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, canonical_key)
);

CREATE TABLE IF NOT EXISTS economic_edge (
    edge_id TEXT PRIMARY KEY,
    src_entity_id TEXT NOT NULL REFERENCES economic_entity(entity_id),
    dst_entity_id TEXT NOT NULL REFERENCES economic_entity(entity_id),
    edge_type TEXT NOT NULL,
    attrs_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(src_entity_id, dst_entity_id, edge_type)
);

CREATE TABLE IF NOT EXISTS edge_evidence (
    edge_id TEXT NOT NULL REFERENCES economic_edge(edge_id),
    evidence_id TEXT NOT NULL REFERENCES research_evidence(evidence_id),
    PRIMARY KEY(edge_id, evidence_id)
);

CREATE TABLE IF NOT EXISTS contradiction (
    contradiction_id TEXT PRIMARY KEY,
    node_or_entity_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    claim_a_json TEXT NOT NULL,
    claim_b_json TEXT NOT NULL,
    evidence_a_id TEXT REFERENCES research_evidence(evidence_id),
    evidence_b_id TEXT REFERENCES research_evidence(evidence_id),
    resolution_status TEXT NOT NULL DEFAULT 'OPEN',
    resolution_task_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS account_value_surface (
    surface_id TEXT PRIMARY KEY,
    organization_entity_id TEXT NOT NULL REFERENCES economic_entity(entity_id),
    surface_type TEXT NOT NULL,
    natural_participant_activity TEXT,
    deliverable TEXT,
    decision_affected TEXT,
    decision_owner TEXT,
    budget_owner TEXT,
    status TEXT NOT NULL DEFAULT 'HYPOTHESIS',
    evidence_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS commercial_offer (
    offer_id TEXT PRIMARY KEY,
    organization_entity_id TEXT NOT NULL REFERENCES economic_entity(entity_id),
    offer_type TEXT NOT NULL,
    deliverable TEXT NOT NULL,
    observed_wtp_status TEXT NOT NULL DEFAULT 'UNKNOWN',
    observed_wtp_amount REAL,
    comparable_low REAL,
    comparable_high REAL,
    rational_value_ceiling REAL,
    recommended_initial_ask REAL,
    negotiation_floor REAL,
    incremental_delivery_cost REAL,
    cash_value REAL NOT NULL DEFAULT 0,
    in_kind_face_value REAL NOT NULL DEFAULT 0,
    actual_cost_avoided REAL NOT NULL DEFAULT 0,
    CHECK (observed_wtp_status <> 'UNKNOWN' OR observed_wtp_amount IS NULL)
);

CREATE TABLE IF NOT EXISTS activity_output_edge (
    activity_id TEXT NOT NULL,
    output_id TEXT NOT NULL,
    commercial_product TEXT,
    buyer_entity_id TEXT REFERENCES economic_entity(entity_id),
    decision_affected TEXT,
    value_type TEXT,
    participant_burden TEXT,
    natural_without_payment INTEGER NOT NULL,
    PRIMARY KEY(activity_id, output_id, buyer_entity_id)
);

CREATE TABLE IF NOT EXISTS commercial_conflict (
    conflict_id TEXT PRIMARY KEY,
    left_offer_id TEXT REFERENCES commercial_offer(offer_id),
    right_offer_id TEXT REFERENCES commercial_offer(offer_id),
    conflict_type TEXT NOT NULL,
    reason TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN'
);

CREATE TABLE IF NOT EXISTS research_task (
    research_task_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    question TEXT NOT NULL,
    decision_impact TEXT NOT NULL,
    uncertainty TEXT NOT NULL,
    sensitivity TEXT NOT NULL,
    resolution_feasibility TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN',
    assigned_agent TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
