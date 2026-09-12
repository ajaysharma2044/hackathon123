"""
Structural-gap search (docs/structural-gap-map.md).

For every spending war, ask the message's question: "What CAN'T the buyer currently purchase?"
    They can buy consultants, but not 30 independent technical approaches in 72 hours.
    They can buy developer telemetry, but not the developers who chose a competitor before the funnel.
    They can buy recruiting, but not observation of high-agency people building under pressure.

A gap is REAL only if two things hold, gated exactly like score.py's HackathonAdvantage:
  (1) there is a genuine "cannot buy today" (gap_severity >= floor), AND
  (2) our environment holds a structural advantage at supplying it (hackathon_advantage >= floor).
If either fails, the gap is not ours — an existing substitute already covers it. A large market does
NOT upgrade a gap our environment cannot fill.
"""
from __future__ import annotations
from dataclasses import dataclass, field

NONE, LOW, MED, HIGH = 0, 1, 2, 3
_LABEL = {0: "NONE", 1: "LOW", 2: "MED", 3: "HIGH"}

GAP_ADVANTAGE_FLOOR = MED

# The scarce ASSETS a temporary high-agency organization might uniquely supply (the message's
# candidate list). These are HYPOTHESES about what our scarce asset actually is — not assumed to be
# "elite student access."
CANDIDATE_ASSETS = (
    "INDEPENDENT_PARALLEL_TECHNICAL_SEARCH", "GREENFIELD_DEVELOPER_DECISION_DATA",
    "RAPID_PROTOTYPE_DIVERSITY", "UNBIASED_COMPETITIVE_CHOICE_DATA", "RARE_TECHNICAL_TALENT",
    "DESIGN_PARTNER_FORMATION", "EXTERNAL_RND_EXPLORATION", "FAST_PRODUCT_EXPERIMENTATION",
    "CROSS_DISCIPLINARY_SOLUTION_SEARCH",
)


@dataclass
class StructuralGap:
    code: str
    category: str                   # the spending war it sits inside (SpendCategory.code)
    they_can_buy: str               # the substitute that already exists
    they_cannot_buy: str            # the specific thing that is missing today
    scarce_asset: str = ""          # which CANDIDATE_ASSET this gap is really about
    substitute: str = ""            # the closest existing substitute (CONSULTING / KAGGLE / ...)
    gap_severity: int = NONE        # how unmet is it? (0 = well served already)
    hackathon_advantage: int = NONE # our structural edge at supplying the missing thing
    evidence_url: str = ""
    quote: str = ""
    evidence_strength: str = "HYPOTHETICAL"

    @property
    def is_real_gap(self) -> bool:
        """Real (and ours) only if it is genuinely unmet AND we hold a structural advantage."""
        return self.gap_severity >= GAP_ADVANTAGE_FLOOR and self.hackathon_advantage >= GAP_ADVANTAGE_FLOOR

    def verdict(self) -> str:
        if self.gap_severity < GAP_ADVANTAGE_FLOOR:
            return "NOT_A_GAP — an existing substitute already covers this well"
        if self.hackathon_advantage < GAP_ADVANTAGE_FLOOR:
            return "NOT_OURS — real gap, but our environment holds no structural advantage at filling it"
        return "REAL_GAP — genuinely unmet and structurally suited to our environment"


EVIDENCE_ORDER = ["HYPOTHETICAL", "INFERRED_JOB_POST", "PUBLIC_STATEMENT", "REGULATORY_FILING",
                  "PROGRAM_ANNOUNCEMENT", "BUYER_STATED", "SIGNED_COMMERCIAL"]


def real_gaps(gaps) -> list:
    """Filter to gaps that pass BOTH gates (the ones worth pursuing)."""
    return [g for g in gaps if g.is_real_gap]


def rank_gaps(gaps) -> list:
    """Rank gaps evidence-first, then by (gap_severity, hackathon_advantage). Killed gaps sink."""
    def key(g: StructuralGap):
        return (g.is_real_gap, EVIDENCE_ORDER.index(g.evidence_strength),
                g.gap_severity, g.hackathon_advantage)
    return sorted(gaps, key=key, reverse=True)


def assets_in_play(gaps) -> dict:
    """Which scarce assets recur across the REAL gaps — the honest read on 'what is our scarce asset
    actually?' (the message forbids assuming it is elite student access)."""
    out = {}
    for g in real_gaps(gaps):
        if g.scarce_asset:
            out[g.scarce_asset] = out.get(g.scarce_asset, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: kv[1], reverse=True))
