"""Provider-neutral retrieval boundary. No canned-answer or implicit model-memory fallback."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Sequence
from research_contracts import AtomicClaim, SourceRef

@dataclass(frozen=True)
class ResearchQuestion:
    question_id: str
    query: str
    target_fields: tuple[str, ...]
    negative_query: bool = False
    preferred_source_tiers: tuple[int, ...] = (1, 2, 3)
    agent: str = 'researcher'
    subject_id: str = ''
    context_claims: tuple[AtomicClaim, ...] = ()
    preferred_domains: tuple[str, ...] = ()

ResearchQuery = ResearchQuestion

@dataclass(frozen=True)
class SearchResult:
    url: str
    title: str
    snippet: str = ''

@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    source: SourceRef
    text: str
    observed_at: str

    def __post_init__(self):
        if not self.source_id or not self.text.strip() or not self.observed_at:
            raise ValueError('opened source requires id, content, and retrieval timestamp')

@dataclass(frozen=True)
class DiscoveredEntity:
    entity_type: str
    canonical_name: str
    canonical_url: str | None = None
    relationship: str | None = None
    evidence_claim_ids: tuple[str, ...] = ()
    relevance: str = ''  # Event #1 connection, required to enter the frontier
    voi: float = 1.0
    profile: str | None = None

@dataclass
class ResearchBatch:
    """Legacy transport only: production does not accept an answer packet as retrieval."""
    claims: list[AtomicClaim] = field(default_factory=list)
    discovered_entities: list[DiscoveredEntity] = field(default_factory=list)
    queries_run: list[str] = field(default_factory=list)
    sources_opened: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

class ResearchExecutor(Protocol):
    def search(self, query: ResearchQuery) -> list[SearchResult]: ...
    def open_source(self, result: SearchResult) -> SourceDocument: ...
    def extract_claims(self, document: SourceDocument,
                       questions: Sequence[ResearchQuestion]) -> list[AtomicClaim]: ...

class EntityExtractor(Protocol):
    def discover_entities(self, document: SourceDocument,
                          claims: Sequence[AtomicClaim], context: dict) -> list[DiscoveredEntity]: ...

class ResearchBackendUnavailable(RuntimeError):
    pass

class MissingResearchExecutor:
    def search(self, query):
        raise ResearchBackendUnavailable('RESEARCH_BACKEND_REQUIRED')
    def open_source(self, result):
        raise ResearchBackendUnavailable('RESEARCH_BACKEND_REQUIRED')
    def extract_claims(self, document, questions):
        raise ResearchBackendUnavailable('RESEARCH_BACKEND_REQUIRED')

@dataclass(frozen=True)
class EvidenceCandidate:
    candidate_id: str
    question_id: str
    target_fields: tuple[str, ...]
    source: SourceRef
    excerpt: str
    relevance: float
    negative_query: bool = False

@dataclass
class ExtractionResult:
    claims: list[AtomicClaim] = field(default_factory=list)
    discovered_entities: list[DiscoveredEntity] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

class GroundedExtractor(Protocol):
    def extract(self, question: ResearchQuestion, candidates: Sequence[EvidenceCandidate], context: dict) -> ExtractionResult: ...
