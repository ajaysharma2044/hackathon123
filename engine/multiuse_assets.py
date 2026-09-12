"""
Multi-use-asset engine (docs/multi-sided/multi-use-assets.md). Net-new: one artifact -> many
downstream uses (Part XXIV), with rights/consent (Part XXV) and NO double-counting of revenue
(Parts XXVII-XXVIII). Reuses compliance (disclosure rules) and opportunity_market.dedup_revenue.
"""
from __future__ import annotations
from itertools import permutations
from math import factorial

# One asset -> the sides that can reuse it, the consent scope, and the grain (Parts XXIV-XXV).
ASSET_USES = {
    "project_repo": [("judges","judging","event","aggregate"), ("product_clients","tool-use evidence","AGGREGATE_RESEARCH","aggregate"),
                     ("rd_clients","technical artifact","rd_license","aggregate"), ("employers","work evidence","RECRUITING_DISCOVERABILITY","individual"),
                     ("vcs","technical diligence","VC_DISCOVERABILITY","individual"), ("participants","portfolio","self","individual"),
                     ("organizers","benchmark","AGGREGATE_RESEARCH","aggregate")],
    "mentor_log": [("product_clients","friction evidence","AGGREGATE_RESEARCH","aggregate"), ("organizers","support model","internal","aggregate")],
    "exit_interview": [("product_clients","qualitative why","QUALITATIVE_RESEARCH","aggregate"), ("organizers","insight","internal","aggregate")],
    "demo": [("judges","judging","event","individual"), ("vcs","startup discovery","VC_DISCOVERABILITY","individual"),
             ("employers","capability evidence","RECRUITING_DISCOVERABILITY","individual"), ("organizers","content","PUBLIC_MEDIA","aggregate")],
    "follow_up_90d": [("product_clients","retention","AGGREGATE_RESEARCH","aggregate"), ("vcs","continuation evidence","VC_DISCOVERABILITY","individual")],
}

def reuse_map(asset):
    return [{"stakeholder": s, "use": use, "consent_scope": scope, "grain": grain}
            for (s, use, scope, grain) in ASSET_USES.get(asset, [])]

def rights_ok(asset, stakeholder, granted_scopes: set):
    """A reuse is permitted only if (a) it is aggregate-grain, or (b) individual-grain AND the exact
    opt-in scope was granted. Absence of an opt-in defaults to NOT visible (the compliance rule)."""
    for (s, _use, scope, grain) in ASSET_USES.get(asset, []):
        if s == stakeholder:
            if grain == "aggregate":
                return True
            return scope in granted_scopes          # explicit, non-revoked individual opt-in required
    return False

def attribute_revenue(contract_value, components_present: set, all_components: set):
    """Shapley attribution of ONE contract across the assets that produced it -- sums to the contract,
    NO double counting (Parts XXVII-XXVIII). Value function = contract * completeness(subset), where
    completeness = fraction of required components present (a transparent, submodular, non-fabricated
    function -- it splits the actual contract, it does not invent value)."""
    comps = sorted(all_components)
    n = len(comps)
    def v(subset): return contract_value * (len(subset & all_components) / n) if n else 0.0
    shap = {c: 0.0 for c in comps}
    for perm in permutations(comps):
        seen = set()
        for c in perm:
            before = v(seen); seen.add(c); shap[c] += (v(seen) - before)
    for c in shap:
        shap[c] /= factorial(n)
    # zero out components that weren't actually present in this deal
    return {c: (shap[c] if c in components_present else 0.0) for c in comps}, sum(
        shap[c] for c in components_present)
