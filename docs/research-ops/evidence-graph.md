# Evidence Graph — claims trace to evidence (Part XXVII)

This is the layer that lets Event 1 pass the test the master doc sets
([live-research-os.md](live-research-os.md)): *can we hand a paying client an aggregate, honestly
caveated, potentially-negative finding — traceable to the evidence AND to the evidence against it?*
The evidence graph is the structural machinery that makes "yes" checkable rather than promised.

> **A client-facing claim must enumerate BOTH the evidence for it and the evidence against it**, and
> it cannot become a published Finding until a deliberate disconfirmation search has actually been
> run. This is Invariant 2 of the schema and the single defence against a research operation that
> "finds something" every weekend because it only ever looked for confirmation.

Schema: `claim` · `claim_evidence` · `negative_case` · `recommendation` in
[`006_live_research.sql`](../../schema/006_live_research.sql). Kernel:
[`evidence_graph.py`](../../engine/evidence_graph.py).

## The graph

```
                    ┌──────────────── SupportingEvidence (polarity = SUPPORTS)
                    │
   Claim ───────────┤                                        ┌─► Interpretation (hedged: assoc. not cause)
   (statement)      │                                        │
                    │                                        ▼
                    └──────────────── ContradictoryEvidence  Confidence  LOW | MED | HIGH
                                       (polarity = CONTRADICTS)   │         (starts LOW; a CONTRADICTS
                                              │                   │          item caps it — see below)
                                              ▼                   ▼
                                        NegativeCase search ──► [PROMOTION GATE] ──► Finding
                                        (disconfirming Q +                              │
                                         searched segment +                            ▼
                                         found: T/F/open)                      Recommendation
                                                                               (DecisionImplication;
                                                                                rests on claim/finding)
```

`claim_evidence` stores supporting and contradictory evidence in **one signed table** (`polarity ∈
{SUPPORTS, CONTRADICTS}`), each row anchored to a real raw source — an `observation`, an
`evidence_event`, an `interview_excerpt`, or a `mentor_interaction`. There is no separate "good
evidence" table that quietly omits the inconvenient rows; the contradiction is a first-class citizen
in the same structure as the support.

## A worked illustrative claim (all values illustrative)

```
CLAIM  c-0191
  statement:      "Authentication friction is associated with early abandonment among first-time users"
  interpretation: "associational, not causal; first-time-founder segment; Product-X auth specifically"
  confidence:     MED        (started LOW; raised on support, then capped — see note)
  status:         SUPPORTED  (not yet promoted to Finding)
```

Evidence enumerated on the claim:

```
 polarity     source kind          ref     note
 SUPPORTS     observation          obs:177 team Kestrel blocked on auth at hour 6 (BLOCKER node)
 SUPPORTS     observation          obs:210 team Merlin: same blocker, then SWITCH to competitor
 SUPPORTS     interview_excerpt    exc:88  "we gave up on the login flow and used something else"
 SUPPORTS     evidence_event       ev:2410 3 first-time-founder teams' final repos drop the Product-X dep
 SUPPORTS     mentor_interaction   mi:61   repeated auth help requests clustered in first-time segment
 CONTRADICTS  observation          obs:181 team Kestrel hit the SAME blocker and did NOT abandon
 CONTRADICTS  evidence_event       ev:2460 2 experienced teams cleared auth in <10 min, no friction
```

N field observations + participant statements + mentor interactions + switching events + final repos
removing the dependency all point the same way — **and so does the Kestrel counterexample pointing
the other way.** Both are on the claim. (This is the same Kestrel/Merlin pair from
[team-trajectories.md](team-trajectories.md): one friction, two arcs.)

### The alternative explanations (why the association may not be what it looks like)

Before this claim may be promoted, the competing readings must be written down and searched —
because each would explain the same pattern *without* "auth friction causes abandonment" being true:

```
 PRIOR FAMILIARITY    abandoners were first-timers who'd never used ANY such API; auth is incidental
 MENTOR AVAILABILITY  Kestrel survived because a mentor was free (mi:54); abandonment tracks mentor
                      queue depth, not auth difficulty
 TEAM SKILL           abandoning teams were weaker across the board; they'd have stalled anywhere
 PROJECT FIT          abandoners picked projects that needed auth deeply; survivors could route around it
```

Each becomes a `negative_case` row with a `disconfirming_question` and a `searched_segment`. Until at
least one such search is **resolved** (`found` set true/false, not left open), the claim cannot be
promoted at all.

## The promotion gate (`can_promote`)

`Claim.can_promote()` in [`evidence_graph.py`](../../engine/evidence_graph.py) returns `(ok, reason)`
and refuses promotion unless **all** of these hold:

```
 1. ≥1 SUPPORTING evidence item            else → "no supporting evidence"
 2. a negative-case search was PLANNED     else → "no negative-case search was even planned
                                                   (confirmation-bias guard)"
 3. that search was actually RESOLVED       else → "negative-case search is still open — run it
    (some negative_case.found is not null)         before promoting"
 4. if a counterexample was FOUND, confidence else → "a disconfirming case exists but confidence
    is NOT still HIGH                               is still HIGH — lower it first"
```

And contradictory evidence **caps confidence mechanically**: `add_evidence()` drops a HIGH claim to
MED the moment a `CONTRADICTS` item is attached, and it cannot return to HIGH without an explicit
re-justification. So confidence is never a free-floating adjective — it is constrained by what the
evidence table actually contains. A claim only becomes a `finding` (through the 001 Finding gate,
via `claim.promoted_to_finding`) once the gate is green; a `recommendation` then rests on that
`finding_id` (or, clearly marked, an in-progress `claim_id`) and **never floats free**
(`recommendation` CHECK `num_nonnulls(finding_id, claim_id) >= 1`).

## End-to-end traceability (`trace`)

`Claim.trace()` returns the full provenance — supporting refs, contradicting refs, and the
disconfirmation searches — so any claim is auditable from the top down:

```
RawQuote ─► Observation ─► Code ─► Theme ─► Claim ─► (Finding) ─► Recommendation
   ▲                                          │
   └───────────── trace() walks back down ────┘   every client-facing claim resolves to the exact
                                                   raw rows it rests on — and those it contradicts
```

This is what "every client-facing claim remains traceable end-to-end" means concretely: a client can
be handed a Recommendation, follow its `finding_id` to the Finding, the Finding to the Claim, the
Claim's `claim_evidence` to the signed raw rows, and each raw row back to the immutable quote or
telemetry event it came from — *including the rows that argue against the claim.* Nothing in the
chain is asserted without a pointer to what it rests on, and consent is still enforced at query time
from the 001 ledger, so a revoked participant's evidence drops out of the trace without anything
being deleted ([research-data-model.md](../research-data-model.md)).

## The three tables, and why each exists

| Table | Holds | Why it is structured this way |
|---|---|---|
| `claim` | statement · interpretation · confidence · status · `promoted_to_finding` | confidence is a **labeled field** (LOW/MED/HIGH), never an unbacked adjective; a claim starts LOW and PROPOSED |
| `claim_evidence` | signed (`SUPPORTS`/`CONTRADICTS`) anchors to raw | supporting and contradictory in **one table** so a claim literally cannot be stored without room for its own disconfirmation |
| `negative_case` | disconfirming question · searched segment · `found` | makes the disconfirmation search a **recorded act**, not a claimed intention — `found = null` means the search is still open and the gate stays shut |

## What the evidence graph guarantees

- No Finding without supporting evidence **and** a completed disconfirmation search.
- No confidence number that the evidence table does not support (a contradiction caps it).
- No recommendation without a claim or finding under it.
- No claim a client cannot trace, row by row, down to raw — support and contradiction alike.

It is the honest-reporting invariant made executable. The war room can move fast on
[analytic-memos.md](analytic-memos.md) and provisional [qualitative-coding.md](qualitative-coding.md)
themes during the event; but the moment something is about to be told to a paying client as true,
it passes through this gate — or it does not get told.
