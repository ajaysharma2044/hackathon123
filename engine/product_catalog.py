"""
Commercial product universe + kill gates (docs/commercial-product-universe.md, docs/product-kill-gates.md;
Parts VIII-IX, XXI).

Build the universe broad, then KILL aggressively. Every product must survive all TEN kill gates
(Part IX). WTP is UNKNOWN for every product until a signed check (never asserted). Products are scored
on decomposed dimensions elsewhere (cohort_advantage.py); here the gate is binary per criterion, and a
single failed gate kills the product no matter how attractive the rest.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# The 10 kill gates (Part IX). A product survives only if EVERY answer is True.
KILL_GATES = {
    1: "Is Cornell's population actually relevant to producing this?",
    2: "Does a hackathon naturally generate the activity?",
    3: "Is the output hard to get elsewhere (panel/consultant/Kaggle/own users)?",
    4: "Does a buyer have an expensive problem this addresses?",
    5: "Is there an identifiable budget?",
    6: "Is there a decision or outcome at stake?",
    7: "Can the event produce credible evidence/artifacts for it?",
    8: "Can we deliver it without degrading the participant experience?",
    9: "Can it coexist with other modules at the same event?",
    10: "Is the output sufficiently differentiated to be worth paying for?",
}


@dataclass
class Product:
    code: str
    name: str
    family: str                      # RESEARCH | PRODUCT_DEV | RND | INNOVATION | ACTIVATION | DESIGN_PARTNER | TALENT | SPONSORSHIP | CONTENT | FOLLOW_ON
    engine: str
    buyer_problem: str
    gates: dict = field(default_factory=dict)   # {1..10: bool}
    cohort_advantage_note: str = ""
    wtp_status: str = "UNKNOWN"      # always UNKNOWN until a signed check
    evidence_strength: str = "HYPOTHETICAL"
    kill_reason: str = ""

    @property
    def survives(self) -> bool:
        return len(self.gates) == 10 and all(self.gates.values())

    @property
    def failed_gates(self) -> list:
        return [g for g in sorted(KILL_GATES) if not self.gates.get(g, False)]

    def verdict(self) -> str:
        if self.survives:
            return "SURVIVES — clears all 10 kill gates (still WTP-UNKNOWN)"
        fg = self.failed_gates
        why = self.kill_reason or KILL_GATES[fg[0]]
        return f"KILL — fails gate {fg} ({why})"


def _g(*true_gates) -> dict:
    """Helper: gates listed are True, the rest False."""
    return {i: (i in true_gates) for i in KILL_GATES}


def _all_but(*false_gates) -> dict:
    return {i: (i not in false_gates) for i in KILL_GATES}


# The universe (broad first). Gate answers are honest current judgements, revisable as evidence
# arrives. Several are deliberately KILLED to show the gates bite.
PRODUCT_UNIVERSE = {
    # ---- RESEARCH ----
    "GREENFIELD_CHOICE_STUDY": Product(
        "GREENFIELD_CHOICE_STUDY", "Greenfield technology-choice study", "RESEARCH",
        "RESEARCH", "which tools do unconstrained builders reach for, and why",
        gates=_all_but(), cohort_advantage_note="students choose before procurement/legacy (pre-enterprise window HYPOTHESIS)",
        evidence_strength="INFERRED_JOB_POST"),
    "WHY_NOT_US_STUDY": Product(
        "WHY_NOT_US_STUDY", "Why-not-us / non-selection study", "RESEARCH",
        "RESEARCH", "why builders chose a competitor before entering our funnel",
        gates=_all_but(), cohort_advantage_note="non-selection is invisible to the buyer's own telemetry (blind spot HIGH)"),
    "AI_PRODUCTIVITY_EXPERIMENT": Product(
        "AI_PRODUCTIVITY_EXPERIMENT", "AI-on-work productivity experiment", "EXPERIMENTATION",
        "EXPERIMENTATION", "does an AI tool actually make builders faster (neutral, causal)",
        gates=_all_but(), cohort_advantage_note="neutral party can say what no vendor can; the sharpest wedge",
        evidence_strength="PUBLIC_STATEMENT"),
    "SWITCHING_STUDY": Product(
        "SWITCHING_STUDY", "Tool switching study", "RESEARCH", "RESEARCH",
        "what triggers builders to switch away from a product mid-build",
        gates=_all_but()),
    "REPRESENTATIVE_MARKET_SURVEY": Product(
        "REPRESENTATIVE_MARKET_SURVEY", "Representative market survey", "RESEARCH", "RESEARCH",
        "what the median developer/market thinks",
        gates=_g(2,4,5,6,7,9), cohort_advantage_note="elite n≈200 is NOT representative",
        kill_reason="killed: a panel does this better; Cornell cohort is unrepresentative (gates 1,3,10)"),

    # ---- PRODUCT DEVELOPMENT ----
    "BETA_ARENA": Product(
        "BETA_ARENA", "Beta arena (competing products, observed use)", "PRODUCT_DEVELOPMENT",
        "PRODUCT_DEVELOPMENT", "how do real builders use our beta vs alternatives",
        gates=_all_but()),
    "ONBOARDING_OPTIMIZATION": Product(
        "ONBOARDING_OPTIMIZATION", "Onboarding / time-to-first-value study", "PRODUCT_DEVELOPMENT",
        "PRODUCT_DEVELOPMENT", "where do new users stall before first value",
        gates=_all_but()),

    # ---- R&D / PARALLEL SEARCH ----
    "PARALLEL_TECHNICAL_SEARCH": Product(
        "PARALLEL_TECHNICAL_SEARCH", "Parallel technical search (N independent approaches)", "RND_PARALLEL_SEARCH",
        "RND_PARALLEL_SEARCH", "30 independent approaches to one hard problem in a weekend",
        gates=_all_but(), cohort_advantage_note="parallel breadth no single internal team produces"),
    "FAILURE_MAP": Product(
        "FAILURE_MAP", "Failure map / option elimination", "RND_PARALLEL_SEARCH", "RND_PARALLEL_SEARCH",
        "which approaches repeatably fail (value of negative results)",
        gates=_all_but()),
    "DEEP_DOMAIN_RND": Product(
        "DEEP_DOMAIN_RND", "Deep-domain confidential R&D", "RND_PARALLEL_SEARCH", "RND_PARALLEL_SEARCH",
        "solve a problem needing deep proprietary domain expertise + secrecy",
        gates=_g(2,4,5,6,9), kill_reason="killed: students lack tacit domain depth; confidentiality impossible at an open event (gates 1,3,7,8,10)"),

    # ---- INNOVATION ----
    "CORPORATE_CHALLENGE": Product(
        "CORPORATE_CHALLENGE", "Corporate innovation challenge", "RND_PARALLEL_SEARCH", "RESEARCH",
        "externalize an internal problem for divergent solutions",
        gates=_all_but()),

    # ---- ACTIVATION ----
    "API_ACTIVATION": Product(
        "API_ACTIVATION", "Developer/API activation + retention", "ACTIVATION", "ACTIVATION",
        "get technical students to genuinely adopt (not just download) our product",
        gates=_all_but(), cohort_advantage_note="required-exposure -> free-choice -> 30/90-day retention separates adoption from a download"),
    "CREDIT_EFFECTIVENESS": Product(
        "CREDIT_EFFECTIVENESS", "Startup-credit effectiveness study", "ACTIVATION", "RESEARCH",
        "do our credits cause durable retention or subsidize churn",
        gates=_all_but(), evidence_strength="PROGRAM_ANNOUNCEMENT"),

    # ---- DESIGN PARTNER ----
    "DESIGN_PARTNER_DISCOVERY": Product(
        "DESIGN_PARTNER_DISCOVERY", "Design-partner / early-adopter discovery", "DESIGN_PARTNER", "DESIGN_PARTNER",
        "find opt-in teams to become design partners",
        gates=_all_but()),

    # ---- TALENT ----
    "WORK_EVIDENCE_RECRUITING": Product(
        "WORK_EVIDENCE_RECRUITING", "Opt-in work-evidence recruiting access", "TALENT", "TALENT",
        "see who can actually build, from first-hand observation",
        gates=_all_but(), cohort_advantage_note="first-hand observation only; access/subscription, never a score (FCRA/LL144)"),
    "CANDIDATE_SCORING": Product(
        "CANDIDATE_SCORING", "Ranked candidate employability scores", "TALENT", "TALENT",
        "a ranked list of the 'best' students to hire",
        gates=_g(1,2,4,5,6,9), kill_reason="killed: emitting a person score/ranking is a hard ethical + legal boundary (LL144/EU AI Act) (gates 3,7,8,10)"),

    # ---- SPONSORSHIP ----
    "TITLE_SPONSOR": Product(
        "TITLE_SPONSOR", "Conventional title/track sponsorship", "SPONSORSHIP", "SPONSORSHIP",
        "brand + recruiting presence at a premium event",
        gates=_g(1,2,4,5,6,7,8,9), kill_reason="survives operationally but low differentiation — the frame the reset rejects (gates 3,10 weak)"),

    # ---- CONTENT / INTELLIGENCE ----
    "CORNELL_BUILDER_REPORT": Product(
        "CORNELL_BUILDER_REPORT", "Annual Cornell builder / tech-adoption index", "RESEARCH", "CONTENT",
        "a syndicated read on what elite student builders adopt",
        gates=_all_but(), cohort_advantage_note="early-adopter leading indicator, sold as depth not representativeness"),

    # ---- FOLLOW-ON ----
    "CONTINUATION_SPRINT": Product(
        "CONTINUATION_SPRINT", "4-week continuation R&D sprint", "RND_PARALLEL_SEARCH", "FOLLOW_ON",
        "extend the most promising teams/prototypes past the weekend",
        gates=_all_but(), cohort_advantage_note="captures the longitudinal/continuation signal that is the moat engine"),
}


def survivors() -> list:
    return [p for p in PRODUCT_UNIVERSE.values() if p.survives]

def killed() -> list:
    return [p for p in PRODUCT_UNIVERSE.values() if not p.survives]

EVIDENCE_ORDER = ["HYPOTHETICAL", "INFERRED_JOB_POST", "PUBLIC_STATEMENT", "REGULATORY_FILING",
                  "PROGRAM_ANNOUNCEMENT", "BUYER_STATED", "SIGNED_COMMERCIAL"]

def rank(products=None) -> list:
    """Survivors first, then evidence strength. WTP is never a ranking input (it is UNKNOWN)."""
    products = products or list(PRODUCT_UNIVERSE.values())
    return sorted(products, key=lambda p: (p.survives, EVIDENCE_ORDER.index(p.evidence_strength)), reverse=True)
