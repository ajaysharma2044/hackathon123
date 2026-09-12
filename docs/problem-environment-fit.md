# Problem × Environment Fit — Fit(P,E)

Documents the code in [`engine/problem_matcher.py`](../engine/problem_matcher.py) and the
`problem_environment_fit` table in
[`schema/004_environment_economy.sql`](../schema/004_environment_economy.sql). It describes what the
matcher already does; it invents no behavior.

`match(problem, env)` computes `Fit(P,E)` on **decomposed** dimensions and gates it with a **HARD
structural-advantage test**. The module docstring states the governing rule:

> a large budget or a big decision CANNOT rescue a problem the environment holds no real advantage
> on. If a consulting team / university lab / the company's own staff would do it as well, Fit is
> killed regardless of the other dimensions.

This is a deliberate generalization of the hard gate in [`engine/score.py`](../engine/score.py) — see
"How this generalizes score.py" at the end.

## The 7 decomposed fit dimensions

`match` builds a `fit` dict of 7 ordinal `0..3` dimensions, each read from the environment's
capability vector (`environment.capability_vector`, see [`engine/environment.py`](../engine/environment.py)).
These mirror the columns of the `problem_environment_fit` table one-for-one.

| Fit dimension (problem_matcher.match) | Source capability | Table column |
|---|---|---|
| `parallel_search_advantage` | `PARALLEL_SEARCH` | `parallel_search_advantage` |
| `talent_match` | `_talent_match(problem, env)` | `talent_match` |
| `behavioral_realism` | `BEHAVIORAL_REALISM` | `behavioral_realism` |
| `observability` | `OBSERVABILITY` | `observability` |
| `prototype_value` | `PROTOTYPEABILITY` | `prototype_value` |
| `counterfactual_quality` | `COUNTERFACTUAL_QUALITY` | `counterfactual_quality` |
| `external_validity` | `EXTERNAL_VALIDITY` | `external_validity` |

Six of the seven are read straight from the environment's capability vector; only `talent_match` is
computed against the problem (below). The dimensions are **never collapsed into one score** — the
docstring says so, and the only scalar returned, `coverage`, is explicitly "a ranking aid, not a
collapse."

## The hard structural-advantage gate

The gate is the heart of the matcher and reproduces the `score.py` discipline. In `match`:

```
gating      = MODE_CAPABILITY_NEEDS.get(problem.mode, [])
env_advantage = min((cap[c] for c in gating), default=NONE)   # min => one weak essential kills it
gate_passed = env_advantage >= FIT_ADVANTAGE_FLOOR
```

`FIT_ADVANTAGE_FLOOR = MED` (problem_matcher.py). The environment must clear an ordinal floor of
**MED** on *every* capability the problem's mode essentially requires (`MODE_CAPABILITY_NEEDS`, from
[`engine/problem_model.py`](../engine/problem_model.py); see
[problem-mechanics.md](problem-mechanics.md)). Because the advantage is the **min** over those
essential capabilities, missing even one drops the pair below the floor and **KILLs** it. The
docstring: *"the environment must clear an ordinal FLOOR on EVERY capability the problem's mode
essentially requires. Miss one → KILL."*

This is a gate, **not a weighted average.** No other dimension — not a large `economic_value`, not a
big `cost_of_wrong`, not deep talent — can lift a pair over a failed gate, because the gate is
evaluated first and `env_advantage` never sees them. `_weakest(cap, gating)` names the capability
that failed so the KILL verdict can cite it.

`coverage` is computed separately as `sum(1 for c in needed if cap.get(c, 0) >= MED)` over the
broader `required_capabilities(problem)` list. It is counted, not gated on, and only shapes the
verdict *after* the gate passes.

## The talent-match sub-model

`_talent_match(problem, env)` returns an ordinal `0..3`. It answers: does the configured population
supply the disciplines the problem's dominant components need? Its discipline is stated in the
docstring — **"Population-level only (Phase 2) — we never score individuals."**

Mechanics: it reads the labels present in `env.talent_mix` (any label with share > 0), then walks
`COMPONENT_TALENT`:

```
COMPONENT_TALENT = {
    "technical_component":   {"SOFTWARE", "ML_RESEARCH", "DATA_SCIENCE", "HARDWARE"},
    "creative_component":    {"DESIGN", "PRODUCT"},
    "operational_component": {"OR_IE", "OPERATIONS", "SUPPLY_CHAIN"},
    "scientific_component":  {"ML_RESEARCH", "SCIENCE", "QUANT"},
}
```

For each problem component scored at `MED` or higher, it counts a "want"; if the population supplies
any matching label, it counts a "have." The base match is `HIGH` when the problem has no dominant
component (`total == 0`), otherwise `round(HIGH * have / total)` — the fraction of dominant
components the population can staff, scaled onto 0..3.

### The domain-expertise dock

After the base score, one adjustment fires:

```
if raw["need_domain_expertise"] >= MED and env.experience_band in ("STUDENT", "EARLY"):
    base = max(NONE, base - 1)
```

If the problem needs deep domain knowledge (`need_domain_expertise >= MED`) and the cohort is a
junior/elite band (`STUDENT` or `EARLY`), the match is **docked by one ordinal level.** This is the
STATE.md caution encoded: *"lack of domain expertise can destroy value."* It is the same structural
weakness the bear case raises — hand-picked elite students may be the wrong panel for a problem that
turns on deep domain knowledge. The dock is population-level and band-level; it never reaches an
individual.

The result is clamped to `[NONE, HIGH]`.

## The verdicts

`match` returns one `verdict` string, chosen in strict priority order:

| Order | Condition | Verdict |
|---|---|---|
| 1 | `not gate_passed` | **KILL** — environment holds no structural advantage on the essential capability `'<weakest>'` (would be done as well by an existing substitute) |
| 2 | `fit["talent_match"] < LOW` | **KILL** — configured talent cannot supply the problem's dominant components |
| 3 | `coverage >= max(2, len(needed) - 1)` | **STRONG_FIT** — environment covers the problem's required capabilities |
| 4 | `coverage >= 1` | **MODERATE_FIT** — partial capability coverage |
| 5 | else | **WEAK_FIT** — gate cleared but little capability coverage |

Two independent ways to KILL: fail the structural gate, or clear the gate but have talent below
`LOW`. Both are hard — no downstream magnitude rescues them. STRONG / MODERATE / WEAK are graded on
`coverage` only *after* both kills are ruled out.

The full return is decomposed: `{"fit": {...7 dims}, "gate_passed": bool, "env_advantage": int,
"coverage": int, "needed_capabilities": [...], "verdict": str}`. There is no single fit score.

## pareto_frontier — a large budget cannot buy onto the frontier

`dominates(a, b)` (problem_matcher.py) is Pareto dominance over the 7 fit dimensions: `a` dominates
`b` iff `a[k] >= b[k]` for all dimensions and strictly greater on at least one. Higher is better on
every dimension.

`pareto_frontier(matches)` takes a list of `(name, match_result)` pairs and returns the names whose
fit vector is non-dominated — **but only among the gate-passing pairs.** The first line filters:

```
live = [(n, m) for n, m in matches if m["gate_passed"]]
```

Killed pairs (`gate_passed is False`) are never considered, so a killed pair can never appear on the
frontier no matter what other quantities it carries. And among live pairs, dominance is over the fit
vector alone. The docstring states the invariant directly: **"A large budget cannot put a dominated
(or killed) pair on the frontier."** This is the same discipline the `problem_environment_fit` table
records with its `fit_gate_passed` and `on_pareto` boolean columns.

## How this generalizes score.py

`score.py` gates a research *question* on `HackathonAdvantage`, defined as
`min(hackathon_naturalness, internal_data_blind_spot)`, with `HACKATHON_ADVANTAGE_FLOOR = MED`. If
that advantage is below the floor, `QuestionScore.opportunity` returns `0.0` — *"KILLED: answerable
without us. Big budget cannot rescue it."* That question compares one environment (a hackathon) to a
fixed set of substitutes (Gartner, a panel, the company's own telemetry).

`problem_matcher.match` generalizes exactly that pattern along two axes:

1. **From one environment to any environment.** `score.py` hardcodes "the hackathon." The matcher
   reads capabilities from a configurable `Environment` object, so the same gate now applies to a
   residency, a prediction tournament, a challenge — any point in the environment design space.
2. **From one substitute set to any substitute.** `score.py`'s advantage is "our edge over the
   alternatives." The matcher's gate is "does *this* environment clear MED on the mode's essential
   capabilities" — which is the same question ("would a consulting team / university lab / internal
   staff do it just as well?") asked structurally, per capability, per mode.

The structural correspondence: `score.py`'s `min(naturalness, blind_spot) >= MED` becomes the
matcher's `min(cap[c] for c in mode_essentials) >= MED`. Both take a **min** so a single weak
essential kills the opportunity; both use **MED** as the floor; both refuse to let economic size or
budget buy past the gate. The matcher is `score.py`'s hard-gate idiom lifted from "hackathon vs a
research panel" to "environment vs any substitute."
