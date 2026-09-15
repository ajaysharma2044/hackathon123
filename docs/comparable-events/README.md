# Comparable Events -- Sourced Benchmark Base

Real benchmark data on past hackathons and comparable elite/premium builder events, gathered to (a) design our own premium ~200-person event and (b) arm sponsor sales calls with numbers that survive scrutiny.

**Sourcing standard:** every datapoint carries a retrieved source URL + an as-of date + a confidence tag (`stated` / `high` / `medium` / `speculation`). Values that are not publicly disclosed are marked `UNKNOWN` -- never invented. Vendor-marketing and unverifiable figures were deliberately excluded (each file lists what was excluded and why). Assembled 2026-09-14 from ~40 events across six research streams.

> Data-gathering only. No scoping, build, or pricing decision is made here. See [../STATE.md](../STATE.md) for the standing understanding and the one gating unknown (willingness-to-pay for this cohort).

## Contents

| File | What it is |
|---|---|
| [comparable-events-dataset.md](comparable-events-dataset.md) | The sourced dataset: MLH/Devpost ecosystem scale, sponsorship ladders + recruiting/prize benchmarks, an elite-collegiate roster (9 events), a premium/AI-builder roster (~14 events), and outcomes + developer-intelligence-market evidence. Each cell has a source + date + confidence. |
| [comparable-events.json](comparable-events.json) | Machine-readable companion mirroring the numeric core of the dataset (sortable/filterable/auditable). |
| [hackathon-benchmarks-trends.md](hackathon-benchmarks-trends.md) | Cross-cluster synthesis: 10 trends, event-design implications for hosting our own event, and an honest "what the data cannot tell us." |
| [sponsor-pitch-benchmark-brief.md](sponsor-pitch-benchmark-brief.md) | Call-ready, quotable numbers organized by pitch beat, with a "do NOT quote these" list of excluded figures. |
| [qualitative-data-collection-methods.md](qualitative-data-collection-methods.md) | Sourced menu of how comparable programs actually collect qualitative data (survey response rates, panel costs, judging-as-data, incentive design) with recommendations for our capture design. |

## Headline findings

- A **~200-person event is the premium-invite tier**, not big-collegiate -- the Cerebral Valley AI Summit (200-350, invite-only, $199-$2,999) already occupies exactly that position.
- **Elite selectivity runs ~2.5-14%** (TreeHacks 6.7%; Anthropic's own hackathon 2.5%). 200 accepted implies roughly 1,500-8,000 applications.
- **Sponsorship benchmarks $10-50K** for a premium student hackathon (Cal Hacks); premium AI events keep pricing inquiry-only, so there is no public benchmark above ~$50K.
- **Full fly-in provisioning (travel + housing + food)** is the premium differentiator, used by only TreeHacks and Cal Hacks -- expensive, and what makes "elite" tangible.
- The **buyer market for developer intelligence is real and funded** (Zoom acquired Common Room 2026; Reo.Dev $11.3M Series A; SlashData) -- but the **event alone is table stakes**: the frontier labs already run their own free hackathons pulling 13,000-46,000 applicants. This corroborates the [council verdict](../hackathon123-council-verdict.md): the defensible white space is the neutral longitudinal **research instrument**, not the event.

## Provenance note

Six parallel research agents produced this. Web-fetch infrastructure (Firecrawl) was rate-limited/quota-exhausted throughout, so figures came via general web search + page fetch + direct PDF reads; PDF-locked sponsorship prospectuses (e.g. HackPrinceton, PyCon) are mostly `UNKNOWN` and a re-run with working fetch access could recover them. The agents caught and excluded several fabricated/contradicted figures (a false $266.8M acquisition price, a spurious prize total, an untraceable revenue claim, a misattributed study statistic) -- flagged in each file's gaps section.

*Source notes for these files are maintained in the working vault; these are exported copies. Obsidian `[[wiki-links]]` inside the individual files refer to companion vault notes.*
