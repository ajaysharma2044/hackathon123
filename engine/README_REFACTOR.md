# Agentic Research Refactor Entry Point

Use `governor.build_research_graph(objective)` for new research runs.

Do **not** use the old seeded discovery graph as the source of truth for new work. The new path expects:

- `ctx['research_executor']`: a live source-backed research adapter;
- optionally `ctx['theme_generator']`: an evidence-bounded theme generator;
- optionally `ctx['synthesizer']`: an evidence-only final synthesizer.

Without these adapters the system must remain PARTIAL rather than hallucinate.

See `docs/agentic/refactor-v2.md` for the architecture and P0/P1 roadmap.
