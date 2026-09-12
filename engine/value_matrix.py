"""
Multi-sided value matrix (docs/multi-sided/mechanic-value-matrix.md). The net-new layer the
integration plan flagged: U[s,j] (mechanic x stakeholder VALUE), C[r,j] (mechanic x resource COST),
cross-side fan-out, synergy Gamma, and conflicts. Builds ON the existing engines
(opportunity_market.fan_out for participant scopes; does not recreate the markets).

DISCIPLINE: utility DIMENSIONS are never collapsed into one universal score. Values are ordinal
(NEG/NONE/LOW/MED/HIGH) with an evidence tag. A numeric projection exists ONLY for the mechanism-
design layer's cross-stakeholder Pareto/Nash comparison, and it is illustrative-ordinal, not
fabricated precision. Every cell carries evidence status; most cross-side synergies start UNKNOWN.
"""
from __future__ import annotations
from opportunity_market import fan_out   # reuse: participant-side value fan-out (do not duplicate)

# Stakeholder sides (Part I) + discovered ones (accelerators, design_partners, followon_customers).
STAKEHOLDERS = ["participants", "teams", "employers", "vcs", "product_clients", "rd_clients",
                "sponsors", "mentors", "judges", "cornell", "organizers", "accelerators",
                "design_partners", "followon_customers"]

# Decomposed utility dimensions per stakeholder (Part II) — kept as vectors, never one score.
UTILITY_DIMS = {
    "participants": ["fun","learning","autonomy","building","mentor_access","social","recognition",
                     "career_opportunity","startup_opportunity","funding_opportunity","continuation",
                     "trust","burden"],   # burden is NEGATIVE-valued
    "employers": ["relevant_talent","work_evidence","capability_evidence","search_efficiency","response_rate","interview_conversion"],
    "vcs": ["relevant_dealflow","technical_evidence","team_evidence","continuation_evidence","thesis_fit","founder_optin","meeting_conversion"],
    "product_clients": ["choice_evidence","friction_evidence","switching_evidence","use_cases","retention","qualitative_why"],
    "rd_clients": ["solution_diversity","prototype_quality","failure_information","search_speed","evaluation_quality"],
    "sponsors": ["brand_exposure","useful_engagement","product_usage","mentor_interaction","developer_relationship","research_output"],
    "cornell": ["student_outcome","entrepreneurship","industry_relationship","employer_relationship","reputation","learning"],
    "organizers": ["revenue","contribution_margin","repeatability","research_assets","client_renewal","reputation","operational_learning"],
    "mentors": ["impact","recruiting_signal","recognition","learning"],
    "teams": ["build_progress","cohesion","recognition","continuation"],
}
ORD = {"NEG": -2, "NONE": 0, "LOW": 1, "MED": 2, "HIGH": 3}

# Event mechanics / primitives (Part III). The atoms we design the event out of.
MECHANICS = ["mentor_request","repo_submission","demo","tool_switch","team_formation",
             "optional_challenge","follow_up_30_90","project_continuation","sponsor_keynote",
             "workshop","exit_interview","checkpoint","brokered_key_use","founder_dinner",
             "sponsored_bounty_track","open_build_track"]

# U[s][j]: (direction/magnitude ordinal, evidence_tag). Only the load-bearing cells are seeded;
# the rest default to ("NONE","U"). Tags: O=observed-in-repo, I=inferred, H=hypothesis, U=unknown.
def _u():
    U = {s: {j: ("NONE", "U") for j in MECHANICS} for s in STAKEHOLDERS}
    def set(s, j, v, t): U[s][j] = (v, t)
    # DEMO — high cross-side fan-out (the flagship multi-use mechanic)
    for s, v, t in [("participants","HIGH","I"),("employers","MED","H"),("vcs","MED","H"),
                    ("product_clients","HIGH","I"),("sponsors","MED","I"),("organizers","HIGH","O"),
                    ("cornell","MED","I"),("judges","HIGH","O")]:
        set(s, "demo", v, t)
    # MENTOR_REQUEST — high participant + research value, per value-per-minute
    set("participants","mentor_request","HIGH","I"); set("product_clients","mentor_request","MED","H")
    set("sponsors","mentor_request","MED","I"); set("mentors","mentor_request","HIGH","I")
    # REPO_SUBMISSION — the multi-use artifact
    for s in ["product_clients","rd_clients","employers","vcs","organizers"]: set(s,"repo_submission","MED","H")
    set("participants","repo_submission","MED","I")
    # TOOL_SWITCH / OPEN_BUILD — product-research + participant autonomy; sponsored bounty distorts it
    set("product_clients","tool_switch","HIGH","O"); set("participants","open_build_track","HIGH","I")
    set("product_clients","open_build_track","HIGH","O")
    # FOLLOW_UP / CONTINUATION — retention + venture + cornell
    for s in ["product_clients","vcs","cornell","organizers"]: set(s,"follow_up_30_90","MED","H")
    for s,v in [("participants","HIGH"),("vcs","MED"),("cornell","HIGH"),("teams","HIGH")]: set(s,"project_continuation",v,"H")
    # SPONSOR_KEYNOTE — low participant value/minute; some sponsor value
    set("participants","sponsor_keynote","NEG","I"); set("sponsors","sponsor_keynote","MED","I")
    # SPONSORED_BOUNTY_TRACK — sponsor value but distorts free-choice research validity
    set("sponsors","sponsored_bounty_track","HIGH","I"); set("product_clients","sponsored_bounty_track","NEG","I")
    set("participants","sponsored_bounty_track","LOW","H")
    # BROKERED_KEY_USE — invisible research value, no participant burden
    for s in ["product_clients","sponsors","organizers"]: set(s,"brokered_key_use","HIGH","O")
    # EXIT_INTERVIEW / CHECKPOINT — research value, participant BURDEN
    set("product_clients","exit_interview","HIGH","I"); set("participants","exit_interview","NEG","I")
    set("participants","checkpoint","NEG","I"); set("product_clients","checkpoint","MED","I")
    # FOUNDER_DINNER — network density: cornell, vcs, participants
    for s in ["participants","vcs","cornell","design_partners"]: set(s,"founder_dinner","MED","H")
    return U
U = _u()

# C[r][j]: resource cost matrix (Part IV). Ordinal consumption per mechanic.
RESOURCES = ["participant_attention","participant_minutes","mentor_hours","researcher_hours",
             "organizer_hours","space","prize_budget","sponsor_slots","research_burden","trust_risk","frontend_distortion"]
def _c():
    C = {r: {j: "NONE" for j in MECHANICS} for r in RESOURCES}
    C["participant_minutes"].update(mentor_request="LOW", demo="MED", exit_interview="MED", checkpoint="LOW",
                                    workshop="MED", sponsor_keynote="MED", founder_dinner="MED")
    C["research_burden"].update(exit_interview="HIGH", checkpoint="MED", follow_up_30_90="MED")
    C["frontend_distortion"].update(sponsored_bounty_track="HIGH", sponsor_keynote="MED", exit_interview="LOW")
    C["trust_risk"].update(sponsored_bounty_track="MED", exit_interview="LOW", brokered_key_use="LOW")
    C["mentor_hours"].update(mentor_request="HIGH")
    C["sponsor_slots"].update(sponsor_keynote="HIGH", workshop="MED", sponsored_bounty_track="HIGH")
    return C
C = _c()

def cross_side_fanout(j):
    """Which stakeholder sides j creates POSITIVE value for (magnitude > 0). Reuses the participant-side
    scope fan-out from opportunity_market where applicable. High fan-out = a multi-use mechanic."""
    positive = [s for s in STAKEHOLDERS if ORD[U[s][j][0]] > 0]
    return {"mechanic": j, "sides_benefited": positive, "count": len(positive),
            "sides_harmed": [s for s in STAKEHOLDERS if ORD[U[s][j][0]] < 0]}

# Synergy Gamma(j,k): >0 complementary, <0 conflicting, 0 independent. Most start UNKNOWN/HYPOTHESIZED.
SYNERGY = {   # (j,k): (value, tag)
    ("repo_submission","demo"): ("POS","H"),               # artifact + demo super-additive for employers/VCs
    ("repo_submission","project_continuation"): ("POS","H"),
    ("demo","follow_up_30_90"): ("POS","H"),
    ("sponsored_bounty_track","open_build_track"): ("NEG","I"),   # bounty contaminates free-choice validity
    ("sponsored_bounty_track","tool_switch"): ("NEG","I"),
    ("mentor_request","exit_interview"): ("POS","H"),       # help context enriches the "why"
}
def synergy(j, k):
    return SYNERGY.get((j, k), SYNERGY.get((k, j), ("UNKNOWN", "U")))

def analyze_mechanic(j):
    """Master query (Part LXX): full multi-sided profile of one event mechanic."""
    fo = cross_side_fanout(j)
    resources = {r: C[r][j] for r in RESOURCES if C[r][j] != "NONE"}
    synergies = {f"{j}+{k}": synergy(j, k) for k in MECHANICS if k != j and synergy(j, k)[0] != "UNKNOWN"}
    return {
        "mechanic": j,
        "stakeholders_benefited": fo["sides_benefited"],
        "stakeholders_harmed": fo["sides_harmed"],
        "cross_side_fanout": fo["count"],
        "resources_consumed": resources,
        "value_cells": {s: U[s][j] for s in STAKEHOLDERS if U[s][j][0] != "NONE"},
        "synergies": synergies,
        "frontend_distortion": C["frontend_distortion"][j],
        "trust_risk": C["trust_risk"][j],
        "consent_note": "individual-grain outputs require opt-in; aggregate-only otherwise (compliance.py)",
        "unknowns": "observed WTP UNKNOWN; most synergy/magnitude cells are H/U until Event 1 measures them",
    }
