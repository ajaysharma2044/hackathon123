# Mentor Interventions — The Support-Success Confounder

This is **Part VIII** of the [live research OS](live-research-os.md): the honest treatment of what
happens to a research signal when a mentor — especially a sponsor's own engineer — does the hard
part for a team. The mentor *system* (taxonomy, routing, the 20-second log, the mentor experience)
is in [mentor-system.md](mentor-system.md). This doc is narrower and sharper: **a success that
happened only after heavy expert help is not the same thing as a product succeeding on its own, and
we must never report them as if they were.**

> **The trap, stated once.** A sponsor engineer sits with a team for 40 minutes, writes the tricky
> integration, and the team ships on the sponsor's product. If that team is counted in "teams that
> succeeded with Product X", the number is a lie of omission. The team succeeded; the *product* did
> not demonstrate that it works unaided. We fix this by **labeling**, not by discarding the team and
> not by estimating a causal effect we cannot support at this n.

## Evidence ≠ Claim — and why rescue is the textbook confounder

The vendor engineer is correlated with both the treatment (heavy use of their product) and the
outcome (the team shipping on it). That is the definition of a confounder. At n=200, split into
arms of ~60 ([measurement.md](../measurement.md)), we cannot isolate its effect — we can only detect
large differences, and the rescue signal is exactly the kind of thing that would masquerade as a
large product effect. So the discipline is:

```
EVIDENCE      a team shipped on Product X ; a company engineer logged a HEAVY interaction on it
CLAIM         (under construction) "teams adopt Product X and ship with it"
FORBIDDEN     "Product X caused the team to succeed"   ← we never write this from a rescued case
ALLOWED       "of teams that shipped on X, k did so ORGANIC, j after VENDOR_RESCUED heavy help"
```

We refuse to collapse the last line into the middle one. Stratification is not causal inference.

## What we track per interaction

Recorded on `mentor_interaction` (schema [`006_live_research.sql`](../../schema/006_live_research.sql))
and carried into the evidence graph through `claim_evidence.mentor_interaction_id`:

| Field | Column | Why it matters to the confounder |
|---|---|---|
| MentorType | `mentor.category` | is this domain help or product help? |
| MentorAffiliation | `mentor.affiliation` / `is_company_engineer` | **the confounder flag** |
| InterventionType | `intervention` | advice vs the mentor writing the code |
| Duration | `duration_min` | an input to the operational intensity |
| Intensity | `intensity` (`mentor_intensity` enum) | NONE / LIGHT / MODERATE / HEAVY |
| Problem | `problem` / `category` | what was being rescued |
| Outcome | `outcome` | where the team ended up |

`MentorAffiliation` is the load-bearing field. A `MODERATE`/`HEAVY` interaction from a neutral domain
expert and the same intensity from a sponsor engineer on their own product are categorically
different for reporting, and the `is_company_engineer` flag is what separates them.

## The operational intensity definition (not subjective)

Intensity is computed, not felt. `support_intensity(duration_min, num_touches, solved_by_mentor)`
([`mentor_routing.py`](../../engine/mentor_routing.py)) is the single source of truth; the mentor
never self-rates "how much did I help". The exact logic:

```
NONE      num_touches == 0                                        no mentor touch at all
LIGHT     num_touches == 1  AND  duration_min < 10  AND  not solved_by_mentor
          └─ a single short touch; the team still drove
HEAVY     solved_by_mentor  AND  (duration_min >= 20  OR  num_touches >= 3)
          └─ long and/or many touches AND the mentor effectively did the hard part
MODERATE  everything else                                         repeated/longer, team still drove
```

The decisive term is `solved_by_mentor`. `HEAVY` does not mean "a lot of help" — it means the mentor
**resolved the blocker for them**, at length or over many touches. A mentor can spend an hour
Socratically and still be `MODERATE` if the team wrote every line. That distinction is the whole
point: `HEAVY` is where "did the product work?" becomes unanswerable from this team alone.

## The success labels

`classify_success(outcome, intensity, is_company_engineer)` produces a `SuccessLabel`
([`mentor_routing.py`](../../engine/mentor_routing.py)). Three labels, one rule each:

```
ORGANIC_SUCCESS          intensity ∈ {NONE, LIGHT}
                         └─ the team succeeded with little or no mentor help
VENDOR_RESCUED_SUCCESS   is_company_engineer AND intensity ∈ {MODERATE, HEAVY}
                         └─ a sponsor engineer materially carried a team onto their own product
ASSISTED_SUCCESS         everything else (neutral expert, MODERATE/HEAVY)
                         └─ real help, but not the vendor's own engineer on their own product
```

`vendor_assisted = is_company_engineer AND intensity ∈ {MODERATE, HEAVY}`. The precedence is
deliberate: a `NONE`/`LIGHT` touch is `ORGANIC` *even from a company engineer* — a two-minute pointer
does not rescue anyone. Vendor rescue requires both the affiliation **and** real intensity.

```
                 intensity:  NONE/LIGHT        MODERATE/HEAVY
 neutral mentor            ORGANIC_SUCCESS     ASSISTED_SUCCESS
 company engineer          ORGANIC_SUCCESS     VENDOR_RESCUED_SUCCESS   ← the confounder cell
```

### The non-causal caveat rides with every label

Every `SuccessLabel` carries a `caveat` field, populated verbatim by `classify_success`:

> `"stratification only; not a causal estimate of the help's effect"`

This is not documentation — it is a field on the data structure, so the caveat physically travels
with the label into any memo, claim, or client view. A label that arrives without its caveat is a
bug. This mirrors the evidence-graph invariant that a claim must enumerate both supporting and
contradictory evidence before promotion ([live-research-os.md](live-research-os.md), Invariant 2):
the honesty is structural, not a matter of remembering to add a footnote.

## What the labels enable — stratification, not an effect estimate

The analysis they unlock is a **comparison of strata**, reported as such:

```
  "Of N teams that shipped on Product X:
     k  ORGANIC_SUCCESS         (succeeded with no/light help)
     j  ASSISTED_SUCCESS        (neutral expert did material work)
     m  VENDOR_RESCUED_SUCCESS  (sponsor engineer did the hard part on their own product)"
```

A client reading this learns something real and actionable: if `k` is large, the product stands on
its own for elite builders; if `m` dominates, the product needs a human in the loop to succeed in a
weekend — a precise, honest diagnosis ([measurement.md](../measurement.md), "precise friction
diagnosis"). What the client does **not** get is "the help caused X% more success", because:

- the mentor-touched and untouched teams are not exchangeable (teams self-select into asking);
- the vendor engineer is correlated with both exposure and outcome;
- at ~60 per arm, only ~20–25pp differences are detectable anyway.

So we stop at the stratified counts, state the limits plainly, and refuse the effect estimate. All
cells are min-cell-suppressed before a client sees them (`ClientView` in
[`live_research.py`](../../engine/live_research.py)); the confounder cell is never unblinded to a
sponsor as individual teams.

## The analytic habit

- A `VENDOR_RESCUED_SUCCESS` team is a **negative case waiting to happen** for any "product X works
  unaided" claim — it is exactly the counterexample [negative-case analysis](negative-case-analysis.md)
  goes looking for. Feed it there.
- `research_flag` on the interaction ([mentor-system.md](mentor-system.md)) is how a mentor hands the
  war room a rescue worth a closer look, without the mentor doing any analysis.
- The label belongs to the team's story as a labeled, hedged episode on its
  [trajectory](team-trajectories.md) (`decision_episode.mentor_interaction_id`), never as an unhedged
  "they loved the product".
- Upstream: whether the rescue pattern should change the event itself (more/fewer company engineers,
  different office-hours structure) is an `event_intervention` with a `CONFOUNDING` validity impact —
  it changes something a study measures, so before/after must be split
  ([`006_live_research.sql`](../../schema/006_live_research.sql)).

The one-line test for this doc: **can a sponsor be told, honestly, "your product was rescued onto m
of these teams by your own engineers" — and will the system refuse to let that m be quietly folded
into the adoption number?** If yes, the confounder is handled.
