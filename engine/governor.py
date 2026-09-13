"""
Agent Governor.

The Governor dispatches work, but it no longer trusts an agent's self-assessment that a research
node is complete. Nodes may declare a deterministic completion_gate; sourced atomic claims are
validated against that gate before RESOLVED is allowed.

UNKNOWN/UNRESEARCHED -> research -> PARTIAL/CONTRADICTED -> EVIDENCE_COMPLETE -> RESOLVED
Primary validation remains open and can only be closed by a real-world observation/commitment.
"""
from __future__ import annotations

import agent_os as aos
from agent_os import (
    Node, NodeGraph, NodeStatus, Permission, Evidence, Decompose, Defer,
    RequestAction, TaskQueue, Log,
)
import agents
import dynamic_agents  # noqa: F401 - import registers dynamic agents with agents.REGISTRY


class Governor:
    def __init__(self, graph: NodeGraph, ctx=None, max_steps=300):
        self.g = graph
        self.ctx = ctx if ctx is not None else {}
        self.q = TaskQueue()
        self.log = Log()
        self.max_steps = max_steps
        self.approvals = []

    def run(self):
        steps = 0
        while steps < self.max_steps:
            self._rollup()
            ready = self.g.ready()
            if not ready:
                break
            node = max(ready, key=lambda n: n.voi)
            steps += 1
            self._dispatch(node)
        self._rollup()
        return self.report()

    def resume(self, node_ids=None):
        """Explicitly retry unresolved research after new evidence or adapter configuration.

        Does not retry external actions or erase accepted claims/negative-search history.
        """
        for n in self.g.all():
            if node_ids is not None and n.id not in node_ids:
                continue
            entry = agents.get(n.resolver)
            if entry and entry[1] == Permission.AUTONOMOUS_READ and n.status in (
                    NodeStatus.PARTIAL, NodeStatus.CONTRADICTED, NodeStatus.PRIMARY_VALIDATION_REQUIRED, NodeStatus.BLOCKED, NodeStatus.RESEARCH_BACKEND_REQUIRED,
                    NodeStatus.CONTRACT_REQUIRED, NodeStatus.RESEARCH_EXHAUSTED):
                n.status = NodeStatus.UNRESEARCHED
                n.attempt_count = 0
                n.retryable = True
        return self.run()

    def _dispatch(self, node: Node):
        entry = agents.get(node.resolver) if node.resolver else None
        if entry is None:
            if node.status == NodeStatus.UNRESEARCHED:
                node.status = NodeStatus.PARTIAL
            node.retryable = False
            self.log.run(node=node.id, agent=None, outcome="no-resolver -> open")
            return
        fn, perm = entry
        task = self.q.push(node.id, node.resolver, perm)
        node.attempt_count += 1
        node.status = NodeStatus.RESEARCHING
        if perm == Permission.NEEDS_APPROVAL:
            res = RequestAction('Execute external action: ' + node.resolver, {'question': node.question})
        else:
            try:
                res = fn(node, self.g, self.ctx)
            except Exception as exc:
                res = Defer(NodeStatus.BLOCKED, f'RESEARCH_ERROR: {type(exc).__name__}: {exc}')
        self.log.run(
            node=node.id,
            agent=node.resolver,
            permission=perm.value,
            result=type(res).__name__,
        )
        self._apply(node, res, task)

    def _validate_completion_gate(self, node: Node, value) -> tuple[bool, dict]:
        if not all(self.g.dependency_complete(i) for i in node.deps + node.children):
            return False, {'missing': ['required_children_or_dependencies']}
        if not node.completion_gate:
            if node.node_type and node.resolver not in ('dynamic_discovery', 'evidence_only_synthesis', 'dynamic_theme_generation'):
                return False, {'missing': ['type_specific_completion_contract']}
            return True, {}
        from research_contracts import AtomicClaim, get_gate
        if node.node_type:
            bridge = self.ctx.get('research_bridge')
            memory = bridge.memory if bridge else None
            raw = value.get('claims', []) if isinstance(value, dict) else []
            if memory is None or not raw or any(not isinstance(c, AtomicClaim) or
                    memory.claims.get(c.claim_id) != c or c.subject_id != node.id for c in raw):
                return False, {'missing': ['accepted_opened_source_evidence']}
            if any(memory.claims.get(c.claim_id) != c for c in value.get('supporting_claims',())):
                return False, {'missing': ['accepted_supporting_evidence']}
            if node.node_type in ('data_opportunity','rd_opportunity'):
                from research_opportunities import ResearchOpportunity
                from research_config import ResearchConfig
                spec = value.get('opportunity')
                if not isinstance(spec,ResearchOpportunity):
                    return False, {'missing': ['structured_opportunity_plan']}
                errors = spec.validate(memory,self.ctx.get('research_config') or ResearchConfig())
                if errors:return False, {'missing':errors}

        claims = []
        raw_claims = value.get("claims", []) if isinstance(value, dict) else []
        for c in raw_claims:
            if isinstance(c, AtomicClaim):
                claims.append(c)
        result = get_gate(node.completion_gate).evaluate(
            claims,
            critical_unknown_fields=node.critical_unknown_fields,
            searches=value.get("searches", []) if isinstance(value, dict) else (),
            profile=value.get("profile") if isinstance(value, dict) else None,
            config=self.ctx.get("research_config"),
            supporting_claims=value.get("supporting_claims",()),
        )
        return result.complete, {
            "missing": result.missing,
            "weak": result.weak,
            "primary_validation": result.primary_validation,
        }

    def _apply(self, node, res, task):
        if isinstance(res, Evidence):
            if res.status != NodeStatus.RESOLVED:
                node.status = res.status if res.status not in aos.SUCCESS_TERMINAL else NodeStatus.PARTIAL
                node.value, node.provenance = res.value, res.provenance
                task.status = 'DONE'
                return
            gate_ok, gate_detail = self._validate_completion_gate(node, res.value)
            if not gate_ok:
                node.status = (
                    NodeStatus.PRIMARY_VALIDATION_REQUIRED
                    if gate_detail.get("primary_validation")
                    else NodeStatus.PARTIAL
                )
                node.value = res.value
                node.provenance = res.provenance
                node.evidence.append({
                    "value": res.value,
                    "provenance": res.provenance,
                    "gate": gate_detail,
                })
                task.status = "DONE"
                self.log.decision(
                    node=node.id,
                    decision="GATE_REJECTED_RESOLUTION",
                    detail=gate_detail,
                )
                return
            node.resolve(res.value, res.provenance, NodeStatus.RESOLVED)
            task.status = "DONE"
            self.log.decision(node=node.id, decision="RESOLVED", provenance=res.provenance)
            self._reoptimize(node)

        elif isinstance(res, Decompose):
            node.status = NodeStatus.PARTIAL
            for k in res.children:
                self.g.add(k)
                if k.id not in node.children and k.id != node.id:
                    node.children.append(k.id)
            task.status = "DONE"
            self.log.decision(node=node.id, decision="DECOMPOSED", n_children=len(res.children))

        elif isinstance(res, Defer):
            node.status = res.status if res.status not in aos.SUCCESS_TERMINAL else NodeStatus.PARTIAL
            node.provenance = res.reason
            node.retryable = False
            task.status = "DONE"
            self.log.decision(
                node=node.id,
                decision=f"DEFER->{res.status.value}",
                reason=res.reason,
            )

        elif isinstance(res, RequestAction):
            node.status = NodeStatus.BLOCKED
            task.status = "NEEDS_APPROVAL"
            self.approvals.append({
                "task": task.id,
                "node": node.id,
                "action": res.description,
                "payload": res.payload,
            })
            self.log.approval(
                node=node.id,
                action=res.description,
                state="AWAITING_HUMAN_APPROVAL",
            )

    def _rollup(self):
        for n in self.g.all():
            if n.children and n.auto_rollup and self.g.children_all_done(n) and n.status == NodeStatus.PARTIAL:
                value = dict(n.value) if isinstance(n.value, dict) else {}
                value['resolved_via_children'] = list(n.children)
                ok, detail = self._validate_completion_gate(n, value)
                if ok:
                    n.resolve(value, 'required children and parent completion contract passed')
                else:
                    self.log.decision(node=n.id, decision='ROLLUP_GATE_REJECTED', detail=detail)

    def _reoptimize(self, node):
        if node.id in ("cost", "pricing", "event_design"):
            self.log.decision(
                node="portfolio",
                decision="REOPTIMIZE_TRIGGERED_BY",
                by=node.id,
            )

    def approve(self, task_id):
        for a in self.approvals:
            if a["task"] == task_id:
                a["state"] = "APPROVED_BY_HUMAN"
                self.log.approval(node=a["node"], action=a["action"], state="APPROVED")
                return a
        return None

    def report(self):
        voi_rank = sorted(self.g.open_for_humans(), key=lambda n: -n.voi)
        return {
            "resolved": {n.id: n.value for n in self.g.by_status(NodeStatus.RESOLVED)},
            "open_for_humans": [
                {
                    "node": n.id,
                    "q": n.question,
                    "status": n.status.value,
                    "voi": n.voi,
                    "next": n.provenance,
                }
                for n in voi_rank
            ],
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


def build_research_graph(objective: str) -> NodeGraph:
    g = NodeGraph()
    g.add(Node(
        id="discovery",
        question=f"Discover the broad economic/event search space for: {objective}",
        resolver="dynamic_discovery",
        node_type="discovery",
        voi=5.0,
    ))
    g.add(Node(
        id="themes",
        question="Generate and research event themes from discovered evidence",
        resolver="dynamic_theme_generation",
        node_type="theme_frontier",
        deps=["discovery"],
        voi=4.0,
    ))
    for kind in ('cornell', 'cost', 'attendance', 'capacity', 'pricing'):
        g.add(Node(kind, f'Research {kind} for: {objective}', resolver='dynamic_entity_research',
                   node_type=kind, completion_gate=kind, voi=3.0, auto_rollup=False))
    g.add(Node('red_team', f'Independently try to disprove the proposed event: {objective}',
               resolver='independent_red_team', node_type='red_team', completion_gate='red_team',
               deps=['themes','cornell','cost','attendance','capacity','pricing'], voi=4.0, auto_rollup=False))
    g.add(Node(
        id="final_synthesis",
        question="Compare evidence-complete themes; introduce no new factual claims",
        resolver="evidence_only_synthesis",
        node_type="synthesis",
        deps=["themes", "red_team"],
        voi=3.0,
    ))
    return g


def build_cornell_graph() -> NodeGraph:
    return build_research_graph(
        "Find the optimal first Cornell hackathon/event, its participant value, company ecosystem, "
        "research/R&D/data surfaces, commercial model, and validation plan."
    )


def run_cornell(n_builders=None):
    ctx = {}
    if n_builders is not None:
        ctx["scenario_n_builders"] = n_builders
    gov = Governor(build_cornell_graph(), ctx=ctx)
    return gov, gov.run()


if __name__ == "__main__":
    import json
    gov, rep = run_cornell()
    print(json.dumps(rep, indent=2, default=str))
