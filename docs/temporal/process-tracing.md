# Process tracing and counterfactual honesty

`engine/process_tracing.py`. For an important outcome we reconstruct the **mechanism**, not just a
correlation. `ProcessTrace` holds: what happened, what immediately preceded it, the proposed mechanism,
the evidence **for** it, the evidence **against** it (which must be sought, not hidden), and the rival
explanations kept explicit. `confidence_note()` never says "proven" — it says CONTESTED when
contradicting evidence exists, PLAUSIBLE_BUT_NOT_UNIQUE when rivals remain open.

**Counterfactual honesty (LXXVIII).** `counterfactual_options(intervention, identification)` returns a
counterfactual **only** when identification is credible (`RANDOMIZED` / `QUASI_EXPERIMENT` with a
comparison group). A single case with no comparison returns **`NOT_IDENTIFIED`** — the engine never
invents "what would have happened." Over repeated events, randomized or quasi-experimental variation
(e.g. contextual mentor routing for group A vs standard help for group B, comparing TimeToResolution)
is what eventually makes these estimable — reported as a CI, not a point claim.
