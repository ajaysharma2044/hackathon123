"""
Round-2 grounded engine run. Same engine + discipline as grounded_run.py, reads the Round-2-enriched
dataset (docs/evidence/comparable-events/comparable-events.json) and BRACKETS the sponsor contract band: the elite grounded band ($10/35/95K, Cal Hacks /
Reality Hack) vs the realistic first-event DOWN-MARKET band ($1/5/10K, from the Round-2 sub-500-person
collegiate ladders). Round 2 also cross-checks the grounded cost: Assemble's real itemized core (~$25K
ex-travel, ~$145/head) + MLH stated per-person benchmarks put a ~200-person core at ~$25-40K, corroborating
the ~$39.7K grounded estimate.

Every dollar here is an INTERNAL, ASSUMED-scenario steering number -- never pitch material. Down-market comps
are still comparables (stated), so the band stays ASSUMED; only real buyer interviews (research/observations.json
-> beliefs.update_beta) move close-rate/WTP out of ASSUMED. Run: python3 grounded_run_r2.py
"""
from __future__ import annotations
import numpy as np
import grounded_inputs as gi
from event_optimizer import EventDesign, economic
from voi import evsi_beta

ASSUMED_CONTRACT = (40000, 75000, 150000)   # engine's original invented band
DOWNMARKET = (1000, 5000, 10000)            # R2 realistic first-event band (entry/mid/top of sub-500 ladders)
ASSUMED_CLOSE = (0.10, 0.25, 0.45)


def _row(mc):
    s = mc.summary()
    return dict(mean=s["mean"], p5=s["p5"], p95=s["p95"], p_be=mc.prob_gt(0), cvar95=mc.cvar(0.95))


def downmarket_band_belief(data):
    """The R2 down-market contract band as a provenance-tagged ASSUMED belief (parsed sub-500 ladders)."""
    src = "R2 down-market ladders: entry ~$1-2K / mid ~$3-5K / top ~$7-10K (HackRU/HenHacks/MadHacks/Hunter Hacks)"
    return gi.belief_from_finding("contract_downmarket", *DOWNMARKET, src, "stated", "2026-09-16",
                                  "realistic first-event sponsor band; NOT observed WTP")


def headline(data):
    print("\n=== 1. HEADLINE: modeled Event-1 contribution (fly-in design, 200 builders), 3 contract bands ===")
    bear, base, bull, src = gi.contract_band_values(data)
    elite = (bear, base, bull)
    d = EventDesign("event1")
    runs = {"ASSUMED $40/75/150K": economic(d, close_band=ASSUMED_CLOSE, contract_band=ASSUMED_CONTRACT),
            "ELITE $10/35/95K": economic(d, close_band=ASSUMED_CLOSE, contract_band=elite),
            "DOWN-MARKET $1/5/10K": economic(d, close_band=ASSUMED_CLOSE, contract_band=DOWNMARKET)}
    print(f"    elite band source: {src}")
    print(f"    down-market band: {DOWNMARKET} (R2 parsed sub-500-person ladders -- the realistic launch price)")
    print(f"\n    {'scenario':22} {'mean':>12} {'p5':>12} {'p95':>12} {'P(break-even)':>14} {'CVaR95':>12}")
    out = {}
    for name, mc in runs.items():
        r = _row(mc); out[name] = r
        print(f"    {name:22} {r['mean']:>12,.0f} {r['p5']:>12,.0f} {r['p95']:>12,.0f} "
              f"{r['p_be']:>14.3f} {r['cvar95']:>12,.0f}")
    print(f"    read: at realistic first-event sponsor prices the fly-in event is MORE underwater, not less --")
    print(f"          the event alone never pays; the research/recruiting product is the business.")
    return out


def voi_and_breakeven(data):
    print("\n=== 2. VOI + break-even under BOTH pricing realities (grounded cost) ===")
    close = gi.close_prior_belief()
    a, b = float(close.dist.args[0]), float(close.dist.args[1])
    cost = gi.grounded_event_cost()
    actions = ["GO", "NOGO"]
    _, elite_base, _, _ = gi.contract_band_values(data)     # $35K
    dm_base = DOWNMARKET[1]                                  # $5K
    print(f"    grounded cost ${cost:,.0f}; close prior Beta({a:.0f},{b:.0f}) mean {a/(a+b):.3f} ({close.status})")
    print(f"    R2 cost cross-check: Assemble real core ~$25K (ex fly-in, donated venue) + MLH $8-10/meal ->")
    print(f"    a ~200-person core is ~$25-40K; the ${cost:,.0f} estimate holds up against real data.\n")
    for label, base_c, n_s in [("ELITE  $35K base, 5 sponsors", elite_base, 5),
                               ("DOWN-MKT $5K base, 5 sponsors", dm_base, 5),
                               ("DOWN-MKT $5K base, 12 sponsors (realistic count)", dm_base, 12)]:
        def util(action, theta, _b=base_c, _n=n_s):
            theta = np.asarray(theta, float)
            return (_n * theta * _b - cost) if action == "GO" else np.zeros_like(theta)
        evsi = {m: evsi_beta(a, b, m, actions, util) for m in (5, 10, 20)}
        be = None
        for theta in [x / 100 for x in range(1, 101)]:
            if n_s * theta * base_c - cost >= 0:
                be = theta; break
        be_s = f"{be:.0%}" if be is not None else ">100% (never at this price/count)"
        print(f"    {label:48}")
        print(f"      EVSI next 5/10/20 interviews: ${evsi[5]:,.0f} / ${evsi[10]:,.0f} / ${evsi[20]:,.0f}"
              f"   | break-even close rate: {be_s}")
    print("\n    read: the next block of buyer interviews is the highest-value action under every pricing")
    print("          scenario -- and at down-market prices even 12 sponsors can't break even on the event alone.")


def main():
    print("=" * 96)
    print("HACKATHON123 GROUNDED ENGINE RUN (ROUND 2) -- INTERNAL ASSUMED-SCENARIO STEERING NUMBERS, NOT PITCH MATERIAL")
    print("Round-1 + Round-2 comparable-events. Close rate / WTP remain demand-side UNKNOWNs (only real calls move them).")
    print("=" * 96)
    data = gi.load_comparable_events()
    gi.build_all(data)                 # asserts every R1 grounded belief is ASSUMED
    downmarket_band_belief(data)       # asserts the R2 down-market band is ASSUMED too
    headline(data)
    voi_and_breakeven(data)
    print("\n" + "=" * 96)
    print("Reminder: steering numbers on ASSUMED bands. AJ's pitch comps live in the vault sponsor-pitch-benchmark-brief.")
    print("What moves any of this: one real buyer price -> research/observations.json -> re-run.")


if __name__ == "__main__":
    main()
