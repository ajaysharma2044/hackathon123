"""
Cornell cohort-advantage engine (docs/cornell-cohort-advantage.md; Part II).

The core test every commercial product must clear:

    CohortAdvantage = StudentSpecificity x CornellCapabilityFit x Naturalness
                      x BuyerBlindSpot x AlternativeDifficulty

Dimensions are DECOMPOSED (ordinal 0..3) and kept visible — weakness is never hidden in a composite.
The hard rule (Part II), enforced as a GATE exactly like score.py / problem_matcher:

    If the exact output can be obtained equally well from a normal panel, consultant, contractor,
    university lab, Kaggle, or the company's own users -> KILL THE PRODUCT.

That rule bites on three essential dimensions: AlternativeDifficulty (is it hard to get elsewhere?),
BuyerBlindSpot (is the buyer's own data blind to it?), and Naturalness (does a hackathon actually
produce it?). If any of the three is below the floor, the advantage is zero no matter how large the
other dimensions or the budget.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict

NONE, LOW, MED, HIGH = 0, 1, 2, 3
_LABEL = {0: "NONE", 1: "LOW", 2: "MED", 3: "HIGH"}

ADVANTAGE_FLOOR = MED
DIMS = ["student_specificity", "cornell_capability_fit", "naturalness",
        "buyer_blind_spot", "alternative_difficulty"]
# The three dimensions the KILL rule gates on (the "obtainable elsewhere" test).
ESSENTIAL = ["naturalness", "buyer_blind_spot", "alternative_difficulty"]


@dataclass
class CohortAdvantage:
    product: str
    student_specificity: int      # does it specifically need students / this life-stage?
    cornell_capability_fit: int   # can the Cornell population actually do it?
    naturalness: int              # does a hackathon naturally generate the activity?
    buyer_blind_spot: int         # is it invisible to the buyer's own users/telemetry?
    alternative_difficulty: int   # how hard to get the SAME output from panel/consultant/Kaggle/etc.
    note: str = ""

    def vector(self) -> dict:
        d = asdict(self)
        return {k: _LABEL[d[k]] for k in DIMS}

    def raw(self) -> dict:
        d = asdict(self)
        return {k: d[k] for k in DIMS}

    @property
    def gate_passed(self) -> bool:
        return all(getattr(self, k) >= ADVANTAGE_FLOOR for k in ESSENTIAL)

    @property
    def weakest_essential(self) -> str:
        return min(ESSENTIAL, key=lambda k: getattr(self, k))

    def verdict(self) -> str:
        if not self.gate_passed:
            k = self.weakest_essential
            reasons = {
                "alternative_difficulty": "the same output is obtainable from a panel/consultant/Kaggle/own users",
                "buyer_blind_spot": "the buyer can already see this in their own data",
                "naturalness": "a hackathon does not naturally generate this activity",
            }
            return f"KILL — {reasons[k]} ({k}={_LABEL[getattr(self, k)]})"
        strong = sum(1 for k in DIMS if getattr(self, k) >= HIGH)
        if strong >= 4:
            return "STRONG — a genuine, hard-to-replicate cohort advantage"
        if strong >= 2:
            return "MODERATE — real advantage, some dimensions soft"
        return "THIN — clears the gate but no dimension is strong"


def evaluate(product, student_specificity, cornell_capability_fit, naturalness,
             buyer_blind_spot, alternative_difficulty, note="") -> CohortAdvantage:
    return CohortAdvantage(product, student_specificity, cornell_capability_fit, naturalness,
                           buyer_blind_spot, alternative_difficulty, note)


def survivors(advantages) -> list:
    """Only the cohort advantages that clear the KILL gate."""
    return [a for a in advantages if a.gate_passed]


def rank(advantages) -> list:
    """Rank gate-passers first, then by count of HIGH dimensions, then total. Killed ones sink."""
    def key(a: CohortAdvantage):
        r = a.raw()
        return (a.gate_passed, sum(1 for k in DIMS if r[k] >= HIGH), sum(r.values()))
    return sorted(advantages, key=key, reverse=True)
