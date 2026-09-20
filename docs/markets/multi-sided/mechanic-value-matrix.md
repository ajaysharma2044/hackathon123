# The mechanic × stakeholder value matrix

`engine/value_matrix.py`. This is the net-new layer the integration plan flagged as missing: a
value matrix **U[side, mechanic]**, a cost/burden matrix **C[resource, mechanic]**, cross-side
fan-out, super-additive synergy (Γ), and the conflict set. It builds **on** the existing markets
(`opportunity_market.fan_out` is reused for the participant-side scope fan-out) rather than
recreating them.

## Mechanics — the atoms an event is built from

`MECHANICS` (16): `mentor_request`, `repo_submission`, `demo`, `tool_switch`, `team_formation`,
`optional_challenge`, `follow_up_30_90`, `project_continuation`, `sponsor_keynote`, `workshop`,
`exit_interview`, `checkpoint`, `brokered_key_use`, `founder_dinner`, `sponsored_bounty_track`,
`open_build_track`. A concrete event **design is a subset** of these.

## U[side, mechanic] — value, ordinal, evidence-tagged

Each cell is `(magnitude, evidence_tag)`:

- magnitude ∈ `NEG(−2) · NONE(0) · LOW(1) · MED(2) · HIGH(3)` (`ORD`)
- evidence_tag ∈ `O` observed-in-repo · `I` inferred · `H` hypothesis · `U` unknown

We seed only the **load-bearing** cells; everything else defaults to `("NONE","U")` — honestly
unknown, not assumed zero-value. The seeded structure encodes what the research actually supports:

| mechanic | who it creates value for (sign/'magnitude) | who it **harms** |
|---|---|---|
| **demo** | participants HIGH, product_clients HIGH, judges HIGH, organizers HIGH, employers/vcs/sponsors/cornell MED | — |
| **mentor_request** | participants HIGH, mentors HIGH, product_clients MED, sponsors MED | — |
| **repo_submission** | product/rd/employers/vcs/organizers MED, participants MED | — |
| **open_build_track** | participants HIGH, product_clients HIGH | — |
| **brokered_key_use** | product_clients/sponsors/organizers HIGH | — (invisible, no participant burden) |
| **exit_interview** | product_clients HIGH | **participants NEG** (burden) |
| **checkpoint** | product_clients MED | **participants NEG** (burden) |
| **sponsor_keynote** | sponsors MED | **participants NEG** (low value / minute) |
| **sponsored_bounty_track** | sponsors HIGH | **product_clients NEG** (distorts free-choice validity) |

The last two rows are the crux of "sides destroying each other's value": the mechanics worth the
**most to sponsors** are exactly the ones that **cost participants or research validity**. The
mechanism-design layer is what stops revenue from selecting them anyway.

## C[resource, mechanic] — burden, kept separate from value

`RESOURCES` (11): `participant_attention`, `participant_minutes`, `mentor_hours`, `researcher_hours`,
`organizer_hours`, `space`, `prize_budget`, `sponsor_slots`, `research_burden`, `trust_risk`,
`frontend_distortion`.

Cost is a **separate matrix** so a burden can never be silently booked as a benefit. Key rows:

- `participant_minutes`: demo MED, exit_interview MED, sponsor_keynote MED, workshop MED, founder_dinner MED, mentor_request LOW, checkpoint LOW
- `research_burden`: exit_interview **HIGH**, checkpoint MED, follow_up_30_90 MED
- `frontend_distortion`: sponsored_bounty_track **HIGH**, sponsor_keynote MED, exit_interview LOW
- `trust_risk`: sponsored_bounty_track MED, exit_interview LOW, brokered_key_use LOW

## Cross-side fan-out — finding the multi-use mechanics

`cross_side_fanout(j)` returns the set of sides `j` creates **positive** value for (and any it
harms). High fan-out = a mechanic that is naturally positive-sum.

- `demo` → benefits **8 sides** (verified in `test_multi_sided.py`), harms none → the flagship
  multi-use mechanic.
- `sponsor_keynote` → harms `participants` → a negative-fanout mechanic.

## Synergy Γ(j,k) — super-additive and conflicting pairs

`SYNERGY` / `synergy(j,k)` returns `POS` / `NEG` / `UNKNOWN` with an evidence tag. Doing two
mechanics can be worth more (or less) than the sum:

- `repo_submission + demo` → **POS** (artifact + demo is super-additive for employers/VCs)
- `demo + follow_up_30_90` → **POS**
- `mentor_request + exit_interview` → **POS** (help context enriches the "why")
- `sponsored_bounty_track + open_build_track` → **NEG** — the bounty contaminates the free-choice
  research validity of the open track. This is the pair the distortion gate blocks.

Most pairs return `UNKNOWN` — honestly unmeasured until Event 1.

## The master query

`analyze_mechanic(j)` returns the full multi-sided profile of one mechanic:

```
analyze_mechanic("demo") → {
  stakeholders_benefited: [participants, employers, vcs, product_clients, sponsors, organizers, cornell, judges],
  stakeholders_harmed:    [],
  cross_side_fanout:      8,
  resources_consumed:     {participant_minutes: MED},
  value_cells:            {participants:(HIGH,I), product_clients:(HIGH,I), judges:(HIGH,O), ...},
  synergies:              {demo+repo_submission:(POS,H), demo+follow_up_30_90:(POS,H)},
  frontend_distortion:    NONE,
  trust_risk:             NONE,
  unknowns:               "observed WTP UNKNOWN; most cells H/U until Event 1 measures them",
}
```

Note `unknowns` is always present: **observed willingness-to-pay is UNKNOWN**, and the query says so
every time. The matrix tells you *structure*, not *proven dollars*.
