# Survival / hazard and event intensity

`engine/survival.py`. Time-to-event with right-censoring, hand-rolled Kaplan–Meier (statsmodels is not
in the stack). Models time until: abandonment, switch, completion, mentor request, retention loss,
continuation (`SURVIVAL_EVENTS`).

`kaplan_meier(durations, observed)` returns the survival step-function (observed=1 event, 0 censored);
`median_survival(km)` the first time S(t) ≤ 0.5 (or None under heavy censoring). This is **descriptive**
— `CAUSAL_WARNING` is attached to every curve; a survival curve is not an effect.

`event_intensity(timestamps, bucket)` gives arrival rate per bucket (e.g. mentor requests / 30 min) and
flags **bursts** (count > mean + 2·std). Deliberately minimal — a full Hawkes point process is not
warranted for Event 1 (Part XIV: "do not over-engineer").
