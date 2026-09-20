# Agent guide

Planning docs live in `docs/`. Before answering from them:

1. **Start at [`docs/overview/STATE.md`](docs/overview/STATE.md)** — the standing understanding. Treat it and [`docs/overview/hackathon123-council-verdict.md`](docs/overview/hackathon123-council-verdict.md) as authoritative; **everything else in `docs/` is raw material.**
2. Use [`docs/README.md`](docs/README.md) as the map — each folder's README tags its docs (`CANONICAL` / `REFERENCE` / `ENGINE-DOC` / `HISTORICAL` / `STALE` / `ARCHIVED`).
3. `docs/_archive/` is **dead** (e.g. the rejected GridCompute theme) — never treat it as current.
4. `STALE`-tagged docs contain framing that predates a later decision — check STATE.md before relying on them.

Code is in `engine/` (flat Python modules) with SQL in `schema/`. Docs describing the engine are under `docs/modeling/` (economic models) and `docs/system/` (the codebase).
