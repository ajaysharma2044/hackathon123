# Adaptive Questioning — The Branching Question Engine

**Part V of the [Live Research Operating System](live-research-os.md).** Layer 8 of the 17.

This is the engine that decides *which question comes next*, given what a participant just said. It
is the difference between a survey ("answer these 20 fixed items") and an interview ("you said you
switched — okay, what pushed you?"). The runnable kernel is
[`adaptive_questions.py`](../../engine/adaptive_questions.py); the stored form is the
`question_tree` / `question` / `question_branch` triple in
[`006_live_research.sql`](../../schema/006_live_research.sql).

This doc does **not** decide *whether* to ask (that is the trigger taxonomy in
[critical-incidents.md](critical-incidents.md)), *who* to ask next (that is
[adaptive-sampling.md](adaptive-sampling.md)), or the one-line prompts that fire without a tree
(that is [micro-prompts.md](micro-prompts.md)). It covers the branching tree that a flagged
interview walks, and the interviewing discipline that keeps every node honest.

> The binding constraint still governs: **the experience wins.** A tree is a ceiling on burden, not
> a script to complete. `walk` stops at `max_questions` and the participant can end it at any node.

## A tree is nodes + edges

```
        ┌──────────────────────────────────────────────────────────────┐
        │  Node(qid, text, answer_kind, burden_sec, branches{})         │
        │     branches: answer-value → next qid   ('*' = default edge)  │
        │     null next qid = terminal                                  │
        └──────────────────────────────────────────────────────────────┘
   answer "setup_friction"                 answer "cost"
        │                                        │
        ▼                                        ▼
   tc_friction_part ──"documentation"──► tc_doc_detail        tc_end
```

Each `Node` is one question; each entry in its `branches` dict is one labeled edge keyed by the
answer value, with `'*'` as the catch-all default. `Node.next_qid(answer)` resolves an answer to
the next node: **exact match first, then the `'*'` default, else terminal**. In the schema this is
`question` (the node) + `question_branch` (the edge, each carrying a `rationale` so the tree stays
auditable — every branch can say *why it exists*). Answer kinds are `MULTI_CHOICE | SHORT_TEXT |
VOICE | SCALE | BRANCH_ONLY`.

Branching is not a nicety — it is how burden is spent only where signal is. A team that switched for
cost reasons is never asked the documentation follow-up; a team that switched on setup friction is
routed straight into it.

## `walk()` — the path is the output, and it is burden-bounded

```python
Tree.walk(answers, max_questions=8) -> {"path": [...], "burden_sec": N, "hit_cap": bool}
```

`walk` follows the edges dictated by `answers` from the root and returns the **ordered path of qids
actually asked**, the summed burden of that path, and `hit_cap` (there was more, but we stopped).
Two disciplines are enforced in code, not merely promised:

- **Acyclic in practice.** A `seen` set guards against a cycle; trees are meant to be DAGs.
- **Burden is bounded.** `walk` stops at `max_questions` and sums `burden_sec` along the path, so a
  tree *cannot quietly become a 30-question survey*. `hit_cap=True` is a signal to the war room that
  this thread was richer than the budget allowed — a candidate for a sampled deeper interview, not a
  longer prompt. Every answered node debits the participant's ledger
  ([participant-burden.md](participant-burden.md), `MICRO_PROMPT` / `INTERVIEW` channel).

## The four reusable trees (the commercial spine)

Four modules ship in the engine, keyed by `module` name in `TREES`; each is a reusable
`question_tree` row. They are reusable because the same decision structure recurs across teams,
tracks, and products.

| Module | Root | What it reconstructs | Commercial engine |
|---|---|---|---|
| `technology_choice` | `tc_goal` | goal → considered → why chosen → expectation gap → switch → friction part → docs | research / product_dev |
| `rd_failure` | `rd_hyp` | hypothesis → test → broken assumption → ruled-out-or-not → next → 24h counterfactual | rd |
| `product_dev` | `pd_expect` | expected → built → missing capability → workaround → surprise → unexpected use → re-reach | product_dev |
| `activation` | `ac_known` | prior use → credit-effect-on-trial → counterfactual → credit-effect-on-usage → continuation → why | activation |

Worked branch, the canonical example, inside `technology_choice`:

```
tc_expectation  "did anything differ from what you expected?"
   │  yes
   ▼
tc_switch_consider  "did you consider switching?"
   │  yes
   ▼
tc_switch_cause  "what specifically pushed you toward switching?"
   │  setup_friction
   ▼
tc_friction_part  "which part of setup?"
   │  documentation
   ▼
tc_doc_detail  "what information were you looking for, and what did you do when you couldn't find it?"
```

This single path turns a raw `TOOL_SWITCH` event into a mechanism: *switch → setup friction →
documentation → the specific missing information and the workaround*. Any other `tc_switch_cause`
answer (cost, api_design, latency…) routes to `tc_end` instead — the documentation follow-up is
asked **only** of teams whose switch was actually about docs.

## More modules (the catalog, Part V tail)

The four trees are the built kernel; the full catalog the war room can compose from — each a
`question_tree` row with audited node wording — covers the rest of the team story
([team-trajectories.md](team-trajectories.md)):

```
onboarding          first-run path, where first value was reached, where it stalled
documentation       what was sought, found/not, and what they did when they couldn't find it
pricing / incentive did the credit change the decision or merely subsidize a decision already made
switching           trigger → alternative considered → what the new thing had that the old lacked
mentor-dependency   what they could not have done without help (confounder, never a person score)
problem-selection   why this problem, what was rejected, how constraints shaped scope
team-formation      who knew whom (prior-collaboration graph), how roles and the stack were decided
design-partner      who they built for, whether a real user was in the loop, what that user said
continued-use       7/30/90-day: still using it? unprompted? what would make them stop?
unexpected-use      the use they did not plan — highest-signal product-discovery material
```

These reuse nodes across modules (a `question` can belong to a tree but be referenced by several),
so `documentation` is both its own module and the tail of `technology_choice`. Modules are selected
by the trigger's `prompt_key` (see [critical-incidents.md](critical-incidents.md)): a
`RD_HYPOTHESIS_FAILURE` flagged for interview opens `rd_failure`; an `UNEXPECTED_USE_CASE` opens
`product_dev` / `unexpected-use`.

## Good interviewing methodology (the node-wording discipline)

A branching engine is only as good as its questions. Each node carries `is_leading_audited` in the
schema; a node may not ship until it passes this review. The rules the audited wording enforces:

**Avoid:**

| Anti-pattern | Bad | Why it corrupts the evidence |
|---|---|---|
| **Leading** | "Was the documentation frustrating?" | plants the answer; manufactures the theme it pretends to find |
| **Loaded / assumed cause** | "Why did the bad API design make you switch?" | assumes API design *and* that it caused the switch |
| **Forced-causal** | "What made you choose X?" (when they may not have chosen) | presumes a deliberate decision that may not have happened |
| **Unanswerable why** | "Why are you the kind of person who…" | invites post-hoc rationalization, not recall; edges toward trait inference (forbidden) |
| **Over-long** | a 40-word multi-clause question | exceeds one breath; the participant answers only the last clause |

**Prioritize instead:**

- **Concrete recent events** over general attitudes — "when you hit that error at ~16:30, what did
  you do next?" beats "how do you feel about error messages?"
- **Specific decisions** over hypotheticals — "what did you consider?" (`tc_considered`) names the
  real shortlist.
- **Careful counterfactuals** — `ac_without` ("would you have tried it without the credit?") and
  `rd_24h` ("with another 24 hours, what would you test first?") isolate the causal contribution
  without leading.
- **Critical incidents** — anchor on the switch, the failure, the workaround — the moments already
  detected as triggers, asked while they are still fresh.
- **Comparison** — `pd_missing` ("a capability you expected that turned out to be missing?") surfaces
  the gap against the expectation, not against our framing.
- **Timeline reconstruction** — the ordered `walk` path *is* a micro-timeline; stitched across a
  team it becomes the `decision_episode` sequence in [team-trajectories.md](team-trajectories.md).

Note how the built trees already embody this: `tc_goal` asks what they were *trying to accomplish*
(not "why did you pick X"); `rd_assumption` asks *which assumption turned out wrong* (concrete,
post-hoc but factual); `pd_unexpected` opens with "tell me about the unexpected use" (an invitation
to narrate a concrete event). None of them names a cause the participant did not supply.

## Where the answers go

An answered node becomes a `prompt` row (instance-level, with `answer_text` / `answer_choice`,
`skipped` mandatory, `burden_sec` debited). Verbatim words that carry signal are promoted to a
`qualitative_observation` (`linked_qual_id`) and then coded — the
`RawQuote → Observation → Code → Theme` pipeline that feeds the evidence graph
([`evidence_graph.py`](../../engine/evidence_graph.py)). The fact/interpretation split from
[capture-system.md](../capture-system.md) holds throughout: what they *said* is evidence; what it
*means* is a separately-labeled, separately-tested claim.

## What this layer is not

- **Not adaptive because it profiles people.** Branching is on *answers about work in context*, never
  on any inferred trait — there is no person model here, by construction ([STATE.md](../STATE.md),
  no-person-score invariant; schema Invariant 5).
- **Not a completion target.** A short path that terminates early is a *success*, not a dropout;
  `hit_cap` and early termination are both first-class outcomes.
- **Not the only channel.** Most incidents get a single [micro-prompt](micro-prompts.md) or nothing
  at all; a full tree walk is reserved for the sampled or trigger-flagged deeper interview.
