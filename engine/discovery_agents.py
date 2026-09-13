"""Deprecated resolver aliases. Every alias executes research; none consumes answer packets.

Old implementations are preserved in examples/legacy, outside production imports.
"""
from agents import agent
from dynamic_agents import dynamic_discovery, dynamic_entity_research, evidence_only_synthesis

ALIASES = {
    'company_research_live':'company', 'economic_battle_live':'industry', 'rd_product':'rd_opportunity',
    'research_product':'data_opportunity', 'pricing_live':'pricing', 'cost_live':'cost',
    'attendance_live':'attendance', 'capacity_live':'capacity', 'deep_cornell':'cornell',
    'product_stack':'product', 'product_dependency':'product', 'problem':'problem',
}
for name, kind in ALIASES.items():
    def research(node,graph,ctx,kind=kind):
        node.node_type = node.completion_gate = kind
        return dynamic_entity_research(node,graph,ctx)
    agent(name)(research)
for name in ('industry_expansion_live','sponsor_universe_live'):
    agent(name)(dynamic_discovery)
agent('final_synthesis')(evidence_only_synthesis)
