# Role Correlations — how it all ties together

Every role and unit at Event 1, and the working relationships between them — within the event org,
within the research org, and **across** the two. This is the structural answer to "show how it is all
tied together." It is not prose alone: it is a typed graph, built in
[`engine/org_graph.py`](../../engine/org_graph.py) (`event1_graph()`) and stored as `role_dependency`
in [`007_event_ops.sql`](../../schema/007_event_ops.sql), so "who depends on whom" is a query, not a
paragraph. Read [operational-architecture.md](operational-architecture.md) and
[org-chart-and-roles.md](org-chart-and-roles.md) first for the roles themselves.

## The seven kinds of correlation

Every edge between two roles is one of these types:

```
REPORTS_TO      org-chart hierarchy                     (Field Researcher → Research Ops Lead)
HANDOFF         one role passes work to another         (Check-in → Consent → the build)
DEPENDS_ON      one cannot function without another     (Judging → Submissions + stations from Ops)
ESCALATES_TO    a problem is raised upward              (Volunteer → Operations → Safety → Director)
STAFFS          one supplies people to another          (Sponsorship → sponsor mentors + judges)
FEEDS_RESEARCH  an ops role generates research evidence (Mentor → a logged mentor_interaction)
CONSTRAINED_BY  a research rule binds an ops role        (Mentor → burden budget + consent gate)
```

The last two are the **cross-layer** edges — the ops↔research interlock — and they are what make this
more than an org chart with a research team stapled on.

## The dependency matrix (day-of flow)

Who needs whom for the event to run. Rows depend on columns.

```
                    │ Logi │ Fin/ │ Ops │ Tech │ Judg │ Ment │ Safe │ Research
                    │ stics│ Spon │     │ /AV  │ &Awd │ or   │ ty   │  org
────────────────────┼──────┼──────┼─────┼──────┼──────┼──────┼──────┼─────────
 Operations         │  ██  │      │     │  ░░  │      │      │  ░░  │
 Tech/AV            │      │      │     │      │      │      │      │
 Judging & Awards   │      │      │ ██  │  ██  │      │      │      │   ░░ (artifact)
 Mentor Lead        │      │  ██  │     │  ░░  │      │      │      │
 Volunteers         │      │      │ ██  │      │      │      │  ██  │
 Research org       │  ░░  │  ░░  │ ██  │  ██  │  ░░  │  ██  │      │
 Participant exp.   │  ░░  │      │ ██  │      │      │  ░░  │  ██  │   ██ (the constraint)
────────────────────┴──────┴──────┴─────┴──────┴──────┴──────┴──────┴─────────
  ██ hard dependency (blocks if it fails)      ░░ soft / partial dependency
```

Read a row: **Judging & Awards** hard-depends on **Operations** (tables, stations, signage) and
**Tech/AV** (the submission platform and finals stage), and softly on the **research** side because
the artifact it evaluates is also a research signal. **The research org** depends on almost
everyone — it is a passenger on the event's infrastructure, which is exactly why the research must
never be allowed to degrade that infrastructure.

## The org-chart chains (REPORTS_TO)

`org_graph.reports_chain(role)` walks these to the top:

```
Field Researcher → Research Ops Lead → Research Director → Event Director
Volunteer        → Operations Lead   → Event Director
Mentor           → Mentor Lead       → Event Director
Judge            → Judging & Awards Lead → Event Director
```

## The escalation chains (ESCALATES_TO)

`org_graph.escalation_path(role)` — where a problem raised here ends up. This is the safety spine:

```
Volunteer  → Operations Lead → Safety Lead → Event Director
Field Researcher → Research Ops Lead                    (systemic event problems seen in the field)
```

Any safety or code-of-conduct issue reaches the **Safety Lead** within one hop of wherever it is
noticed, and a **critical** one reaches the Event Director — the reason Safety is a dedicated,
never-shared role ([logistics.md](logistics.md)).

## The interlock: FEEDS_RESEARCH (the sensor network)

This is the heart of the whole design. The operational roles **are** the research sensors —
`org_graph.feeds_research()` enumerates them:

```
  Registration / Check-in  ──FEEDS──►  the baseline + consent grants   (the gate for everything else)
  Mentor                   ──FEEDS──►  mentor_interaction: blocker, friction, intensity (the confounder)
  Judge                    ──FEEDS──►  structured evaluation of the built artifact
  Operations (app + keys)  ──FEEDS──►  behavioral telemetry: team formation, submissions, tool use, switches
  Field Researcher         ──FEEDS──►  field notes (fact ≠ interpretation)
```

Because the sensors are the event staff doing their normal jobs, the research is **produced by the
event happening** — not by a parallel data-collection apparatus that would tax the builders
([../research-ops/participant-burden.md](../research-ops/participant-burden.md)). This is the single
idea that reconciles "an amazing hackathon" with "an exceptionally rich research environment."

## The interlock: CONSTRAINED_BY (the rules that bind ops)

The reverse edges — the research disciplines that keep the sensor network from ever harming the
event or a participant:

```
  Mentor            ──CONSTRAINED_BY──►  burden budget + consent gate  (≤20s logs, scoped, no scoring)
  Field Researcher  ──CONSTRAINED_BY──►  burden budget + consent gate  (ask only within budget + an OK window)
  Marketing Lead    ──CONSTRAINED_BY──►  consent gate                  (photos only under PUBLIC_MEDIA)
  Finance/Sponsorship ─CONSTRAINED_BY──►  client-view gate             (sponsors get aggregate only, never raw)
```

Every cross-layer edge is either a sensor (`FEEDS_RESEARCH`) or a rule (`CONSTRAINED_BY`) — the
event feeds the research, the research constrains itself. `org_graph.cross_layer_edges()` returns
exactly this set, and the test suite asserts they all cross the boundary.

## Criticality: where a failure cascades

`org_graph.criticality()` ranks roles by how connected they are — high-degree nodes are where a
failure spreads, so they are the roles to staff most carefully:

```
  Event Director            most connected — the coordination hub; single point of final decision
  Operations Lead           day-of everything routes through it; judging + volunteers + research lean on it
  Research Ops Lead          runs the live loop; the field researchers + the war room depend on it
  Finance/Sponsorship Lead   staffs mentors + judges; funds the whole thing
  Safety Lead                every escalation terminates here — thin coverage here is unacceptable
```

The lesson the graph makes concrete: **the roles you are tempted to cut to save money — the data
steward, the safety lead, the research director's independence — are either high-criticality or
integrity-critical.** Cutting them doesn't shrink the org gracefully; it removes a load-bearing edge.

## The correlations that must NOT exist

Some edges are forbidden by design, and the schema enforces the sharpest ones:

```
  Sponsor engineer (as judge)  ─╳─►  neutral grand prize        (conflict; sponsor judges → category only)
  Judge                        ─╳─►  their own team              (conflict; the assigner refuses it)
  Travel-grant request         ─╳─►  admission decision          (admission-blind; affects_admission = false)
  Safety incident              ─╳─►  research data / a client    (firewalled; is_research = false)
  Volunteer                    ─╳─►  covert research capture      (only trained + logged research touches data)
```

## Reading the graph in practice

During planning, the graph answers concrete questions: *if the Tech/AV Lead is out sick, what breaks?*
(`dependents("Tech/AV Lead")` → judging, telemetry, the submission platform). *Where does a
harassment report go?* (`escalation_path` → Safety Lead → Event Director). *Which ops roles touch
participant data, so which need consent training?* (`feeds_research()` + `cross_layer_edges()`). The
same graph is the map for the run-of-show ([run-of-show.md](run-of-show.md)) and the staffing plan
([org-chart-and-roles.md](org-chart-and-roles.md)) — one structure, tying the whole event and its
research instrument together.
