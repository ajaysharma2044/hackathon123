"""
Autonomous grounding agent (docs/grounding.md). Goes to the web ITSELF (pure urllib, no LLM in the
loop), pulls live values into grounding.NODES, and refreshes ONLY stale nodes -- staleness decided by
freshness.py, the same decay engine the rest of the system uses. It knows its limits: QUOTE nodes
(behind 'contact us') and PRIMARY nodes (a sponsor/buyer 'yes' that exists nowhere online) are not
scrapable, and the agent reports them as such instead of inventing a number.

Run:  PYTHONPATH=. python3 node_scraper.py            # refresh stale nodes, print report
      PYTHONPATH=. python3 node_scraper.py --force    # re-scrape everything now
"""
from __future__ import annotations
import urllib.request, urllib.error, re, socket, sys
from datetime import datetime, date
import freshness, grounding

UA = {"User-Agent": "Mozilla/5.0 (hackathon123 grounding-agent)"}
socket.setdefaulttimeout(12)

_CATER = "https://conferenceservices.cornell.edu/catering/catering-services/"
BREAKFAST = _CATER + "classic-catering-breakfast-menu"
BREAKS    = _CATER + "classic-catering-breaks-menu"

# node_key -> how to fetch it live. anchor = keyword to locate; the next "$N.NN" is the value.
# claim = the freshness.py claim_type that governs how fast this value goes stale.
SOURCE_SPECS = {
    "cater_breakfast_hot":  dict(url=BREAKFAST, anchor="Scrambled Eggs",   claim="product_pricing"),
    "cater_breakfast_min":  dict(url=BREAKFAST, anchor="Hard-boiled Eggs", claim="product_pricing"),
    "cater_beverage_break": dict(url=BREAKS,    anchor="BEVERAGE BREAK",   claim="product_pricing"),
    "cater_snack_addon":    dict(url=BREAKS,    anchor="choose two",       claim="product_pricing"),
}

def _fetch(url: str) -> str:
    """GET a page and strip it to plain text. Raises on any network/HTTP error (caller handles)."""
    html = urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read().decode("utf-8", "ignore")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))

def _price_after(txt: str, anchor: str):
    """The first $N.NN within 60 chars after `anchor`, or None if the anchor/price isn't found."""
    m = re.search(re.escape(anchor) + r".{0,60}?\$\s?(\d+\.\d{2})", txt, re.I)
    return float(m.group(1)) if m else None

def scrape_node(key: str, spec: dict, cache: dict, fetch=_fetch) -> dict:
    """Fetch + extract one node. Returns a provenance dict; never raises (failures are reported, not fatal)."""
    try:
        txt = cache.get(spec["url"]) or cache.setdefault(spec["url"], fetch(spec["url"]))
    except Exception as e:                                  # noqa: BLE001 -- report any fetch failure
        return dict(value=None, status="FETCH_FAILED", note=type(e).__name__, url=spec["url"])
    v = _price_after(txt, spec["anchor"])
    if v is None:
        return dict(value=None, status="ANCHOR_MISS", note=f"anchor {spec['anchor']!r} not found", url=spec["url"])
    return dict(value=v, status="SCRAPED", url=spec["url"], observed_at=str(date.today()), claim=spec["claim"])

def _is_stale(node: dict, claim: str, now: datetime) -> bool:
    """Reuse freshness.py: stale if never observed, or past its validity window for this claim type."""
    oa = node.get("as_of") if node else None
    if not oa:
        return True
    try:
        observed = datetime.strptime(oa, "%Y-%m-%d")
    except ValueError:
        return True
    return freshness.freshness(claim, observed, now)["status"] == "STALE"

def refresh(now: datetime = None, force: bool = False, fetch=_fetch) -> dict:
    """The agent loop: scrape every stale spec'd node, write live values back into grounding.NODES,
    and report the QUOTE/PRIMARY nodes it deliberately did NOT try (they aren't on the web)."""
    now = now or datetime.now()
    cache, report = {}, []
    for key, spec in SOURCE_SPECS.items():
        node = grounding.NODES.get(key, {})
        if not force and not _is_stale(node, spec["claim"], now):
            report.append((key, "FRESH_SKIP", node.get("v")))
            continue
        r = scrape_node(key, spec, cache, fetch)
        if r["status"] == "SCRAPED":
            grounding.NODES[key] = dict(v=r["value"], status="SCRAPED",
                                        src=f"live-scraped: {r['url']}", as_of=r["observed_at"])
            report.append((key, "REFRESHED", r["value"]))
        else:
            report.append((key, r["status"], r.get("note")))
    unscrapable = {k: d["status"] for k, d in grounding.NODES.items() if d.get("status") in ("QUOTE", "PRIMARY")}
    return dict(ran_at=str(now), report=report, unscrapable=unscrapable)

def main(argv):
    force = "--force" in argv
    out = refresh(force=force)
    print(f"grounding-agent ran {out['ran_at']}  (force={force})\n")
    for key, status, val in out["report"]:
        print(f"  {status:13} {key:22} {val}")
    print(f"\n  NOT scrapable (agent knows its limits): {len(out['unscrapable'])} nodes")
    for k, s in out["unscrapable"].items():
        print(f"    {s:8} {k}  <- {grounding.NODES[k]['src']}")

if __name__ == "__main__":
    main(sys.argv[1:])
