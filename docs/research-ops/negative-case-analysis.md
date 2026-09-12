# Negative-Case Analysis — Deliberate Disconfirmation

**Parts XIII and XXIII (anti-bias) of the [Live Research Operating System](live-research-os.md).**

This is the system's structural defence against confirmation bias. The rule is one sentence:

> **For every emerging explanation, ask: "what evidence would make this wrong?" — then go look for
> it on purpose.**

Looking is not optional and not incidental. The sampler schedules disconfirming interviews *first*
([adaptive-sampling.md](adaptive-sampling.md)), and a claim **cannot be promoted to a published
finding** until a negative-case search has actually been run
([`evidence_graph.py`](../../engine/evidence_graph.py) `can_promote`). The stored form is the
`negative_case` table in [`006_live_research.sql`](../../schema/006_live_research.sql); the
selection logic is the `DISCONFIRMING` segment map in
[`adaptive_sampling.py`](../../engine/adaptive_sampling.py).

This matters because every prior research pass in this project *baked the conclusion in*
([STATE.md](../STATE.md), "Correcting the frame"). Negative-case analysis is how the event-embedded
research refuses to repeat that mistake: it is built to *discover* the truth, not confirm a desired
one.

## The disconfirming-segment map

Every explanation names a confirming segment (where the supporting case lives) and, via
`DISCONFIRMING`, the segment where a *counterexample* would live:

```
explanation built on…      confirm in…          look for the break in…
adoption                   ADOPTER              NON_ADOPTER
switching                  SWITCHER             NON_SWITCHER
abandonment                ABANDONER            SUCCESSFUL_TEAM
team success               SUCCESSFUL_TEAM      FAILED_TEAM
mentor-driven outcome      HIGH_MENTOR_SUPPORT  LOW_MENTOR_SUPPORT
novel usage                UNEXPECTED_USE_CASE  COMMON_USE_CASE
R&D winner path            RD_WINNER            RD_FAILURE
tool choice                CHOOSER              NON_CHOOSER
```

The map encodes a simple discipline: to test "X causes Y," you need cases of X-without-Y and
Y-without-X, not just more cases of X-with-Y. A theme that only ever appears where you went looking
for it is not evidence — it is an echo.

## Worked example

**Emerging explanation:** *"Teams abandon Product X because its auth setup is hard."*

Confirming evidence accumulates easily: abandoners who hit auth friction, a cluster of
`friction:auth_setup` codes, a few vivid quotes. This is exactly where confirmation bias wins — the
explanation *feels* settled. The negative-case search deliberately goes the other way:

```
Disconfirming question:  "What evidence would make 'auth friction causes abandonment' wrong?"

Search 1  →  segment NON_SWITCHER / SUCCESSFUL_TEAM
             teams that hit the SAME auth friction but STAYED.
             If many stayed, auth friction is not sufficient for abandonment.

Search 2  →  segment ABANDONER with no auth problem
             teams that abandoned X but never hit auth friction at all.
             If many, auth friction is not necessary for abandonment.

Stratify both searches across:
   experience     (did only first-timers abandon? then it's experience, not auth)
   mentor-support (did LOW_MENTOR_SUPPORT teams abandon and HIGH stay? then it's support, not auth)
```

Three outcomes, all honest:

- **No counterexamples found** → the explanation survives a real attempt to break it; confidence can
  rise (but see the promotion gate — it still must be *searched*, not merely unfalsified by luck).
- **Counterexamples found** → the explanation is wrong or partial. Maybe auth friction only causes
  abandonment for *inexperienced* teams *without* mentor support — a sharper, truer claim.
- **Search still open** → the claim stays un-promotable. An untested explanation is not a finding.

## Wired into the sampler

Negative-case analysis is not a review step at the end — it drives *which interview happens next*.
`Sampler.suggest_next` checks the disconfirmation deficit **before** anything else:

```python
# priority 1, ahead of confirming deficit and coverage gaps
for ex in explanations:
    if ex.disconfirming_n < ex.target_each:
        seg = DISCONFIRMING.get(ex.confirming_segment)
        pick = self._pick(candidates, seg)
        if pick:
            return SamplePlan(pick.participant_id, seg,
                              f"seek a case that could FALSIFY: '{ex.text}'", "DISCONFIRM")
```

So an explanation **cannot** quietly accumulate only-confirming evidence: the moment it is short of
its disconfirming quota, the next interview is spent trying to break it. Each `Explanation` tracks
`confirming_n` and `disconfirming_n` against `target_each` (default 3) — the system treats an
explanation as *tested* only when both sides have been sought.

## Wired into the evidence-graph promotion gate

The same discipline is enforced structurally at the point a claim would become client-facing.
`Claim.can_promote()` in [`evidence_graph.py`](../../engine/evidence_graph.py) refuses promotion
unless:

```
1. there is at least one SUPPORTING evidence item, AND
2. a negative-case search was at least PLANNED        → else "confirmation-bias guard"
3. that search was actually RUN (nc.found is not None) → else "run it before promoting"
4. if a counterexample WAS found, confidence is not HIGH → else "lower it first"
```

In the schema this is the `negative_case` row (`disconfirming_question`, `searched_segment`,
`found`, `evidence_ref`) bound to a `claim`, plus signed `claim_evidence`
(`polarity ∈ {SUPPORTS, CONTRADICTS}`). A claim that has never been shot at cannot graduate:

```
Claim (PROPOSED)
   │  supporting evidence only
   ▼
   can_promote() → (False, "no negative-case search was even planned")   ✗ blocked
   │
   │  record NegativeCase(disconfirming_question, searched_segment); run the disconfirming interview
   ▼
   NegativeCase.found = False (no counterexample)  or  True (counterexample exists → lower confidence)
   ▼
   can_promote() → (True, "ok")                                           ✓ may become a Finding
```

`add_evidence` reinforces it: a `CONTRADICTS` item automatically caps confidence at `MED` unless
explicitly re-justified — contradictory evidence can never be silently outvoted.

## How this prevents confirmation bias (the failure modes it closes)

| Failure mode | Without negative-case analysis | With it |
|---|---|---|
| **Cherry-picking** | interview only abandoners; "see, auth is the problem" | sampler forces `SUCCESSFUL_TEAM` / `NON_SWITCHER` interviews first |
| **Echo-chamber coding** | frequent theme read as cause | theme frequency ≠ outcome prediction, and must survive a disconfirming search ([capture-system.md](../capture-system.md)) |
| **Premature certainty** | a vivid quote promoted to a finding | `can_promote` blocks until the search is run |
| **Silent overrule of contradiction** | inconvenient counterexample ignored | `CONTRADICTS` caps confidence at MED; the negative case is first-class in `trace()` |
| **Confounds read as causes** | "auth causes abandonment" (really experience) | stratify the disconfirming search across experience / mentor-support |

The payoff is the test the whole system must pass ([live-research-os.md](live-research-os.md)): we
can hand a client a finding **traceable to the evidence *against* it** — because the evidence against
it was deliberately sought, recorded, and, where found, allowed to change the claim. A negative case
is not a threat to the research; it is the research working.
