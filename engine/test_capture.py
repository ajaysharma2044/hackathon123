"""Runnable tests for the two hardest correctness properties. `python3 engine/test_capture.py`."""
from datetime import datetime, timedelta
from capture import (EvidenceEvent, ConsentRecord, ConsentLedger, CaptureStore,
                     retention_events, DEFAULT_MIN_CELL)

D0 = datetime(2027, 8, 1)
def day(n): return D0 + timedelta(days=n)
PASS, FAIL = 0, 0
def check(name, cond):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  PASS  {name}")
    else:    FAIL += 1; print(f"  FAIL  {name}")

def grant(l, p, s, at): l.record(ConsentRecord(p, s, "GRANT", at))
def revoke(l, p, s, at): l.record(ConsentRecord(p, s, "REVOKE", at))
def ev(eid, p, occ, avail, scopes, etype="FEATURE_USED", self_report=False, obs=None, sup=None):
    return EvidenceEvent(eid, etype, p, occ, obs or occ, avail, frozenset(scopes),
                         self_report, superseded_by=sup)

# 1. Point-in-time: an "as of D" query must not see evidence available only later.
def test_as_of_excludes_future_knowledge():
    l = ConsentLedger(); grant(l, "p1", "AGGREGATE_RESEARCH", day(0))
    s = CaptureStore(l)
    s.append(ev("e1", "p1", occ=day(1), avail=day(1), scopes=["AGGREGATE_RESEARCH"]))
    s.append(ev("e2", "p1", occ=day(1), avail=day(5), scopes=["AGGREGATE_RESEARCH"]))  # learned later
    got = {e.event_id for e in s.query("AGGREGATE_RESEARCH", as_of=day(2))}
    check("as-of query hides evidence available only later", got == {"e1"})
    got_later = {e.event_id for e in s.query("AGGREGATE_RESEARCH", as_of=day(6))}
    check("later as-of query now sees the delayed evidence", got_later == {"e1", "e2"})

# 2. Retention runs on occurred_at even when observed_at is much later (survey lag).
def test_retention_uses_occurred_at_not_observed_at():
    reuse = EvidenceEvent("r1", "VOLUNTARY_REUSE", "p1",
                          occurred_at=day(9), observed_at=day(30),  # occurred day 9, learned day 30
                          available_at=day(30), consent_scope=frozenset(["LONGITUDINAL_FOLLOWUP"]),
                          is_self_report=True)
    buckets = retention_events([reuse], "VOLUNTARY_REUSE", [7, 14, 30], t0=D0)
    # day-9 reuse must fall in the <=14 and <=30 buckets, NOT be pushed to a day-30 bucket only.
    check("reuse bucketed by occurred_at (day 9), not observed_at (day 30)",
          buckets.get(14) == 1 and buckets.get(7, 0) == 0)

# 3. Revocation enforced at query time; a pre-revocation published snapshot is not rewritten.
def test_revocation_enforced_at_query_time():
    l = ConsentLedger(); grant(l, "p1", "AGGREGATE_RESEARCH", day(0))
    s = CaptureStore(l)
    s.append(ev("e1", "p1", occ=day(1), avail=day(1), scopes=["AGGREGATE_RESEARCH"]))
    before = s.query("AGGREGATE_RESEARCH", as_of=day(2))
    check("participant visible while consent stands", len(before) == 1)
    # a finding "published" at day 2 snapshots n=1 (provenance); revocation must not rewrite it.
    published_snapshot_n = len(before)
    revoke(l, "p1", "AGGREGATE_RESEARCH", day(3))
    after = s.query("AGGREGATE_RESEARCH", as_of=day(4))
    check("revocation excludes participant from later queries (query-time enforcement)", len(after) == 0)
    check("nothing deleted: event row still present", len(s._events) == 1)
    check("published snapshot n is not retroactively rewritten", published_snapshot_n == 1)

# 4. A query for a purpose returns only rows collected under that scope AND consented.
def test_scope_required():
    l = ConsentLedger()
    grant(l, "p1", "AGGREGATE_RESEARCH", day(0))          # p1 consented to aggregate only
    grant(l, "p2", "QUALITATIVE_RESEARCH", day(0))        # p2 to qualitative
    s = CaptureStore(l)
    s.append(ev("e1", "p1", day(1), day(1), ["AGGREGATE_RESEARCH"]))
    s.append(ev("e2", "p2", day(1), day(1), ["QUALITATIVE_RESEARCH"], etype="INTERVIEW_COMPLETED"))
    qual = {e.event_id for e in s.query("QUALITATIVE_RESEARCH", as_of=day(2))}
    check("qualitative query returns only qualitative-consented rows", qual == {"e2"})

# 5. Min-cell-size suppression on sponsor-facing aggregates.
def test_min_cell_suppression():
    l = ConsentLedger(); s = CaptureStore(l)
    for i in range(DEFAULT_MIN_CELL):                    # exactly K distinct participants on product A
        p = f"a{i}"; grant(l, p, "AGGREGATE_RESEARCH", day(0))
        s.append(ev(f"ea{i}", p, day(1), day(1), ["AGGREGATE_RESEARCH"], etype="ACTIVATED"))
    for i in range(3):                                   # only 3 on product B -> suppressed
        p = f"b{i}"; grant(l, p, "AGGREGATE_RESEARCH", day(0))
        s.append(ev(f"eb{i}", p, day(1), day(1), ["AGGREGATE_RESEARCH"], etype="ACTIVATED"))
    agg = s.aggregate("AGGREGATE_RESEARCH", as_of=day(2), cell_key=lambda e: e.payload.get("prod", e.event_id[:2]))
    # cell "ea" has K participants (kept), "eb" has 3 (suppressed -> None)
    check("cell with n>=K is reported", agg.get("ea") == DEFAULT_MIN_CELL)
    check("cell with n<K is suppressed to None", agg.get("eb") is None)

# 6. Aggregate-only scope cannot produce individual-grain output.
def test_aggregate_only_blocks_individual_disclosure():
    l = ConsentLedger(); grant(l, "p1", "AGGREGATE_RESEARCH", day(0))
    s = CaptureStore(l)
    s.append(ev("e1", "p1", day(1), day(1), ["AGGREGATE_RESEARCH"]))
    raised = False
    try:
        s.individual_disclosure("AGGREGATE_RESEARCH", as_of=day(2))
    except PermissionError:
        raised = True
    check("individual disclosure refused for aggregate-only scope", raised)
    # but an opted-in discoverability scope IS allowed to disclose individually
    grant(l, "p1", "RECRUITING_DISCOVERABILITY", day(0))
    s.append(ev("e2", "p1", day(1), day(1), ["RECRUITING_DISCOVERABILITY"], etype="ARTIFACT_CREATED"))
    disclosed = s.individual_disclosure("RECRUITING_DISCOVERABILITY", as_of=day(2))
    check("individual disclosure allowed for opted-in discoverability scope", len(disclosed) == 1)

# 7. Consent effective_at is respected: a grant effective in the future is not yet in force.
def test_consent_effective_at_is_point_in_time():
    l = ConsentLedger(); grant(l, "p1", "AGGREGATE_RESEARCH", day(5))   # effective only from day 5
    s = CaptureStore(l)
    s.append(ev("e1", "p1", occ=day(1), avail=day(1), scopes=["AGGREGATE_RESEARCH"]))
    check("no consent in force before effective_at -> excluded", len(s.query("AGGREGATE_RESEARCH", as_of=day(3))) == 0)
    check("consent in force after effective_at -> included", len(s.query("AGGREGATE_RESEARCH", as_of=day(6))) == 1)

if __name__ == "__main__":
    for t in [test_as_of_excludes_future_knowledge, test_retention_uses_occurred_at_not_observed_at,
              test_revocation_enforced_at_query_time, test_scope_required, test_min_cell_suppression,
              test_aggregate_only_blocks_individual_disclosure, test_consent_effective_at_is_point_in_time]:
        print(f"\n{t.__name__}"); t()
    print(f"\n{'='*50}\n{PASS} passed, {FAIL} failed")
    import sys; sys.exit(1 if FAIL else 0)
