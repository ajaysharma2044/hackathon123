"""Economic question → event research plan, using the existing Live Research OS kernels."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from qualitative import assert_not_surveillance
from capture import ALL_SCOPES, ConsentLedger, CaptureStore
from burden_budget import BurdenBudget
from adaptive_questions import Tree, Node as QuestionNode
from adaptive_sampling import Sampler
from commercial_logic import WTPStatus

@dataclass(frozen=True)
class ResearchOpportunity:
    company_id: str
    question: str
    economic_importance: str
    unansweredness: str
    hackathon_answerability: str
    cohort_fit: str
    natural_activity: str
    capture_plan: dict
    qualitative_plan: dict
    artifact: str
    decision_affected: str
    buyer_function: str
    substitute: str
    validity_ceiling: str
    participant_value: str
    participant_burden: int
    privacy_risk: str
    wtp_status: str = WTPStatus.UNKNOWN.value
    kind: str = 'data_opportunity'
    evidence_claim_ids: tuple[str, ...] = ()
    rd_dimensions: dict = field(default_factory=dict)

    def validate(self, memory, config):
        errors = []
        for f in ('company_id','question','economic_importance','unansweredness','hackathon_answerability',
                  'cohort_fit','natural_activity','artifact','decision_affected','buyer_function',
                  'substitute','validity_ceiling','participant_value','privacy_risk'):
            if not getattr(self,f) or str(getattr(self,f)).upper() == 'UNKNOWN':
                errors.append(f)
        if not self.evidence_claim_ids or any(i not in memory.claims or memory.claims[i].status.value not in ('FACT','INFERENCE') for i in self.evidence_claim_ids):
            errors.append('accepted_evidence_required')
        if self.wtp_status not in (WTPStatus.UNKNOWN.value,WTPStatus.PRIMARY_VALIDATION_REQUIRED.value):
            # Commercial observations are separate atomic buyer evidence, never mapper assertions.
            errors.append('wtp_must_come_from_buyer_evidence')
        p = self.capture_plan
        try:
            assert_not_surveillance(p.get('mode'), p.get('covert',False), p.get('boundary'))
        except ValueError as exc: errors.append(str(exc))
        scopes = set(p.get('consent_scopes',()))
        if not scopes or not scopes <= ALL_SCOPES or 'CORE_EVENT' in scopes:
            errors.append('separate_research_consent_required')
        if p.get('mode') == 'BROKERED_TELEMETRY' and 'PRODUCT_TELEMETRY' not in scopes:
            errors.append('PRODUCT_TELEMETRY_required')
        if not p.get('optional') or p.get('individual_scoring') or p.get('forced_product_use'):
            errors.append('participant_choice_or_privacy')
        if p.get('mode') == 'SELF_REPORTED' and self.participant_burden == 0:
            errors.append('explicit_question_burden_cannot_be_zero')
        if self.privacy_risk.upper() in ('HIGH','UNACCEPTABLE'):
            errors.append('privacy_risk')
        if type(self.participant_burden) is not int or not 0 <= self.participant_burden <= config.participant_burden_cap_sec:
            errors.append('participant_burden')
        for f in ('why_question','valid_inference','invalid_inference','generalizability_limit',
                  'sponsor_contamination_risk','negative_case_segment'):
            if not self.qualitative_plan.get(f):errors.append('qualitative:' + f)
        if 'QUALITATIVE_RESEARCH' not in scopes:
            errors.append('QUALITATIVE_RESEARCH_required')
        if self.kind == 'rd_opportunity':
            required = ('uncertainty','parallelizable','prototypeable_in_event','evaluable','needs_deep_domain',
                        'failure_information_valuable','internal_substitute_researched','ip_understood','student_fit')
            if any(f not in self.rd_dimensions for f in required):errors.append('rd_dimensions')
            else:
                from value_engines import RDProblem, rd_fit
                dims = self.rd_dimensions
                names = required[:5]
                if any(type(dims[k]) not in (int,float) or not 0 <= dims[k] <= 1 for k in names):
                    errors.append('rd_scores_out_of_range')
                elif rd_fit(RDProblem(**{k:dims[k] for k in names}))[0] != 'advantageous':
                    errors.append('rd_fit_inferior')
                if not all(dims[k] is True for k in required[5:]):errors.append('rd_constraints')
        return sorted(set(errors))

    def live_tools(self, config, ledger=None, burden=None, now=None):
        """Planning integration; does not collect data, grant consent, or contact participants."""
        ledger = ledger or ConsentLedger()
        budget = burden or BurdenBudget(cap_sec=config.participant_burden_cap_sec)
        tree = Tree('opportunity:' + self.company_id, 'why', {'why':QuestionNode(
            'why',self.qualitative_plan['why_question'],burden_sec=self.participant_burden)})
        return {'capture_store':CaptureStore(ledger),'burden':budget,'question_tree':tree,
                'sampler':Sampler(budget,now or datetime.now())}
