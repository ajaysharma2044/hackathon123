# Measurement Design

What specifically to look for, and how to actually capture it with 200 people over 3 days.

## The constraint nobody plans around: you get one well-powered question

200 builders sounds like a lot. It isn't, once it's divided.

If the anchor sponsor's product is relevant to ~60% of participants, that's ~120 people. Split
into an exposure arm and a comparison arm, that's ~60 per arm. At that size you can reliably
detect only **large** differences — roughly 20–25 percentage points. Subtler effects are
invisible.

Run five sponsor experiments in parallel and every one of them is underpowered garbage.

**Design rule:**

```
1  primary experiment      the anchor sponsor's question, properly powered
2-3 secondary studies      observational, no control arm, diagnosis-focused
N  activation sponsors     exposure + usage counts only, sold as such
```

Sell the tiers honestly. An $8K activation sponsor gets usage numbers, not a research report.
Promising five companies a rigorous study on one 200-person event is how the second year of
sponsorships doesn't happen.

## What the sponsor is actually buying at n=200

Not a p-value. The statistical comparison is the weakest thing you produce.

The valuable outputs, in order:

**1. Precise friction diagnosis.** *"38 of 72 builders stalled at the same step in auth setup.
Median time lost: 41 minutes. Here are 12 of them describing it in their own words."* That is
directly actionable, needs no inference, and is worth the contract on its own.

**2. The unconstrained baseline.** When nothing is required, what do 200 elite builders
actually reach for? This is the single most valuable number in the whole event and it exists
**only if you protect unconstrained surface**. If every track carries a required tool, this
disappears. Hold the line on it in sponsor negotiations.

**3. The funnel shape with real drop-off points.** Where the curve bends, not just where it ends.

**4. Switching narratives.** What happened in the 20 minutes before someone abandoned the
product — the trigger, the alternative chosen, the stated reason.

**5. Post-event retention.** The number no other hackathon can produce at all.

**6. Segment differences.** Directional at this n. Report as signals worth confirming, not as
findings.

Lead every report with 1 and 2. Put the statistics in the appendix with honest intervals.

## The primary experiment: structure

```
REQUIRED EXPOSURE     every relevant participant completes one real task with Product A
        ↓                  (disclosed in the challenge terms — never covert)
FREE CHOICE           any tool, any approach, for the rest of the event
        ↓
OBSERVE               who keeps using it, who switches, when, and why
        ↓
FOLLOW-UP             7 / 30 / 90 days
```

The comparison arm is participants on tracks without the required exposure. Not a clean RCT —
track choice is self-selected — so control for track and builder type, and state the limitation
rather than dressing it up as randomized.

Where randomization *is* cheap, use it: which of two onboarding paths a participant gets, which
docs version, which starter template. Those are genuine randomized comparisons inside a
non-randomized event, and they're free.

## Operational definitions — write these before the event

These are decisions, not observations. Fix them in advance or they become dials that get turned
until the report looks good.

| Term | Must specify |
|---|---|
| `exposure` | Completed the required task, or merely assigned it? |
| `activation` | The specific technical moment — first successful API call? First working integration? Name the event. |
| `meaningful action` | Shipped something using the product in the submitted project? Or a usage threshold? |
| `repeated use` | Unprompted use after the required task, separated by how long? |
| `voluntary_reuse` | Any use after the event ends, or use in a new context? |
| `retention_30d` | Active in the last 7 days at day 30, or any use since day 7? |
| `tool_switched` | What evidence counts — stopped calls? Declared switch? Competitor in the repo? |

Pre-register these in the experiment record alongside the hypothesis.

## Capture mechanics — the part that actually decides whether this works

Six instruments. The first one matters more than the other five combined.

### 1. Brokered API keys — do this

Issue per-participant scoped credentials for sponsor products **through your registration
system**. Every call, timestamp, error, and silence is then server-side ground truth.

This single decision gives you:

- activation timing without self-report
- exact drop-off points in onboarding
- error and retry patterns — the friction data
- **abandonment**, observed directly rather than inferred

It is the only clean solution to the `tool_switched` problem, which is otherwise the hardest
thing you're trying to measure. Make key brokering a **term of the research sponsorship**, not
a favor you ask for later. A sponsor who won't provision keys through you can't buy the
research tier — they can buy activation.

Consent scope: participants must know their usage of that product is instrumented. Disclosed in
the challenge terms, scoped in the consent record.

### 2. Checkpoint capture

Structured check-ins every ~6 hours. Five questions, under 60 seconds: what are you building,
what tools are you using right now, what's blocking you, what did you change since last
checkpoint, how stuck are you (1–5).

Compliance is the whole problem. Tie it to something they want: mentor slot booking, meal
access, judging eligibility. Voluntary checkpoints get ~30% response and the non-responders are
exactly the people whose data you need.

The "what tools right now" field, sampled every 6 hours, is your switching timeline.

### 3. Observer logs

8–12 trained floaters (mentors, staff) logging friction in real time against a fixed taxonomy —
`friction_type`, `severity`, `stage`, free text. Trained on the codebook, not improvising.

This is where the qualitative side deploys at scale. One person cannot observe 200 builders;
twelve trained observers with a shared vocabulary can, and their logs are codeable.

### 4. Artifact capture at submission

Repo, deploy, commit history, dependency manifest — with consent. The dependency file is an
honest record of what was actually used, independent of what anyone reported.

### 5. Stratified exit interviews

**30–40, not 200.** Deliberately sampled to span outcomes: adopted, switched, never activated,
never touched it. The never-activated group is the most informative and the least likely to
volunteer.

15 minutes, recorded with consent, semi-structured.

### 6. Follow-up

7 / 30 / 90 days. Response rates decay hard — 7-day might hit 60%, 90-day maybe 25% without
incentive. Budget real incentives for the follow-up waves; retention data is the thing no
competitor has and it is worth paying for.

Remember `occurred_at ≠ observed_at` on everything learned through a survey.

## Selection is an instrument too

What to look for in the ~200, and why it isn't just "the most impressive applicants":

**For panel quality:** stratify deliberately across builder type — technical builder, founder,
product, designer, business builder — and across experience level. An all-senior panel can't
tell you anything about onboarding friction for newcomers, which is usually the sponsor's actual
question.

**For research validity:** capture application evidence in structured form — past projects, work
samples, current stack, tool history, track preference, team preference. These become covariates
in the model, and the pre-existing stack is essential: someone already using the sponsor's
product is measuring retention, not adoption, and mixing them corrupts both.

**For the long game:** you can eventually compare application evidence against observed
performance and learn which signals actually predict good builders. That only works if
application data is structured from event 1. Free-text applications are unanalyzable later.

## Honest limits to state in the report

- Self-selected track choice, not randomized assignment
- Elite panel — generalizes to elite student builders and early adopters, not median developers
- Hackathon conditions are time-compressed and atypical of normal work
- n supports direction and diagnosis, not precise effect size
- Follow-up response bias: people who kept using it are likelier to answer

Sponsors sophisticated enough to pay $100K are sophisticated enough to spot these. Stating them
first is what makes the rest credible.
