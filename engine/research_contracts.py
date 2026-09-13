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
from typing import Iterable, Mapping, Sequence


class EpistemicStatus(str, Enum):
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

    def __post_init__(self):
        if not self.url or not self.title:
            raise ValueError("source requires url + title")


@dataclass(frozen=True)
class AtomicClaim:
    claim_id: str
    field: str
    statement: str
    status: EpistemicStatus
    sources: tuple[SourceRef, ...] = ()
    confidence: float = 0.5
    contradictory_claim_ids: tuple[str, ...] = ()

    def __post_init__(self):
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

    def evaluate(self, claims: Iterable[AtomicClaim], critical_unknown_fields: Sequence[str] = ()) -> GateResult:
        claims = list(claims)
        by_field: dict[str, list[AtomicClaim]] = {}
        for c in claims:
            by_field.setdefault(c.field, []).append(c)

        missing: list[str] = []
        weak: list[str] = []
        primary: list[str] = []

        for req in self.requirements:
            field_claims = by_field.get(req.field, [])
            factual = [c for c in field_claims if c.status == EpistemicStatus.FACT]
            acceptable = [
                c for c in factual
                if c.strongest_tier is not None and c.strongest_tier <= req.max_source_tier
            ]
            if req.require_fact and len(acceptable) < req.min_claims:
                if any(c.status == EpistemicStatus.PRIMARY_VALIDATION_REQUIRED for c in field_claims):
                    primary.append(req.field)
                elif field_claims:
                    weak.append(req.field)
                else:
                    missing.append(req.field)

        if self.require_counterevidence:
            has_counter = any(c.contradictory_claim_ids for c in claims) or any(
                c.field == "counterevidence" and c.status == EpistemicStatus.FACT for c in claims
            )
            if not has_counter:
                missing.append("counterevidence")

        if self.require_no_critical_unknowns:
            for f in critical_unknown_fields:
                if any(c.field == f and c.status in {
                    EpistemicStatus.UNKNOWN,
                    EpistemicStatus.PRIMARY_VALIDATION_REQUIRED,
                } for c in claims):
                    primary.append(f)

        return GateResult(
            complete=not (missing or weak or primary),
            missing=sorted(set(missing)),
            weak=sorted(set(weak)),
            primary_validation=sorted(set(primary)),
        )


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
        GateRequirement("external_incremental_value", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("event_answerable_question", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("buyer_function", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("substitute", max_source_tier=SourceTier.TIER_3_CONTEXT),
        GateRequirement("event_value_chain", max_source_tier=SourceTier.TIER_3_CONTEXT),
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


GATES: Mapping[str, CompletionGate] = {
    "company": COMPANY_COMPLETION_GATE,
    "theme": THEME_COMPLETION_GATE,
}


def get_gate(name: str) -> CompletionGate:
    try:
        return GATES[name]
    except KeyError as exc:
        raise KeyError(f"unknown completion gate {name!r}") from exc
