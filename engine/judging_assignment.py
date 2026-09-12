"""
Judging assignment + scoring (docs/event-ops/judging-system.md).

Implements the science-fair judging model used by MLH and most elite hackathons:

  1. HOW MANY JUDGES  — J = ceil(P * rounds * minutes / window). Each project is visited `rounds`
     times by different judges; `minutes` is demo + Q + travel; `window` is the judging block.
  2. THE ROTATION     — assign judges to submissions so every submission is seen exactly `rounds`
     times, no judge is overloaded, and no judge evaluates a submission they are CONFLICTED on
     (their own team, or — for a neutral grand-prize round — their own sponsor).
  3. THE SCORE        — stack ranking, not absolute scores: within each judge's batch, rank the
     top projects and map rank→points (3/2/1). This normalizes strict vs lenient judges, which
     raw 1–10 scores do not. Aggregate points across judges to rank the field.

Sponsor/category prizes are judged by subject-matter judges over only the submissions tagged for
that category — a separate round, so a sponsor judge never decides the neutral grand prize.

Pure stdlib. A reference scheduler + aggregator; the schema is judging_* in schema/007_event_ops.sql.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import ceil
from collections import defaultdict


def judges_needed(n_projects, rounds=3, minutes=4, window_min=120):
    return 0 if n_projects <= 0 else ceil(n_projects * rounds * minutes / window_min)


@dataclass
class Submission:
    submission_id: str
    team_id: str
    category_tags: frozenset = frozenset()


@dataclass
class Judge:
    judge_id: str
    expertise: frozenset = frozenset()
    conflict_team_ids: frozenset = frozenset()   # teams they mentored / are affiliated with
    is_sponsor_judge: bool = False


def _conflicted(judge: Judge, sub: Submission) -> bool:
    return sub.team_id in judge.conflict_team_ids


def assign_science_fair(submissions, judges, rounds=3):
    """Round-robin assign so each submission is seen `rounds` times by distinct, non-conflicted
    judges, balancing load across judges. Returns {submission_id: [judge_id, ...]} and raises if
    coverage is impossible (too few eligible judges for some submission)."""
    if not judges:
        raise ValueError("no judges")
    load = {j.judge_id: 0 for j in judges}
    result = {s.submission_id: [] for s in submissions}
    # Hardest-to-cover submissions first (most conflicts) so we don't paint ourselves into a corner.
    order = sorted(submissions,
                   key=lambda s: sum(1 for j in judges if not _conflicted(j, s)))
    for s in order:
        eligible = [j for j in judges if not _conflicted(j, s)]
        if len(eligible) < rounds:
            raise ValueError(
                f"submission {s.submission_id}: only {len(eligible)} non-conflicted judges for "
                f"{rounds} rounds — recruit more neutral judges or reduce rounds")
        # pick the `rounds` least-loaded eligible judges (stable, balanced)
        picks = sorted(eligible, key=lambda j: (load[j.judge_id], j.judge_id))[:rounds]
        for j in picks:
            result[s.submission_id].append(j.judge_id)
            load[j.judge_id] += 1
    return result


def assign_category(submissions, judges, category, rounds=2):
    """A sponsor/category round: only submissions tagged `category`, judged by judges whose
    expertise covers it (sponsor judges allowed here — this is their prize, not the grand prize)."""
    subs = [s for s in submissions if category in s.category_tags]
    panel = [j for j in judges if category in j.expertise]
    if not subs:
        return {}
    if not panel:
        raise ValueError(f"no judges with expertise in '{category}'")
    return assign_science_fair(subs, panel, rounds=min(rounds, len(panel)))


# --- stack-rank scoring -------------------------------------------------------------------------
RANK_POINTS = {1: 3, 2: 2, 3: 1}   # MLH default: top-3 get 3/2/1; the rest get 0


def stack_rank_batch(ranked_submission_ids):
    """A judge hands back their batch ranked best→worst. Map the top 3 to 3/2/1 points."""
    return {sid: RANK_POINTS.get(i + 1, 0) for i, sid in enumerate(ranked_submission_ids)}


def aggregate(batches):
    """Sum stack-rank points across all judges' batches. `batches` is a list of {sid: points}.
    Returns submissions sorted best→worst by total points (ties broken by id for determinism)."""
    totals = defaultdict(int)
    for b in batches:
        for sid, pts in b.items():
            totals[sid] += pts
    return sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
