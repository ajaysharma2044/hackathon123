"""python3 test_agent_os.py -- guardrails for the agentic OS (governor, graph, permissions, logs)."""
import agent_os as aos
from agent_os import Node, NodeGraph, NodeStatus, Permission, Evidence, Decompose, Defer, RequestAction
import agents, governor
P = F = 0
def ck(n, c):
    global P, F; P += bool(c); F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# ---- graph: dependency-aware readiness --------------------------------------
g = NodeGraph()
g.add(Node("a", "a", resolver="x")); g.add(Node("b", "b", resolver="x", deps=["a"]))
ck("a node with an unresolved dep is NOT ready", [n.id for n in g.ready()] == ["a"])
g.get("a").resolve(1, "test")
ck("it becomes ready once its dep resolves", "b" in [n.id for n in g.ready()])

# ---- governor: autonomous Evidence resolves a node --------------------------
order = []
agents.REGISTRY["_mock_hi"] = (lambda node, gr, ctx: order.append(node.id) or Evidence(42, "mock"), Permission.AUTONOMOUS_READ)
agents.REGISTRY["_mock_lo"] = (lambda node, gr, ctx: order.append(node.id) or Evidence(7, "mock"), Permission.AUTONOMOUS_READ)
g2 = NodeGraph()
g2.add(Node("lo", "lo", resolver="_mock_lo", voi=1)); g2.add(Node("hi", "hi", resolver="_mock_hi", voi=9))
gov = governor.Governor(g2); gov.run()
ck("autonomous agent resolves its node with a value+provenance", g2.get("hi").value == 42 and g2.get("hi").status == NodeStatus.RESOLVED)
ck("VOI prioritization dispatches the higher-voi node FIRST", order[0] == "hi")

# ---- decomposition + rollup -------------------------------------------------
agents.REGISTRY["_decomp"] = (lambda node, gr, ctx: Decompose([Node("kid1","k1",resolver="_mock_lo"), Node("kid2","k2",resolver="_mock_lo")]), Permission.AUTONOMOUS_READ)
g3 = NodeGraph(); g3.add(Node("parent", "p", resolver="_decomp"))
governor.Governor(g3).run()
ck("a decomposed node gains children", set(g3.get("parent").children) == {"kid1", "kid2"})
ck("parent rolls up to RESOLVED once all children terminal", g3.get("parent").status == NodeStatus.RESOLVED)

# ---- defer: no fabrication --------------------------------------------------
agents.REGISTRY["_defer"] = (lambda node, gr, ctx: Defer(NodeStatus.PRIMARY, "exists nowhere online"), Permission.AUTONOMOUS_READ)
g4 = NodeGraph(); g4.add(Node("wtp", "buyer WTP?", resolver="_defer", voi=5))
governor.Governor(g4).run()
ck("a PRIMARY-deferred node is NEVER given a value (no fabrication)", g4.get("wtp").value is None and g4.get("wtp").status == NodeStatus.PRIMARY)

# ---- permission gate: external action BLOCKS for approval, never executes ----
g5 = NodeGraph(); g5.add(Node("email", "email a sponsor?", resolver="outreach", voi=1))
gov5 = governor.Governor(g5, ctx={}); rep5 = gov5.run()
ck("an external-action node is BLOCKED, not resolved", g5.get("email").status == NodeStatus.BLOCKED)
ck("the action is queued for human approval", len(rep5["awaiting_approval"]) == 1)
appr = gov5.approve(rep5["awaiting_approval"][0]["task"])
ck("approve() records human approval", appr["state"] == "APPROVED_BY_HUMAN")

# ---- append-only logs --------------------------------------------------------
ck("runs + decisions are logged append-only", len(gov.log.runs) >= 1 and len(gov.log.decisions) >= 1)

# ---- no-resolver leaf -> human ----------------------------------------------
g6 = NodeGraph(); g6.add(Node("human_only", "a human decision", resolver=None))
governor.Governor(g6).run()
ck("a node with no resolver routes to NEEDS_RESEARCH (human)", g6.get("human_only").status == NodeStatus.NEEDS_RESEARCH)

# ---- the one-button Cornell pipeline (integration) --------------------------
gov7, rep = governor.run_cornell()
ck("offline pipeline cannot resolve any business facts", not rep['resolved'])
ck("offline pipeline explicitly requires research", any('RESEARCH_BACKEND_REQUIRED' in str(n['next']) for n in rep['open_for_humans']))
ck("offline pipeline does not plan unsolicited outreach", not rep['awaiting_approval'])

# cleanup mock agents
for k in ["_mock_hi","_mock_lo","_decomp","_defer"]: agents.REGISTRY.pop(k, None)

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
