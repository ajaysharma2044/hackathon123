"""
The Agent Governor (docs/agentic/architecture.md). Drives the node graph via the core loop:

    UNKNOWN -> VOI-rank -> AgentTask -> run -> {Evidence | Decompose | Defer | RequestAction}
            -> NodeUpdate -> (recurse / rollup) -> Reoptimize

Recursive decomposition (a node becomes children), permission gates (external actions BLOCK for
approval, never auto-execute), and append-only run/decision/approval logs. Plus the one-button Cornell
pipeline. VOI prioritization reuses the spirit of voi.py: resolve the highest-value-of-information
node first, and rank the still-open ones as the human's next-action list.
"""
from __future__ import annotations
import agent_os as aos
from agent_os import (Node, NodeGraph, NodeStatus, Permission, Evidence, Decompose, Defer,
                      RequestAction, TaskQueue, Log)
import agents

class Governor:
    def __init__(self, graph: NodeGraph, ctx=None, max_steps=300):
        self.g = graph; self.ctx = ctx or {}; self.q = TaskQueue(); self.log = Log()
        self.max_steps = max_steps; self.approvals = []

    def run(self):
        steps = 0
        while steps < self.max_steps:
            self._rollup()                                   # promote DECOMPOSED parents whose kids are done
            ready = self.g.ready()
            if not ready:
                break
            node = max(ready, key=lambda n: n.voi)           # VOI-prioritized dispatch
            steps += 1
            self._dispatch(node)
        self._rollup()
        return self.report()

    def _dispatch(self, node: Node):
        entry = agents.get(node.resolver) if node.resolver else None
        if entry is None:                                    # no agent: it's a human/leaf node
            if node.status == NodeStatus.UNKNOWN:
                node.status = NodeStatus.NEEDS_RESEARCH
            self.log.run(node=node.id, agent=None, outcome="no-resolver -> human")
            return
        fn, perm = entry
        task = self.q.push(node.id, node.resolver, perm)
        node.status = NodeStatus.RESOLVING
        res = fn(node, self.g, self.ctx)                     # run the agent
        self.log.run(node=node.id, agent=node.resolver, permission=perm.value, result=type(res).__name__)
        self._apply(node, res, task)

    def _apply(self, node, res, task):
        if isinstance(res, Evidence):
            node.resolve(res.value, res.provenance, res.status); task.status = "DONE"
            self.log.decision(node=node.id, decision="RESOLVED", provenance=res.provenance)
            self._reoptimize(node)
        elif isinstance(res, Decompose):
            node.status = NodeStatus.DECOMPOSED
            for k in res.children:
                self.g.add(k); node.children.append(k.id)
            task.status = "DONE"
            self.log.decision(node=node.id, decision="DECOMPOSED", n_children=len(res.children))
        elif isinstance(res, Defer):
            node.status = res.status; node.provenance = res.reason; task.status = "DONE"
            self.log.decision(node=node.id, decision=f"DEFER->{res.status.value}", reason=res.reason)
        elif isinstance(res, RequestAction):                 # permission gate: never auto-execute
            node.status = NodeStatus.BLOCKED; task.status = "NEEDS_APPROVAL"
            self.approvals.append({"task": task.id, "node": node.id, "action": res.description, "payload": res.payload})
            self.log.approval(node=node.id, action=res.description, state="AWAITING_HUMAN_APPROVAL")

    def _rollup(self):
        for n in self.g.all():
            if n.status == NodeStatus.DECOMPOSED and self.g.children_all_done(n):
                n.resolve("(resolved via children)", "decomposition rollup", NodeStatus.RESOLVED)

    def _reoptimize(self, node):
        """Reoptimization hook: when cost/pricing/design changes, the portfolio node (still UNKNOWN with
        deps on them) is naturally re-picked when its deps are all resolved. Logged for the trace."""
        if node.id in ("cost", "pricing", "event_design"):
            self.log.decision(node="portfolio", decision="REOPTIMIZE_TRIGGERED_BY", by=node.id)

    def approve(self, task_id):
        """A human approves a gated action. The framework records it; it still does not send anything
        here -- executing an external send stays a human step (safety)."""
        for a in self.approvals:
            if a["task"] == task_id:
                a["state"] = "APPROVED_BY_HUMAN"; self.log.approval(node=a["node"], action=a["action"], state="APPROVED")
                return a
        return None

    def report(self):
        voi_rank = sorted(self.g.open_for_humans(), key=lambda n: -n.voi)
        return {
            "resolved": {n.id: n.value for n in self.g.by_status(NodeStatus.RESOLVED)},
            "open_for_humans": [{"node": n.id, "q": n.question, "status": n.status.value, "voi": n.voi,
                                 "next": n.provenance} for n in voi_rank],
            "awaiting_approval": self.approvals,
            "counts": {s.value: len(self.g.by_status(s)) for s in NodeStatus if self.g.by_status(s)},
            "log_sizes": {"runs": len(self.log.runs), "decisions": len(self.log.decisions), "approvals": len(self.log.approvals)},
        }

# ------------------------------------------------------------------- the one-button Cornell pipeline ----
def build_cornell_graph() -> NodeGraph:
    g = NodeGraph()
    N = lambda **k: g.add(Node(**k))
    N(id="capability", question="What can Cornell builders actually build?", resolver="cornell_capability", voi=2)
    N(id="industries", question="Which industries have the sharpest pains?", resolver="industry_expansion", voi=2)
    N(id="sponsors", question="Who would sponsor / buy?", resolver="sponsor_discovery", voi=3)
    N(id="topic", question="What is the event topic?", resolver="topic_synthesis", deps=["capability", "industries"], voi=3)
    N(id="falsifier", question="How would the topic be falsified?", resolver="falsifier", deps=["topic"], voi=2)
    N(id="pricing", question="What should we charge?", resolver="pricing", voi=2)
    N(id="cost", question="What will the event cost?", resolver="cost", voi=3)
    N(id="attendance", question="How many builders can we get?", resolver="attendance", deps=["capability"], voi=1)
    N(id="event_design", question="What is the event design?", resolver="event_design", deps=["cost", "attendance"], voi=2)
    N(id="portfolio", question="Does it make money?", resolver="portfolio_optimizer", deps=["cost", "pricing"], voi=3)
    N(id="outreach", question="Email a sponsor/venue?", resolver="outreach", deps=["cost"], voi=1)
    return g

def run_cornell(n_builders=250):
    gov = Governor(build_cornell_graph(), ctx={"n_builders": n_builders})
    return gov, gov.run()

if __name__ == "__main__":
    import json
    gov, rep = run_cornell()
    print("=== RESOLVED autonomously ===")
    for k, v in rep["resolved"].items():
        print(f"  {k}: {v}")
    print("\n=== OPEN for humans (VOI-ranked next actions) ===")
    for o in rep["open_for_humans"]:
        print(f"  [{o['status']:14}] voi={o['voi']} {o['node']}: {o['next']}")
    print("\n=== AWAITING APPROVAL (external actions, gated) ===")
    for a in rep["awaiting_approval"]:
        print(f"  {a['task']} {a['node']}: {a['action']}")
    print("\ncounts:", rep["counts"], "\nlogs:", rep["log_sizes"])
