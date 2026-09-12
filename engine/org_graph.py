"""
The role-correlation graph (docs/event-ops/role-correlations.md).

This is the structural answer to "show how it is all tied together." Every role/unit — across BOTH
the event org and the research org — is a node; every working relationship is a typed edge:

    REPORTS_TO · HANDOFF · DEPENDS_ON · ESCALATES_TO · STAFFS · FEEDS_RESEARCH · CONSTRAINED_BY

So the ops↔research interlock is a queryable object, not prose. The graph answers: who depends on
whom, what an org-chart path looks like, which roles feed the research layer, which research rules
constrain an ops role, and which nodes are critical (a failure there cascades widely).

The canonical Event 1 graph is built in `event1_graph()`; it is the machine-readable twin of the
matrix in docs/event-ops/role-correlations.md. Pure stdlib.
"""
from __future__ import annotations
from dataclasses import dataclass, field

KINDS = ("REPORTS_TO", "HANDOFF", "DEPENDS_ON", "ESCALATES_TO", "STAFFS",
         "FEEDS_RESEARCH", "CONSTRAINED_BY")
# edges whose two endpoints live in different orgs (the ops↔research boundary)
CROSS_LAYER_KINDS = frozenset({"FEEDS_RESEARCH", "CONSTRAINED_BY"})


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    kind: str
    why: str

    def __post_init__(self):
        assert self.kind in KINDS, f"unknown dependency kind {self.kind}"


class OrgGraph:
    def __init__(self):
        self.nodes: set = set()
        self.edges: list = []

    def add(self, src, dst, kind, why):
        self.nodes.add(src); self.nodes.add(dst)
        self.edges.append(Edge(src, dst, kind, why))
        return self

    def out_edges(self, role, kind=None):
        return [e for e in self.edges if e.src == role and (kind is None or e.kind == kind)]

    def in_edges(self, role, kind=None):
        return [e for e in self.edges if e.dst == role and (kind is None or e.kind == kind)]

    def reports_chain(self, role):
        """Walk REPORTS_TO upward to the top of the org chart."""
        chain, seen = [role], {role}
        cur = role
        while True:
            up = [e.dst for e in self.out_edges(cur, "REPORTS_TO")]
            if not up or up[0] in seen:
                break
            cur = up[0]; chain.append(cur); seen.add(cur)
        return chain

    def escalation_path(self, role):
        """Follow ESCALATES_TO to see where a problem raised here ends up."""
        path, seen = [role], {role}
        cur = role
        while True:
            nxt = [e.dst for e in self.out_edges(cur, "ESCALATES_TO")]
            if not nxt or nxt[0] in seen:
                break
            cur = nxt[0]; path.append(cur); seen.add(cur)
        return path

    def feeds_research(self):
        """Every ops role that generates research evidence (the sensor network)."""
        return sorted({(e.src, e.dst) for e in self.edges if e.kind == "FEEDS_RESEARCH"})

    def cross_layer_edges(self):
        return [e for e in self.edges if e.kind in CROSS_LAYER_KINDS]

    def dependents(self, role):
        """Who would be blocked if `role` failed — anyone DEPENDS_ON / HANDOFF / STAFFS-fed by it."""
        return sorted({e.src for e in self.edges
                       if e.dst == role and e.kind in ("DEPENDS_ON", "HANDOFF", "STAFFS")})

    def criticality(self):
        """Rank nodes by degree (in+out). High-degree nodes are where a failure cascades — the
        roles to staff most carefully. Returns [(role, degree), ...] descending."""
        deg = {n: 0 for n in self.nodes}
        for e in self.edges:
            deg[e.src] += 1; deg[e.dst] += 1
        return sorted(deg.items(), key=lambda kv: (-kv[1], kv[0]))


def event1_graph() -> OrgGraph:
    """The canonical Event 1 correlation graph — the twin of role-correlations.md's matrix."""
    g = OrgGraph()
    # --- org chart (REPORTS_TO) ---------------------------------------------------------------
    for unit_head in ["Logistics Lead", "Finance/Sponsorship Lead", "Marketing Lead",
                      "Operations Lead", "Tech/AV Lead", "Design Lead",
                      "Participant Experience Lead", "Judging & Awards Lead", "Mentor Lead",
                      "Safety Lead"]:
        g.add(unit_head, "Event Director", "REPORTS_TO", "committee head reports to the director")
    g.add("Research Director", "Event Director", "REPORTS_TO",
          "research reports in for coordination, but owns study validity independently")
    g.add("Research Ops Lead", "Research Director", "REPORTS_TO", "runs the live loop")
    g.add("Field Researcher", "Research Ops Lead", "REPORTS_TO", "zone coverage")
    g.add("Volunteer", "Operations Lead", "REPORTS_TO", "day-of volunteers run by ops")
    g.add("Mentor", "Mentor Lead", "REPORTS_TO", "mentor roster + shifts")
    g.add("Judge", "Judging & Awards Lead", "REPORTS_TO", "judging panel")

    # --- handoffs + dependencies (the day-of flow) --------------------------------------------
    g.add("Participant Experience Lead", "Registration/Check-in", "HANDOFF",
          "check-in hands the arriving builder into the experience")
    g.add("Registration/Check-in", "Consent (Data Steward)", "HANDOFF",
          "check-in routes the builder through modular consent before any capture")
    g.add("Judging & Awards Lead", "Operations Lead", "DEPENDS_ON",
          "science-fair judging needs tables/signage/stations from ops")
    g.add("Judging & Awards Lead", "Tech/AV Lead", "DEPENDS_ON",
          "finals need stage AV; submissions need the platform up")
    g.add("Judge", "Submissions (Devpost)", "DEPENDS_ON", "judges cannot score without submissions")
    g.add("Mentor Lead", "Finance/Sponsorship Lead", "DEPENDS_ON",
          "many mentors are sponsor engineers sourced via sponsorship")
    g.add("Operations Lead", "Logistics Lead", "DEPENDS_ON", "ops runs on the venue/food/resources logistics books")

    # --- staffing (STAFFS) --------------------------------------------------------------------
    g.add("Finance/Sponsorship Lead", "Mentor", "STAFFS", "sponsor engineers supplied as mentors")
    g.add("Finance/Sponsorship Lead", "Judge", "STAFFS", "sponsor judges for category prizes")

    # --- escalation (ESCALATES_TO) ------------------------------------------------------------
    g.add("Volunteer", "Operations Lead", "ESCALATES_TO", "a volunteer escalates an ops problem")
    g.add("Operations Lead", "Safety Lead", "ESCALATES_TO", "anything safety/CoC goes to Safety")
    g.add("Safety Lead", "Event Director", "ESCALATES_TO", "critical incidents reach the director")
    g.add("Field Researcher", "Research Ops Lead", "ESCALATES_TO", "a systemic event problem seen in the field")

    # --- the ops↔research interlock: FEEDS_RESEARCH (the sensor network) -----------------------
    g.add("Mentor", "Research (mentor_interaction)", "FEEDS_RESEARCH",
          "a logged mentor interaction is a blocker/friction signal (006.mentor_interaction)")
    g.add("Registration/Check-in", "Research (baseline)", "FEEDS_RESEARCH",
          "check-in captures the pre-event baseline + consent")
    g.add("Judge", "Research (artifact signal)", "FEEDS_RESEARCH",
          "judging is structured evaluation of the built artifact")
    g.add("Operations Lead", "Research (telemetry/app events)", "FEEDS_RESEARCH",
          "the event app + brokered keys emit behavioral events")
    g.add("Field Researcher", "Research (observations)", "FEEDS_RESEARCH",
          "the human sensor network's field notes")

    # --- the research rules that CONSTRAIN ops roles ------------------------------------------
    g.add("Mentor", "Burden Budget + Consent Gate", "CONSTRAINED_BY",
          "mentor logging is ≤20s and consent-scoped; no person scoring (006 + capture.py)")
    g.add("Field Researcher", "Burden Budget + Consent Gate", "CONSTRAINED_BY",
          "interrupts only within budget + an OK interruption window; fact≠interpretation")
    g.add("Marketing Lead", "Consent Gate", "CONSTRAINED_BY",
          "photos/media only under PUBLIC_MEDIA consent")
    g.add("Finance/Sponsorship Lead", "Client View Gate", "CONSTRAINED_BY",
          "sponsors get aggregate findings only — never raw/individual data")
    return g
