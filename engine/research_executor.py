"""Tool-agnostic research execution interfaces.

The orchestration layer must not know *which* browser/search runtime exists.  It asks a research
executor for evidence.  Production adapters can wrap ChatGPT web search, Codex/browser sessions,
MCP tools, or another retrieval system.  Tests can use deterministic fakes.

The important boundary: an executor returns source-backed atomic claims and discovered entities;
it never returns an already-resolved business conclusion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence

from research_contracts import AtomicClaim


@dataclass(frozen=True)
class ResearchQuestion:
    question_id: str
    query: str
    target_fields: tuple[str, ...]
    negative_query: bool = False
    preferred_source_tiers: tuple[int, ...] = (1, 2, 3)


@dataclass(frozen=True)
class DiscoveredEntity:
    entity_type: str
    canonical_name: str
    canonical_url: str | None = None
    relationship: str | None = None
    evidence_claim_ids: tuple[str, ...] = ()


@dataclass
class ResearchBatch:
    claims: list[AtomicClaim] = field(default_factory=list)
    discovered_entities: list[DiscoveredEntity] = field(default_factory=list)
    queries_run: list[str] = field(default_factory=list)
    sources_opened: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class ResearchExecutor(Protocol):
    def research(self, questions: Sequence[ResearchQuestion], context: dict) -> ResearchBatch:
        """Execute research and return source-backed evidence.  Must not fabricate missing facts."""
        ...


class MissingResearchExecutor:
    """Explicit null adapter.  It keeps an offline run honest instead of hallucinating."""
    def research(self, questions: Sequence[ResearchQuestion], context: dict) -> ResearchBatch:
        return ResearchBatch(
            queries_run=[],
            notes=["No live research executor configured; leave node OPEN/NEEDS_RESEARCH."],
        )
