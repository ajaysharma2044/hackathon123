# The temporal event graph

`engine/temporal_graph.py`. Every edge is timestamped, so the graph answers questions a static graph
cannot.

```
Team A  USED         Product X   [14:12 → 18:44]
Mentor  HELPED       Team A      [17:51 → 18:07]
Team B  RECOMMENDED  Product Y   [18:12]
Team A  SWITCHED_TO  Product Y   [18:44]
```

## Sequence is a variable

`FAIL → MENTOR → SUCCESS`, `MENTOR → TRY → FAIL`, and `FAIL → PEER → SWITCH → SUCCESS` share the same
nouns but tell **different causal stories**. `sequence(entity)` returns the ordered event-type chain;
`find_motifs(sequences, n, min_support)` mines recurring ordered n-grams with support. Crucially,
`FAIL → MENTOR` is a motif and its reverse is not — order is preserved and matters.

**Order is not causation.** Every motif result carries that caveat, and `motif_outcomes` attaches
outcomes *and negative cases* separately — never an effect estimate.

## Window and trajectory queries

- `window_before(target_rel, minutes)` — *"show the N minutes before every database switch."*
  For each `SWITCHED_TO`, it returns the preceding edges within the window (marked "proximity is not
  causation"). This is the query behind *"show all teams whose architecture changed within an hour of a
  mentor intervention."*
- `trajectory(entity)` — the entity's whole ordered evolution.

Example product insight the graph makes reachable (once data exists): Product A produces
`DocsFailure → MentorRequest → VendorRescue → Retention`, while Product B produces
`DocsFailure → Switch`. Same trigger, opposite outcome — a real product-research finding, stated as a
pattern with negative cases, not a proven cause.
