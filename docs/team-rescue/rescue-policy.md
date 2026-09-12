# Rescue Policy

The **acting half** of the engine. Given a team's state ([team-state-model.md](team-state-model.md)),
decide *how much* to help and *what kind* of help — a graduated ladder that starts at "do nothing"
and only climbs when a team is genuinely losing preventable time. The master framing (objective, the
loop, the Preventable-Blocked-Minutes metric) is [adaptive-rescue-engine.md](adaptive-rescue-engine.md);
the runnable core is [`../../engine/rescue_engine.py`](../../engine/rescue_engine.py); the storage is
[`../../schema/008_team_rescue.sql`](../../schema/008_team_rescue.sql).

Three disciplines are enforced in code, not merely promised:

> **Counterfactual honesty.** An intervention is logged as having *preceded* an outcome, never
> *caused* it (Part LVI). `record_outcome(..., causal=True)` raises.
>
> **Performance/research firewall.** Rescue consumes OPERATIONAL team state only; `_firewall`
> rejects any research-grain or person-level field (Part XXXIII, [firewalls-and-ethics.md](firewalls-and-ethics.md)).
>
> **Scenarios, not certainty.** `simulate_intervention` returns a range, never a fabricated
> probability (Parts XXXIV–XXXV).

---

## Part III — The No-Dead-Team principle and the escalation ladder

The whole policy exists to make it **hard for a team to quietly fail from a preventable problem** —
and equally hard for the system to become a manager hovering over people who are fine. Those two
goals are reconciled by one rule:

> **A team making progress stays at level 0.** We never interrupt a working team, even if it briefly
> reports a blocker. `escalation_level(..., making_progress=True)` returns 0 unconditionally.

`LADDER` (in [`rescue_engine.py`](../../engine/rescue_engine.py)) is monotonic — higher means more
intervention, and the engine climbs it only as severity **and** duration justify:

```
 0  no action — team is making progress
 1  suggest a relevant resource / docs
 2  route a mentor
 3  route a SPECIALIST mentor
 4  short team diagnosis (a researcher/organizer sits with them ~5 min)
 5  scope reduction / architecture reset
 6  team restructuring / optional merge  (VOLUNTARY)
```

`escalation_level(blocker_severity, blocked_minutes, making_progress)` maps *(severity, duration,
progress)* → a level, **capped at 6**:

```
making_progress ................................... → 0   (always; the No-Dead-Team override)
otherwise:  sev = clamp(blocker_severity, 0..3)
            dur = 0 (<20m) · 1 (<60m) · 2 (<120m) · 3 (≥120m)
            level = min(6, max(1, sev + dur))         # ≥1 once genuinely blocked
```

Duration matters as much as severity: a MED blocker that has lasted two hours outranks a HIGH one
reported thirty seconds ago. The level is stored per blocker (`blocker.escalation_level`, checked
`between 0 and 6`). Level 6 is always **voluntary** — a merge proceeds only if *both* teams opt in
([team-state-model.md](team-state-model.md) invariants; `team_merge_suggestion` requires
`a_opted_in AND b_opted_in`). Who a mentor route reaches is decided by the router
([../research-ops/mentor-system.md](../research-ops/mentor-system.md)); the ladder decides only *when*
and *at what intensity*.

---

## Part IV — The early project-quality check

Most preventable failure is **set in the first hours**, not the last. A short, structured
`project_definition` (captured early, in [`008`](../../schema/008_team_rescue.sql)) catches the three
early failure modes — *impossible*, *trivial*, *unclear* — while there is still time to fix them:

```
what            — what are you building?
who_for         — who is it for?
core_challenge  — what is the hard part?
success_if      — what must work to count as done?
can_cut         — what is droppable if time runs short?
feasible_in_event — can the core be built in the time available?
```

> This is **not a pitch session** and not a gate anyone can fail. It is a five-field sanity check —
> a team that cannot yet answer `core_challenge` or `success_if` is not "bad," it is a team the
> engine can help *now* rather than at hour 60. Unclear → clarify; impossible → scope down (Part V);
> trivial → stretch (Part V). The point is early, cheap correction.

---

## Part V — The scope optimizer

Scope is the single most common preventable failure, in both directions. `scope_optimizer(
required_work, feasible_work)` compares estimated `RequiredWork` against `FeasibleWork` and returns a
verdict plus concrete moves — it **never forces complexity for its own sake**:

```
ratio = required_work / feasible_work

ratio > 1.3   OVER_SCOPED   → reduce features · use an existing component · narrow the problem
                              · change architecture · build the core proof first
ratio < 0.7   UNDER_SCOPED  → a harder technical extension · a better evaluation · a real user test
                              · a stronger artifact · additional functionality
0.7 ≤ r ≤ 1.3 WELL_MATCHED  → nothing; leave it alone
feasible ≤ 0  UNKNOWN       → no recommendation (we do not guess)
```

OVER_SCOPED is about **cut / reuse / narrow / reset**; UNDER_SCOPED is about **stretch / extend /
test** — offered as options, never imposed. A WELL_MATCHED team gets no suggestion at all. Assessments
are logged in `scope_assessment` (verdict + recommendation) so the event can learn whether its scope
advice actually helped. When a blocker is diagnosed as a scope problem, `best_support` routes it to
`SCOPE_RESET` rather than "another mentor" — a scope problem is not fixed by more hands.

---

## Part IX — The diagnosis taxonomy

Before acting, the engine names the *kind* of trouble. `diagnose(state)` reads the decomposed vector
and returns an **ordered list** (most likely first) drawn from the 10 `DIAGNOSES` — never a single
opaque verdict:

```
TECHNICAL_BLOCKER   blocker_severity ≥ 2
SCOPE_PROBLEM       scope_fit ≤ 1
TEAM_ROLE_GAP       role_coverage ≤ 1  OR  capability_coverage ≤ 1
COORDINATION        team_coordination ≤ 1  OR  decision_latency ≥ 2
PRODUCT_CONFUSION   goal_clarity ≤ 1  OR  problem_quality ≤ 1
MOTIVATION          energy ≤ 1  OR  confidence ≤ 1
DEPENDENCY_FAILURE · RESOURCE_SHORTAGE · DOMAIN_KNOWLEDGE · OTHER   (context-supplied / fallback)
```

A team can carry several diagnoses at once — the list is ordered, not collapsed, so the intervention
can address the binding one first. `diagnose` runs behind `_firewall`, so it only ever sees
operational dims.

---

## Part XXII — The quick-win engine

When a team is stuck or demoralized, the highest-leverage move is often not solving the whole problem
but restoring momentum. `quick_win(blocker_desc)` returns the **smallest demonstrable success**:

```
"one successful tool call"        BEFORE   "full agent workflow"
"a single record end-to-end"      BEFORE   "the whole pipeline"
"one screen that renders"         BEFORE   "the full UI"
```

The engine's suggestion is always: *find the smallest end-to-end slice that works, then build
outward.* One green result changes a team's trajectory more than an hour of advice. Quick-wins are
also the default response to a `MOTIVATION` diagnosis (alongside `BREAK`).

---

## Part XXIII — Pivot decision support

Whether to continue or pivot is a judgement only the team can make. `pivot_support(state)` therefore
returns **the factors, not a threshold** — there is deliberately no universal pivot cutoff:

```
factors: {
  time_remaining         : how much runway is left
  blocker_severity       : how deep is the current wall
  artifact_already_built : how much would a pivot discard
  motivation             : min(energy, confidence)
}
note: "decision support only — the team chooses; there is no universal pivot threshold"
```

The engine lays out the trade-off; the team decides. A pivot is a lifecycle transition
([team-state-model.md](team-state-model.md), `PIVOTING`), not a failure — a team that pivots with two
hours left and little built is making a rational call the engine should *support*, not veto.

---

## Parts LI–LII — Submission risk and demo rescue

A good project should never fail on a **forgotten demo**. `submission_risk(checklist)` tracks the
operational pieces and returns exactly what is missing, so reminders are *specific, not spam*:

```
required = { repo · deploy_or_demo · core_functionality · submission_form }

missing ≥ 2  → HIGH      missing == 1 → MED      missing == 0 → LOW
```

The output is the missing set plus a risk label. A HIGH team late in the event gets a targeted nudge
— *"your repo isn't linked and the form isn't submitted"* — not a generic blast. This closes the most
infuriating preventable loss in any hackathon: a working project that never gets submitted because
nobody remembered the form. `submission_risk_rising` is also a stall signal
([team-state-model.md](team-state-model.md), Part VIII), so demo trouble surfaces early, not at 4:59.

---

## Part LXVI — The required functions: support as a sequential decision

Three accessor functions are the public interface, and together they frame support as a **sequential
decision problem** — `state → intervention → next state → outcome`, logged for learning:

```
intervention_options(state)          → the actions available for this state, low→high
                                        (always includes NOTHING and RESOURCE; adds MENTOR/SPECIALIST,
                                         SCOPE_RESET/QUICK_WIN, REMATCH/CHALLENGE_LEVEL, BREAK by diagnosis)
best_support(state, blocked_minutes) → the recommended Recommendation(action, level, reason, evidence)
                                        — returns NOTHING when the team is EARLY/ON_TRACK and not stalled
simulate_intervention(state, action) → SCENARIOS + calibrated_probability=None  (Parts XXXIV–XXXV)
```

`best_support` is bottleneck-first: it weighs `blocker_severity`, `blocked_minutes`, and
`time_remaining`, maps them to a ladder level, and overrides to `SCOPE_RESET` when the diagnosis is a
scope problem. Its `Recommendation.evidence` is the decomposed vector that motivated it — a **status,
not a claim** (Evidence ≠ Claim). Every recommendation is a *hypothesis about what would help*, to be
confirmed or contradicted by the logged outcome — never a certainty.

---

## Parts XXXIV–XXXV — Contextual-bandit LATER, RL NOT YET

The long-run vision is a policy that learns the best intervention per state from experience. We are
explicit that **we are not there**, and the initial policy is deliberately hand-written and
human-reviewed:

```
NOW (Event 1)     a fixed, human-reviewed policy (this module). Every decision is inspectable and
                  overridable by a human in the war room. We collect state→intervention→outcome.
LATER             once multi-event data exists, a CONTEXTUAL BANDIT over interventions (which action
                  helps most, given the state) — with human veto retained.
NOT YET / MAYBE   full reinforcement learning over the sequential problem. Deferred until we have the
                  data, the calibration, and the ethical review to justify it.
```

`simulate_intervention` returns three scenarios (best / likely / worst) and
`calibrated_probability = None`, with `to_learn_it` naming exactly what data would make a real
probability possible: *state → intervention → outcome logged across multiple events*. We would rather
say UNKNOWN than fabricate a number.

---

## Part XXV — Preventable vs informative failure

Not all failure is waste. `classify_failure(cause)` separates the two, because the Event-1 metric
(Preventable Blocked Minutes, [adaptive-rescue-engine.md](adaptive-rescue-engine.md)) must **exclude**
genuine research failure:

```
INFORMATIVE (CAPTURE, do not "rescue")   algorithm_failed · hypothesis_failed
                                         architecture_underperformed · simulation_disproved_approach
PREVENTABLE (prevent / recover)          everything else — confusion, missing expertise, waiting,
                                         bad scope, operational friction
```

A team whose algorithm genuinely does not work has produced a **valuable result to capture**, not a
failure to prevent ([firewalls-and-ethics.md](firewalls-and-ethics.md); the research layer,
[../research-ops/critical-incidents.md](../research-ops/critical-incidents.md)). Trying to "rescue" an
informative failure would destroy the very finding worth keeping. The scope optimizer, quick-win, and
ladder all target the *preventable* column only.

---

## Parts LV–LVI — Logging the loop, and counterfactual discipline

Every intervention is recorded so the system can learn across events — `record_outcome(state_before,
intervention, state_after, outcome)` writes the loop into `rescue_intervention` (`state_before`,
`state_after`, `outcome`, `participant_experience`). And it enforces the discipline that makes that
data honest:

> **Precedence is not cause.** `record_outcome(..., causal=True)` raises. The stored relationship is
> literally `"intervention_preceded_outcome"`. The schema agrees: `rescue_intervention.causal_claim`
> is `default false CHECK (causal_claim = false)`. Causal language is reserved for an experiment or
> quasi-experiment — never inferred from a single team that got a mentor and then shipped.

This is what lets the log accumulate into something trustworthy: over many events we can *eventually*
learn `P(state_{t+1} | state_t, intervention)` from data — but until then we record what happened
and in what order, and we refuse to pretend we know why. That is the same epistemic honesty the whole
system runs on ([../research-ops/live-research-os.md](../research-ops/live-research-os.md)).

---

See also: [team-state-model.md](team-state-model.md) (the state this policy consumes) ·
[contribution-and-roles.md](contribution-and-roles.md) (rematch / merge / role routing at levels 3–6)
· [event-control-and-waste.md](event-control-and-waste.md) (event-wide resource fairness and the
blocked-minutes metric) · [firewalls-and-ethics.md](firewalls-and-ethics.md) (the firewall and
no-person-score guarantees this policy inherits).
