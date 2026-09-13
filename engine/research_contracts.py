"""Evidence contracts and deterministic completion gates for agentic research.

Retrieval produces evidence; models may interpret it, but they may not invent facts. Facts require
exact source anchors, inferences require supporting claim ids, and completion is determined by code.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence
from urllib.parse import urlparse
import hashlib


class EpistemicStatus(str, Enum):
    EVIDENCE = "EVIDENCE"
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    UNKNOWN = "UNKNOWN"
    PRIMARY_VALIDATION_REQUIRED = "PRIMARY_VALIDATION_REQUIRED"


class SourceTier(int, Enum):
    TIER_1_PRIMARY = 1
    TIER_2_REPUTABLE = 2
    TIER_3_CONTEXT = 3
    TIER_4_DISCOVERY = 4


@dataclass(frozen=True)
class SourceRef:
    url: str
    title: str
    tier: SourceTier
    published_at: str | None = None
    source_type: str | None = None
    retrieved_at: str | None = None
    content_sha256: str | None = None

    def __post_init__(self):
        if not self.url or not self.title:
            raise ValueError("source requires url + title")
        if urlparse(self.url).scheme not in {"http", "https"}:
            raise ValueError("source url must be http(s)")

    @property
    def domain(self) -> str:
        return (urlparse(self.url).hostname or "").lower().removeprefix("www.")


@dataclass(frozen=True)
class EvidenceAnchor:
    source_url: str
    excerpt: str
    content_sha256: str | None = None

    def __post_init__(self):
        if not self.source_url or not self.excerpt.strip():
            raise ValueError("evidence anchor requires source_url + non-empty excerpt")

    @property
    def anchor_id(self) -> str:
        raw = f"{self.source_url}\n{self.excerpt}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:20]


@dataclass(frozen=True)
class AtomicClaim:
    claim_id: str
    field: str
    statement: str
    status: EpistemicStatus
    sources: tuple[SourceRef, ...] = ()
    anchors: tuple[EvidenceAnchor, ...] = ()
    supporting_claim_ids: tuple[str, ...] = ()
    confidence: float = 0.5
    contradictory_claim_ids: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.claim_id or not self.field or not self.statement:
            raise ValueError("claim requires id, field, and statement")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0,1]")
        if self.status == EpistemicStatus.FACT:
            if not self.sources:
                raise ValueError("FACT requires at least one source")
            if not self.anchors:
                raise ValueError("FACT requires at least one exact evidence anchor")
            source_urls = {s.url for s in self.sources}
            if any(a.source_url not in source_urls for a in self.anchors):
                raise ValueError("every FACT anchor must point at one of the claim's sources")
        if self.status == EpistemicStatus.INFERENCE and not self.supporting_claim_ids:
            raise ValueError("INFERENCE requires supporting_claim_ids")
        if self.status in {EpistemicStatus.UNKNOWN, EpistemicStatus.PRIMARY_VALIDATION_REQUIRED}:
            if self.sources or self.anchors:
                raise ValueError(f"{self.status.value} must not masquerade as sourced evidence")

    @property
    def strongest_tier(self) -> SourceTier | None:
        return min((s.tier for s in self.sources), default=None)

    @property
    def independent_domains(self) -> set[str]:
        return {s.domain for s in self.sources if s.domain}


@dataclass
class ResearchCoverage:
    searched_fields: set[str] = field(default_factory=set)
    negative_searched_fields: set[str] = field(default_factory=set)
    queries_run: list[str] = field(default_factory=list)
    source_urls: set[str] = field(default_factory=set)
    source_domains_by_field: dict[str, set[str]] = field(default_factory=dict)

    def merge(self, other: "ResearchCoverage") -> "ResearchCoverage":
        self.searched_fields |= set(other.searched_fields)
        self.negative_searched_fields |= set(other.negative_searched_fields)
        self.queries_run.extend(q for q in other.queries_run if q not in self.queries_run)
        self.source_urls |= set(other.source_urls)
        for field_name, domains in other.source_domains_by_field.items():
            self.source_domains_by_field.setdefault(field_name, set()).update(domains)
        return self


@dataclass(frozen=True)
class GateRequirement:
    field: str
    min_claims: int = 1
    max_source_tier: SourceTier = SourceTier.TIER_3_CONTEXT
    allowed_statuses: tuple[EpistemicStatus, ...] = (EpistemicStatus.FACT,)
    min_independent_domains: int = 1
    require_search: bool = True


@dataclass
class GateResult:
    complete: bool
    missing: list[str] = field(default_factory=list)
    weak: list[str] = field(default_factory=list)
    primary_validation: list[str] = field(default_factory=list)
    missing_negative_search: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CompletionGate:
    gate_id: str
    requirements: tuple[GateRequirement, ...]
    negative_search_fields: tuple[str, ...] = ()
    require_no_critical_unknowns: bool = True

    def evaluate(self, claims: Iterable[AtomicClaim], critical_unknown_fields: Sequence[str] = (), coverage: ResearchCoverage | None = None) -> GateResult:
        claims = list(claims)
        coverage = coverage or ResearchCoverage()
        by_field: dict[str, list[AtomicClaim]] = {}
        for claim in claims:
            by_field.setdefault(claim.field, []).append(claim)

        missing, weak, primary, missing_negative = [], [], [], []
        for req in self.requirements:
            field_claims = by_field.get(req.field, [])
            if any(c.status == EpistemicStatus.PRIMARY_VALIDATION_REQUIRED for c in field_claims):
                primary.append(req.field)
                continue
            acceptable = []
            for claim in field_claims:
                if claim.status not in req.allowed_statuses:
                    continue
                if claim.status == EpistemicStatus.FACT and (claim.strongest_tier is None or claim.strongest_tier > req.max_source_tier):
                    continue
                acceptable.append(claim)
            if len(acceptable) < req.min_claims:
                (weak if field_claims else missing).append(req.field)
                continue
            domains = set()
            for claim in acceptable:
                domains |= claim.independent_domains
            if req.min_independent_domains > 1 and len(domains) < req.min_independent_domains:
                weak.append(req.field)
            if req.require_search and req.field not in coverage.searched_fields:
                weak.append(req.field)

        for field_name in self.negative_search_fields:
            if field_name not in coverage.negative_searched_fields:
                missing_negative.append(field_name)

        if self.require_no_critical_unknowns:
            for field_name in critical_unknown_fields:
                if any(c.field == field_name and c.status in {EpistemicStatus.UNKNOWN, EpistemicStatus.PRIMARY_VALIDATION_REQUIRED} for c in claims):
                    primary.append(field_name)

        return GateResult(
            complete=not (missing or weak or primary or missing_negative),
            missing=sorted(set(missing)),
            weak=sorted(set(weak)),
            primary_validation=sorted(set(primary)),
            missing_negative_search=sorted(set(missing_negative)),
        )


FACT_OR_INFERENCE = (EpistemicStatus.FACT, EpistemicStatus.INFERENCE)

COMPANY_COMPLETION_GATE = CompletionGate(
    gate_id="company_v2",
    requirements=(
        GateRequirement("identity", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("current_initiative", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("financial_capacity", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("product_business_model", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("strategic_need", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("internal_capability", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("external_incremental_value", allowed_statuses=(EpistemicStatus.INFERENCE,), require_search=False),
        GateRequirement("event_answerable_question", allowed_statuses=(EpistemicStatus.INFERENCE, EpistemicStatus.HYPOTHESIS), require_search=False),
        GateRequirement("buyer_function", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("substitute", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("event_value_chain", allowed_statuses=(EpistemicStatus.INFERENCE,), require_search=False),
    ),
    negative_search_fields=("strategic_need", "internal_capability", "external_incremental_value", "event_answerable_question", "substitute"),
)

THEME_COMPLETION_GATE = CompletionGate(
    gate_id="theme_v2",
    requirements=(
        GateRequirement("economic_problem", max_source_tier=SourceTier.TIER_2_REPUTABLE),
        GateRequirement("student_value", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("cornell_fit", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("company_ecosystem", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("event_feasibility", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("commercial_surface", allowed_statuses=FACT_OR_INFERENCE),
        GateRequirement("falsification", allowed_statuses=(EpistemicStatus.HYPOTHESIS, EpistemicStatus.INFERENCE), require_search=False),
    ),
    negative_search_fields=("economic_problem", "event_feasibility", "commercial_surface"),
)

GATES: Mapping[str, CompletionGate] = {"company": COMPANY_COMPLETION_GATE, "theme": THEME_COMPLETION_GATE}


def get_gate(name: str) -> CompletionGate:
    try:
        return GATES[name]
    except KeyError as exc:
        raise KeyError(f"unknown completion gate {name!r}") from exc
