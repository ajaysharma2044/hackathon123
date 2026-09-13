"""Honest ingestion bridge between session-assisted web research and product agents.

The standalone Python Agentic OS does NOT browse the web by pretending it can. A browser/session
researcher writes sourced findings through this bridge; product agents consume them deterministically.
That boundary makes SESSION_ASSISTED research explicit and preserves provenance/contradictions.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Iterable
import json


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Finding:
    node_id: str
    resolver: str
    value: Any
    source_url: str
    source_title: str
    source_type: str
    claim: str
    observed_at: str = field(default_factory=_now)
    mode: str = "SESSION_ASSISTED"
    tags: tuple[str, ...] = ()

    def validate(self):
        if not self.node_id or not self.resolver:
            raise ValueError("finding requires node_id + resolver")
        if not self.source_url or not self.claim:
            raise ValueError("sourced finding requires source_url + claim")
        if self.mode not in {"SESSION_ASSISTED", "SELF_CONTAINED"}:
            raise ValueError("unknown research mode")
        return self


class ResearchBridge:
    def __init__(self, findings: Iterable[Finding] = ()):
        self.memory = EvidenceMemory()
        self._by_node: dict[str, list[Finding]] = {}
        self._by_resolver: dict[str, list[Finding]] = {}
        for f in findings:
            self.ingest(f)

    def ingest(self, f: Finding):
        f.validate()
        self._by_node.setdefault(f.node_id, []).append(f)
        self._by_resolver.setdefault(f.resolver, []).append(f)

    def findings_for(self, node_id: str, resolver: str | None = None) -> list[Finding]:
        xs = list(self._by_node.get(node_id, []))
        if resolver is not None:
            xs = [x for x in xs if x.resolver == resolver]
        return xs

    def resolver_findings(self, resolver: str, tag: str | None = None) -> list[Finding]:
        xs = list(self._by_resolver.get(resolver, []))
        if tag:
            xs = [x for x in xs if tag in x.tags]
        return xs

    def packet(self, node_id: str, resolver: str | None = None) -> dict[str, Any] | None:
        xs = self.findings_for(node_id, resolver)
        if not xs:
            return None
        serial = [json.dumps(x.value, sort_keys=True, default=str) for x in xs]
        if len(set(serial)) == 1:
            return {
                "status": "CACHED_UNVALIDATED",
                "value": xs[0].value,
                "provenance": [self._prov(x) for x in xs],
                "research_mode": self._mode(xs),
            }
        return {
            "status": "CONTRADICTED",
            "value": None,
            "claims": [{"value": x.value, "claim": x.claim, **self._prov(x)} for x in xs],
            "provenance": [self._prov(x) for x in xs],
            "research_mode": self._mode(xs),
        }

    @staticmethod
    def _mode(xs: list[Finding]) -> str:
        modes = {x.mode for x in xs}
        return modes.pop() if len(modes) == 1 else "MIXED"

    @staticmethod
    def _prov(f: Finding) -> dict[str, Any]:
        return {
            "source_url": f.source_url,
            "source_title": f.source_title,
            "source_type": f.source_type,
            "claim": f.claim,
            "observed_at": f.observed_at,
            "mode": f.mode,
        }

    def to_json(self, path: str):
        data = [asdict(f) for xs in self._by_node.values() for f in xs]
        for d in data:
            d["tags"] = list(d.get("tags", []))
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)

    @classmethod
    def from_json(cls, path: str) -> "ResearchBridge":
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
        return cls(Finding(**{**d, "tags": tuple(d.get("tags", []))}) for d in raw)

# The v2 memory stores opened documents and atomic proposals. Legacy Finding/packet is an import
# format only and is never completion evidence in the v2 runtime.
class EvidenceMemory:
    def __init__(self):
        self.documents = {}
        self.claims = {}
        self.findings = {}  # existing evidence_graph.Claim, not a second finding ontology
        self.searches = []
        self.rejections = []

    def remember_source(self, document):
        from urllib.parse import urlparse
        if urlparse(document.source.url).scheme not in ('https', 'http'):
            raise ValueError('source URL must be http(s); private buyer records need an authorized adapter URL')
        if document.source.content_sha256:
            import hashlib
            if hashlib.sha256(document.text.encode()).hexdigest() != document.source.content_sha256:
                raise ValueError('source content digest mismatch')
        old = self.documents.get(document.source_id)
        if old is not None and old != document:
            raise ValueError('source ID reused with different content; version the source')
        self.documents[document.source_id] = document

    def accept(self, claim, document=None):
        from research_contracts import AtomicClaim, EpistemicStatus
        from evidence_graph import Claim, EvidenceRef, SUPPORTS, CONTRADICTS
        from commercial_logic import PRIMARY_WTP_EVIDENCE, WTPStatus
        import copy
        if not isinstance(claim, AtomicClaim):
            raise ValueError('extractor must return AtomicClaim objects')
        if not claim.subject_id:
            raise ValueError('claim requires subject_id')
        if claim.claim_id in self.claims:
            if self.claims[claim.claim_id] != claim:
                raise ValueError('claim ID collision; evidence is append-only')
            return False
        if claim.status in (EpistemicStatus.FACT, EpistemicStatus.EVIDENCE):
            doc = self.documents.get(claim.source_id)
            if doc is None or (document is not None and doc.source_id != document.source_id):
                raise ValueError('FACT must reference the opened document')
            if not claim.quote_or_excerpt.strip() or claim.quote_or_excerpt not in doc.text:
                raise ValueError('FACT excerpt must occur verbatim in opened content')
            if any(a.source_url != doc.source.url or a.excerpt not in doc.text or
                   (a.content_sha256 and a.content_sha256 != doc.source.content_sha256) for a in claim.anchors):
                raise ValueError('anchor does not match retrieved content')
            if claim.sources != (doc.source,):
                raise ValueError('source quality must come from retrieval, not extraction')
            if claim.observed_at != doc.observed_at or claim.published_at != doc.source.published_at:
                raise ValueError('claim clocks must match source clocks')
        if any(i not in self.claims for i in claim.supporting_claim_ids):
            raise ValueError('support references must already be accepted (cycles forbidden)')
        if claim.status == EpistemicStatus.INFERENCE:
            if not claim.supporting_claim_ids or any(i not in self.claims for i in claim.supporting_claim_ids):
                raise ValueError('INFERENCE requires accepted supporting claims (cycles forbidden)')
            if any(self.claims[i].status not in (EpistemicStatus.FACT, EpistemicStatus.INFERENCE)
                   for i in claim.supporting_claim_ids):
                raise ValueError('hypotheses and unknowns cannot ground an inference')
        if claim.field == 'wtp_status' and claim.status in (EpistemicStatus.UNKNOWN, EpistemicStatus.PRIMARY_VALIDATION_REQUIRED):
            if claim.value is not None and claim.value not in ('UNKNOWN','PRIMARY_VALIDATION_REQUIRED'):
                raise ValueError('unknown WTP cannot carry a numeric or observed payload')
        if claim.field == 'wtp_status' and claim.status == EpistemicStatus.FACT:
            if not isinstance(claim.value, dict) or claim.value.get('status') != WTPStatus.OBSERVED.value:
                raise ValueError('desk-research WTP must remain UNKNOWN or PRIMARY_VALIDATION_REQUIRED')
            if not any(s.tier == 1 and s.source_type in PRIMARY_WTP_EVIDENCE for s in claim.sources):
                raise ValueError('funding/comparables cannot establish observed WTP')
            if not claim.value.get('buyer') or not claim.value.get('scope') or claim.value.get('amount') is None:
                raise ValueError('observed WTP needs buyer, scope, and amount')
            from math import isfinite
            amount = claim.value['amount']
            if type(amount) not in (int,float) or not isfinite(amount) or amount < 0:
                raise ValueError('observed WTP amount must be finite and nonnegative')
        self.claims[claim.claim_id] = copy.deepcopy(claim)
        f = Claim(claim.claim_id, claim.statement)
        if claim.status in (EpistemicStatus.FACT, EpistemicStatus.EVIDENCE):
            f.add_evidence(EvidenceRef(SUPPORTS, 'source_document', claim.source_id, claim.quote_or_excerpt))
        for i in claim.supporting_claim_ids:
            f.add_evidence(EvidenceRef(SUPPORTS, 'atomic_claim', i))
        self.findings[claim.claim_id] = f
        # Link in both directions, even if the opposing claim arrives in a later batch.
        for other in self.claims.values():
            if (other.claim_id in claim.contradictory_claim_ids or
                    claim.claim_id in other.contradictory_claim_ids):
                f.add_evidence(EvidenceRef(CONTRADICTS, 'atomic_claim', other.claim_id))
                self.findings[other.claim_id].add_evidence(EvidenceRef(CONTRADICTS, 'atomic_claim', claim.claim_id))
        return True

    def for_subject(self, subject_id):
        return [c for c in self.claims.values() if c.subject_id == subject_id]

    def record_search(self, record):
        from evidence_graph import NegativeCase
        self.searches.append(dict(record))
        if record.get('negative_query') and record.get('status') == 'SEARCHED':
            for c in self.for_subject(record['node']):
                self.findings[c.claim_id].negative_cases.append(NegativeCase(
                    record['question'], record['query'],
                    bool(self.findings[c.claim_id].contradicting())))

    def trace_claim(self, claim_id):
        c = self.claims[claim_id]
        return {'atomic_claim': asdict(c), 'finding': self.findings[claim_id].trace(),
                'sources': [asdict(self.documents[c.source_id])] if c.source_id in self.documents else [],
                'supports': [self.trace_claim(i) for i in c.supporting_claim_ids]}
