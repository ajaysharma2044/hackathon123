# 7 / 30 / 90-Day Longitudinal Follow-Up

Layer 15 of [live-research-os.md](live-research-os.md): the retention asset no other hackathon can
produce. The event ends Sunday, but the *research object* — WHAT CONTINUED AFTER THE EVENT, and WHY
([live-research-os.md](live-research-os.md)'s team story) — only resolves over the following 90
days. This is where a weekend of behavior becomes a retention curve, and where the single most
valuable, least-reproducible data in the whole system is captured.

> **Why this is the differentiator.** Every hackathon can tell a sponsor who *used* a product over
> a weekend. Almost none can tell them who was *still using it 30 days later, and who quietly
> switched away* — the question [measurement.md](../measurement.md) calls the one no competitor has.
> Retention is the output; activation was only the input ([research-data-model.md](../research-data-model.md),
> the credit→activation→retention chain).

## Cornell's same-campus advantage (a structural retention asset)

Event 1 is **Cornell-only** ([event1-design.md](../event1-design.md)). This is not a recruiting
constraint — it is the reason the follow-up works. A national hackathon scatters its cohort across
the country on Sunday night; a Cornell cohort is **still reachable on the same campus** at day 7,
day 30, and day 90.

```
SAME-CAMPUS FOLLOW-UP ASSETS
  physical reachability   in-person 30-day check-ins, not just email into the void
  shared institution       a Cornell channel (club, Slack, dorm, course) keeps the cohort warm
  repeat contact           the same people are reachable for Event 2 — the panel compounds
  higher base response     proximity lifts every wave above the email-only decay curve
```

No other hackathon structure has this. It is also *why* the year-round panel (below) is feasible at
all: you cannot build a longitudinal panel out of a cohort you can never find again.

## What to capture at 7 / 30 / 90 days

Minimal, incentive-tied, and mapped to the `checkpoint` kinds `FOLLOWUP_7 / _30 / _90`
([`006_live_research.sql`](../../schema/006_live_research.sql)). The point is survival signals, not
a long survey — the burden budget ([consent-design.md](consent-design.md)) still applies, and only
participants who granted `LONGITUDINAL_FOLLOWUP` are contacted.

```
                                                 7d   30d   90d   grain
  project continuation      still building it?    ●     ●     ●    team
  tool retention            still using the tool?  ●     ●     ●    participant / product
  tool switching            switched to what, why? ●     ●     ●    participant / product
  team continuation         team still together?         ●     ●    team
  startup continuation      incorporated / raising?       ●     ●    team (VC_DISCOVERABILITY)
  product continued use     voluntary_reuse in a new context?  ●   ●    participant
  new blocker               what stopped you since?  ●     ●     ●    team
  reason for abandonment    why did it stop?         ●     ●     ●    team
  new artifact              shipped / deployed since?      ●     ●    team
  design-partner continuation  talks progressing?          ●     ●    team (DESIGN_PARTNER_*)
```

Each answer is a `FOLLOWUP` burden-channel debit and, where it reveals a behavior, an
`EvidenceEvent` whose `occurred_at` is *when the behavior happened*, not when the survey caught it
(see the three clocks below). Self-report is flagged `is_self_report=true` and kept distinct from
any brokered-key signal that corroborates or contradicts it.

## Follow-up interview triggers and prioritization

Most follow-up is the structured check-in. A *deeper* interview is sampled only when a case is
unusually informative — the same adaptive-sampling discipline as the live event
([adaptive-questioning.md](adaptive-questioning.md)), now over the 90-day window. Priority is
ordinal; the war room works the list top-down under the interview burden budget.

```
TRIGGER                              PRIORITY   why it earns a conversation
  continued project                    HIGH      the rare success arc — what made it stick
  abandoned project                    HIGH      why it died is the finding sponsors can't get elsewhere
  unexpected product RETENTION         HIGH      kept using something we didn't predict → a real signal
  unexpected SWITCHING                 HIGH      dropped a tool we expected to stick → the why-not
  R&D continuation                     MED       an event approach that survived contact with reality
  design partner progressing           MED       a continuation lead, opt-in, participant-controlled
  unusual adoption pattern             MED       used it for something it wasn't built for
  contradictory case                   HIGH      behavior that disconfirms an emerging claim (negative_case)
```

The **contradictory case** is deliberately over-weighted: the system hunts the disconfirming
example, not just more of the confirming one ([live-research-os.md](live-research-os.md)'s
confirm-*and*-contradict loop). A 90-day follow-up that only re-interviews the people who kept
using the product manufactures a flattering retention curve — response bias
([measurement.md](../measurement.md)'s honest limits) — so the abandoners and switchers are
priority targets, not afterthoughts.

## Incentives: response rates decay, so budget for them

Follow-up response is not free and it does not hold. Per [measurement.md](../measurement.md),
without incentive:

```
  wave     ~response (no incentive)     implication
  7-day        ~60%                     still warm; light incentive holds it high
  30-day        ~40% (decaying)         the curve is bending — incentive matters now
  90-day       ~25%                     without real incentive, you lose 3 of 4 — and the 1 who
                                        answers is the one who kept using it (biased up)
```

Budget **real** incentives for every wave — the retention data is the thing no competitor has and
it is worth paying for ([event1-design.md](../event1-design.md): follow-up is *never dropped*). The
same-campus advantage lets incentives be things proximity makes cheap and welcome (an on-campus
event, a meal, priority for Event 2), not just cash. State the residual response bias in the report
regardless; incentives reduce it, they do not erase it.

## occurred_at ≠ observed_at on everything learned late

This is the correctness invariant that the whole follow-up depends on, and it is enforced, not just
documented ([`capture.py`](../../engine/capture.py) `retention_events`; the three clocks in
[research-data-model.md](../research-data-model.md)):

```
  occurred_at    WHEN THE BEHAVIOR HAPPENED      — the survival / retention axis
  observed_at    when the survey caught it        — may be >> occurred_at for self-report
  available_at   when it became queryable         — drives "as of D" point-in-time queries

  A reuse that OCCURRED on day 9 but was LEARNED via the day-30 survey belongs in the DAY-9 bucket.
  Running survival on observed_at would silently push every self-reported reuse into a later
  bucket and corrupt the entire retention curve.
```

So retention, survival, and time-to-event **always** run on `occurred_at`. Survey lag is measured
as `observed_at − occurred_at`, not hidden. The 30-day survey is a *measurement instrument pointed
at the past*, not a timestamp — treating it as a timestamp is the most common way a longitudinal
curve lies.

## Why this is the seed of a year-round panel

The 90-day window is not the end state. It is the proof-of-concept for the asset the whole business
compounds on:

```
  Event 1 cohort  →  7/30/90 follow-up  →  a reachable, consented, characterized panel
                                          →  re-contactable for Event 2 and beyond
                                          →  a longitudinal builder panel no one else has
```

A single hackathon is a snapshot; a *same-campus cohort you can find again* is a panel. Combined
with `LONGITUDINAL_LINKAGE` (joining event data to Club OS / prior-event history, strictly opt-in —
[consent-design.md](consent-design.md)), Event 1 becomes the first wave of a standing research
panel of elite builders. That is the data asset that compounds only if the event keeps happening
([live-research-os.md](live-research-os.md)'s one hard constraint) — which is exactly why the
weekend experience, and the follow-up incentives that keep the cohort willing to answer, are
protected spending and not costs to trim.

**Honest limits, restated for the long horizon:** follow-up response bias favors the satisfied;
elite Cornell builders generalize to elite student builders and early adopters, not median
developers; and a 90-day window catches early retention, not durable multi-year adoption. State
each in the report ([measurement.md](../measurement.md)). The panel makes these *tractable over
time* — successive waves can measure the bias directly — but Event 1 alone does not resolve them.
