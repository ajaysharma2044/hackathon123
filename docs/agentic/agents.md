# The agents

15 agents in [`agents.py`](../../engine/agents.py), each declaring a permission. Three classes:

## Autonomous now (reuse real engines / real data)

| Agent | Reuses | What it resolves |
|---|---|---|
| `grounding` | node_scraper + grounding | scraped cost inputs (refreshes stale ones live) |
| `cost` | cornell_scenario + grounding | grounded event cost ($39,732 from real Cornell menu prices) |
| `pricing` | grounding rate cards | ask-price recommendation (LF $150K syndicated / $25K Tier-A / $27 panel floor) |
| `event_design` | event_optimizer (mechanism engine) | the event design's experience + research-info scores |
| `portfolio_optimizer` | cost node | break-even sponsorship identity |
| `cornell_capability` | cornell-audience-map (KNOWN counts) | decomposes into 5 capability segments; buildable-fraction → PRIMARY |
| `industry_expansion` | seed set | decomposes into 6 economic-battle nodes |
| `sponsor_discovery` | top-prospects.md (verified) | decomposes into seed companies (Jump/IMC, Citadel, ...) |
| `attendance` | cornell-audience-map | accessible-pool estimate; yield-rate → PRIMARY |
| `falsifier` | STATE.md discipline | emits the falsification test as the highest-VOI next action |

## Hook-backed cognition (Defer NEEDS_RESEARCH; seed from repo, never fabricate)

`economic_battle`, `company_research`, `topic_synthesis` — these need a live web/LLM research step to do
their real job (sweep an industry's pain, research a firm's business unit + buyer + budget, synthesize
the topic). They resolve seeded nodes from repo evidence and `Defer(NEEDS_RESEARCH)` the rest. Plugging
in live cognition (a subagent or the web tools) is the next build.

## External action (permission-gated)

`outreach` (`NEEDS_APPROVAL`) — would email a sponsor or a venue for a quote. It only ever **proposes**;
the Governor blocks it for human approval and never sends autonomously.

## The one-button Cornell run

`governor.run_cornell()` builds the pipeline goal graph and runs it. A live run today:

- **Resolves 18 nodes autonomously** — grounded cost, rate-card pricing, event design, break-even,
  the 5 capability segments, 4 seed sponsors.
- **Recursively decomposes** capability→5, industries→6, sponsors→4.
- **Leaves 9 NEEDS_RESEARCH + 2 PRIMARY**, honestly, ranked by VOI — the **#1 next action is the
  falsification test** (a $5–15K paid pilot), then topic synthesis, then the Tableau-locked buildable
  fraction.
- **Gates 1 external action** (outreach) for approval.

That is the `UNKNOWN → VOI → task → evidence → update` loop end to end: the system does everything it
can from real data and machinery, and tells you the highest-value thing only a human can do next.
