# The Interruption Policy — Is Now an OK Moment?

This is **Part XVIII** of the [live research OS](live-research-os.md): the context-aware gate that
decides whether the system may speak to a team *right now*, and how loudly. It is the timing half of
the two-part governor on every explicit touch — the other half is the [burden budget](participant-burden.md),
which decides whether there is any budget left at all. A touch happens only when **both** say yes.

> **Staying silent is a first-class, correct outcome — not a failure to act.** The live loop is
> designed so that the default response to an interesting moment is *no interruption*. The
> interruption policy exists to make "capture as much as possible" compatible with "the builders had
> one of the best weekends of their lives" ([live-research-os.md](live-research-os.md), the one hard
> constraint). Interrupting a team wrong is a direct debit against the binding constraint.

## The four interrupt states

A team's current (or scheduled) interruptibility is one of four ordered states
(`interrupt_state` enum, schema [`006_live_research.sql`](../../schema/006_live_research.sql)). They
are a ladder: each state permits everything lighter than itself.

```
DO_NOT_INTERRUPT      ── nothing. not a prompt, not an observer question. silence only.
MICRO_PROMPT_OK       ── a single skippable micro-prompt is allowed (micro-prompts.md)
SHORT_INTERVIEW_OK    ── a brief, few-minute conversation is allowed
DEEP_INTERVIEW_OK     ── a full sampled/triggered interview is allowed (only in an explicit slot)
      ▲ heavier touch permitted as you go down
```

The state is the *ceiling* on what may happen, never a floor: `DEEP_INTERVIEW_OK` does not mean
interview them, it means an interview *would be* acceptable timing if sampling and budget also chose
this team. Most of the time the right action in any state is still nothing.

## GOOD moments (when to consider a touch)

These are moments when a builder is naturally between things — asking costs little and the answer is
fresh. They tend to raise the state toward `MICRO_PROMPT_OK` or higher:

| Moment | Why it's good | Typical state |
|---|---|---|
| after a switch | the reason is fresh and a switch is high-signal | `MICRO_PROMPT_OK` |
| after help resolution | the blocker just cleared; they're surfacing | `MICRO_PROMPT_OK` |
| after submission | the pressure is off; reflection is cheap | `SHORT_INTERVIEW_OK` |
| meal break | they're already paused and social | `SHORT_INTERVIEW_OK` |
| scheduled checkpoint | an expected, incentive-tied touch | `SHORT_INTERVIEW_OK` |
| after a demo | outcome is known, energy is up | `SHORT_INTERVIEW_OK` |
| explicit interview slot | they opted into a deeper conversation | `DEEP_INTERVIEW_OK` |

"After a switch" and "after help resolution" are the two highest-value micro-prompt moments in the
whole system — they catch a stated reason while it is still true, which reconstruction at END never
recovers cleanly ([checkpoints.md](checkpoints.md)).

## BAD moments (when to stay silent no matter what)

These force `DO_NOT_INTERRUPT`. Any one of them overrides an otherwise-good signal — the presence of
a valuable incident does **not** buy permission to interrupt.

```
minutes before a deadline      ── the worst possible moment; do not exist to them right now
active debugging               ── deep flow; a prompt here is a genuine harm
judging                        ── sacred; never touched
critical hardware test         ── a one-shot moment you could ruin
presenting / demoing (live)    ── obviously off-limits while on stage
sleep hours                    ── overnight rest is protected, including for the tired team
```

The asymmetry is deliberate: a missed question can be asked later or recovered from an artifact; a
ruined debugging flow or a blown hardware test cannot be given back. When GOOD and BAD signals
conflict, **BAD wins** and the state collapses to `DO_NOT_INTERRUPT`.

## How the live loop consults the policy

The policy is a function the kernel is *handed*, not one it second-guesses:
`LiveResearchOS(triggers, burden, interrupt_state)` takes `interrupt_state` as a callable
`(team, at) -> state` ([`live_research.py`](../../engine/live_research.py)). Inside
`observe_then_decide`, the timing gate runs **before** any prompt can fire:

```
observe_then_decide(incident, now):
    route = triggers.route(incident.trigger_type)
    state = interrupt_state(team, now)              # ← consult the policy

    if route.action == FIRE_PROMPT:
        if state == "DO_NOT_INTERRUPT":
            return SILENT("timing: team is heads-down/near deadline")   # policy wins, unconditionally
        if not burden.can_spend(participant, "MICRO_PROMPT", ...):
            return SILENT("participant research-minutes budget spent")  # then the budget
        return FIRE_PROMPT(...)
```

Two properties are worth stating explicitly:

- **The system stays SILENT in `DO_NOT_INTERRUPT` windows, regardless of how valuable the incident
  is.** The timing check is evaluated before the budget check and short-circuits it — a team near a
  deadline is left alone even if a once-in-the-event switch just happened and the budget is full.
  The incident is still *captured* (the mentor note, the telemetry row, the observer's field note
  all persist); only the explicit *ask* is suppressed.
- **`MENTOR_NOTE_SUFFICIENT` and `FLAG_FOR_INTERVIEW` do not interrupt the team at all**, so they are
  returned before the timing gate is even consulted — a mentor note is ambient, and an interview
  flag is a note to the war room, not a knock on the team's door. The timing gate guards only the
  action that actually reaches the builder: `FIRE_PROMPT`.

## The `team_interrupt_window` table

Current and scheduled interruptibility is recorded in `team_interrupt_window`
([`006_live_research.sql`](../../schema/006_live_research.sql)):

```
team_interrupt_window
  team_id     ── who
  as_of       ── when this state applies (PK with team_id → a timeline, not a single value)
  state       ── DO_NOT_INTERRUPT | MICRO_PROMPT_OK | SHORT_INTERVIEW_OK | DEEP_INTERVIEW_OK
  reason      ── 'near deadline' | 'meal break' | 'post-switch' | 'judging' | …
```

Because `(team_id, as_of)` is the primary key, the table is a **timeline** of a team's
interruptibility, not a single current flag. That lets the war room ([research-war-room.md](research-war-room.md))
*schedule* windows ahead of time — mark all teams `DO_NOT_INTERRUPT` across the judging block and the
overnight hours, mark the post-demo slot `SHORT_INTERVIEW_OK` — and lets the callable resolve "the
state as of `now`" by reading the most recent row at or before `now`. The `reason` field keeps the
decision auditable: every silence and every permitted touch can be traced to why the window was in
that state.

## Interaction with the rest of the system

- **Burden budget.** Timing and budget are independent gates and both must pass; the budget
  ([participant-burden.md](participant-burden.md)) is checked *after* timing in the loop. A refused
  spend on either is the system protecting the golden goose, not an error to route around.
- **Critical incidents.** The taxonomy in [critical-incidents.md](critical-incidents.md) decides
  *what* happened and *whether* it routes to a prompt at all; the interruption policy decides whether
  *now* is an acceptable moment to deliver it. Most incidents ask nothing regardless.
- **Checkpoints.** A scheduled checkpoint is itself a pre-arranged `SHORT_INTERVIEW_OK` window, which
  is why checkpoints ([checkpoints.md](checkpoints.md)) can touch every team without violating the
  policy — the window was scheduled, disclosed, and incentive-tied.
- **Experience feedback.** Whether the policy is actually working is measured from the participant
  side: `experience_pulse.prompts_annoying` / `felt_watched`
  ([`006_live_research.sql`](../../schema/006_live_research.sql)). If builders feel watched or nagged,
  the policy is too permissive and the states tighten — the research system evaluates itself.
- **Governing question.** Can the system notice a valuable moment, want to ask, and *still choose
  silence* because the timing is wrong — and have that silence be the correct, traceable outcome? If
  yes, the interruption policy works.
