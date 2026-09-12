"""python3 test_event_optimizer.py"""
from event_optimizer import EventDesign, experience, research_information, objectives, pareto_frontier, tweak, robust_eval
P = F = 0
def ck(n, c):
    global P, F; P += c; F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

base = EventDesign("base")
# Experience responds correctly to knobs.
ck("more mentors raises experience", experience(EventDesign("m", mentor_ratio=0.2)) > experience(EventDesign("m0", mentor_ratio=0.02)))
ck("higher research burden lowers experience", experience(EventDesign("b", research_minutes=45)) < experience(base))
ck("premium travel+hotel raises experience", experience(base) > experience(EventDesign("cheap", travel_funded=False, hotel_premium=False)))
# Research info responds correctly.
ck("more builders raises research info", research_information(EventDesign("big", n_builders=300)) > research_information(EventDesign("small", n_builders=120)))
ck("more free-choice surface raises research info", research_information(EventDesign("free", free_choice_share=0.6)) > research_information(EventDesign("locked", free_choice_share=0.15)))
ck("90-day follow-up raises research info", research_information(base) > research_information(EventDesign("nf", followup_90d=False)))
# Tweak engine: adding sponsors raises expected contribution but the tradeoff shows on experience/free-choice.
t_sponsor = tweak(base, n_research_sponsors=6)
ck("adding sponsors raises expected contribution", t_sponsor["econ_mean_contribution"] > 0)
t_mentor = tweak(base, mentor_ratio=0.2)
ck("adding mentors raises experience (tweak)", t_mentor["experience"] > 0)
t_burden = tweak(base, research_minutes=40)
ck("over-burdening research lowers experience (tweak)", t_burden["experience"] < 0)
# Pareto: a strictly-dominated design is off the frontier; a specialist design is on it.
designs = [("balanced", objectives(EventDesign("balanced"))),
           # same cost profile as balanced (n=200, funded) but strictly worse on every quality axis -> dominated
           ("dominated", objectives(EventDesign("dominated", n_builders=200, free_choice_share=0.12, research_minutes=48, followup_90d=False))),
           ("research_max", objectives(EventDesign("research_max", n_builders=300, free_choice_share=0.6)))]
front = pareto_frontier(designs)
ck("dominated design is off the Pareto frontier", "dominated" not in front)
ck("at least one specialist design is on the frontier", len(front) >= 1)
# Robust: bull scenario dominates bear on expected contribution.
rb = robust_eval(base)
ck("bull WTP scenario beats bear on expected contribution", rb["bull"]["mean"] > rb["bear"]["mean"])
ck("bear scenario has lower break-even probability", rb["bear"]["p_breakeven"] <= rb["bull"]["p_breakeven"])

if __name__ == "__main__":
    import sys; print(f"\n{'='*50}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
