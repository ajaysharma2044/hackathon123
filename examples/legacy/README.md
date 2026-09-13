# Historical implementations — not production entrypoints

These files preserve the earlier seeded/packet architecture for migration reference. They are not
imported by `engine.research_run`, the governor, or the production resolver registry. Their names,
prices, audience counts, event defaults and packets are historical assumptions, not new evidence.
Do not register these agents in a production research run. Use the evidence-first entrypoint described
in `engine/README_REFACTOR.md`.
