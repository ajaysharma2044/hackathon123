"""Resolver registry. Entity discovery is exclusively source-backed (dynamic_agents)."""
from agent_os import Permission, RequestAction
REGISTRY = {}
def agent(name, permission=Permission.AUTONOMOUS_READ):
    def register(fn):
        REGISTRY[name] = (fn,permission)
        return fn
    return register

def get(name):return REGISTRY.get(name)

@agent('outreach',Permission.NEEDS_APPROVAL)
def outreach(node,graph,ctx):
    return RequestAction('Contact a prospective buyer',{'question':node.question})
