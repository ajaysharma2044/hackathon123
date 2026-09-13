"""Evidence-first research governor."""
from __future__ import annotations

from agent_os import (
    Node, NodeGraph, NodeStatus, Evidence, Decompose, Defer,
    RequestAction, TaskQueue, Log,
)
import agents
import dynamic_agents  # noqa: F401 - registers dynamic research agents


class Governor:
    def __init__(self, graph, ctx=None, max_steps=300):
        self.g = graph
        self.ctx = ctx or {}
        self.q = TaskQueue()
        self.log = Log()
        self.max_steps = max_steps
        self.approvals = []
        self.step = 0

    def run(self):
        while self.step < self.max_steps:
            self._rollup()
            ready = self.g.ready()
            if not ready:
                break
            node = max(
                ready,
                key=lambda n: (n.voi / (1 + n.attempt_count), -n.attempt_count, n.id),
            )
            self.step += 1
            self._dispatch(node)
        self._rollup()
        return self.report()

    def _dispatch(self, node):
        entry = agents.get(node.resolver) if node.resolver else None
        if entry is None:
            node.status = NodeStatus.CONTRACT_REQUIRED
            node.retryable = False
            node.provenance = "No resolver/contract registered"
            self.log.run(node=node.id, agent=None, outcome="contract-required")
            return
        fn, perm = entry
        task = self.q.push(node.id, node.resolver, perm)
        node.status = NodeStatus.RESEARCHING
        node.attempt_count += 1
        res = fn(node, self.g, self.ctx)
        self.log.run(
            node=node.id,
            agent=node.resolver,
            permission=perm.value,
            result=type(res).__name__,
            attempt=node.attempt_count,
        )
        self._apply(node, res, task)

    def _claims_coverage(self, value):
        if not isinstance(value, dict):
            return [], None
        from research_contracts import AtomicClaim, ResearchCoverage
        claims = [c for c in value.get("claims", []) if isinstance(c, AtomicClaim)]
        cov = value.get("coverage")
        return claims, cov if isinstance(cov, ResearchCoverage) else ResearchCoverage()

    def _gate(self, node, value):
        if not node.completion_gate:
            return True, {}
        from research_contracts import get_gate
        claims, cov = self._claims_coverage(value)
        result = get_gate(node.completion_gate).evaluate(
            claims,
            node.critical_unknown_fields,
            cov,
        )
        return result.complete, {
            "missing": result.missing,
            "weak": result.weak,
            "primary_validation": result.primary_validation,
            "missing_negative_search": result.missing_negative_search,
        }

    def _apply(self, node, res, task):
        if isinstance(res, Evidence):
            ok, detail = self._gate(node, res.value)
            if not ok:
                node.value = res.value
                node.provenance = res.provenance
                node.evidence.append({
                    "value": res.value,
                    "provenance": res.provenance,
                    "gate": detail,
                })
                if detail.get("primary_validation"):
                    node.status = NodeStatus.PRIMARY_VALIDATION_REQUIRED
                    node.retryable = False
                elif node.attempt_count >= node.max_attempts:
                    node.status = NodeStatus.RESEARCH_EXHAUSTED
                    node.retryable = False
                else:
                    node.status = NodeStatus.PARTIAL
                task.status = "DONE"
                self.log.decision(
                    node=node.id,
                    decision="GATE_REJECTED_RESOLUTION",
                    detail=detail,
                )
                return
            node.resolve(res.value, res.provenance)
            task.status = "DONE"
            self.log.decision(
                node=node.id,
                decision="RESOLVED",
                provenance=res.provenance,
            )
            return

        if isinstance(res, Decompose):
            node.status = NodeStatus.PARTIAL
            node.retryable = False
            for child in res.children:
                existing = self.g.add(child)
                if existing.id not in node.children:
                    node.children.append(existing.id)
            task.status = "DONE"
            self.log.decision(
                node=node.id,
                decision="DECOMPOSED",
                n_children=len(res.children),
            )
            return

        if isinstance(res, Defer):
            node.status = res.status
            node.provenance = res.reason
            if res.status in {
                NodeStatus.PRIMARY_VALIDATION_REQUIRED,
                NodeStatus.RESEARCH_BACKEND_REQUIRED,
                NodeStatus.CONTRACT_REQUIRED,
                NodeStatus.RESEARCH_EXHAUSTED,
                NodeStatus.BLOCKED,
            }:
                node.retryable = False
            elif node.attempt_count >= node.max_attempts:
                node.status = NodeStatus.RESEARCH_EXHAUSTED
                node.retryable = False
            task.status = "DONE"
            self.log.decision(
                node=node.id,
                decision=f"DEFER->{node.status.value}",
                reason=res.reason,
            )
            return

        if isinstance(res, RequestAction):
            node.status = NodeStatus.BLOCKED
            node.retryable = False
            task.status = "NEEDS_APPROVAL"
            self.approvals.append({
                "task": task.id,
                "node": node.id,
                "action": res.description,
                "payload": res.payload,
                "state": "AWAITING_HUMAN_APPROVAL",
            })
            self.log.approval(
                node=node.id,
                action=res.description,
                state="AWAITING_HUMAN_APPROVAL",
            )
            return

        node.status = NodeStatus.RESEARCH_EXHAUSTED
        node.retryable = False
        task.status = "FAILED"

    def _rollup(self):
        for node in self.g.all():
            if (
                node.children
                and node.status == NodeStatus.PARTIAL
                and self.g.children_all_done(node)
            ):
                node.resolve(
                    {"resolved_via_children": list(node.children)},
                    "decomposition rollup",
                )

    def approve(self, task_id):
        """Record human approval; executing the external action remains outside this kernel."""
        for approval in self.approvals:
            if approval["task"] == task_id:
                approval["state"] = "APPROVED_BY_HUMAN"
                self.log.approval(
                    node=approval["node"],
                    action=approval["action"],
                    state="APPROVED",
                )
                return approval
        return None

    def report(self):
        opens = sorted(self.g.open_for_humans(), key=lambda n: (-n.voi, n.id))
        open_rows = [
            {
                "node": n.id,
                "q": n.question,
                "status": n.status.value,
                "voi": n.voi,
                "attempts": n.attempt_count,
                "next": n.provenance,
            }
            for n in opens
        ]
        return {
            "resolved": {
                n.id: n.value for n in self.g.by_status(NodeStatus.RESOLVED)
            },
            "open": open_rows,
            # Backward-compatible name used by old diagnostics.
            "open_for_humans": open_rows,
            "awaiting_approval": self.approvals,
            "counts": {
                s.value: len(self.g.by_status(s))
                for s in NodeStatus
                if self.g.by_status(s)
            },
            "log_sizes": {
                "runs": len(self.log.runs),
                "decisions": len(self.log.decisions),
                "approvals": len(self.log.approvals),
            },
        }


def build_research_graph(objective):
    g = NodeGraph()
    g.add(Node(
        "discovery",
        f"Discover the broad economic/event search space for: {objective}",
        "dynamic_discovery",
        node_type="discovery",
        voi=5,
        max_attempts=7,
    ))
    g.add(Node(
        "themes",
        "Generate evidence-backed event themes from the discovered search space",
        "dynamic_theme_generation",
        node_type="theme_frontier",
        deps=["discovery"],
        voi=4,
        max_attempts=4,
    ))
    g.add(Node(
        "final_synthesis",
        "Compare evidence-complete themes without introducing new factual claims",
        "evidence_only_synthesis",
        node_type="synthesis",
        deps=["themes"],
        voi=3,
        max_attempts=2,
    ))
    return g


def build_cornell_graph():
    return build_research_graph(
        "Find the optimal first Cornell hackathon/event, its participant value, "
        "company ecosystem, research/R&D/data surfaces, commercial model, and "
        "validation plan."
    )


def run_cornell(ctx=None):
    gov = Governor(build_cornell_graph(), ctx=ctx or {})
    return gov, gov.run()
