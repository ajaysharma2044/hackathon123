"""Dynamic query planning from unresolved research fields.

This hardcodes research ontology, not companies, sectors, or answers.
"""
from __future__ import annotations
from research_executor import ResearchQuestion

FIELD_TERMS = {
    "identity": ("official", "about", "company", "founded", "headquarters"),
    "current_initiative": ("launch", "announcement", "expansion", "new product", "partnership"),
    "financial_capacity": ("funding", "financing", "revenue", "valuation", "cash", "investment"),
    "product_business_model": ("product", "pricing", "customers", "API", "SDK", "enterprise"),
    "strategic_need": ("hiring", "growth", "adoption", "developer", "research", "product feedback"),
    "internal_capability": ("research team", "user research", "DevRel", "developer relations", "lab", "university recruiting"),
    "buyer_function": ("product research", "growth", "developer relations", "innovation", "recruiting", "research leadership"),
    "substitute": ("user panel", "customer advisory board", "hackathon", "consulting", "internal research", "university program"),
    "economic_problem": ("cost", "constraint", "shortage", "capacity", "risk", "bottleneck", "demand"),
    "student_value": ("students", "builders", "learning", "projects", "mentorship", "technical challenge"),
    "cornell_fit": ("Cornell", "research", "engineering", "computer science", "ORIE", "project teams"),
    "company_ecosystem": ("vendors", "companies", "startups", "customers", "ecosystem", "suppliers"),
    "event_feasibility": ("prototype", "hackathon", "48 hours", "benchmark", "API", "simulation"),
    "commercial_surface": ("sponsorship", "research", "recruiting", "R&D", "developer adoption", "innovation"),
}
NEGATIVE_TERMS = {
    "strategic_need": ("already solved", "mature", "no hiring", "downsizing", "low priority"),
    "internal_capability": ("internal research team", "UX research", "developer research", "existing lab", "existing university program"),
    "external_incremental_value": ("internal alternative", "existing vendor", "existing panel", "existing hackathon"),
    "event_answerable_question": ("not representative", "cannot test", "enterprise only", "long sales cycle"),
    "substitute": ("Topcoder", "Kaggle", "Devpost", "consulting", "customer advisory board", "user panel"),
    "economic_problem": ("resolved", "declining importance", "low spend", "low urgency"),
    "event_feasibility": ("specialized equipment", "cannot prototype", "requires proprietary data", "months to validate"),
    "commercial_surface": ("no budget", "procurement", "internal only", "no university program"),
}


def _domain_query(domain, terms):
    if not domain: return None
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0].removeprefix("www.")
    return f"site:{domain} {terms}"


def company_questions(company_name, missing_fields, official_domain=None, prior_terms=()):
    questions, prior = [], " ".join(str(x) for x in prior_terms if x)[:300]
    for field_name in sorted(set(missing_fields)):
        if field_name in {"external_incremental_value", "event_answerable_question", "event_value_chain"}: continue
        terms = " ".join(FIELD_TERMS.get(field_name, (field_name.replace("_", " "),)))
        questions.append(ResearchQuestion(f"{company_name}:{field_name}:general", f'"{company_name}" {terms} {prior}'.strip(), (field_name,)))
        official = _domain_query(official_domain, terms)
        if official: questions.append(ResearchQuestion(f"{company_name}:{field_name}:official", official, (field_name,), preferred_domains=(official_domain,)))
        if field_name in NEGATIVE_TERMS:
            neg = " OR ".join(f'"{x}"' for x in NEGATIVE_TERMS[field_name])
            questions.append(ResearchQuestion(f"{company_name}:{field_name}:negative", f'"{company_name}" ({terms}) ({neg})', (field_name, "counterevidence"), negative_query=True))
    return tuple(questions)


def theme_questions(theme_name, missing_fields, prior_terms=()):
    prior, out = " ".join(str(x) for x in prior_terms if x)[:300], []
    for field_name in sorted(set(missing_fields)):
        if field_name == "falsification": continue
        terms = " ".join(FIELD_TERMS.get(field_name, (field_name.replace("_", " "),)))
        out.append(ResearchQuestion(f"theme:{theme_name}:{field_name}:support", f'"{theme_name}" {terms} {prior}'.strip(), (field_name,)))
        if field_name in NEGATIVE_TERMS:
            neg = " OR ".join(f'"{x}"' for x in NEGATIVE_TERMS[field_name])
            out.append(ResearchQuestion(f"theme:{theme_name}:{field_name}:negative", f'"{theme_name}" ({terms}) ({neg})', (field_name, "counterevidence"), negative_query=True))
    return tuple(out)


def generic_entity_discovery_questions(objective, round_number=0, prior_entities=()):
    seen = ", ".join(list(prior_entities)[-12:])
    diversify = f" exclude or diversify beyond recently found: {seen}" if seen else ""
    lenses = (
        "rapid capital deployment technical bottlenecks unmet engineering demand",
        "high R&D spending uncertain prototypeable technical problems external experimentation",
        "recently funded technical companies developer products small teams aggressive growth",
        "technical talent shortages high compensation weak university recruiting presence",
        "developer ecosystems APIs SDKs competitive switching onboarding adoption",
        "industrial or infrastructure sectors where many independent technical approaches have value",
        "organizations currently funding university research innovation challenges hackathons external R&D",
        "emerging technical markets with high spending and weak internal research capability",
    )
    return tuple(ResearchQuestion(f"discovery:{round_number}:{i}", f"{lens}; objective: {objective}{diversify}", ("discovered_entity",)) for i, lens in enumerate(lenses))
