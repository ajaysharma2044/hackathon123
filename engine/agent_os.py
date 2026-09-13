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
SUCCESS_TERMINAL = {NodeStatus.RESOLVED, NodeStatus.KILLED}
OPEN_STATES = {
    NodeStatus.UNRESEARCHED,
    NodeStatus.RESEARCHING,
    NodeStatus.PARTIAL,
    NodeStatus.CONTRADICTED,
    NodeStatus.EVIDENCE_COMPLETE,
    NodeStatus.SYNTHESIS_READY,
    NodeStatus.PRIMARY_VALIDATION_REQUIRED,
    NodeStatus.BLOCKED,
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

    def resolve(self, value, provenance, status=NodeStatus.RESOLVED):
        if status not in SUCCESS_TERMINAL and status != NodeStatus.RESOLVED:
            raise ValueError(f"resolve() requires a terminal success status, got {status}")
        self.value, self.provenance, self.status = value, provenance, status
        self.evidence.append({"value": value, "provenance": provenance, "at": _now()})


class NodeGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}

    def add(self, node: Node) -> Node:
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
        }]

    def dependency_complete(self, node_id: str) -> bool:
        return self.nodes[node_id].status in SUCCESS_TERMINAL

    def ready(self):
        """Only dispatch nodes whose dependencies are genuinely finished."""
        return [
            n for n in self.unknown()
            if all(self.dependency_complete(d) for d in n.deps)
        ]

    def children_all_done(self, node):
        return bool(node.children) and all(
            self.nodes[c].status in SUCCESS_TERMINAL for c in node.children
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
