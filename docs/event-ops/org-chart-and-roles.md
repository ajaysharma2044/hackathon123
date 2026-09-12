# Org Chart & Roles

Every role that runs Event 1 — organizers, crew, mentors, judges, volunteers, participants, and the
research staff — what each does, how many we need, and who reports to whom. The role catalog is the
`staff_role` / `org_unit` schema in [`007_event_ops.sql`](../../schema/007_event_ops.sql); the counts
come from [`staffing_model.py`](../../engine/staffing_model.py); the reporting lines and cross-org
edges are in [`org_graph.py`](../../engine/org_graph.py) and drawn out in
[role-correlations.md](role-correlations.md). Ratios are sourced in
[prior-hackathons.md](prior-hackathons.md). The research org is defined in
[../research-ops/event1-staffing.md](../research-ops/event1-staffing.md); it is included here so the
whole picture is in one place.

## The seven layers of people

```
ORGANIZER   directors + committee heads who plan and run the event
CREW        paid/lead staff executing a domain day-of (AV, F&B, logistics, registration)
MENTOR      technical help (help-first; also a disclosed research sensor)
JUDGE       evaluates the built artifacts
VOLUNTEER   shift-based day-of help (check-in, floaters, runners, room leads)
RESEARCH    the Live Research OS staff (field researchers, interviewers, analysts, steward)
PARTICIPANT the builders — the reason the whole thing exists
```

## The org chart

```
                              ┌─────────────────┐        ┌───────────────────┐
                              │  EVENT DIRECTOR │◄──────►│ RESEARCH DIRECTOR │
                              └────────┬────────┘  coord └─────────┬─────────┘
       ┌───────────┬───────────┬───────┼──────────┬─────────┐       │
       ▼           ▼           ▼       ▼          ▼         ▼       ▼
  Logistics   Finance/    Marketing  Operations  Tech/AV  Judging  Research
    Lead      Sponsorship   Lead       Lead       Lead    & Awards  Ops Lead
       │        Lead          │         │           │      Lead        │
       │          │           │    ┌────┴────┐      │        │    ┌─────┼───────┐
       ▼          ▼           ▼    ▼         ▼      ▼        ▼    ▼     ▼       ▼
   crew +     sponsor      social  Volunteers Participant AV   Judges Field  Inter-  Analysts
   vendors    liaisons     team     (shifts)  Experience  crew  panel  Res.  viewers    │
                                              Lead                                   Data Steward
                              ┌───────────┐                                          (conflict-free)
                              │ Mentor Lead│──► Mentors      ┌───────────┐
                              └───────────┘                 │ Safety Lead│──► on-call + medical
                                                            └───────────┘
```

Two directors, deliberately. The **Event Director** owns the experience; the **Research Director**
owns study validity and can publish a finding a sponsor dislikes. They coordinate; neither overrules
the other's core mandate. Everything safety-related escalates to the **Safety Lead** and, if
critical, to the Event Director.

## Layer 1 — Organizers (committee)

Roughly **fixed** in count regardless of size (they scale by adding crew/deputies, not by
multiplying heads). The twelve units:

| Unit / Role | Owns | Key correlations |
|---|---|---|
| **Event Director** | the whole event; the experience is their P&L; final call | everything reports up |
| **Research Director** | study designs, pre-registration, honest findings | coordinates with Event Dir; owns the research org |
| **Logistics Lead** | venue, schedule, swag, prizes, food, resources | Operations depends on this ([logistics.md](logistics.md)) |
| **Finance/Sponsorship Lead** | sponsor $$, vendor payment, budget, sponsor liaisons | **staffs** sponsor mentors + category judges |
| **Marketing Lead** | promotion, website, social, photography | constrained by `PUBLIC_MEDIA` consent |
| **Operations Lead** | the hacker experience day-of; runs volunteers | depends on Logistics; runs the event app/keys |
| **Tech/AV Lead** | wifi, power, event app, brokered keys, stage AV, submissions platform | judging + telemetry depend on it |
| **Design Lead** | brand, signage, stage, swag design | supports Marketing + Ops |
| **Participant Experience Lead** | the pulse, logistics quality, the hard-constraint veto | the builders' advocate ([../research-ops/participant-experience.md](../research-ops/participant-experience.md)) |
| **Judging & Awards Lead** | the judging system, panel, prizes, IP | depends on Ops (stations) + Tech (platform) ([judging-system.md](judging-system.md)) |
| **Mentor Lead** | mentor roster, shifts, the support queue | staffed partly by Sponsorship ([../research-ops/mentor-system.md](../research-ops/mentor-system.md)) |
| **Safety Lead** | code of conduct, emergency plan, incidents | every escalation ends here or at the Director |

## Layer 2 — Crew (paid domain execution)

The people who *do* the domain work day-of, under a committee head. Sized ~**1 per 40** participants
(plus fixed leads): **AV crew**, **F&B lead + servers/vendors**, **logistics/setup crew**,
**registration lead**, **stage manager**. Crew are paid because their reliability is load-bearing —
a missed meal or a dead mic degrades the experience for everyone at once.

## Layer 3 — Mentors

Help-first technical support, the **mixed model** (assigned + pool). Density ~**1 per 10** builders
for an elite event ([event1-design.md](../event1-design.md)). Categories mirror the tracks:

```
GENERAL · FRONTEND · BACKEND · INFRA · CLOUD · DB · AI_ML · AGENTS · DATA · ORIE_OPT · ECE
HARDWARE · ROBOTICS · PRODUCT · DESIGN · DOMAIN · COMPANY_ENGINEER
```

Recruited from Cornell TAs/tutors, alumni, industry, professors, and **sponsor engineers** (the last
disclosed and, when they help heavily with their own product, logged as a confounder —
[../research-ops/mentor-interventions.md](../research-ops/mentor-interventions.md)). Full mentor
operations: [../research-ops/mentor-system.md](../research-ops/mentor-system.md).

## Layer 4 — Judges

Not a ratio but a **formula**: `J = ⌈teams × rounds × minutes / window⌉`
([`judging_assignment.py`](../../engine/judging_assignment.py), sourced from MLH). For ~45 teams at 3
rounds × 4 min in a 2-hour window, that is ~**5 judges per science-fair window** — scaled up for
parallel **category/sponsor rounds**, so the practical panel is larger. Judges are a **diverse
panel**; **sponsor judges** decide only their category prize, never the neutral grand prize; a judge
is never assigned their own team. Details: [judging-system.md](judging-system.md).

## Layer 5 — Volunteers

Shift-based day-of help, ~**1 per 20** participants (more at check-in and meal peaks): **check-in,
floaters, runners, room leads, mentor-desk support, photography, social, documentation.** Recruited
~10 days out, rotating shifts, thin overnight. Volunteers **route help and surface problems but do
not do research** unless trained and logged. Details:
[volunteers-and-crew.md](volunteers-and-crew.md).

## Layer 6 — Research staff

The Live Research OS org, sized to coverage (field researcher ~**1 per 28**), with a **conflict-free
data steward** (exactly one, never shared). Full detail:
[../research-ops/event1-staffing.md](../research-ops/event1-staffing.md).

## Layer 7 — Participants

The **~150–200 builders** in **~45 teams** (2–5 each). Curated, Cornell-only, stratified across
builder type and experience so the panel can speak to onboarding friction, not just senior speed
([measurement.md](../measurement.md)). They are hosted, not farmed — the entire operation exists to
give them one of the best weekends they'll attend.

## Counts by size (from `staffing_model.py`)

Illustrative, computed from the sourced ratios + the judge formula; a human can override any line
with reasons.

| Size | Teams | Committee heads | Mentors (1:10) | Judges (formula) | Volunteers (1:20) | Crew (1:40) | Field researchers (1:28) |
|---|---|---|---|---|---|---|---|
| **80** | 20 | 12 | 8 | ~3–4/window | 4 | 2 | 3 |
| **120** | 30 | 12 (+deputies) | 12 | ~4/window | 6 | 3 | 5 |
| **150** | 38 | 12 (+deputies) | 15 | ~5/window | 8 | 4 | 6 |
| **200** | 50 | 12 (+deputies) | 20 | ~5/window ×parallel | 10 | 5 | 8 |

> The judge count is per science-fair window; multiple parallel category rounds and finals raise the
> total panel. Above ~200 the coordination + cost rises super-linearly — the bear case in
> [STATE.md](../STATE.md) — which is why Event 1 sits at 150–200.

## Which roles overlap vs must stay separate

```
MAY OVERLAP (smaller sizes)                    MUST STAY SEPARATE (every size)
  Event Director + Participant Experience        Data Steward ⟂ anyone who interprets/sells
  Research Director + Research Ops Lead           Research Director ⟂ Client-facing sales
  Design Lead + Marketing Lead                    Safety Lead ⟂ (a dedicated, reachable owner)
  a committee head + a domain mentor (disclosed)  Sponsor engineer (mentor/judge) ⟂ neutral grand-prize judge
```

The separations are the ones that protect integrity: consent/provenance (steward), honest findings
(research vs sales), participant safety (Safety Lead), and unbiased awards (sponsor conflict). Cutting
those to save headcount is exactly where the asset breaks — see
[role-correlations.md](role-correlations.md) for why these are the highest-criticality nodes.
