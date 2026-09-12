"""
The GENERAL ECONOMY (docs/economic-flow-model.md).

Generalizes the "hackathon as a compressed economic laboratory" (research-data-model.md) and the
choice_set / economic_transaction tables (schema 002) beyond participants-choosing-devtools. The
temporary organization is a real economy: actors face opportunities, hold resources, respond to
incentives, decide, allocate resources, transact, behave, produce artifacts, and generate outcomes.

    Actor -> Opportunity -> ChoiceSet -> ResourcesAvailable -> Incentives -> Decision
          -> ResourceAllocation -> Transaction -> Behavior -> Artifact -> Outcome

Two disciplines carried over:
- CASH IS ONLY ONE PRICE (Phase 4). Non-cash resources (mentor-minutes, GPU-hours, customer intros)
  carry SHADOW PRICES represented as `beliefs.Belief`, default UNKNOWN. We do not invent a dollar
  value for a mentor-hour without evidence.
- FLOW ANALYTICS ARE DESCRIPTIVE. The ledger reconstructs where attention/resources actually flowed;
  it does not impute value where none is evidenced (marginal-value stays UNKNOWN without a belief).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from beliefs import Belief, unknown
from monte_carlo import simulate

# Resource catalogue (schema 004 resource_kind). Cash is one entry among many.
RESOURCE_KINDS = (
    "CASH", "PARTICIPANT_TIME_MIN", "MENTOR_TIME_MIN", "DOMAIN_EXPERT_TIME_MIN", "COMPUTE_GPU_HR",
    "API_CREDITS", "DATASET_ACCESS", "CUSTOMER_ACCESS", "CAPITAL", "PRIZE", "BOUNTY", "GRANT",
    "INTRODUCTION", "DISTRIBUTION", "REPUTATION", "SOCIAL_CAPITAL", "WORKSPACE", "MATERIALS",
    "EQUIPMENT", "JOB_OPPORTUNITY", "INVESTMENT_OPPORTUNITY", "DESIGN_PARTNER_SLOT",
    "PROCUREMENT_OPPORTUNITY", "IP",
)

ACTOR_KINDS = (
    "PARTICIPANT", "TEAM", "CORPORATION", "BUSINESS_UNIT", "SPONSOR", "BUYER", "MENTOR", "JUDGE",
    "DOMAIN_EXPERT", "INVESTOR", "VENDOR", "RECRUITER", "CUSTOMER", "USER", "GOVERNMENT",
    "UNIVERSITY", "ORGANIZER", "STARTUP",
)


@dataclass
class Actor:
    actor_id: str
    kind: str                       # one of ACTOR_KINDS
    label: str = ""


@dataclass
class Episode:
    """One actor's path from opportunity to (optional) outcome. Missing stages stay None — we do not
    fill them in. `choice_set` records what was AVAILABLE (choice != preference, schema 002)."""
    episode_id: str
    actor_id: str
    opportunity_kind: str                                  # PROBLEM | PROJECT | TEAM | BOUNTY | ...
    choice_set: tuple = ()                                 # options that were available
    resources_available: dict = field(default_factory=dict)   # {resource_kind: amount}
    incentives: dict = field(default_factory=dict)
    decision: str = None                                   # the option chosen (None = abandoned/none)
    resource_allocation: dict = field(default_factory=dict)   # {resource_kind: amount committed}
    behavior: dict = field(default_factory=dict)
    artifact_kind: str = None
    outcome_kind: str = None
    is_negative_result: bool = False                       # a failure that is itself informative (Phase 17)
    changed_a_decision: bool = None                        # the only outcome that matters commercially


class ShadowPrices:
    """Registry of resource -> price Belief. Default UNKNOWN for every resource until evidenced.
    `value_of` returns None (not a number) when the price is UNKNOWN."""
    def __init__(self):
        self.prices = {r: unknown(f"shadow_price[{r}]", "no evidence",
                                  "non-cash resource price is UNKNOWN until evidenced")
                       for r in RESOURCE_KINDS}

    def set(self, resource: str, belief: Belief):
        if resource not in RESOURCE_KINDS:
            raise KeyError(f"unknown resource {resource!r}")
        self.prices[resource] = belief
        return belief

    def value_of(self, resource: str, amount: float):
        """Point value of `amount` units, using the belief mean. None if the price is UNKNOWN."""
        b = self.prices[resource]
        m = b.mean()
        return None if m is None else m * amount

    def unresolved(self):
        """Resources whose shadow price is still UNKNOWN — the honest to-do list."""
        return [r for r, b in self.prices.items() if b.status == "UNKNOWN"]


class EconomicLedger:
    """Append-only ledger of episodes; reconstructs the temporary economy and reports flows (Phase 15).
    All analytics are descriptive counts/sums over what actually happened."""
    def __init__(self, shadow_prices: ShadowPrices = None):
        self.actors = {}
        self.episodes = []
        self.shadow_prices = shadow_prices or ShadowPrices()

    def add_actor(self, a: Actor):
        self.actors[a.actor_id] = a; return a

    def add_episode(self, e: Episode):
        self.episodes.append(e); return e

    # ---- flow analytics (descriptive; never impute unevidenced value) ----
    def attention_flow(self) -> dict:
        """How many actors CHOSE each opportunity — where talent/attention actually flowed."""
        out = defaultdict(int)
        for e in self.episodes:
            if e.decision is not None:
                out[e.opportunity_kind] += 1
        return dict(out)

    def abandonment(self) -> dict:
        """Opportunities that were in a choice set but not chosen (offered != taken; schema 001
        `opportunity`). Absence of behavior != inability."""
        out = defaultdict(int)
        for e in self.episodes:
            if e.decision is None and e.opportunity_kind:
                out[e.opportunity_kind] += 1
        return dict(out)

    def resource_flow(self) -> dict:
        """Total committed amount by resource across all episodes."""
        out = defaultdict(float)
        for e in self.episodes:
            for r, amt in e.resource_allocation.items():
                out[r] += amt
        return dict(out)

    def bottlenecks(self, supply: dict) -> dict:
        """Resources where committed demand exceeds supplied capacity. supply: {resource: capacity}.
        Returns {resource: overshoot} for the binding ones."""
        demand = self.resource_flow()
        out = {}
        for r, cap in supply.items():
            d = demand.get(r, 0.0)
            if d > cap:
                out[r] = d - cap
        return out

    def negative_results(self) -> int:
        """Count of informative failures — the value-of-failure surface (Phase 17)."""
        return sum(1 for e in self.episodes if e.is_negative_result)

    def decisions_changed(self) -> int:
        """Count of outcomes that changed a buyer decision — the commercial numerator."""
        return sum(1 for e in self.episodes if e.changed_a_decision)


def simulate_contribution(revenue_params: dict, cost_params: dict, n=40000, seed=7):
    """Generalized contribution = sum(revenue beliefs) - sum(cost beliefs), as a Monte Carlo
    distribution (generalizes event_optimizer.economic). Both dicts map name -> beliefs.Belief.
    Reuses monte_carlo.simulate, which RAISES if any belief is UNKNOWN — so an unevidenced revenue
    line cannot silently become a number. Returns an MCResult (mean/p5/p95/prob_gt/var/cvar)."""
    params = {}
    params.update(revenue_params)
    params.update(cost_params)
    rev_names = list(revenue_params)
    cost_names = list(cost_params)

    def model(s, rng):
        rev = sum(s[k] for k in rev_names)
        cost = sum(s[k] for k in cost_names)
        return rev - cost

    return simulate(model, params, n=n, seed=seed)
