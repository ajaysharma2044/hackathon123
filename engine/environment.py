"""
The ENVIRONMENT primitive (docs/temporary-economy-thesis.md, docs/environment-capability-map.md,
docs/environment-archetypes.md).

This GENERALIZES event_optimizer.EventDesign. There, the environment was hardcoded to a 200-person,
72-hour, flown-in software hackathon. Here the environment is the configurable object itself:

    E = (Talent, Information, Tools, Capital, Incentives, Constraints, Time, Competition,
         Collaboration, Feedback, Governance, MarketMechanism, PhysicalEnvironment, DigitalEnvironment)

A hackathon is ONE point in this space (see `hackathon_flagship()`), not the space.

CRITICAL HONESTY (same discipline as event_optimizer.py): the coefficients that map a configuration
to its CAPABILITIES are ASSUMPTIONS, not measurements. They live in one ASSUMPTIONS dict `A` so they
are obviously assumptions. The value here is the machinery + the explicit mapping — NOT the specific
numbers. Capabilities are returned as a DECOMPOSED VECTOR (21 dims), never collapsed into one score,
mirroring score.py's "dimensions are never averaged away."
"""
from __future__ import annotations
from dataclasses import dataclass, field, replace
import numpy as np

# The 21 capability dimensions a temporary high-agency organization may have (Phase 5 / schema 004
# environment_capability_kind). Kept as an explicit list so the vector is always complete.
CAPABILITIES = [
    "PARALLEL_SEARCH", "SOLUTION_DIVERSITY", "FEEDBACK_SPEED", "PROTOTYPEABILITY",
    "EXPERIMENTABILITY", "BEHAVIORAL_REALISM", "MANIPULABILITY", "COUNTERFACTUAL_QUALITY",
    "OBSERVABILITY", "ARTIFACT_VALUE", "TIME_COMPRESSION", "INTERDISCIPLINARY_ADVANTAGE",
    "EXTERNAL_TALENT_ADVANTAGE", "SIMULATION_FEASIBILITY", "LONGITUDINAL_CAPTURE",
    "EXTERNAL_VALIDITY", "REPEATABILITY", "DEFENSIBILITY", "COST_ADVANTAGE",
    "SPEED_ADVANTAGE", "VALUE_OF_FAILURE",
]

MEDIA = ("IN_PERSON", "ONLINE", "HYBRID")
INCENTIVES = ("WINNER_TAKE_ALL", "MULTIPLE_PRIZES", "BOUNTIES", "MILESTONE_PAYMENTS",
              "PEER_PREDICTION", "AUCTION", "INTERNAL_MARKET", "RESOURCE_BUDGET",
              "CONTINUATION_CONTRACT", "PROCUREMENT_OFFER", "EQUITY", "REPUTATION_ONLY")

# ---- ASSUMED capability model (every coefficient here is an assumption; see docs/quant-assumptions.md) ----
# Each capability is a transparent, monotonic function of a few knobs. We deliberately keep these
# STRUCTURAL (thresholds / sums of labeled contributions) rather than fitting precise coefficients we
# do not have. Latent scores are unbounded-ish; `capability_vector` buckets them to ordinal 0..3.
A = {
    "parallel_k": 0.9,           # parallel search grows sublinearly in team count
    "diversity_interdisc": 0.8,  # solution diversity rewards interdisciplinary mix
    "diversity_competition": 0.6,
    "feedback_cadence_w": 1.0,
    "inperson_feedback_bonus": 0.5,
    "behavioral_inperson_bonus": 1.0,   # observed real behavior is more real in person
    "behavioral_incentive_penalty": 0.8, # heavy prizes contaminate "natural" behavior
    "observability_digital_w": 1.0,
    "longitudinal_followup_w": 1.5,      # the compounding-panel differentiator (STATE.md caveat #6)
    "time_compression_w": 1.2,
    "external_validity_selectivity_penalty": 0.7,  # elite selection HURTS representativeness (caveat #4)
    "cost_advantage_inperson_penalty": 1.0,        # flown-in in-person is the COSTLIEST data path (caveat #5)
    "value_of_failure_parallel_w": 0.7,            # many parallel attempts => informative negative results (Phase 17)
    "domain_expertise_w": 0.9,
}


@dataclass(frozen=True)
class Environment:
    """A configurable temporary organization. Fields group under the 14-tuple E. Every knob is a
    DECISION VARIABLE (Phase 12): a company brings a problem and the generator proposes values."""
    name: str
    archetype: str = "HACKATHON"
    # --- Talent (Phase 2): population-level mix, NEVER individual scoring ---
    n_participants: int = 200
    # talent_mix: tuple of (capability_label, population_share); shares should sum ~1.0
    talent_mix: tuple = (("SOFTWARE", 0.7), ("DESIGN", 0.15), ("BUSINESS", 0.15))
    interdisciplinarity: float = 0.3      # 0..1; how many distinct disciplines are represented
    selectivity: float = 0.9             # 0..1; elite selection. HIGH helps prestige, HURTS external validity
    experience_band: str = "STUDENT"     # STUDENT | EARLY | SENIOR | MIXED
    # --- Information ---
    information_asymmetry: float = 0.2   # 0..1; how much is hidden between actors
    data_access: int = 1                 # 0..3; real proprietary data given to teams
    # --- Tools / Digital ---
    tool_richness: int = 2               # 0..3
    instrumentation: int = 2             # 0..3; digital capture surface (observability)
    # --- Capital / Incentives ---
    prize_pool: float = 20000.0
    capital_access: int = 0              # 0..3; investment/continuation capital available
    incentive: str = "MULTIPLE_PRIZES"
    incentive_intensity: float = 0.5     # 0..1; how much behavior is driven by extrinsic reward
    # --- Constraints (hard rules the design must satisfy) ---
    constraints: tuple = ()
    # --- Time ---
    duration_hours: float = 72.0
    has_continuation: bool = False       # a 30/60/90-day follow-on phase
    followup_waves: int = 0              # number of longitudinal follow-up waves
    # --- Competition / Collaboration ---
    competition: float = 0.6             # 0..1
    collaboration: float = 0.5           # 0..1
    team_size: int = 4
    # --- Feedback ---
    feedback_cadence: int = 2            # 0..3; how often teams get signal / new information
    # --- Governance ---
    judging: str = "PANEL"               # PANEL | PEER_VOTE | AUCTION | MARKET | CUSTOMER_VOTE
    ip_terms: str = "PARTICIPANT_OWNS"
    # --- Market mechanism ---
    market_mechanism: str = "NONE"       # NONE | INTERNAL_MARKET | AUCTION | PROCUREMENT
    # --- Physical ---
    medium: str = "IN_PERSON"


def _share_of(env: Environment, label: str) -> float:
    return float(sum(s for lbl, s in env.talent_mix if lbl == label))


def _n_disciplines(env: Environment) -> int:
    return len({lbl for lbl, s in env.talent_mix if s > 0})


def capability_scores(env: Environment) -> dict:
    """Continuous latent capability scores (higher = more of that capability). ASSUMED structural
    model — see `A`. Returned as the FULL 21-dim vector, never collapsed. Use `capability_vector`
    for ordinal 0..3. Monotonicity (more participants -> more parallel search, etc.) is the property
    the tests pin, not the magnitudes."""
    n = max(env.n_participants, 1)
    teams = n / max(env.team_size, 1)
    inperson = 1.0 if env.medium == "IN_PERSON" else (0.5 if env.medium == "HYBRID" else 0.0)
    s = {}
    s["PARALLEL_SEARCH"] = A["parallel_k"] * np.log1p(teams)
    s["SOLUTION_DIVERSITY"] = (A["diversity_interdisc"] * env.interdisciplinarity * _n_disciplines(env)
                              + A["diversity_competition"] * env.competition + 0.3 * np.log1p(teams))
    s["FEEDBACK_SPEED"] = A["feedback_cadence_w"] * env.feedback_cadence + A["inperson_feedback_bonus"] * inperson
    s["PROTOTYPEABILITY"] = env.tool_richness + 0.5 * _share_of(env, "SOFTWARE") + 0.3 * env.data_access
    s["EXPERIMENTABILITY"] = 0.6 * env.data_access + 0.5 * env.feedback_cadence + 0.7 * (env.market_mechanism != "NONE")
    s["BEHAVIORAL_REALISM"] = (A["behavioral_inperson_bonus"] * inperson + 0.5 * env.data_access
                              - A["behavioral_incentive_penalty"] * env.incentive_intensity)
    s["MANIPULABILITY"] = 1.0 + env.feedback_cadence * 0.5 + (env.market_mechanism != "NONE")  # can we introduce shocks/treatments?
    s["COUNTERFACTUAL_QUALITY"] = 0.5 * env.feedback_cadence + 0.8 * (env.competition > 0.3) + 0.6 * (teams >= 8)
    s["OBSERVABILITY"] = A["observability_digital_w"] * env.instrumentation + 0.4 * inperson
    s["ARTIFACT_VALUE"] = env.tool_richness + env.data_access + 0.5 * env.capital_access
    s["TIME_COMPRESSION"] = A["time_compression_w"] * (1.0 / np.log1p(env.duration_hours / 24.0 + 1)) * np.log1p(teams)
    s["INTERDISCIPLINARY_ADVANTAGE"] = A["diversity_interdisc"] * env.interdisciplinarity * _n_disciplines(env)
    s["EXTERNAL_TALENT_ADVANTAGE"] = env.selectivity + 0.5 * (env.experience_band in ("SENIOR", "MIXED"))
    s["SIMULATION_FEASIBILITY"] = 0.7 * env.data_access + 0.6 * (env.market_mechanism != "NONE") + 0.4 * env.tool_richness
    s["LONGITUDINAL_CAPTURE"] = A["longitudinal_followup_w"] * env.followup_waves + 1.0 * env.has_continuation
    # external validity is HURT by elite selection (STATE.md caveat #4) and by short artificial time
    s["EXTERNAL_VALIDITY"] = (2.0 - A["external_validity_selectivity_penalty"] * env.selectivity
                             + 0.5 * env.data_access + 0.3 * env.has_continuation)
    s["REPEATABILITY"] = 1.0 + 0.5 * (env.archetype != "BESPOKE") + 0.5 * (env.followup_waves > 0)
    s["DEFENSIBILITY"] = 0.6 * env.followup_waves + 0.5 * env.has_continuation + 0.4 * env.instrumentation
    # cost advantage is LOWER (worse) for flown-in in-person (caveat #5)
    s["COST_ADVANTAGE"] = 3.0 - A["cost_advantage_inperson_penalty"] * inperson - 0.4 * (env.n_participants > 150)
    s["SPEED_ADVANTAGE"] = A["time_compression_w"] * np.log1p(teams) / np.log1p(env.duration_hours / 24.0 + 1)
    s["VALUE_OF_FAILURE"] = A["value_of_failure_parallel_w"] * np.log1p(teams) + 0.5 * env.competition
    return {k: float(v) for k, v in s.items()}


def _bucket(x: float, lo: float, hi: float) -> int:
    """Map a latent score into ordinal 0..3 (NONE/LOW/MED/HIGH) against a labeled [lo,hi] band."""
    if hi <= lo:
        return 0
    q = (x - lo) / (hi - lo)
    return int(np.clip(np.floor(q * 4), 0, 3))


def capability_vector(env: Environment) -> dict:
    """Ordinal 0..3 capability vector (score.py NONE/LOW/MED/HIGH convention). Bands are ASSUMED and
    chosen so a flagship hackathon lands mid-range, leaving room above and below for other archetypes."""
    raw = capability_scores(env)
    # ASSUMED normalization bands, per capability (min, max of the plausible design space).
    bands = {
        "PARALLEL_SEARCH": (0, 5), "SOLUTION_DIVERSITY": (0, 4), "FEEDBACK_SPEED": (0, 4),
        "PROTOTYPEABILITY": (0, 5), "EXPERIMENTABILITY": (0, 4), "BEHAVIORAL_REALISM": (-1, 3),
        "MANIPULABILITY": (0, 4), "COUNTERFACTUAL_QUALITY": (0, 3), "OBSERVABILITY": (0, 4),
        "ARTIFACT_VALUE": (0, 6), "TIME_COMPRESSION": (0, 3), "INTERDISCIPLINARY_ADVANTAGE": (0, 2.2),
        "EXTERNAL_TALENT_ADVANTAGE": (0, 1.5), "SIMULATION_FEASIBILITY": (0, 4),
        "LONGITUDINAL_CAPTURE": (0, 6), "EXTERNAL_VALIDITY": (0, 4), "REPEATABILITY": (0, 3),
        "DEFENSIBILITY": (0, 4), "COST_ADVANTAGE": (0, 3), "SPEED_ADVANTAGE": (0, 4),
        "VALUE_OF_FAILURE": (0, 4),
    }
    return {k: _bucket(raw[k], *bands[k]) for k in CAPABILITIES}


def tweak(env: Environment, **changes) -> dict:
    """Change one knob, return the delta on each capability latent (mirrors event_optimizer.tweak)."""
    base = capability_scores(env)
    new = capability_scores(replace(env, **changes))
    return {k: round(new[k] - base[k], 3) for k in CAPABILITIES}


# ---- Named reference points in the design space (each is ONE point, not the space) ----
def hackathon_flagship() -> Environment:
    """The prior thesis's flagship, expressed as ONE Environment. Preserved, not privileged."""
    return Environment(name="hackathon_flagship", archetype="HACKATHON", n_participants=200,
                       duration_hours=72, medium="IN_PERSON", selectivity=0.95,
                       instrumentation=2, followup_waves=0, incentive="MULTIPLE_PRIZES")


def hackathon_with_panel() -> Environment:
    """The hackathon PLUS the longitudinal follow-up that STATE.md flags as the untested moat engine."""
    return replace(hackathon_flagship(), name="hackathon_with_panel",
                   has_continuation=True, followup_waves=3)
