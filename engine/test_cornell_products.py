"""python3 test_cornell_products.py"""
from audience import CORNELL_SEGMENTS, to_talent_mix, segments_for_talent, unresolved_populations
from cohort_advantage import evaluate as ca_eval, survivors as ca_survivors, rank as ca_rank, NONE, LOW, MED, HIGH
from qualitative import (assert_not_surveillance, PERMITTED_CAPTURE_MODES, CAPTURE_HARD_BOUNDARIES,
                         BEHAVIOR_DEFINITIONS, sampling_plan, InsightNode, traces_to_raw,
                         interpretation_valid, write_claim, LEVELS)
from product_catalog import (KILL_GATES, PRODUCT_UNIVERSE, survivors, killed, rank as prod_rank)

P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

# ---------------- audience ----------------
ck("cornell segments include AI_ML and ORIE_OPTIMIZATION", {"AI_ML", "ORIE_OPTIMIZATION"} <= set(CORNELL_SEGMENTS))
ck("all segment populations default UNKNOWN (no fabricated counts)", len(unresolved_populations()) == len(CORNELL_SEGMENTS))
mix = to_talent_mix({"AI_ML": 20, "ORIE_OPTIMIZATION": 15, "SOFTWARE_FULLSTACK": 40})
ck("talent mix shares sum to ~1", abs(sum(s for _, s in mix) - 1.0) < 5e-3)  # 4-dp rounding tolerance
ck("talent mix contains OR_IE from ORIE segment", any(lbl == "OR_IE" for lbl, _ in mix))
ck("reverse lookup: ORIE supplies OR_IE", "ORIE_OPTIMIZATION" in segments_for_talent("OR_IE"))

# ---------------- cohort_advantage ----------------
strong = ca_eval("greenfield_choice", student_specificity=HIGH, cornell_capability_fit=HIGH,
                 naturalness=HIGH, buyer_blind_spot=HIGH, alternative_difficulty=HIGH)
ck("a strong cohort advantage clears the gate", strong.gate_passed is True)
ck("strong advantage is not a KILL", not strong.verdict().startswith("KILL"))
obtainable = ca_eval("survey", student_specificity=HIGH, cornell_capability_fit=HIGH,
                     naturalness=HIGH, buyer_blind_spot=HIGH, alternative_difficulty=LOW)
ck("obtainable-elsewhere product is KILLED", obtainable.gate_passed is False)
ck("kill verdict names the obtainable-elsewhere reason", "obtainable" in obtainable.verdict().lower())
ck("cohort survivors filters out the killed one", strong in ca_survivors([strong, obtainable]) and obtainable not in ca_survivors([strong, obtainable]))
ck("cohort rank puts the survivor first", ca_rank([obtainable, strong])[0] is strong)

# ---------------- qualitative (capture-not-surveillance + insight chain) ----------------
ck("permitted capture mode passes the guard", assert_not_surveillance("ARTIFACT_DERIVED") is True)
def _raises(fn):
    try: fn(); return False
    except ValueError: return True
ck("covert capture is refused", _raises(lambda: assert_not_surveillance("ARTIFACT_DERIVED", covert=True)))
ck("non-permitted mode is refused", _raises(lambda: assert_not_surveillance("SECRET_SNIFFER")))
ck("hard-boundary capture is refused", _raises(lambda: assert_not_surveillance("SELF_REPORTED", boundary="KEYSTROKE_CAPTURE")))
ck("all 14 behavior kinds are defined", len(BEHAVIOR_DEFINITIONS) == 14)
ck("every behavior definition uses a permitted capture mode", all(b.capture_mode in PERMITTED_CAPTURE_MODES for b in BEHAVIOR_DEFINITIONS.values()))
ck("sampling plan includes non-adopters and abandoners (not just winners)", {"NON_ADOPTER", "ABANDONER"} <= set(sampling_plan()))

quote = InsightNode("q1", "RAW_QUOTE", "auth setup took us two hours")
obs = InsightNode("o1", "OBSERVATION", "5 teams removed Product X before submitting"); obs.add_child(quote)
code = InsightNode("c1", "CODE", "auth/setup friction"); code.add_child(obs)
theme = InsightNode("t1", "THEME", "setup friction"); theme.add_child(code)
patt = InsightNode("p1", "PATTERN", "auth friction precedes abandonment"); patt.add_child(theme)
interp = InsightNode("i1", "INTERPRETATION", "authentication friction", alternatives=["prior familiarity", "docs quality"]); interp.add_child(patt)
rec = InsightNode("r1", "RECOMMENDATION", "test a starter-template simplification"); rec.add_child(interp)
ck("recommendation traces down to a raw quote", traces_to_raw(rec) is True)
ck("child of wrong level is rejected", _raises(lambda: quote.add_child(InsightNode("x", "RECOMMENDATION", "bad"))))
ck("interpretation with alternatives is valid", interpretation_valid(interp) is True)
bad_interp = InsightNode("i2", "INTERPRETATION", "auth causes churn", alternatives=[]); bad_interp.add_child(patt)
ck("interpretation without alternatives is invalid", interpretation_valid(bad_interp) is False)
ck("write_claim hedges (no causal overclaim) when alternatives unresolved", "MAY be" in write_claim(interp))
ck("write_claim refuses an interpretation with no alternatives", _raises(lambda: write_claim(bad_interp)))

class _Alt:
    def __init__(self): self.ruled_out = True
ruled = InsightNode("i3", "INTERPRETATION", "authentication friction", alternatives=[_Alt(), _Alt()]); ruled.add_child(patt)
ck("write_claim strengthens language only when alternatives are ruled out", "appears to drive" in write_claim(ruled))

# ---------------- product_catalog ----------------
ck("there are exactly 10 kill gates", len(KILL_GATES) == 10)
ck("greenfield choice study survives", PRODUCT_UNIVERSE["GREENFIELD_CHOICE_STUDY"].survives is True)
ck("representative market survey is killed (unrepresentative cohort)", PRODUCT_UNIVERSE["REPRESENTATIVE_MARKET_SURVEY"].survives is False)
ck("candidate scoring is killed (person-score boundary)", PRODUCT_UNIVERSE["CANDIDATE_SCORING"].survives is False)
ck("deep confidential domain R&D is killed", PRODUCT_UNIVERSE["DEEP_DOMAIN_RND"].survives is False)
ck("every product WTP is UNKNOWN", all(p.wtp_status == "UNKNOWN" for p in PRODUCT_UNIVERSE.values()))
ck("survivors and killed partition the universe", len(survivors()) + len(killed()) == len(PRODUCT_UNIVERSE))
ck("ranking puts a survivor first", prod_rank()[0].survives is True)

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
