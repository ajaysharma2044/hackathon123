# Participant Experience Engine

The hard constraint, made into a measured system. The research only exists because the event is
genuinely excellent; the moment it stops being excellent, the panel degrades and the data goes with
it ([STATE.md](../STATE.md), [live-research-os.md](live-research-os.md)). So participant experience
is not a nice-to-have we hope for — it is a **tracked outcome with its own feedback loop**, and the
research system is required to evaluate *itself* against it.

## The two minds the event must satisfy at once

```
THE IDEAL PARTICIPANT THINKS                  THE IDEAL CLIENT THINKS
  "I built a cool thing, met good people,       "We got an unusually rich reconstruction of how
   got useful help, ate well, learned a lot,     technically capable future users actually made
   and occasionally answered a few relevant      decisions, struggled, switched, built, and
   questions."                                   continued — from real artifacts and observed
                                                 behavior, not survey claims."
NOT                                           NOT
  "I spent the weekend in a corporate study."   "We got a logo on a banner and a résumé book."
```

If the participant's line is not true, we redesign — **even if it costs data.** The client's line is
only reachable *through* the participant's; a farmed cohort produces defensive, low-signal behavior
(and doesn't come back for the longitudinal follow-up that is the real asset).

## What we track from the participant side

The `experience_pulse` table ([`schema/006_live_research.sql`](../../schema/006_live_research.sql))
captures, lightly and optionally:

```
EXPERIENCE QUALITY            fun · freedom · flow state · mentor usefulness · social quality ·
                              community · learning · prize motivation
FRICTION & LOGISTICS          wait time · food · sleep · technical friction · confusion
THE RESEARCH ITSELF           research burden felt · "did you feel watched?" · "were prompts
                              annoying?" · privacy concern · IP concern · sponsor pressure
```

The research-about-the-research block is the unusual part and the important one. Most events measure
satisfaction; almost none measure whether their *own instrumentation* made the event worse. We do,
because that signal is what protects the golden goose.

## The feedback loop

The pulse is not a post-hoc survey — it feeds back into the live system within the event:

```
experience_pulse signal            →  live response
prompts_annoying ↑                 →  tighten the burden cap / widen the prompt gap (participant-burden.md)
felt_watched ↑                     →  pull back observer density in that zone; re-disclose
mentor_usefulness ↓ in a category  →  add mentor capacity there (event-adaptation.md)
wait_time ↑ at the mentor queue    →  open office hours (an operational intervention)
flow ↓ mid-build                   →  check whether checkpoints/prompts are mistimed
```

Every such change is logged as an [event intervention](event-adaptation.md) with its validity
impact, so we never forget we adjusted the environment — including adjustments made *for the
participants' sake*.

## The questions the research system must ask about itself

Answered honestly, in the exit interview and the pulse:

```
Did research interactions make the event worse?
Did participants feel watched or farmed?
Were the field researchers helpful, or just extractive?
Were the micro-prompts relevant, or annoying and random?
Did the mentor logging make mentors feel bureaucratic?
Did the research actually improve the support they got?
Would a strong Cornell builder tell their friends "that hackathon was amazing"?
```

That last question is the single acceptance test. If the honest answer trends "no," the research
design is wrong regardless of how rich the data looks.

## How each part of the system earns its place in the experience

The design goal is that **almost every research touch also does something for the builder**, so it
reads as help or structure rather than a tax:

| Research mechanism | What the builder gets from it |
|---|---|
| Checkpoint | routes them to a relevant mentor / meal slot / judging eligibility ([checkpoints.md](checkpoints.md)) |
| `/blocked` signal | summons help *right now* while logging the blocker |
| Mentor note | they sought the help; the note is the mentor's, not theirs ([mentor-system.md](mentor-system.md)) |
| Micro-prompt | fires only at a fresh, relevant moment; one line; skippable ([micro-prompts.md](micro-prompts.md)) |
| Field researcher | a friendly expert who routes help and surfaces broken resources ([field-researcher-guide.md](field-researcher-guide.md)) |
| Demo-as-interview | they were pitching anyway; the prompts just structure it |
| Follow-up | incentivized, and a genuine check-in on their project ([longitudinal-followup.md](longitudinal-followup.md)) |
| Artifact capture | zero prompts; reads their repo, which they wrote anyway |

The mechanisms that **harm** the event — and are therefore excluded regardless of data value — are
the mirror image: anything covert, any person-scoring, any cadence that taxes the build, any
recruiting/VC disclosure the participant didn't clearly opt into, and any prompt near a deadline or
during sleep ([interruption-policy.md](interruption-policy.md)).

## The walk-through test

[event1-live-playbook.md](event1-live-playbook.md) walks the event hour-by-hour from a participant's
seat and counts: *how many times do they encounter "research," does each one have a purpose, and do
they have long uninterrupted build blocks?* The target for a typical participant is **only a handful
of explicit research touches across 72 hours** — a baseline, a few checkpoints tied to things they
wanted, maybe two well-timed prompts, and possibly one exit interview — inside long stretches of
uninterrupted building with useful help on tap.

> The perfect research experience is one the participant barely notices as research — because it
> mostly *was* building, deciding, getting help, and demoing, lightly structured and honestly
> disclosed. That is not a constraint on the research. Over the 90-day window, it **is** the
> research.
