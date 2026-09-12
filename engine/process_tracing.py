"""
Process tracing + counterfactual honesty (docs/temporal/process-tracing.md; Parts LXX, LXXI, LXXVIII).

For an important outcome we reconstruct the MECHANISM, not just the correlation: what happened, what
immediately preceded it, the proposed mechanism, the evidence for AND against it, and the rival
explanations kept explicit. Counterfactuals are only asserted when causal identification actually
exists (randomization / a credible comparison) — otherwise the engine says NOT_IDENTIFIED and invents
nothing. This is the discipline that separates 'we can explain how value was produced' from 'we have a
lot of data'.
"""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ProcessTrace:
    outcome: str
    preceding_events: list = field(default_factory=list)   # ordered, from the temporal graph
    proposed_mechanism: str = None
    supporting_evidence: list = field(default_factory=list)
    contradicting_evidence: list = field(default_factory=list)   # LXX: must be sought, not hidden
    alternative_explanations: list = field(default_factory=list)
    thick_description: str = None                          # LXXI
    def confidence_note(self):
        if not self.supporting_evidence:
            return "NO_SUPPORT: mechanism is a hypothesis only"
        if self.contradicting_evidence:
            return "CONTESTED: supporting and contradicting evidence both present — report both"
        if self.alternative_explanations:
            return "PLAUSIBLE_BUT_NOT_UNIQUE: rival explanations remain open"
        return "SUPPORTED_PENDING_ALTERNATIVES: still list what could overturn it"

def trace(outcome, preceding_events, mechanism, supporting=None, contradicting=None, alternatives=None,
          thick=None):
    """Build a ProcessTrace. Every field the analyst leaves empty stays empty (missing is valid); the
    engine never fabricates supporting evidence or suppresses a rival explanation."""
    return ProcessTrace(outcome=outcome, preceding_events=list(preceding_events or []),
                        proposed_mechanism=mechanism, supporting_evidence=list(supporting or []),
                        contradicting_evidence=list(contradicting or []),
                        alternative_explanations=list(alternatives or []), thick_description=thick)

def counterfactual_options(intervention, identification=None):
    """LXXVIII. Return the counterfactual ONLY when identification is credible. identification is one of
    None/'NONE' (single case, no comparison) -> NOT_IDENTIFIED; 'RANDOMIZED'/'QUASI_EXPERIMENT' with a
    comparison group -> estimable. We NEVER invent 'what would have happened' from a single observation."""
    ok = identification in ("RANDOMIZED", "QUASI_EXPERIMENT")
    if not ok:
        return {"intervention": intervention, "counterfactual": "NOT_IDENTIFIED",
                "_note": "single case or no comparison group — the counterfactual is unknowable here; "
                         "collect randomized/quasi-experimental variation across events to estimate it"}
    return {"intervention": intervention, "identification": identification,
            "counterfactual": "ESTIMABLE", "_note": "estimate from the comparison group; report a CI, "
            "not a point claim, and keep descriptive vs causal separate"}
