"""Tool-agnostic research execution interfaces.

The orchestrator asks an executor for retrieved evidence, not a finished business conclusion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence

from research_contracts import AtomicClaim, ResearchCoverage, SourceRef


@dataclass(frozen=True)
class ResearchQuestion:
    question_id: str
    query: str
    target_fields: tuple[str, ...]
    negative_query: bool = False
    preferred_source_tiers: tuple[int, ...] = (1, 2, 3)
    preferred_domains: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvidenceCandidate:
    candidate_id: str
    question_id: str
    target_fields: tuple[str, ...]
    source: SourceRef
    excerpt: str
    relevance: float
    negative_query: bool = False


@dataclass(frozen=True)
class DiscoveredEntity:
    entity_type: str
    canonical_name: str
    canonical_url: str | None = None
    relationship: str | None = None
    evidence_claim_ids: tuple[str, ...] = ()
    confidence: float = 0.5


@dataclass
class ExtractionResult:
    claims: list[AtomicClaim] = field(default_factory=list)
    discovered_entities: list[DiscoveredEntity] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class GroundedExtractor(Protocol):
    def extract(self, question: ResearchQuestion, candidates: Sequence[EvidenceCandidate], context: dict) -> ExtractionResult:
        ...


@dataclass
class ResearchBatch:
    claims: list[AtomicClaim] = field(default_factory=list)
    evidence_candidates: list[EvidenceCandidate] = field(default_factory=list)
    discovered_entities: list[DiscoveredEntity] = field(default_factory=list)
    queries_run: list[str] = field(default_factory=list)
    sources_opened: list[str] = field(default_factory=list)
    rejected_claims: list[str] = field(default_factory=list)
    coverage: ResearchCoverage = field(default_factory=ResearchCoverage)
    notes: list[str] = field(default_factory=list)
    backend_available: bool = True


class ResearchExecutor(Protocol):
    def research(self, questions: Sequence[ResearchQuestion], context: dict) -> ResearchBatch:
        ...


class MissingResearchExecutor:
    def research(self, questions: Sequence[ResearchQuestion], context: dict) -> ResearchBatch:
        return ResearchBatch(notes=["No live research executor configured; do not synthesize from memory."], backend_available=False)
