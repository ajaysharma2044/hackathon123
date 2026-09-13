"""Adversarial runtime tests. Fictional entities live only in tests."""
from dataclasses import replace, asdict
import json
import pytest
from agent_os import Node, NodeGraph, NodeStatus, Evidence, Defer
from governor import Governor
from research_contracts import *
from research_executor import *
from research_config import ResearchConfig
from research_runtime import ResearchRuntime
from research_bridge import EvidenceMemory, ResearchBridge
from dynamic_agents import evidence_only_synthesis, independent_red_team
from research_opportunities import ResearchOpportunity

STAMP='2026-01-01T00:00:00+00:00'

def document(host='official.example', tier=SourceTier.TIER_1_PRIMARY, kind='company_documentation'):
    return SourceDocument(host,SourceRef('https://'+host+'/source','Source',tier,source_type=kind),
                          'Exact supporting excerpt. Opposing evidence.',STAMP)

def atomic(doc, cid='a', field='identity', subject='company:a', **kw):
    return AtomicClaim(cid,field,'Exact supporting excerpt.',EpistemicStatus.FACT,(doc.source,),
        subject_id=subject,source_id=doc.source_id,quote_or_excerpt='Exact supporting excerpt.',observed_at=STAMP,**kw)

def searches(gate, subject='company:a'):
    return [dict(node=subject,query=f'{r.field}:{angle}',target_fields=[r.field],negative_query=angle==2,
                 status='SEARCHED',question=r.field) for r in gate.requirements for angle in range(3)]

class FakeExecutor:
    def __init__(self, subject='company:a', discoveries=False):
        self.subject=subject;self.discoveries=discoveries;self.calls=[]
    def search(self,q):
        self.calls.append(q)
        return [SearchResult('https://'+h+'/source','Source') for h in ('official.example','reporter.example')]
    def open_source(self,result):
        return document(result.url.split('/')[2])
    def extract_claims(self,doc,questions):
        q=questions[0];field=q.target_fields[0]
        cid=q.subject_id+':'+q.question_id+':'+doc.source_id
        if field in ('wtp_status','budget_function','talent_need_status'):
            return [AtomicClaim(cid,field,'UNKNOWN',EpistemicStatus.UNKNOWN,subject_id=q.subject_id)]
        return [atomic(doc,cid,field,q.subject_id)]
    def discover_entities(self,doc,claims,context):
        if not self.discoveries or not claims:return []
        return [DiscoveredEntity('company','Unseeded Test Instruments','https://unseeded.example',
            evidence_claim_ids=(claims[0].claim_id,),relevance='prototype tooling for the requested event')]

def test_inference_requires_support_and_memory_rejects_unknown_support():
    with pytest.raises(ValueError):AtomicClaim('i','x','guess',EpistemicStatus.INFERENCE)
    m=EvidenceMemory()
    with pytest.raises(ValueError):m.accept(AtomicClaim('i','x','guess',EpistemicStatus.INFERENCE,
        subject_id='a',supporting_claim_ids=('missing',)))

def test_fact_must_trace_to_opened_content_and_preserve_clocks():
    m=EvidenceMemory();d=document();c=atomic(d)
    with pytest.raises(ValueError):m.accept(c)
    m.remember_source(d)
    with pytest.raises(ValueError):m.accept(replace(c,quote_or_excerpt='Invented quote'))
    with pytest.raises(ValueError):m.accept(replace(c,observed_at='yesterday'))
    assert m.accept(c)
    assert m.trace_claim(c.claim_id)['sources'][0]['text']==d.text

def test_cannot_promote_source_tier_during_extraction():
    m=EvidenceMemory();d=document(tier=SourceTier.TIER_4_DISCOVERY);m.remember_source(d)
    with pytest.raises(ValueError):m.accept(replace(atomic(d),sources=(replace(d.source,tier=SourceTier.TIER_1_PRIMARY),)))

def test_unknown_and_hypothesis_do_not_satisfy_factual_gate():
    g=CompletionGate('test',(GateRequirement('identity'),),require_counterevidence=False)
    for status in (EpistemicStatus.UNKNOWN,EpistemicStatus.HYPOTHESIS):
        assert not g.evaluate([AtomicClaim('x','identity','unknown',status)]).complete

def test_killed_blocked_and_primary_never_satisfy_parent():
    for status in (NodeStatus.KILLED,NodeStatus.BLOCKED,NodeStatus.NEEDS_RESEARCH,NodeStatus.PRIMARY_VALIDATION_REQUIRED):
        g=NodeGraph();g.add(Node('c','child',status=status));p=g.add(Node('p','parent',children=['c'],status=NodeStatus.PARTIAL))
        Governor(g).run();assert p.status!=NodeStatus.RESOLVED

def test_rollup_checks_parent_gate_and_evidence_status_is_honored():
    g=NodeGraph();g.add(Node('c','child',status=NodeStatus.RESOLVED));p=g.add(Node('p','parent',children=['c'],node_type='company',status=NodeStatus.PARTIAL))
    Governor(g).run();assert p.status==NodeStatus.PARTIAL
    gov=Governor(NodeGraph());n=gov.g.add(Node('n','q'));t=gov.q.push('n','test',__import__('agent_os').Permission.AUTONOMOUS_READ)
    gov._apply(n,Evidence({},'cannot answer',NodeStatus.PRIMARY_VALIDATION_REQUIRED),t)
    assert n.status==NodeStatus.PRIMARY_VALIDATION_REQUIRED
    gov._apply(n,Defer(NodeStatus.RESOLVED,'try to bypass'),t);assert n.status!=NodeStatus.RESOLVED

def test_ungrounded_typed_node_cannot_resolve_directly():
    n=Node('n','q',node_type='company')
    with pytest.raises(ValueError):n.resolve({'claims':[]},'plausible paragraph')

def test_company_contract_missing_buyer_internal_or_negative_search_fails():
    d=document();d2=document('second.example');gate=COMPANY_COMPLETION_GATE
    claims=[atomic(d,str(i),r.field) for i,r in enumerate(gate.requirements)]
    claims.append(atomic(d2,'extra','identity'))
    ss=searches(gate)
    assert gate.evaluate(claims,searches=ss).complete
    for field in ('buyer_function','internal_capability'):
        result=gate.evaluate([c for c in claims if c.field!=field],searches=ss)
        assert not result.complete and field in result.missing
    assert not gate.evaluate(claims,searches=[s for s in ss if not s['negative_query']]).complete

def test_dynamic_research_runs_multiple_angles_and_emits_gate_trace():
    g=NodeGraph();n=g.add(Node('company:a','Research a fictional firm',node_type='company',resolver='dynamic_company_research'))
    ex=FakeExecutor();ctx={'research_executor':ex};gov=Governor(g,ctx);gov.run()
    assert n.status==NodeStatus.RESOLVED,n.value
    assert len(ex.calls)>2
    assert any(r['negative_query'] for r in ctx['research_trace'])
    assert all('completion_gate_after' in r for r in ctx['research_trace'])
    assert ctx['research_bridge'].memory.findings

def test_discovery_with_no_sector_or_logo_seed_saturates_on_duplicates():
    g=NodeGraph();n=g.add(Node('discovery','Find an excellent technical event',node_type='discovery'))
    ex=FakeExecutor('discovery',True);rt=ResearchRuntime(g,{'research_executor':ex})
    assert rt.discover(n)=='SATURATED'
    companies=[n for n in g.all() if n.node_type=='company']
    assert len(companies)==1 and companies[0].value['canonical_name']=='Unseeded Test Instruments'
    assert any(r.get('entity_stop_reasons') for r in rt.trace)
    assert len({q.question_id.split(':')[2] for q in ex.calls})>1

def test_no_backend_and_broken_backend_never_claim_saturation():
    g=NodeGraph();n=g.add(Node('discovery','objective',node_type='discovery'))
    rt=ResearchRuntime(g,{})
    assert rt.discover(n)=='RESEARCH_BACKEND_REQUIRED'
    assert not rt.memory.claims
    class Broken(FakeExecutor):
        def search(self,q):raise RuntimeError('retrieval failure')
    assert ResearchRuntime(g,{'research_executor':Broken()}).discover(n)=='RESEARCH_BACKEND_ERROR'

def test_discovery_limits_are_not_saturation_and_cycles_do_not_spawn_dependencies():
    g=NodeGraph();n=g.add(Node('discovery','objective',node_type='discovery'))
    rt=ResearchRuntime(g,{'research_executor':FakeExecutor('discovery',True),
                         'research_config':ResearchConfig(max_nodes=1)})
    assert rt.discover(n)=='DISCOVERY_BUDGET_EXHAUSTED'
    assert not n.children
    g2=NodeGraph();a=g2.add(Node('a','a',deps=['b']));g2.add(Node('b','b',deps=['a']))
    assert not Governor(g2,max_steps=10).run()['resolved']

def test_contradictions_preserved_in_both_directions():
    m=EvidenceMemory();d=document();m.remember_source(d)
    m.accept(atomic(d,'a',contradictory_claim_ids=('b',)))
    m.accept(atomic(d,'b'))
    assert m.findings['a'].contradicting() and m.findings['b'].contradicting()
    assert set(m.claims)=={'a','b'}
    assert not COMPANY_COMPLETION_GATE.evaluate(m.claims.values()).complete

def test_funding_and_comparables_do_not_establish_wtp():
    for kind in ('funding','sponsorship_comparable','pricing'):
        m=EvidenceMemory();d=document(kind=kind);m.remember_source(d)
        with pytest.raises(ValueError):m.accept(atomic(d,field='wtp_status',value={
            'status':'OBSERVED','buyer':'buyer','scope':'pilot','amount':25000}))
    m=EvidenceMemory();d=document(kind='signed_contract');m.remember_source(d)
    assert m.accept(atomic(d,field='wtp_status',value={'status':'OBSERVED','buyer':'buyer','scope':'pilot','amount':100}))

def opportunity(**kw):
    d=dict(company_id='company:a',question='Why abandon?',economic_importance='decision risk',
        unansweredness='external nonusers',hackathon_answerability='observed choice',cohort_fit='novice users',
        natural_activity='build a project',capture_plan={'mode':'SELF_REPORTED','optional':True,
        'consent_scopes':['QUALITATIVE_RESEARCH','AGGREGATE_RESEARCH']},
        qualitative_plan={k:'explicit plan' for k in ('why_question','valid_inference','invalid_inference',
            'generalizability_limit','sponsor_contamination_risk','negative_case_segment')},artifact='aggregate report',
        decision_affected='onboarding change',buyer_function='product research',substitute='panel',
        validity_ceiling='descriptive cohort only',participant_value='mentor help',participant_burden=20,
        privacy_risk='LOW',evidence_claim_ids=('a',))
    d.update(kw);return ResearchOpportunity(**d)

def test_covert_capture_and_person_scoring_are_rejected_and_live_kernels_used():
    m=EvidenceMemory();d=document();m.remember_source(d);m.accept(atomic(d));cfg=ResearchConfig()
    good=opportunity();assert not good.validate(m,cfg)
    tools=good.live_tools(cfg)
    assert tools['question_tree'].walk({})['burden_sec']==20
    assert tools['capture_store'].query('QUALITATIVE_RESEARCH',__import__('datetime').datetime.now())==[]
    for change in ({'covert':True},{'boundary':'KEYSTROKE_CAPTURE'},{'individual_scoring':True}):
        bad=replace(good,capture_plan={**good.capture_plan,**change})
        assert bad.validate(m,cfg)

def test_rd_requires_parallelizability_and_all_other_constraints():
    m=EvidenceMemory();d=document();m.remember_source(d);m.accept(atomic(d))
    spec=opportunity(kind='rd_opportunity',rd_dimensions={'uncertainty':.9})
    assert 'rd_dimensions' in spec.validate(m,ResearchConfig())
    gate=get_gate('rd_opportunity');claims=[atomic(d,str(i),r.field,value=True) for i,r in enumerate(gate.requirements) if r.field!='parallelizable']
    assert 'parallelizable' in gate.evaluate(claims,searches=searches(gate)).missing

def test_synthesis_rejects_prose_even_with_valid_reference():
    class Synth:
        def synthesize(self,**kw):return {'claim_ids':['a'],'fact':'Company will pay $25000'}
    g=NodeGraph();n=g.add(Node('synthesis','decide',node_type='synthesis'))
    result=evidence_only_synthesis(n,g,{'synthesizer':Synth()})
    assert isinstance(result,Defer)

def test_red_team_requires_independent_backend():
    g=NodeGraph();n=g.add(Node('red','audit',node_type='red_team',completion_gate='red_team'))
    ex=FakeExecutor('red')
    assert isinstance(independent_red_team(n,g,{'research_executor':ex,'red_team_executor':ex}),Defer)

def test_legacy_packets_cannot_resolve_production():
    from research_bridge import Finding
    bridge=ResearchBridge([Finding('n','company_research_live',{'answer':'strong sponsor'},'https://example.com','x','blog','claim')])
    assert bridge.packet('n')['status']=='CACHED_UNVALIDATED'
    import discovery_agents
    g=NodeGraph();n=g.add(Node('n','Research a company',resolver='company_research_live'))
    Governor(g,{'research_bridge':bridge}).run()
    assert n.status!=NodeStatus.RESOLVED

def test_independent_source_groups_prevent_syndication_counting_twice():
    gate=CompletionGate('identity',(GateRequirement('identity'),),require_counterevidence=False)
    d=document();d2=document('second.example')
    d=replace(d,source=replace(d.source,independent_group='same-owner'))
    d2=replace(d2,source=replace(d2.source,independent_group='same-owner'))
    out=gate.evaluate([atomic(d),atomic(d2,'b')],searches=searches(gate))
    assert 'independent_sources' in out.missing

def test_cross_node_inference_uses_accepted_provenance_and_rejects_weak_support():
    m=EvidenceMemory();d=document();d2=document('second.example')
    for doc,cid in ((d,'a'),(d2,'b')):m.remember_source(doc);m.accept(atomic(doc,cid))
    c=AtomicClaim('inference','cohort_fit','Supported interpretation',EpistemicStatus.INFERENCE,
                  subject_id='theme:a',supporting_claim_ids=('a','b'))
    m.accept(c)
    gate=CompletionGate('fit',(GateRequirement('cohort_fit',require_fact=False),),require_counterevidence=False)
    assert gate.evaluate([c],searches=searches(gate),supporting_claims=list(m.claims.values())).complete
    weak=replace(d.source,tier=SourceTier.TIER_4_DISCOVERY)
    assert not gate.evaluate([c],searches=searches(gate),supporting_claims=[replace(atomic(d),sources=(weak,)),atomic(d2,'b')]).complete

def test_resume_retries_partial_without_erasing_rejected_search_trace():
    g=NodeGraph();n=g.add(Node('company:a','research',node_type='company',resolver='dynamic_company_research'))
    ctx={};gov=Governor(g,ctx);gov.run();assert n.status==NodeStatus.PARTIAL
    ctx['research_executor']=FakeExecutor()
    gov.resume();assert n.status==NodeStatus.RESOLVED
    assert any(r['status']=='RESEARCH_BACKEND_REQUIRED' for r in ctx['research_trace'])

def test_red_team_reopens_upstream_and_dependent_decisions():
    g=NodeGraph();up=g.add(Node('company:a','research',node_type='company',resolver='dynamic_company_research'))
    ctx={'research_executor':FakeExecutor()};Governor(g,ctx).run();assert up.status==NodeStatus.RESOLVED
    decision=g.add(Node('decision','compare',deps=[up.id],status=NodeStatus.RESOLVED))
    target=next(iter(ctx['research_bridge'].memory.claims))
    class Attack(FakeExecutor):
        def extract_claims(self,doc,questions):
            return [replace(c,contradictory_claim_ids=(target,)) for c in super().extract_claims(doc,questions)]
    ctx['red_team_executor']=Attack('red')
    red=g.add(Node('red','audit',node_type='red_team',completion_gate='red_team'))
    result=independent_red_team(red,g,ctx)
    assert result.status==NodeStatus.CONTRADICTED
    assert up.status==NodeStatus.CONTRADICTED and decision.status==NodeStatus.PARTIAL
    assert target in ctx['research_bridge'].memory.claims

def test_opportunity_mapper_uses_shared_live_burden_budget():
    g=NodeGraph();company=g.add(Node('company:a','research',node_type='company'))
    class Mapper:
        def map_opportunities(self,**kw):return [opportunity(),opportunity(question='Why switch?')]
    ctx={'opportunity_mapper':Mapper()};rt=ResearchRuntime(g,ctx);d=document()
    rt.memory.remember_source(d);rt.memory.accept(atomic(d))
    ids=rt.map_opportunities(company)
    assert len(ids)==2
    assert ctx['live_opportunity_tools'][ids[0]]['burden'] is ctx['live_opportunity_tools'][ids[1]]['burden']
    assert all(g.get(i).status==NodeStatus.UNRESEARCHED for i in ids)

def test_pareto_comparison_has_no_hidden_weights_and_rejects_unknown_dimensions():
    from research_comparison import compare,DIMENSIONS,COSTS
    m=EvidenceMemory();d=document();m.remember_source(d)
    assert compare(['theme:a'],m)['ranking']=='UNKNOWN'
    for n in ('theme:a','theme:b'):
        for dim in DIMENSIONS:
            score=(.2 if dim in COSTS else .8) if n=='theme:a' else .5
            m.accept(atomic(d,n+dim,dim,n,value={'scale':'normalized_0_1','score':score}))
    out=compare(['theme:a','theme:b'],m)
    assert out['pareto_frontier']==['theme:a'] and out['ranking']=='UNWEIGHTED_PARETO_ONLY'
    with pytest.raises(ValueError):compare(['theme:a','theme:b'],m,{'student_value':1})

def test_positive_evidence_only_synthesis_copies_claims_and_keeps_wtp_unknown():
    from research_comparison import DIMENSIONS
    g=NodeGraph();node=g.add(Node('theme:a','theme',node_type='theme'))
    ctx={'research_executor':FakeExecutor('theme:a')};rt=ResearchRuntime(g,ctx)
    assert rt.research(node)=='EVIDENCE_COMPLETE'
    # Add normalized dimensions as evidence; reject ambiguous duplicate scales at comparison time.
    d=document()
    for dim in DIMENSIONS:
        rt.memory.accept(atomic(d,'score:'+dim,dim,node.id,value={'scale':'normalized_0_1','score':.5}))
    node.value['claims']=rt.memory.for_subject(node.id)
    node.resolve(node.value,'test accepted evidence')
    class Synth:
        def synthesize(self,**kw):return {'claim_ids':['score:student_value'],'candidate_node_ids':['theme:a']}
    ctx['synthesizer']=Synth();s=g.add(Node('synthesis','compare',node_type='synthesis'))
    out=evidence_only_synthesis(s,g,ctx)
    assert isinstance(out,Evidence) and out.status==NodeStatus.RESOLVED
    assert out.value['commercial_validation']=='PRIMARY_VALIDATION_REQUIRED'
    assert out.value['findings'][0]['atomic_claim']['statement']=='Exact supporting excerpt.'

def test_negative_burden_cannot_credit_back_participant_attention():
    from burden_budget import BurdenBudget
    from datetime import datetime
    b=BurdenBudget(120)
    with pytest.raises(ValueError):b.spend('p','MICRO_PROMPT',-30,datetime.now())
    assert b.remaining('p')==120

def test_negative_search_is_required_for_each_material_field():
    gate=COMPANY_COMPLETION_GATE;d=document();d2=document('second.example')
    claims=[atomic(d,str(i),r.field) for i,r in enumerate(gate.requirements)]+[atomic(d2,'extra')]
    ss=[s for s in searches(gate) if not (s['negative_query'] and s['target_fields']==['external_incremental_value'])]
    assert 'negative_search:external_incremental_value' in gate.evaluate(claims,searches=ss).missing

def test_unknown_wtp_cannot_hide_an_observed_numeric_payload():
    m=EvidenceMemory()
    with pytest.raises(ValueError):m.accept(AtomicClaim('x','wtp_status','UNKNOWN',EpistemicStatus.UNKNOWN,
        subject_id='company:a',value={'status':'OBSERVED','amount':25000}))
