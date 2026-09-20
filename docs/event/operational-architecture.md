# Event Operations Architecture

How Event 1 is actually **run** — the organization, the logistics, the judging, the people — and how
every part of it ties into the [Live Research OS](../research-ops/live-research-os.md). This is the
master document for [`docs/event-ops/`](.); the runnable structure is
[`schema/007_event_ops.sql`](../../schema/007_event_ops.sql) plus three engines
([`staffing_model.py`](../../engine/staffing_model.py),
[`judging_assignment.py`](../../engine/judging_assignment.py),
[`org_graph.py`](../../engine/org_graph.py)).

There are **two organizations running one event on one timeline.** The event org makes the weekend
excellent; the research org makes it an instrument. They are deliberately separate so the hard
constraint stays enforceable — *if experience and research conflict, experience wins*
([participant-experience.md](../research-ops/participant-experience.md)) — and they are deliberately
interlocked so the research is produced by the event happening, not bolted on.

```
                         ┌──────────────────── EVENT DIRECTOR ────────────────────┐
                         │            (the weekend is excellent + on time)          │
   LOGISTICS · FINANCE/SPONSORSHIP · MARKETING · OPERATIONS · TECH/AV · DESIGN ·
   PARTICIPANT EXPERIENCE · JUDGING & AWARDS · MENTORSHIP · SAFETY
                         │                                                          │
                         │   ── the event the builders experience ──                │
                         ▼                                                          ▼
   builders arrive → consent → build (free ≥40%) → get help → submit → demo → judged → awards
                         │                                                          │
                         │   every natural action emits evidence (FEEDS_RESEARCH)   │
                         ▼                                                          ▼
                         └──────────────── RESEARCH DIRECTOR ──────────────────────┘
                                   (the weekend is a traceable instrument)
   RESEARCH OPS · FIELD RESEARCHERS · INTERVIEWERS · ANALYSTS · DATA STEWARD
                         = the Live Research OS (docs/research-ops/)
```

## The operational layers

The event, read as a stack of operational concerns — each owned, each with a home in the schema and
a doc:

| # | Layer | What it covers | Where |
|---|---|---|---|
| 1 | **Organization** | the committee, directors, reporting lines, who owns what | [org-chart-and-roles.md](org-chart-and-roles.md) |
| 2 | **People supply** | recruiting + staffing counts for organizers, mentors, judges, volunteers, crew, researchers | [org-chart-and-roles.md](org-chart-and-roles.md); [`staffing_model.py`](../../engine/staffing_model.py) |
| 3 | **Logistics** | venue, food, travel/fly-in, check-in, wifi/power, hardware, swag, overnight, safety, A/V, signage | [logistics.md](logistics.md) |
| 4 | **Run of show** | the 72-hour timeline: opening, meals, workshops, mentor hours, submission, expo, finals, closing | [run-of-show.md](run-of-show.md) |
| 5 | **Mentorship** | help-first support that also reveals blockers (shared with the research layer) | [../research-ops/mentor-system.md](../research-ops/mentor-system.md) |
| 6 | **Judging & awards** | science-fair + finals, the judge formula, stack-ranking, prizes, IP | [judging-system.md](judging-system.md); [`judging_assignment.py`](../../engine/judging_assignment.py) |
| 7 | **Volunteers & crew** | shift-based day-of help and paid domain crew | [volunteers-and-crew.md](volunteers-and-crew.md) |
| 8 | **Safety** | code of conduct, emergency plan, incident handling (operations data, firewalled from research) | [logistics.md](logistics.md) |
| 9 | **The correlation graph** | how every role ties to every other, within and across the two orgs | [role-correlations.md](role-correlations.md); [`org_graph.py`](../../engine/org_graph.py) |

## Grounded in how real hackathons run

None of this is invented from scratch. The structure is adapted from how elite events actually
operate — MLH's organizer guide (committee teams, the science-fair judging formula), HackMIT's
~20-person student org, Hack the North's functional teams, and the premium fly-in model of TreeHacks
and Cal Hacks (funded, admission-blind travel). The sourced detail and what we take vs change for a
Cornell-only premium event is in [prior-hackathons.md](prior-hackathons.md).

## The tie-in: ops is the research sensor network

The single most important idea: **the operational roles are the research sensors.** We do not run a
separate data-collection apparatus alongside the event — the event *is* the apparatus, lightly
instrumented and honestly disclosed. Every edge below is a real, typed relationship in
[`org_graph.py`](../../engine/org_graph.py) (`FEEDS_RESEARCH`):

```
OPERATIONAL ROLE            →  RESEARCH EVIDENCE IT PRODUCES
Registration / Check-in     →  the pre-event baseline + the consent grants (the gate for everything)
Mentor                      →  a logged mentor_interaction: blocker, friction, intensity (the confounder)
Judge                       →  structured evaluation of the built artifact
Operations (event app+keys) →  behavioral telemetry: team formation, submissions, tool usage, switches
Field researcher            →  the human sensor network's field notes (fact ≠ interpretation)
```

And the reverse: **the research rules constrain the operational roles** (`CONSTRAINED_BY`), so the
sensor network can never degrade the event or a participant:

```
RESEARCH RULE               CONSTRAINS
Burden budget + consent gate   mentors (≤20s logs, scoped), field researchers (ask only within budget)
Interruption policy            anyone who would prompt a team near a deadline or during sleep
Client-view gate               sponsorship — clients get aggregate findings, never raw/individual data
No person scoring              everyone — judging ranks projects, mentors log friction; nobody scores a person
```

## Two firewalls the operations must respect

1. **Operations data ≠ client research data.** Mentor-queue depth, food counts, room capacity, and
   **safety incidents** are operations data — used to run the event, never sold, never in a client
   deliverable. Choice/behavior/artifact/interview/outcome are research data, delivered only in
   aggregate. The schema enforces the sharpest case: `safety_incident.is_research = false` and
   `travel_grant.affects_admission = false` are CHECK constraints, not hopes.
2. **The research org reports in but is not overruled.** The Research Director coordinates with the
   Event Director, but owns study validity — a finding can come back negative, and a sponsor who
   funds the event gets instrument review and early access, **not** editorial control
   ([../research-ops/client-protocols.md](../research-ops/client-protocols.md)).

## Staffing, in one line per size

From [`staffing_model.py`](../../engine/staffing_model.py) (ratios sourced in
[prior-hackathons.md](prior-hackathons.md)); full breakdown in
[org-chart-and-roles.md](org-chart-and-roles.md):

```
~180 builders → ~45 teams → ~12 committee heads + ~18 mentors (1:10) + judges by formula
                + ~9 volunteers + ~5 crew + ~7 field researchers + research leads + 1 data steward
```

Judges are not a ratio but a **formula** — `J = ceil(teams × rounds × minutes / window)` — the same
one MLH publishes; for ~45 teams at 3 rounds × 4 min in a 2-hour window that is ~5 judges per
science-fair window, scaled up for parallel category rounds ([judging-system.md](judging-system.md)).

## What must never happen, operationally

The event-side mirror of the research no-go list:

```
• admission biased by ability to pay or by a travel-grant request (travel is admission-blind)
• a sponsor engineer judging the neutral grand prize, or a judge scoring their own team
• a safety/CoC incident treated as research data or surfaced to a client
• a volunteer doing covert research, or any capture the participant didn't consent to
• a participant feeling like the logistics exist to farm them rather than host them
```

## How to read the rest of this directory

Start here, then: [prior-hackathons.md](prior-hackathons.md) for the evidence base;
[org-chart-and-roles.md](org-chart-and-roles.md) for every role and count;
[role-correlations.md](role-correlations.md) for how they interlock (the graph);
[logistics.md](logistics.md), [judging-system.md](judging-system.md),
[run-of-show.md](run-of-show.md), and [volunteers-and-crew.md](volunteers-and-crew.md) for the
operational domains. The research half lives in [`docs/research-ops/`](../research-ops/), and the two
meet in the correlation graph.
