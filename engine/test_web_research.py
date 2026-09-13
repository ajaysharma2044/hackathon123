"""Scraper integration from the concurrent branch, tested through the granular executor contract."""
import hashlib
from dataclasses import replace
from research_executor import ResearchQuestion, ExtractionResult
from research_contracts import AtomicClaim,EpistemicStatus,EvidenceAnchor
from web_research import SearchHit,SourceDocument,ScrapingResearchExecutor,StrictGroundingValidator

TEXT='Acme announced a new developer platform. Acme raised $100 million in Series C financing.'
class FakeSearch:
    def search(self,query,limit=8):return [SearchHit('Acme announcement','https://acme.test/news','',0)]
class FakeFetcher:
    def fetch(self,url):return SourceDocument(url,'Acme announcement',TEXT,'2026-09-13T00:00:00+00:00',hashlib.sha256(TEXT.encode()).hexdigest())

def opened():
    ex=ScrapingResearchExecutor(search_provider=FakeSearch(),fetcher=FakeFetcher())
    q=ResearchQuestion('q','Acme funding financing',('financial_capacity',),subject_id='company:acme',preferred_domains=('acme.test',))
    hits=ex.search(q);doc=ex.open_source(hits[0]);return ex,q,doc

def test_scraper_produces_exact_anchored_evidence_without_keyword_promotion():
    ex,q,doc=opened();claims=ex.extract_claims(doc,[q])
    assert claims and claims[0].status==EpistemicStatus.EVIDENCE
    assert claims[0].quote_or_excerpt in doc.text
    assert claims[0].anchors[0].content_sha256==hashlib.sha256(TEXT.encode()).hexdigest()

def test_validator_rejects_unfetched_quote():
    ex,q,doc=opened()
    bad=AtomicClaim('bad','financial_capacity','Acme raised $999M',EpistemicStatus.FACT,(doc.source,),
        subject_id=q.subject_id,source_id=doc.source_id,quote_or_excerpt='Acme raised $999M',observed_at=doc.observed_at,
        anchors=(EvidenceAnchor(doc.source.url,'Acme raised $999M'),))
    valid,rejected=StrictGroundingValidator().validate(ExtractionResult(claims=[bad]),doc)
    assert not valid.claims and rejected

def test_fetcher_rejects_private_dns_and_redirect_targets(monkeypatch):
    import web_research as web
    monkeypatch.setattr(web.socket,'getaddrinfo',lambda *a,**kw:[(2,1,6,'',('127.0.0.1',80))])
    assert not web._safe_url('https://public-looking.example/path')
    import pytest
    with pytest.raises(ValueError):web._SafeRedirect().redirect_request(None,None,302,'',{},'http://127.0.0.1/')
