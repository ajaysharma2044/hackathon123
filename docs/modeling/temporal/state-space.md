# Team state-transition model

`engine/state_space.py`. Teams move through `TEAM_STATES` — FORMING, PLANNING, BUILDING, BLOCKED,
PIVOTING, INTEGRATING, TESTING, POLISHING, SUBMISSION_READY, DONE — over the project clock.

`transition_counts(sequences)` tallies observed state→state moves; `transition_matrix(counts,
min_observations)` row-normalises to probabilities **only** for states with enough outgoing
observations. A sparse row returns `INSUFFICIENT_DATA`, not a noisy estimate — *"estimate transition
probabilities only after enough data"* (Part XI). `next_state_distribution` predicts from the matrix.

**Hidden state (XII):** the observed label is not the true state — a team can look BUILDING while
silently BLOCKED. `fit_hidden_markov` is deliberately unimplemented for Event 1 (`NotImplementedError`
with `HIDDEN_STATE_NOTE`): no premature latent-variable modelling before multi-event data supports it.
