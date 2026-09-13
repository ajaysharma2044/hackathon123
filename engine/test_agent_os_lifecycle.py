from agent_os import Node, NodeGraph, NodeStatus


def test_needs_research_alias_is_open_not_done():
    g = NodeGraph()
    child = g.add(Node("child", "needs more evidence", status=NodeStatus.NEEDS_RESEARCH))
    parent = g.add(Node("parent", "parent", status=NodeStatus.PARTIAL, children=["child"]))
    assert not g.children_all_done(parent)


def test_primary_validation_is_open_not_done():
    g = NodeGraph()
    g.add(Node("primary", "will buyer pay?", status=NodeStatus.PRIMARY_VALIDATION_REQUIRED))
    dependent = g.add(Node("decision", "final decision", deps=["primary"]))
    assert dependent not in g.ready()


def test_resolved_dependency_allows_dispatch():
    g = NodeGraph()
    g.add(Node("done", "done", status=NodeStatus.RESOLVED))
    dependent = g.add(Node("next", "next", deps=["done"]))
    assert dependent in g.ready()
