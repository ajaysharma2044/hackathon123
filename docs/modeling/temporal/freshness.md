# Evidence freshness and decay

`engine/freshness.py`. Every claim has a shelf life. A 2026 Claude-vs-Gemini tool preference may be
stale by 2028; eHub room capacity persists until the facility changes.

`FRESHNESS_POLICY` sets a **validity window by claim type** (venue_fact 3650d, cornell_culture 730d,
tool_preference 180d, company_strategy 365d, …). `freshness(claim_type, observed_at, now)` returns an
age and a `FRESH / AGING / STALE` status. **Old evidence is aged and down-weighted, never deleted.**

`decay_weight(...)` applies an exponential weight **only when a half-life is actually grounded** for
that claim type; otherwise it returns `weight: None` with *"do NOT assume exponential decay"* — the
user's explicit instruction. This weights company intelligence (LIX): a new launch outranks a
three-year-old strategy article, but the old one is marked aged, not discarded. The
`validity_days` are honestly flagged as **assumed orderings, not measured constants**. Feeds the
temporal product ladder in [temporal-voi.md](temporal-voi.md).
