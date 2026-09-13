"""
Agentic OS core (docs/agentic/architecture.md).

The node lifecycle deliberately distinguishes "we cannot answer this from current research" from
"this question is resolved".  NEEDS_RESEARCH / PRIMARY_VALIDATION_REQUIRED / QUOTE are OPEN states,
not terminal research success.  A parent never rolls up to RESOLVED merely because its children are
waiting on more evidence.

Core loop:

    UNRESEARCHED -> RESEARCHING -> PARTIAL / CONTRADICTED / EVIDENCE_COMPLETE
                 -> SYNTHESIS_READY -> RESOLVED

External actions (email/spend/publish) remain permission-gated.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import itertools


def _now():
    return datetime.now().isoformat(timespec="seconds")


class NodeStatus(str, Enum):
    # New explicit lifecycle.
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

    # Backward-compatible aliases used by older modules.  These are intentionally OPEN except
    # RESOLVED.  Keeping aliases lets the refactor proceed without breaking every old import at once.
    UNKNOWN = "UNRESEARCHED"
    RESOLVING = "RESEARCHING"
    NEEDS_RESEARCH = "PARTIAL"
    PRIMARY = "PRIMARY_VALIDATION_REQUIRED"
    QUOTE = "PRIMARY_VALIDATION_REQUIRED"
    DECOMPOSED = "PARTIAL"


class Permission(str, Enum):
    AUTONOMOUS_READ = "AUTONOMOUS_READ"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"


# A status is terminal only when the research/decision itself is finished.  Waiting for a human,
# another research round, or primary validation is NOT research completion.
SUCCESS_TERMINAL = {NodeStatus.RESOLVED}
CLOSED_UNRESOLVED = {NodeStatus.KILLED, NodeStatus.BLOCKED}
OPEN_STATES = {
    NodeStatus.UNRESEARCHED,
    NodeStatus.RESEARCHING,
    NodeStatus.PARTIAL,
    NodeStatus.CONTRADICTED,
    NodeStatus.EVIDENCE_COMPLETE,
    NodeStatus.SYNTHESIS_READY,
    NodeStatus.PRIMARY_VALIDATION_REQUIRED,
    NodeStatus.RESEARCH_BACKEND_REQUIRED, NodeStatus.CONTRACT_REQUIRED, NodeStatus.RESEARCH_EXHAUSTED,
}


@dataclass
class Node:
    id: str
    question: str
    resolver: str = None
    status: NodeStatus = NodeStatus.UNRESEARCHED
    value: object = None
    provenance: str = None
    deps: list = field(default_factory=list)
    children: list = field(default_factory=list)
    voi: float = 0.0
    evidence: list = field(default_factory=list)
    node_type: str | None = None
    completion_gate: str | None = None
    critical_unknown_fields: list[str] = field(default_factory=list)
    depth: int = 0
    auto_rollup: bool = True
    attempt_count: int = 0
    max_attempts: int = 8
    retryable: bool = True

    def __post_init__(self):
        if self.node_type in ('company','theme','event_concept','industry','problem','product','investor',
                              'technology','business_unit','buyer_function','rd_opportunity','data_opportunity'):
            self.completion_gate = self.completion_gate or self.node_type

    def can_retry(self):
        return self.retryable and self.status in (NodeStatus.UNRESEARCHED,NodeStatus.PARTIAL,NodeStatus.CONTRADICTED) and self.attempt_count < self.max_attempts

    def resolve(self, value, provenance, status=NodeStatus.RESOLVED):
        if status not in SUCCESS_TERMINAL and status != NodeStatus.RESOLVED:
            raise ValueError(f"resolve() requires a terminal success status, got {status}")
        if self.completion_gate:
            from research_contracts import get_gate
            from research_config import ResearchConfig
            v = value if isinstance(value, dict) else {}
            gate = get_gate(self.completion_gate).evaluate(v.get('claims',()), self.critical_unknown_fields,
                searches=v.get('searches',()), profile=v.get('profile'),
                config=ResearchConfig(**v.get('research_config',{})), supporting_claims=v.get('supporting_claims',()))
            if not gate.complete:
                raise ValueError('Node.resolve requires its completion contract to pass')
        self.value, self.provenance, self.status = value, provenance, status
        self.evidence.append({"value": value, "provenance": provenance, "at": _now()})


class NodeGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}

    def add(self, node: Node) -> Node:
        if node.id in self.nodes:
            return self.nodes[node.id]
        self.nodes[node.id] = node
        return node

    def get(self, i) -> Node:
        return self.nodes[i]

    def all(self):
        return list(self.nodes.values())

    def by_status(self, *st):
        return [n for n in self.nodes.values() if n.status in st]

    def unknown(self):
        return self.by_status(NodeStatus.UNRESEARCHED)

    def open_for_humans(self):
        return [n for n in self.nodes.values() if n.status in {
            NodeStatus.PARTIAL,
            NodeStatus.CONTRADICTED,
            NodeStatus.PRIMARY_VALIDATION_REQUIRED,
            NodeStatus.BLOCKED,
            NodeStatus.RESEARCH_BACKEND_REQUIRED, NodeStatus.CONTRACT_REQUIRED, NodeStatus.RESEARCH_EXHAUSTED,
        }]

    def dependency_complete(self, node_id: str) -> bool:
        n = self.nodes.get(node_id)
        if n is None or n.status not in SUCCESS_TERMINAL:
            return False
        if n.completion_gate:
            from research_contracts import get_gate
            v = n.value if isinstance(n.value, dict) else {}
            from research_config import ResearchConfig
            return get_gate(n.completion_gate).evaluate(v.get("claims", []), n.critical_unknown_fields,
                searches=v.get("searches", []), profile=v.get("profile"),
                config=ResearchConfig(**v.get('research_config',{})), supporting_claims=v.get('supporting_claims',())).complete
        return True

    def ready(self):
        """Only dispatch nodes whose dependencies are genuinely finished."""
        return [
            n for n in self.all()
            if n.can_retry() and not n.children and all(self.dependency_complete(d) for d in n.deps)
        ]

    def children_all_done(self, node):
        return bool(node.children) and all(
            self.dependency_complete(c) for c in node.children
        )


@dataclass
class AgentTask:
    id: str
    node_id: str
    agent_type: str
    permission: Permission
    status: str = "QUEUED"
    created_at: str = field(default_factory=_now)


class TaskQueue:
    def __init__(self):
        self._q: list[AgentTask] = []
        self._c = itertools.count(1)

    def push(self, node_id, agent_type, permission) -> AgentTask:
        t = AgentTask(f"task_{next(self._c)}", node_id, agent_type, permission)
        self._q.append(t)
        return t

    def pending(self):
        return [t for t in self._q if t.status == "QUEUED"]

    def all(self):
        return list(self._q)


@dataclass
class Evidence:
    value: object
    provenance: str
    status: NodeStatus = NodeStatus.RESOLVED


@dataclass
class Decompose:
    children: list


@dataclass
class Defer:
    status: NodeStatus
    reason: str


@dataclass
class RequestAction:
    description: str
    payload: dict = field(default_factory=dict)


class Log:
    """Append-only run / decision / approval logs."""
    def __init__(self):
        self.runs = []
        self.decisions = []
        self.approvals = []

    def run(self, **kw):
        self.runs.append({"at": _now(), **kw})

    def decision(self, **kw):
        self.decisions.append({"at": _now(), **kw})

    def approval(self, **kw):
        self.approvals.append({"at": _now(), **kw})
