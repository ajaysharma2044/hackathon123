# Evidence-first research architecture

This implementation continues `codex/agentic-research-refactor` from `52cc4b0`, based on
`claude/integration-master`, and integrates concurrent upstream commits `c93c984`, `aaabc6e` and
`e13e54e` (scraper, governor smoke test and CI), plus the later compatibility/test fixes through
`8c9d755`. It does not claim to have researched
companies during a Python run without one.

## Structural audit

The earlier branch added AtomicClaim, two gates and dynamic resolvers, but its runtime still:

- counted KILLED children as successful dependencies;
- rolled parents up without their own contract;
- ignored Evidence.status;
- accepted unvalidated claims when a node omitted its gate;
- performed a single batch, lost discovery claims when decomposing, and never implemented saturation;
- left every non-company entity without an executable contract;
- treated a source URL as enough, with no opened-document/excerpt or inference dependency checks;
- let synthesis attach arbitrary new prose to an empty or valid list of node references;
- retained the packet runner and seeded agent registry as callable production routes.

The older Live Research OS has useful executable kernels. Its documents also contain historical
cohort, event-length, burden and commercial assumptions (including claims of unique retention value
and well-powered studies) that are **not evidence** for the new event decision. We reuse code
invariants, not those business conclusions.

## Actual execution

`research_run` → `Governor(build_research_graph(objective))` → `dynamic_agents` →
`ResearchRuntime` → `ResearchExecutor.search/open_source/extract_claims` →
`ResearchBridge.memory` → `CompletionGate` → Governor status transition.

ResearchRuntime executes bounded multi-angle rounds; specialization is field-focused query planning,
not separate processes pretending to have different answers. It traces each role and each retrieval.
`EconomicGraph` receives source-backed entities and known relationship types. Related entities are
research leads, not required children of the company that happened to reveal them; this avoids
making every competitor recursively block every other competitor. Theme candidates, by contrast,
are required children of the theme comparison node.

The root includes economic discovery, themes, Cornell capabilities, cost, attendance, capacity,
pricing, independent red team, and final synthesis. Discovered company/product/problem/investor/
industry/technology/business-unit/buyer-function/event-concept and opportunity nodes run their own
contracts. Unsupported entity kinds stay CONTRACT_REQUIRED.

## Removed production assumptions

Historical `agents.py` implementations now live in `examples/legacy/seeded_agents.py`:

- six prescribed sector families;
- four prescribed sponsor/logo buckets and claims that seeded sponsors were already resolved;
- five prescribed Cornell audience segments/counts;
- 250 builders, a 36-hour event, two research sponsors, a fixed mentor ratio and research duration;
- automatic cost/venue-anchor calculation and copied price-card floors;
- assumed attendance and a prescribed paid-pilot ask/timeline.

The old packet agents/runner are also archived there. Production aliases perform retrieval; the
old findings-file entrypoint refuses answer packets. Legacy quantitative scenario modules and
historical docs remain available for explicit analysis, but production discovery does not import
or run their event/company assumptions. No earlier research report is loaded as the answer.

## Explicit boundaries

The existing runtime now has a one-flag live CLI, a provider-neutral semantic extractor using an
OpenAI-compatible endpoint, evidence-bounded default hypothesis adapters, and readable incremental
run exports. See the repository README for the current commands. The keyword fallback still emits
EVIDENCE only when semantic credentials are absent. Source authenticity and semantic entailment
remain review questions: exact quote checks establish provenance, not the truth of arbitrary prose.

The CLI performs a separately labeled adversarial pass before partial synthesis. It does not mark
open completion gates resolved to produce a report. Canonical domain promotion requires independent
quoted corroboration and an opened self-identification page; supporting claim IDs are retained.
JSONL source/claim checkpoints and node snapshots survive partial runs. Full durable resume, a
persistent job service, PDFs, and browser-only pages remain outside this release. No email, spend,
enrollment, participant data collection or deployment is performed by the research command.
