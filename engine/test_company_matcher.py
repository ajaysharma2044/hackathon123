"""python3 test_company_matcher.py"""
from company_matcher import CompanySituation, match, Offer, NoFit
P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# A strong ACTIVATION/RESEARCH fit: dev-facing, blind spot, adoption intent, credits program.
stripe = CompanySituation(
    company="Stripe", industry="payments", business_unit="Growth / Startup Program",
    problem="why developers test us but never reach production",
    evidence="publishes 20% of Atlas startups charged in 30d, nothing on the other 80%",
    trigger="startup program expansion", decision_owner="Head of Startup Program",
    budget_owner_candidates=["Growth", "Startup Programs", "Product"],
    current_solution="own telemetry (sees only their users)", why_insufficient="cannot see the sandbox->prod abandonment mechanism",
    economic_consequence="activation drives revenue across thousands of startups",
    developer_facing="HIGH", blind_spot="HIGH", hackathon_naturalness="HIGH", decision_value="HIGH",
    budget_signal="HIGH", wants_adoption="HIGH", problem_uncertainty=0.4, parallelizable=0.5,
    prototypeable=0.8, evaluable=0.6, needs_deep_domain=0.2, participant_fit="HIGH")
o = match(stripe)
ck("Stripe-like situation produces an Offer (not NoFit)", isinstance(o, Offer))
ck("Offer routes to a differentiated engine", o.engine in ("RESEARCH", "ACTIVATION", "PRODUCT_DEV", "R&D"))
ck("Offer carries a rational price ceiling, labeled not-WTP", "NOT observed WTP" in o.pricing_evidence)
ck("Offer states what remains UNKNOWN", "UNKNOWN" in o.still_to_learn)

# A genuine NO_FIT: not developer-facing, no blind spot, low uncertainty, weak participant fit.
bank = CompanySituation(
    company="Regional Bank", industry="retail banking", business_unit="Branch Ops",
    problem="which teller-scheduling policy reduces wait times",
    evidence="internal ops review", trigger="cost program", decision_owner="COO",
    budget_owner_candidates=["Operations"], current_solution="ops consultants + their own data",
    why_insufficient="they already measure this well internally", economic_consequence="modest opex",
    developer_facing="NONE", blind_spot="LOW", hackathon_naturalness="NONE", decision_value="LOW",
    budget_signal="LOW", wants_adoption="NONE", problem_uncertainty=0.2, parallelizable=0.2,
    prototypeable=0.2, evaluable=0.5, needs_deep_domain=0.6, participant_fit="LOW")
nf = match(bank)
ck("non-fit company returns NoFit", isinstance(nf, NoFit))
ck("NoFit explains why (answerable elsewhere / weak fit)", len(nf.reason) > 20)

# An R&D-inferior case: high budget but LOW uncertainty -> R&D engine must NOT be selected.
lowunc = CompanySituation(
    company="DeepCorp", industry="deeptech", business_unit="R&D", problem="tune a known algorithm's constant",
    evidence="internal", trigger="none", decision_owner="VP Eng", budget_owner_candidates=["R&D"],
    current_solution="internal team", why_insufficient="", economic_consequence="high",
    developer_facing="LOW", blind_spot="LOW", hackathon_naturalness="LOW", decision_value="HIGH",
    budget_signal="HIGH", wants_adoption="NONE", problem_uncertainty=0.15, parallelizable=0.9,
    prototypeable=0.9, evaluable=0.9, needs_deep_domain=0.2, participant_fit="MED")
r = match(lowunc)
ck("low-uncertainty problem is NOT sold as R&D (Boudreau/Lakhani gate)",
   isinstance(r, NoFit) or r.engine != "R&D")

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
