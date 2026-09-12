# Historical Structural Analysis

How organizations have historically extracted value from competitions, contests, prizes, open
innovation, hackathons, and sponsored research — reconstructed structurally, to learn what our
event can and cannot be. Grounded in repo evidence ([innovation-budget.md](innovation-budget.md),
[venture-upside.md](venture-upside.md), [event-comps.md](event-comps.md), [who-pays-for-research.md](who-pays-for-research.md))
plus the innovation-contest academic literature. Epistemic tags: **[F]** fact/verified · **[O]**
observed in repo evidence · **[I]** inferred structural knowledge · **[H]** hypothesis · **[U]** unknown.

## The one academic result that governs the R&D use

**Boudreau, Lacetera & Lakhani, "Incentives and Problem Uncertainty in Innovation Contests,"
*Management Science* 2011 [F]** (verified via search). Two competing forces as the number of
competing teams rises:

1. **Parallel-path / max-of-N:** more teams → higher chance at least one finds an *extreme-value*
   solution.
2. **Effort dilution / rivalry:** more teams → each individual's chance of winning falls → each
   exerts *less* effort → mean solution quality drops.

**The extreme-value force dominates for HIGH-uncertainty problems; the effort-dilution force
dominates for LOW-uncertainty problems.** Structural lessons, load-bearing for our R&D engine
([rd-engine.md](rd-engine.md), coded in [engine/value_engines.py](../engine/value_engines.py)):

- A parallel contest / hackathon is **advantageous** when the problem is *uncertain* (nobody knows
  the best approach), *parallelizable*, *prototypeable* quickly, and has a *clear evaluation*.
- It is **inferior** for *low-uncertainty* problems, where one focused expert team beats a diluted
  crowd — and for problems needing scarce domain knowledge or equipment.
- There is an **interior optimal number of teams**, not "more is better." (Reproduced in code.)

Related [I]: Terwiesch & Ulrich (idea portfolios / parallel paths), Girotra-Terwiesch-Ulrich (the
value of a portfolio is in its *best* member, not its average) — the same max-of-N logic.

## Structural reconstruction of the major historical models

Each entry: **who paid · mechanism · output · economics · why it works/fails · lesson for us.**
Numbers carry their tag; where a number is not in evidence it is **[U]**, never invented.

### Prize challenges / grand challenges — DARPA, NASA, XPRIZE
- **Who paid:** government / foundations. **Mechanism:** one hard problem, many independent teams,
  large winner-take-most purse, months-long. **Output:** a breakthrough capability (autonomous
  driving, etc.). **Economics [O]:** DARPA purses $1M–$3.5M; NASA/Luminary Labs vehicles $2.8M–$15M;
  **XPRIZE's own 990 shows operating cost ≈ the purse** — running the prize costs about what it pays.
- **Why it works [I]:** high uncertainty + parallelizable + clear evaluation = textbook max-of-N.
- **Why it fails [I/O]:** slow, expensive to run, winners not always implemented, needs a crisp
  evaluation function. **Lesson:** our event is the *compressed, cheaper* version — but only for
  problems that fit in 48–72h and evaluate cleanly.

### Open-innovation marketplaces — InnoCentive/Wazoku, Topcoder, Kaggle
- **Who paid:** corporations post problems. **Mechanism:** a standing marketplace of solvers,
  variable/success-based reward. **Economics [O]:** InnoCentive average solver award ~$20K (some
  >$100K); Topcoder paid **$100K for a single NASA crater-detection challenge** and holds
  **$200K+ enterprise contracts**; Kaggle sponsored competitions custom, purses historically $200K–$1M.
- **Why it works [I]:** parallel search on well-specified, evaluable problems (algorithms, data).
- **Why it fails [I]:** needs a machine-scorable objective; weak for open-ended product/UX work;
  solver ≠ implementer (the winning solution still has to be productionized). **Lesson:** we can host
  a Topcoder/Kaggle-style *challenge track*, but our differentiator is observing *building behavior*,
  not just scoring a submission.

### Corporate/enterprise hackathons run by contractors
- **Economics [O] (federal contract data, innovation-budget.md):** logistics-only $28K–$68K; a
  branded multi-event series $240K–$300K; **a full enterprise hackathon with real delivery $600K–$2.5M**
  (Accenture/DLA generative-AI hackathon **$1.27M**). **Lesson:** the ceiling exists *when real output
  is attached to the event* — pure logistics is cheap, delivered R&D/product is not.

### Innovation consulting — IDEO, BCG X
- **Economics [O]:** IDEO federal engagements cluster **$0.5M–$3M**; BCG X takes fees + equity in
  co-created ventures. **Lesson:** the product-development use has a large-budget comparable; a
  hackathon that produces *N independent prototypes + a solution-space map* competes on cost and
  variety, not on senior-designer polish.

### University-industry structures — SRC, MIT Media Lab, Stanford HAI, affiliate programs
- **Economics [O]:** SRC **~$2.28M/member/yr**; MIT Media Lab **~$560K/member**; Stanford HAI
  **$1M / $5M tiers with a directed research wallet**; CIFE/BSAC/UT-Austin **$10K–$300K**. **Key
  structural lesson [O]:** they **bundle recruiting into the cheapest tier and charge the premium for
  research + IP + a directed wallet.** Access is cheap; the research/IP layer is what clears six
  figures. This is the single most transferable pricing structure ([innovation-budget.md](innovation-budget.md)).

### Research firms & panels — LF Research, Forrester/IDC, expert networks, omnibus
- **Economics [O]:** LF Research commissioned studies **$25K–$95K+** with a published slot
  structure ($50K/$15K/$5K); Forrester TEI/IDC **$50K–$250K+**; Gartner seat **$70,928/yr**; expert
  networks **$1,000–$1,400/call**; omnibus **$1,000/question, confidential per client**. **Lesson:**
  the research use has the deepest, most-proven budget — and the omnibus model (one fieldwork event,
  many confidential clients) is exactly the multi-client structure our event can copy.

### Accelerators / venture studios / talent programs
- **Economics [O] (venture-upside.md):** YC $500K/7%, EF/Antler $90–250K/6–12%, Z Fellows $10K at a
  $1B cap; no elite-student program charges a per-hire fee. **Lesson:** the talent/venture use
  monetizes through fund economics or philanthropy, **never a placement fee** — and the Carta case
  warns that mixing data + investment poisons trust.

### Bug bounties / activation programs / startup credits
- **Economics [O]:** ETHGlobal sponsor tracks **$10K–$20K each**; startup credits are huge face value
  (AWS up to $200K, Google $350K) but **$0 organizer-captured** and mostly subsidize temporary usage
  **[H — the credit→retention question, question-catalog Q1]**. **Lesson:** activation is real
  sponsor spend, and the *"do credits create retention?"* question is itself a high-VOI research product.

## What history repeatedly says (patterns, with confidence)

| Pattern | Evidence | Confidence | Applies to us |
|---|---|---|---|
| Parallel contests win for **high-uncertainty, parallelizable, evaluable** problems | Boudreau/Lakhani [F] + DARPA/InnoCentive [O] | **High** | R&D & innovation engines only for problems that fit these |
| **More teams is not better** — interior optimum from effort dilution | Boudreau/Lakhani [F] | **High** | cap teams per challenge; coded in optimal_teams() |
| **Solver ≠ implementer** — prototypes rarely reach production | InnoCentive/Kaggle/hackathon [I/O] | Med-High | sell prototypes + follow-on, never "production" |
| **Bundle access cheap, charge for research/IP/wallet** | SRC/HAI/affiliates [O] | **High** | the pricing structure to copy |
| **Curation + real output** is what lets a small event charge | CCDC caps, Reality Hack $65–95K [O] | Med-High | protect exclusivity + attach a deliverable |
| **Novelty wears off / logistics are brutal** — many programs shut down | On Deck, buildspace, Miami Hack Week [O] | Med | recurring value must come from data/relationships, not the party |
| **Mixing data with investment poisons trust** | Carta [O] | High | keep research and any venture vehicle firewalled |

## The honest boundary this history draws

A hackathon is **not** a general-purpose corporate-value machine. History shows it is *unusually
good* at a specific intersection — **compressed, parallel, high-uncertainty, prototypeable,
evaluable building by a curated crowd, observed** — and *inferior* to internal teams, consultants,
universities, panels, or standing marketplaces almost everywhere else. The commercial engines
([company-opportunity-map.md](company-opportunity-map.md)) exist to find that intersection per
company, and to say **NO FIT** when it isn't there.
