"""
First-ever grounded engine run (audit Section 7, steps 2-4). Runs the post-fix engine on the REAL
Round-1 comparable-events data via grounded_inputs.py and prints four internal steering results:

  1. Headline: economic() on the ASSUMED contract band vs the comparable-grounded band.
  2. VOI: EVSI of the next block of buyer interviews (what AJ's next calls are worth).
  3. Break-even raise as a function of sponsor close rate, on grounded costs.
  4. Band sensitivity: which uncertain input moves the headline most.

EVERY dollar here is an INTERNAL, ASSUMED-scenario steering number -- never pitch material. The close
rate and WTP are demand-side UNKNOWNs (grounding.py PRIMARY); only real buyer interviews
(research/observations.json -> beliefs.update_beta) can move them out of ASSUMED. Run: python3 grounded_run.py
"""
from __future__ import annotations
import numpy as np
import grounded_inputs as gi
from event_optimizer import EventDesign, economic
from voi import evsi_beta

ASSUMED_CONTRACT = (40000, 75000, 150000)     # the engine's original invented band (docs/quant-assumptions.md)
ASSUMED_CLOSE = (0.10, 0.25, 0.45)            # close rate stays ASSUMED -- no demand-side evidence exists


def _row(mc):
    s = mc.summary()
    return dict(mean=s["mean"], p5=s["p5"], p95=s["p95"], p_be=mc.prob_gt(0), cvar95=mc.cvar(0.95))


def headline(data):
    print("\n=== 1. HEADLINE: modeled Event-1 contribution (fly-in design, 200 builders) ===")
    print("    contract band ASSUMED $40/75/150K  ->  comparable-grounded $10/35/95K (close band ASSUMED)")
    bear, base, bull, src = gi.contract_band_values(data)
    grounded = (bear, base, bull)
    base_d = EventDesign("event1")
    runs = {"ASSUMED contract": economic(base_d, close_band=ASSUMED_CLOSE, contract_band=ASSUMED_CONTRACT),
            "GROUNDED contract": economic(base_d, close_band=ASSUMED_CLOSE, contract_band=grounded)}
    print(f"    grounded source: {src}")
    print(f"\n    {'scenario':20} {'mean':>12} {'p5':>12} {'p95':>12} {'P(break-even)':>14} {'CVaR95':>12}")
    out = {}
    for name, mc in runs.items():
        r = _row(mc); out[name] = r
        print(f"    {name:20} {r['mean']:>12,.0f} {r['p5']:>12,.0f} {r['p95']:>12,.0f} "
              f"{r['p_be']:>14.3f} {r['cvar95']:>12,.0f}")
    d = out["GROUNDED contract"]["mean"] - out["ASSUMED contract"]["mean"]
    print(f"    delta (grounded - assumed) mean contribution: {d:>+,.0f}")
    return out


def voi(data):
    print("\n=== 2. VOI: what the next block of buyer interviews is worth (grounded cost + contract) ===")
    N_S = 5                                    # sponsors approached (ASSUMED targeting)
    _, base_contract, _, _ = gi.contract_band_values(data)   # Golden Bear $35K grounded base
    cost = gi.grounded_event_cost()            # ~$39,732 grounded Cornell-scale
    close = gi.close_prior_belief()            # ASSUMED Beta(2,6) ~25%; no demand evidence yet
    a, b = float(close.dist.args[0]), float(close.dist.args[1])
    actions = ["GO", "NOGO"]
    def util(action, theta):
        theta = np.asarray(theta, float)
        return (N_S * theta * base_contract - cost) if action == "GO" else np.zeros_like(theta)
    print(f"    decision: GO = run event (revenue = {N_S} sponsors x close-rate x ${base_contract:,} "
          f"- ${cost:,.0f} grounded cost) vs NO-GO=0")
    print(f"    close-rate prior: Beta({a:.0f},{b:.0f}) mean {a/(a+b):.3f}, status {close.status} (no demand evidence)")
    out = {}
    print(f"\n    {'m interviews':>14} {'EVSI ($)':>14}")
    for m in (5, 10, 20):
        ev = evsi_beta(a, b, m, actions, util)
        out[m] = ev
        print(f"    {m:>14} {ev:>14,.0f}")
    return out


def breakeven(data):
    print("\n=== 3. Break-even raise as a function of sponsor close rate (grounded costs) ===")
    N_S = 5
    _, base_contract, _, _ = gi.contract_band_values(data)
    cost = gi.grounded_event_cost()
    print(f"    (5 sponsors approached at ${base_contract:,} grounded base; ${cost:,.0f} grounded cost)")
    print(f"\n    {'close_rate':>10} {'exp_sponsor_rev':>16} {'contribution':>14} {'raise_to_break_even':>20}")
    out = {}
    for theta in (0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.70):
        rev = N_S * theta * base_contract
        contrib = rev - cost
        need = max(0.0, -contrib)
        out[theta] = need
        print(f"    {theta:>10.2f} {rev:>16,.0f} {contrib:>+14,.0f} {need:>20,.0f}")
    return out


def sensitivity(data):
    print("\n=== 4. Band sensitivity: which uncertain input moves the headline mean most ===")
    bear, base, bull, _ = gi.contract_band_values(data)
    d = EventDesign("event1")
    def mean_of(close_band, contract_band):
        return economic(d, close_band=close_band, contract_band=contract_band).summary()["mean"]
    grounded = (bear, base, bull)
    # one-at-a-time: hold the other band at its grounded/assumed base point, swing this one bear->bull
    contract_lo = mean_of(ASSUMED_CLOSE, (bear, bear, bear))
    contract_hi = mean_of(ASSUMED_CLOSE, (bull, bull, bull))
    close_lo = mean_of((ASSUMED_CLOSE[0],) * 3, grounded)
    close_hi = mean_of((ASSUMED_CLOSE[2],) * 3, grounded)
    swings = {"contract band ($10K..$95K)": abs(contract_hi - contract_lo),
              "close band (0.10..0.45)": abs(close_hi - close_lo)}
    print(f"    {'input band':32} {'mean@low':>12} {'mean@high':>12} {'|swing|':>12}")
    print(f"    {'contract band ($10K->$95K)':32} {contract_lo:>12,.0f} {contract_hi:>12,.0f} "
          f"{abs(contract_hi-contract_lo):>12,.0f}")
    print(f"    {'close band (0.10->0.45)':32} {close_lo:>12,.0f} {close_hi:>12,.0f} "
          f"{abs(close_hi-close_lo):>12,.0f}")
    top = max(swings, key=swings.get)
    print(f"    -> largest lever: {top}  (chase this in Round 3)")
    return swings


def main():
    print("=" * 92)
    print("HACKATHON123 GROUNDED ENGINE RUN -- INTERNAL ASSUMED-SCENARIO STEERING NUMBERS, NOT PITCH MATERIAL")
    print("Round-1 comparable-events only (Round-2 absent). Close rate / WTP remain demand-side UNKNOWNs.")
    print("=" * 92)
    data = gi.load_comparable_events()
    gi.build_all(data)   # asserts every grounded belief is ASSUMED (no OBSERVED laundering)
    headline(data); voi(data); breakeven(data); sensitivity(data)
    print("\n" + "=" * 92)
    print("Reminder: these are steering numbers on ASSUMED bands. Sourced pitch comps live in the vault")
    print("sponsor-pitch-benchmark-brief, not here.")


if __name__ == "__main__":
    main()
