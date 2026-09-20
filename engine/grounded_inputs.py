"""
Grounded inputs adapter (audit Section 7, step 1): turn the sourced Round-1 comparable-events dataset
(docs/evidence/comparable-events/comparable-events.json) into provenance-tagged beliefs.Belief objects the quant
engine can consume. Nothing else in the repo reads the Round-1 dataset -- this is the data-in seam the
audit flagged as the single biggest gap.

Discipline: every band carries its real source URL + as_of date, and the vault confidence tag maps to
an evidence kind/weight. NOTHING in this dataset is a signed commercial commitment, so every belief
here is ASSUMED -- never OBSERVED. A belief that came out OBSERVED would be a bug in the fix-2 mass
rule; build_all() asserts against it. Trunk-neutral: depends only on beliefs.py + grounding.py.
"""
from __future__ import annotations
import json, os
import beliefs
import grounding as g

# Vault confidence tag -> (evidence kind, reliability weight). None of these can mint OBSERVED.
CONFIDENCE_TO_KIND = {
    "stated":      ("EXTERNAL_COMPARABLE", 0.25),
    "high":        ("EXTERNAL_COMPARABLE", 0.25),
    "medium":      ("EXPERT_PRIOR", 0.20),
    "speculation": ("MODEL_ESTIMATE", 0.10),
}
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_JSON = os.path.join(_HERE, "..", "docs", "comparable-events", "comparable-events.json")


def load_comparable_events(path=None):
    """Load the Round-1 dataset. Defaults to the repo copy; pass a path (e.g. the vault copy) if the
    file is absent on this branch."""
    with open(path or _REPO_JSON) as f:
        return json.load(f)


def belief_from_finding(name, bear, base, bull, source, confidence, as_of, reason=None):
    """The one genuinely new function the data-in path needs: a sourced comparable band -> an ASSUMED
    scenario Belief with real provenance. `confidence` is the vault tag; its evidence kind + weight are
    recorded in the provenance but NEVER promote the belief past ASSUMED (comparable evidence cannot
    mint OBSERVED -- see beliefs.update_beta's mass rule)."""
    kind, weight = CONFIDENCE_TO_KIND.get(confidence, ("MODEL_ESTIMATE", 0.10))
    src = f"{source} | as_of {as_of} | {confidence}->{kind}(w={weight})"
    b = beliefs.scenario(name, bear, base, bull, src, reason or f"comparable band, {kind}")
    assert b.status == beliefs.ASSUMED, f"{name!r} came out {b.status}, expected ASSUMED"
    return b


# ---- field map (audit Section 7) : comparable-events.json -> engine beliefs --------------------
def contract_band_values(data):
    """sponsorship_ladders_usd -> (bear, base, bull, source). Published tiers: Cal Hacks Bronze /
    Golden Bear / Reality Hack top tier (the audit's $10K/$35K/$95K)."""
    ladders = {row["org"]: row for row in data["sponsorship_ladders_usd"]}
    cal, rh = ladders["Cal Hacks 13.0"], ladders["MIT Reality Hack"]
    bear, base = cal["tiers"]["Bronze"], cal["tiers"]["Golden Bear"]          # 10k / 35k
    bull = rh["tiers"]["Maximum Visibility"]                                  # 95k (audit calls it "Impact")
    src = f'{cal["source"]} (Bronze {bear}, Golden Bear {base}); {rh["source"]} (top tier {bull})'
    return bear, base, bull, src


def contract_band_belief(data):
    """The grounded research-sponsor contract band as a provenance-tagged ASSUMED Belief."""
    bear, base, bull, src = contract_band_values(data)
    return belief_from_finding("contract", bear, base, bull, src, "stated", "2026-09-14",
                               "published sponsor ladders; NOT observed WTP")


def close_prior_belief(observations=None):
    """Sponsor close-rate prior. NO comparable resolves demand-side close (grounding.py marks
    research_close_prob PRIMARY -- unscrapable), so it stays an ASSUMED Beta(2,6) ~25% until real
    buyer interviews move it through the observations.json channel (beliefs.update_beta, post fix-2)."""
    return beliefs.update_beta(2, 6, list(observations or []), source="close_prior")


def grounded_event_cost(n_builders=250, venue_2day=3000, ops=12000, mentor_ratio=0.08,
                        mentor_rate=150, prize=8000, food_mode="lean"):
    """Cornell-scale grounded event cost from grounding.py components, WITHOUT mutating
    event_optimizer.A (cornell_scenario does that global mutation; the audit flags it, Section 3b).
    food/builder = SCRAPED Cornell menu; venue_2day/ops = QUOTE-pending estimate (be honest: the $500/day
    Appel rate is SCRAPED but the big-hall + ops uplift is not)."""
    food = g.grounded_food_per_builder(food_mode)
    return float(venue_2day + ops + n_builders * food + n_builders * mentor_ratio * mentor_rate + prize)


def attendance_funnel_belief(data):
    """elite selectivity/applications -> builder acceptance-rate prior (supply-side attendance funnel)."""
    ev = [e for e in data["elite_collegiate_events"] + data["premium_ai_builder_events"]
          if e.get("selectivity_pct") is not None]
    rates = sorted(e["selectivity_pct"] / 100.0 for e in ev)
    src = "; ".join(f'{e["name"]} {e["selectivity_pct"]}%' for e in ev)
    return belief_from_finding("accept_rate", rates[0], rates[len(rates) // 2], rates[-1],
                               src, "high", "2026-09-14", "acceptance rate across elite events")


def value_per_hire_belief(data):
    """recruiting benchmarks -> value-per-hire ceiling (context for rational_price_ceiling; NOT WTP)."""
    r = {x["metric"]: x for x in data["recruiting_and_prize_benchmarks_usd"]}
    base = r["cost_per_hire_tech_median"]["value"]                             # 9000
    return belief_from_finding("value_per_hire", round(base * 0.7), base,
                               r["cost_per_hire_avg_SHRM"]["exec"],            # 35879
                               "SHRM cost-per-hire + tech median (comparable-events.json)", "medium",
                               "2026-09-14", "recruiting cost anchors; ceiling context, not WTP")


def instrumentation_yield_belief(data):
    """qual-methods response rates -> expected-n instrumentation yield (usable survey fraction)."""
    return belief_from_finding("survey_yield", 0.0277, 0.1597, 0.34,
                               "Imam Mahmoud 2022 + Survicate/SurveyMonkey 2025 (comparable-events.json)",
                               "high", "2026-09-14", "cold-email usable -> in-app short -> in-app band")


def retention_belief(data):
    """project survival -> retention prior."""
    s = data["outcomes_and_market_evidence"]["project_survival"]
    return belief_from_finding("retention_5mo", 0.035, 0.05, s["commit_after_event_pct"] / 100.0,
                               f'Nolte et al. 2020 PACM HCI (commit {s["commit_after_event_pct"]}%, '
                               f'5mo {s["active_at_5_months_pct"]}%)', "stated", "2020",
                               "project survival after hackathons")


def build_all(data=None):
    """All grounded beliefs, keyed. Asserts every one is ASSUMED (no comparable can mint OBSERVED)."""
    data = data if data is not None else load_comparable_events()
    out = {"contract": contract_band_belief(data), "close_prior": close_prior_belief(),
           "accept_rate": attendance_funnel_belief(data), "value_per_hire": value_per_hire_belief(data),
           "survey_yield": instrumentation_yield_belief(data), "retention_5mo": retention_belief(data)}
    for name, b in out.items():
        assert b.status == beliefs.ASSUMED, f"{name!r} is {b.status}; comparable data must stay ASSUMED"
    return out
