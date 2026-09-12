"""`python3 engine/test_score.py` — proves HackathonAdvantage is a kill filter, not a weight."""
from score import QuestionScore, HIGH, MED, LOW, NONE
PASS = FAIL = 0
def check(n, c):
    global PASS, FAIL
    ok = "PASS" if c else "FAIL"; PASS += c; FAIL += (not c); print(f"  {ok}  {n}")

# A flagship question: big decision, blind spot, occurs naturally, observable.
credits = QuestionScore("Do startup credits create retained usage or subsidize temporary activation?",
    economic_decision_size=HIGH, current_uncertainty=HIGH, existing_research_spend=HIGH,
    internal_data_blind_spot=HIGH, hackathon_naturalness=HIGH, behavior_observability=HIGH,
    experimental_feasibility=MED, longitudinal_value=HIGH, repeatability=HIGH, buyer_authority=HIGH)
check("flagship has non-zero opportunity", credits.opportunity > 0)
check("flagship verdict is PURSUE", credits.verdict().startswith("PURSUE"))
check("dimensions stay visible (vector returned)", credits.vector()["internal_data_blind_spot"] == "HIGH")

# The kill case: huge budget + huge decision, but a panel/telemetry answers it (low naturalness).
median_dev = QuestionScore("What does the median developer think of our brand?",
    economic_decision_size=HIGH, current_uncertainty=HIGH, existing_research_spend=HIGH,
    internal_data_blind_spot=LOW, hackathon_naturalness=LOW,   # <-- a survey/panel does this better
    behavior_observability=LOW, experimental_feasibility=LOW,
    longitudinal_value=LOW, repeatability=HIGH, buyer_authority=HIGH)
check("big-budget question with no hackathon advantage is KILLED", median_dev.opportunity == 0.0)
check("kill verdict names the reason", "answerable without a hackathon" in median_dev.verdict())

# Enterprise-procurement question: wrong population; occurs nowhere in a hackathon.
procurement = QuestionScore("Which vendor will enterprise procurement teams standardize on?",
    economic_decision_size=HIGH, current_uncertainty=HIGH, existing_research_spend=HIGH,
    internal_data_blind_spot=MED, hackathon_naturalness=NONE,  # procurement doesn't happen here
    behavior_observability=NONE, experimental_feasibility=NONE,
    longitudinal_value=LOW, repeatability=MED, buyer_authority=HIGH)
check("wrong-population question is KILLED", procurement.opportunity == 0.0)

# Confirm the gate is HackathonAdvantage = min(naturalness, blind_spot), not a weighted average.
half = QuestionScore("q", HIGH, HIGH, HIGH, NONE, HIGH, HIGH, HIGH, HIGH, HIGH, HIGH)  # blind_spot NONE
check("high naturalness but zero blind-spot still killed (min gate)", half.opportunity == 0.0)

if __name__ == "__main__":
    print("\ntest_score"); 
    import sys; print(f"\n{'='*50}\n{PASS} passed, {FAIL} failed"); sys.exit(1 if FAIL else 0)
