"""
Startup <-> fund matching + investor discovery (docs/venture/startup-matching.md; Parts XXXIII,
XXXVII, XXXVIII, XLVIII).

Decomposed thesis match — never a "founder quality" score (Part XXXIII). Discovery covers ALL opt-in
projects meeting the query, not only winners (Part XXXVII). Only INVESTOR-opted ventures are
retrievable (Part XXXIX). Missing data is neutral, never negative.
"""
from __future__ import annotations
import compliance

MATCH_DIMS = ["stage_fit", "sector_fit", "check_size_fit", "geography_fit", "thesis_fit",
              "technical_domain_fit", "continuation_evidence"]


def _eq_fit(a, b):
    if not a or not b:
        return None                      # unknown, not zero
    return 3 if str(a).lower() == str(b).lower() else 0


def match(venture, fund) -> dict:
    """Decomposed venture<->fund match + explanation. No founder score."""
    attr = venture.attributes
    why, unknowns = [], []

    stage_fit = _eq_fit(attr.get("STAGE"), fund.stage)
    sector = attr.get("SECTOR")
    sector_fit = (3 if sector and sector.lower() in [s.lower() for s in fund.sectors] else
                  (0 if sector else None))
    geo_fit = _eq_fit(attr.get("GEOGRAPHY"), fund.geography)
    tech = attr.get("TECHNICAL_DOMAIN")
    tech_fit = (3 if tech and fund.thesis and tech.lower() in fund.thesis.lower() else
                (1 if tech else None))
    thesis_fit = (2 if tech and fund.thesis and tech.lower() in fund.thesis.lower() else None)
    check_fit = None if not attr.get("CAPITAL_NEED") else 2  # coarse; refine with real check sizes

    cont_map = {"CONTINUED": 3, "STARTUP_FORMED": 3, "PIVOTED": 2, "STOPPED": 0, "UNKNOWN": None}
    cont = cont_map.get(venture.continuation_status, None)

    if sector_fit == 3: why.append(f"sector '{sector}' in fund sectors")
    if stage_fit == 3: why.append(f"stage '{attr.get('STAGE')}' matches fund stage")
    if tech_fit == 3: why.append(f"technical domain '{tech}' matches fund thesis")
    if cont == 3: why.append(f"still building at follow-up ({venture.continuation_status})")
    for k, v in [("STAGE", stage_fit), ("SECTOR", sector_fit), ("GEOGRAPHY", geo_fit)]:
        if v is None: unknowns.append(f"{k.lower()} not provided")

    return {"venture_id": venture.venture_id, "fund_id": fund.fund_id,
            "stage_fit": stage_fit, "sector_fit": sector_fit, "check_size_fit": check_fit,
            "geography_fit": geo_fit, "thesis_fit": thesis_fit, "technical_domain_fit": tech_fit,
            "continuation_evidence": cont, "why": why, "unknowns": unknowns}
            # no founder_score / overall_score, by design


def discover(fund, ventures) -> list:
    """Investor discovery: all INVESTOR-opted ventures, matched — winners and non-winners alike."""
    return [match(v, fund) for v in ventures if v.investor_visible]


def explain(m: dict) -> str:
    lines = [f"Potentially relevant introduction: venture {m['venture_id']} <-> fund {m['fund_id']}"]
    lines += [f"  • {w}" for w in m["why"]] or ["  • (thesis overlap unclear from provided evidence)"]
    if m["unknowns"]:
        lines.append("  Unknown (not held against the team): " + "; ".join(m["unknowns"]))
    lines.append("  This is thesis-based discovery, not an investment recommendation.")
    return "\n".join(lines)
