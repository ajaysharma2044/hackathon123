# Logistics — The Physical Event

Every logistical domain a 72-hour premium fly-in has to get right, mapped to the data model in
[`../../schema/007_event_ops.sql`](../../schema/007_event_ops.sql) and the staffing plan in
[`../../engine/staffing_model.py`](../../engine/staffing_model.py). Its sibling is the hour-by-hour
[run-of-show.md](run-of-show.md); the org that executes it is [org-chart-and-roles.md](org-chart-and-roles.md);
how the domains interlock is [operational-architecture.md](operational-architecture.md); the comps
behind every sourced number are in [prior-hackathons.md](prior-hackathons.md).

It sits **downstream of the go/no-go gate** — no irreversible logistics until ≥1 paid pilot/LOI is
signed ([event1-design.md](../event1-design.md), [funding.md](../funding.md)) — and answers: **given
Event 1 runs for ~150–200 curated builders over 72h, what has to physically exist, who owns it, when
it is due, and which decisions quietly protect the research layer.**

> **Epistemic note.** Ratios and per-person bands labeled *sourced* come from hackathon.guide and the
> premium fly-in comps (TreeHacks, Cal Hacks) in [prior-hackathons.md](prior-hackathons.md). Every
> dollar figure is an **estimate**, not a quote; invented counts are *illustrative*. Real numbers
> replace these before signing — [funding.md](../funding.md) holds the budget of record and wins.

## The domains at a glance

```
VENUE ──────────► space types → venue_resource.kind
FOOD ───────────► meal cadence + dietary → meal_service
TRAVEL/FLY-IN ──► funded, regional caps, admission-blind → travel_grant
CHECK-IN ───────► arrival pipeline → HANDOFF to research (consent + baseline)
WIFI + POWER ───► load-tested network, 1 strip/table → venue_resource
HARDWARE LAB ──► loaner kit + workbench → venue_resource(HARDWARE_LAB)
SWAG / PRIZES ──► badges, kit, prize pool → prize / prize_award
OVERNIGHT ──────► sleep + wellness → venue_resource(SLEEP_ROOM)
SAFETY / CoC ───► public CoC, emergency plan, on-call → safety_incident
A/V + SIGNAGE ──► stage, mics, projector, wayfinding → venue_resource(AV_KIT|SIGNAGE)
```

## VENUE — space types (`venue_resource.kind`)

A 72h build needs distinct spaces, not one room. hackathon.guide (sourced): hacking at tables of
~10 seats, gender-neutral single-occupancy bathrooms preferred, AC available after-hours, a projector
+ mic for the stage. Cornell-only is a **same-campus advantage** — a university venue is plausibly
in-kind ([funding.md](../funding.md)), the biggest cost lever and the first credibility signal.

| Space | `venue_resource.kind` | Illustrative sizing (175 builders) | Notes |
|---|---|---|---|
| Main hacking hall | `HACK_TABLE` | ~18 tables × 10 seats | power + wifi at every seat; the center of gravity |
| Workshop rooms | `WORKSHOP_ROOM` | 2–3 rooms, 30–50 cap each | sponsor talks, workshops; soundproof from the hall |
| Mentor / help desk | `WORKSHOP_ROOM` (zoned) | 1 staffed desk + queue board | help-first; the capture byproduct ([../research-ops/mentor-system.md](../research-ops/mentor-system.md)) |
| Judging / expo hall | `HACK_TABLE` (re-zoned) | same floor, station signage | science-fair stations ([judging-system.md](judging-system.md)) |
| Quiet / sleep room | `SLEEP_ROOM` | 2 rooms, lights-low, ~40 cots | gendered options; see OVERNIGHT below |
| Meal area | (staging, not a resource row) | flow for 175 in ≤30 min | separate from tables to reset energy |
| Stage | `AV_KIT` | 1 main stage | ceremonies, demos, finals |

`venue_resource` carries `quantity` and `capacity_each`, so "18 tables × 10 seats" and "1 AP per ~25
devices" are both rows. Setup/teardown are **30 minutes each** (sourced), each its own critical-path
`logistics_task`.

## FOOD — `meal_service`

Food is mandatory, continuous, and a morale instrument. hackathon.guide (sourced): **$7–15 per person
per meal**, order catering **3+ days ahead**, cover dietary needs. [funding.md](../funding.md) budgets
the lower MLH band (~$8–10/meal); this doc uses that. Every meal is a `meal_service` row with a
non-empty `dietary_options[]` — **dietary coverage is schema-enforced** (`text[] not null`).

```
72h MEAL CADENCE (illustrative, ~175 headcount)
 Fri  dinner ········· opening-ceremony meal
 Sat  breakfast · lunch · dinner · 2am snack (overnight)
 Sun  breakfast · lunch · dinner · 2am snack (overnight)
 Mon  breakfast ······ pre-deadline fuel
 + standing coffee/snacks/water, refreshed continuously in the hall
```

`dietary_options[]` covers **vegetarian, vegan, gluten-free, halal, kosher** as a floor, keyed off the
dietary fields captured at application so per-option headcounts are known before the 3-day lock.
Overnight snacks (`label = 'Sat 2am snack'`) are not optional at a multi-night event. Meal breaks are
also deliberate research windows — the interruption policy rates a meal break `SHORT_INTERVIEW_OK`
([../research-ops/interruption-policy.md](../research-ops/interruption-policy.md)) — so cadence here and
in [run-of-show.md](run-of-show.md) are designed together.

## TRAVEL / FLY-IN — `travel_grant`

The premium differentiator: **funded travel** (sourced: TreeHacks reimburses every competitor; Cal
Hacks uses **regional travel-stipend caps**, the stipend is an **optional** application question, and
it is **admission-blind**). Our schema hard-codes the invariant:
`travel_grant.affects_admission = false` (a `check` constraint, not a convention). Selection never sees
who asked for money.

```
travel_grant:  participant_id · region · amount · status(OFFERED→ACCEPTED→REIMBURSED|DECLINED)
               affects_admission = false   ← enforced, admission is blind to the grant
```

Cornell-only keeps this **mostly regional/local**: most builders are on-campus or Northeast, so
`region` caps stay low and the travel line is far smaller than a national fly-in
([funding.md](../funding.md): bus charters from Northeast hubs, stipend-capped rather than booked
flights, which also removes change-fee and no-show exposure). **Stipend, don't book.** Registration
math differs from free events: those see ~65% show and cap at ~150% of capacity (sourced); a **premium
fly-in is different — accepted ≈ attend**, so plan near 100% and manage a waitlist, not an over-admit.

## CHECK-IN — the arrival pipeline (and the research handoff)

Check-in is a pipeline, and it is the single most research-critical logistics moment: it is where
**consent and baseline happen** before anyone builds. This is a typed `HANDOFF` edge in
`role_dependency` (registration → participant-experience → research), and it crosses the
ops↔research boundary (`is_cross_layer = true`).

```
ARRIVAL PIPELINE (per builder, target < 5 min)
  ID / confirm ──► BADGE (name + team + dietary flag) ──► SWAG kit ──►
      CONSENT hand-off ──► BASELINE checkpoint(START) ──► TEAM AREA
        │                        │
        └─ research layer owns ──┘   (consent-design.md, checkpoints.md)
```

The consent + baseline steps belong to the research org's `DATA_STEWARD` and field researchers, but are
physically embedded in the ops arrival line so **no capture precedes recorded consent** and the t0 SAID
baseline is fixed before exposure ([../research-ops/event-phase-plan.md](../research-ops/event-phase-plan.md),
ARRIVAL/CONSENT). Ops owns the ID→badge→swag throughput; research owns the consent→baseline integrity;
the handoff is the seam. Check-in is the day's biggest volunteer peak — `staffing_model.py` sizes the
baseline (~1 volunteer per 20 builders) and flags that peaks need more at once.

## WIFI / NETWORK + POWER

Non-negotiable and chronically under-budgeted ([funding.md](../funding.md): "wifi capable of 250
concurrent devs is not optional"). hackathon.guide (sourced): **load-test the network for all
participants**, **do not block ports** (builders need SSH, VPNs, custom ports, deploy tooling), and
provide **one power strip per table**.

| Resource | `venue_resource.kind` | Illustrative | Rule |
|---|---|---|---|
| Wifi APs | `WIFI_AP` | ~8–10 APs | `capacity_each` ≈ devices/AP; builders carry 2+ devices each |
| Power strips | `POWER_STRIP` | ≥1 per table (~18+) | sourced: 1 strip/table minimum; plan spares |

Load-test against **2× headcount in devices** before doors open (a blocking `logistics_task`).
Brokered-key instrumentation for the research layer rides on this same network
([../research-ops/participant-experience.md](../research-ops/participant-experience.md)); if the network
falls over, both the build and the research capture fail — so the AP/port test is on the critical path.

## HARDWARE LAB — `venue_resource(HARDWARE_LAB)`

A staffed loaner bench — dev boards, sensors, cables, adapters, a few GPUs/peripherals — checked out
against a badge, logged. Modest for a software-leaning cohort, but a **critical hardware test** is one
of the `DO_NOT_INTERRUPT` moments — a one-shot moment research must never ruin
([../research-ops/interruption-policy.md](../research-ops/interruption-policy.md)).

## SWAG / PRIZES

Swag is part of the arrival kit (badge, shirt, stickers, lanyard) — a `logistics_task` owned by DESIGN,
ordered against the 3-day lock. Prizes live in `prize` / `prize_award` (kinds `GRAND | CATEGORY |
SPONSOR | R&D_CHALLENGE`); **cash prizes stay modest, credits/hardware come in-kind from sponsors**
([event1-design.md](../event1-design.md): oversized prize pools barely move outcomes). IP terms on any
sponsor/R&D prize are decided **before** the event and disclosed in the challenge
([judging-system.md](judging-system.md)).

## OVERNIGHT / SLEEP + WELLNESS — `venue_resource(SLEEP_ROOM)`

A safety and experience requirement (sourced: overnight/quiet sleeping space, AC after-hours). Quiet
rooms are dark, low-stimulation, cots/air mattresses, gendered options. The critical interlock: **sleep
hours are a `DO_NOT_INTERRUPT` window**, protected even for the tired team, so the quiet room's posted
hours and the research layer's protected sleep-hours are the **same hours by construction**
([../research-ops/interruption-policy.md](../research-ops/interruption-policy.md)). Wellness also means
water, caffeine, quiet, and a visible on-call organizer.

## SAFETY / SECURITY / CoC + emergency plan — `safety_incident`

Mandatory, public, enforced (sourced): an MLH-style **public Code of Conduct**, an **emergency plan**,
accessibility, and an **on-call organizer** reachable at all hours. Every incident is a
`safety_incident` row (`kind = COC_VIOLATION | MEDICAL | FACILITIES | SECURITY`, with `severity`).

> **Firewall (schema-enforced).** `safety_incident.is_research = false` is a `check` constraint.
> Safety data is **operations data only** — it never enters a client deliverable or any participant
> research record. This is the same ops-vs-research separation the research OS commits to
> ([../research-ops/live-research-os.md](../research-ops/live-research-os.md)).

CoC acknowledgement is required to work the event (`staff.coc_acknowledged_at`,
`judge.coc_acknowledged_at`) and is briefed to all participants at the opening ceremony
([run-of-show.md](run-of-show.md)). Escalation is a typed `ESCALATES_TO` edge: any volunteer → Safety
lead / on-call organizer.

## A/V + SIGNAGE — `venue_resource(AV_KIT | SIGNAGE)`

Stage A/V (projector + mics + speakers, sourced) for ceremonies, talks, demos, and finals; signage for
wayfinding (hall, workshops, help desk, quiet rooms, gender-neutral bathrooms, meals) and live
schedule/announcements. A/V is owned by TECH_AV crew, signage by DESIGN; both are `logistics_task` rows
with setup on the critical path.

## Illustrative budget — per-person + fixed lines

Estimates only; reconcile to [funding.md](../funding.md) before committing. Per the sourced bands, ~175 builders:

| Line | Basis (sourced band) | Per-person | Illustrative total |
|---|---|---:|---:|
| Food | $8–10/meal × ~9 servings | ~$80 | ~$14,000 |
| Venue | $10–30/person (major city); target in-kind | $0–25 | $0–4,400 |
| Travel grants | regional caps, stipend not booked | ~$250 avg | ~$44,000 |
| Swag / kit | — | ~$40 | ~$7,000 |
| **Per-person subtotal** | | **~$160–415** | **~$65K** |
| Wifi / A/V / power (fixed) | load-tested for 2× devices | — | $10–30K |
| Prizes (cash only) | credits/HW in-kind | — | $10K |
| Insurance / legal / entity | liability + agreements | — | $5–15K |
| Contingency (15%) | — | — | on the totals above |

This is a subset view of [funding.md](../funding.md)'s full stack; where they differ, funding.md wins.

## `logistics_task` checklist (by `due_offset_days`)

Each row is owned by an `org_unit_code` and carries `due_offset_days` (negative = before start) and a
`blocking` flag. Critical-path (`blocking = true`) tasks are **bold**.

| `due_offset_days` | Task | Owner unit | Blocking? |
|---:|---|---|:--:|
| **T-60** | **Venue contract signed (in-kind target)** | LOGISTICS | ✅ |
| **T-45** | **Network/power plan; confirm no port blocks** | TECH_AV | ✅ |
| T-45 | Travel-grant offers sent (admission-blind) | FINANCE_SPONSORSHIP | |
| T-30 | Public CoC + emergency plan published | SAFETY | ✅ |
| T-30 | Swag + signage ordered | DESIGN | |
| T-21 | Quiet/sleep rooms + cots reserved | LOGISTICS | |
| T-14 | Bus charters / travel logistics locked | LOGISTICS | |
| T-7 | Final dietary headcounts per option | OPERATIONS | |
| **T-4** | **Catering ordered (3+ days ahead, sourced)** | OPERATIONS | ✅ |
| T-2 | Badges printed; swag kits packed | PARTICIPANT_EXPERIENCE | |
| **T-1** | **Network load-test @ 2× devices; A/V check** | TECH_AV | ✅ |
| **T-0 (−0.5d)** | **Setup: tables, power strips, signage (30 min block)** | CREW | ✅ |
| T-0 | Check-in line staffed; consent/baseline station live | PARTICIPANT_EXPERIENCE + RESEARCH | ✅ |
| T+3 (teardown) | Teardown, lost-and-found, equipment return (30 min) | CREW | |

**The critical path** (what, if late, moves the event): venue → network/power + no-port-blocks →
catering (3-day lock) → load-test → setup → staffed check-in with the consent/baseline station live.
Everything else has slack; these do not.

## Which logistics decisions protect the research

Logistics is not neutral to the research layer — several domains exist partly to keep the research
honest and low-friction ([role-correlations.md](role-correlations.md) has the full edge map):

- **Check-in is where consent + baseline happen** — the arrival pipeline embeds the research handoff so
  no capture precedes consent and the t0 baseline is fixed before exposure.
- **The quiet room's hours = the research sleep-hours** — protected rest is one schedule, not two.
- **Meal breaks are the `SHORT_INTERVIEW_OK` windows** — the cheapest research moments exist by cadence.
- **The network carries brokered-key instrumentation** — the load-test protects capture and build alike.
- **Safety + CoC data is firewalled** (`is_research = false`) — operations data never becomes product.

The ops↔research interlock is a first-class, queryable object (`role_dependency`, `is_cross_layer`),
not prose — see [operational-architecture.md](operational-architecture.md).
