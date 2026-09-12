"""Tests for the critical-incident trigger engine: routing, defaults, high-value set.
`python3 engine/test_research_triggers.py`."""
from research_triggers import (TriggerRegistry, TRIGGERS, FIRE_PROMPT, MENTOR_NOTE_SUFFICIENT,
                               FLAG_FOR_INTERVIEW, OBSERVE_ONLY)

PASS, FAIL = 0, 0
def check(name, cond):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  PASS  {name}")
    else:    FAIL += 1; print(f"  FAIL  {name}")

R = TriggerRegistry()


def test_switch_fires_a_prompt():
    t = R.route("SWITCH")
    check("SWITCH fires a micro-prompt", t.action == FIRE_PROMPT)
    check("SWITCH routes to the switch-reason prompt", t.prompt_key == "switch_reason")
    check("SWITCH costs the participant a small, bounded burden", 0 < t.burden_sec <= 30)


def test_help_request_does_not_burden_participant():
    t = R.route("HELP_REQUEST")
    check("a single help request is covered by the mentor note, not a prompt",
          t.action == MENTOR_NOTE_SUFFICIENT and t.burden_sec == 0)
    rep = R.route("REPEATED_HELP_REQUEST")
    check("repeated help escalates to a deeper interview flag", rep.action == FLAG_FOR_INTERVIEW)


def test_unknown_trigger_is_observed_not_asked():
    t = R.route("SOMETHING_WE_NEVER_DEFINED")
    check("unknown trigger never improvises a prompt", t.action == OBSERVE_ONLY and t.burden_sec == 0)


def test_most_triggers_do_not_ask():
    # The default must be silence: fewer than half of all triggers fire a participant prompt.
    asking = [t for t in TRIGGERS.values() if t.action == FIRE_PROMPT]
    check("fewer than half of triggers fire a participant prompt", len(asking) < len(TRIGGERS) / 2)


def test_high_value_ask_set():
    hv = {t.trigger_type for t in R.high_value_asks()}
    check("SWITCH is in the high-value ask set", "SWITCH" in hv)
    check("UNEXPECTED_USE_CASE is in the high-value ask set", "UNEXPECTED_USE_CASE" in hv)
    check("PROTOTYPE_COMPLETION (low value) is not", "PROTOTYPE_COMPLETION" not in hv)


def test_credit_triggers_exist():
    check("CREDIT_USE asks whether the incentive changed the choice", R.route("CREDIT_USE").action == FIRE_PROMPT)
    check("CREDIT_IGNORE is captured too", "CREDIT_IGNORE" in TRIGGERS)


if __name__ == "__main__":
    for t in [test_switch_fires_a_prompt, test_help_request_does_not_burden_participant,
              test_unknown_trigger_is_observed_not_asked, test_most_triggers_do_not_ask,
              test_high_value_ask_set, test_credit_triggers_exist]:
        print(f"\n{t.__name__}"); t()
    print(f"\n{'='*50}\n{PASS} passed, {FAIL} failed")
    import sys; sys.exit(1 if FAIL else 0)
