"""Tests for the adaptive question engine: branching is correct, bounded, and auditable.
`python3 engine/test_adaptive_questions.py`."""
from adaptive_questions import (TECHNOLOGY_CHOICE, RD_FAILURE, PRODUCT_DEV, ACTIVATION, TREES,
                                MICRO_PROMPTS)

PASS, FAIL = 0, 0
def check(name, cond):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  PASS  {name}")
    else:    FAIL += 1; print(f"  FAIL  {name}")


def test_branch_follows_answers():
    # A switch caused by setup→documentation must reach the docs-detail question.
    ans = {"tc_expectation": "yes", "tc_switch_consider": "yes", "tc_switch_cause": "setup_friction",
           "tc_friction_part": "documentation"}
    r = TECHNOLOGY_CHOICE.walk(ans)
    check("docs-friction path reaches the doc-detail probe", "tc_doc_detail" in r["path"])
    # A switch caused by cost must NOT reach the docs probe.
    ans2 = {"tc_expectation": "yes", "tc_switch_consider": "yes", "tc_switch_cause": "setup_friction",
            "tc_friction_part": "cost"}
    r2 = TECHNOLOGY_CHOICE.walk(ans2)
    check("cost-friction path skips the doc-detail probe", "tc_doc_detail" not in r2["path"])


def test_default_branch_and_early_terminal():
    # No expectation gap → short path that ends at the counterfactual question.
    r = TECHNOLOGY_CHOICE.walk({"tc_expectation": "no"})
    check("no-gap path ends at the 'choose same again' question", r["path"][-1] == "tc_end")
    check("no-gap path is short (<=5 questions)", len(r["path"]) <= 5)


def test_known_vs_unknown_answer_uses_default():
    # An unmapped answer value falls through the '*' default edge, never crashes.
    r = TECHNOLOGY_CHOICE.walk({"tc_goal": "anything at all"})
    check("unmapped answer uses '*' default, reaches considered", "tc_considered" in r["path"])


def test_burden_is_bounded():
    r = TECHNOLOGY_CHOICE.walk({"tc_expectation": "yes", "tc_switch_consider": "yes",
                                "tc_switch_cause": "setup_friction", "tc_friction_part": "documentation"},
                               max_questions=3)
    check("walk stops at max_questions cap", len(r["path"]) == 3 and r["hit_cap"])
    full = TECHNOLOGY_CHOICE.walk({"tc_expectation": "no"})
    check("a completed walk reports no cap hit", full["hit_cap"] is False)
    check("burden is summed along the path", full["burden_sec"] > 0)


def test_activation_branches_on_prior_familiarity():
    prior = ACTIVATION.walk({"ac_known": "yes"})
    fresh = ACTIVATION.walk({"ac_known": "no"})
    check("prior users get the 'how much' credit branch", "ac_credit_use" in prior["path"])
    check("new users get the 'whether' credit branch", "ac_credit_consider" in fresh["path"])


def test_trees_and_prompts_registered():
    check("all four modules registered", set(TREES) == {"technology_choice", "rd_failure", "product_dev", "activation"})
    check("rd_failure asks the failed-assumption question", "rd_assumption" in RD_FAILURE.nodes)
    check("product_dev asks about workarounds", "pd_workaround" in PRODUCT_DEV.nodes)
    check("micro-prompts exist for switch and credit", "switch_reason" in MICRO_PROMPTS and "credit_effect" in MICRO_PROMPTS)
    check("micro-prompts are short single lines", all("\n" not in p and len(p) < 80 for p in MICRO_PROMPTS.values()))


if __name__ == "__main__":
    for t in [test_branch_follows_answers, test_default_branch_and_early_terminal,
              test_known_vs_unknown_answer_uses_default, test_burden_is_bounded,
              test_activation_branches_on_prior_familiarity, test_trees_and_prompts_registered]:
        print(f"\n{t.__name__}"); t()
    print(f"\n{'='*50}\n{PASS} passed, {FAIL} failed")
    import sys; sys.exit(1 if FAIL else 0)
