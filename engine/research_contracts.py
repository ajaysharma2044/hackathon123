"""Research contracts for the agentic discovery system.

This module makes it hard for an LLM or resolver to turn a plausible paragraph into a resolved
research node.  Facts, inferences, hypotheses, and primary-validation questions are distinct; source
quality is explicit; and domain objects resolve only after deterministic completion gates pass.

The contracts are intentionally generic.  Industries, companies, themes, products, buyers, and
research questions are discovered at runtime rather than enumerated here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from typing import Iterable, Mapping, Sequence


class EpistemicStatus(str, Enum):
    EVIDENCE = "EVIDENCE"
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    UNKNOWN = "UNKNOWN"
    PRIMARY_VALIDATION_REQUIRED = "PRIMARY_VALIDATION_REQUIRED"


class SourceTier(int, Enum):
    """Lower is stronger.  Tier 4 is discovery-only and cannot satisfy hard gates by itself."""
    TIER_1_PRIMARY = 1          # company docs/filings, government, academic primary, contracts
    TIER_2_REPUTABLE = 2       # Reuters/Bloomberg/FT/WSJ, high-quality specialist reporting
    TIER_3_CONTEXT = 3         # jobs, conference agendas, LinkedIn company pages, portfolio pages
    TIER_4_DISCOVERY = 4       # aggregators/SEO/unsourced databases


@dataclass(frozen=True)
class SourceRef:
    url: str
    title: str
    tier: SourceTier
    published_at: str | None = None
    source_type: str | None = None
    independent_group: str | None = None
    retrieved_at: str | None = None
    content_sha256: str | None = None

    def __post_init__(self):
        if not self.url or not self.title:
            raise ValueError("source requires url + title")
        if self.tier not in tuple(SourceTier):
            raise ValueError('source tier must be one of the defined quality tiers')


    @property
    def domain(self):
        from urllib.parse import urlparse
        return (urlparse(self.url).hostname or '').lower().removeprefix('www.')

@dataclass(frozen=True)
class EvidenceAnchor:
    source_url: str
    excerpt: str
    content_sha256: str | None = None

    def __post_init__(self):
        if not self.source_url or not self.excerpt.strip():
            raise ValueError('evidence anchor requires source and excerpt')

    @property
    def anchor_id(self):
        import hashlib
        return hashlib.sha256((self.source_url+'\n'+self.excerpt).encode()).hexdigest()[:20]


@dataclass(frozen=True)
class AtomicClaim:
    claim_id: str
    field: str
    statement: str
    status: EpistemicStatus
    sources: tuple[SourceRef, ...] = ()
    confidence: float = 0.5
    contradictory_claim_ids: tuple[str, ...] = ()

    subject_id: str = ''
    value: Any = None
    source_id: str | None = None
    quote_or_excerpt: str = ''
    observed_at: str | None = None
    published_at: str | None = None
    supporting_claim_ids: tuple[str, ...] = ()
    anchors: tuple[EvidenceAnchor, ...] = ()

    def __post_init__(self):
        if not isinstance(self.status, EpistemicStatus):
            raise ValueError('status must be an EpistemicStatus')
        if self.status == EpistemicStatus.INFERENCE and not self.supporting_claim_ids:
            raise ValueError('INFERENCE requires supporting evidence IDs')
        if not self.claim_id or not self.field or not self.statement:
            raise ValueError("claim requires id, field, and statement")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0,1]")
        if self.status == EpistemicStatus.FACT and not self.sources:
            raise ValueError("FACT requires at least one source")
        if self.status in {EpistemicStatus.UNKNOWN, EpistemicStatus.PRIMARY_VALIDATION_REQUIRED} and self.sources:
            # Unknowns may cite why the fact is unavailable in narrative, but they are not evidence claims.
            raise ValueError(f"{self.status.value} must not masquerade as a sourced fact")

    @property
    def strongest_tier(self) -> SourceTier | None:
        return min((s.tier for s in self.sources), default=None)


@dataclass(frozen=True)
class GateRequirement:
    field: str
    min_claims: int = 1
    max_source_tier: SourceTier = SourceTier.TIER_3_CONTEXT
    require_fact: bool = True
    accepted_statuses: tuple[EpistemicStatus, ...] = ()
    applies_to: tuple[str, ...] = ()
    positive: bool = False



@dataclass
class GateResult:
    complete: bool
    missing: list[str] = field(default_factory=list)
    weak: list[str] = field(default_factory=list)
    primary_validation: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CompletionGate:
    gate_id: str
    requirements: tuple[GateRequirement, ...]
    require_counterevidence: bool = True
    require_no_critical_unknowns: bool = True

    def evaluate(self, claims: Iterable[AtomicClaim], critical_unknown_fields: Sequence[str] = (),
                 *, searches=(), profile=None, config=None, supporting_claims=()) -> GateResult:
        from research_config import ResearchConfig
        config = config or ResearchConfig()
        claims = list(claims)
        all_claims = {c.claim_id:c for c in list(supporting_claims) + claims}
        ids = set(all_claims)
        missing, weak, primary = [], [], []
        def valid(c, req):
            statuses = req.accepted_statuses or ((EpistemicStatus.FACT,) if req.require_fact else
                         (EpistemicStatus.FACT, EpistemicStatus.INFERENCE))
            if c.status not in statuses:
                return False
            if c.status in (EpistemicStatus.UNKNOWN, EpistemicStatus.PRIMARY_VALIDATION_REQUIRED):
                return True  # only explicitly optional/status fields permit these
            if c.status == EpistemicStatus.HYPOTHESIS:
                return True  # explicit design proposal, never a required fact
            if c.status == EpistemicStatus.INFERENCE:
                def grounded(item, seen=()):
                    if item.claim_id in seen:return False
                    if item.status == EpistemicStatus.FACT:
                        return item.strongest_tier is not None and item.strongest_tier <= req.max_source_tier
                    if item.status != EpistemicStatus.INFERENCE:return False
                    return bool(item.supporting_claim_ids) and all(i in ids and
                        grounded(all_claims[i], seen+(item.claim_id,)) for i in item.supporting_claim_ids)
                return grounded(c)
            return c.strongest_tier is not None and c.strongest_tier <= req.max_source_tier
        for req in self.requirements:
            if req.applies_to and profile not in req.applies_to:
                continue
            xs = [c for c in claims if c.field == req.field]
            ok = [c for c in xs if valid(c, req) and (not req.positive or c.value is True)]
            if len(ok) < req.min_claims:
                (primary if any(c.status == EpistemicStatus.PRIMARY_VALIDATION_REQUIRED for c in xs)
                 else weak if xs else missing).append(req.field)
            # Search attempts are runtime records, not claims supplied by the extractor.
            angles = {x['query'] for x in searches if req.field in x.get('target_fields', ())
                      and x.get('status') == 'SEARCHED'}
            if len(angles) < config.min_query_angles:
                missing.append('search:' + req.field)
        if self.require_counterevidence:
            negatives = [x for x in searches if x.get('negative_query') and x.get('status') == 'SEARCHED']
            if not negatives:missing.append('counterevidence')
            for req in self.requirements:
                if req.applies_to and profile not in req.applies_to:continue
                if not any(req.field in x.get('target_fields',()) for x in negatives):
                    missing.append('negative_search:' + req.field)
        for c in claims:
            if c.contradictory_claim_ids:
                weak.append('contradiction:' + c.field)
        if self.require_no_critical_unknowns:
            for f in critical_unknown_fields:
                if not any(c.field == f and c.status == EpistemicStatus.FACT for c in claims):
                    primary.append(f)
        from urllib.parse import urlparse
        good = [s for c in all_claims.values() if c.status == EpistemicStatus.FACT for s in c.sources
                if s.tier <= SourceTier.TIER_3_CONTEXT]
        if len({s.url for s in good if s.tier == SourceTier.TIER_1_PRIMARY}) < config.min_primary_sources:
            missing.append('primary_sources')
        if len({s.independent_group or urlparse(s.url).hostname for s in good}) < config.min_independent_sources:
            missing.append('independent_sources')
        return GateResult(not (missing or weak or primary), sorted(set(missing)),
                          sorted(set(weak)), sorted(set(primary)))


# Company research is deliberately generic: no company names or sectors are encoded here.
COMPANY_COMPLETION_GATE = CompletionGate(
    gate_id="company_v1",
    requirements=(
        GateRequirement("identity", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("current_initiative", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("financial_capacity", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("product_business_model", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("strategic_need", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("internal_capability", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("external_incremental_value", require_fact=False),
        GateRequirement("event_answerable_question", require_fact=False),
        GateRequirement("buyer_function", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("substitute", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("event_value_chain", require_fact=False),
        GateRequirement("talent_need_status", accepted_statuses=(EpistemicStatus.FACT, EpistemicStatus.UNKNOWN)),
        GateRequirement("developer_need_status", accepted_statuses=(EpistemicStatus.FACT, EpistemicStatus.UNKNOWN), applies_to=("developer",)),
        GateRequirement("cohort_fit", require_fact=False),
        GateRequirement("natural_activity", require_fact=False),
        GateRequirement("corporate_artifact", require_fact=False),
        GateRequirement("decision_affected", require_fact=False),
        GateRequirement("strongest_objection", require_fact=False),
        GateRequirement("budget_function", accepted_statuses=(EpistemicStatus.FACT, EpistemicStatus.UNKNOWN)),
        GateRequirement("wtp_status", accepted_statuses=(EpistemicStatus.UNKNOWN, EpistemicStatus.PRIMARY_VALIDATION_REQUIRED, EpistemicStatus.FACT)),
    ),
    require_counterevidence=True,
)


THEME_COMPLETION_GATE = CompletionGate(
    gate_id="theme_v1",
    requirements=(
        GateRequirement("economic_problem", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("student_value", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("cornell_fit", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("company_ecosystem", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("event_feasibility", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("commercial_surface", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("falsification", max_source_tier=SourceTier.TIER_3_CONTEXT),
    ),
    require_counterevidence=True,
)


GATES: dict[str, CompletionGate] = {
    "company": COMPANY_COMPLETION_GATE,
    "theme": THEME_COMPLETION_GATE,
}


def get_gate(name: str) -> CompletionGate:
    try:
        return GATES[name]
    except KeyError as exc:
        raise KeyError(f"unknown completion gate {name!r}") from exc

# Type-specific ontology; none of these fields seeds an entity or conclusion.
TYPE_FIELDS = {
    "industry": ("economic_problem", "spending", "technical_transition", "event_connection"),
    "problem": ("economic_problem", "affected_organizations", "uncertainty", "event_connection"),
    "product": ("identity", "documentation", "access", "onboarding", "competitors", "event_connection"),
    "investor": ("identity", "portfolio", "investment_thesis", "event_connection"),
    "technology": ("identity", "technical_transition", "users", "event_connection"),
    "business_unit": ("identity", "product_business_model", "buyer_function", "event_connection"),
    "buyer_function": ("identity", "decision_affected", "budget_function", "event_connection"),
    "cornell": ("capabilities", "access", "student_demand", "uniqueness", "constraints"),
    "cost": ("cost", "cost_scope", "quote_status"),
    "attendance": ("attendance", "recruitment_channel", "conversion_uncertainty"),
    "capacity": ("venue", "staffing", "capacity"),
    "pricing": ("pricing_comparable", "comparable_scope", "wtp_status"),
    "red_team": ("theme", "company_ecosystem", "revenue_assumptions", "research_validity",
        "cornell_uniqueness", "student_experience", "participant_burden", "privacy", "cost",
        "rd_value", "sponsor_demand", "procurement", "repeatability"),
}
for kind, fields in TYPE_FIELDS.items():
    GATES[kind] = CompletionGate(kind, tuple(GateRequirement(f,
        accepted_statuses=(EpistemicStatus.UNKNOWN, EpistemicStatus.PRIMARY_VALIDATION_REQUIRED, EpistemicStatus.FACT)
        if f in ('wtp_status','quote_status','conversion_uncertainty') else ()) for f in fields))
GATES['event_concept'] = THEME_COMPLETION_GATE
DESIGN = (EpistemicStatus.INFERENCE, EpistemicStatus.HYPOTHESIS)
GATES['data_opportunity'] = CompletionGate('data_opportunity', tuple(
    GateRequirement(f, accepted_statuses=DESIGN) for f in (
        'natural_activity', 'capture_plan', 'consent_scope', 'participant_burden', 'research_question',
        'buyer_relevance', 'valid_inference', 'invalid_inference', 'generalizability_limit',
        'sponsor_contamination_risk', 'corporate_deliverable')))
GATES['rd_opportunity'] = CompletionGate('rd_opportunity', tuple(
    GateRequirement(f, require_fact=False, positive=True) for f in (
        'high_uncertainty', 'parallelizable', 'prototypeable', 'evaluable', 'student_fit',
        'failure_information_valuable', 'internal_substitute_researched', 'ip_understood', 'participant_value')))

# Red-team conclusions are interpretations backed by accepted evidence, not invented facts.
GATES['red_team'] = CompletionGate('red_team', tuple(GateRequirement(f, require_fact=False)
    for f in TYPE_FIELDS['red_team']))

# Candidate comparison dimensions are explicit. Unknown dimensions cannot produce a final ranking.
DIMENSIONS = ('student_value','technical_quality','company_value','research_value','rd_value',
    'recruiting_value','repeatability','founder_economics','participant_burden','privacy_risk',
    'research_contamination','operational_complexity','conflict')
GATES['theme'] = GATES['event_concept'] = CompletionGate('theme_v2',
    THEME_COMPLETION_GATE.requirements + tuple(GateRequirement(d, require_fact=False)
        for d in DIMENSIONS if d not in {r.field for r in THEME_COMPLETION_GATE.requirements}))
