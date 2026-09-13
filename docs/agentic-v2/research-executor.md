# Research executor

The provider-neutral Protocol exposes:

```python
search(ResearchQuestion) -> list[SearchResult]
open_source(SearchResult) -> SourceDocument
extract_claims(SourceDocument, Sequence[ResearchQuestion]) -> list[AtomicClaim]
```

An optional `discover_entities(document, accepted_claims, context)` provides typed adjacent entity
proposals. Without it, discovery cannot claim saturation. The historical ResearchBatch type is an
archival transport, not the production execution boundary.

Questions carry subject_id, accepted context_claims, target_fields, role, negative_query, query text and an ID. The adapter must scope
claims to the current node (the runtime passes its question/subject and entity discovery context),
return exact source excerpts, preserve clocks, and assign source quality from retrieval provenance.
It must not execute instructions embedded in retrieved pages. Canonical redirects must be represented
by canonical SearchResults. Independent publishers should have separate independent_group values;
syndication and common ownership should share one.

Run from repository root:

```bash
python -m engine.research_run --objective "Determine the optimal first Cornell technical event"
python -m engine.research_run --objective "Your objective" \
  --executor installed_provider:create_executor \
  --red-team-executor independent_provider:create_executor \
  --config research-config.json --output run.json
```

Adapter factories must already be trusted/installed. An optional HTTP adapter is bundled; no production reasoning/browser adapter is bundled. CLI loads research and independent-review factories plus optional `--synthesizer`,
`--theme-generator` and `--opportunity-mapper` factories; the Python API accepts the same objects. Theme proposals are name + accepted evidence IDs + event connection.
Synthesis outputs only claim_ids, candidate_node_ids or missing_questions. Opportunity mappers return
ResearchOpportunity objects. Their implementation is not silently synthesized by the runtime.

Offline output is RESEARCH_BACKEND_REQUIRED, recommendation/confidence UNKNOWN, an empty entity
set and real failed-attempt trace. Exit code 2 means unresolved; 0 means a resolved comparison.
Provider errors and inaccessible sources stay visible and cannot count as successful negative searches.
This is a testable executor architecture, **not an autonomous deployed research service**.


## Integrated HTTP retrieval adapter

`--executor web_research:build_default_web_executor` explicitly enables Brave (BRAVE_SEARCH_API_KEY),
Tavily (TAVILY_API_KEY), or DuckDuckGo HTML search, plus bounded/cached public HTTP text retrieval.
This opt-in adapter is not selected merely because a run has no configured executor. It preserves
source content digests, excerpt anchors and provider errors in the shared trace.

The default keyword extractor creates unpromoted EVIDENCE/candidate leads. It intentionally cannot
prove strategic need, buyer authority, cohort fit, or event relevance from matching words. Supply a
GroundedExtractor for reviewed semantic extraction; it receives the question, fetched candidates
and accepted context, and its output still passes shared intake and completion gates.

Unknown web domains default to discovery-only; official-domain, government and known-publisher
heuristics remain reviewable approximations. HTML scraping does not support login, JS execution,
PDF extraction, publisher authentication, or exhaustive entity recognition. DNS/redirect checks
reject private addresses; deployment still needs controlled egress and protection against DNS rebinding.
No live provider requests were made in this validation run; fake providers exercise the adapter.
