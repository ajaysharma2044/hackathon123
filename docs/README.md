# hackathon123 — docs

**Start here → [overview/STATE.md](overview/STATE.md).** It is the standing understanding; *everything else in `docs/` is raw material.*

This tree is organized so an agent (or person) can tell **what's canonical from what's raw research.** Each folder's README tags its docs:

- `CANONICAL` — standing truth; treat as authoritative
- `REFERENCE` — working reference; solid but not the single source of truth
- `ENGINE-DOC` — describes a model or the codebase, not the business decision
- `HISTORICAL` — kept for context; superseded or already executed
- `STALE` — flagged: framing that predates a later decision — check STATE.md first
- `ARCHIVED` — dead; not part of the live plan (`_archive/`)

## For a given question, read

- The one gating question (will any buyer pay?) → [overview/STATE.md](overview/STATE.md), [overview/hackathon123-council-verdict.md](overview/hackathon123-council-verdict.md)
- Pricing / economics → [business-model/research-pricing.md](business-model/research-pricing.md), [business-model/economics.md](business-model/economics.md)
- Who to sell to → [buyers/target-list.md](buyers/target-list.md), [buyers/top-prospects.md](buyers/top-prospects.md)
- The research product → [research-product/research-framework.md](research-product/research-framework.md), [research-product/measurement.md](research-product/measurement.md)
- Before quoting any engine number → [modeling/quant-engine/quant-assumptions.md](modeling/quant-engine/quant-assumptions.md)
- Running the event → [event/operational-architecture.md](event/operational-architecture.md), [event/run-of-show.md](event/run-of-show.md)

## Folders

| Folder | What's in it |
|---|---|
| [_archive/](_archive/README.md) | Superseded material, kept for the record. Not part of the live plan. |
| [business-model/](business-model/README.md) | How the thing makes money — monetization, pricing, economics, funding. |
| [buyers/](buyers/README.md) | Demand discovery and sponsor/company targeting — who pays, why, and which names. |
| [event/](event/README.md) | Event design and physical operations — the concrete Event 1, logistics, judging, staffing, Cornell context. |
| [evidence/](evidence/README.md) | Historical and comparable-events evidence base — what similar programs did and charged. |
| [markets/](markets/README.md) | The multi-sided market design and its two opt-in sides (talent, venture). |
| [meta/](meta/README.md) | Process/meta docs — cross-branch integration and refactor planning (largely executed). |
| [modeling/](modeling/README.md) | Docs that describe the economic/decision MODELS (each maps to an engine module) — not the codebase itself. |
| [overview/](overview/README.md) | Canonical standing docs — start here. The thesis, current understanding, roadmap, and the council verdict. |
| [research-ops/](research-ops/README.md) | The live in-event research operating system — how research is actually run during an event. |
| [research-product/](research-product/README.md) | The sellable research product — methodology, capture system, data model, instrumentation. |
| [system/](system/README.md) | Docs that describe the CODEBASE itself (the autonomous research engine). |
