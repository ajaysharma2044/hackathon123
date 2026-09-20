# Run 2 — Technical Run Log

## Execution boundary

This run used:

- GitHub connector for the private repository state and file inspection;
- web research for current public evidence;
- local Python/container execution for the new graph/bridge/commercial primitives and tests.

The container could not clone the private GitHub repository over the network. Therefore:

- the prior remote commit's claim of **446 passed / 0 failed** is recorded but was not independently rerun;
- unpushed local Cowork worktree/untracked artifacts could not be inspected;
- new Run-2 code was tested independently before being written back to GitHub.

No emails, sponsor outreach, purchases, contracts, venue bookings or other external commercial actions were executed.

## Remote reconciliation

```text
REMOTE_BRANCH       claude/integration-master
REMOTE_HEAD         cdca9a0760039d9d10e7e4dda2644ef1046f6962
SCHEMA_MAX          013_agentic.sql
LEGACY_AGENT_COUNT  15
LEGACY_GAP          economic_battle / company_research / topic_synthesis -> NEEDS_RESEARCH
LEGACY_EXPANSION    six hardcoded industry seeds + four sponsor seeds
```

`Decision Grid`, `live_findings.py` and `decision_arena.py` were not found on the inspected remote canonical branch. This says nothing about an inaccessible local Cowork session.

## New code tested

`engine/test_run2_core.py`:

```text
PASS duplicate organizations merge safely
PASS contradictory evidence is preserved
PASS cycles do not infinite-loop
PASS source provenance survives graph propagation
PASS recursive expansion terminates on stop rule
PASS session-assisted sourced evidence resolves
PASS contradictory research is not silently averaged
PASS UNKNOWN cannot silently become numeric
PASS Observed WTP remains UNKNOWN without primary evidence
PASS primary paid pilot can establish observed WTP
PASS cash is distinct from credits and avoided cost
PASS high-paying artificial sponsor mechanic can be rejected
PASS research contamination can reject a sponsor mechanic
PASS substitute parity can kill an opportunity
PASS anchor product absence meaningfully weakens a theme
PASS poor hackathon fit kills a giant market

16 passed, 0 failed
```

## Actual Run-2 system execution

Input: `docs/run-2/session_findings.json`

- 48 sourced/session-synthesis findings ingested.
- 10 economy-wide industry-family children dynamically created by `industry_expansion_live`.
- 10 economic-battle nodes resolved with ordinal evidence packets.
- Cornell archaeology + capability intersection resolved.
- 30-theme frontier resolved.
- 3 finalists resolved.
- product economy, organization universe, account value, multiplier, conflicts, cost, pricing, attendance, capacity and in-kind packets resolved.
- final synthesis + falsification resolved.

Output counts:

```json
{"RESOLVED": 34}
```

Key output assertions:

```text
winner                    GridCompute
total_event_cost          UNKNOWN
observed_wtp              UNKNOWN
```

This is intentional: a node can resolve to a structured conclusion that a quantity is unknown. “Resolved node” does not convert unknown business facts into numbers.

## Product graph

`product-ecosystem-graph.json` was generated with the new `EconomicGraph`:

```text
38 nodes
62 typed edges
0 silently overwritten contradictions
```

The graph includes EconomicProblem → Decision → Product → Infrastructure → Organization relationships and 3+ meaningful recursive layers.

## Known implementation limitation after this run

Legacy `cost_agent` / `cornell_scenario.py` still exists and historically labels an aggregate as grounded even though $3,000 venue and $12,000 ops are hardcoded while the file says large halls/ops are quote-pending. The Run-2 pipeline does **not** inherit that number: `cost_v2.total_event_cost = UNKNOWN`. A follow-up cleanup should deprecate the legacy aggregate or refactor it to a status-preserving cost tree without breaking older interfaces.
