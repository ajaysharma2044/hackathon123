# Integration Plan — Reconciling Three Parallel Architectures

> Part XCVIII deliverable. Three sessions built in parallel on divergent branches sharing only the
> ancestor `e258113`. This maps them, resolves the conflicts, and defines the migration — **without
> silently overwriting any architecture**. Nothing here is executed until the reconciliation route is
> chosen (see the decision at the bottom).

## The three lineages

| Lineage | Branch | Head | Adds |
|---|---|---|---|
| **A-trunk** | `main` (via `demand-side-research-pass`) | `586eec8` | value engines, historical analysis, structural archetypes, company→offer, **Event 1 design + 40-Q synthesis**, `schema/004_value_engines.sql` |
| **A-ext** | `claude/cornell-hackathon-research-os` | `8dd4514` | (builds on A-trunk) **Live Research OS** + **event-operations layer**, `schema/006_live_research.sql`, `007_event_ops.sql`, ~35 engine files, 83 docs |
| **B** (this) | `claude/research-findings-clarification` | `01987e4` | **discovery engine** (environment/problem/economy primitives), **arms-race lens**, **Cornell audience/product/cohort-advantage**, `schema/008_environment_economy.sql`, `009_audience_products.sql`, 56 docs |

Merge-base of A and B: `e258113` (the pre-session trunk). They have diverged substantially.

## The key finding: they are COMPLEMENTARY, not contradictory

At the engine level the overlap is only the **original shared base** (`beliefs, calibration, capture,
event_optimizer, monte_carlo, portfolio, score, voi, worked_example` + their tests — the 54-check
core). Everything each lineage added is disjoint:

- **Only on B (mine):** `environment, problem_model, economy, problem_matcher, environment_generator,
  talent_allocator, business_model, icp_discovery, bilevel, spend_intensity, gap_finder,
  opportunity_matcher, audience, cohort_advantage, qualitative, product_catalog`.
- **Only on A-ext (cornell-os):** `value_engines, live_research, mentor_routing, research_triggers,
  adaptive_questions, adaptive_sampling, burden_budget, intervention_log, staffing_model,
  judging_assignment, evidence_graph, company_matcher, org_graph, question_backlog, team_trajectory`.

**The event-OS this master pass asks for already largely exists on A-ext.** B supplies the
demand/discovery/audience half A-ext lacks. Together they are close to the full system.

## Conflicts to resolve

| # | Conflict | Resolution |
|---|---|---|
| 1 | **`schema/004` collision** — A: `004_value_engines.sql`; B: `008_environment_economy.sql` | A-trunk's `004_value_engines` is already on `main`, so it keeps `004`. **Renumber B's migrations → `008_environment_economy.sql`, `009_audience_products.sql`** (after A-ext's 006/007). Migration numbers are ordering only; content unaffected. |
| 2 | **`STATE.md` divergence** — both edited it | Merge: keep the epistemic frame + gating unknown (identical intent in both); union the two "what's known" tables; keep one canonical status line. |
| 3 | **`event1-design.md` (A) vs my `temporary-economy-thesis.md`/Cornell docs** | Complementary. A's `event1-design.md` is the concrete event; B's thesis is the discovery framing. Cross-link; do not overwrite. Event 1 blueprint reconciles to **Cornell-only @ eHub** (both agree). |
| 4 | **company matching** — A `company_matcher.py` vs B `opportunity_matcher.py` + planned `company_matcher_v2` | Keep both: B's `opportunity_matcher`/`spend_intensity`/`gap_finder` is the *demand-discovery* front; A's `company_matcher`/`org_graph` is the *company→offer→track* back. Wire B's output into A's input; don't duplicate. |
| 5 | **Cornell audience docs** — B `cornell-audience-map.md` vs A-ext audience/history docs | Union; B has the cited seed sweep, A-ext has `historical-program-dataset` / `prior-hackathons`. Keep both, cross-reference. |
| 6 | **doc filename overlaps** (STATE, capture-system, economics, event-optimizer, quant-*, research-*, etc.) | These descend from the shared ancestor and are mostly identical or lightly edited; standard 3-way merge, human-review the few that diverge. |

## Module map (Part XCVIII: Old → New → Conflict → Resolution → Migration → Tests)

| Master-pass module | Already exists as | Conflict | Resolution |
|---|---|---|---|
| `mentor_queue` | A-ext `mentor_routing.py` | none | reuse A-ext |
| `interruption_engine` | A-ext `research_triggers.py` + `interruption-policy.md` | none | reuse A-ext |
| `research_burden` | A-ext `burden_budget.py` | none | reuse A-ext |
| `event_adaptation` | A-ext `intervention_log.py` + `event-adaptation.md` | none | reuse A-ext |
| `run_of_show` | A-ext `run-of-show.md` (+ needs engine?) | partial | keep doc; add engine only if missing |
| `company_to_track` | A-ext `company_matcher.py` + `company-opportunity-map.md` | overlaps B `opportunity_matcher` | wire B→A |
| `track_generator` / `track_compatibility` / `sponsor_capacity` | **missing on both** | none | **build new (this pass)** |
| `experience_optimizer` (hard floors) | A-ext `participant-experience.md` (doc) | partial | build the engine with hard floors |
| `energy_curve` | A-ext `event-phase-plan.md` (doc) | partial | build engine if missing |
| `multiuse_assets` | **missing on both** | none | **build new (this pass)** |
| `frontstage/backstage` model + FrontendDistortion gate | **missing as code** | none | **build new (this pass)** |
| discovery/arms-race/audience/product | B (mine) | none | port into canonical trunk |

**Net new work after integration** (not yet built anywhere): track generator/compatibility/sponsor-
capacity, the frontend-distortion gate, the multi-use-asset engine, experience-optimizer with hard
floors, the master node graph unifying B's discovery graph with A-ext's `org_graph`, and the Part-XCVI
guardrail test-suite spanning both halves.

## Recommended route

**Create an integration branch off `main`, merge A-ext into it (event/research OS), then port B's
engine + docs on top (renumbered schema 008/009), resolve the 6 conflicts, and build only the net-new
pieces.** This yields one canonical trunk that is the master operating layer — the goal of this pass —
instead of a fourth parallel architecture.

**Caveat:** if the `cornell-os` session is still actively committing, coordinate first — merging under
it risks clobbering in-flight work. That is why the route is a decision below, not an executed merge.
