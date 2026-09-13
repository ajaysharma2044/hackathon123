"""Core state machine for evidence-first agentic research."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import itertools


def _now(): return datetime.now().isoformat(timespec="seconds")


class NodeStatus(str, Enum):
    UNRESEARCHED = "UNRESEARCHED"
    RESEARCHING = "RESEARCHING"
    PARTIAL = "PARTIAL"
    CONTRADICTED = "CONTRADICTED"
    EVIDENCE_COMPLETE = "EVIDENCE_COMPLETE"
    SYNTHESIS_READY = "SYNTHESIS_READY"
    RESOLVED = "RESOLVED"
    PRIMARY_VALIDATION_REQUIRED = "PRIMARY_VALIDATION_REQUIRED"
    RESEARCH_BACKEND_REQUIRED = "RESEARCH_BACKEND_REQUIRED"
    CONTRACT_REQUIRED = "CONTRACT_REQUIRED"
    RESEARCH_EXHAUSTED = "RESEARCH_EXHAUSTED"
    KILLED = "KILLED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNRESEARCHED"
    RESOLVING = "RESEARCHING"
    NEEDS_RESEARCH = "PARTIAL"
    PRIMARY = "PRIMARY_VALIDATION_REQUIRED"
    QUOTE = "PRIMARY_VALIDATION_REQUIRED"
    DECOMPOSED = "PARTIAL"


class Permission(str, Enum):
    AUTONOMOUS_READ = "AUTONOMOUS_READ"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"


SUCCESS_TERMINAL = {NodeStatus.RESOLVED, NodeStatus.KILLED}
RETRYABLE = {NodeStatus.UNRESEARCHED, NodeStatus.PARTIAL, NodeStatus.CONTRADICTED}
OPEN_NONRETRYABLE = {NodeStatus.PRIMARY_VALIDATION_REQUIRED, NodeStatus.RESEARCH_BACKEND_REQUIRED, NodeStatus.CONTRACT_REQUIRED, NodeStatus.RESEARCH_EXHAUSTED, NodeStatus.BLOCKED}


@dataclass
class Node:
    id: str
    question: str
    resolver: str | None = None
    status: NodeStatus = NodeStatus.UNRESEARCHED
    value: object = None
    provenance: str | None = None
    deps: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    voi: float = 0.0
    evidence: list[dict] = field(default_factory=list)
    node_type: str | None = None
    completion_gate: str | None = None
    critical_unknown_fields: list[str] = field(default_factory=list)
    attempt_count: int = 0
    max_attempts: int = 8
    retryable: bool = True

    def resolve(self, value, provenance, status=NodeStatus.RESOLVED):
        if status not in SUCCESS_TERMINAL:
            raise ValueError(f"resolve() requires a true terminal state, got {status}")
        self.value, self.provenance, self.status, self.retryable = value, provenance, status, False
        self.evidence.append({"value": value, "provenance": provenance, "at": _now()})

    def can_retry(self) -> bool:
        return self.retryable and self.status in RETRYABLE and self.attempt_count < self.max_attempts


class NodeGraph:
    def __init__(self): self.nodes: dict[str, Node] = {}
    def add(self, node: Node) -> Node:
        if node.id in self.nodes: return self.nodes[node.id]
        self.nodes[node.id] = node
        return node
    def get(self, node_id: str) -> Node: return self.nodes[node_id]
    def all(self): return list(self.nodes.values())
    def by_status(self, *statuses): return [n for n in self.nodes.values() if n.status in statuses]
    def unknown(self): return self.by_status(NodeStatus.UNRESEARCHED)
    def open_for_humans(self): return [n for n in self.nodes.values() if n.status in OPEN_NONRETRYABLE or n.status in {NodeStatus.PARTIAL, NodeStatus.CONTRADICTED}]
    def dependency_complete(self, node_id: str) -> bool: return self.nodes[node_id].status in SUCCESS_TERMINAL
    def ready(self): return [n for n in self.nodes.values() if n.can_retry() and all(self.dependency_complete(d) for d in n.deps)]
    def children_all_done(self, node: Node): return bool(node.children) and all(self.nodes[c].status in SUCCESS_TERMINAL for c in node.children)


@dataclass
class AgentTask:
    id: str
    node_id: str
    agent_type: str
    permission: Permission
    status: str = "QUEUED"
    created_at: str = field(default_factory=_now)


class TaskQueue:
    def __init__(self): self._q, self._c = [], itertools.count(1)
    def push(self, node_id, agent_type, permission):
        t = AgentTask(f"task_{next(self._c)}", node_id, agent_type, permission); self._q.append(t); return t
    def pending(self): return [t for t in self._q if t.status == "QUEUED"]
    def all(self): return list(self._q)


@dataclass
class Evidence: value: object; provenance: str; status: NodeStatus = NodeStatus.RESOLVED
@dataclass
class Decompose: children: list[Node]
@dataclass
class Defer: status: NodeStatus; reason: str
@dataclass
class RequestAction: description: str; payload: dict = field(default_factory=dict)


class Log:
    def __init__(self): self.runs, self.decisions, self.approvals = [], [], []
    def run(self, **kw): self.runs.append({"at": _now(), **kw})
    def decision(self, **kw): self.decisions.append({"at": _now(), **kw})
    def approval(self, **kw): self.approvals.append({"at": _now(), **kw})
