# Volunteers & Crew

The human layer that actually runs the 72 hours: **paid crew** who own a domain day-of, and
**shift-based volunteers** who cover the floor. This doc defines the tiers, how they are recruited
and trained, how shifts and coverage floors work, the ratios that size the roster, the escalation
chain — and the firewall that keeps a volunteer from quietly becoming an unlogged researcher.

This is the EVENT OPERATIONS view. The org chart is in [org-chart-and-roles.md](org-chart-and-roles.md);
sizing across the whole org is [`../../engine/staffing_model.py`](../../engine/staffing_model.py);
the schedule these roles staff is [run-of-show.md](run-of-show.md); the tables are `staff` /
`staff_role` / `ops_shift` / `shift_assignment` in
[`../../schema/007_event_ops.sql`](../../schema/007_event_ops.sql). How every role ties to every
other is [role-correlations.md](role-correlations.md).

> **One rule, stated once.** Crew and volunteers keep the event excellent; they are **not**
> researchers. They may route help and surface issues, but a volunteer does not log research unless
> trained and logged as a mentor/observer record. The wall is structural (see *The firewall* below).

## The two tiers

```
  CREW  (staff_role.layer = CREW, is_paid = true)         VOLUNTEERS (layer = VOLUNTEER, is_paid = false)
  ──────────────────────────────────────────────         ────────────────────────────────────────────────
  own a DOMAIN for the whole event; few, senior,          cover the FLOOR in rotating shifts; many, trained
  reliable; report to a committee head                    day-of; report to a room/shift lead
     AV / Tech crew        (TECH_AV)                          check-in / registration      (rotating)
     F&B lead              (LOGISTICS)                         floaters                     (fill gaps)
     Logistics crew        (LOGISTICS)                         runners                      (judge clock, supplies)
     Registration lead     (OPERATIONS)                        room leads                   (own one zone/shift)
                                                               photography / social         (documentation)
                                                               workshop / mentor-desk support
```

Both tiers are `staff` rows against a `staff_role` in the catalog; the split is `layer`
(`CREW` vs `VOLUNTEER`) and `is_paid`. Crew are a small number of paid, accountable domain owners;
volunteers are the larger, shift-scheduled body. Mentors and judges are their own layers
([../research-ops/mentor-system.md](../research-ops/mentor-system.md), [judging-system.md](judging-system.md)) —
not covered here.

| Tier | Who | Count basis | Source |
|---|---|---|---|
| **Crew** | AV, F&B lead, logistics, registration lead | ~1 per 40 participants (`crew_ratio`) | **design default** — staffing_model |
| **Volunteers** | check-in, floaters, runners, room leads, photo/social, workshop/desk | ~1 per 20 participants (`volunteer_ratio`) | **sourced** — hackathon.guide shift model |
| **Workshop helper** | volunteer supporting a workshop room | ~1 per 10–20 attendees | **sourced** — hackathon.guide |

## Recruiting, training, and the CoC gate

Volunteer roles (sourced — hackathon.guide) are: **registration / check-in**, **front-door
shifts**, **floaters**, **runners**, **photography / social**, **workshop support**, and
**documentation**. The operating cadence:

- **Identify ~10 days prior** (sourced). Crew are locked earlier — they own a domain and appear in
  the logistics plan ([logistics.md](logistics.md)); volunteers are confirmed in the final ~10-day
  window when headcount and the schedule are firm.
- **Rotating shifts, not marathons** (sourced). Nobody works the whole 72h; volunteers rotate so
  coverage holds and people stay fresh — especially across the overnight.
- **Train to the run-of-show.** A short briefing per role: where things are, who the leads are, the
  escalation chain (below), and — the load-bearing line — *what you do and do not write down* (the
  firewall).
- **Code-of-conduct gate.** Every crew member and volunteer acknowledges the CoC before they work:
  `staff.coc_acknowledged_at` must be set. No acknowledgement, no shift. This mirrors the judge gate
  (`judge.coc_acknowledged_at`) and is a participant-experience hard requirement, not a formality.

## Shifts and coverage floors

A shift is an `ops_shift`: a role, a window (`starts_at`/`ends_at`), a `zone`, a **coverage floor**
`min_headcount`, and an `is_overnight` flag. People are attached via `shift_assignment`, and
`checked_in_at` records whether they actually showed — the difference between the roster and reality.

```
  ops_shift(role, zone, starts_at→ends_at, min_headcount, is_overnight)
       └── shift_assignment(staff_id, checked_in_at?)     ← did they show for THIS shift?

  coverage check:   count(checked_in_at is not null)  ≥  min_headcount
       if short → floaters pulled in ; the Operations Lead is paged
```

- **`min_headcount` is a floor, not a target.** Peaks (Friday check-in, meal service, the demo expo)
  need many volunteers at once; the quiet middle of the night needs few. The schedule sizes each
  shift to its moment ([run-of-show.md](run-of-show.md)).
- **Overnight is deliberately thin.** `is_overnight = true` shifts run a minimal but non-zero floor:
  a room lead, a safety-aware volunteer, and an on-call crew/organizer — enough to keep the space
  safe and running, not the daytime density. Thin is fine; **zero is not** — the floor exists so
  overnight never silently drops to nobody.
- **Floaters are the shock absorber.** They hold no fixed post so they can be moved to whatever shift
  fell below `min_headcount` (a no-show, a surprise queue). They are how a coverage floor is
  actually defended in real time.

## The ratios (sizing the roster)

`staffing_model.plan(participants)` sizes both tiers from `DEFAULTS` and reports the rule each count
came from ([`../../engine/staffing_model.py`](../../engine/staffing_model.py)):

```
  vols = ceil(participants / volunteer_ratio)     volunteer_ratio = 20   (sourced: hackathon.guide)
  crew = ceil(participants / crew_ratio)          crew_ratio      = 40   (design default)
  workshop helpers: ~1 per 10–20 attendees in a room (sourced), sized per workshop, not globally
```

Worked for the Event 1 range (team-size-4 midpoint; counts *illustrative* except the sourced
ratios):

| Participants | Volunteers (1:20) | Paid crew (1:40) | Note |
|---:|---:|---:|---|
| 120 | 6 | 3 | lower bound |
| 150 | 8 | 4 | |
| **180** | **9** | **5** | Event 1 midpoint |
| 200 | 10 | 5 | |

> These are **steady-state** counts. Peaks (check-in, meals, expo) briefly need more volunteers
> *simultaneously* than the ratio implies, which is why the number is spread across rotating shifts
> rather than a flat headcount — and why floaters exist. `plan` also warns when the broader org is
> thin (e.g. mentors vs teams); above ~200 participants it flags that ops + parallel research is no
> longer a small team ([../event1-design.md](../event1-design.md), the bear case).

## Day-of management and the escalation chain

Crew and volunteers are run by radio and a clear escalation path. Anything a volunteer cannot
resolve at their post goes **up**, fast — the chain is a first-class object in the schema as
`ESCALATES_TO` edges in `role_dependency`:

```
  VOLUNTEER ──ESCALATES_TO──► OPERATIONS LEAD ──► SAFETY LEAD ──► EVENT DIRECTOR
  (floor issue: supplies,     (staffing, room,     (CoC, medical,   (final call;
   a lost badge, a queue)      logistics call)      security)        anything unresolved)
```

- **Operations Lead** owns day-of floor operations — coverage, supplies, room resets, the volunteer
  roster. Most issues stop here.
- **Safety Lead** owns anything that touches wellbeing or conduct. A **CoC / medical / facilities /
  security** matter is a `safety_incident` (severity `LOW | MED | HIGH | CRITICAL`), and it is
  **operations data, not research data** — the schema enforces `is_research = false`. It never
  enters a client deliverable or any participant research record.
- **Event Director** is the final escalation for anything unresolved or high-severity.

Radios, a single shared incident channel, and named leads per shift make this chain real rather than
nominal. The full set of `role_dependency` edges (who hands off to, depends on, staffs, escalates to
whom) is documented in [role-correlations.md](role-correlations.md).

## The firewall: volunteers are not researchers

This is the sharp edge. Volunteers are everywhere on the floor and see everything — which is exactly
why the boundary has to be explicit and structural, not left to good intentions.

```
  ALLOWED (any volunteer)                         REQUIRES TRAINING + A LOGGED RECORD
  ───────────────────────────                     ────────────────────────────────────
  route a team to a mentor / the help desk        log a research observation
  surface an ops issue (queue, blocker, outage)      → only a trained field researcher,
  answer "where is X / when is Y"                       as an observation (fact ≠ interpretation)
  keep the room running                            do real technical mentoring
                                                      → logged as a mentor_interaction (the confounder)
```

- **Routing is not research.** A volunteer noticing "table 12 is stuck on auth" and walking them to a
  mentor is good ops. It becomes a research record **only** when a trained observer writes it up as
  an `observation` under the fact-vs-interpretation discipline
  ([../research-ops/field-researcher-guide.md](../research-ops/field-researcher-guide.md)). An
  untrained volunteer's hallway impression is not evidence and does not enter the evidence graph.
- **A volunteer who does real technical mentoring is a mentor, and must be logged as one.** If a
  workshop helper or floater actually sits down and writes the tricky integration for a team, that is
  a `mentor_interaction` — not an anonymous act of kindness. It has to be logged with intensity
  (`support_intensity`) and affiliation, because **help is the textbook confounder**: a success that
  happened only after heavy expert help is not the product succeeding on its own
  ([../research-ops/mentor-interventions.md](../research-ops/mentor-interventions.md)). An unlogged
  volunteer rescue is precisely the signal that silently corrupts a research finding.
- **The constraint is queryable, not just prose.** The research rules that bind an ops role appear as
  `CONSTRAINED_BY` edges in `role_dependency` (any role → the consent gate / burden budget). A
  volunteer operates *under* those rules the moment their action touches a participant's research
  record.

So the volunteer layer has two jobs and a bright line between them: **make the weekend excellent**,
and **surface — but never silently record — what they see**. The instant a volunteer's action would
become research, it must pass through a trained role and a logged record, or it does not count as
research at all. That is what keeps the experience great and the research honest at the same time
([../research-ops/participant-experience.md](../research-ops/participant-experience.md)).
