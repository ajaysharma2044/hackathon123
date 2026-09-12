"""
Team state-transition model (docs/temporal/state-space.md; Parts XI, XII).

Teams move through states over the project clock. We estimate transition probabilities ONLY after
enough data — before that the honest answer is INSUFFICIENT_DATA, not a fabricated matrix. True state
is partially observed (a team can look BUILDING while silently BLOCKED); we acknowledge the hidden
state rather than pretending the observed label is ground truth. No premature HMM.
"""
from __future__ import annotations
from collections import defaultdict, Counter

TEAM_STATES = ("FORMING", "PLANNING", "BUILDING", "BLOCKED", "PIVOTING", "INTEGRATING",
               "TESTING", "POLISHING", "SUBMISSION_READY", "DONE")

def transition_counts(sequences):
    """Count observed state->state transitions across many team state-sequences."""
    c = defaultdict(Counter)
    for seq in sequences:
        for a, b in zip(seq, seq[1:]):
            c[a][b] += 1
    return c

def transition_matrix(counts, min_observations=10):
    """Row-normalise to probabilities, but ONLY for states with >= min_observations outgoing
    transitions (Part XI: 'estimate only after enough data'). Sparse rows return INSUFFICIENT_DATA so
    no one reads noise as signal."""
    out = {}
    for s in TEAM_STATES:
        row = counts.get(s, Counter())
        total = sum(row.values())
        if total < min_observations:
            out[s] = {"_status": "INSUFFICIENT_DATA", "_n": total}
        else:
            out[s] = {b: row[b] / total for b in row}
    return out

def next_state_distribution(matrix, state):
    """Predicted next-state distribution, or the insufficient-data marker."""
    return matrix.get(state, {"_status": "INSUFFICIENT_DATA", "_n": 0})

# XII. Hidden state: the observed label is not the true state.
HIDDEN_STATE_NOTE = ("Observed state != true state. A team can appear BUILDING while BLOCKED. Only fit "
                     "a latent-state (HMM/state-space) model once multi-event data supports it.")

def fit_hidden_markov(*_a, **_k):
    """Deliberately unimplemented for Event 1 (Part XII/XIX — no premature complexity)."""
    raise NotImplementedError(HIDDEN_STATE_NOTE)
