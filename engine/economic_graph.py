"""Typed recursive economic graph for hackathon discovery.

This module is deliberately independent of any browser/LLM runtime. It stores sourced
entities/edges, preserves contradictions, merges duplicate organizations/products, and
terminates recursive product expansion using explicit stop rules and cycle detection.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Callable, Iterable
import re

REQUIRED_EDGE_TYPES = {
    "OWNS_PROBLEM", "EXPERIENCES_FAILURE", "MAKES_DECISION", "USES", "BUYS", "SELLS",
    "DEPENDS_ON", "BUILDS_ON", "INTEGRATES_WITH", "COMPETES_WITH", "SUBSTITUTES_FOR",
    "COMPLEMENTS", "HOSTS", "MONITORS", "SECURES", "AUTHENTICATES", "SUPPLIES_DATA_TO",
    "IMPLEMENTS", "CONSULTS_FOR", "DISTRIBUTES", "FINANCES", "INSURES", "RECRUITS_FROM",
    "INVESTS_IN", "SPONSORS", "SUPPLIES_RESOURCE", "REDUCES_COST_OF", "ENABLES",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


@dataclass(frozen=True)
class EvidenceRef:
    source_url: str
    source_title: str
    source_type: str
    claim: str
    observed_at: str = field(default_factory=_now)

    def __post_init__(self):
        if not self.source_url or not self.claim:
            raise ValueError("evidence requires source_url and claim")


@dataclass
class EconomicNode:
    id: str
    kind: str
    name: str
    attrs: dict[str, Any] = field(default_factory=dict)
    evidence: list[EvidenceRef] = field(default_factory=list)
    stop_reason: str | None = None


@dataclass
class EconomicEdge:
    src: str
    dst: str
    kind: str
    attrs: dict[str, Any] = field(default_factory=dict)
    evidence: list[EvidenceRef] = field(default_factory=list)


@dataclass
class Contradiction:
    node_id: str
    field: str
    value_a: Any
    value_b: Any
    evidence_a: list[EvidenceRef]
    evidence_b: list[EvidenceRef]
    created_at: str = field(default_factory=_now)


class EconomicGraph:
    """Graph with canonical entity merge, provenance and recursion guards."""

    def __init__(self):
        self.nodes: dict[str, EconomicNode] = {}
        self.edges: dict[tuple[str, str, str], EconomicEdge] = {}
        self._canonical: dict[tuple[str, str], str] = {}
        self.contradictions: list[Contradiction] = []

    def add_node(
        self,
        kind: str,
        name: str,
        *,
        node_id: str | None = None,
        attrs: dict[str, Any] | None = None,
        evidence: Iterable[EvidenceRef] = (),
    ) -> EconomicNode:
        key = (kind.lower(), _norm(name))
        if key in self._canonical:
            n = self.nodes[self._canonical[key]]
            self._merge_attrs(n, attrs or {}, list(evidence))
            self._merge_evidence(n.evidence, evidence)
            return n
        if node_id is None:
            slug = _norm(name).replace(" ", "_")[:64] or "node"
            node_id = f"{kind.lower()}:{slug}"
            base = node_id
            i = 2
            while node_id in self.nodes:
                node_id = f"{base}:{i}"
                i += 1
        n = EconomicNode(node_id, kind, name, dict(attrs or {}), list(evidence))
        self.nodes[node_id] = n
        self._canonical[key] = node_id
        return n

    @staticmethod
    def _merge_evidence(target: list[EvidenceRef], new: Iterable[EvidenceRef]):
        seen = {(e.source_url, e.claim) for e in target}
        for e in new:
            if (e.source_url, e.claim) not in seen:
                target.append(e)
                seen.add((e.source_url, e.claim))

    def _merge_attrs(self, node: EconomicNode, attrs: dict[str, Any], incoming_evidence: list[EvidenceRef]):
        for k, v in attrs.items():
            if k not in node.attrs or node.attrs[k] is None:
                node.attrs[k] = v
            elif v is not None and node.attrs[k] != v:
                self.contradictions.append(
                    Contradiction(node.id, k, node.attrs[k], v, list(node.evidence), incoming_evidence)
                )
                # Preserve the first value; contradiction is explicit rather than silently overwritten.

    def add_edge(
        self,
        src: str,
        dst: str,
        kind: str,
        *,
        attrs: dict[str, Any] | None = None,
        evidence: Iterable[EvidenceRef] = (),
    ) -> EconomicEdge:
        if src not in self.nodes or dst not in self.nodes:
            raise KeyError("both edge endpoints must exist")
        if kind not in REQUIRED_EDGE_TYPES:
            raise ValueError(f"unsupported edge type: {kind}")
        key = (src, dst, kind)
        if key in self.edges:
            e = self.edges[key]
            e.attrs.update(attrs or {})
            self._merge_evidence(e.evidence, evidence)
            return e
        e = EconomicEdge(src, dst, kind, dict(attrs or {}), list(evidence))
        self.edges[key] = e
        return e

    @staticmethod
    def stop_reason(node: EconomicNode) -> str | None:
        a = node.attrs
        checks = [
            (str(a.get("hackathon_relevance", "")).upper() == "LOW", "LOW_HACKATHON_RELEVANCE"),
            (str(a.get("economic_importance", "")).upper() == "LOW", "LOW_ECONOMIC_IMPORTANCE"),
            (a.get("event_influence") is False, "EVENT_CANNOT_INFLUENCE_DECISION"),
            (a.get("artificial_participant_behavior") is True, "ARTIFICIAL_PARTICIPANT_BEHAVIOR"),
            (a.get("commercial_relevance_too_indirect") is True, "COMMERCIAL_RELEVANCE_TOO_INDIRECT"),
            (a.get("dominated") is True, "DOMINATED_BRANCH"),
            (str(a.get("source_quality", "")).upper() == "LOW", "SOURCE_QUALITY_COLLAPSED"),
            (str(a.get("marginal_voi", "")).upper() == "LOW", "LOW_MARGINAL_VOI"),
        ]
        for cond, reason in checks:
            if cond:
                return reason
        return None

    def expand_products(
        self,
        starts: Iterable[str],
        expand_fn: Callable[[EconomicNode], Iterable[dict[str, Any]]],
        *,
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """Breadth-first recursive product expansion with stop/cycle guards.

        expand_fn returns dicts with at minimum: kind, name, edge_kind. Optional attrs/evidence.
        The source node's evidence is propagated to the edge if child evidence is absent.
        """
        q = [(s, 0) for s in starts]
        seen_at_depth: set[tuple[str, int]] = set()
        expanded: set[str] = set()
        cycle_skips = 0
        stops: dict[str, str] = {}
        while q:
            node_id, depth = q.pop(0)
            if (node_id, depth) in seen_at_depth:
                continue
            seen_at_depth.add((node_id, depth))
            node = self.nodes[node_id]
            reason = self.stop_reason(node)
            if reason:
                node.stop_reason = reason
                stops[node_id] = reason
                continue
            if depth >= max_depth:
                node.stop_reason = "MAX_DEPTH"
                stops[node_id] = "MAX_DEPTH"
                continue
            if node_id in expanded:
                cycle_skips += 1
                continue
            expanded.add(node_id)
            for spec in expand_fn(node) or []:
                child = self.add_node(
                    spec["kind"], spec["name"], attrs=spec.get("attrs", {}), evidence=spec.get("evidence", [])
                )
                edge_evidence = spec.get("evidence") or node.evidence
                self.add_edge(
                    node.id,
                    child.id,
                    spec["edge_kind"],
                    attrs=spec.get("edge_attrs", {}),
                    evidence=edge_evidence,
                )
                if child.id == node.id or child.id in expanded:
                    cycle_skips += 1
                    continue
                q.append((child.id, depth + 1))
        return {"expanded": len(expanded), "cycle_skips": cycle_skips, "stops": stops}

    def snapshot(self) -> dict[str, Any]:
        return {
            "nodes": [self._node_dict(n) for n in self.nodes.values()],
            "edges": [self._edge_dict(e) for e in self.edges.values()],
            "contradictions": [self._contradiction_dict(c) for c in self.contradictions],
        }

    @staticmethod
    def _eref(e: EvidenceRef) -> dict[str, Any]:
        return asdict(e)

    def _node_dict(self, n: EconomicNode) -> dict[str, Any]:
        d = asdict(n)
        d["evidence"] = [self._eref(e) for e in n.evidence]
        return d

    def _edge_dict(self, e: EconomicEdge) -> dict[str, Any]:
        d = asdict(e)
        d["evidence"] = [self._eref(x) for x in e.evidence]
        return d

    def _contradiction_dict(self, c: Contradiction) -> dict[str, Any]:
        return {
            "node_id": c.node_id,
            "field": c.field,
            "value_a": c.value_a,
            "value_b": c.value_b,
            "evidence_a": [self._eref(e) for e in c.evidence_a],
            "evidence_b": [self._eref(e) for e in c.evidence_b],
            "created_at": c.created_at,
        }
