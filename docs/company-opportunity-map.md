# Company Opportunity Map

The system that turns `COMPANY = X` into a structured offer or a NO FIT. Implemented and tested in
[engine/company_matcher.py](../engine/company_matcher.py). The ICP is an **output** of this routing,
never an input — a logo means nothing until its situation clears an engine's structural gate.

## How it routes

A `CompanySituation` carries evidence-tagged structural flags (developer-facing, blind-spot,
hackathon-naturalness, decision-value, budget-signal, adoption-intent, and the R&D fit dimensions:
uncertainty/parallelizable/prototypeable/evaluable/needs-deep-domain, plus participant-fit). `match()`:

1. Scores each engine's **structural fit** from the flags.
2. Applies the **HackathonAdvantage kill gate** (`min(naturalness, blind_spot)`) to the value engines —
   a question a panel/telemetry/consultant answers equally well scores 0 regardless of budget.
3. Applies the **R&D fit gate** (Boudreau/Lakhani) — low-uncertainty problems cannot be sold as R&D.
4. Picks the best engine; if the best differentiated fit is below threshold, returns **NoFit** —
   distinguishing "only commodity sponsorship fits" from "no fit at all."

It **is allowed to say no**, and does: a non-developer-facing, low-uncertainty, well-instrumented
internal problem returns NoFit with the reason "answerable elsewhere." (Tested.)

## The 20-field offer it produces

`company · engine · fit · problem · evidence · decision_owner · economic_importance · current_method ·
why_hackathon_helps · event_module · participants · event_changes · data_captured · deliverable ·
ip_confidentiality · capacity_consumed · cost_to_us · pricing_evidence (a ceiling, NOT WTP) ·
commercial_package · sales_message · confidence · still_to_learn (always includes: observed WTP UNKNOWN).`

## Worked routings (from tested inputs)

- **Stripe / Growth** — problem: "developers test us but never reach production"; HIGH blind-spot +
  HIGH naturalness + adoption intent → routes to **Research/Activation**, ceiling $50–150K, sales
  message opens with *their* blind spot. Offer, not NoFit. ✅
- **A regional bank / branch ops** — teller-scheduling, well-instrumented internally, not
  developer-facing → **NoFit**: "answerable elsewhere; a panel/consultant does this better." ✅
- **A deep-tech firm tuning a known algorithm constant** — HIGH budget but LOW uncertainty →
  **not sold as R&D** (the Boudreau/Lakhani gate fires). ✅

The point of the worked cases: the system's most valuable outputs are the **NO FITs** — they stop us
selling a hackathon where it is structurally worse than the alternative, which is exactly the
discipline the whole thesis needs to be credible.

## Usage

```python
from company_matcher import CompanySituation, match
result = match(CompanySituation(company="X", ..., blind_spot="HIGH", problem_uncertainty=0.6, ...))
# -> Offer(engine=..., pricing_evidence="ceiling $..., NOT observed WTP", still_to_learn="WTP UNKNOWN ...")
#    or NoFit(reason="...", best_engine=..., best_fit=...)
```

The `CompanySituation` fields are populated by evidence (job posts, launches, earnings, changelogs) —
the [go-to-market](go-to-market.md) sweep is how they get filled at scale.
