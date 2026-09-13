# Evidence contract

AtomicClaim extends the branch's existing model with subject_id, value, source_id, quote_or_excerpt,
observed_at, published_at and supporting_claim_ids. `field` is its predicate; `statement` is the
extracted text. FACT, INFERENCE, HYPOTHESIS, UNKNOWN and PRIMARY_VALIDATION_REQUIRED stay distinct.

FACT construction requires a source. Production intake additionally requires an opened SourceDocument,
a nonempty excerpt present verbatim in its content, matching source metadata and matching clocks.
An extractor cannot upgrade the retrieval adapter's source tier. Sources have IDs, URLs, titles,
publication/retrieval times, type, quality and optional independent_group for syndicated/common-owner
material. Unknown publication dates stay null. Retrieval is not claimed when opening fails.

INFERENCE requires accepted support IDs, which must trace through facts/inferences. Forward references,
cycles and hypothetical/unknown foundations are rejected. Field gates inspect source quality through
that support closure. UNKNOWN and PRIMARY_VALIDATION_REQUIRED never satisfy factual requirements;
only explicitly optional/status fields can accept them. Design contracts may explicitly accept
hypotheses, retaining that label.

EvidenceMemory is owned by ResearchBridge. Its documents/claims are append-only by ID; collisions
with changed content are rejected. Opposing claim references are kept and connected in both directions,
including when the second claim arrives later. Claims reuse `evidence_graph.Claim`, EvidenceRef and
NegativeCase for finding provenance. Trace follows findings → atomic support → source documents.
Legacy Finding/packet export remains archival; packets now say CACHED_UNVALIDATED, never RESOLVED.

WTP uses the existing commercial_logic taxonomy plus PRIMARY_VALIDATION_REQUIRED. A factual
wtp_status must be OBSERVED and cite primary buyer/contract evidence recognized by that module,
with buyer, scope and amount. Funding, valuation, price cards and historical sponsorship comparables
cannot establish observed WTP. Without this evidence, desk-research WTP stays UNKNOWN or
PRIMARY_VALIDATION_REQUIRED. Comparable prices remain in their own fields.

Acceptance validates provenance and structure; semantic entailment, source authenticity, source-type
classification, and a buyer's actual authority require adapter quality controls and primary validation.
