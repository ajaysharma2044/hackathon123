# Temporal resource allocation

`engine/dynamic_allocation.py`. Participant minutes are the scarcest, most perishable resource.

**Minute ledgers (XXXIX).** `make_ledgers(...)` returns four. The **participant** ledger *is*
`burden_budget.BurdenBudget` — the real research-burden floor (channels + rate governor), reused so
temporal allocation cannot silently breach the experience floor. The three **supply pools** (mentor,
researcher, engineer) are `MinuteLedger`s that **raise** when over capacity rather than clamping. The
participant ledger is deliberately *not* an ordinary pool — its floor is structurally distinct.

**Interruption cost (XL).** A 20-minute workshop can cost more than 20 minutes because it breaks flow.
`interruption_cost(direct, recovery)` returns `direct + recovery`, but recovery is **UNKNOWN until
measured** — when absent it says so rather than assuming zero (which would undercount).

**Time-budget packing (XLII):** `time_budget_pack(modules, capacity)` respects team-hours /
attention-minutes / mentor-hours caps. **Reallocation (XLVI):** `reallocation_schedule` moves support
across phases (morning team-formation → mid technical specialists → late deploy/demo) — resources move,
they are not parked for visibility. **Critical path (XLIV):** `critical_path(tasks)` finds the
dependency chain whose slip slips everything downstream.
