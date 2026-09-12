# Client-Specific Live Research Modules

How the *one* instrument serves different buyers without becoming five different events. This is
layer 16 of the master [live-research-os.md](live-research-os.md) (Parts XXXII, XXXVI, XXXIII): the
same human sensor network, the same evidence graph, the same consent gate — pointed at a different
question per client. The engine mix for Event 1 is fixed in [event1-design.md](../event1-design.md)
(**1 Research primary + 1 Activation + 1 R&D challenge + ≤1 sponsorship floor**); this document is
the live protocol each engine runs *during* the 72 hours.

> **The instrument does not bend to the buyer.** A client buys a *question* and a *grain of
> rigor* ([measurement.md](../measurement.md)'s tiering), not a conclusion. Sponsors get instrument
> review and early access — never editorial control. Findings come back negative. A client whose
> protocol would require covert capture, individual surveillance, or a person score cannot be sold
> the research tier; the no-go list ([consent-design.md](consent-design.md)) is not negotiable.

## The five engines and what each one is trying to reconstruct

Each engine maps to a `question_tree.module` in [`006_live_research.sql`](../../schema/006_live_research.sql)
and an `engine` tag on the [research_question_backlog](../../schema/006_live_research.sql). The
grain of rigor column is the honest promise from [measurement.md](../measurement.md): you get **one**
well-powered study per event.

| Engine | Module | Core question | Rigor grain | ICP |
|---|---|---|---|---|
| **Research** | `technology_choice` | why considered / rejected / switched | primary experiment (1) | dev-facing co. whose deciding behavior is invisible to telemetry |
| **Product-dev** | `product_dev` | expectation vs friction vs missing capability | observational (2–3) | product team exploring a solution space |
| **R&D** | `rd_failure` | which approaches converge, which fail, why | N prototypes + failure map | org with a high-uncertainty parallelizable problem |
| **Activation** | `activation` | does the incentive buy adoption or only activation | funnel + 7/30/90 retention | co. running credits / a startup program |
| **Design-partner** | (opt-in flow) | which team is worth a paid partnership | individual, consented | sponsor seeking a continuation partner |

## Per-engine live protocol — what to OBSERVE, what to ASK

The discipline is the master loop's: **observe first, ask only at the fresh moment if the burden
budget allows** ([live-research-os.md](live-research-os.md)). Most incidents ask nothing. "ASK"
below is the micro-prompt that fires *only* when a trigger warrants it and the team's
`interrupt_window` is open.

### Research / greenfield tool choice (`technology_choice`)

```
OBSERVE  choice set at t0 (what was reachable) · consideration (what was opened/read/tried)
         · selection (what the repo/telemetry shows chosen) · switching (calls stop, dep removed)
ASK      why considered?  why rejected (the invisible non-choice)?  what triggered the switch?
```

The prize is the **unconstrained baseline** and the **why-not** — the rejected alternative is
invisible to any sponsor's own first-party telemetry ([measurement.md](../measurement.md) #5).
`ChoiceSet` ([research-data-model.md](../research-data-model.md)) is what turns "72 signups" into
"chosen 41% of the time when two equally-reachable competitors were unincentivized."

### Product-development (`product_dev`)

```
OBSERVE  feature use (which surfaces touched) · workarounds (the hack around a missing capability)
         · unexpected uses (the tool used for something it was not built for)
ASK      what did you expect here?  where did it fight you?  what capability was simply missing?
```

The `decision_episode` product-journey fields (`expectation → friction → workaround → switched_to`)
carry this. The workaround is the highest-signal row: it is a demand statement with a timestamp.

### R&D (`rd_failure`)

```
OBSERVE  hypotheses (the stated approach at t0) · experiments (what was actually tried)
         · failures (the assumption that broke) · convergence (do independent teams land together)
ASK      why this approach?  what failed and at what assumption?  what is the next test?
```

Parallel teams are an R&D search only for high-uncertainty, parallelizable, evaluable,
prototypeable-in-event problems ([event1-design.md](../event1-design.md) #15–16). The deliverable
is **N independent prototypes + the value-of-failure map** — the map of which approaches died and
where is often worth more than the winner. Uses the `RD_REASONING` trajectory
(`hypothesis → why_hypothesis → experiment → result → assumption_failed`).

### Activation (`activation`)

```
OBSERVE  exposure (required task done) · activation (the named technical moment, e.g. first
         successful call) · integration (shipped in the submitted project) · retention (7/30/90)
ASK      did the credit change what you'd have done?  what made it worth continuing — or not?
```

The one question worth the contract: **does a $100 credit create sustained adoption, or only
subsidize temporary activation?** If `Credits↑ ⇒ Activation↑` but `Retention_30d` is flat, the
client learns its startup-credit spend buys temporary usage ([research-data-model.md](../research-data-model.md)).
Operational definitions (`activation`, `repeated_use`, `retention_30d`) are pre-registered before
the event per [measurement.md](../measurement.md), never tuned after.

### Design-partner (opt-in intro flow)

```
1  team opts in            DESIGN_PARTNER_DISCOVERABILITY scope granted in the ledger
2  just-in-time re-prompt   before any intro is surfaced (consent-design.md)
3  aggregate signal only    the client sees continuation signals, not a dossier, until the team says yes
4  warm intro               a two-sided opt-in; the team controls its own first-hand work evidence
5  continuation             → a paid design partnership, no equity grab (event1-design.md #20)
```

This is the only engine that produces individual-grain output, and only through the participant's
own consented work evidence — never through the client research view. It never runs on a team that
has not opted in, and an opt-in is revocable ([consent-design.md](consent-design.md)).

## What clients see live — and what they NEVER see

The split is enforced structurally by the `ClientView` gate ([live-research-os.md](live-research-os.md),
`assert_clean`) and the query gate in [`capture.py`](../../engine/capture.py): a client-facing query
runs under `AGGREGATE_RESEARCH`, which is **aggregate-only with min cell size 8**.

```
CLIENTS SEE LIVE (aggregate, suppressed)        CLIENTS NEVER SEE
  aggregate module progress                       individual participant surveillance
  help/support demand by category                 raw field notes / mentor logs
  active-team count, challenge progress            unreviewed quotes (pre human-gate coding)
  artifact previews (consented submissions)        any person score / employability / trait inference
  scheduled observation windows                    the live research interface itself (no interference)
```

A client does not get a live feed that lets them *act on* a single team mid-event — that would
contaminate the baseline and turn the event into a sales floor. The live client view is a
dashboard of aggregate progress ([dashboard-spec.md](dashboard-spec.md)), not a window into people.
The only exception is a design-partner intro the participant themselves opted into and confirmed.

## The final client report — how the evidence integrates

One instrument, three evidence types, one traceable report ([evidence-graph.md](evidence-graph.md)):

```
QUALITATIVE   coded interview excerpts + observer notes (the "why", human-gated)
BEHAVIORAL    brokered-key telemetry + checkpoints (the "what", server-side ground truth)
ARTIFACT      repo / deploy / dependency manifest (the honest cross-check on self-report)
        └──────────────── all three point back to raw evidence via claim_evidence ──────────────┘
```

Report order is fixed by [measurement.md](../measurement.md) and is not the client's to reorder:

1. **Precise friction diagnosis** — "38 of 72 stalled at the same auth step, median 41 min lost,
   here are 12 describing it." Actionable, needs no inference.
2. **The unconstrained baseline** — what elite builders reach for when nothing is required.
3. Funnel shape, switching narratives, retention — in that order.
4. **Statistics in the appendix**, with honest intervals (n≈150–200, self-selected track choice,
   Hawthorne effect, elite ≠ median developer). Every client-facing claim enumerates both
   supporting *and* contradictory evidence before promotion — a `claim` without its `CONTRADICTS`
   rows cannot become a `finding`.

Leading with the diagnosis and the baseline, and burying the p-value, is what makes the report
credible to a buyer sophisticated enough to spot a dressed-up n.

## Capacity and the no-competitor rule

```
MAX SIMULTANEOUS ENGAGEMENTS  ~3–4 non-competing  (event1-design.md #39: capacity + contamination)
  · one sponsor per competitive category                  (protects the choice baseline)
  · study-compatibility check before accepting a second    (shared instrument, non-conflicting asks)
  · no two directly-competing studies in one event          (a clean A-vs-B cannot serve both A and B)
  · free-choice surface ≥40% held regardless of sponsor count (below 25% w/ ≥4 sponsors = contamination)
```

Four is not a quota to fill — it is a ceiling set by the burden budget and the contamination risk.
A fifth engagement that would force required exposure past the free-choice floor, or that competes
with an accepted client, is declined. Saying no to the wrong client is how the second year of
sponsorships happens.
