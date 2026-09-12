"""
Critical-path analysis (docs/team-rescue/contribution-and-roles.md, Part XIV).

Teams do NOT enter giant Gantt charts. From a handful of lightweight tasks (duration estimate,
dependencies, owner capability, status) this computes the project's critical path and answers the
one operationally useful question:

    "What must finish next to unblock the most downstream work?"

so bottleneck-first mentoring (Part XV) can route help to the task that frees the most future work,
not merely the easiest question. Pure stdlib; the schema is team_task / task_dependency in
schema/008_team_rescue.sql.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    task_id: str
    duration_min: int
    deps: tuple = ()            # prerequisite task_ids
    owner_capability: str = ""
    status: str = "TODO"        # TODO | DOING | DONE | BLOCKED


def _toposort(tasks: dict):
    """Return task_ids in dependency order; raise on a cycle (tasks must form a DAG)."""
    order, temp, perm = [], set(), set()

    def visit(tid):
        if tid in perm:
            return
        if tid in temp:
            raise ValueError(f"dependency cycle through {tid}")
        temp.add(tid)
        for d in tasks[tid].deps:
            if d in tasks:
                visit(d)
        temp.discard(tid); perm.add(tid); order.append(tid)

    for tid in tasks:
        visit(tid)
    return order


def critical_path(task_list):
    """Longest-duration path through the DAG (by estimated minutes). Returns (path, total_minutes).
    This is the chain that determines the minimum time to finish the project."""
    tasks = {t.task_id: t for t in task_list}
    if not tasks:
        return [], 0
    order = _toposort(tasks)
    best_len = {tid: 0 for tid in tasks}     # longest path ENDING at tid
    best_prev = {tid: None for tid in tasks}
    for tid in order:
        t = tasks[tid]
        dep_best = 0; prev = None
        for d in t.deps:
            if d in tasks and best_len[d] > dep_best:
                dep_best = best_len[d]; prev = d
        best_len[tid] = dep_best + t.duration_min
        best_prev[tid] = prev
    end = max(best_len, key=lambda k: best_len[k])
    path = []
    cur = end
    while cur is not None:
        path.append(cur); cur = best_prev[cur]
    path.reverse()
    return path, best_len[end]


def next_to_unblock(task_list):
    """The earliest UNFINISHED task on the critical path — the one whose completion unblocks the
    most downstream work. Returns the task_id, or None if the critical path is done."""
    path, _ = critical_path(task_list)
    tasks = {t.task_id: t for t in task_list}
    for tid in path:
        if tasks[tid].status not in ("DONE",):
            return tid
    return None


def bottleneck_capability(task_list):
    """Which owner capability sits on the most critical-path minutes — where expert help would most
    move the project. Returns (capability, critical_minutes) or (None, 0)."""
    path, _ = critical_path(task_list)
    tasks = {t.task_id: t for t in task_list}
    by_cap = {}
    for tid in path:
        cap = tasks[tid].owner_capability or "unassigned"
        by_cap[cap] = by_cap.get(cap, 0) + tasks[tid].duration_min
    if not by_cap:
        return None, 0
    cap = max(by_cap, key=lambda k: by_cap[k])
    return cap, by_cap[cap]
