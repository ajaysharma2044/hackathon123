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
                "status": "RESOLVED",
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
