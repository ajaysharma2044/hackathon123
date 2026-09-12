"""
ICP discovery (docs/icp-discovery-engine.md; Phases 19-20).

The ICP is an OUTPUT, never an input. This module clusters high-opportunity problems and synthesizes
candidate ICPs. It deliberately does NOT start from "our customer is a devtools company" — that is
one hypothesis in a much larger space, and it must earn its place from the problem universe like any
other.

Discipline:
- Every buyer dimension (pain, urgency, budget, decision value, WTP) is a beliefs.Belief, default
  UNKNOWN. update_beta moves them only on reliability-weighted evidence (a signed check moves them
  far; a comparable barely). No dimension is fabricated into a number.
- Candidates are ranked by EVIDENCE STRENGTH first, not by imagined opportunity size — a cluster built
  only from HYPOTHETICAL worked examples can never outrank one with real demand-side evidence.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from beliefs import Belief, unknown, update_beta, RateObservation

# Strength ordering for demand-side evidence (schema 004 demand_evidence_kind), weakest -> strongest.
EVIDENCE_ORDER = ["HYPOTHETICAL", "INFERRED_JOB_POST", "PUBLIC_STATEMENT", "REGULATORY_FILING",
                  "PROGRAM_ANNOUNCEMENT", "BUYER_STATED", "SIGNED_COMMERCIAL"]


@dataclass
class ICPDimensions:
    """Latent buyer state. Each dimension is a Belief; all default UNKNOWN (mirrors schema 003
    buyer_state, where every dimension is a belief id)."""
    pain: Belief = None
    urgency: Belief = None
    budget: Belief = None
    decision_value: Belief = None
    wtp: Belief = None            # willingness-to-pay — stays UNKNOWN until a signed check (caveat #1)

    def __post_init__(self):
        for f in ("pain", "urgency", "budget", "decision_value", "wtp"):
            if getattr(self, f) is None:
                setattr(self, f, unknown(f, "no evidence", f"{f} UNKNOWN until evidenced"))

    def unresolved(self):
        return [f for f in ("pain", "urgency", "budget", "decision_value", "wtp")
                if getattr(self, f).status == "UNKNOWN"]


@dataclass
class ICPCandidate:
    label: str
    problems: list = field(default_factory=list)     # the Problem objects in this cluster
    company_characteristics: str = ""
    exact_problem: str = ""
    exact_buyer: str = ""                             # the specific executive/role
    trigger: str = ""
    budget_source: str = ""
    existing_alternative: str = ""
    why_alternative_fails: str = ""
    why_our_environment_wins: str = ""
    required_talent: str = ""
    required_environment: str = ""
    frequency: str = ""
    business_model: str = ""
    risks: str = ""
    evidence_strength: str = "HYPOTHETICAL"           # strongest evidence behind the cluster
    dims: ICPDimensions = field(default_factory=ICPDimensions)

    @property
    def is_hypothetical_only(self) -> bool:
        return self.evidence_strength == "HYPOTHETICAL"


def cluster_problems(problems, by="mode") -> dict:
    """Group problems into candidate clusters. `by` in {'mode','industry','buyer'}. Clustering by
    mechanics/mode (not industry) is the Phase 7 discipline; industry is offered but secondary."""
    key = {"mode": lambda p: p.mode,
           "industry": lambda p: p.industry,
           "buyer": lambda p: p.budget_owner}[by]
    out = defaultdict(list)
    for p in problems:
        out[key(p)].append(p)
    return dict(out)


def _cluster_evidence_strength(problems, evidence_lookup=None) -> str:
    """Strongest evidence across the cluster. evidence_lookup: optional {problem_statement: kind}.
    With no external evidence, a cluster of real (non-hypothetical) problems is only INFERRED_JOB_POST
    at best here — the engine will not upgrade evidence it cannot see."""
    strengths = []
    for p in problems:
        if evidence_lookup and p.statement in evidence_lookup:
            strengths.append(evidence_lookup[p.statement])
        elif p.is_hypothetical:
            strengths.append("HYPOTHETICAL")
        else:
            strengths.append("INFERRED_JOB_POST")
    return max(strengths, key=lambda s: EVIDENCE_ORDER.index(s)) if strengths else "HYPOTHETICAL"


def synthesize(label, problems, evidence_lookup=None, **fields) -> ICPCandidate:
    """Build a candidate ICP from a cluster of problems. Descriptive fields are passed in (they are
    human/analytic judgements); the quantitative dims stay UNKNOWN until evidenced."""
    strength = _cluster_evidence_strength(problems, evidence_lookup)
    return ICPCandidate(label=label, problems=list(problems), evidence_strength=strength, **fields)


def record_wtp_evidence(icp: ICPCandidate, observations):
    """Move the WTP belief with reliability-weighted evidence (reuses beliefs.update_beta). Each obs
    is a beliefs.RateObservation (e.g. 1 of 8 buyers signed a pilot => close-rate). A SIGNED_COMMERCIAL
    observation is the only thing that flips WTP out of UNKNOWN into OBSERVED."""
    posterior = update_beta(1.0, 1.0, observations, source=f"wtp[{icp.label}]")
    icp.dims.wtp = posterior
    return posterior


def rank(candidates) -> list:
    """Rank candidate ICPs by EVIDENCE STRENGTH first (honesty), then cluster size. A well-sourced
    small cluster beats a large imagined one. Returns candidates sorted best-first."""
    return sorted(candidates,
                  key=lambda c: (EVIDENCE_ORDER.index(c.evidence_strength), len(c.problems)),
                  reverse=True)
