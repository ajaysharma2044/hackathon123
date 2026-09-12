# The Judging System

How Event 1 turns ~45 shipped prototypes into a defensible ranking and a set of awards — the
**science-fair expo**, the **finals**, and the **sponsor/category rounds** — and how that
evaluation stays cleanly separated from the research product.

This is the EVENT OPERATIONS view. It sits **downstream of the decision to run Event 1**
([../event1-design.md](../event1-design.md)) and inherits the IP terms decided before the event
([../recruiting-legal.md](../recruiting-legal.md)). Frame: [operational-architecture.md](operational-architecture.md),
[org-chart-and-roles.md](org-chart-and-roles.md); rooms/schedule: [logistics.md](logistics.md),
[run-of-show.md](run-of-show.md). The kernel is
[`../../engine/judging_assignment.py`](../../engine/judging_assignment.py) and the tables are `judge`
/ `submission` / `judging_round` / `judging_assignment` / `judging_score` / `prize` in
[`../../schema/007_event_ops.sql`](../../schema/007_event_ops.sql).

> **One discipline, stated once.** Judging ranks **projects, not people**, and its output is an
> awards artifact — never a research finding and never a person score. The wall between the two is
> structural (see *Judging feeds research, but is not research* below), not a promise.

## The shape: expo → finals, with sponsor rounds in parallel

```
  SUBMISSIONS (Devpost-style)          a team's judged artifact: repo + deploy + writeup + table #
        │                               submission.{repo_url,deploy_url,devpost_url,table_number,category_tags}
        ▼
  ┌─ SCIENCE-FAIR EXPO ──────────────────────────────────────────────────────┐
  │  hackers stay at assigned tables; JUDGES ROTATE (sourced: MLH).           │
  │  every submission seen `rounds` times by distinct, non-conflicted judges. │
  │  each judge stack-ranks their own batch → 3/2/1 points → aggregate.       │
  └───────────────┬───────────────────────────────────────────┬──────────────┘
                  │ top of the aggregate                       │ tagged submissions only
                  ▼                                             ▼
         ┌─ FINALS ────────────────┐              ┌─ SPONSOR / CATEGORY ROUNDS ─────────┐
         │ ~5–8 finalists pitch a   │              │ subject-matter judges over ONLY the │
         │ diverse panel on stage;  │              │ submissions tagged for that prize.  │
         │ ~7 min/team (sourced).   │              │ a sponsor judge decides HERE — never│
         │ decides GRAND prize.     │              │ the neutral grand prize (conflict). │
         └────────────┬─────────────┘              └──────────────────┬──────────────────┘
                      ▼                                                ▼
                 prize_award (GRAND)                         prize_award (CATEGORY/SPONSOR/R&D)
```

The expo is the wide, cheap, de-biased first pass; the finals are the narrow, high-ceremony deciding
round; sponsor/category rounds run in parallel over a tagged subset. All three are `judging_round`
rows distinguished by `kind ∈ {SCIENCE_FAIR, FINALS, SPONSOR_CATEGORY}`.

### Sourced vs design choice

| Element | Status |
|---|---|
| Science-fair format (hackers stay, judges rotate) | **sourced** — MLH organizer guide |
| `J = ceil(P·n·t / T)`, defaults n=3, t=4, T=120 | **sourced** — MLH; 175 projects/2h → 18 judges |
| Stack-rank top-3 → 3/2/1, summed across judges | **sourced** — MLH de-bias recommendation |
| Rubric criteria (complexity/creativity/impact/execution/presentation) | **sourced** — Devpost |
| Finals ~7 min/team (3–5 pitch + 2 setup) | **sourced** — common elite-event practice |
| ~45 teams, 5–8 finalists, the specific panel sizes below | **design choice** — Event 1, *illustrative* |

## How many judges — the formula, worked

The judge count is a coverage constraint, not a taste: to see every project `rounds` times in a
fixed window, you need enough rotating judges. `judges_needed(P, rounds, minutes, window_min)` in
both [`../../engine/judging_assignment.py`](../../engine/judging_assignment.py) and
[`../../engine/staffing_model.py`](../../engine/staffing_model.py) is the single source of truth:

```
J = ceil( P × rounds × minutes / window )          P = projects (teams), not participants
  sourced defaults:  rounds n = 3                   each project seen 3× by distinct judges
                     minutes t = 4                  2 demo + 1 Q + 1 travel, per visit
                     window  T = 120 min            the science-fair block
  sourced anchor:    175 projects / 120 min → ceil(175·3·4/120) = ceil(17.5) = 18 judges
```

Event 1 runs ~150–200 builders at a team-size-4 planning midpoint ([../event1-design.md](../event1-design.md)),
so **~38–50 teams**. Worked across the plausible range (all rows *illustrative* except the sourced
MLH anchor):

| Participants | Teams (P) | n | t | T | `judges_needed` | Note |
|---:|---:|---:|---:|---:|---:|---|
| 120 | 30 | 3 | 4 | 120 | **3** | floor; at/near the `j<3` warning in `staffing_model.plan` |
| 150 | 38 | 3 | 4 | 120 | **4** | |
| **180** | **45** | **3** | **4** | **120** | **5** | the Event 1 midpoint: ceil(45·3·4/120)=ceil(4.5) |
| 200 | 50 | 3 | 4 | 120 | **5** | |
| 180 | 45 | 3 | 4 | 90 | **6** | a shorter window raises the floor; 150 min lowers it to 4 |
| (MLH) | 175 | 3 | 4 | 120 | **18** | sourced reference, for calibration |

> **The formula gives a FLOOR, not the roster.** Five judges is the minimum that can physically
> cover 45 teams three times in two hours. A premium, one-shot event **deliberately over-recruits**
> (Event 1 plans ~12–18 judges, *illustrative*) for three reasons: richer overlap makes the
> aggregate stack-rank more robust, a diverse panel reduces single-judge taste bias, and a no-show
> judge must not break coverage. `staffing_model.plan` reports the floor; the Judging & Awards head
> sets the actual count above it. Fewer than 3 judges cannot support 3-round stack-ranking at all —
> `plan` raises exactly that warning.

## The conflict-free rotation

`assign_science_fair(submissions, judges, rounds)` builds the expo schedule so that:

1. **Every submission is seen exactly `rounds` times** by **distinct** judges.
2. **No judge ever evaluates a submission they are conflicted on** — `_conflicted(judge, sub)` is
   true when `sub.team_id ∈ judge.conflict_team_ids` (their own team, or a team they mentored). The
   engine enforces this; it is not left to the judge's honor. On the schema side the blocked pairing
   is recorded as `judging_assignment.conflict_blocked = true`.
3. **Load is balanced** — each submission is given to the `rounds` **least-loaded** eligible judges,
   so no one is overloaded and the counts stay even.
4. **Hardest-to-cover submissions go first** — the function sorts submissions by *fewest
   non-conflicted judges* ascending, so a heavily-conflicted project is scheduled before the easy
   ones and we never paint ourselves into a corner. If any submission has fewer than `rounds`
   eligible judges, it **raises** rather than silently under-covering — the operational signal to
   recruit more neutral judges or cut a round.

```
  order submissions by (count of non-conflicted judges) ASC   ← scarcest coverage first
  for each submission s:
      eligible = judges with s.team_id NOT in conflict_team_ids
      if len(eligible) < rounds:  RAISE  (recruit neutral judges / reduce rounds)
      pick the `rounds` least-loaded eligible judges ; increment their load
```

**Sponsor / category prizes** use `assign_category(submissions, judges, category, rounds=2)`: it
filters to submissions whose `category_tags` include the category and to judges whose `expertise`
covers it, then runs the same balanced rotation over that subset. **Sponsor judges are allowed
here** — it is their prize. They are *not* in the neutral grand-prize panel, because a sponsor judge
deciding the grand prize is a conflict (sourced MLH guidance; mirrored by `judge.is_sponsor_judge`
and `judge.affiliation` in the schema).

## Why stack-ranking beats absolute scores

A 1–10 absolute score conflates two things: how good the project is, and how strict the judge is. A
lenient judge's 8 and a harsh judge's 5 can mean the same thing — and summing raw scores lets the
harsh/lenient axis swamp the quality axis. **Stack ranking removes the judge's scale entirely:** a
judge only has to say *which of the projects they saw was best*, and rank maps to points.

`RANK_POINTS = {1:3, 2:2, 3:1}` (sourced MLH default). `stack_rank_batch(ranked_ids)` maps a judge's
own best→worst ordering to points; `aggregate(batches)` sums across all judges and sorts best→worst,
ties broken by id for determinism. A worked, *illustrative* example — three judges, five projects:

```
  Judge A ranks:  P3 > P1 > P4   →  P3:3  P1:2  P4:1   (P2,P5: 0)
  Judge B ranks:  P1 > P3 > P2   →  P1:3  P3:2  P2:1   (P4,P5: 0)
  Judge C ranks:  P3 > P2 > P1   →  P3:3  P2:2  P1:1   (P4,P5: 0)

  aggregate():   P3 = 3+2+3 = 8      ← wins on CONSENSUS, not on one judge's generosity
                 P1 = 2+3+1 = 6
                 P2 = 0+1+2 = 3
                 P4 = 1+0+0 = 1
                 P5 = 0
```

P3 wins because it placed high on **distinct** judges' ballots — exactly the de-biasing property raw
scores lack. Points are stored on `judging_score.points` (with `rank_in_batch`); the optional
per-criterion `rubric` jsonb holds notes but does **not** feed the ranking. Finals use the same
mechanism over the finalist set, typically a single diverse on-stage panel.

## The rubric (published before the event)

Criteria are announced with the prize list **before** builders start, so teams build toward a known
target and judging is legible rather than a black box (sourced — Devpost common criteria):

| Criterion | The question it asks |
|---|---|
| **Technical complexity** | Was the hard thing actually hard, and did they do it? |
| **Creativity / originality** | Is the idea non-obvious, or a rebuild of something that exists? |
| **Potential impact** | If it worked at scale, would it matter? |
| **Execution / UX** | Does it actually run, and is it usable? |
| **Presentation** | Can they explain what they built and why? |

Judges apply the **same** criteria across all eligible projects in a round; a sponsor/category round
may add that sponsor's own criterion over only the tagged subset. The rubric is guidance for the
ranking — judges still hand back an ordering, not a weighted numeric score (see *Why stack-ranking*,
and the "never emit a score" discipline in [../recruiting-legal.md](../recruiting-legal.md)).

## Submissions, judge recruiting, and the clock

- **Submission platform.** Teams submit a Devpost-style entry: `repo_url`, `deploy_url`,
  `devpost_url`, a `table_number` (science-fair station), and `category_tags` (prizes entered).
  `submitted_at` closes at the hard deadline; late repos are frozen at the deadline commit
  ([run-of-show.md](run-of-show.md)).
- **Judge recruiting + briefing.** Judging & Awards recruits a **neutral** panel (faculty, alumni,
  domain experts) plus **sponsor** judges for category prizes. Every judge acknowledges the CoC
  (`judge.coc_acknowledged_at`) and declares conflicts (teams they mentored/are affiliated with)
  *before* the rotation runs — those declarations populate `conflict_team_ids`. A short pre-expo
  briefing covers the rubric, the stack-rank mechanic ("rank your top 3, don't score"), the conflict
  rule, and the clock.
- **The 3-minute limit.** Each table visit is time-boxed — 2 min demo + 1 min Q, ~1 min travel
  (sourced MLH `t=4`). A visible timer and runners keep the rotation on schedule; finals are the
  longer, unrushed round at ~7 min/team.

## Prizes and IP

`prize.kind ∈ {GRAND, CATEGORY, SPONSOR, R&D_CHALLENGE}`; winners land in `prize_award`.

| Prize kind | Judged by | Over what |
|---|---|---|
| **GRAND** | neutral panel (finals) | all eligible submissions |
| **CATEGORY** | subject-matter judges | submissions tagged for the category |
| **SPONSOR** | that sponsor's judges | submissions tagged for that sponsor |
| **R&D_CHALLENGE** | challenge owner + neutral judges | submissions against the directed challenge |

**IP terms are decided in the agreement BEFORE the event and disclosed in the challenge** — not
negotiated at the judging table ([../event1-design.md](../event1-design.md) Q19;
[../recruiting-legal.md](../recruiting-legal.md)). The default: **participants keep everything they
build**; for a paid R&D challenge, the buyer licenses or owns *that challenge solution only*, stated
up front. `prize.ip_terms` records the agreed terms per prize. Prize sizing follows the
marginal-value-of-the-next-team logic, not a vanity purse ([../event1-design.md](../event1-design.md) Q18/Q22).

## The logistics run

```
  BEFORE   tables numbered + mapped ; signage ; judge badges + conflict sheets ; submission freeze
           rotation computed (assign_science_fair) ; printed judge routes
  EXPO     judges walk routes ; runners keep the clock ; points entered per batch (judging_score)
  TALLY    aggregate() → finalist cut ; post finalists ; reset stations for finals
  FINALS   on-stage pitches ~7 min ; neutral panel ; grand prize decided
  AFTER    awards ceremony (prize_award) ; judge debrief (what the rubric missed, next-event notes)
```

Signage, table numbering, and finals AV are a **crew** job
([volunteers-and-crew.md](volunteers-and-crew.md)); the rotation and tally are **Judging & Awards**.
Table count and station power draw are sized in [logistics.md](logistics.md).

## Judging feeds research, but is not research

Judging is **structured evaluation of the built artifact** — the same repo/deploy the research layer
analyzes. That makes it a genuine input to research: the edge `FEEDS_RESEARCH` in `role_dependency`
([`../../schema/007_event_ops.sql`](../../schema/007_event_ops.sql)) records that Judging & Awards
produces signal the research layer can read (which projects shipped, on what stack, with what
maturity). But the wall is strict:

```
  OPS / AWARDS OUTPUT        judging_score.points · prize_award · the finalist cut
  (ranks PROJECTS)           → the ceremony, the sponsor's category winner
                                 STAYS in the event-ops tables

  RESEARCH EVIDENCE          observation · evidence_event · interview_excerpt · mentor_interaction
  (claims about BEHAVIOR)    → the evidence graph → aggregate, caveated findings per client
                                 (../research-ops/evidence-graph.md)
```

- **A judge score is never a research evidence row.** It ranks a project for an award; it is not an
  `observation` and never anchors a `claim_evidence` row. The evidence graph's polarity-signed
  support/contradiction machinery ([../research-ops/evidence-graph.md](../research-ops/evidence-graph.md))
  draws on the *artifact*, not on who won.
- **No person scoring, ever.** Judging ranks projects; it produces no quality / employability /
  founder score on any individual — the same prohibition the research OS encodes
  ([../research-ops/participant-experience.md](../research-ops/participant-experience.md)) and the
  recruiting product's "never emit a score" rule ([../recruiting-legal.md](../recruiting-legal.md)).
- **Winning is a covariate, not a conclusion.** That a team won is a fact the research layer may
  *note*; it is never laundered into "Product X caused success." The artifact is the cross-check on
  self-report; the award is not evidence about a product.

So judging is the event's visible climax and an honest feed into the research asset — built so those
two roles never contaminate each other.
