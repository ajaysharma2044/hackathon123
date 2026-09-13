"""
The participant burden budget (docs/research-ops/participant-burden.md).

Participant attention is the scarce resource that keeps the event excellent. Every explicit research
touch is a debit against a per-participant budget, and a prompt-rate governor keeps a builder in deep
flow from being pinged. The budget is the mechanism that makes "capture as much as possible" safe:
the system spends the budget on the highest-signal moments and stays silent otherwise.

Defaults (tunable, see the doc for the reasoning):
  * EXPLICIT_CAP_SEC = 18 min of EXPLICIT research per participant across the whole event.
  * Artifact submission and the ambient mentor-log impact are NOT counted as explicit burden —
    they are things the builder did anyway.
  * MIN_PROMPT_GAP_SEC: no two micro-prompts to the same participant closer than this.

A refused spend is correct behavior, not an error to route around: the absence of a prompt is the
system protecting the golden goose.
"""
from __future__ import annotations
from datetime import datetime, timedelta

EXPLICIT_CAP_SEC = 18 * 60          # ~18 explicit research-minutes per participant (event1-design.md)
MIN_PROMPT_GAP_SEC = 45 * 60        # at most ~one micro-prompt per 45 min per participant
# Channels that count toward the EXPLICIT cap. Ambient/byproduct channels are excluded on purpose.
EXPLICIT_CHANNELS = frozenset({"BASELINE", "CHECKPOINT", "MICRO_PROMPT", "INTERVIEW", "DIARY", "FOLLOWUP"})
AMBIENT_CHANNELS = frozenset({"APPLICATION", "MENTOR_LOG_IMPACT", "ARTIFACT_SUBMISSION"})
ALL_CHANNELS = EXPLICIT_CHANNELS | AMBIENT_CHANNELS


class BurdenExceeded(Exception):
    pass


class BurdenBudget:
    """Append-only ledger of research touches, with a spend gate."""

    def __init__(self, cap_sec: int = EXPLICIT_CAP_SEC, min_gap_sec: int = MIN_PROMPT_GAP_SEC):
        if type(cap_sec) is not int or cap_sec < 0 or min_gap_sec < 0:
            raise ValueError("burden limits must be nonnegative")
        self.cap_sec = cap_sec
        self.min_gap = timedelta(seconds=min_gap_sec)
        self._ledger: list = []        # (participant, channel, seconds, at)

    def _spent_explicit(self, participant: str) -> int:
        return sum(s for p, c, s, _ in self._ledger if p == participant and c in EXPLICIT_CHANNELS)

    def _last_prompt_at(self, participant: str):
        times = [at for p, c, _, at in self._ledger if p == participant and c == "MICRO_PROMPT"]
        return max(times) if times else None

    def can_spend(self, participant: str, channel: str, seconds: int, now: datetime) -> bool:
        """Would a spend of `seconds` on `channel` be allowed right now?"""
        if type(seconds) is not int or seconds < 0:
            raise ValueError("burden must be nonnegative integer seconds")
        assert channel in ALL_CHANNELS, f"unknown channel {channel}"
        if channel in AMBIENT_CHANNELS:
            return True                # ambient channels never consume the explicit budget
        if self._spent_explicit(participant) + seconds > self.cap_sec:
            return False               # would blow the explicit research-minutes cap
        if channel == "MICRO_PROMPT":
            last = self._last_prompt_at(participant)
            if last is not None and now - last < self.min_gap:
                return False           # rate governor: too soon since the last prompt
        return True

    def spend(self, participant: str, channel: str, seconds: int, now: datetime):
        """Debit the budget, or raise BurdenExceeded. Raising (not silently clamping) is deliberate:
        the caller must treat a full budget as a reason to stay silent."""
        if not self.can_spend(participant, channel, seconds, now):
            raise BurdenExceeded(
                f"{participant}: spending {seconds}s on {channel} would exceed the budget "
                f"(spent {self._spent_explicit(participant)}s / cap {self.cap_sec}s) or the prompt rate")
        self._ledger.append((participant, channel, seconds, now))

    def remaining(self, participant: str) -> int:
        return max(0, self.cap_sec - self._spent_explicit(participant))

    def is_over_half(self, participant: str) -> bool:
        """Sampling uses this to prefer lightly-burdened participants (we do not farm one person)."""
        return self._spent_explicit(participant) >= self.cap_sec // 2
