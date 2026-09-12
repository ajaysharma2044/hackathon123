# Commercial Engines (Research · Product-Dev · Activation · Innovation · Experimentation · Sponsorship · Design-Partner)

The R&D engine has its own doc ([rd-engine.md](rd-engine.md)); the rest are collected here as one
coherent set rather than seven stubs. Each: what it sells, hackathon advantage, the value model
(coded in [engine/value_engines.py](../engine/value_engines.py) where quantitative), and comparables.
All prices are rational **ceilings**, never observed WTP.

## Research Engine — the behavioral observatory
Sells archetype-3. **Already the most-built part of the repo** — see [research-modules.md](research-modules.md)
(the 13 pain-first modules + the question-VOI kill-filter), [capture-system.md](capture-system.md)
(instrumentation), and [question-catalog.md](question-catalog.md). Value = `DecisionValue ×
P(research changes decision) × HackathonAdvantage`, computed via [engine/score.py](../engine/score.py)
and [engine/voi.py](../engine/voi.py). **Advantage:** answers *"why did the people who didn't choose us
not choose us"* — invisible to first-party telemetry. **Ceiling:** $50–150K/study, $150K+ with
qualitative depth (the-quote.md). The deepest, most-proven budget of any engine.

## Product-Development Engine — variation & convergence
Sells archetype-4. Value is the **solution-space distribution**, not the max: N independent prototypes
reveal feature demand, integration patterns, failure points, and unexpected uses; *convergence* (many
teams choosing X) is a strong default signal. Coded: `product_dev_value(n, diversity, decision_value,
p_change)` — coverage saturates in n (you learn the space, then repeat), so **5–15 teams**, not 50.
**Advantage over a design agency (IDEO $0.5–3M):** diversity of *independent* attempts at lower cost.
**Ceiling:** $50–150K. **Fails when:** the buyer needs one polished concept, not variety.

## Activation Engine — behavioral adoption + the credit question
Sells archetype-6. Value = incremental **retained** developers × value/retained, benchmarked against
paid-marketing CAC. Coded: `activation_value(exposed, funnel_rates, value_per_retained, cost,
cac_benchmark)` returns the exposure→activation→meaningful→integration→30/90d funnel and whether it
beats CAC. **The embedded high-VOI product:** *does a $100 credit create retention or subsidize
temporary activation?* (question-catalog Q1) — worth a $10–350K/startup allocation. **Advantage over
DevRel/paid marketing:** behavioral, post-incentive retention evidence, not impressions. **Ceiling:**
$10–60K activation, more as a research study. **Buyer:** DevRel / Growth / Startup Programs.

## Innovation Engine — the directed corporate challenge
Sells archetype-5 (R&D-lite): one company's *specific* prototypeable problem as a disclosed track,
M teams, a bounty/prize, ranked solutions. Reuses the R&D fit gate (`rd_fit`) and prize economics
(ETHGlobal tracks $10–20K; delivered challenges to $1.27M). **Advantage:** options + a demo, fast.
**Fails when:** the problem needs proprietary context or long cycles. Packaged as a **directed wallet**.

## Experimentation Engine — randomized arms inside the event
Enables the *rare* L3/L4 causal claims: randomize credit tier, onboarding path, docs variant, a
narrow AI-workflow sub-task. Coded: `min_detectable_effect(n_per_arm)` — **honest power**: ~60/arm
detects only ~15–25pp effects, so randomize *narrow, high-contrast* interventions, never the whole
event. Pre-register outcome/sample/stopping rules (measurement.md). **Not a standalone sale** — a
method that raises the evidence level (and price) of the Research/Activation engines.

## Sponsorship Engine — the commodity floor
Sells archetype-10. Branding + opt-in recruiting; priced by **published ladders** (`SPONSOR_COMPARABLES`:
activation track $5–25K, title $30–80K, recruiting $5–27K). High certainty, **low VOI** — the matcher
treats "only sponsorship fits" as effectively **no differentiated fit**. It's the fallback, never the
thesis. Keep it available (it funds logistics) but never lead with it.

## Design-Partner Engine — demonstrated fit, opt-in
Sells archetype-7. Output: warm, qualified design-partner intros — builders who *built on* the product
and opted in. Dodges the FCRA/placement walls that constrain recruiting (recruiting-legal.md). **Advantage:**
*demonstrated* fit beats a résumé. An add-on to Activation/Product-Dev, not usually a standalone six-figure sale.

## The ranking that falls out

By (hackathon advantage × proven budget × six-figure ceiling): **Research ≈ R&D > Product-Dev ≈
Innovation > Activation > Design-Partner > Sponsorship.** Research and R&D — wrapped in a directed
wallet — are the spine; the rest are real but secondary or additive. Experimentation is a multiplier
on the top two, not a product.
