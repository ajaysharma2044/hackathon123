"""Budgets and evidence rules, never entity seeds or winning event weights."""
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ResearchConfig:
    max_queries: int = 240
    max_companies: int = 10
    max_rounds: int = 4
    max_results_per_query: int = 4
    max_queries_per_round: int = 48
    min_primary_sources: int = 1
    min_independent_sources: int = 2
    min_query_angles: int = 2
    saturation_rounds: int = 2
    max_new_entity_fraction: float = .15
    max_dependency_hops: int = 3
    max_nodes: int = 300  # resource ceiling; reaching it is NOT saturation
    min_entity_voi: float = .1
    participant_burden_cap_sec: int = 120
    field_priorities: dict = field(default_factory=dict)
    decision_weights: dict = field(default_factory=dict)

    def __post_init__(self):
        for k in ('max_rounds', 'max_results_per_query', 'max_queries_per_round',
                  'min_primary_sources', 'min_independent_sources', 'min_query_angles',
                  'saturation_rounds', 'max_nodes', 'max_queries', 'max_companies', 'participant_burden_cap_sec'):
            if not isinstance(getattr(self, k), int) or getattr(self, k) < 1:
                raise ValueError(f'{k} must be a positive integer')
        if not 0 <= self.max_new_entity_fraction <= 1 or self.max_dependency_hops < 0:
            raise ValueError('invalid discovery limits')
