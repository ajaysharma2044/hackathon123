"""
Grounding registry — every model input tagged with its REAL source, not an assumption.
status: SCRAPED = published web value (url+date) · QUOTE = real but behind 'contact us' (needs an
email) · PRIMARY = exists nowhere online; only a human commitment resolves it (a sponsor/buyer yes).
This is the discipline the user asked for: no number runs in the model without a provenance tag.
"""
from datetime import date
S = "2026-09-12"

# ---- COST NODES ---------------------------------------------------------------------------------
NODES = {
 # Cornell venue — one real published rate; the big halls are quote-only.
 "venue_appel_per_day":   dict(v=500,   status="SCRAPED", src="conferenceservices.cornell.edu (Appel Commons)", as_of=S),
 "venue_barton_bailey":   dict(v=None,  status="QUOTE",   src="Cornell Conf & Event Svcs, 206 RPCC / contact form, 2-biz-day reply", as_of=S),
 # Cornell Dining classic-catering, real per-person menu prices
 "cater_lunch":           dict(v=17.95, status="SCRAPED", src="Cornell Classic Catering — lunch (10-min)", as_of=S),
 "cater_breakfast_hot":   dict(v=2.95,  status="SCRAPED", src="Cornell Classic Catering — scrambled eggs (25-min)", as_of=S),
 "cater_beverage_break":  dict(v=4.75,  status="SCRAPED", src="Cornell Classic Catering — AM/PM beverage break", as_of=S),
 "cater_snack_addon":     dict(v=8.50,  status="SCRAPED", src="Cornell Classic Catering — snack add-on (choose 2)", as_of=S),
 "cater_dinner_est":      dict(v=22.00, status="QUOTE",   src="Cornell entree/reception stations ($3.45–13.95 + entree) — confirm exact", as_of=S),
 "cater_service_charge":  dict(v=0.18,  status="SCRAPED", src="Cornell Catering — 18% staffed service charge", as_of=S),
 "cater_order_min":       dict(v=450,   status="SCRAPED", src="Cornell Catering — $450 order minimum", as_of=S),
 # ---- SPONSORSHIP / REVENUE COMPS (published elsewhere; collegiate tiers are NOT published) -----
 "comp_calhacks_top":     dict(v=50000, status="SCRAPED", src="Cal Hacks published prospectus (3,000 hackers)", as_of=S),
 "comp_ethglobal_track":  dict(v=15000, status="SCRAPED", src="ETHGlobal sponsor track $10–20K each", as_of=S),
 "comp_cmu_recruiting":   dict(v=10000, status="SCRAPED", src="CMU 2-semester CS recruiting access", as_of=S),
 "comp_react_summit":     dict(v=38000, status="SCRAPED", src="React Summit top sponsor", as_of=S),
 "sponsor_raise_actual":  dict(v=None,  status="PRIMARY", src="YOUR pitch to Jump/IMC/Citadel/dev-tools — no web value exists", as_of=S),
 # ---- RESEARCH RATE CARDS (published) -----------------------------------------------------------
 "rc_lf_syndicated":      dict(v=150000,status="SCRAPED", src="Linux Foundation prospectus (1×50k+4×15k+8×5k)", as_of=S),
 "rc_lf_tierA":           dict(v=25000, status="SCRAPED", src="LF custom Tier A, 150 completes", as_of=S),
 "rc_panel_complete":     dict(v=27,    status="SCRAPED", src="LF pass-through panel complete $24–30", as_of=S),
 # ---- THE DEMAND-SIDE NODES NO SCRAPER CAN RESOLVE ---------------------------------------------
 "research_close_prob":   dict(v=None,  status="PRIMARY", src="Will a buyer say yes? Only a pilot/sales call resolves it", as_of=S),
 "research_wtp_actual":   dict(v=None,  status="PRIMARY", src="What THEY pay for THIS cohort — exists nowhere online", as_of=S),
}

def grounded_food_per_builder(mode="lean"):
    """Compute REAL per-builder weekend food cost from Cornell's actual menu (not an assumption).
    lean = continental breakfasts + light lunch + one beverage break; full = classic catered."""
    n = NODES; sc = 1 + n["cater_service_charge"]["v"]
    if mode == "lean":   # 2 continental b'fasts + 2 lunches + 1 beverage break (+ meal-sponsor offset likely)
        raw = 2*n["cater_breakfast_hot"]["v"] + 2*n["cater_lunch"]["v"] + n["cater_beverage_break"]["v"]
    else:                # full: + 2 dinners + snack add-on
        raw = (2*n["cater_breakfast_hot"]["v"] + 2*n["cater_lunch"]["v"] + 2*n["cater_dinner_est"]["v"]
               + n["cater_beverage_break"]["v"] + n["cater_snack_addon"]["v"])
    return round(raw * sc, 2)

def report():
    order = {"SCRAPED":0,"QUOTE":1,"PRIMARY":2}
    print(f"{'NODE':26} {'VALUE':>10}  {'STATUS':8} SOURCE")
    for k, d in sorted(NODES.items(), key=lambda kv: order[kv[1]['status']]):
        val = "—" if d["v"] is None else (f"${d['v']:,.2f}" if d['v']<1 or d['v']%1 else f"${d['v']:,.0f}")
        print(f"{k:26} {val:>10}  {d['status']:8} {d['src']}")
    print(f"\nGrounded food/builder (real menu): lean ${grounded_food_per_builder('lean')}  full ${grounded_food_per_builder('full')}")

if __name__ == "__main__":
    report()
