# Qualitative Coding — the pipeline (Parts XXV–XXVI)

Telemetry says *they switched after 24 minutes*; it does not say *why*
([research-framework.md](../research-framework.md)). The coding pipeline is how raw human language —
a mentor's note, an interview quote, a checkpoint free-text — becomes a structured, traceable input
to synthesis **without an LLM silently converting a comment into a fact along the way.**

> The one rule that governs this entire document: **an LLM label is a HYPOTHESIS, not truth.** The
> raw text is kept beside every extracted label, the label carries its `model_version`, and a human
> gate stands between every AI suggestion and anything a client ever sees
> ([research-data-model.md](../research-data-model.md), provenance rules 3 + 5).

## XXV — The pipeline, with provenance at every step

```
RawQuote ─► Observation ─► Code ─► Subtheme ─► Theme ─► Pattern
   │                                                      │
   │                                                      ▼
   └──────────── provenance points BACK at every arrow ──► PossibleExplanation
                 (derived → raw, one-directional,              │
                  model_version on every derived node)         ▼
                                                       CompetingExplanation
                                                              │
                                                              ▼
                           Finding ◄── (promotion gate: evidence-graph.md) ◄── Claim
                              │
                              ▼
                     DecisionImplication ─► Recommendation (rests on a Finding/Claim, never free)
```

Each arrow is one-directional: a derived node points back at the raw it rests on and never the
reverse, so you can always walk **down** from a Recommendation to the exact quote — and never
fabricate **up** from a quote to a conclusion the evidence does not carry. A `Recommendation` with
no `finding_id` and no `claim_id` is structurally rejected
([`evidence_graph.py`](../../engine/evidence_graph.py) `Recommendation.__post_init__`).

## XXVI — The code layer (where the pipeline meets the schema)

`theme` and `theme_assignment` already live in `001_core.sql`. The **code layer sits underneath
them** — finer-grained than a theme, anchored to exactly one raw unit. In
[`006_live_research.sql`](../../schema/006_live_research.sql):

```
code                 codebook_version · label (e.g. friction:auth_setup:docs_missing)
                     · subtheme · theme_id → theme (a HYPOTHESIS, not truth) · definition

coding_assignment    code_id → code
                     · EXACTLY ONE raw anchor: qual_id | excerpt_id | observation_id
                       (CHECK num_nonnulls(...) = 1 — a code is always pinned to one raw unit)
                     · model_version_id → model_version   (set iff AI produced the first pass)
                     · human_review_state  UNREVIEWED | CONFIRMED | REJECTED | EDITED
                     · confidence [0,1]
```

A `code` rolls up to a `subtheme`, a subtheme to a `theme`, and a theme is itself a **hypothesis**
that a set of observations hang together — not a proven claim. The worked example from
[research-framework.md](../research-framework.md) in pipeline terms:

```
RawQuote      "I couldn't figure out how auth worked"        (interview_excerpt, immutable)
Observation   participant stuck on auth at onboarding         (observation, occurred_at set)
Code          friction:auth_setup:docs_missing                (coding_assignment, anchored to excerpt)
Subtheme      onboarding-auth friction
Theme         "auth setup is a retention risk"                (HYPOTHESIS — not yet a finding)
```

The excerpt is never overwritten by the code; both persist, joined. That is what lets a reviewer —
or a skeptical client — read the label back against the actual words.

## Where AI genuinely helps

AI earns its place as a **first-pass accelerator over hundreds of open responses**, every output of
which is a suggestion awaiting a human gate:

```
transcription of recorded interviews (with consent)   · first-pass coding (label suggestions)
theme suggestions / clustering of friction comments   · contradiction detection across notes
linking a quote to the behavioral event it explains   · summarizing a team's trajectory
identifying missing evidence (what a claim still lacks)· suggesting the next follow-up question
```

Each of these is a *proposal*. The AI's value is consistency and recall across volume — it reads
every comment the same way and never tires — not authority.

## Where AI must NOT go (default-prohibited, permanently)

```
invent a statement nobody made            · infer hidden personality or intent
score a person (quality/employability/...) · infer a protected trait
convert speculation into a stated fact      · erase or down-weight contradictory evidence
```

This is the same no-go spine as the master doc ([live-research-os.md](live-research-os.md)) and
Invariant 5 of the schema: **no person score, no protected-trait inference, anywhere.** An AI that
proposes a personality read, a founder score, or a protected-trait inference is not producing a
low-confidence hypothesis to be reviewed — it is producing output the pipeline refuses to store at
all. And an AI that drops the one quote contradicting the emerging theme has not summarized; it has
laundered, which is exactly what the contradictory-evidence requirement
([evidence-graph.md](evidence-graph.md)) exists to prevent.

## The human-review gate

Every `coding_assignment` produced or touched by a model carries `human_review_state`, and nothing
reaches a Finding while still `UNREVIEWED`:

```
 UNREVIEWED ──► CONFIRMED   human agrees with the AI label as-is
     │      ──► EDITED      human keeps the anchor, rewrites the label (model_version still recorded)
     │      ──► REJECTED    label was wrong; the raw unit stays, the code is removed
     ▼
 (an UNREVIEWED AI code is a proposal only — it cannot back a client-facing claim)
```

`REJECTED` never deletes the raw unit — the quote is immutable evidence regardless of whether a
proposed code survived. `EDITED` preserves the `model_version_id` so the provenance records *that* an
AI first pass happened and *that* a human changed it. The reviewer must be a `trained_codebook_version`
holder (the `researcher.trained_codebook_version` gate), so a code is only as valid as the codebook
version it was assigned under.

## ThemeFrequency is not a Finding (top complaints ≠ top problems)

The single most common analytic error this pipeline is built to block:

```
 ThemeFrequency (DESCRIPTIVE, L1)        "auth was the #1 mentioned friction (47 comments)"
      is a COUNT of a descriptive theme. It is true, cheap, and says NOTHING about outcomes.

 Finding (TESTED, L2+)                   "auth friction is associated with early abandonment
      requires that a theme PREDICTS an    among first-time users" — a claim that survived the
      outcome, survived a negative-case     promotion gate (evidence-graph.md can_promote)
      search, and enumerated contradictory
      evidence.
```

> **Top complaints are not top problems.** The loudest theme is often the most *articulable* one, not
> the most *consequential* one; the friction that actually killed retention may be the one nobody
> bothered to comment on because they quietly left. A `ThemeFrequency` is a descriptive L1 object and
> is reported as such. Promoting it to "this is what's hurting you" is a different, higher-bar object
> — a Finding — and it must go through the evidence graph's gate, not the frequency table.

This is why the pipeline deliberately separates **Theme** (a hypothesis that observations cluster)
from **Pattern** (a recurring structure across teams/trajectories) from **Finding** (a tested,
disconfirmation-searched claim). Frequency lives at the Theme layer; causation-flavored language
lives only past the gate.

## How this feeds the rest of the system

- Coded units become citable **evidence** on a claim — supporting *or* contradictory
  ([evidence-graph.md](evidence-graph.md)).
- An emerging theme that is still unstable is written up as an [analytic-memos.md](analytic-memos.md)
  entry (which *requires* a contradictory-evidence field), not as a finding.
- A theme that a trajectory's failed path illuminates is linked straight back to the
  [team-trajectories.md](team-trajectories.md) node that produced the raw quote.

The pipeline's job is to move language up the ladder of abstraction **while keeping every rung
pinned to the rung below it** — so that at the top, a client-facing recommendation can still be
walked all the way back down to the exact words a builder actually said.
