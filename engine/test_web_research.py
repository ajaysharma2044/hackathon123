from research_executor import ResearchQuestion,ExtractionResult,EvidenceCandidate
from research_contracts import AtomicClaim,EpistemicStatus,EvidenceAnchor,SourceRef,SourceTier
from web_research import SearchHit,SourceDocument,ScrapingResearchExecutor,StrictGroundingValidator

class FakeSearch:
    def search(self,query,limit=8): return [SearchHit("Acme announcement","https://acme.test/news","",0)]
class FakeFetcher:
    def fetch(self,url): return SourceDocument(url,"Acme announcement","Acme announced a new developer platform. Acme raised $100 million in Series C financing.","2026-09-13T00:00:00+00:00","abc123")
def test_scraper_produces_exact_anchored_claims():
    ex=ScrapingResearchExecutor(search_provider=FakeSearch(),fetcher=FakeFetcher()); out=ex.research([ResearchQuestion("q","Acme funding financing",("financial_capacity",))],{"official_domain":"acme.test"}); assert out.sources_opened==["https://acme.test/news"] and out.claims; assert out.claims[0].status==EpistemicStatus.FACT
def test_validator_rejects_unfetched_quote():
    s=SourceRef("https://acme.test/news","Acme",SourceTier.TIER_1_PRIMARY); bad=AtomicClaim("bad","financial_capacity","Acme raised $999M",EpistemicStatus.FACT,(s,),(EvidenceAnchor(s.url,"Acme raised $999M"),)); c=EvidenceCandidate("e","q",("financial_capacity",),s,"Acme raised $100M",1.0); valid,rejected=StrictGroundingValidator().validate(ExtractionResult(claims=[bad]),[c]); assert not valid.claims and rejected
