"""
The event staffing model (docs/event-ops/org-chart-and-roles.md, event1-staffing.md).

Given an event size, compute the full staffing plan across BOTH orgs — organizers, crew, mentors,
judges, volunteers, and the research staff — with the ratios each count is derived from, and flag
any under-staffing. The ratios are grounded in the researched comps
(docs/event-ops/prior-hackathons.md); they are defensible defaults, not laws, and every number
reports the rule it came from so a human can override it with reasons.

Sourced anchors:
  * Judges: J = ceil(P * rounds * minutes / window)  — MLH science-fair formula (n=3, t=4, T=120).
  * Mentors: elite density ~1 per 10 builders (event1-design.md); mixed model.
  * Field researchers: ~1 per ~25–30 participants for primary coverage (research-ops/event1-staffing.md).
  * Volunteers: day-of shift help ~1 per ~20 participants, higher at check-in/meal peaks.
  * Organizer committee: a fixed set of unit heads (does not scale linearly with size).

Pure stdlib. A planning calculator, not a roster — it sizes the org and surfaces the thin spots.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil

# The organizer committee heads — roughly fixed regardless of size (they scale by adding crew/leads).
COMMITTEE_UNITS = (
    "EXECUTIVE", "LOGISTICS", "FINANCE_SPONSORSHIP", "MARKETING", "OPERATIONS", "TECH_AV",
    "DESIGN", "PARTICIPANT_EXPERIENCE", "JUDGING_AWARDS", "MENTORSHIP", "SAFETY", "RESEARCH",
)

# Default ratios (people : participants), and the source each comes from.
DEFAULTS = {
    "mentor_ratio": 10,            # 1 mentor per 10 builders (elite density, event1-design.md)
    "field_researcher_ratio": 28, # 1 per ~25–30 (research-ops/event1-staffing.md)
    "volunteer_ratio": 20,        # 1 day-of volunteer per ~20 (hackathon.guide shift model)
    "crew_ratio": 40,             # paid domain crew (AV/F&B/logistics execution) per ~40
    "team_size": 4,               # 2–5 typical; 4 is the planning midpoint
    "judge_rounds": 3,            # MLH n
    "judge_minutes": 4,           # MLH t (2 demo + 1 Q + 1 travel)
    "judge_window_min": 120,      # MLH T (a 2-hour science-fair window)
}


def judges_needed(n_projects: int, rounds: int = 3, minutes: int = 4, window_min: int = 120) -> int:
    """MLH science-fair formula J = ceil(P * rounds * minutes / window). Each project is seen
    `rounds` times; `minutes` covers demo + Q + travel; `window_min` is the judging block."""
    if n_projects <= 0:
        return 0
    return ceil(n_projects * rounds * minutes / window_min)


@dataclass
class Line:
    role: str
    count: int
    basis: str            # the rule the count came from


@dataclass
class StaffingPlan:
    participants: int
    teams: int
    lines: list           # list[Line]
    warnings: list        # list[str]

    def total(self) -> int:
        return sum(l.count for l in self.lines)

    def by_role(self) -> dict:
        return {l.role: l.count for l in self.lines}


def plan(participants: int, cfg: dict = None) -> StaffingPlan:
    """Build the full cross-org staffing plan for `participants` builders."""
    c = dict(DEFAULTS, **(cfg or {}))
    teams = ceil(participants / c["team_size"])
    lines, warn = [], []

    # Organizer committee — fixed heads, plus a deputy once the event is large.
    heads = len(COMMITTEE_UNITS)
    deputies = 0 if participants <= 120 else (len(COMMITTEE_UNITS) // 2)
    lines.append(Line("Organizer committee heads", heads, f"one head per unit ({heads} units)"))
    if deputies:
        lines.append(Line("Committee deputies", deputies, "added above ~120 participants"))

    # Mentors, judges, volunteers, crew — ratio / formula driven.
    mentors = ceil(participants / c["mentor_ratio"])
    lines.append(Line("Mentors", mentors, f"1 per {c['mentor_ratio']} builders (elite density)"))

    j = judges_needed(teams, c["judge_rounds"], c["judge_minutes"], c["judge_window_min"])
    lines.append(Line("Judges (science-fair)", j,
                      f"ceil({teams} teams × {c['judge_rounds']} × {c['judge_minutes']}min / {c['judge_window_min']}min)"))

    vols = ceil(participants / c["volunteer_ratio"])
    lines.append(Line("Volunteers (day-of)", vols, f"1 per {c['volunteer_ratio']} (peaks need more at once)"))

    crew = ceil(participants / c["crew_ratio"])
    lines.append(Line("Paid crew (AV/F&B/logistics)", crew, f"1 per {c['crew_ratio']}"))

    # Research staff — the live-research org (research-ops/event1-staffing.md).
    field = ceil(participants / c["field_researcher_ratio"])
    lines.append(Line("Field researchers", field, f"1 per {c['field_researcher_ratio']} (primary coverage)"))
    lines.append(Line("Research leads/interviewers/analysts", max(3, ceil(field / 2) + 2),
                      "leads+interviewers+analysts scale with field count"))
    lines.append(Line("Data steward", 1, "exactly one, conflict-free (never scales, never shared)"))

    # --- under-staffing checks ---------------------------------------------------------------
    if mentors < teams / 3:
        warn.append(f"mentors ({mentors}) thin vs {teams} teams: expect long help-queue waits "
                    f"(mentor-system.md) — raise density or add office hours")
    if j < 3:
        warn.append("fewer than 3 judges cannot support 3-round stack-ranking; add judges or shrink rounds")
    if field < 2:
        warn.append("a single field researcher cannot hold coverage + synthesis — minimum 2")
    if participants > 200:
        warn.append("above ~200 the bear case bites: ops + parallel research is not a small team "
                    "(STATE.md) — costs and coordination rise super-linearly")
    return StaffingPlan(participants, teams, lines, warn)
