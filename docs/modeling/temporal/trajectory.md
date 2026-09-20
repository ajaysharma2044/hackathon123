# Trajectories — snapshots become paths

`engine/trajectory.py`. A trajectory is `τ_i = (S0, A0, S1, A1, …, ST)`. Two teams that look different
at the end may have had similar journeys; `similarity()` compares state paths (normalised Levenshtein).

`classify_archetype(τ)` labels the **project's shape** — FAST_STRAIGHT_LINE,
EARLY_FAILURE_SUCCESSFUL_PIVOT, LATE_COLLAPSE, MENTOR_DEPENDENT_RECOVERY, SLOW_START_RAPID_FINISH,
RD_EXPLORER, OVERSCOPED_CUT_SHIP. **These describe the project's path, never the people** — every result
carries `ARCHETYPE_DISCLAIMER`. They are operational shapes, not personality categories.

**Domain trajectories** are ordered stage templates with timestamps (`stage_timestamps`), missing
stages valid:

- **Learning (XXX):** PriorExperience → FirstExposure → FirstAttempt → Failure → LearningResource →
  SuccessfulApplication → Integration → Continuation
- **Venture (XXXVI):** Idea → Prototype → Demo → Continued → Users → Revenue → Pivot → Stopped → Startup
- **R&D (XXXVII):** Hypothesis → Experiment → Failure → Revision → SecondExperiment → Convergence → Prototype
- **Product (XXXVIII):** Aware → Considered → Tried → Activated → Integrated → Failed → ReceivedHelp →
  Switched → Retained

A learning/capability trajectory is **artifact-anchored evidence a participant may choose to share — it
is NEVER an intelligence, IQ, or general-ability score** (`NO_PERSON_SCORE`). This is what makes
trajectory-based hiring/venture evidence (Parts XXXV–VI) richer than an endpoint label *without*
becoming a hidden "potential" score.
