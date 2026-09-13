"""python3 test_grounding.py -- the grounding agent's guardrails (offline; fetch is mocked)."""
from datetime import datetime
import node_scraper as ns, grounding as g
P = F = 0
def ck(n, c):
    global P, F; P += bool(c); F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

SAMPLE = ("BREAKFAST Scrambled Eggs (VG, GF) - $2.95 Hard-boiled Eggs (GF) - $1.20 "
          "AM BEVERAGE BREAK - $4.75/person snacks AM BEVERAGE BREAK - choose two $8.50/person")
def mock_fetch(url): return SAMPLE
def fail_fetch(url): raise ConnectionError("no network")

# 1. extraction
ck("price extracted right after the anchor", ns._price_after(SAMPLE, "Scrambled Eggs") == 2.95)
ck("missing anchor yields None, not a guess", ns._price_after(SAMPLE, "Lobster Thermidor") is None)

# 2. scrape_node succeeds and fails gracefully
r = ns.scrape_node("cater_breakfast_hot", ns.SOURCE_SPECS["cater_breakfast_hot"], {}, fetch=mock_fetch)
ck("scrape_node returns SCRAPED with a value + provenance", r["status"] == "SCRAPED" and r["value"] == 2.95 and "observed_at" in r)
rf = ns.scrape_node("cater_breakfast_hot", ns.SOURCE_SPECS["cater_breakfast_hot"], {}, fetch=fail_fetch)
ck("a fetch failure is REPORTED, never raised", rf["status"] == "FETCH_FAILED" and rf["value"] is None)

# 3. refresh writes live values into the registry and reports them
out = ns.refresh(now=datetime(2026, 9, 12), force=True, fetch=mock_fetch)
ck("refresh REFRESHED the beverage-break node from the mock page", g.NODES["cater_beverage_break"]["v"] == 4.75)
ck("refreshed node is tagged SCRAPED with a live-scraped source", g.NODES["cater_beverage_break"]["status"] == "SCRAPED" and "live-scraped" in g.NODES["cater_beverage_break"]["src"])

# 4. the agent knows its limits: PRIMARY/QUOTE nodes are reported unscrapable, never invented
ck("PRIMARY demand-side node is reported as unscrapable", out["unscrapable"].get("research_wtp_actual") == "PRIMARY")
ck("QUOTE venue node is reported as unscrapable", out["unscrapable"].get("venue_barton_bailey") == "QUOTE")
ck("the agent NEVER assigned a value to an unscrapable node", g.NODES["research_wtp_actual"]["v"] is None)

# 5. freshness gate: a today-dated node is FRESH and skipped without --force
g.NODES["cater_snack_addon"] = dict(v=8.50, status="SCRAPED", src="x", as_of="2026-09-12")
skip = ns.refresh(now=datetime(2026, 9, 13), force=False, fetch=mock_fetch)
ck("fresh node is SKIPPED (freshness.py gate), not needlessly re-scraped",
   ("cater_snack_addon", "FRESH_SKIP", 8.5) in skip["report"])
g.NODES["cater_snack_addon"] = dict(v=8.50, status="SCRAPED", src="x", as_of="2020-01-01")
old = ns.refresh(now=datetime(2026, 9, 13), force=False, fetch=mock_fetch)
ck("a STALE node IS re-scraped by the freshness gate",
   ("cater_snack_addon", "REFRESHED", 8.5) in old["report"])

# 6. grounded food cost still computes from the (live) values
ck("grounded food/builder computes from scraped values", g.grounded_food_per_builder("lean") > 0)

if __name__ == "__main__":
    import sys; print(f"\n{'='*46}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
