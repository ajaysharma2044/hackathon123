# Structural Archetypes

The recurring *structures* behind competitions/contests/programs, abstracted from the history
([historical-structural-analysis.md](historical-structural-analysis.md)) — not named companies.
Each archetype tells us when the hackathon format is advantageous vs inferior, which is how the
[company matcher](company-opportunity-map.md) routes a company to an engine (or to NO FIT).

Legend per archetype: **INPUT · MECHANISM · OUTPUT · BUYER · BUDGET · PARTICIPANT INCENTIVE ·
IP/FOLLOW-ON · WHY IT WORKS · WHY IT FAILS · HACKATHON ADVANTAGE (when it wins / loses).**

## 1. Prize Tournament (extreme-value search)
INPUT: one hard, uncertain, evaluable problem · MECHANISM: many independent teams, winner-take-most
purse · OUTPUT: the single best solution · BUYER: R&D/innovation/government · BUDGET: R&D / prize ·
INCENTIVE: prize + prestige · IP: usually buyer-owned or licensed · WHY WORKS: max-of-N on high
uncertainty (Boudreau/Lakhani) · WHY FAILS: effort dilution past the optimum; solver ≠ implementer;
needs crisp evaluation · **HACKATHON WINS** when the problem fits 48–72h and evaluates cleanly;
**LOSES** for low-uncertainty problems (one team is better).

## 2. Parallel R&D Search (value-of-failure)
Like #1 but the buyer values the **whole map**: which approaches fail, which converge, the shortlist.
OUTPUT: N prototypes + an elimination map + a follow-on shortlist. WHY WORKS: failures cheaply
eliminate search space; independent convergence is a strong signal. **HACKATHON WINS** when the
buyer's real need is to *narrow options fast*, not just get one winner. This is the [R&D engine](rd-engine.md).

## 3. Research Instrument (behavioral observatory)
INPUT: a decision the buyer can't resolve from their own data · MECHANISM: instrument real building
with consent · OUTPUT: an aggregate findings report (choice/friction/switching/retention) · BUYER:
Product Research / UXR / Growth · BUDGET: research / insights · INCENTIVE: participants build; research
is invisible/organic · WHY WORKS: the deciding behavior happens naturally and is invisible to the
buyer's telemetry · WHY FAILS: n≈200, self-selected → L1/L2 only; elite ≠ median · **HACKATHON WINS**
when the question is *"why did the people who didn't choose us not choose us?"* This is the
[research engine](research-engine.md) / the whole capture system.

## 4. Product Beta Arena (variation for product development)
INPUT: a product decision needing exploration · MECHANISM: 5–15 teams build on the product,
independently · OUTPUT: solution-space map + feature demand + integration patterns + failure points ·
BUYER: Product / DX Eng · BUDGET: product / engineering · WHY WORKS: variation reveals the space one
team can't; convergence reveals the default · WHY FAILS: prototypes ≠ production; needs product access ·
**HACKATHON WINS** vs a single design agency when *diversity of independent attempts* is the value.

## 5. Corporate Problem Challenge (directed innovation)
A specific company problem posed as a disclosed track, M teams, bounty/prize. OUTPUT: ranked
solutions to *their* problem. BUYER: Innovation / R&D / a product team. BUDGET: innovation / R&D /
directed wallet. **HACKATHON WINS** when the problem is prototypeable and the company wants options;
**LOSES** when it needs deep proprietary context or long build cycles.

## 6. Product Activation Event
INPUT: a product wanting developer adoption · MECHANISM: required exposure → free choice → observe ·
OUTPUT: activation→30/90d retention funnel + the credit-vs-retention finding · BUYER: DevRel / Growth /
Startup Programs · BUDGET: developer marketing / credits / startup program · WHY WORKS: builders
actually integrate; retention is observable post-event · WHY FAILS: elite ≠ typical user; short window ·
**HACKATHON WINS** vs paid marketing when the buyer needs *behavioral* adoption evidence, not impressions.
This is the [activation engine](commercial-engines.md).

## 7. Design-Partner Funnel
INPUT: a product wanting qualified early design partners · MECHANISM: builders build on it; opt-in
intro · OUTPUT: warm, qualified design-partner leads (people who built on it and chose to be introduced) ·
BUYER: Product / DevRel · BUDGET: product / partnerships · WHY WORKS: demonstrated fit + opt-in
consent; dodges FCRA/placement walls · **HACKATHON WINS** by producing *demonstrated* fit, not a list.

## 8. Talent Discovery Event
INPUT: an employer wanting evidence of real technical work · MECHANISM: opt-in work evidence ·
OUTPUT: first-hand work-evidence records (**never a score** — FCRA/LL144) · BUYER: technical employers /
quant firms · BUDGET: recruiting · WHY FAILS: legal boundaries are hard; no per-hire fee market exists ·
**HACKATHON WINS** modestly — as evidence, never as a ranking.

## 9. Directed Research Wallet (the pricing structure)
Not a use — a *packaging* archetype from SRC/Stanford HAI. The buyer gets a **directed wallet**
($100–400K) they spend on teams/questions they choose, plus early access + instrument review. **This
is how any of the above clears six figures**: it converts a sponsorship into an R&D line item with an
owner and a spend plan ([innovation-budget.md](innovation-budget.md)).

## 10. Ordinary Sponsorship (the floor)
INPUT: a brand wanting exposure/recruiting · OUTPUT: logo + booth + opt-in resumes · BUDGET: marketing /
recruiting · **HACKATHON is not advantageous here** — it's the commodity floor ($5–50K), priced by
published ladders, and it caps low. The [matcher](company-opportunity-map.md) treats "only sponsorship
fits" as effectively **NO differentiated FIT**.

## The archetype → engine map

| Archetype | Engine | Hackathon advantage | Six-figure? |
|---|---|---|---|
| 1 Prize Tournament | R&D | high-uncertainty only | via directed wallet |
| 2 Parallel R&D Search | **R&D** | when narrowing options fast | **yes** |
| 3 Research Instrument | **Research** | invisible-to-telemetry questions | **yes** |
| 4 Product Beta Arena | Product-Dev | when variation is the value | yes |
| 5 Corporate Challenge | Innovation | prototypeable problems | via directed wallet |
| 6 Activation Event | Activation | behavioral adoption evidence | mid ($10–60K) |
| 7 Design-Partner Funnel | Design-Partner | demonstrated fit | add-on |
| 8 Talent Discovery | Recruiting | evidence not scores | low, capped |
| 9 Directed Wallet | (packaging) | the six-figure wrapper | — |
| 10 Ordinary Sponsorship | Sponsorship | none (commodity floor) | no |

The two archetypes that are **both hackathon-advantaged AND six-figure** are **#2 Parallel R&D
Search** and **#3 Research Instrument** — wrapped in **#9 Directed Wallet**. That is the spine of the
commercial thesis, and everything the matcher and Event 1 design optimizes toward.
