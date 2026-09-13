# Agentic Research Refactor v2

## Why this refactor exists

The previous discovery layer had two structural failure modes:

1. many specialized resolver names delegated to the same packet reader, so the system looked more agentic than it was;
2. `NEEDS_RESEARCH`, `QUOTE`, and `PRIMARY` were treated as terminal by dependency roll-up, so an incompletely researched branch could make a parent look resolved.

It also embedded discovery assumptions directly in Python: fixed industry seeds, fixed sponsor seeds, fixed participant scenarios, and conclusion-shaped pipelines. That is useful for a deterministic demo, but it is the wrong architecture for open-ended research.

## New invariant

> A model may propose questions and synthesize accepted evidence. It may not create factual state merely by producing plausible prose.

The research path is now designed around:

`objective -> research plan -> live retrieval -> atomic claims -> source quality -> contradiction search -> completion gate -> synthesis`

## What is generic now

`engine/research_contracts.py`
- epistemic states: FACT / INFERENCE / HYPOTHESIS / UNKNOWN / PRIMARY_VALIDATION_REQUIRED
- source tiers
- atomic claims
- deterministic completion gates
- generic company and theme contracts

`engine/research_executor.py`
- tool-agnostic protocol for live research
- returns claims and discovered entities, never a pre-resolved business conclusion
- null executor leaves work open rather than hallucinating

`engine/research_planner.py`
- turns missing evidence fields into research questions
- broad discovery is based on economic signals, not a list of sectors/logos

`engine/dynamic_agents.py`
- discovers entities from research results
- spawns company/entity nodes dynamically
- company nodes can resolve only after the company completion gate passes
- themes require an injected evidence-bounded generator
- final synthesis is evidence-only and may not cite unresolved nodes

`engine/agent_os.py`
- open research states are no longer terminal success
- primary validation is explicitly distinct from resolution

`engine/governor.py`
- objective-driven graph instead of six industries/four sponsor seeds
- deterministic completion-gate enforcement

## Research executor contract

A production research adapter should wrap whichever live retrieval system is actually available (browser, ChatGPT web, Codex browser, MCP, etc.). It must return:

- exact query strings run;
- source URLs opened;
- source-backed `AtomicClaim` objects;
- newly discovered entities;
- notes/limitations.

It must not return `"Genspark is a great sponsor"` as a primitive.

It can return claims such as:

- FACT: company raised X; source = financing announcement;
- FACT: company is hiring role Y; source = careers page;
- INFERENCE: hiring pattern suggests capability gap; supporting claim IDs = ...;
- HYPOTHESIS: a Cornell event may answer question Q;
- PRIMARY_VALIDATION_REQUIRED: buyer would pay $25K.

## Company completion contract

A company does not resolve until evidence covers, at minimum:

- identity;
- current initiative;
- financial capacity;
- product/business model;
- strategic need;
- internal capability;
- why external research/event access is incremental;
- a question the event can actually answer;
- buyer function;
- substitutes;
- activity -> signal -> artifact -> buyer-decision value chain;
- counterevidence.

A company can be commercially interesting while still remaining `PRIMARY_VALIDATION_REQUIRED` on willingness to pay. That is expected and preferable to inventing WTP.

## Hardcoding policy

Runtime source code should not enumerate:

- target sectors;
- target company logos;
- a fixed winning theme;
- a fixed participant count presented as fact;
- fixed sponsor archetypes as exhaustive;
- magic WTP numbers presented as evidence.

Allowed configuration includes:

- source-quality rules;
- generic research fields;
- epistemic states;
- privacy/compliance boundaries;
- scenario parameters explicitly labeled scenario/assumption;
- query templates over unresolved fields.

Seeds may exist only as **optional experiments** in fixture/config files, never as the discovery universe.

## Next P0 work

1. Implement a real production `ResearchExecutor` adapter for the runtime actually used by Codex/Astra.
2. Convert ResearchBridge from conclusion packets into an append-only atomic evidence cache.
3. Add type-specific contracts for industry, product, investor, buyer, R&D question, data/research module, and event theme.
4. Add contradiction and source-diversity gates, including independent-source counting rather than URL count.
5. Add saturation logic: continue discovery rounds until marginal Tier-S/A entities stop appearing.
6. Add an agent trace recording questions, queries, sources, claims, spawned nodes, rejected claims, gate failures, and status transitions.
7. Fuse the older Live Research OS into theme/company evaluation: every candidate event should be evaluated for natural capture surfaces, participant burden, research validity, R&D value, recruiting value, and commercial deliverables.
8. Keep `WTP = UNKNOWN / PRIMARY_VALIDATION_REQUIRED` until a real priced ask, LOI, pilot, sponsorship, or contract exists.

## The final architecture

```text
Objective
  -> discovery research
  -> discovered economic families / organizations / products / problems
  -> type-specific deep research
  -> atomic evidence graph
  -> contradiction search
  -> deterministic completion gates
  -> event/theme candidates
  -> participant-value + live-research/data/R&D evaluation
  -> company universe
  -> company deep dives
  -> sponsor/research/R&D/talent value chains
  -> cost/attendance/capacity scenarios
  -> red team
  -> evidence-only synthesis
  -> primary validation queue
```

The system should get *more uncertain* when evidence is weak, not more eloquent.
