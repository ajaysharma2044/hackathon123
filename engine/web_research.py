"""Live search + scraping executor with strict source grounding.

Search/fetch is observable. An extractor may only promote claims from fetched excerpts, and a
validator rejects facts whose quoted evidence does not occur in the fetched page. Only public
http(s) pages are fetched.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode, urlparse, parse_qs, unquote
import hashlib, html, ipaddress, json, os, re, socket, time
import urllib.error, urllib.request

from research_contracts import AtomicClaim, EpistemicStatus, EvidenceAnchor, SourceRef, SourceTier
from research_executor import DiscoveredEntity, EvidenceCandidate, ExtractionResult, GroundedExtractor, ResearchBatch, ResearchExecutor

UA = "Mozilla/5.0 (compatible; hackathon123-research/2.0; evidence-first)"
REPUTABLE_NEWS = {"reuters.com","bloomberg.com","ft.com","wsj.com","cnbc.com","apnews.com","techcrunch.com","theinformation.com","axios.com"}
CONTEXT_DOMAINS = {"linkedin.com","crunchbase.com","wellfound.com","greenhouse.io","lever.co"}

@dataclass(frozen=True)
class SearchHit:
    title: str; url: str; snippet: str = ""; rank: int = 0

@dataclass(frozen=True)
class SourceDocument:
    url: str; title: str; text: str; retrieved_at: str; content_sha256: str; status_code: int = 200; content_type: str = "text/html"

class SearchProvider:
    def search(self, query: str, limit: int = 8) -> list[SearchHit]: raise NotImplementedError

class BraveSearchProvider(SearchProvider):
    def __init__(self, api_key: str): self.api_key = api_key
    def search(self, query: str, limit: int = 8):
        url = "https://api.search.brave.com/res/v1/web/search?" + urlencode({"q": query, "count": min(limit,20)})
        req = urllib.request.Request(url, headers={"Accept":"application/json","X-Subscription-Token":self.api_key,"User-Agent":UA})
        with urllib.request.urlopen(req, timeout=15) as r: payload = json.loads(r.read().decode("utf-8","ignore"))
        return [SearchHit(x.get("title") or x.get("url",""), x.get("url",""), x.get("description",""), i) for i,x in enumerate(payload.get("web",{}).get("results",[])[:limit]) if x.get("url","").startswith(("http://","https://"))]

class TavilySearchProvider(SearchProvider):
    def __init__(self, api_key: str): self.api_key = api_key
    def search(self, query: str, limit: int = 8):
        body = json.dumps({"api_key":self.api_key,"query":query,"max_results":limit,"search_depth":"advanced"}).encode()
        req = urllib.request.Request("https://api.tavily.com/search", data=body, headers={"Content-Type":"application/json","User-Agent":UA})
        with urllib.request.urlopen(req, timeout=20) as r: payload = json.loads(r.read().decode("utf-8","ignore"))
        return [SearchHit(x.get("title") or x.get("url",""), x.get("url",""), x.get("content",""), i) for i,x in enumerate(payload.get("results",[])[:limit]) if x.get("url","").startswith(("http://","https://"))]

class DuckDuckGoHTMLSearchProvider(SearchProvider):
    _RESULT_RE = re.compile(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.I|re.S)
    def search(self, query: str, limit: int = 8):
        req = urllib.request.Request("https://html.duckduckgo.com/html/?" + urlencode({"q":query}), headers={"User-Agent":UA})
        with urllib.request.urlopen(req, timeout=15) as r: page = r.read(2_000_000).decode("utf-8","ignore")
        out=[]
        for i,m in enumerate(self._RESULT_RE.finditer(page)):
            raw_url=html.unescape(m.group(1))
            if raw_url.startswith("//"): raw_url="https:"+raw_url
            p=urlparse(raw_url)
            if "duckduckgo.com" in (p.hostname or "") and p.path.startswith("/l/"):
                target=parse_qs(p.query).get("uddg",[""])[0]; raw_url=unquote(target) if target else raw_url
            title=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",html.unescape(m.group(2)))).strip()
            if raw_url.startswith(("http://","https://")): out.append(SearchHit(title or raw_url,raw_url,"",i))
            if len(out)>=limit: break
        return out

def default_search_provider():
    if os.getenv("BRAVE_SEARCH_API_KEY"): return BraveSearchProvider(os.environ["BRAVE_SEARCH_API_KEY"])
    if os.getenv("TAVILY_API_KEY"): return TavilySearchProvider(os.environ["TAVILY_API_KEY"])
    return DuckDuckGoHTMLSearchProvider()

class _TextParser(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self._skip=0; self.title=""; self._in_title=False
    def handle_starttag(self,tag,attrs):
        if tag in {"script","style","noscript","svg"}: self._skip+=1
        if tag=="title": self._in_title=True
        if tag in {"p","div","li","h1","h2","h3","br","tr"} and not self._skip: self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in {"script","style","noscript","svg"} and self._skip: self._skip-=1
        if tag=="title": self._in_title=False
        if tag in {"p","div","li","h1","h2","h3","tr"} and not self._skip: self.parts.append("\n")
    def handle_data(self,data):
        if self._skip: return
        if self._in_title: self.title+=data
        self.parts.append(data)

def _safe_url(url):
    p=urlparse(url)
    if p.scheme not in {"http","https"} or not p.hostname: return False
    host=p.hostname.lower()
    if host in {"localhost","localhost.localdomain"} or host.endswith(".local"): return False
    try:
        ip=ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved: return False
    except ValueError: pass
    return True

class HTTPFetcher:
    def __init__(self, timeout=15, max_bytes=4_000_000, min_domain_interval=.15):
        self.timeout=timeout; self.max_bytes=max_bytes; self.min_domain_interval=min_domain_interval; self._cache={}; self._last_domain_fetch={}
    def fetch(self,url):
        if url in self._cache: return self._cache[url]
        if not _safe_url(url): return None
        domain=(urlparse(url).hostname or "").lower(); elapsed=time.monotonic()-self._last_domain_fetch.get(domain,0.0)
        if elapsed<self.min_domain_interval: time.sleep(self.min_domain_interval-elapsed)
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,text/plain,application/xhtml+xml"})
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as r:
                ctype=r.headers.get_content_type()
                if ctype not in {"text/html","text/plain","application/xhtml+xml"}: return None
                raw=r.read(self.max_bytes+1)[:self.max_bytes]; charset=r.headers.get_content_charset() or "utf-8"; body=raw.decode(charset,"ignore"); status=getattr(r,"status",200)
        except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError,socket.timeout,ValueError): return None
        finally: self._last_domain_fetch[domain]=time.monotonic()
        if ctype in {"text/html","application/xhtml+xml"}:
            parser=_TextParser(); parser.feed(body); title=re.sub(r"\s+"," ",parser.title).strip() or url
            text="\n".join(re.sub(r"\s+"," ",x).strip() for x in "".join(parser.parts).splitlines() if x.strip())
        else: title=url; text=body
        text=text[:1_500_000]; digest=hashlib.sha256(text.encode()).hexdigest(); doc=SourceDocument(url,title,text,datetime.now(timezone.utc).isoformat(timespec="seconds"),digest,status,ctype); self._cache[url]=doc; return doc

def classify_source(url,official_domain=None):
    domain=(urlparse(url).hostname or "").lower().removeprefix("www."); official=(official_domain or "").lower().removeprefix("www.")
    if official and (domain==official or domain.endswith("."+official)): return SourceTier.TIER_1_PRIMARY
    if domain.endswith(".gov") or domain.endswith(".edu"): return SourceTier.TIER_1_PRIMARY
    if any(domain==x or domain.endswith("."+x) for x in REPUTABLE_NEWS): return SourceTier.TIER_2_REPUTABLE
    return SourceTier.TIER_3_CONTEXT

def _tokens(text): return {x for x in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}",text.lower()) if x not in {"the","and","with","from","that","this","company","latest"}}

def relevant_excerpts(doc,question,limit=6):
    q=_tokens(question.query); chunks=[c.strip() for c in re.split(r"\n+|(?<=[.!?])\s+(?=[A-Z])",doc.text) if 45<=len(c.strip())<=1200]; scored=[]
    for chunk in chunks:
        overlap=len(q&_tokens(chunk))
        if overlap: scored.append((chunk,overlap/max(3,len(q)**.5)))
    scored.sort(key=lambda x:(-x[1],len(x[0]))); return scored[:limit]

class RuleBasedGroundedExtractor(GroundedExtractor):
    FIELD_PATTERNS={
        "identity":re.compile(r"\b(company|founded|headquartered|platform|provides|develops|builds)\b",re.I),
        "current_initiative":re.compile(r"\b(launch(?:ed|es)?|announc(?:ed|es)|expand(?:ed|s|ing)?|release(?:d|s)?|partnership|new product)\b",re.I),
        "financial_capacity":re.compile(r"\b(raised|funding|financing|investment|revenue|valuation|cash|series [a-z])\b",re.I),
        "product_business_model":re.compile(r"\b(api|sdk|pricing|subscription|customers?|platform|product|developer|enterprise|usage-based)\b",re.I),
        "strategic_need":re.compile(r"\b(hiring|recruit(?:ing)?|grow(?:th|ing)?|expan(?:d|sion)|adoption|developer|research|product feedback)\b",re.I),
        "internal_capability":re.compile(r"\b(user research|ux research|research team|developer relations|devrel|lab|university recruiting|community team|benchmark)\b",re.I),
        "buyer_function":re.compile(r"\b(product|growth|developer relations|devrel|research|innovation|recruiting|engineering leadership|community)\b",re.I),
        "substitute":re.compile(r"\b(user panel|customer advisory|hackathon|innovation challenge|university program|consult(?:ant|ing)|internal research|developer program)\b",re.I),
        "economic_problem":re.compile(r"\b(shortage|constraint|cost|bottleneck|failure|risk|spending|demand|capacity|latency|productivity)\b",re.I),
        "cornell_fit":re.compile(r"\b(cornell|university|students?|campus|research lab|engineering)\b",re.I),
        "company_ecosystem":re.compile(r"\b(companies|vendors|suppliers|startups|customers|ecosystem|market)\b",re.I),
    }
    DISCOVERY_ENTITY_PATTERNS=(
        re.compile(r"(?P<name>[A-Z][A-Za-z0-9&.+\-]*(?: [A-Z][A-Za-z0-9&.+\-]*){0,4})\s+(?:has\s+)?(?:raised|raises|secured|announced|launched|develops|builds)\b"),
        re.compile(r"(?:startup|company|firm)\s+(?P<name>[A-Z][A-Za-z0-9&.+\-]*(?: [A-Z][A-Za-z0-9&.+\-]*){0,4})\b"),
    )
    def extract(self,question,candidates,context):
        claims,entities=[],[]; official=(context.get("official_domain") or "").lower(); seen=set()
        for candidate in candidates:
            if "discovered_entity" in question.target_fields:
                for rx in self.DISCOVERY_ENTITY_PATTERNS:
                    for m in rx.finditer(candidate.excerpt):
                        name=re.sub(r"\s+"," ",m.group("name")).strip(" ,.-")
                        if len(name)<2 or name.lower() in {"the company","the startup","series a","series b","series c"}: continue
                        cid=hashlib.sha256(f"discovered_entity|{candidate.source.url}|{candidate.excerpt}|{name}".encode()).hexdigest()[:20]
                        claim=AtomicClaim(f"scrape:{cid}","discovered_entity",candidate.excerpt,EpistemicStatus.FACT,(candidate.source,),(EvidenceAnchor(candidate.source.url,candidate.excerpt,candidate.source.content_sha256),),confidence=min(.8,.5+candidate.relevance*.08))
                        claims.append(claim)
                        if name.lower() not in seen:
                            entities.append(DiscoveredEntity("company",name,relationship="grounded discovery lead from scraped source",evidence_claim_ids=(claim.claim_id,),confidence=claim.confidence)); seen.add(name.lower())
            for field_name in question.target_fields:
                pattern=self.FIELD_PATTERNS.get(field_name)
                if not pattern or not pattern.search(candidate.excerpt): continue
                if field_name=="identity" and official and candidate.source.domain!=official: continue
                cid=hashlib.sha256(f"{field_name}|{candidate.source.url}|{candidate.excerpt}".encode()).hexdigest()[:20]
                claims.append(AtomicClaim(f"scrape:{cid}",field_name,candidate.excerpt,EpistemicStatus.FACT,(candidate.source,),(EvidenceAnchor(candidate.source.url,candidate.excerpt,candidate.source.content_sha256),),confidence=min(.85,.55+candidate.relevance*.08)))
        return ExtractionResult(claims,entities)

class StrictGroundingValidator:
    def validate(self,result,candidates):
        by_url={}; accepted=[]; rejected=[]; accepted_ids=set()
        for c in candidates: by_url.setdefault(c.source.url,[]).append(c)
        for claim in result.claims:
            try:
                if claim.status==EpistemicStatus.FACT:
                    for anchor in claim.anchors:
                        if not any(anchor.excerpt==c.excerpt for c in by_url.get(anchor.source_url,[])): raise ValueError("fact anchor is not an exact fetched candidate excerpt")
                accepted.append(claim); accepted_ids.add(claim.claim_id)
            except Exception as exc: rejected.append(f"{claim.claim_id}: {type(exc).__name__}: {exc}")
        entities=[]
        for entity in result.discovered_entities:
            if entity.evidence_claim_ids and not set(entity.evidence_claim_ids).issubset(accepted_ids): rejected.append(f"entity {entity.canonical_name}: unsupported evidence_claim_ids"); continue
            entities.append(entity)
        return ExtractionResult(accepted,entities,list(result.notes)),rejected

class ScrapingResearchExecutor(ResearchExecutor):
    def __init__(self,search_provider=None,fetcher=None,extractor=None,max_results_per_query=8,max_documents_per_query=5,excerpts_per_document=5):
        self.search_provider=search_provider or default_search_provider(); self.fetcher=fetcher or HTTPFetcher(); self.extractor=extractor or RuleBasedGroundedExtractor(); self.validator=StrictGroundingValidator(); self.max_results_per_query=max_results_per_query; self.max_documents_per_query=max_documents_per_query; self.excerpts_per_document=excerpts_per_document
    def research(self,questions,context):
        batch=ResearchBatch(); official=context.get("official_domain"); seen_urls=set(); seen_claims=set()
        for question in questions:
            batch.queries_run.append(question.query); batch.coverage.queries_run.append(question.query); batch.coverage.searched_fields.update(question.target_fields)
            if question.negative_query: batch.coverage.negative_searched_fields.update(question.target_fields)
            try: hits=self.search_provider.search(question.query,self.max_results_per_query)
            except Exception as exc: batch.notes.append(f"search failed for {question.question_id}: {type(exc).__name__}"); continue
            candidates=[]; opened=0
            for hit in hits:
                if opened>=self.max_documents_per_query: break
                if hit.url in seen_urls: continue
                doc=self.fetcher.fetch(hit.url); seen_urls.add(hit.url)
                if doc is None or not doc.text.strip(): continue
                opened+=1; batch.sources_opened.append(doc.url); batch.coverage.source_urls.add(doc.url); tier=classify_source(doc.url,official)
                source=SourceRef(doc.url,doc.title or hit.title or doc.url,tier,source_type="scraped_web",retrieved_at=doc.retrieved_at,content_sha256=doc.content_sha256)
                for field_name in question.target_fields: batch.coverage.source_domains_by_field.setdefault(field_name,set()).add(source.domain)
                for excerpt,relevance in relevant_excerpts(doc,question,self.excerpts_per_document):
                    cid=hashlib.sha256(f"{question.question_id}|{doc.url}|{excerpt}".encode()).hexdigest()[:20]
                    candidates.append(EvidenceCandidate(f"ev:{cid}",question.question_id,question.target_fields,source,excerpt,relevance,question.negative_query))
            batch.evidence_candidates.extend(candidates)
            if not candidates: continue
            try: result=self.extractor.extract(question,candidates,{**context,"official_domain":official}); valid,rejected=self.validator.validate(result,candidates)
            except Exception as exc: batch.notes.append(f"extractor failed for {question.question_id}: {type(exc).__name__}: {exc}"); continue
            batch.rejected_claims.extend(rejected)
            for claim in valid.claims:
                if claim.claim_id not in seen_claims: batch.claims.append(claim); seen_claims.add(claim.claim_id)
            batch.discovered_entities.extend(valid.discovered_entities); batch.notes.extend(valid.notes)
        return batch

def build_default_web_executor(extractor=None): return ScrapingResearchExecutor(extractor=extractor)
