"""
Question-VOI scoring (docs/research-modules.md, "From Company-Fit to Question-VOI").

Scores a candidate research question on visible dimensions and returns the FULL VECTOR plus a
composite — dimensions are never collapsed away. HackathonAdvantage is a HARD GATE, not a weight:
if a hackathon holds no advantage over Gartner / a panel / the company's own telemetry, the
opportunity is ~0 regardless of how large the economic decision or budget is.

Scores are ordinal 0..3 (NONE, LOW, MED, HIGH) so they map cleanly to honest human judgement and
never imply false precision. VOI is a RATIONAL CEILING on price, not an observed WTP.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict

NONE, LOW, MED, HIGH = 0, 1, 2, 3
_LABEL = {0: "NONE", 1: "LOW", 2: "MED", 3: "HIGH"}

# Below this HackathonAdvantage, the opportunity is killed no matter the other dimensions.
HACKATHON_ADVANTAGE_FLOOR = MED


@dataclass
class QuestionScore:
    question: str
    economic_decision_size: int      # how big is the decision this could change?
    current_uncertainty: int         # how unsure is the buyer today?
    existing_research_spend: int     # do they already pay for research (budget proven)?
    internal_data_blind_spot: int    # is it invisible to their own telemetry?
    hackathon_naturalness: int       # does this behavior occur NATURALLY in a hackathon?
    behavior_observability: int      # can we actually observe it with allowed capture?
    experimental_feasibility: int    # can we get above L1 (randomize / compare)?
    longitudinal_value: int          # does 7/30/90-day follow-up add a lot?
    repeatability: int               # can we sell this again across events/buyers?
    buyer_authority: int             # is there a specific team with budget authority?

    def vector(self) -> dict:
        d = asdict(self); d.pop("question")
        return {k: _LABEL[v] for k, v in d.items()}

    @property
    def hackathon_advantage(self) -> int:
        """Our edge over the alternatives = how naturally the behavior occurs here AND how blind
        their own data is to it. If either is low, a panel/telemetry answers it just as well."""
        return min(self.hackathon_naturalness, self.internal_data_blind_spot)

    @property
    def voi_ceiling(self) -> int:
        """Rational price ceiling ~ ValueOfDecision × P(research changes the decision).
        P(change) proxied by uncertainty × our ability to reduce it (observability × feasibility)."""
        return self.economic_decision_size * self.current_uncertainty * max(
            self.behavior_observability, self.experimental_feasibility)

    @property
    def opportunity(self) -> float:
        """Opportunity = EconomicImportance × Unansweredness × HackathonAdvantage ×
        BehavioralObservability × BuyerBudget — with HackathonAdvantage as a HARD GATE."""
        if self.hackathon_advantage < HACKATHON_ADVANTAGE_FLOOR:
            return 0.0    # KILLED: answerable without us. Big budget cannot rescue it.
        return (self.economic_decision_size * self.current_uncertainty *
                self.hackathon_advantage * self.behavior_observability *
                max(self.existing_research_spend, self.buyer_authority))

    def verdict(self) -> str:
        if self.opportunity == 0.0:
            return "KILL — answerable without a hackathon (no HackathonAdvantage)"
        if self.opportunity >= 200:
            return "PURSUE — high-VOI, hackathon-unique"
        if self.opportunity >= 60:
            return "CANDIDATE — real but not flagship"
        return "WEAK — low opportunity"
