"""Dynamic research planning primitives.

No sectors, companies, products, or sponsor archetypes are enumerated here.  Research plans are
produced from a node type + unresolved fields.  This is intentionally small: model cognition may
propose the questions, but the orchestrator validates their shape and the completion gate determines
when the work is actually done.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from research_executor import ResearchQuestion


@dataclass(frozen=True)
class ResearchPlan:
    node_id: str
    node_type: str
    questions: tuple[ResearchQuestion, ...]
    saturation_round: int = 0


def company_questions(company_name: str, missing_fields: Iterable[str]) -> tuple[ResearchQuestion, ...]:
    missing = set(missing_fields)
    templates = {
        "identity": f"{company_name} official company product business model",
        "current_initiative": f"{company_name} latest launch initiative expansion 2026",
        "financial_capacity": f"{company_name} funding revenue valuation financing 2026",
        "product_business_model": f"{company_name} pricing customers API developer product official docs",
        "strategic_need": f"{company_name} hiring growth product adoption developer program challenge",
        "internal_capability": f"{company_name} research team user research developer relations university recruiting labs",
        "external_incremental_value": f"{company_name} external research hackathon university partnership design partner developer community",
        "event_answerable_question": f"{company_name} developer onboarding switching product feedback benchmark unresolved problem",
        "buyer_function": f"{company_name} product research developer relations growth innovation recruiting leadership",
        "substitute": f"{company_name} user research panel hackathon innovation challenge developer program internal research",
        "event_value_chain": f"{company_name} what metric product team developer adoption recruiting R&D decision",
        "counterevidence": f"{company_name} existing internal capabilities why hackathon would not help limitations criticism",
    }
    out = []
    for field in missing:
        if field not in templates:
            continue
        out.append(ResearchQuestion(
            question_id=f"{company_name}:{field}:support",
            query=templates[field],
            target_fields=(field,),
            negative_query=False,
        ))
        # Important fields get an explicit disconfirmation search rather than relying on one query.
        if field in {"strategic_need", "internal_capability", "external_incremental_value", "event_answerable_question"}:
            out.append(ResearchQuestion(
                question_id=f"{company_name}:{field}:negative",
                query=f"{templates[field]} evidence against weakness already solved internally",
                target_fields=(field, "counterevidence"),
                negative_query=True,
            ))
    return tuple(out)


def generic_entity_discovery_questions(objective: str, round_number: int = 0) -> tuple[ResearchQuestion, ...]:
    """Broad discovery without an embedded sector list.

    The queries ask for economic *signals* rather than known logos/categories.  A live executor can
    diversify phrasing further.  Later rounds should use discovered entities/relations from the graph.
    """
    base = (
        "industries with rapid capital deployment and severe technical talent shortages",
        "industries with high R&D spending and prototypeable uncertain technical problems",
        "developer-facing companies with recent large funding rounds and small engineering organizations",
        "companies expanding developer ecosystems APIs SDKs or technical communities",
        "industries where university technical talent is strategically valuable but campus presence is weak",
        "companies launching new technical products where independent user choice and switching are hard to observe internally",
        "organizations funding innovation challenges university research hackathons or external experimentation",
    )
    return tuple(
        ResearchQuestion(
            question_id=f"discovery:{round_number}:{i}",
            query=f"{q}; objective: {objective}",
            target_fields=("discovered_entity",),
        )
        for i, q in enumerate(base)
    )
