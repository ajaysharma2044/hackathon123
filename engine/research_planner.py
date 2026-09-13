"""Specialized strategies generated from missing contract fields; no entity/sector seeds."""
from __future__ import annotations
from dataclasses import dataclass
from research_executor import ResearchQuestion

# Ontology/strategies are allowed constants. Every query is scoped to a runtime subject/objective.
STRATEGIES = {
    'economy_discovery': ('spending investment technical transitions regulatory changes infrastructure constraints',
                          'weak demand stalled investment technical substitution unsuccessful external programs'),
    'company_discovery': ('suppliers customers investors portfolio competitors complements product dependencies hiring',
                          'inactive acquired discontinued organizations weak event relevance'),
    'capital_research': ('official financing filings revenue cash ownership capex',
                         'liquidity restrictions losses restructuring financing not operating cash'),
    'talent_need': ('current technical openings required skills new teams university recruiting',
                    'hiring freeze senior only eligibility location existing university recruiting'),
    'product_research': ('official documentation API SDK pricing developer program onboarding',
                         'access restrictions discontinued API licensing competitors setup failure'),
    'internal_capability': ('research labs UX team developer relations benchmarking university program',
                            'internal teams consultants panels already solve this question'),
    'research_blindspot': ('non users switching independent choice unanswered question',
                           'own telemetry customer panel internal experiment already answers this question'),
    'buyer_research': ('department decision owner budget function current initiative',
                       'procurement restrictions no budget wrong population no decision affected'),
    'substitute_research': ('internal R&D consultancy panel innovation challenge university program alternatives',
                            'alternative supplier cheaper higher validity better skills cohort'),
    'opportunity_mapper': ('natural participant activity output buyer decision external evidence',
                           'artificial activity cohort mismatch contamination participant burden'),
    'rd_research': ('uncertainty parallel independent prototypes evaluation failure information IP constraints',
                    'nonparallel problem specialist equipment infeasible time window internal substitute'),
    'qualitative_research': ('natural choice reason permitted capture consent validity qualitative deliverable',
                             'covert capture surveillance causal overclaim generalizability selection contamination'),
    'skeptic': ('strongest objection limitations unsuccessful programs substitutes',
                'why company would not pay why cohort adds no value procurement blocks adoption'),
    'red_team': ('independent critical review falsification evidence audit',
                 'disprove theme demand economics validity privacy burden operational feasibility repeatability'),
}
FIELD_AGENT = {}
for role, fields in {
    'capital_research': ('financial_capacity',),
    'talent_need': ('talent_need_status',),
    'product_research': ('product_business_model','developer_need_status','documentation','access','onboarding'),
    'internal_capability': ('internal_capability',),
    'research_blindspot': ('external_incremental_value','event_answerable_question'),
    'buyer_research': ('buyer_function','budget_function','wtp_status','decision_affected'),
    'substitute_research': ('substitute','internal_substitute_researched'),
    'skeptic': ('strongest_objection','counterevidence'),
}.items():
    FIELD_AGENT.update({f: role for f in fields})

@dataclass(frozen=True)
class ResearchPlan:
    node_id: str
    node_type: str
    questions: tuple[ResearchQuestion, ...]
    saturation_round: int = 0

def questions_for(subject, missing_fields, node_type, round_number=0, config=None, previous=()):
    priorities = config.field_priorities if config else {}
    fields = sorted(set(missing_fields), key=lambda f: (-priorities.get(f, 0), f))
    out = []
    default = {'rd_opportunity':'rd_research', 'data_opportunity':'qualitative_research',
               'red_team':'red_team', 'company':'company_discovery'}.get(node_type, 'economy_discovery')
    for field in fields:
        role = FIELD_AGENT.get(field, default)
        support, negative = STRATEGIES[role]
        # Different rounds search an explicit unresolved question, informed by actual earlier results.
        prior = '; '.join(previous[-3:])
        for angle, phrase in [('support', support), ('alternative', 'independent evidence ' + support),
                              ('negative', negative)]:
            out.append(ResearchQuestion(f'{node_type}:{round_number}:{field}:{angle}',
                f'{subject}: {field.replace("_", " ")}; {phrase}; research pass {round_number + 1}'
                + (f'; unresolved after {prior}' if prior else ''), (field,), angle == 'negative',
                agent=role))
    return tuple(out)

def company_questions(company_name, missing_fields):
    return questions_for(company_name, missing_fields, 'company')

def generic_entity_discovery_questions(objective, round_number=0, known=()):
    out = []
    for role in ('economy_discovery', 'company_discovery'):
        for i, strategy in enumerate(STRATEGIES[role]):
            out.append(ResearchQuestion(f'discovery:{round_number}:{role}:{i}',
                f'{objective}; {strategy}; pass {round_number + 1}' +
                (f'; extend or challenge relationships around {", ".join(known[-8:])}' if known else ''),
                ('discovered_entity',), bool(i), agent=role))
    return tuple(out)
