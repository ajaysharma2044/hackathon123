"""Deterministic live-path acceptance tests: real executor/runtime, fake network/model only."""
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import pytest
from research_executor import ResearchQuestion, EvidenceCandidate
from research_contracts import SourceRef, SourceTier, EpistemicStatus
from semantic_extractor import SemanticGroundedExtractor, OpenAICompatibleProvider
from web_research import ScrapingResearchExecutor, SourceDocument, SearchHit
from research_run import run, main
from research_config import ResearchConfig
from research_output import RunWriter
from live_defaults import DefaultOpportunityMapper, DefaultThemeGenerator, DefaultSynthesis

TEXT = 'Acme develops the Acme Kit platform for builders. Acme raised $100 million in financing. Acme operates its company website at acme.test. Acme Kit has limited offline integration support.'
class Search:
    def __init__(self): self.queries=[]
    def search(self,query,limit=8):
        self.queries.append(query)
        return [SearchHit('Acme profile','https://reuters.com/acme'),SearchHit('Acme company','https://acme.test/about')][:limit]
class Fetch:
    def __init__(self): self.urls=[]
    def fetch(self,url):
        self.urls.append(url)
        return SourceDocument(url,'Acme company',TEXT,'2026-09-13T00:00:00+00:00',hashlib.sha256(TEXT.encode()).hexdigest())
class Model:
    def __init__(self): self.calls=[]
    def complete(self,instruction,payload):
        self.calls.append((instruction,payload))
        if 'passages' in payload:
            c=payload['passages'][0]; field=payload['target_fields'][0]
            item={'local_id':'a','candidate_id':c['candidate_id'],'field':field,
                  'statement':c['excerpt'],'status':'FACT','quote_or_excerpt':c['excerpt']}
            if field=='product_business_model': item['value']={'research_terms':['Acme Kit']}
            if field=='wtp_status': item.update(status='PRIMARY_VALIDATION_REQUIRED',statement='Buyer validation required',quote_or_excerpt='')
            entities = [{'entity_type':'company','canonical_name':'Acme','evidence_local_ids':['a'],
                         'relevance':'Documented builder platform warrants research'}] if field=='discovered_entity' else []
            return {'claims':[item],'entities':entities}
        if 'opportunities' in instruction:
            return {'opportunities':[dict(question='Why do builders abandon an integration?',
                economic_importance='Hypothesis: product adoption decision',unansweredness='Validate whether existing research answers this',
                hackathon_answerability='Observe voluntarily chosen prototypes',cohort_fit='Validate builder fit',
                natural_activity='Build a freely chosen prototype',artifact='Aggregate reasons and limitations',
                decision_affected='Hypothesis: onboarding investment',buyer_function='Hypothesis: product research',
                substitute='Compare internal user panels',validity_ceiling='Selected cohort only',participant_value='Optional reflection',
                evidence_claim_ids=[payload['claims'][0]['claim_id']],kind='data_opportunity',
                qualitative_plan=dict(why_question='Why did you switch?',valid_inference='Reported reasons in this cohort',
                    invalid_inference='Causal market effect',generalizability_limit='Selected volunteers',
                    sponsor_contamination_risk='Sponsor influence',negative_case_segment='Non-adopters'))]}
        return {'themes':[{'name':'Integration learning event','evidence_claim_ids':[payload['claims'][0]['claim_id']],
                           'event_connection':'HYPOTHESIS: compare integration experiences and student learning'}]}

def setup():
    search,fetch,model=Search(),Fetch(),Model()
    ex=ScrapingResearchExecutor(search,fetch,SemanticGroundedExtractor(model))
    red=ScrapingResearchExecutor(search,fetch,SemanticGroundedExtractor(model,adversarial=True))
    return ex,red,model

def live_run(tmp_path,company=None):
    ex,red,model=setup()
    writer=RunWriter(tmp_path/'run')
    result=run('Discover builder product research opportunities',ex,
        ResearchConfig(max_rounds=3,max_queries=80,max_companies=2,max_results_per_query=2),red,
        company=company,live_mode=True,run_writer=writer,independence_level='SAME_PROVIDER_SEPARATE_PASS',
        opportunity_mapper=DefaultOpportunityMapper(model),theme_generator=DefaultThemeGenerator(model),synthesizer=DefaultSynthesis())
    # Normalize exactly as JSON export does.
    from research_output import serialize
    result=json.loads(json.dumps(result,default=serialize));writer.finish(result)
    return result,model,writer

def test_company_live_end_to_end(tmp_path):
    result,model,writer=live_run(tmp_path,'Acme')
    assert result['status']=='PARTIAL'
    assert len(result['source_documents'])>=2
    facts=[c for c in result['atomic_claims'] if c['status']=='FACT']
    assert facts
    docs={d['source_id']:d for d in result['source_documents']}
    assert all(c['quote_or_excerpt'] in docs[c['source_id']]['text'] for c in facts)
    trace=result['full_research_trace']
    assert any(r.get('negative_query') for r in trace)
    assert len([r for r in trace if r.get('query')])<=80
    company=result['company_dossiers'][0]
    assert company['value']['identity_status']=='CORROBORATED'
    assert len(company['value']['identity_evidence_claim_ids'])>=2
    assert any(d['source']['tier']==1 for d in result['source_documents'])
    assert result['primary_validation_required']
    assert result['research_opportunities']
    assert result['candidate_event_concepts']
    assert result['partial_synthesis']['verdict']=='NO FINAL WINNER YET'
    adversarial=[p for i,p in model.calls if 'SEPARATE ADVERSARIAL PASS' in i]
    assert adversarial and all('synthesis' not in p for p in adversarial)
    for name in ('summary.md','result.json','trace.jsonl','sources.json','claims.json','entities.json','nodes.json','primary-validation.md','errors.json','sources.jsonl','claims.jsonl','events.jsonl'):
        assert (writer.path/name).exists()
    assert list((writer.path/'companies').glob('*.md'))

def test_objective_discovers_and_researches_company(tmp_path):
    result,model,writer=live_run(tmp_path)
    companies=result['company_dossiers']
    assert len(companies)==1 and companies[0]['value']['canonical_name']=='Acme'
    assert companies[0]['value']['discovery_claim_ids']
    assert any(r.get('node')==companies[0]['id'] and r.get('sources_opened') for r in result['full_research_trace'])
    assert any(r.get('agent')=='red_team' for r in result['full_research_trace'])

def test_semantic_rejects_urls_fake_quotes_and_unsupported_inferences():
    source=SourceRef('https://example.test','Retrieved',SourceTier.TIER_4_DISCOVERY,retrieved_at='now')
    candidate=EvidenceCandidate('p','q',('identity',),source,'Acme builds tools.',1)
    q=ResearchQuestion('q','Acme',('identity',),subject_id='company:acme')
    class Bad:
        def complete(self,*args):
            return {'claims':[
                {'field':'identity','statement':'Injected','status':'FACT','candidate_id':'p','quote_or_excerpt':'Acme builds tools.','url':'https://invented.test'},
                {'field':'identity','statement':'Fake','status':'FACT','candidate_id':'p','quote_or_excerpt':'Invented quote'},
                {'field':'identity','statement':'Inference','status':'INFERENCE','supporting_claim_ids':['invented']} ]}
    output=SemanticGroundedExtractor(Bad()).extract(q,[candidate],{})
    assert not output.claims and len(output.notes)==3

def test_cli_live_defaults_without_keys(monkeypatch,tmp_path,capsys):
    import web_research
    for key in ('RESEARCH_LLM_API_KEY','RESEARCH_LLM_MODEL','RESEARCH_RED_TEAM_LLM_API_KEY','RESEARCH_RED_TEAM_LLM_MODEL'):
        monkeypatch.delenv(key,raising=False)
    monkeypatch.setattr(web_research,'default_search_provider',lambda:Search())
    monkeypatch.setattr(web_research,'HTTPFetcher',lambda:Fetch())
    assert main(['--company','Acme','--live','--max-queries','9','--max-rounds','2','--output',str(tmp_path/'cli')])==2
    out=capsys.readouterr()
    assert 'Semantic extractor: MISSING' in out.err and '[OPEN]' in out.err
    result=json.loads((tmp_path/'cli/result.json').read_text())
    assert result['source_documents'] and not any(c['status']=='FACT' for c in result['atomic_claims'])
    assert len([r for r in result['full_research_trace'] if r.get('query')])<=9

def test_empty_search_not_successful_research():
    from agent_os import Node,NodeGraph
    from research_runtime import ResearchRuntime
    class Empty:
        def search(self,q):return []
    g=NodeGraph();n=Node('n','Acme',node_type='company',completion_gate='company');g.add(n)
    rt=ResearchRuntime(g,{'research_executor':Empty()})
    _,records=rt.execute(n,[ResearchQuestion('q','Acme',('identity',),True)])
    assert records[0]['status']=='SOURCE_ACCESS_FAILED'

def test_provider_http_contract(monkeypatch):
    captured=[]
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,n):return json.dumps({'choices':[{'finish_reason':'stop','message':{'content':'{"claims":[]}'}}]}).encode()
    class Opener:
        def open(self,request,timeout):captured.append(request);return Response()
    import semantic_extractor
    monkeypatch.setattr(semantic_extractor.urllib.request,'build_opener',lambda *a:Opener())
    assert OpenAICompatibleProvider('fake','test-model').complete('Extract',{})=={'claims':[]}
    body=json.loads(captured[0].data)
    assert body['response_format']=={'type':'json_object'}
    assert len(body['messages'])==2 and 'tools' not in body

def test_identity_needs_independent_corroboration_and_versions_source_metadata():
    from agent_os import Node,NodeGraph
    from research_runtime import ResearchRuntime
    from research_bridge import EvidenceMemory
    ex,_,_=setup()
    g=NodeGraph();n=Node('company:acme','Acme',node_type='company',completion_gate='company',value={'canonical_name':'Acme','canonical_url':'https://acme.test'});g.add(n)
    rt=ResearchRuntime(g,{'research_executor':ex})
    ex.search_provider.search=lambda *a,**k:[SearchHit('Acme','https://acme.test/about')]
    rt.execute(n,[ResearchQuestion('one','Acme identity',('identity',))])
    assert n.value['identity_status']=='UNVERIFIED'
    assert all(d.source.tier==4 for d in rt.memory.documents.values())

def test_budget_company_cap_and_checkpoint_before_interruption(tmp_path):
    from agent_os import Node,NodeGraph
    from research_runtime import ResearchRuntime
    from research_executor import DiscoveredEntity
    ex,_,_=setup()
    g=NodeGraph();n=Node('discovery','Discover',node_type='discovery');g.add(n)
    rt=ResearchRuntime(g,{'research_executor':ex,'research_config':ResearchConfig(max_companies=1)})
    entities,_=rt.execute(n,[ResearchQuestion('discover','Acme financing company',('discovered_entity',))])
    spawned,_=rt.spawn(n,entities)
    assert len(spawned)==1
    extra=replace(entities[0],canonical_name='Another company')
    _,stops=rt.spawn(n,[extra])
    assert stops[0]['reason']=='COMPANY_BUDGET_EXHAUSTED'
    assert 'max_companies' in rt.ctx['budget_exhausted']
    writer=RunWriter(tmp_path/'interrupted')
    def progress(event,payload):
        if event=='CLAIM': raise KeyboardInterrupt()
    result=run('Acme',ex,ResearchConfig(max_queries=12),company='Acme',live_mode=True,run_writer=writer,progress=progress)
    assert result['status']=='INTERRUPTED'
    assert (writer.path/'sources.jsonl').read_text() and (writer.path/'claims.jsonl').read_text()
    assert (writer.path/'nodes.json').exists()

def test_semantic_wtp_cannot_be_inferred_from_funding():
    source=SourceRef('https://reuters.com/story','Retrieved',SourceTier.TIER_2_REPUTABLE,retrieved_at='now')
    candidate=EvidenceCandidate('p','q',('wtp_status',),source,'Acme raised $100 million.',1)
    class BadWTP:
        def complete(self,*args):return {'claims':[{'field':'wtp_status','statement':'Will pay $25000',
            'status':'FACT','candidate_id':'p','quote_or_excerpt':'Acme raised $100 million.'}]}
    result=SemanticGroundedExtractor(BadWTP()).extract(ResearchQuestion('q','Acme WTP',('wtp_status',),subject_id='company:a'),[candidate],{})
    assert not result.claims and result.notes

def test_query_planner_uses_only_exact_grounded_product_terms():
    from research_planner import questions_for
    from research_contracts import AtomicClaim
    source=SourceRef('https://example.test','Source',SourceTier.TIER_4_DISCOVERY)
    claim=AtomicClaim('a','product_business_model','Acme Kit',EpistemicStatus.FACT,(source,),
        quote_or_excerpt='Acme launched Acme Kit.',value={'research_terms':['Acme Kit','Invented SDK']})
    queries=questions_for('Acme',['product_business_model'],'company',1,accepted_claims=[claim])
    assert all('"Acme Kit"' in q.query and 'Invented SDK' not in q.query for q in queries)
    assert any(q.negative_query for q in queries)

def test_html_links_are_retrieved_identity_evidence():
    from web_research import _TextParser
    p=_TextParser();p.feed('<p>Acme runs <a href="https://acme.test/">its official website</a>.</p>')
    assert 'https://acme.test/' in ''.join(p.parts)

def test_fetch_cache_retry_and_size_limit(monkeypatch):
    import web_research as web
    from email.message import Message
    monkeypatch.setattr(web,'_safe_url',lambda u:True)
    monkeypatch.setattr(web.time,'sleep',lambda _:None)
    calls=[]
    class Response:
        headers=Message();headers['Content-Type']='text/plain'
        status=200
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,n):return b'Acme builds developer tools.'[:n]
    class Opener:
        def open(self,*args,**kwargs):
            calls.append(1)
            if len(calls)==1: raise web.urllib.error.URLError('temporary')
            return Response()
    monkeypatch.setattr(web.urllib.request,'build_opener',lambda *a:Opener())
    fetcher=web.HTTPFetcher(retries=1)
    assert fetcher.fetch('https://acme.test')
    assert fetcher.fetch('https://acme.test')
    assert len(calls)==2
    assert web.HTTPFetcher(max_bytes=5,retries=0).fetch('https://acme.test') is None

def test_cli_configured_semantic_defaults(monkeypatch,tmp_path,capsys):
    import web_research
    model=Model()
    monkeypatch.setattr(web_research,'default_search_provider',lambda:Search())
    monkeypatch.setattr(web_research,'HTTPFetcher',lambda:Fetch())
    monkeypatch.setattr(OpenAICompatibleProvider,'from_env',classmethod(lambda cls,prefix='RESEARCH_LLM':
        (model,None) if prefix=='RESEARCH_LLM' else (None,'not configured')))
    code=main(['--company','Acme','--live','--max-queries','40','--max-rounds','3','--output',str(tmp_path/'configured')])
    assert code==2
    assert 'Semantic extractor: CONFIGURED' in capsys.readouterr().err
    result=json.loads((tmp_path/'configured/result.json').read_text())
    assert any(c['status']=='FACT' for c in result['atomic_claims'])
    assert result['research_opportunities'] and result['candidate_event_concepts']
    assert 'EpistemicStatus.' not in (tmp_path/'configured/summary.md').read_text()

def test_provider_priority_and_invalid_config(monkeypatch,tmp_path,capsys):
    from web_research import default_search_provider, BraveSearchProvider, TavilySearchProvider, DuckDuckGoHTMLSearchProvider
    monkeypatch.setenv('BRAVE_SEARCH_API_KEY','fake')
    monkeypatch.setenv('TAVILY_API_KEY','fake')
    assert isinstance(default_search_provider(),BraveSearchProvider)
    monkeypatch.delenv('BRAVE_SEARCH_API_KEY')
    assert isinstance(default_search_provider(),TavilySearchProvider)
    monkeypatch.delenv('TAVILY_API_KEY')
    assert isinstance(default_search_provider(),DuckDuckGoHTMLSearchProvider)
    assert main(['--company','Acme','--max-queries','0','--output',str(tmp_path/'bad')])==1
    assert 'max_queries must be a positive integer' in capsys.readouterr().err
    folder=tmp_path/'existing';folder.mkdir();(folder/'keep').write_text('retain')
    assert main(['--company','Acme','--output',str(folder)])==1
    assert (folder/'keep').read_text()=='retain'

def test_unknown_alone_is_not_useful_source_research():
    from agent_os import Node,NodeGraph
    from research_runtime import ResearchRuntime
    from research_contracts import AtomicClaim
    ex,_,_=setup()
    ex.extract_claims=lambda doc,qs:[AtomicClaim('unknown:'+doc.source_id,qs[0].target_fields[0],
        'Unknown',EpistemicStatus.UNKNOWN,subject_id=qs[0].subject_id)]
    g=NodeGraph();n=Node('company:a','Acme',node_type='company',completion_gate='company');g.add(n)
    rt=ResearchRuntime(g,{'research_executor':ex})
    _,records=rt.execute(n,[ResearchQuestion('q','Acme identity',('identity',),True)])
    assert records[0]['sources_opened'] and records[0]['status']=='NO_RELEVANT_EVIDENCE'
