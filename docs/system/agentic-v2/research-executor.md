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
python -m engine.research_run --company "Genspark" --live --output runs/genspark
python -m engine.research_run --objective "Discover company research questions for Cornell builders" \
  --live --max-companies 10 --output runs/cornell
```

The README documents credentials, budgets, and exact setup commands. Advanced trusted adapter
factories remain optional overrides. `--live` selects Brave, Tavily or DuckDuckGo, configures
`SemanticGroundedExtractor` when `RESEARCH_LLM_API_KEY` and `RESEARCH_LLM_MODEL` are present, and
uses default opportunity/theme/synthesis adapters. `RESEARCH_LLM_BASE_URL` selects a compatible
endpoint; missing semantic credentials retain the conservative EVIDENCE extractor.

The model receives only questions, retrieved passages with runtime metadata, and accepted relevant
claims. Returned metadata is rejected; exact quotes, inference support and WTP rules still pass
through shared evidence intake. A separate adversarial context uses negative queries before any
synthesis prose exists. Same-provider review is explicitly labeled. Proposed themes and structured
opportunities remain hypotheses until their existing completion contracts pass.

Each output is a new directory containing Markdown dossiers, partial comparison, complete JSON,
and incrementally flushed source/claim/search JSONL. Full resume is not implemented. Exit 2 means
partial/backend-required output, not successful completion. Search failures, challenges, inaccessible
pages, and queries producing no useful retrieved evidence do not count as completed field research.

HTML and plain text are supported with bounded timeouts, retries, caches, size limits and public-IP
redirect checks. Retrieved external link destinations remain in extracted text to support identity
corroboration. No PDF, login or JavaScript browser execution is provided. Domain classification is
heuristic and reviewable; deployment should address DNS rebinding beyond preliminary DNS checks.

Validation used fake model/network boundaries for end-to-end extraction, discovery and output.
The real free-search smoke received a DuckDuckGo challenge. Direct Cornell homepage fetching
succeeded. No Brave, Tavily or semantic API credentials were available; no paid API success is claimed.
