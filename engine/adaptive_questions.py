"""
The adaptive question engine (docs/research-ops/adaptive-questioning.md).

Questions branch on answers. A reusable question tree is a set of nodes plus labeled edges; given a
participant's answers, `walk` produces the PATH actually taken — so a switch caused by "docs" leads
to "what information were you looking for?", while a switch caused by "cost" does not.

Two disciplines are enforced here, not just documented:
  * Branching is explicit and auditable (each edge has a rationale); a '*' edge is the default.
  * Burden is bounded: `walk` stops at `max_questions` and sums the burden of the path, so a tree
    can never quietly turn into a 30-question survey.

No leading questions, no loaded assumptions: the prompts ask about concrete recent events and
specific decisions, never "why did <assumed cause> frustrate you?". Leading-question review is a
flag on each node (is_leading_audited) in the schema; here the node text reflects audited wording.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

MULTI_CHOICE, SHORT_TEXT, VOICE, SCALE, BRANCH_ONLY = (
    "MULTI_CHOICE", "SHORT_TEXT", "VOICE", "SCALE", "BRANCH_ONLY")


@dataclass
class Node:
    qid: str
    text: str
    answer_kind: str = SHORT_TEXT
    burden_sec: int = 15
    branches: dict = field(default_factory=dict)   # answer value (or '*') -> next qid (or None=terminal)

    def next_qid(self, answer: Optional[str]):
        """Resolve the edge for `answer`: exact match first, then the '*' default, else terminal."""
        if answer in self.branches:
            return self.branches[answer]
        if "*" in self.branches:
            return self.branches["*"]
        return None


@dataclass
class Tree:
    module: str
    root: str
    nodes: dict                      # qid -> Node
    version: int = 1

    def walk(self, answers: dict, max_questions: int = 8) -> dict:
        """Follow the branches dictated by `answers` from the root. Returns the ordered path of
        qids asked, the total burden, and whether it terminated cleanly or hit the cap."""
        path, burden, qid, seen = [], 0, self.root, set()
        while qid is not None and len(path) < max_questions:
            if qid in seen:                       # cycle guard — trees must be acyclic in practice
                break
            seen.add(qid)
            node = self.nodes[qid]
            path.append(qid)
            burden += node.burden_sec
            qid = node.next_qid(answers.get(qid))
        hit_cap = qid is not None                 # there was more, but we stopped to protect burden
        return {"path": path, "burden_sec": burden, "hit_cap": hit_cap}


def _n(qid, text, kind=SHORT_TEXT, b=15, **branches):
    return Node(qid, text, kind, b, dict(branches))


# ------------------------------------------------------------------------------------------------
# TECHNOLOGY CHOICE TREE — the commercial spine. Concrete, recent, specific; no leading assumptions.
# ------------------------------------------------------------------------------------------------
TECHNOLOGY_CHOICE = Tree("technology_choice", "tc_goal", {n.qid: n for n in [
    _n("tc_goal", "What were you trying to accomplish when you picked this?", SHORT_TEXT, 15, **{"*": "tc_considered"}),
    _n("tc_considered", "What did you consider?", MULTI_CHOICE, 15, **{"*": "tc_why_chosen"}),
    _n("tc_why_chosen", "What mattered most in choosing the one you did?", SHORT_TEXT, 20, **{"*": "tc_expectation"}),
    _n("tc_expectation", "After you started, did anything differ from what you expected?",
       MULTI_CHOICE, 15, no="tc_end", yes="tc_switch_consider"),
    _n("tc_switch_consider", "Did you consider switching?", MULTI_CHOICE, 10, no="tc_end", yes="tc_switch_cause"),
    _n("tc_switch_cause", "What specifically pushed you toward switching?", MULTI_CHOICE, 15,
       setup_friction="tc_friction_part", other="tc_end", **{"*": "tc_end"}),
    _n("tc_friction_part", "Which part of setup?", MULTI_CHOICE, 10,
       documentation="tc_doc_detail", authentication="tc_end", installation="tc_end",
       api_design="tc_end", debugging="tc_end", latency="tc_end", cost="tc_end", **{"*": "tc_end"}),
    _n("tc_doc_detail", "What information were you looking for, and what did you do when you couldn't find it?",
       SHORT_TEXT, 25, **{"*": "tc_end"}),
    _n("tc_end", "If you started again tomorrow, would you choose the same thing?", MULTI_CHOICE, 10),
]})

# ------------------------------------------------------------------------------------------------
# R&D FAILURE TREE — the value is in the failed path + why, not only the winner.
# ------------------------------------------------------------------------------------------------
RD_FAILURE = Tree("rd_failure", "rd_hyp", {n.qid: n for n in [
    _n("rd_hyp", "What was your initial hypothesis, and why did it seem promising?", SHORT_TEXT, 25, **{"*": "rd_test"}),
    _n("rd_test", "What test did you run, and what happened?", SHORT_TEXT, 25, **{"*": "rd_assumption"}),
    _n("rd_assumption", "Which assumption turned out to be wrong?", SHORT_TEXT, 20, **{"*": "rd_eliminate"}),
    _n("rd_eliminate", "Did that rule out the approach entirely, or just this version?", MULTI_CHOICE, 10, **{"*": "rd_next"}),
    _n("rd_next", "What are you trying next, and what's still uncertain?", SHORT_TEXT, 25, **{"*": "rd_24h"}),
    _n("rd_24h", "With another 24 hours, what would you test first?", SHORT_TEXT, 20),
]})

# ------------------------------------------------------------------------------------------------
# PRODUCT DEVELOPMENT TREE — expectation vs reality, workarounds, unexpected uses.
# ------------------------------------------------------------------------------------------------
PRODUCT_DEV = Tree("product_dev", "pd_expect", {n.qid: n for n in [
    _n("pd_expect", "What did you expect this product to let you build?", SHORT_TEXT, 20, **{"*": "pd_built"}),
    _n("pd_built", "What did you actually build with it?", SHORT_TEXT, 20, **{"*": "pd_missing"}),
    _n("pd_missing", "Was there a capability you expected that turned out to be missing?",
       MULTI_CHOICE, 10, no="pd_surprise", yes="pd_workaround"),
    _n("pd_workaround", "What did you do instead — did you build a workaround?", SHORT_TEXT, 20, **{"*": "pd_surprise"}),
    _n("pd_surprise", "Did anything surprise you, or did you find a use you didn't plan?",
       MULTI_CHOICE, 10, no="pd_again", yes="pd_unexpected"),
    _n("pd_unexpected", "Tell me about the unexpected use.", SHORT_TEXT, 25, **{"*": "pd_again"}),
    _n("pd_again", "What would have to change for you to reach for this again?", SHORT_TEXT, 20),
]})

# ------------------------------------------------------------------------------------------------
# ACTIVATION / CREDIT TREE — did the incentive change the decision, or just subsidize it?
# ------------------------------------------------------------------------------------------------
ACTIVATION = Tree("activation", "ac_known", {n.qid: n for n in [
    _n("ac_known", "Had you used this product before today?", MULTI_CHOICE, 10, yes="ac_credit_use", no="ac_credit_consider"),
    _n("ac_credit_consider", "Did the credit affect whether you tried it at all?", MULTI_CHOICE, 10, **{"*": "ac_without"}),
    _n("ac_without", "Would you have tried it without the credit?", MULTI_CHOICE, 10, **{"*": "ac_continue"}),
    _n("ac_credit_use", "Did the credit change how much you used it?", MULTI_CHOICE, 10, **{"*": "ac_continue"}),
    _n("ac_continue", "Do you expect to keep using it after the credit runs out?", MULTI_CHOICE, 10, **{"*": "ac_why"}),
    _n("ac_why", "What would make you continue — or stop?", SHORT_TEXT, 20),
]})

# The module catalog (Part V tail). Each is a reusable tree keyed by module name.
TREES = {t.module: t for t in [TECHNOLOGY_CHOICE, RD_FAILURE, PRODUCT_DEV, ACTIVATION]}

# One-line micro-prompts (Part XIX) keyed by the prompt_key that research_triggers routes to.
MICRO_PROMPTS = {
    "switch_reason": "What was the main reason you switched?",
    "abandon_reason": "What made you stop using it?",
    "expected_what": "What did you expect to happen?",
    "tool_choice_reason": "What mattered most in choosing this?",
    "credit_effect": "Did the credit affect your choice?",
    "credit_ignore": "You had a credit available — what made you not use it?",
    "doc_looking_for": "What were you looking for in the docs?",
    "workaround": "What were you working around?",
    "pivot_reason": "What changed your mind?",
    "why_not_shortlist": "What ruled it out?",
    "non_completion": "What was the main thing that blocked finishing?",
    "continuation": "Do you plan to keep working on this? Why?",
}
