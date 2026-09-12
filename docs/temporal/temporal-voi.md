# Time-sensitive value of information

`engine/temporal_voi.py`. Client value depends not only on *what* we learn but *when*. If a company
must decide its roadmap in November, October evidence can be worth far more than identical January
evidence. VOI becomes **VOI(E, t)**, and we separate **information quality** from **delivery speed** —
never blending them into one opaque number. Reuses `voi.py` (EVPI/EVSI/NetVOI), does not reimplement it.

`voi_at(evsi_value, delivery_time, decision_deadline, cost)`: evidence delivered **on time** carries
its decision value; delivered **after the deadline** it carries **zero decision value** (the decision
is already made) — though it may still have research value, tracked elsewhere. Verified: the same
$20K-quality evidence is worth **$15K net on time** and **−$5K net late**.

## The temporal product ladder (XXIX)

Different horizons answer **different buyer decisions** — they are not the same product:

| Rung | Horizon | Decision it informs |
|---|---|---|
| LIVE_AGGREGATE_SIGNAL | during-event | real-time ops / sponsor activation |
| RAPID_READOUT | T+48h | urgent roadmap / launch go-no-go |
| WEEK_ONE_FINDING | T+7d | short-term continuation |
| THIRTY_DAY_PERSISTENCE | T+30d | behavioral persistence / retention |
| NINETY_DAY_LONGITUDINAL | T+90d | long-term retention / venture / hiring |
| MULTI_EVENT_BENCHMARK | multi-event | benchmarking vs prior cohorts |

`ladder_for_deadline(days)` returns only the rungs a deadline can wait for — a **3-day deadline cannot
be served by the 90-day rung** (Part LXII: don't sell a horizon the deadline can't wait for).
**WTP for every rung remains UNKNOWN until buyers are asked** (`WTP_STATUS`).
