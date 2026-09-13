# Grounding: real data on the nodes, not assumptions

The model is only as honest as its inputs. This layer replaces every assumed number with a **sourced**
one, and marks the ones that *cannot* be sourced from the web so they're never mistaken for fact.

## Two files

- **[`engine/grounding.py`](../engine/grounding.py)** — the registry. Every model input is a node with a
  provenance status:
  - `SCRAPED` — a published web value, with URL + observed date.
  - `QUOTE` — real, but behind a "contact us" (needs one email; the node names the exact door).
  - `PRIMARY` — exists **nowhere online**; only a human commitment resolves it (a sponsor/buyer "yes").
- **[`engine/node_scraper.py`](../engine/node_scraper.py)** — the **autonomous agent**. It goes to the web
  itself (pure `urllib`, no LLM in the loop), pulls live values into the registry, and refreshes **only
  stale nodes** — staleness decided by [`freshness.py`](../engine/freshness.py), the same decay engine the
  rest of the system uses. It knows its limits: it never assigns a value to a `QUOTE`/`PRIMARY` node,
  it reports them.

```
PYTHONPATH=. python3 node_scraper.py          # refresh stale nodes from the web, print the report
PYTHONPATH=. python3 node_scraper.py --force  # re-scrape everything now
```

A live run pulls Cornell's real catering prices (scrambled eggs **$2.95**, hard-boiled **$1.20**,
beverage break **$4.75**, snack add-on **$8.50**) straight off the menu pages, and reports the 5 nodes
it deliberately did not touch (venue quote, dinner quote, sponsor raise, buyer close-prob, buyer WTP).

## What this can and cannot do — honestly

| Side | Nodes | Resolver |
|---|---|---|
| **Cost** | catering, venue, comps, rate cards | mostly **SCRAPED** now; the rest **QUOTE** (one email) |
| **Revenue** | your sponsor raise, buyer willingness-to-pay | **PRIMARY** — not on the web anywhere; only a sponsor call / paid pilot |

The cost side can be made fully real by the agent + a couple of emails. The revenue side **structurally
cannot** be scraped — *what a specific sponsor will pay you is not published data*. So the grounded model
([`cornell_scenario.py`](../engine/cornell_scenario.py)) collapses the whole question to **one number you go
get** — the actual raise — instead of a pile of assumptions. Break-even lands at ~$40K on the grounded
Cornell cost of ~$39.7K.

## How it composes

`node_scraper.refresh()` → writes into `grounding.NODES` → `cornell_scenario.py` reads grounded costs →
the quant engine ([`event_optimizer.py`](../engine/event_optimizer.py)) runs the economics. Every value that
flows through carries a provenance tag, so no output is ever cleaner than its evidence.
