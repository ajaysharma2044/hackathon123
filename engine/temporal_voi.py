"""
Time-sensitive value of information (docs/temporal/temporal-voi.md; Parts XXVI, XXVII, XXVIII, XXIX).

Client value depends not only on WHAT we learn but WHEN. Evidence delivered after the client's
decision deadline has little/no decision value even if identical. So VOI becomes VOI(E,t), and we
separate INFORMATION QUALITY from DELIVERY SPEED. This creates a temporal product ladder (live signal
-> rapid readout -> week-one -> 30d -> 90d -> multi-event benchmark). WTP for every rung remains
UNKNOWN until buyers are asked. Reuses voi.net_voi / voi.evpi (does not reimplement the VOI math).
"""
from __future__ import annotations
from datetime import datetime
import voi   # reuse EVPI/EVSI/NetVOI

def voi_at(evsi_value, delivery_time: datetime, decision_deadline: datetime, cost=0.0):
    """VOI(E,t): the decision value of evidence that ARRIVES at delivery_time for a decision due at
    decision_deadline. After the deadline the decision is already made -> decision value 0 (the info
    may still have research value, tracked elsewhere). Quality (evsi_value) and speed (timing) are
    reported separately, never blended into one opaque number."""
    on_time = delivery_time <= decision_deadline
    decision_value = evsi_value if on_time else 0.0
    return {"information_quality": evsi_value,          # what we'd learn (speed-independent)
            "delivered_on_time": on_time,
            "decision_value": decision_value,           # 0 if it misses the deadline
            "net_voi": voi.net_voi(decision_value, cost),
            "_note": "quality and speed kept separate; post-deadline info has research value, not decision value"}

# XXIX. The temporal product ladder — different horizons answer DIFFERENT buyer decisions.
TEMPORAL_LADDER = [
    {"rung": "LIVE_AGGREGATE_SIGNAL", "horizon": "during-event", "decision": "real-time ops / sponsor activation"},
    {"rung": "RAPID_READOUT",         "horizon": "T+48h",        "decision": "urgent roadmap / launch go-no-go"},
    {"rung": "WEEK_ONE_FINDING",      "horizon": "T+7d",         "decision": "short-term continuation signal"},
    {"rung": "THIRTY_DAY_PERSISTENCE","horizon": "T+30d",        "decision": "behavioral persistence / retention"},
    {"rung": "NINETY_DAY_LONGITUDINAL","horizon":"T+90d",        "decision": "long-term retention / venture / hiring"},
    {"rung": "MULTI_EVENT_BENCHMARK", "horizon": "multi-event",  "decision": "benchmarking vs prior cohorts"},
]

def ladder_for_deadline(days_until_decision):
    """Which rungs can inform a decision that is `days_until_decision` away. A 90-day report cannot
    inform a decision due in 3 days — do not sell a horizon the deadline can't wait for (Part LXII)."""
    reach = {"LIVE_AGGREGATE_SIGNAL": 0, "RAPID_READOUT": 2, "WEEK_ONE_FINDING": 7,
             "THIRTY_DAY_PERSISTENCE": 30, "NINETY_DAY_LONGITUDINAL": 90, "MULTI_EVENT_BENCHMARK": 365}
    return [r for r in TEMPORAL_LADDER
            if reach[r["rung"]] <= days_until_decision] or [TEMPORAL_LADDER[0]]

WTP_STATUS = "UNKNOWN — willingness-to-pay for every rung must be measured, never assumed"
