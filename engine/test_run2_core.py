from economic_graph import EconomicGraph, EvidenceRef
from research_bridge import ResearchBridge, Finding
from commercial_logic import ValueBundle, PriceEvidence, WTPStatus, Mechanic, ThemeGate

P = F = 0
def ck(name, cond):
    global P, F
    P += bool(cond); F += not bool(cond)
    print(("PASS " if cond else "FAIL ") + name)

src = EvidenceRef("https://example.com/a", "A", "PRIMARY_COMPANY", "A supports this")
g = EconomicGraph()
a = g.add_node("Organization", "Acme, Inc.", attrs={"budget":"HIGH"}, evidence=[src])
a2 = g.add_node("Organization", "Acme Inc", attrs={"budget":"HIGH"}, evidence=[src])
ck("duplicate organizations merge safely", a.id == a2.id and len(g.nodes) == 1)

src2 = EvidenceRef("https://example.com/b", "B", "REGULATORY", "B disagrees")
g.add_node("Organization", "Acme Inc", attrs={"budget":"LOW"}, evidence=[src2])
ck("contradictory evidence is preserved", len(g.contradictions) == 1 and g.nodes[a.id].attrs["budget"] == "HIGH")

p1 = g.add_node("Product", "Scheduler A", attrs={"hackathon_relevance":"HIGH"}, evidence=[src])
p2 = g.add_node("Product", "Scheduler B", attrs={"hackathon_relevance":"HIGH"}, evidence=[src])
def exp(n):
    if n.name == "Scheduler A": return [{"kind":"Product","name":"Scheduler B","edge_kind":"DEPENDS_ON","evidence":[src]}]
    if n.name == "Scheduler B": return [{"kind":"Product","name":"Scheduler A","edge_kind":"DEPENDS_ON","evidence":[src]}]
    return []
r = g.expand_products([p1.id], exp, max_depth=10)
ck("cycles do not infinite-loop", r["cycle_skips"] >= 1 and r["expanded"] <= 2)
ck("source provenance survives graph propagation", all(e.evidence for e in g.edges.values()))

low = g.add_node("Product", "Irrelevant", attrs={"hackathon_relevance":"LOW"}, evidence=[src])
r2 = g.expand_products([low.id], lambda n: (_ for _ in ()).throw(Exception("must not expand")))
ck("recursive expansion terminates on stop rule", r2["stops"][low.id] == "LOW_HACKATHON_RELEVANCE")

b = ResearchBridge()
b.ingest(Finding("battle_power", "economic_battle", {"urgency":"HIGH"}, "https://iea.org/x", "IEA", "GOVERNMENT", "demand doubles"))
ck("session-assisted packets remain unvalidated", b.packet("battle_power", "economic_battle")["status"] == "CACHED_UNVALIDATED")
b.ingest(Finding("battle_power", "economic_battle", {"urgency":"MEDIUM"}, "https://ferc.gov/y", "FERC", "GOVERNMENT", "different framing"))
ck("contradictory research is not silently averaged", b.packet("battle_power", "economic_battle")["status"] == "CONTRADICTED")

try:
    PriceEvidence(100000, WTPStatus.UNKNOWN)
    ok = False
except ValueError: ok = True
ck("UNKNOWN cannot silently become numeric", ok)
try:
    PriceEvidence(100000, WTPStatus.OBSERVED, "market_size")
    ok = False
except ValueError: ok = True
ck("Observed WTP remains UNKNOWN without primary evidence", ok)
ck("primary paid pilot can establish observed WTP", PriceEvidence(10000, WTPStatus.OBSERVED, "paid_pilot").amount == 10000)

v = ValueBundle(cash=10000, in_kind_face_value=100000, actual_cost_avoided=4000)
ck("cash is distinct from credits and avoided cost", v.cash == 10000 and v.in_kind_face_value == 100000 and v.actual_cost_avoided == 4000)

m = Mechanic("forced survey", natural_without_payment=False, participant_burden="LOW")
ck("high-paying artificial sponsor mechanic can be rejected", m.admissible()[0] is False)
m2 = Mechanic("biased forced tool", natural_without_payment=True, participant_burden="LOW", research_contamination=True)
ck("research contamination can reject a sponsor mechanic", m2.admissible()[0] is False)

bad_market = ThemeGate(True, True, True, True, substitute_parity=True, anchor_product_exists=True)
ck("substitute parity can kill an opportunity", bad_market.result()[0] is False)
no_anchor = ThemeGate(True, True, True, True, substitute_parity=False, anchor_product_exists=False)
ck("anchor product absence meaningfully weakens a theme", no_anchor.result()[0] is False)
poor_fit = ThemeGate(False, False, False, False, substitute_parity=False, anchor_product_exists=True)
ck("poor hackathon fit kills a giant market", poor_fit.result()[0] is False)

print(f"\n{P} passed, {F} failed")
raise SystemExit(1 if F else 0)
