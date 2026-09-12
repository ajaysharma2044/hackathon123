# Field Researcher Guide

The field researcher program for Event 1: the role, the methodologies it borrows from, how many we
need, how they are trained, and a quick-reference field card. This is the human half of the sensor
network described in [live-research-os.md](live-research-os.md); the note structure it produces is
[field-note-system.md](field-note-system.md), and the moments it watches for are
[critical-incidents.md](critical-incidents.md).

The defining tension: field researchers must make the event *better* (more help, faster routing,
fewer broken resources) while observing it *honestly* (neutral, non-leading, fact-before-
interpretation). A researcher who is only an extractor degrades the experience; a researcher who
becomes a full-time mentor stops being an observer. The role is designed to hold both.

## Methodologies we borrow from — and what survives a 72-hour technical event

We do not copy any methodology wholesale. Each is translated into something that works in a
compressed, high-energy build weekend where the participants' attention is the scarce resource.

| Methodology | What we take | What we drop (doesn't fit 72h) |
|---|---|---|
| **Contextual inquiry** | observe work *in situ*, ask about the thing happening right now | the multi-hour master-apprentice session; we get minutes, not hours |
| **Critical Incident Technique** | anchor on specific, recent, consequential moments (a switch, a failure) | retrospective-only recall; we catch incidents live |
| **Rapid ethnographic assessment / RQI** | multiple observers, shared codebook, fast team synthesis | the weeks of immersion; we compress to shift-by-shift war-room synthesis |
| **Participant observation** | a friendly expert circulating, low-intrusion presence | going native / long embedding; researchers stay neutral and disclosed |
| **Process tracing** | reconstruct the causal chain of a decision from evidence | formal within-case causal inference; we stay at L1/L2 and hedge |
| **Diary studies** | lightweight self-capture at moments of change | daily long diaries; replaced by telemetry-fired micro-prompts + checkpoints |
| **Organizational ethnography** | attention to context, roles, coordination | the thick description; we keep context snapshots, not field monographs |

The net: **trained observers running critical-incident spotting and very short contextual
interviews, synthesized every few hours by leads** — rapid qualitative inquiry adapted to a
hackathon. The depth comes from triangulating many light observations against telemetry and
artifacts, not from long sessions.

## What a field researcher actually does

```
CIRCULATE assigned zone  →  OBSERVE natural team interaction  →  RECORD critical incidents + decisions
   →  NOTICE switching / confusion / repeated problems / unusual use cases
   →  when a trigger warrants: a SHORT contextual interview (or flag a DEEPER one)
   →  coordinate with mentors (route help, surface broken resources)
   →  SEPARATE observation from interpretation in every note
   →  flag candidate teams for follow-up  →  bring it all to war-room synthesis
```

**They DO:** circulate assigned + roaming zones; record critical incidents and important decisions;
notice and log switching, confusion, and repeated problems; flag unusual use cases; run short
in-the-moment interviews and deeper triggered ones; coordinate with mentors; capture environmental
context; flag follow-up candidates; keep fact and interpretation separate; and participate in
war-room synthesis.

**They value-add (Part XXIX):** help find the right mentor, route support, surface a broken doc or a
down API, spot a team that needs help before it asks, collect suggestions, and escalate systemic
event problems to organizers. This is what makes a researcher a welcome presence rather than a
clipboard. **But** when a researcher does real technical mentoring, it is logged as a
`mentor_interaction` with intensity — otherwise the observational role is quietly corrupted (a
researcher who fixed a team's auth can't neutrally observe that they "struggled with auth").

**They NEVER:** record screens continuously; record private messages; capture keystrokes; secretly
listen or record audio; infer protected traits; build a hidden person score; interrupt
unnecessarily; pressure anyone into answering; or degrade the event to get data. These are the
permanent no-go boundaries from [live-research-os.md](live-research-os.md) and
[capture-risk-register.md](../capture-risk-register.md).

## Staffing — reasoned, not guessed

The scarce resource is **researcher-hours with coverage continuity**, not participant-minutes
([event1-instrumentation-plan.md](../event1-instrumentation-plan.md) capacity model). A useful
heuristic: one field researcher can hold **genuine coverage of ~6–8 teams** (primary) while
roaming over a few more — beyond that, notes get shallow and incidents are missed. At ~4 builders
per team, that is roughly **one field researcher per ~25–30 participants** for primary coverage,
plus leads, interviewers, and a steward who do not carry a primary zone.

Alternatives by event size (generate the option, let the sold studies pick the point):

| Event size | Teams (~4/team) | Field researchers | Leads | Interviewers | Data steward | Ops lead | Total research staff | Model |
|---|---|---|---|---|---|---|---|---|
| **80** | ~20 | 3 | 1 | 1 (can be a lead) | 1 (shared) | 1 (can be the lead) | **~5–6** | single zone, roaming-heavy |
| **120** | ~30 | 4 | 1 | 2 | 1 | 1 | **~8–9** | 2 zones + roaming |
| **150** | ~38 | 5–6 | 2 | 2 | 1 | 1 | **~11–12** | assigned zones + roaming floaters |
| **200** | ~50 | 7–8 | 2 | 3 | 1 | 1 | **~14–16** | zoned, with a dedicated interview pod |

Roles can overlap at small sizes (a lead also interviews; the ops lead is also the steward) and
should separate as size grows — the **data steward must stay separate from interpretation duty** at
every size, because consent/burden/provenance integrity is a conflict-free job.

### Shifts, coverage windows, and overnight

A 72-hour event is not staffed uniformly. Coverage follows the signal:

```
ARRIVAL/FORMATION/BUILD-START   heavy   (the choice-set + problem-selection signal is born here)
EARLY + MID BUILD               heavy   (first failures, first help, the switching window)
LATE BUILD                      medium  (completion pressure; interview the already-decided)
DEEP NIGHT (≈2am–7am)           light   (a skeleton roamer; DO_NOT_INTERRUPT dominates — see
                                         interruption-policy.md; sleep hours are a bad-moment)
SUBMISSION + DEMO               heavy   (retrospective-as-interview, judging observation)
```

Researchers work overlapping ~8-hour shifts with a **30-minute handoff** into the war room so no
team's thread is dropped at a shift change. Overnight is deliberately thin: the highest-signal
moments are daytime, and pinging exhausted builders at 4am is exactly the kind of burden that
damages the experience.

### Roaming vs assigned zones

Neither alone. **Assigned zones** give continuity (the same researcher follows a team's arc, which
is what makes a [team trajectory](team-trajectories.md) coherent). **Roaming floaters** catch what a
zoned researcher misses and cover the gaps. The [coverage map](../../schema/006_live_research.sql)
(`research_assignment`: primary / secondary / roaming, with `last_observed_at` / `last_prompted_at`
/ `last_interviewed_at`) is the tool that keeps teams **neither ignored nor over-interrupted**.

## Training program

Researchers are trained before the event on:

```
neutral observation · avoiding leading questions · quote vs inference · probing without bias
capturing context · identifying critical incidents · consent boundaries · when NOT to ask
how to not interrupt flow · evidence tagging · research ethics · commercial confidentiality
escalation protocols
```

The training is mostly *calibration*: everyone codes the same three recorded/role-played incidents
and compares, until the codebook and the fact/interpretation split are shared vocabulary rather than
personal style. Inter-observer agreement on the same scene is the readiness bar, not a lecture.

## Quick-reference field card

Small enough to laminate. This is what a researcher carries.

```
┌─────────────────────────── FIELD CARD ───────────────────────────┐
│ WRITE THE FACT FIRST.  What did you SEE or HEAR? Quote exactly.    │
│ Then, separately and labelled: your reading — AND a competing one. │
│   BAD : "Team hated Supabase."                                     │
│   GOOD: "Said 'we're wasting time on auth'; removed Supabase ~12   │
│          min later."  INTERP: auth friction may have driven it.    │
│          ALT: teammate already knew the alternative.               │
│                                                                    │
│ APPROACH A TEAM:  "Mind if I watch for a minute? Ignore me."       │
│   Ask about the thing happening NOW, not feelings in general.      │
│   One question. Let silence do the work. Never finish their story. │
│                                                                    │
│ ASK WHEN:  after a switch · after help resolves · after submit ·   │
│            at a meal · in a booked slot.                           │
│ DO NOT ASK WHEN:  near a deadline · mid-debug · judging · hardware │
│            test · presenting · asleep.  (See interruption-policy)  │
│                                                                    │
│ IF YOU HELP TECHNICALLY → log it as a mentor interaction (it's a   │
│   confounder, not free data).                                      │
│ NEVER:  screens · keystrokes · DMs · secret audio · person scores  │
│   · protected traits · pressure.  When unsure → DON'T, and ask a   │
│   lead.                                                            │
│ FOUND A BROKEN DOC / DOWN API / STUCK TEAM?  Route help first,     │
│   then log it. You are here to help too.                           │
└────────────────────────────────────────────────────────────────────┘
```

## The one line a researcher should internalize

> **You are a helpful expert who happens to be paying careful, honest attention — not a camera.**
> The best note is a specific thing that actually happened, written so a stranger could tell the
> fact from your guess about it.
