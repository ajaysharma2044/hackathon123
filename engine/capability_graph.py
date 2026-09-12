"""
Professional capability ontology + artifact->capability evidence mapping
(docs/talent/capability-ontology.md; Parts VI-VIII).

Separates SELF_REPORTED skill from ARTIFACT_SUPPORTED experience. Artifact evidence supports
EXPERIENCE IN an area — it never proves mastery, seniority, intelligence, or future performance
(Part VIII). The ontology is extensible.
"""
from __future__ import annotations

# capability -> subskills. Extensible; add nodes without touching consumers.
CAPABILITY_ONTOLOGY = {
    "BACKEND": ["API_DESIGN", "AUTH", "PERSISTENCE", "QUEUES", "CACHING", "DEPLOYMENT"],
    "FRONTEND": ["UI", "STATE_MGMT", "PERFORMANCE", "ACCESSIBILITY"],
    "MOBILE": ["IOS", "ANDROID", "CROSS_PLATFORM"],
    "ML": ["TRAINING", "EVALUATION", "INFERENCE", "DATA_PIPELINES"],
    "LLM": ["PROMPTING", "AGENTS", "RAG", "EVAL_HARNESS", "FINE_TUNING"],
    "DATA_ENGINEERING": ["ETL", "STREAMING", "WAREHOUSE", "ORCHESTRATION"],
    "DATA_SCIENCE": ["STATISTICS", "CAUSAL_INFERENCE", "VISUALIZATION"],
    "OPTIMIZATION": ["LP_MIP", "HEURISTICS", "SIMULATION"],
    "ORIE": ["STOCHASTIC_MODELING", "SUPPLY_CHAIN", "SCHEDULING"],
    "QUANT": ["MARKET_MODELING", "BACKTESTING", "RISK"],
    "SECURITY": ["APPSEC", "CRYPTO", "RED_TEAM"],
    "DEVOPS": ["CI_CD", "OBSERVABILITY", "IAC"],
    "CLOUD": ["AWS", "GCP", "AZURE", "SERVERLESS"],
    "DATABASES": ["SQL", "NOSQL", "VECTOR", "INDEXING"],
    "DISTRIBUTED_SYSTEMS": ["CONSENSUS", "SHARDING", "LOW_LATENCY"],
    "HARDWARE": ["PCB", "FIRMWARE", "SIGNAL"],
    "EMBEDDED": ["RTOS", "SENSORS", "CONTROL"],
    "ROBOTICS": ["PERCEPTION", "CONTROLS", "AUTONOMY"],
    "PRODUCT": ["DISCOVERY", "SPEC", "USER_RESEARCH"],
    "DESIGN": ["UX", "UI_DESIGN", "PROTOTYPING"],
    "RESEARCH": ["EXPERIMENT_DESIGN", "WRITEUP"],
}

# technology -> (capability, subskill) evidence. Presence in an artifact supports EXPERIENCE, not skill
# level. Extend freely.
TECH_TO_CAPABILITY = {
    "fastapi": ("BACKEND", "API_DESIGN"), "flask": ("BACKEND", "API_DESIGN"),
    "django": ("BACKEND", "API_DESIGN"), "postgres": ("DATABASES", "SQL"),
    "postgresql": ("DATABASES", "SQL"), "redis": ("BACKEND", "CACHING"),
    "docker": ("DEVOPS", "IAC"), "kubernetes": ("DEVOPS", "IAC"),
    "react": ("FRONTEND", "UI"), "nextjs": ("FRONTEND", "UI"),
    "pytorch": ("ML", "TRAINING"), "tensorflow": ("ML", "TRAINING"),
    "langchain": ("LLM", "AGENTS"), "llamaindex": ("LLM", "RAG"),
    "gurobi": ("OPTIMIZATION", "LP_MIP"), "ortools": ("OPTIMIZATION", "LP_MIP"),
    "simpy": ("OPTIMIZATION", "SIMULATION"), "spark": ("DATA_ENGINEERING", "ETL"),
    "kafka": ("DATA_ENGINEERING", "STREAMING"), "aws": ("CLOUD", "AWS"),
    "gcp": ("CLOUD", "GCP"), "pinecone": ("DATABASES", "VECTOR"),
}


def all_capabilities() -> list:
    return list(CAPABILITY_ONTOLOGY.keys())


def subskills(capability: str) -> list:
    return CAPABILITY_ONTOLOGY.get(capability, [])


def is_capability(code: str) -> bool:
    return code in CAPABILITY_ONTOLOGY or any(code in v for v in CAPABILITY_ONTOLOGY.values())


def capabilities_from_technologies(techs) -> list:
    """Map a list of technologies (e.g. from a dependency manifest) to ARTIFACT_SUPPORTED capability
    evidence. Returns dicts, each tagged support_kind=ARTIFACT_SUPPORTED and a human note. Unknown
    technologies are simply skipped — never counted against anyone."""
    out = []
    for t in techs:
        key = str(t).strip().lower()
        if key in TECH_TO_CAPABILITY:
            cap, sub = TECH_TO_CAPABILITY[key]
            out.append({"capability": cap, "subskill": sub, "support_kind": "ARTIFACT_SUPPORTED",
                        "note": f"artifact uses {t}"})
    return out


def self_reported_capability(code: str) -> dict:
    """Wrap a self-reported skill. Kept DISTINCT from artifact-supported evidence (Part VI)."""
    return {"capability": code, "support_kind": "SELF_REPORTED",
            "note": "self-reported; not artifact-verified"}
