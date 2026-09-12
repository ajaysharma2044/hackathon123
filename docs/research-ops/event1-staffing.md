# Event 1 Staffing

The people who actually run the live research OS, what each does, which roles can overlap, and the
recommended structure for Event 1. This builds on the field-researcher staffing ratios in
[field-researcher-guide.md](field-researcher-guide.md) and is costed against the two-person-load
warning in [STATE.md](../STATE.md) (bear case #6: a 200-person flown-in event with parallel
engagements is *not* a two-person job, and no amount of research changes that).

## The roles

```
EVENT DIRECTOR ───────────── owns the whole event; the experience is their P&L
  │
  ├─ PARTICIPANT EXPERIENCE LEAD ─ the golden goose's advocate; owns the pulse + the hard constraint
  ├─ TECHNICAL OPERATIONS ──────── Wi-Fi, power, brokered keys, event app, artifact capture
  ├─ MENTOR LEAD ───────────────── recruits/schedules mentors, runs the support queue + routing
  │     └─ MENTORS ─────────────── help first; log lightly (mentor-system.md)
  ├─ CHALLENGE LEADS ───────────── own each sponsor/R&D challenge's design + judging
  └─ CLIENT LEAD ───────────────── the single interface to paying clients; shields research from them

RESEARCH DIRECTOR ───────────── owns the study designs, pre-registration, and the findings
  │
  ├─ RESEARCH OPERATIONS LEAD ──── runs the war room, the backlog, and sampling allocation live
  ├─ LEAD RESEARCHERS ──────────── own synthesis for a cluster of zones; write analytic memos
  │     └─ FIELD RESEARCHERS ───── circulate zones, log observations, run short interviews
  ├─ INTERVIEWERS ──────────────── run the deeper sampled/triggered interviews
  ├─ RESEARCH ANALYSTS ─────────── coding, the evidence graph, the quant funnels
  └─ DATA STEWARD ──────────────── consent, burden ledger, provenance integrity — CONFLICT-FREE
```

The two directors are deliberately separate people. The **Event Director optimizes the experience;
the Research Director optimizes the evidence.** When they conflict, the experience wins
([participant-experience.md](participant-experience.md)) — and having two distinct owners makes that
tension explicit and negotiable rather than hidden inside one overloaded person.

## What each role does (and why it exists)

| Role | Core job | Why separate |
|---|---|---|
| Event Director | the event is excellent and runs on time | the buck stops somewhere for the experience |
| Research Director | the studies are valid, pre-registered, honestly reported | can say "that finding doesn't hold" to a client |
| Research Ops Lead | runs the live loop: war room, backlog, who-to-interview-next | the loop needs a single driver in real time |
| Field Researchers | the human sensor network; notes + short interviews | coverage requires bodies in zones |
| Lead Researchers | shift-by-shift synthesis; memos; codebook calibration | raw notes don't synthesize themselves |
| Interviewers | the ~12–15 min deeper conversations | interviewing well is a distinct skill from roaming |
| Research Analysts | coding, evidence graph, funnels, retention | turns capture into a deliverable |
| **Data Steward** | consent/burden/provenance; the `ClientView` gate | **must not also interpret** — integrity is conflict-free |
| Mentor Lead | mentor roster, shifts, the support queue | support quality is an experience driver |
| Client Lead | the only client-facing voice; schedules client observation | keeps clients out of the research process (no editorial control) |
| Participant Experience Lead | the pulse, logistics quality, the hard-constraint veto | someone must be paid to defend the builders |
| Technical Operations | keys, app, connectivity, artifact capture | instrumentation fails silently without an owner |
| Challenge Leads | challenge design + judging per track | domain ownership |

## Which roles overlap vs stay separate

```
MAY OVERLAP (especially at smaller sizes)
  Research Director + Research Ops Lead        (small events)
  Lead Researcher + Interviewer                (a lead runs deep interviews in their cluster)
  Participant Experience Lead + Event Director  (small events)
  Challenge Lead + a domain Mentor              (if disclosed and load permits)
  Research Analyst + Lead Researcher            (the same people code what they synthesized)

MUST STAY SEPARATE (at every size)
  Data Steward  ⟂  anyone who interprets or sells   (consent/provenance integrity is conflict-free)
  Research Director  ⟂  Client Lead                  (the person who can say "negative finding"
                                                       is not the person selling the engagement)
  Company/sponsor engineers (as mentors)  ⟂  neutral observers of their own product
                                                      (the confounder — mentor-interventions.md)
```

## Recommended structure by size

Pairs with the field-researcher table in [field-researcher-guide.md](field-researcher-guide.md).
"Research staff" counts the research org; the event org (mentors, tech ops, challenge leads,
experience, client) is additional and partly volunteer/sponsor-supplied.

| Size | Research Dir | Ops Lead | Field | Leads | Interviewers | Analysts | Steward | **Research total** | Event-org core |
|---|---|---|---|---|---|---|---|---|---|
| **80** | 1 (also ops) | — | 3 | 1 | shared | 1 | 1 | **~6** | dir + mentor lead + tech ops + exp/client (dir doubles) |
| **120** | 1 | 1 | 4 | 1 | 2 | 1–2 | 1 | **~10** | + a dedicated experience lead |
| **150** | 1 | 1 | 5–6 | 2 | 2 | 2 | 1 | **~13–14** | + a client lead, 2–3 challenge leads |
| **200** | 1 | 1 | 7–8 | 2 | 3 | 2–3 | 1 | **~16–18** | full structure, interview pod |

For **Event 1 at ~150–200** ([event1-design.md](../event1-design.md)), the recommendation is the
150/200 column: roughly **13–18 research staff**, separate event and research directors, a dedicated
data steward, and a client lead who keeps paying clients on the aggregate side of the
[ClientView](live-research-os.md) gate.

## Cost and simplicity levers

The staff line is real money, so optimize it honestly:

- **Field researchers and mentors can be trained Cornell grad students / staff / sponsor engineers**
  (the last only as *disclosed, logged* mentors — never as neutral observers of their own product).
  This is the Reality-Hack-style model referenced in [event1-design.md](../event1-design.md).
- **The war room can be run by a small core** (Research Ops Lead + 1–2 leads) if the field
  researchers are well-calibrated — good notes reduce synthesis load.
- **Much of the "engine" is a disciplined process + a spreadsheet for Event 1**
  ([event1-live-playbook.md](event1-live-playbook.md)): you do not need the software built to run
  the loop by hand at n≈150.
- **Do not under-staff the data steward or the experience lead to save money.** Those two roles are
  exactly where cutting corners destroys the asset — consent/provenance failures are legal and
  reputational, and a degraded experience kills the compounding panel.

## The honest staffing conclusion

The live research OS is **staff-heavy by design** — it is a human sensor network, and the humans are
the sensors. That is a direct answer to the bear case: this is not a two-person operation, and
pretending it is would either ruin the event or produce thin data. The cost is justified only if a
client is paying for the depth the staffing buys ([STATE.md](../STATE.md)) — which is why no staff
are hired until the [WTP gate](../event1-design.md) is passed and the sold study sizes the event.
