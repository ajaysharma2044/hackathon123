"""
Reproducible Cornell Event-1 economics, run off grounding.py (real/sourced inputs), NOT assumptions.
Cost is built from Cornell's scraped catering menu + venue rate; the result is expressed as a function
of the ONE node no scraper can resolve — the actual sponsorship raise. Contrast row = the old fly-in.
Run: PYTHONPATH=. python3 cornell_scenario.py
"""
import event_optimizer as eo, grounding as g

def grounded_cornell(n=250):
    FOOD = g.grounded_food_per_builder("lean")     # $54.93 from Cornell's real menu (SCRAPED)
    VENUE_2DAY, OPS = 3000, 12000                  # Appel $500/day real; big halls + ops QUOTE-pending
    eo.A["cost_fixed"] = VENUE_2DAY + OPS
    eo.A["cost_per_builder_base"] = FOOD
    eo.A["cost_per_mentor"] = 150
    d = eo.EventDesign("Cornell", n_builders=n, duration_h=36, travel_funded=False, hotel_premium=False,
                       n_research_sponsors=0, mentor_ratio=0.08, research_minutes=15.0, prize_pool=8000)
    return eo._fixed_non_travel(d), FOOD, VENUE_2DAY, OPS

def main():
    cost, food, venue, ops = grounded_cornell()
    print(f"GROUNDED Cornell all-in cost (n=250, weekend): ${cost:,.0f}")
    print(f"  venue ${venue:,} + ops ${ops:,} + food ${food}/builder x250 + mentors + $8k prize")
    print("  food/catering = SCRAPED-real; venue/ops = QUOTE-pending; sponsorship = PRIMARY (below)\n")
    print("Contribution vs YOUR sponsorship raise (the one node no scraper resolves):")
    for r, note in [(15000,"~1 dev-tool sponsor"),(25000,"2-3 sponsors"),(35000,"quant recruiter + a few"),
                    (50000,"= Cal Hacks TOP, 1/12 the size"),(70000,"strong multi-sponsor + Citadel")]:
        c = r - cost
        print(f"  raise ${r:>7,}  ->  {c:>+9,.0f}   [{'PROFIT' if c>0 else 'loss'}]  {note}")
    print(f"\nBreak-even sponsorship needed: ${cost:,.0f}")

if __name__ == "__main__":
    main()
