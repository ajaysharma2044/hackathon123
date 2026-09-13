"""Guardrails for the evidence-first agentic OS."""
import agent_os as aos
from agent_os import (
    Node, NodeGraph, NodeStatus, Permission,
    Evidence, Decompose, Defer,
)
import agents
import governor


def test_dependency_readiness():
    g = NodeGraph()
    g.add(Node("a", "a", resolver="x"))
    g.add(Node("b", "b", resolver="x", deps=["a"]))
    assert [n.id for n in g.ready()] == ["a"]
    g.get("a").resolve(1, "test")
    assert "b" in [n.id for n in g.ready()]


def test_governor_resolves_evidence_and_prioritizes_voi():
    order = []
    agents.REGISTRY["_mock_hi"] = (
        lambda node, gr, ctx: order.append(node.id) or Evidence(42, "mock"),
        Permission.AUTONOMOUS_READ,
    )
    agents.REGISTRY["_mock_lo"] = (
        lambda node, gr, ctx: order.append(node.id) or Evidence(7, "mock"),
        Permission.AUTONOMOUS_READ,
    )
    try:
        g = NodeGraph()
        g.add(Node("lo", "lo", resolver="_mock_lo", voi=1))
        g.add(Node("hi", "hi", resolver="_mock_hi", voi=9))
        gov = governor.Governor(g)
        gov.run()
        assert g.get("hi").value == 42
        assert g.get("hi").status == NodeStatus.RESOLVED
        assert order[0] == "hi"
        assert gov.log.runs and gov.log.decisions
    finally:
        agents.REGISTRY.pop("_mock_hi", None)
        agents.REGISTRY.pop("_mock_lo", None)


def test_decomposition_rolls_up_only_after_real_child_completion():
    agents.REGISTRY["_mock_leaf"] = (
        lambda node, gr, ctx: Evidence(7, "mock"),
        Permission.AUTONOMOUS_READ,
    )
    agents.REGISTRY["_decomp"] = (
        lambda node, gr, ctx: Decompose([
            Node("kid1", "k1", resolver="_mock_leaf"),
            Node("kid2", "k2", resolver="_mock_leaf"),
        ]),
        Permission.AUTONOMOUS_READ,
    )
    try:
        g = NodeGraph()
        g.add(Node("parent", "p", resolver="_decomp"))
        governor.Governor(g).run()
        assert set(g.get("parent").children) == {"kid1", "kid2"}
        assert g.get("parent").status == NodeStatus.RESOLVED
    finally:
        agents.REGISTRY.pop("_mock_leaf", None)
        agents.REGISTRY.pop("_decomp", None)


def test_primary_validation_never_fabricates_value():
    agents.REGISTRY["_defer"] = (
        lambda node, gr, ctx: Defer(
            NodeStatus.PRIMARY_VALIDATION_REQUIRED,
            "requires a real buyer commitment",
        ),
        Permission.AUTONOMOUS_READ,
    )
    try:
        g = NodeGraph()
        g.add(Node("wtp", "buyer WTP?", resolver="_defer", voi=5))
        governor.Governor(g).run()
        assert g.get("wtp").value is None
        assert g.get("wtp").status == NodeStatus.PRIMARY_VALIDATION_REQUIRED
    finally:
        agents.REGISTRY.pop("_defer", None)


def test_permission_gate_and_human_approval_recording():
    g = NodeGraph()
    g.add(Node("email", "email a sponsor?", resolver="outreach", voi=1))
    gov = governor.Governor(g, ctx={})
    report = gov.run()
    assert g.get("email").status == NodeStatus.BLOCKED
    assert len(report["awaiting_approval"]) == 1
    approval = gov.approve(report["awaiting_approval"][0]["task"])
    assert approval["state"] == "APPROVED_BY_HUMAN"


def test_no_resolver_requires_contract_not_guessing():
    g = NodeGraph()
    g.add(Node("unknown_type", "something unsupported", resolver=None))
    governor.Governor(g).run()
    assert g.get("unknown_type").status == NodeStatus.CONTRACT_REQUIRED


def test_offline_cornell_pipeline_does_not_fall_back_to_hardcoded_answers():
    gov, report = governor.run_cornell(ctx={"offline": True})
    assert gov.g.get("discovery").status == NodeStatus.RESEARCH_BACKEND_REQUIRED
    assert "cost" not in report["resolved"]
    assert "pricing" not in report["resolved"]
    assert not report["resolved"]
