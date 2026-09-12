# STATE — Read This First

The honest synthesis of everything researched, organized to *discover* the truth rather than
confirm a desired one. Everything else in `docs/` is raw material; this is the standing
understanding, and it is meant to be updated as evidence arrives.

## Correcting the frame

The research so far was run with the conclusion baked in — the agent briefs asked *"what will
companies pay for a research product,"* *"who buys developer research,"* *"how high can the
engagement price go."* That is confirmation, not discovery. It produced a rich map, but a biased
one: it went looking for reasons the premium model works and mostly found them, because that is
what it was told to look for.

The correct question is not *"why will companies pay $100K for this."* It is:

> **There may be valuable unmet needs around elite builders, product research, recruiting, R&D,
> and events. What is actually true — and what is the greatest real economic pain this specific
> group of builders can solve?**

The answer might be a $25K sponsorship, a $150K research study, a $300K innovation engagement,
something we haven't named, or nothing. This document holds what the evidence says, honestly
scored, including the parts that hurt.

## The four layers, kept separate

Evidence ≠ Claim ≠ Hypothesis ≠ Decision. Collapsing them is how bias enters.

**EVIDENCE** (raw, sourced observations — what someone actually said or what a price actually is):
- *"Getting 30 experienced developers who actually use our SDK is always difficult"* — pattern
  across Anthropic, Vercel, Stripe, Adyen, Databricks job postings [verified at ATS source]
- Datadog, in print: their research data *"skews toward adoption of cloud platforms more than the
  general population"* [verified]
- A B2B research study's sample + incentives = ~45% of project cost; hard-to-reach specialists
  cost $200–500 per completed response [published agency rate cards]
- Cal Hacks (3,000 hackers) tops out at $50K published; CMU sells two semesters of CS recruiting
  access for $10,000 [published prospectuses]
- Stripe commissioned a developer-economics study in 2018 and never refreshed it [verified 404]
- TreeHacks already flies in, houses, and feeds 1,000+ hackers [verified]

**CLAIM** (aggregated interpretation, with confidence and support/contradict counts):
- *"Developer-tools companies have real, recurring, currently-unmet needs to understand developers
  they don't already have as customers."* — **support: ~20 independent sources** (job postings,
  published methodologies, stale reports). **contradict: 0 direct**, but all evidence is
  supply-side. Confidence: **medium-high** as a description of need; **unproven** as budget.
- *"Elite student builders are a defensible research cohort because they're unbuyable on panels."*
  — support: panel economics, incidence data. contradict: the representativeness objection below.
  Confidence: **medium**.

**HYPOTHESIS** (a testable business proposition, not yet tested):
- *"Some buyer will pay ≥$75K for a study built on ~200 elite student builders."* — **untested.**
- *"The premium fly-in event is worth funding as the vehicle for that study."* — **untested, and
  partially contradicted** (see bear case).

**DECISION** (what we commit to): **none yet.** No entity, no venue, no date, no price should be
committed until the gating unknown below is tested.

## Epistemic status of the load-bearing questions

| Question | Status | Why |
|---|---|---|
| Do comparable research studies sell for $25–250K? | **KNOWN** | Published rate cards, federal contract data |
| Does hackathon *sponsorship* cap around $30–38K? | **KNOWN** | Cal Hacks $50K/3,000, React Summit $38K, CNCF 200-person events $5–25K |
| Do dev-tools firms have unmet developer-understanding needs? | **LIKELY** | ~20 supply-side sources; but need ≠ budget-for-this |
| Do vendors only see their own users? | **KNOWN** | Datadog/SO/Vercel/Retool all state it |
| **Will any buyer pay ≥$75K for a study on 200 elite _student_ builders?** | **UNKNOWN** | **Zero demand-side evidence. This is the whole ballgame.** |
| Are elite student builders seen as representative enough to study? | **UNKNOWN** | Council flagged hard; evidence both ways |
| Does the confidential multi-client (omnibus) model work in *qualitative*? | **UNKNOWN** | No vendor found doing it |
| Is the premium fly-in event the differentiator? | **CONTRADICTED** | TreeHacks already does it at 5x scale |
| Can we charge more per sponsor than Cal Hacks on an *attention* basis? | **CONTRADICTED** | 200 < 3,000 people; worth a fraction, not a multiple |
| Will a University Recruiting Lead fund this? | **CONTRADICTED** | NACE: ~$2,850/school median budget |
| Everything about actual buyer behavior | **UNTESTED** | We have not spoken to one buyer |

## The bear case, at full strength

Given equal weight, because it wasn't before:

1. **The whole edifice is supply-side.** Every datapoint is a comparable price or an inferred need
   from a job posting. **Not one is a buyer committing real money at a real price for this.** A job
   post proving a team *measures* activation is not proof they'll *pay an outsider* to study it.
2. **Elite students may be the wrong panel.** The council's sharpest line: *"hand-picked elites
   are among the least representative humans alive."* A buyer wanting to know why *median*
   developers churn may see 200 MIT/Stanford builders as actively misleading. The
   unrepresentativeness that makes them prestigious may make the research less valuable, not more.
3. **The research validity is genuinely attackable.** n≈200, self-selected, Hawthorne effect
   (observed builders behave differently), and prize money contaminates the "free tool choice" the
   whole experiment depends on. A sophisticated research buyer will see all of this.
4. **A cheaper substitute exists for most of it.** A customer advisory board is $22–55K; a
   UserInterviews panel session is $98 + incentive; a company can run its own 25 interviews. The
   buyer's default is not "nothing," it's "the thing I already do."
5. **The event is the most expensive way to collect the data.** If the product is research, the
   $280K flown-in event is a data-collection apparatus in a costume. You could buy the same
   interviews for a fraction and skip the logistics entirely.
6. **Two-person operational load.** A 200-person flown-in event, 8–12 parallel research
   engagements, and a sponsor pipeline is not a two-person job, and nothing in the research
   changes that.

## Pain-point clusters, scored honestly

Discovered (not assumed) from the evidence, scored on raw dimensions — kept separate so the
weighting stays visible rather than hidden in one magic number.

```
CLUSTER A — "We can't see the developers who chose someone else"
  frequency HIGH · severity MED-HIGH · recurrence HIGH · current-spend MED
  buyer-authority MED · unsatisfiedness HIGH · evidence-quality HIGH (supply-side)
  → strongest discovered pain. But WTP-for-this UNKNOWN.

CLUSTER B — "We can't measure if AI tools actually make developers faster"
  frequency HIGH · severity HIGH · recurrence HIGH · current-spend HIGH
  buyer-authority MED · unsatisfiedness HIGH · evidence-quality HIGH
  → METR (19% slower, felt 20% faster) + Cognition ("unsolved") + Anthropic ("can't measure").
  A neutral party is uniquely positioned here — no vendor can credibly say its own tool slows
  people down. Possibly the single best wedge. WTP UNKNOWN.

CLUSTER C — "Recruiting is easy; knowing who can actually build is hard"
  frequency HIGH · severity MED · recurrence HIGH · current-spend HIGH (screens, take-homes)
  buyer-authority MED · unsatisfiedness MED · evidence-quality MED
  → real, but crowded (Karat, CodeSignal, HackerRank) and FCRA-constrained.

CLUSTER D — "Onboarding/activation friction we can't diagnose"
  frequency HIGH · severity MED-HIGH · recurrence HIGH · current-spend MED
  → named in ~8 job postings as "time to first X." Winston Francois sells exactly this at $20-35K.
```

None of these was assumed; all emerged from the evidence. All share the same missing variable:
**proven willingness to pay for a solution shaped like ours.**

## What the buyer is actually deciding (and why price could be high — or not)

The reason a study *could* be worth six figures is not "comparable hackathon sponsorship." It's
that the buyer is making a large decision under uncertainty:

```
WTP ≤ Expected economic value of reducing the decision's uncertainty
```

If a company is making a $20M product bet and a study materially reduces the uncertainty, $150K
is cheap. **But this cuts both ways** — it's only true if (a) the decision is genuinely that big,
(b) our study genuinely reduces its uncertainty, and (c) the buyer believes both. We have
evidence for none of the three yet. The value-of-information logic is the *route* to high pricing;
it is not evidence that the pricing is achievable.

## Falsification criteria for the core thesis

The thesis — *"a buyer will pay ≥$75K for research built on this cohort"* — should be treated as
**rejected or weakened** if:

- 10–15 qualified buyers consistently value it below $30K
- existing vendors (UserInterviews, dscout, a CAB) are seen as equivalent and cheaper
- buyers don't consider elite student builders representative enough to act on
- procurement structurally blocks multi-client event studies
- the instrumentation is seen to compromise participant authenticity
- no buyer will pre-commit cash before the event exists

## The one gating unknown, and the cheapest way to resolve it

After ~15 research passes we have a thorough **supply-side** map and **zero demand-side**
evidence. The entire business rests on one untested assumption: *someone will pay.*

By the information-gain logic — high uncertainty × enormous business impact × low cost to test —
the single highest-value next action is not more desk research, a venue, or a prospectus. It is
**a falsification attempt against willingness-to-pay**:

1. Pick the sharpest wedge (currently Cluster B — "is AI actually making developers faster," where
   a neutral party has a structural advantage no vendor has).
2. Build one artifact: a mock findings report on invented data, clearly labeled, showing a buyer
   exactly what they'd receive.
3. Take it to 10 named buyers (start: the research-ops and startup-program doors in
   [target-list.md](target-list.md), not DevRel).
4. Ask an open question first — *"tell me about the last time you needed to understand how
   developers use a new product"* — not *"would you buy our hackathon."*
5. Try to close a **$5–15K paid pilot**. A signed check is the only evidence that matters.
6. If no check in ~4 weeks of real attempts, the premium thesis is weakened and the answer may be
   $30K sponsorships — or a different business entirely.

## What this means for Event 1

**Event 1 should not be designed or funded yet**, because its economics depend entirely on the
untested unknown. The honest sequence:

```
test willingness-to-pay  →  IF a buyer commits, the study defines the event
                            (size, tracks, duration, instrumentation fall out of what was sold)
                         →  IF no buyer commits, we learned it cheaply and pivot
```

This reconciles "understand everything so we can have our first event" with the evidence: we now
understand the *world* thoroughly, and the one thing standing between us and a real Event 1 is a
single buyer saying yes at a real price. Everything about the event — 120 vs 200 builders, 2 vs 3
days, which tracks — is a downstream optimization that the first sold study will answer for us.

## Status line

```
Strongest discovered pain      "measuring real AI-on-developer productivity" (Cluster B)
Most likely buyer              Research Ops / Product Research / startup-program owner
Evidence-supported price       $25K-$250K (comparables) — but WTP-for-this UNKNOWN
Largest unresolved question    will any buyer pay real money for THIS cohort?
Most valuable next research     10 open buyer interviews + 1 paid-pilot attempt
Strongest evidence against     all evidence is supply-side; elites may be unrepresentative;
                               n≈200 validity is attackable; the event is the costliest data path
Decision committed             none — correctly
```

---

## Convergence with the council evidence-pass (Aarush, 2026-09-12)

An independent LLM-council + web-evidence pass ([hackathon123-council-verdict.md](hackathon123-council-verdict.md))
reached the same core conclusion from a different direction — pre-sell before building — and
tested the market-existence priors this synthesis left as UNKNOWN. Three of its findings update
the standing view:

**1. The demand category is real and funded — but the backend alone is not a business.**
Developer-behavior intelligence is a funded, growing category: SlashData has sold it to Microsoft/
Google/Amazon/Intel/Meta for ~20 years; Common Room raised ~$52.9M (~$300M val, ~$15M ARR);
Reo.Dev raised $4M for "developer intent intelligence." This moves the CLAIM *"buyers pay for
developer intelligence"* from LIKELY toward **KNOWN**. **But the caution matters as much as the
proof:** Orbit (acquired by Postman, product closed) and Common Room (being acquired by Zoom) both
got absorbed into GTM platforms rather than thriving standalone. **Passive developer-intelligence
alone did not sustain a company.** The event + proprietary panel is the thing that could make this
version defensible where passive-signal plays were not — but the backend is not a business by
itself.

**2. There is a competitor already running the front-end: Cerebral Valley.**
Premium, invite-only, elite-AI-builder events with lab sponsorships — revenue from tickets
($199–$2,999) plus sponsorships, with deals reportedly seeded there. This did not surface in the
research sweep and it should have. **The event is table stakes; someone already runs the elite
version.** The unoccupied white space is the rigorous causal + longitudinal research instrument
fused onto the panel — which nobody has done — not the event itself.

**3. A fourth, cheaper first move — Wedge D: run the first study on someone else's event.**
Instead of building a 200-person event to get a panel, **layer the research instrument onto an
existing elite event** (an MLH/HackMIT-tier hackathon, or Cerebral Valley / AI Engineer). You get
the elite panel, real behavioral data, and a live retention test **without six-figure logistics or
one-shot reputation risk** — and you produce the first *real* (not mock) sponsor deliverable. This
dissolves the chicken-and-egg in [roadmap.md](roadmap.md): the event's economics don't have to be
solved before the research thesis is tested.

### Revised next move

The single first step is unchanged and now doubly-sourced: **build one polished sample report and
pitch 5–10 named buyers for a $5–15K paid pilot; no signed commitment in ~4 weeks means the event
would have flopped too.** Add two refinements from the council pass:

- **Probe offer-shape, not just demand.** In the same calls, test whether buyers want a *report*
  or *talent access* — recruiting has proven, quantified WTP (~$35K cost-to-hire; hackathon hiring
  ~$5–10K/hire, ~4.2 qualified hires/event) and may be the easier first check. Sell the deliverable
  and the access; let the buyer tell you which they'll pay for.
- **Line up Wedge D in parallel** — one existing elite event to run the first real study on, so the
  second sales call can show real data instead of a mock.

### What still holds against both analyses

- **Internal validity survives every optimistic reframe.** n≈200, Hawthorne, prize-contaminated
  "free choice" → this is *directional leading-indicator behavioral signal on an early-adopter
  cohort*, not representative market research. Sell it as **depth** (observed causal behavior)
  against SlashData's **breadth** (12,500+-dev surveys). Overselling generalizability loses the
  sophisticated buyer in one meeting.
- **Panel retention** into 7/30/90-day tracking is the untested engine of the compounding moat —
  the council's evidence pass agrees this is the real supply-side risk (recruiting elite builders
  is easy; *retaining* them into longitudinal tracking is not).
- **Willingness-to-pay at the specific price for THIS deliverable** is still the one thing no desk
  research resolves. The category is proven; the specific check is not.
