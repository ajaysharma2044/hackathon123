"""
Temporal event graph — timestamped edges, window/trajectory queries, and motif mining
(docs/temporal/temporal-graph.md; Parts IX, X, XX-XXI, XXXIII-XXXIV, LXXVI-LXXVII).

Every edge is timestamped, so we can ask "show the 30 minutes before every database switch" or "show
teams whose architecture changed within an hour of a mentor intervention". Sequence itself is a
variable: FAIL->MENTOR->SUCCESS is a different causal story from MENTOR->TRY->FAIL. We discover
recurring motifs — but ORDER IS NOT CAUSALITY, and the API says so at every turn.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter, defaultdict

@dataclass(frozen=True)
class TemporalEdge:
    src: str
    rel: str                 # USED | SWITCHED_TO | HELPED | RECOMMENDED | ...
    dst: str
    t_start: datetime
    t_end: datetime = None
    def active_at(self, t):
        return self.t_start <= t and (self.t_end is None or t <= self.t_end)

class TemporalGraph:
    def __init__(self):
        self.edges: list[TemporalEdge] = []
    def add_edge(self, e: TemporalEdge):
        self.edges.append(e); return self
    def edges_in_window(self, t0: datetime, t1: datetime):
        return [e for e in self.edges if t0 <= e.t_start <= t1]

    def window_before(self, target_rel: str, minutes: float, entity=None):
        """LXXVI. For every occurrence of `target_rel`, return the edges in the `minutes` before it —
        e.g. events_before('SWITCHED_TO', 30). Descriptive context, not a cause."""
        out = []
        for e in self.edges:
            if e.rel != target_rel:
                continue
            if entity is not None and e.src != entity:
                continue
            lo = e.t_start - timedelta(minutes=minutes)
            preceding = [p for p in self.edges if p is not e and e.src == p.src
                         and lo <= p.t_start < e.t_start]
            out.append({"target": e, "preceding": sorted(preceding, key=lambda p: p.t_start),
                        "_note": "temporal proximity is not causation"})
        return out

    def trajectory(self, entity: str):
        """LXXVII. The whole ordered evolution for one entity."""
        return sorted([e for e in self.edges if e.src == entity], key=lambda e: e.t_start)

    def sequence(self, entity: str):
        """Ordered event-type sequence for an entity: E1 -> E2 -> ... -> En."""
        return [e.rel for e in self.trajectory(entity)]

def find_motifs(sequences, n=3, min_support=2):
    """X. Recurring ordered n-gram motifs across many sequences, with support. Returns motifs sorted by
    frequency. Order != causality: outcomes and negative cases must be attached separately (motif_outcomes).
    sequences: list of lists of event-type labels."""
    counts = Counter()
    for seq in sequences:
        for i in range(len(seq) - n + 1):
            counts[tuple(seq[i:i+n])] += 1
    return [{"motif": " -> ".join(m), "support": c,
             "_caveat": "frequency only; do NOT infer causality from order"}
            for m, c in counts.most_common() if c >= min_support]

def motif_outcomes(sequences_with_outcomes, motif):
    """Attach outcomes AND negative cases to a motif (Part X): among sequences containing the motif,
    how many reached each outcome, and the negative cases (motif present, outcome absent).
    sequences_with_outcomes: list of (sequence_list, outcome_label)."""
    m = tuple(motif.split(" -> ")) if isinstance(motif, str) else tuple(motif)
    def contains(seq):
        return any(tuple(seq[i:i+len(m)]) == m for i in range(len(seq) - len(m) + 1))
    matched = [(s, o) for s, o in sequences_with_outcomes if contains(s)]
    outc = Counter(o for _, o in matched)
    return {"motif": " -> ".join(m), "n_with_motif": len(matched), "outcomes": dict(outc),
            "negative_cases": [s for s, o in matched if o in (None, "", "FAILURE", "ABANDONED")],
            "_caveat": "descriptive co-occurrence; not an effect estimate"}
