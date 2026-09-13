from agent_os import Node,NodeGraph,NodeStatus

def test_partial_nodes_are_retryable_until_budget_exhausted():
    g=NodeGraph(); n=g.add(Node("n","research",status=NodeStatus.PARTIAL,attempt_count=1,max_attempts=3)); assert n in g.ready(); n.attempt_count=3; assert n not in g.ready()
def test_primary_validation_is_open_not_dispatchable():
    g=NodeGraph(); n=g.add(Node("primary","will buyer pay?",status=NodeStatus.PRIMARY_VALIDATION_REQUIRED)); assert n not in g.ready()
def test_backend_required_is_open_not_dispatchable():
    g=NodeGraph(); n=g.add(Node("backend","need web",status=NodeStatus.RESEARCH_BACKEND_REQUIRED)); assert n not in g.ready()
def test_unresolved_child_does_not_resolve_parent():
    g=NodeGraph(); g.add(Node("child","needs research",status=NodeStatus.PARTIAL)); p=g.add(Node("parent","parent",status=NodeStatus.PARTIAL,children=["child"],retryable=False)); assert not g.children_all_done(p)
def test_resolved_dependency_allows_dispatch():
    g=NodeGraph(); g.add(Node("done","done",status=NodeStatus.RESOLVED)); n=g.add(Node("next","next",deps=["done"])); assert n in g.ready()
