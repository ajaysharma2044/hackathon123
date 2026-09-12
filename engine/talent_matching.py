"""
Talent retrieval + matching (docs/talent/job-matching.md; Parts XIII-XVI, XLVII, L).

Bipartite matching between structured job requirements and OPT-IN participant work-evidence. The
output is a DECOMPOSED, EXPLAINABLE match — never a single opaque candidate score (Part XIII/XIV).
Only participants who opted into EMPLOYER visibility are retrievable (Part XXI). Matching runs in BOTH
directions (Part XV). Missing evidence is neutral (None), never a penalty (Part L).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import compliance

MATCH_DIMS = ["capability_coverage", "artifact_relevance", "domain_relevance", "technology_overlap",
              "role_preference_fit", "location_fit", "availability_fit"]


@dataclass
class ParticipantEvidenceView:
    participant_id: str
    opted_scopes: dict = field(default_factory=dict)     # scope -> bool
    capabilities: tuple = ()          # list of {capability, support_kind, note}
    domains: tuple = ()
    technologies: tuple = ()
    desired_roles: tuple = ()
    location_preference: str = None
    availability: str = None

    def opted(self, scope) -> bool:
        return compliance.individual_disclosure_allowed(self.opted_scopes, scope)

    def artifact_caps(self) -> set:
        return {c["capability"] for c in self.capabilities if c.get("support_kind") == "ARTIFACT_SUPPORTED"}

    def all_caps(self) -> set:
        return {c["capability"] for c in self.capabilities}


def _ordinal(frac):
    if frac is None:
        return None
    if frac <= 0: return 0
    if frac < 0.5: return 1
    if frac < 1.0: return 2
    return 3


def match(job, pv: ParticipantEvidenceView) -> dict:
    """Decomposed match + explanation + explicit unknowns. No overall score. Assumes pv has opted into
    EMPLOYER visibility (callers should gate via retrieve)."""
    desired = set(job.desired_capabilities())
    why, unknowns = [], []

    # capability coverage (from all caps) and artifact relevance (artifact-supported only)
    cov = (len(desired & pv.all_caps()) / len(desired)) if desired else None
    art = (len(desired & pv.artifact_caps()) / len(desired)) if desired else None
    if desired & pv.all_caps():
        why.append(f"opted-in evidence covers capabilities: {sorted(desired & pv.all_caps())}")
    if desired & pv.artifact_caps():
        why.append(f"artifact-supported experience in: {sorted(desired & pv.artifact_caps())}")

    dom = (len(set(job.domains) & set(pv.domains)) / len(job.domains)) if job.domains else None
    tech = (len(set(t.lower() for t in job.technologies) & set(t.lower() for t in pv.technologies))
            / len(job.technologies)) if job.technologies else None

    # role preference (missing -> unknown, not 0)
    if pv.desired_roles:
        role_fit = 3 if any(r.lower() in (job.title.lower() + " " + job.job_family.lower())
                            for r in pv.desired_roles) else 0
        if role_fit:
            why.append(f"candidate opted into roles matching '{job.title}'")
    else:
        role_fit = None; unknowns.append("role preference not provided")

    if pv.location_preference:
        loc_fit = 3 if (not job.location or job.location.lower() in pv.location_preference.lower()
                        or pv.location_preference.lower() in job.location.lower()) else 1
    else:
        loc_fit = None; unknowns.append("location preference not provided")

    avail_fit = 3 if pv.availability else None
    if not pv.availability:
        unknowns.append("availability not provided")

    return {
        "job_id": job.job_id, "participant_id": pv.participant_id,
        "capability_coverage": _ordinal(cov), "artifact_relevance": _ordinal(art),
        "domain_relevance": _ordinal(dom), "technology_overlap": _ordinal(tech),
        "role_preference_fit": role_fit, "location_fit": loc_fit, "availability_fit": avail_fit,
        "why": why, "unknowns": unknowns,
        # deliberately NO 'overall_score' key — retrieval/matching, not a verdict
    }


def retrieve(job, participant_views) -> list:
    """Return matches only for participants who opted into EMPLOYER visibility, each with an
    explanation. Never returns non-opted participants (Part XXI)."""
    out = []
    for pv in participant_views:
        if pv.opted("EMPLOYER"):
            out.append(match(job, pv))
    return out


def participant_side_matches(pv: ParticipantEvidenceView, jobs) -> list:
    """Direction 2 (Part XV): which jobs match this participant's demonstrated work. Works even if the
    participant has not opted into EMPLOYER visibility — this is FOR the participant."""
    return [match(j, pv) for j in jobs]


def explain(m: dict) -> str:
    """Human-readable 'why this person appeared' (Part XIV) — evidence reasons + honest unknowns."""
    lines = [f"Match for job {m['job_id']}, participant {m['participant_id']}:"]
    lines += [f"  • {w}" for w in m["why"]] or ["  • (no positive evidence overlap yet)"]
    if m["unknowns"]:
        lines.append("  Unknown (not held against the candidate): " + "; ".join(m["unknowns"]))
    lines.append("  This is evidence-based retrieval, not a hiring recommendation.")
    return "\n".join(lines)
