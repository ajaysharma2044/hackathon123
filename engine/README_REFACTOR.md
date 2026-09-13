# Evidence-first research entrypoint

From the repository root:

```bash
python -m engine.research_run --objective "Determine the optimal first Cornell technical event"
```

Without a configured research adapter this intentionally returns `RESEARCH_BACKEND_REQUIRED`,
`UNKNOWN` recommendation, and exit code 2. It does not load a sponsor or theme packet.

Supply a trusted installed `--executor module:factory`, an independent `--red-team-executor`,
and optionally a JSON `--config`. Python `research_run.run` additionally accepts the theme,
opportunity and synthesis adapters. An explicit opt-in HTTP adapter is available as
`web_research:build_default_web_executor`; its default extractor produces unpromoted excerpts, not
complete business findings. No production browser/LLM reasoning adapter is bundled.

See [architecture](../docs/agentic-v2/architecture.md),
[executor contract](../docs/agentic-v2/research-executor.md), and
[actual validation](../docs/agentic-v2/testing.md). Historical seeded/packet agents are quarantined
under `examples/legacy`; they are not production discovery.
