"""
Economic arms-race / spending-intensity engine (docs/economic-arms-races.md,
docs/spending-intensity-map.md).

Do not look for companies that "could benefit." Look for markets where organizations are ALREADY
SPENDING AGGRESSIVELY to win an economically important outcome — a spending war — and then find the
critical gap inside that war our environment can fill. "Spend first, company second."

Same disciplines as the rest of the engine:
- Money magnitudes (current annual spend, cost of failure, value of winning) are beliefs.Belief,
  default UNKNOWN. A category is not disqualified for having UNKNOWN spend — it is flagged as needing
  the evidence sweep — but it also cannot be RANKED above an evidenced one on spend it cannot show.
- The intensity dimensions are ordinal 0..3 and kept decomposed; ranking never hides a weak dimension
  inside a composite (the message's explicit rule).
- A desperation SIGNAL (high comp, rapid hiring, big vendor contracts) is not an opportunity by
  itself; it must be connected to a specific unresolved structural gap (see gap_finder.py).
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from beliefs import Belief, unknown

NONE, LOW, MED, HIGH = 0, 1, 2, 3
_LABEL = {0: "NONE", 1: "LOW", 2: "MED", 3: "HIGH"}

# Ordinal intensity dimensions, kept separate (the message's "do not hide weak dimensions").
INTENSITY_DIMS = ["economic_value", "competitive_intensity", "spend_growth", "cost_of_failure",
                  "cost_of_delay", "value_of_winning", "scarcity", "decision_urgency"]

# Buyer-desperation signal kinds (the message's list). Evidence that a valuable problem EXISTS.
SIGNAL_KINDS = ("HIGH_COMP", "RAPID_HIRING", "MANY_OPEN_ROLES", "LARGE_ACQUISITION",
                "LARGE_VENDOR_CONTRACT", "HIGH_CONSULTING_SPEND", "STARTUP_CREDIT_PROGRAM",
                "NEW_RND_FACILITY", "NEW_INNOVATION_UNIT", "EXEC_MANDATE", "STATED_BOTTLENECK",
                "MISSED_TARGET", "LAUNCH_DELAY", "COMPETITIVE_LOSS", "LARGE_GRANT",
                "GOVERNMENT_PROCUREMENT", "CHALLENGE_PRIZE", "BUDGET_INCREASE")


@dataclass
class DesperationSignal:
    kind: str                       # one of SIGNAL_KINDS
    who: str                        # the organization / buyer showing the signal
    evidence_url: str = ""
    quote: str = ""
    linked_gap: str = ""            # the specific unresolved gap this signal points to (REQUIRED to count)

    @property
    def counts_as_opportunity(self) -> bool:
        """A raw signal is only opportunity-relevant once tied to a concrete gap."""
        return bool(self.linked_gap)


@dataclass
class SpendCategory:
    """One economic battleground / spending war."""
    code: str
    desired_outcome: str
    major_buyers: str = ""
    budget_categories: str = ""     # which internal budgets fund it
    current_methods: str = ""       # how it is pursued today
    current_vendors: str = ""
    major_gaps: str = ""            # what is missing (free text; formalized in gap_finder)
    switching_dynamics: str = ""
    hackathon_fit: int = NONE       # ordinal advantage our environment holds in this war
    # --- ordinal intensity dims ---
    economic_value: int = NONE
    competitive_intensity: int = NONE
    spend_growth: int = NONE
    cost_of_failure: int = NONE
    cost_of_delay: int = NONE
    value_of_winning: int = NONE
    scarcity: int = NONE
    decision_urgency: int = NONE
    # --- money magnitudes as beliefs (default UNKNOWN; never fabricated) ---
    current_annual_spend: Belief = None
    # --- provenance ---
    evidence_strength: str = "HYPOTHETICAL"   # demand_evidence_kind (schema 004)
    signals: list = field(default_factory=list)

    def __post_init__(self):
        if self.current_annual_spend is None:
            self.current_annual_spend = unknown(f"annual_spend[{self.code}]", "no evidence",
                                                "current annual spend UNKNOWN until the sweep evidences it")

    def intensity_vector(self) -> dict:
        d = asdict(self)
        return {k: _LABEL[d[k]] for k in INTENSITY_DIMS}

    def intensity_raw(self) -> dict:
        d = asdict(self)
        return {k: d[k] for k in INTENSITY_DIMS}

    @property
    def spend_is_evidenced(self) -> bool:
        return self.current_annual_spend.status != "UNKNOWN"

    def linked_signals(self) -> list:
        return [s for s in self.signals if s.counts_as_opportunity]


# Evidence strength order (schema 004 demand_evidence_kind), weakest -> strongest.
EVIDENCE_ORDER = ["HYPOTHETICAL", "INFERRED_JOB_POST", "PUBLIC_STATEMENT", "REGULATORY_FILING",
                  "PROGRAM_ANNOUNCEMENT", "BUYER_STATED", "SIGNED_COMMERCIAL"]


def rank_categories(categories) -> list:
    """Rank spending wars. Ordering is a decomposed tuple (the message's 8 ranking criteria), NOT a
    single collapsed score, and it is EVIDENCE-GATED: a category cannot rank on spend it cannot show,
    so evidence strength leads. Ties fall through the ordinal intensity dims. Returns best-first."""
    def key(c: SpendCategory):
        return (
            EVIDENCE_ORDER.index(c.evidence_strength),   # 1. how real is the evidence
            c.economic_value,                            # 2. size of the prize
            c.competitive_intensity,                     # 3. spending-war heat
            c.cost_of_failure,                           # 4. cost of failure
            c.decision_urgency,                          # 5. urgency
            c.hackathon_fit,                             # 6. our structural advantage
        )
    return sorted(categories, key=key, reverse=True)


def spend_rationale(category: SpendCategory) -> dict:
    """The 'why would they spend a lot?' test (the message). Surfaces whether a large economic
    surface EXISTS and what budget the money would otherwise go to — WITHOUT asserting WTP. Returns a
    structured, honest answer: the ceiling stays UNKNOWN unless spend is evidenced."""
    return {
        "why_care_at_100k": category.desired_outcome,
        "what_makes_a_higher_number_rational":
            f"cost_of_failure={_LABEL[category.cost_of_failure]}, "
            f"cost_of_delay={_LABEL[category.cost_of_delay]}, "
            f"value_of_winning={_LABEL[category.value_of_winning]}",
        "budget_this_would_replace": category.budget_categories or "UNKNOWN",
        "economic_surface_exists": (category.economic_value >= MED and category.competitive_intensity >= MED),
        "spend_evidenced": category.spend_is_evidenced,
        "note": "Existence of a large surface != willingness to pay. WTP stays UNKNOWN until a signed check.",
    }
