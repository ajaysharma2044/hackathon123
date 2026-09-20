# Optimal stopping — continue vs pivot, kill vs fund

`engine/optimal_stopping.py`. A stuck team faces: keep trying or pivot? Continue while
`E[value of another attempt] > E[value of pivoting now]`.

`should_continue(p_success_next, value_success, value_pivot_now, attempt_cost)` returns CONTINUE/PIVOT
**with both expected values shown**, so the reasoning is transparent. R&D gets the three-way version
`rd_path_decision(...)` — CONTINUE the current path, KILL it, or FUND_ALTERNATIVE — the same
expected-value logic used to decide when to stop funding a failing approach and move resources.

**No fake thresholds.** The probabilities and values are the caller's estimates; when any is missing
the engine returns `INPUTS_UNKNOWN` rather than inventing a number. Before Event 1 these functions are
*structure for collecting the data that will let them be learned*, not pretend-precise oracles.
