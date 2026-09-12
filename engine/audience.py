"""
Cornell audience model (docs/cornell-audience-map.md; Parts I-II).

Event 1 is CORNELL-ONLY. This models Cornell student subpopulations at the POPULATION level — never
individuals, never a "quality"/intelligence/employability score (a hard ethical boundary). Segment
DEFINITIONS (codes, skills, the talent labels each maps to) live here; accessible-population COUNTS
default to None/UNKNOWN and are filled only from the cited seed sweep (docs/cornell-audience-map.md).
We do not fabricate enrollment numbers.

The bridge to the rest of the engine: `to_talent_mix` turns a chosen cohort (segment -> count) into an
`environment.Environment.talent_mix`, and the talent labels align with
`problem_matcher.COMPONENT_TALENT`, so a Cornell cohort can be matched to problems by the existing
Fit(P,E) machinery.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict

# Talent labels shared with problem_matcher.COMPONENT_TALENT (so audience -> Fit works).
# SOFTWARE, ML_RESEARCH, DATA_SCIENCE, HARDWARE, DESIGN, PRODUCT, OR_IE, OPERATIONS, SUPPLY_CHAIN,
# SCIENCE, QUANT, BUSINESS.


@dataclass
class AudienceSegment:
    code: str
    name: str
    talent_labels: tuple                 # maps to problem_matcher.COMPONENT_TALENT labels
    skills: tuple = ()
    typical_tools: tuple = ()
    buildable_24_48_72: str = ""
    strengths: str = ""
    weaknesses: str = ""
    resembles_corporate: str = ""        # which corporate audience they resemble
    not_resembles: str = ""              # which they emphatically do NOT resemble
    do_not_use_for: str = ""
    accessible_population: int = None     # None = UNKNOWN until the cited sweep fills it
    population_status: str = "UNKNOWN"    # KNOWN | LIKELY | UNKNOWN


# Segment DEFINITIONS for a Cornell hackathon. Populations are UNKNOWN by design — the sweep supplies
# cited figures. These definitions are structural (which disciplines exist and what they can build),
# not claims about how many students there are.
CORNELL_SEGMENTS = {
    "AI_ML": AudienceSegment(
        "AI_ML", "AI / ML builders", ("ML_RESEARCH", "DATA_SCIENCE"),
        skills=("model training", "LLM apps", "agents", "eval"),
        typical_tools=("PyTorch", "HF", "OpenAI/Anthropic APIs", "LangChain"),
        buildable_24_48_72="a working ML/agent prototype on real data",
        strengths="fluent with current AI tooling; greenfield tool choice",
        weaknesses="production hardening; domain ground truth",
        resembles_corporate="early-adopter AI engineers",
        not_resembles="regulated-enterprise ML with legacy constraints",
        do_not_use_for="representative enterprise ML adoption"),
    "SOFTWARE_FULLSTACK": AudienceSegment(
        "SOFTWARE_FULLSTACK", "Full-stack / infra software", ("SOFTWARE",),
        skills=("web/backend", "APIs", "cloud", "devtools"),
        typical_tools=("React", "Node/Python", "AWS/GCP", "Docker"),
        buildable_24_48_72="a deployed full-stack app integrating several APIs",
        strengths="fast integration; unconstrained stack choice",
        weaknesses="scale/ops; enterprise security",
        resembles_corporate="startup / greenfield developers",
        not_resembles="enterprise devs bound by procurement/legacy",
        do_not_use_for="legacy-migration realism"),
    "ORIE_OPTIMIZATION": AudienceSegment(
        "ORIE_OPTIMIZATION", "ORIE / operations research", ("OR_IE", "OPERATIONS"),
        skills=("optimization", "simulation", "stochastic modeling", "supply chain"),
        typical_tools=("Gurobi", "Python/OR-Tools", "SimPy"),
        buildable_24_48_72="an optimization/simulation model of a real ops problem",
        strengths="operations/optimization problems; simulation",
        weaknesses="domain specifics; real proprietary data access",
        resembles_corporate="ops-research / IE analysts",
        not_resembles="frontline operators with tacit knowledge",
        do_not_use_for="problems needing deep tacit domain ops knowledge"),
    "ECE_HARDWARE": AudienceSegment(
        "ECE_HARDWARE", "ECE / embedded / hardware", ("HARDWARE",),
        skills=("embedded", "signal/PCB", "firmware"),
        buildable_24_48_72="a hardware/embedded demo or instrument",
        strengths="physical prototypes; sensing",
        weaknesses="manufacturing; certification",
        resembles_corporate="hardware/embedded engineers",
        not_resembles="high-volume manufacturing teams",
        do_not_use_for="manufacturing-scale realism"),
    "ROBOTICS_AUTONOMY": AudienceSegment(
        "ROBOTICS_AUTONOMY", "Robotics / autonomous systems", ("HARDWARE", "SOFTWARE", "SCIENCE"),
        skills=("controls", "perception", "autonomy", "systems integration"),
        buildable_24_48_72="an autonomy/controls prototype (project-team caliber)",
        strengths="systems integration under constraints",
        weaknesses="field robustness; safety certification",
        resembles_corporate="autonomy R&D teams",
        not_resembles="deployed safety-certified systems",
        do_not_use_for="field-generalization claims"),
    "QUANT_FINANCE": AudienceSegment(
        "QUANT_FINANCE", "Quant / trading / fintech", ("QUANT",),
        skills=("quant modeling", "market microstructure", "risk"),
        buildable_24_48_72="a quant model / backtest / market-design sim",
        strengths="quantitative modeling; incentive/market design",
        weaknesses="regulated production; capital",
        resembles_corporate="quant researchers",
        not_resembles="regulated trading desks",
        do_not_use_for="compliance-bound trading realism"),
    "STATS_DATA": AudienceSegment(
        "STATS_DATA", "Statistics / data science", ("DATA_SCIENCE", "QUANT"),
        skills=("statistics", "causal inference", "data engineering"),
        buildable_24_48_72="an analysis / causal study / data product",
        strengths="rigorous measurement; causal design",
        weaknesses="domain ground truth",
        resembles_corporate="data-science / research-ops teams",
        not_resembles="business analysts with domain tenure",
        do_not_use_for="deep-domain interpretation"),
    "PRODUCT_DESIGN": AudienceSegment(
        "PRODUCT_DESIGN", "Product / design / UX", ("DESIGN", "PRODUCT"),
        skills=("UX", "product", "prototyping", "user research"),
        buildable_24_48_72="a designed prototype + user-flow",
        strengths="divergent product interpretations; UX",
        weaknesses="engineering depth",
        resembles_corporate="product/design teams",
        not_resembles="enterprise buyers",
        do_not_use_for="technical feasibility depth"),
    "MECHE_APPLIEDPHYS": AudienceSegment(
        "MECHE_APPLIEDPHYS", "MechE / Applied Physics", ("HARDWARE", "SCIENCE"),
        skills=("mechanical design", "simulation", "physical modeling"),
        buildable_24_48_72="a CAD/sim or physical prototype",
        strengths="physical/scientific modeling",
        weaknesses="software integration",
        resembles_corporate="mechanical / R&D engineers",
        not_resembles="production manufacturing",
        do_not_use_for="software-adoption studies"),
    "BUSINESS_FOUNDER": AudienceSegment(
        "BUSINESS_FOUNDER", "Business / founder (Dyson/eLab)", ("BUSINESS",),
        skills=("business models", "GTM", "venture"),
        buildable_24_48_72="a business model / venture concept + validation",
        strengths="venture framing; commercialization",
        weaknesses="technical build depth",
        resembles_corporate="founders / BD",
        not_resembles="enterprise procurement",
        do_not_use_for="technical feasibility evidence"),
}


def to_talent_mix(cohort_counts: dict) -> tuple:
    """Turn a chosen cohort (segment_code -> count) into an environment.Environment.talent_mix:
    a tuple of (talent_label, share). A segment's headcount is spread evenly across its talent
    labels, then normalized. Unknown codes raise (no silent miscount)."""
    weights = defaultdict(float)
    for code, n in cohort_counts.items():
        seg = CORNELL_SEGMENTS[code]
        if not seg.talent_labels:
            continue
        per = n / len(seg.talent_labels)
        for lbl in seg.talent_labels:
            weights[lbl] += per
    total = sum(weights.values())
    if total <= 0:
        return ()
    return tuple((lbl, round(w / total, 4)) for lbl, w in sorted(weights.items(), key=lambda kv: -kv[1]))


def segments_for_talent(label: str) -> list:
    """Which Cornell segments supply a given talent label (reverse lookup for demand-driven selection)."""
    return [code for code, s in CORNELL_SEGMENTS.items() if label in s.talent_labels]


def unresolved_populations() -> list:
    """Segments whose accessible population is still UNKNOWN — the honest sweep to-do list."""
    return [code for code, s in CORNELL_SEGMENTS.items() if s.accessible_population is None]
