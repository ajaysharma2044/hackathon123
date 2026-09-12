"""
COMPANY -> OFFER generator (docs/company-opportunity-map.md, Part XII). Takes a company situation
and routes to the best-fit value engine with a structured 20-field offer -- or concludes NO_FIT.
Deterministic, transparent, and ALLOWED to say no. All fit scores are structural (from evidence
flags); every price is a rational CEILING, never observed WTP.

Engines: RESEARCH | R&D | PRODUCT_DEV | ACTIVATION | INNOVATION | SPONSORSHIP.
The HackathonAdvantage kill gate (min of naturalness & blind-spot) applies to the value engines;
SPONSORSHIP is the always-available floor product (branding/recruiting), never the differentiated sale.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from value_engines import RDProblem, rd_fit

L = {"NONE": 0, "LOW": 1, "MED": 2, "HIGH": 3}   # ordinal helper for structural flags


@dataclass
class CompanySituation:
    company: str
    industry: str
    business_unit: str
    problem: str                     # the expensive unresolved question/decision
    evidence: str                    # source of the problem (job post, launch, earnings, ...)
    trigger: str                     # why now
    decision_owner: str
    budget_owner_candidates: list    # which budget lines could pay (research/growth/R&D/...)
    current_solution: str
    why_insufficient: str
    economic_consequence: str        # decision size, qualitatively (belief lives in schema)
    # structural fit flags (each "NONE|LOW|MED|HIGH"); the ICP is an OUTPUT of these, not a logo
    developer_facing: str = "NONE"
    blind_spot: str = "NONE"         # is the deciding behavior invisible to their own telemetry?
    hackathon_naturalness: str = "NONE"  # does the behavior occur naturally in a build event?
    decision_value: str = "NONE"
    budget_signal: str = "NONE"      # do they already spend on research/R&D/credits?
    wants_adoption: str = "NONE"     # activation intent (startup program / credits / free tier)
    problem_uncertainty: float = 0.0
    parallelizable: float = 0.0
    prototypeable: float = 0.0
    evaluable: float = 0.0
    needs_deep_domain: float = 0.0
    participant_fit: str = "NONE"    # are our elite student builders the right population?


def _g(x): return L[x] / 3.0

def _hackathon_advantage(s):  # the kill gate: min(naturalness, blind_spot)
    return min(_g(s.hackathon_naturalness), _g(s.blind_spot))

def _engine_fits(s: CompanySituation):
    ha = _hackathon_advantage(s)
    fits = {}
    # RESEARCH: decision value x blind spot x naturalness x participant fit, gated by HackathonAdvantage.
    fits["RESEARCH"] = (0.0 if ha < 0.5 else
                        _g(s.decision_value) * ha * (0.4 + 0.6 * _g(s.participant_fit)) * (0.5 + 0.5 * _g(s.budget_signal)))
    # R&D: structural verdict from the parallel-search fit gate.
    verdict, _why = rd_fit(RDProblem(s.problem_uncertainty, s.parallelizable, s.prototypeable, s.evaluable, s.needs_deep_domain))
    fits["R&D"] = (0.0 if verdict == "inferior" else
                   s.problem_uncertainty * s.parallelizable * s.prototypeable * (0.4 + 0.6 * _g(s.decision_value)))
    # PRODUCT_DEV: wants the solution-space/feature-demand distribution; dev-facing + prototypeable.
    fits["PRODUCT_DEV"] = _g(s.developer_facing) * s.prototypeable * (0.4 + 0.6 * _g(s.decision_value)) * (0.5 + 0.5 * ha)
    # ACTIVATION: dev-facing + adoption intent + participant fit. Blind spot less required.
    fits["ACTIVATION"] = _g(s.developer_facing) * _g(s.wants_adoption) * (0.4 + 0.6 * _g(s.participant_fit))
    # INNOVATION: a specific company problem as a challenge (R&D-lite; needs prototypeable + evaluable).
    fits["INNOVATION"] = (0.0 if s.evaluable < 0.4 or s.prototypeable < 0.4 else
                          s.problem_uncertainty * s.prototypeable * s.evaluable * (0.4 + 0.6 * _g(s.decision_value)))
    # SPONSORSHIP: always available floor, scaled only by participant fit (branding/recruiting).
    fits["SPONSORSHIP"] = 0.25 * _g(s.participant_fit)
    return fits, verdict


# Rational price CEILINGS by engine (assumed bands; the-quote.md / innovation-budget.md). NOT WTP.
PRICE_CEILING = {"RESEARCH": (50000, 150000), "R&D": (75000, 300000), "PRODUCT_DEV": (50000, 150000),
                 "ACTIVATION": (10000, 60000), "INNOVATION": (25000, 150000), "SPONSORSHIP": (5000, 50000)}
CAPACITY = {"RESEARCH": "1 primary study / ~1200 participant-min + ~60 researcher-hrs",
            "R&D": "1 challenge track / N teams (see optimal_teams)", "PRODUCT_DEV": "1 track / 5-15 teams",
            "ACTIVATION": "1 exposure arm; consumes unconstrained surface", "INNOVATION": "1 challenge track",
            "SPONSORSHIP": "booth/branding; ~0 research capacity"}
DELIVERABLE = {"RESEARCH": "aggregate findings report (funnel + friction + retention)",
               "R&D": "N independent prototypes + failure/elimination map + shortlist",
               "PRODUCT_DEV": "solution-space map + feature-demand + integration patterns",
               "ACTIVATION": "activation->30/90d retention funnel + the credit-vs-retention finding",
               "INNOVATION": "ranked solutions to your defined problem + prototypes",
               "SPONSORSHIP": "brand exposure + opt-in recruiting access"}
FIT_THRESHOLD = 0.18


@dataclass
class Offer:
    company: str; engine: str; fit: float
    problem: str; evidence: str; decision_owner: str; economic_importance: str
    current_method: str; why_hackathon_helps: str; event_module: str; participants: str
    event_changes: str; data_captured: str; deliverable: str; ip_confidentiality: str
    capacity_consumed: str; cost_to_us: str; pricing_evidence: str; commercial_package: str
    sales_message: str; confidence: str; still_to_learn: str


@dataclass
class NoFit:
    company: str; reason: str; best_engine: str; best_fit: float


def match(s: CompanySituation):
    fits, rd_verdict = _engine_fits(s)
    engine, fit = max(fits.items(), key=lambda kv: kv[1])
    # A differentiated (non-sponsorship) sale requires clearing the bar. Otherwise it is at best a
    # commodity sponsorship -- or NO FIT if even participant fit is weak.
    if engine == "SPONSORSHIP" or fit < FIT_THRESHOLD:
        if fits["SPONSORSHIP"] < 0.12:
            return NoFit(s.company, "no differentiated engine clears the bar and participant fit is weak; "
                         "a panel/telemetry/consultant answers this better", engine, round(fit, 3))
        return NoFit(s.company, "only commodity sponsorship fits; no differentiated value engine applies "
                     f"(best differentiated fit {round(max(v for k,v in fits.items() if k!='SPONSORSHIP'),3)})",
                     "SPONSORSHIP", round(fits["SPONSORSHIP"], 3))
    lo, hi = PRICE_CEILING[engine]
    conf = "HIGH" if fit > 0.5 else "MED" if fit > 0.3 else "LOW"
    return Offer(
        company=s.company, engine=engine, fit=round(fit, 3),
        problem=s.problem, evidence=s.evidence, decision_owner=s.decision_owner,
        economic_importance=s.economic_consequence, current_method=s.current_solution,
        why_hackathon_helps=s.why_insufficient + " -- observable naturally in a build event",
        event_module=f"{engine} module", participants=f"elite builders; fit={s.participant_fit}",
        event_changes=CAPACITY[engine], data_captured="brokered-key telemetry + artifacts + qualitative",
        deliverable=DELIVERABLE[engine], ip_confidentiality="per-sponsor confidential (omnibus); no cross-client leakage",
        capacity_consumed=CAPACITY[engine], cost_to_us="delivery cost per quant-assumptions.md",
        pricing_evidence=f"rational ceiling ${lo:,}-${hi:,} (comparables, NOT observed WTP)",
        commercial_package=f"{engine} engagement, ${lo:,}-${hi:,}",
        sales_message=f"You are trying to solve: {s.problem}. Your own data can't see it ({s.blind_spot} blind spot). "
                      f"We're assembling elite builders who will {s.problem.split()[0].lower()} naturally; a {engine} "
                      f"study on that resolves it. Open to a paid pilot?",
        confidence=conf,
        still_to_learn="observed WTP (UNKNOWN until a quote); champion strength; procurement path; sponsor telemetry cooperation")
