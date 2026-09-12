"""
Structured hiring requirement graph (docs/talent/job-matching.md; Parts XII, XXVI).

Job requirements are structural (capabilities, domain, technologies, work type, location) and are
vetted to contain NO sensitive attributes. Requirements express what work the role needs — they are a
retrieval target, never a filter that excludes people on protected traits.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import compliance
import capability_graph


@dataclass
class JobRequirement:
    job_id: str
    title: str
    company: str = ""
    job_family: str = ""
    work_type: str = "INTERNSHIP"          # INTERNSHIP | NEW_GRAD | FULL_TIME | CONTRACT
    location: str = ""
    employment_type: str = ""
    # capability_code -> importance 0..3 (desired, not a hard exclusion on people)
    required_capabilities: dict = field(default_factory=dict)
    domains: tuple = ()
    technologies: tuple = ()

    def __post_init__(self):
        # Vet against sensitive attributes appearing anywhere in the structured requirement.
        compliance.assert_no_sensitive(list(self.required_capabilities.keys())
                                       + list(self.domains) + list(self.technologies)
                                       + [self.job_family, self.work_type])
        for cap in self.required_capabilities:
            if not capability_graph.is_capability(cap):
                raise ValueError(f"{cap!r} is not a known capability")

    def desired_capabilities(self) -> list:
        return [c for c, imp in self.required_capabilities.items() if imp >= 1]
