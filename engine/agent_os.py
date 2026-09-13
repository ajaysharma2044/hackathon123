"""
Agentic OS core (docs/agentic/architecture.md). The node graph, task queue, permission gates, and
append-only logs the Governor drives. The core loop is:

    UNKNOWN -> VOI -> AgentTask -> Research -> Evidence -> NodeUpdate -> Reoptimization

Discipline carried from the rest of the repo: a node is never fabricated. UNKNOWN means unresolved;
QUOTE means real-but-behind-contact; PRIMARY means it exists nowhere online (a human commitment).
External actions (email/spend/publish) are permission-gated -- an agent may propose them, never
execute them autonomously. Every run/decision/approval is logged append-only (tri-temporal spirit).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import itertools

def _now(): return datetime.now().isoformat(timespec="seconds")

class NodeStatus(str, Enum):
    UNKNOWN = "UNKNOWN"           # not yet resolved
    RESOLVING = "RESOLVING"       # an agent is working it
    RESOLVED = "RESOLVED"         # has a sourced value
    DECOMPOSED = "DECOMPOSED"     # replaced by children; resolves when they do
    NEEDS_RESEARCH = "NEEDS_RESEARCH"  # needs live web/LLM cognition (hook, not yet run)
    QUOTE = "QUOTE"               # real but behind 'contact us' -> a human email
    PRIMARY = "PRIMARY"           # exists nowhere online -> only a human commitment resolves it
    BLOCKED = "BLOCKED"           # awaiting an approval gate

class Permission(str, Enum):
    AUTONOMOUS_READ = "AUTONOMOUS_READ"   # read-only research: runs with no approval
    NEEDS_APPROVAL = "NEEDS_APPROVAL"     # external action: routed to an approval gate

TERMINAL = {NodeStatus.RESOLVED, NodeStatus.QUOTE, NodeStatus.PRIMARY, NodeStatus.NEEDS_RESEARCH}

@dataclass
class Node:
    id: str
    question: str
    resolver: str = None                       # agent-type expected to resolve it
    status: NodeStatus = NodeStatus.UNKNOWN
    value: object = None
    provenance: str = None                     # source/agent + date once resolved
    deps: list = field(default_factory=list)   # node ids that must resolve first
    children: list = field(default_factory=list)
    voi: float = 0.0                           # priority weight (value of resolving it)
    evidence: list = field(default_factory=list)
    def resolve(self, value, provenance, status=NodeStatus.RESOLVED):
        self.value, self.provenance, self.status = value, provenance, status
        self.evidence.append({"value": value, "provenance": provenance, "at": _now()})

class NodeGraph:
    def __init__(self): self.nodes: dict[str, Node] = {}
    def add(self, node: Node) -> Node: self.nodes[node.id] = node; return node
    def get(self, i) -> Node: return self.nodes[i]
    def all(self): return list(self.nodes.values())
    def by_status(self, *st): return [n for n in self.nodes.values() if n.status in st]
    def unknown(self): return self.by_status(NodeStatus.UNKNOWN)
    def open_for_humans(self):  # what the agents legitimately could not resolve
        return self.by_status(NodeStatus.QUOTE, NodeStatus.PRIMARY, NodeStatus.NEEDS_RESEARCH)
    def ready(self):            # UNKNOWN nodes whose deps are all resolved (dependency-aware)
        done = lambda d: self.nodes[d].status in TERMINAL or self.nodes[d].status == NodeStatus.DECOMPOSED
        return [n for n in self.unknown() if all(done(d) for d in n.deps)]
    def children_all_done(self, node):
        return node.children and all(self.nodes[c].status in TERMINAL for c in node.children)

@dataclass
class AgentTask:
    id: str
    node_id: str
    agent_type: str
    permission: Permission
    status: str = "QUEUED"     # QUEUED | RUNNING | DONE | NEEDS_APPROVAL | FAILED
    created_at: str = field(default_factory=_now)

class TaskQueue:
    def __init__(self): self._q: list[AgentTask] = []; self._c = itertools.count(1)
    def push(self, node_id, agent_type, permission) -> AgentTask:
        t = AgentTask(f"task_{next(self._c)}", node_id, agent_type, permission)
        self._q.append(t); return t
    def pending(self): return [t for t in self._q if t.status == "QUEUED"]
    def all(self): return list(self._q)

# What an agent hands back from run(): resolve the node, decompose it, defer it, or request an action.
@dataclass
class Evidence:      value: object; provenance: str; status: NodeStatus = NodeStatus.RESOLVED
@dataclass
class Decompose:     children: list                       # list[Node] to add under the node
@dataclass
class Defer:         status: NodeStatus; reason: str      # QUOTE / PRIMARY / NEEDS_RESEARCH
@dataclass
class RequestAction: description: str; payload: dict = field(default_factory=dict)  # NEEDS_APPROVAL

class Log:
    """Append-only run / decision / approval logs. Never mutated in place (tri-temporal spirit)."""
    def __init__(self): self.runs = []; self.decisions = []; self.approvals = []
    def run(self, **kw): self.runs.append({"at": _now(), **kw})
    def decision(self, **kw): self.decisions.append({"at": _now(), **kw})
    def approval(self, **kw): self.approvals.append({"at": _now(), **kw})
