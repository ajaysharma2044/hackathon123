"""python3 test_temporal.py — Part-LXXXIV guardrails for the temporal + context + tracing layer."""
from datetime import datetime, timedelta
from capture import EvidenceEvent
import temporal_core as tc
import context_envelope as ce
import episode as ep
import temporal_graph as tg
import state_space as ss
import survival as sv
import freshness as fr
import temporal_voi as tv
import optimal_stopping as ostop
import dynamic_allocation as da
import process_tracing as pt
import trajectory as tj
import compliance
P = F = 0
def ck(n, c):
    global P, F; P += bool(c); F += (not c); print(f"  {'PASS' if c else 'FAIL'}  {n}")

SC = frozenset({"AGGREGATE_RESEARCH"})
def ev(eid, etype, occ, avail=None, subj="p1", payload=None):
    avail = avail or occ
    return EvidenceEvent(eid, etype, subj, occ, occ, avail, SC, False, payload=payload or {})

D0 = datetime(2026, 3, 1, 12, 0)   # event start
def m(mins): return D0 + timedelta(minutes=mins)

# ---- 1. NO FUTURE LEAKAGE -------------------------------------------------------
events = [ev("e1", "EVENT_START", m(0), m(0)), ev("e2", "FIRST_SUCCESS", m(60), m(60)),
          ev("e3", "SELF_REPORT_SWITCH", m(120), m(2880))]   # occurred day0, only available day2
iset = tc.information_set(events, m(200))
ck("information_set excludes not-yet-available events", "e3" not in {e.event_id for e in iset})
ck("information_set includes available events", {"e1", "e2"} <= {e.event_id for e in iset})
try:
    tc.assert_no_future_leakage(events, m(200)); ck("leakage not caught", False)
except ValueError:
    ck("assert_no_future_leakage raises on a future-available event", True)
ck("no leakage when all events are available", tc.assert_no_future_leakage(iset, m(200)))

# ---- 2. SEQUENCE ORDERING (order is a variable) --------------------------------
g = tg.TemporalGraph()
g.add_edge(tg.TemporalEdge("t1", "FAIL", "x", m(10)))
g.add_edge(tg.TemporalEdge("t1", "MENTOR", "x", m(20)))
g.add_edge(tg.TemporalEdge("t1", "SUCCESS", "x", m(30)))
ck("sequence is returned in occurred order", g.sequence("t1") == ["FAIL", "MENTOR", "SUCCESS"])
ms = tg.find_motifs([["FAIL","MENTOR","SUCCESS"]*1, ["FAIL","MENTOR","SUCCESS"]], n=2, min_support=2)
motifs = {x["motif"] for x in ms}
ck("FAIL->MENTOR is a motif; MENTOR->FAIL (reverse) is NOT", "FAIL -> MENTOR" in motifs and "MENTOR -> FAIL" not in motifs)

# ---- 3. DURATION CORRECTNESS (the user's worked example) -----------------------
# blocker 14:03, mentor req 14:17, arrived 14:24, intervention end 14:33, first success 14:47
base = datetime(2026, 3, 1, 14, 0)
typed = [("BLOCK_BEGAN", base.replace(minute=3)), ("MENTOR_REQUEST", base.replace(minute=17)),
         ("MENTOR_ARRIVED", base.replace(minute=24)), ("INTERVENTION_END", base.replace(minute=33)),
         ("FIRST_SUCCESS", base.replace(minute=47)), ("BLOCK_RESOLVED", base.replace(minute=47))]
mets = tc.time_metrics(typed)
ck("BlockedDuration = 44 min", mets["BlockedDuration"] == 44)
ck("MentorWait = 7 min", mets["MentorWait"] == 7)
ck("TimeToRecovery (post-intervention) = 14 min", mets["TimeToRecovery"] == 14)

# ---- 4. POINT-IN-TIME RECONSTRUCTION -------------------------------------------
# a day-30 outcome must be invisible to a submission-time reconstruction
allev = [ev("s0", "EVENT_START", m(0), m(0)), ev("s1", "PROTOTYPE", m(600), m(600)),
         ev("d30", "RETAINED", m(0), m(43200))]   # available only at day 30
recon = ep.reconstruct_episode(allev, "p1", m(0), m(1000), as_of=m(1000))
ck("submission-time episode excludes the day-30 outcome", "d30" not in recon.evidence_links)
ck("submission-time episode includes in-window available events", {"s0", "s1"} <= set(recon.evidence_links))

# ---- 5. FRESHNESS / EVIDENCE DECAY ---------------------------------------------
now = datetime(2026, 9, 12); old = datetime(2026, 1, 1)
ck("a >6-month tool_preference is STALE", fr.freshness("tool_preference", old, now)["status"] == "STALE")
ck("a venue_fact is still FRESH after months", fr.freshness("venue_fact", old, now)["status"] == "FRESH")
ck("decay refuses exponential when half-life ungrounded", fr.decay_weight("venue_fact", old, now)["weight"] is None)
ck("decay applies exponential when half-life grounded", 0 < fr.decay_weight("tool_preference", old, now)["weight"] < 1)

# ---- 6/7. DELAYED OUTCOMES + FOLLOW-UP HORIZON ---------------------------------
before = tv.voi_at(20000, datetime(2026,10,1), datetime(2026,11,1), cost=5000)
after  = tv.voi_at(20000, datetime(2026,12,1), datetime(2026,11,1), cost=5000)
ck("evidence on-time carries decision value", before["decision_value"] == 20000)
ck("evidence past the deadline carries ZERO decision value", after["decision_value"] == 0.0)
ck("info quality is reported separately from timing", after["information_quality"] == 20000)
ck("a 3-day deadline cannot be served by the 90-day rung",
   "NINETY_DAY_LONGITUDINAL" not in {r["rung"] for r in tv.ladder_for_deadline(3)})
ck("a 120-day deadline CAN be served by the 90-day rung",
   "NINETY_DAY_LONGITUDINAL" in {r["rung"] for r in tv.ladder_for_deadline(120)})

# ---- 8. INTERVENTION TIMING (latency + state, not just 'a mentor helped') -------
early = tc.time_metrics([("MENTOR_REQUEST", base.replace(minute=0)), ("MENTOR_ARRIVED", base.replace(minute=3))])
late  = tc.time_metrics([("MENTOR_REQUEST", base.replace(minute=0)), ("MENTOR_ARRIVED", base.replace(minute=40))])
ck("intervention latency is measured and differs by timing", early["MentorWait"] == 3 and late["MentorWait"] == 40)

# ---- 9. STATE RECONSTRUCTION ---------------------------------------------------
counts = ss.transition_counts([["BUILDING","BLOCKED","BUILDING"], ["BUILDING","BLOCKED","PIVOTING"],
                               ["BUILDING","TESTING"]])
mat = ss.transition_matrix(counts, min_observations=3)
ck("dense state row yields probabilities summing to 1",
   abs(sum(v for k, v in mat["BUILDING"].items() if not k.startswith("_")) - 1.0) < 1e-9)
ck("sparse state row returns INSUFFICIENT_DATA, not noise", mat["FORMING"]["_status"] == "INSUFFICIENT_DATA")

# ---- 10. MISSING CONTEXT TOLERATED ---------------------------------------------
empty = ce.context_at([], "p1", m(100))
ck("missing context field is UNKNOWN, never a penalty", empty.get("CurrentBlocker") == "UNKNOWN")
ck("time metric with a missing anchor is None, never fabricated 0",
   tc.time_metrics([("EVENT_START", base)])["TimeToMentor"] is None)

# ---- 11. NO UNSUPPORTED COUNTERFACTUAL -----------------------------------------
ck("single-case counterfactual is NOT_IDENTIFIED",
   pt.counterfactual_options("mentor_routing")["counterfactual"] == "NOT_IDENTIFIED")
ck("counterfactual estimable only with identification",
   pt.counterfactual_options("mentor_routing", "RANDOMIZED")["counterfactual"] == "ESTIMABLE")
tr = pt.trace("retention", ["FAIL","MENTOR","SUCCESS"], "mentor unblocked", supporting=["log"],
              contradicting=["team was already expert"])
ck("process trace surfaces contradicting evidence, not just supporting", "CONTESTED" in tr.confidence_note())

# ---- 12. NO HIDDEN SOCIOECONOMIC / PERSON-QUALITY SCORE ------------------------
for bad in ("advantage_score", "socioeconomic_index", "potential_score"):
    try:
        ce.assert_opportunity_not_scored(bad); ck(f"opportunity scored as {bad}", False)
    except ValueError:
        ck(f"opportunity/context refused as a '{bad}'", True)
try:
    ce.vet_starting_context(["prior_tool_experience", "income"]); ck("sensitive starting field allowed", False)
except ValueError:
    ck("starting-context vetting refuses a sensitive field (income)", True)
try:
    compliance.assert_not_a_person_score("hireability_from_trajectory"); ck("person score allowed", False)
except ValueError:
    ck("a capability trajectory may never be turned into a person score", True)
ck("project archetype is labelled a project shape, not a personality",
   "personality" in tj.classify_archetype(tj.trajectory(["FORMING","DONE"]))["_note"].lower())

if __name__ == "__main__":
    import sys; print(f"\n{'='*54}\n{P} passed, {F} failed"); sys.exit(1 if F else 0)
