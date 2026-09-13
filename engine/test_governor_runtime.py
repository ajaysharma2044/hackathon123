from governor import build_cornell_graph, Governor
from agent_os import NodeStatus


def test_offline_runtime_imports_and_stops_honestly():
    gov = Governor(build_cornell_graph(), ctx={"offline": True}, max_steps=10)
    report = gov.run()
    discovery = gov.g.get("discovery")
    assert discovery.status == NodeStatus.RESEARCH_BACKEND_REQUIRED
    assert "discovery" not in report["resolved"]
    assert report["counts"].get("RESEARCH_BACKEND_REQUIRED") == 1
