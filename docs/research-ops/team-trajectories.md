# Team Trajectories — the team story (Parts XXII–XXIV)

The team story is the first of the two chains the master doc
([live-research-os.md](live-research-os.md)) sets out to reconstruct: **what did they want → what
did they consider → what did they choose → why → what happened → where did they fail → who helped →
what changed their mind → what did they switch to → what did they build → what continued.** This
document specifies the object that holds that arc — the `team_trajectory` — and the discipline that
keeps it honest.

> A `team_trajectory` is **DERIVED**, exactly like a `behavioral_episode` in
> [research-data-model.md](../research-data-model.md). It is assembled from raw evidence and
> observations, carries a `model_version`, and is **re-derivable** — never hand-edited. If the
> assembler improves, you throw the old story away and rebuild it. A story you cannot rebuild from
> raw is not a finding; it is a memory.

The schema is `team_trajectory` + `decision_episode` in
[`006_live_research.sql`](../../schema/006_live_research.sql); the runnable kernel is
[`team_trajectory.py`](../../engine/team_trajectory.py).

## The two invariants (enforced in `assemble()`)

```
PROVENANCE REQUIRED   every episode cites ≥1 raw source (evidence_event_ids OR observation_ids).
                      Episode.has_provenance() is False → assemble() raises. No provenance, no node.
RE-DERIVABLE          assemble() is a pure function of (team_id, raw_episodes, model_version).
                      Run it twice on the same inputs → byte-identical ordered arc. Duplicate seq
                      numbers raise: a hand-edited arc is structurally rejected.
```

These are not style rules. They are the structural defence against the trajectory quietly becoming
an analyst's story *about* a team rather than a traceable reconstruction *of* one.

## XXII — The DECISION trajectory (the default arc)

The canonical phase order (`PHASES` in [`team_trajectory.py`](../../engine/team_trajectory.py),
`decision_episode.phase` in the schema):

```
TEAM CREATED → PROBLEM_SELECTED → INITIAL_PLAN → TOOL_SET → FIRST_APPROACH → BLOCKER → HELP
  → DECISION → SWITCH / PIVOT → SECOND_APPROACH → ARTIFACT → OUTCOME → CONTINUATION
```

Every transition carries the same five fields, so the arc reads as evidence, not narration:

| Field | What it holds | Where it comes from |
|---|---|---|
| **Behavior** | the observed "what", no inference | `observation.observed_event`, `evidence_event` |
| **Explanation** | the qualitative "why", hedged + labeled | `observation.researcher_interpretation`, interview excerpt |
| **Evidence** | the raw rows this node rests on | `evidence_event_ids[]`, `observation_ids[]` |
| **MentorIntervention** | help received at this node, if any (a confounder) | `mentor_interaction_id` → `mentor_interaction` |
| **ArtifactState** | the repo/deploy state at this node | `artifact_state`, linked artifact |

Behavior and Explanation are kept in **separate columns** for the same reason a field note keeps
`observed_event` apart from `researcher_interpretation` (Invariant 1,
[live-research-os.md](live-research-os.md)): "they switched off Product X at hour 14" is a fact;
"they switched because auth was confusing" is a hypothesis that must point at a quote or an
observation and may be wrong. MentorIntervention is recorded on the node because mentor help is a
**confounder** on every downstream outcome ([qualitative-coding.md](qualitative-coding.md)) — a team
that pivoted cleanly after `HEAVY` mentor intensity did not necessarily pivot *well on its own*.

## XXIII — The RD_REASONING trajectory (value lives in the failed paths)

For teams doing genuine R&D, the interesting structure is not the product arc but the **reasoning
arc** — and the commercial value is concentrated in the paths that *failed* and why, which no
artifact and no demo ever records.

```
Problem → InitialHypothesis → WhyHypothesis → Approach → Experiment → Result
  → Failure → Interpretation → NewHypothesis → NewApproach → Outcome → NextExperiment
```

`kind = RD_REASONING` episodes carry the R&D fields from the schema/engine:
`hypothesis`, `why_hypothesis`, `experiment`, `result`, `assumption_failed`, `interpretation`,
leading to the `NewHypothesis` of the next node. The spine to protect:

```
  HYPOTHESIS ──(why this one?)──► APPROACH ──► EXPERIMENT ──► RESULT
       ▲                                                        │
       │                                                        ▼
  NEW HYPOTHESIS ◄── INTERPRETATION ◄── FAILURE (assumption_failed: what broke + why)
       │
       └──► NEXT EXPERIMENT (what to try next — captured while it is fresh)
```

> **The dead branch is the asset.** "We assumed the embedding model would handle long context; it
> silently truncated at 8k and we only found out at hour 20" is worth more to an R&D client than the
> winning approach, because it is exactly the knowledge that never ships. `assumption_failed` plus
> the `Interpretation` that followed it is the node we work hardest to capture at the fresh moment.

## XXIV — The PRODUCT_JOURNEY trajectory (adoption, friction, switch, continued use)

For product/activation clients, the arc is the **lived journey with a tool** — the chain
[research-framework.md](../research-framework.md)'s funnel measures quantitatively, reconstructed
qualitatively per team:

```
InitialExpectation → DiscoverySource → ConsiderationSet → InitialChoice → Activation
  → Friction → Support → Integration → Workaround → Switch → FinalUsage → PerceivedValue → ContinuedUse
```

`kind = PRODUCT_JOURNEY` episodes carry `expectation`, `friction`, `workaround`, `switched_to`.
`ConsiderationSet` is the `ChoiceSet` primitive from [research-data-model.md](../research-data-model.md)
— a choice is only a preference signal if we know what else was reachable. `ContinuedUse` is
populated from the 7/30/90-day follow-up, so a product-journey trajectory is not *closed* at event
end; it accretes the continuation node when the follow-up wave lands.

## How a trajectory is assembled (pure, re-derivable, provenance-required)

`assemble(team_id, raw_episodes, model_version)` does exactly three things, in order:

```
 1. REJECT duplicate seq numbers        → a clean ordered arc, never a hand-patched one
 2. REJECT any episode with no provenance → every node traces to raw (evidence_event / observation)
 3. SORT by seq and return Trajectory(team_id, model_version, ordered)
```

It computes nothing it cannot re-derive: no hidden state, no network call, no analyst free-text
injected after the fact. `Trajectory.story()` renders the ordered `(phase, behavior, explanation)`
list for the report; `Trajectory.transitions()` yields the adjacent phase pairs for the switching
and blocker analytics. Because assembly is pure, two analysts running the same `model_version`
against the same raw rows get the **same arc** — a precondition for the arc being evidence a client
can audit rather than one analyst's reading.

The raw episodes themselves are produced upstream by the human sensor network
([live-research-os.md](live-research-os.md)): observers write `observation` rows, mentors write
`mentor_interaction` rows, telemetry writes `evidence_event` rows, and the note-synthesis role links
them into candidate episodes. The trajectory is the *assembly* of those, not a new source of fact.

## A worked illustrative team (all values illustrative)

Team "Kestrel" — 3 builders, AI track. Rendered as the DECISION arc. Every `ev:*` / `obs:*` /
`mi:*` id below is an illustrative pointer to a raw row; in production each is a real FK.

```
seq phase            behavior                              explanation (hedged)          evidence       mentor    artifact
 1  PROBLEM_SELECTED  picked "meeting-notes summarizer"     "wanted something demoable"   obs:114        —         —
 2  INITIAL_PLAN      whiteboarded RAG pipeline             self-reported at START         chk:START/K    —         empty repo
 3  TOOL_SET          chose Product-X API + Neon            ConsiderationSet: also saw     obs:131        —         scaffold
                                                            Pinecone, Supabase (reachable)
 4  FIRST_APPROACH    built ingest + embed loop             —                              ev:2201,2208   —         ingest.py
 5  BLOCKER           auth to Product-X failing at hour 6   "docs didn't match console"    obs:177        —         401s in logs
 6  HELP              flagged REPEATED_HELP_REQUEST         mentor walked through keys     obs:181        mi:54     —
                                                            (intensity MODERATE)           (HIGH conf)   (conf'd)
 7  DECISION          kept Product-X, narrowed scope        "too far in to switch stacks"  obs:190        —         —
 8  SECOND_APPROACH   dropped live embeds, precomputed      workaround after friction      ev:2260        —         batch_embed
 9  ARTIFACT          deployed demo on Sunday               —                              ev:2301(deploy)—         live URL
10  OUTCOME           shipped, placed top-10                judge rubric                   ev:2330        —         tagged v1
11  CONTINUATION      still committing at 30 days           FOLLOWUP_30: "using it weekly" chk:FU30/K     —         +14 commits
```

What the discipline buys us on this one team:

- **Node 5→7 is the money.** The BLOCKER→HELP→DECISION sub-arc shows a team that *did not switch*
  despite high auth friction — a **negative case** for any claim that "auth friction causes
  abandonment" ([evidence-graph.md](evidence-graph.md)). The trajectory surfaces it automatically
  because the arc enumerates what happened, not only the outcome.
- **Node 6 carries `mi:54` (MODERATE).** Kestrel's clean recovery is **confounded** by mentor help.
  Any downstream claim about Product-X's self-serve recoverability must treat this team as
  mentor-assisted, not organic.
- **Node 11 exists only because the follow-up wave landed.** Before FOLLOWUP_30 this trajectory
  ended at OUTCOME; continuation is accreted, never assumed.

Contrast team "Merlin" (not shown in full): identical BLOCKER at node 5, but node 6 = SWITCH to a
competitor and node 10 OUTCOME = abandoned. Two teams, one friction, opposite arcs — which is
precisely the supporting/contradictory pair the [evidence-graph.md](evidence-graph.md) promotion
gate requires before "auth friction → abandonment" may ever become a Finding.

## Where trajectories feed

- **Synthesis**: the arcs are the raw material the war room codes into themes
  ([qualitative-coding.md](qualitative-coding.md)).
- **Evidence graph**: a trajectory node (with its provenance) is citable as `SUPPORTS` or
  `CONTRADICTS` evidence on a claim ([evidence-graph.md](evidence-graph.md)).
- **Analytic memos**: a surprising transition is the seed of an [analytic-memos.md](analytic-memos.md)
  entry and often a new backlog question.

A trajectory is never itself a client-facing claim. It is a **traceable reconstruction** that claims
are built *from* — and, just as often, a reconstruction that **contradicts** the claim we expected
to make. Keeping those two uses honest is the whole point of the provenance invariant.
