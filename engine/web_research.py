"""Live search + scraping executor with strict source grounding.

Search/fetch is observable. An extractor may only promote claims from fetched excerpts, and a
validator rejects facts whose quoted evidence does not occur in the fetched page. Only public
http(s) pages are fetched.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlencode, urlparse, parse_qs, unquote
import hashlib, html, ipaddress, json, os, re, socket, time
import urllib.error, urllib.request

from research_contracts import AtomicClaim, EpistemicStatus, EvidenceAnchor, SourceRef, SourceTier
from research_executor import (DiscoveredEntity, EvidenceCandidate, ExtractionResult, GroundedExtractor,
    ResearchExecutor, SearchResult, SourceDocument as RuntimeDocument)

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
        if any(marker in page.lower() for marker in ('anomaly.js','anomaly-modal','bots use duckduckgo')):
            raise ValueError('DuckDuckGo blocked automated search; configure BRAVE_SEARCH_API_KEY or TAVILY_API_KEY')
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
    def __init__(self): super().__init__(); self.parts=[]; self._skip=0; self.title=""; self._in_title=False; self._links=[]
    def handle_starttag(self,tag,attrs):
        if tag in {"script","style","noscript","svg"}: self._skip+=1
        if tag=="a" and not self._skip:
            href=dict(attrs).get('href','')
            self._links.append(href if href.startswith(('https://','http://')) else '')
        if tag=="title": self._in_title=True
        if tag in {"p","div","li","h1","h2","h3","br","tr"} and not self._skip: self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in {"script","style","noscript","svg"} and self._skip: self._skip-=1
        if tag=="a" and not self._skip and self._links:
            href=self._links.pop()
            if href: self.parts.append(' ('+href+')')
        if tag=="title": self._in_title=False
        if tag in {"p","div","li","h1","h2","h3","tr"} and not self._skip: self.parts.append("\n")
    def handle_data(self,data):
        if self._skip: return
        if self._in_title: self.title+=data
        self.parts.append(data)

def _safe_url(url):
    p=urlparse(url)
    if p.scheme not in {'http','https'} or not p.hostname or p.username or p.password:return False
    if p.hostname.lower() in {'localhost','localhost.localdomain'} or p.hostname.endswith('.local'):return False
    try:
        addresses=socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM)
        return bool(addresses) and all(ipaddress.ip_address(a[4][0]).is_global for a in addresses)
    except (ValueError,OSError):return False

class _SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not _safe_url(newurl):raise ValueError('redirect to non-public address rejected')
        return super().redirect_request(req,fp,code,msg,headers,newurl)

class HTTPFetcher:
    def __init__(self, timeout=15, max_bytes=4_000_000, min_domain_interval=.3, retries=2):
        self.retries=retries
        self.timeout=timeout; self.max_bytes=max_bytes; self.min_domain_interval=min_domain_interval; self._cache={}; self._last_domain_fetch={}
    def fetch(self,url):
        if url in self._cache: return self._cache[url]
        for attempt in range(self.retries+1):
            doc = self._fetch_once(url)
            if doc is not None: return doc
            if attempt < self.retries: time.sleep(min(2**attempt,4))
        self._cache[url] = None
        return None

    def _fetch_once(self,url):
        if url in self._cache: return self._cache[url]
        if not _safe_url(url): return None
        domain=(urlparse(url).hostname or "").lower(); elapsed=time.monotonic()-self._last_domain_fetch.get(domain,0.0)
        if elapsed<self.min_domain_interval: time.sleep(self.min_domain_interval-elapsed)
        req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html,text/plain,application/xhtml+xml"})
        try:
            with urllib.request.build_opener(_SafeRedirect()).open(req,timeout=self.timeout) as r:
                ctype=r.headers.get_content_type()
                if ctype not in {"text/html","text/plain","application/xhtml+xml"}: return None
                raw=r.read(self.max_bytes+1)
                if len(raw)>self.max_bytes: return None
                charset=r.headers.get_content_charset() or "utf-8"; body=raw.decode(charset,"ignore"); status=getattr(r,"status",200)
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
    if domain.endswith(".gov"): return SourceTier.TIER_1_PRIMARY
    if domain.endswith(".edu"): return SourceTier.TIER_3_CONTEXT
    if any(domain==x or domain.endswith("."+x) for x in REPUTABLE_NEWS): return SourceTier.TIER_2_REPUTABLE
    if any(domain==x or domain.endswith("."+x) for x in CONTEXT_DOMAINS): return SourceTier.TIER_3_CONTEXT
    return SourceTier.TIER_4_DISCOVERY

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
        claims,entities=[],[]
        for candidate in candidates:
            for field_name in question.target_fields:
                pattern=self.FIELD_PATTERNS.get(field_name)
                names=[]
                if field_name=='discovered_entity':
                    names=[m.group('name').strip() for rx in self.DISCOVERY_ENTITY_PATTERNS
                           for m in rx.finditer(candidate.excerpt)]
                if not names and (not pattern or not pattern.search(candidate.excerpt)):
                    continue
                cid=hashlib.sha256((question.subject_id+field_name+candidate.source.url+candidate.excerpt).encode()).hexdigest()[:24]
                # A keyword match is retrieved evidence, not proof of a company need, buyer, or fit.
                claim=AtomicClaim('scrape:'+cid,field_name,candidate.excerpt,EpistemicStatus.EVIDENCE,
                    sources=(candidate.source,),subject_id=question.subject_id,
                    quote_or_excerpt=candidate.excerpt,observed_at=candidate.source.retrieved_at,
                    anchors=(EvidenceAnchor(candidate.source.url,candidate.excerpt,candidate.source.content_sha256),))
                claims.append(claim)
                for name in names:
                    entities.append(DiscoveredEntity('company',name,
                        evidence_claim_ids=(claim.claim_id,),relationship='REQUIRES_RELEVANCE_RESEARCH'))
        return ExtractionResult(claims,entities)

class StrictGroundingValidator:
    """Use the same shared evidence intake, including inference support and source-tier checks."""
    def validate(self,result,document,context_claims=()):
        from research_bridge import EvidenceMemory
        memory=EvidenceMemory()
        # Context is already accepted by ResearchRuntime; only used to validate inference links here.
        memory.claims.update({c.claim_id:c for c in context_claims})
        from evidence_graph import Claim
        memory.findings.update({c.claim_id:Claim(c.claim_id,c.statement) for c in context_claims})
        memory.remember_source(document)
        accepted,rejected=[],[]
        for c in result.claims:
            try:
                c=replace(c,source_id=document.source_id)
                memory.accept(c,document);accepted.append(c)
            except (ValueError,TypeError,AttributeError) as exc:
                rejected.append({'claim_id':getattr(c,'claim_id',None),'reason':str(exc)})
        ids={c.claim_id for c in accepted}
        entities=[e for e in result.discovered_entities if e.evidence_claim_ids and set(e.evidence_claim_ids)<=ids]
        return ExtractionResult(accepted,entities,result.notes),rejected

class ScrapingResearchExecutor:
    """Explicit opt-in HTTP adapter; conservative excerpt extraction cannot complete business gates.

    Supply a GroundedExtractor for reviewed atomic facts/inferences and relevant entity proposals.
    The default preserves keyword-matched excerpts as EVIDENCE, never fabricates field answers.
    """
    def __init__(self,search_provider=None,fetcher=None,extractor=None,max_results_per_query=8,
                 max_documents_per_query=5,excerpts_per_document=5):
        self.search_provider=search_provider or default_search_provider()
        self.fetcher=fetcher or HTTPFetcher()
        self.extractor=extractor or RuleBasedGroundedExtractor()
        self.validator=StrictGroundingValidator()
        self.max_results_per_query=max_results_per_query
        self.excerpts_per_document=excerpts_per_document
        self._questions={};self._entities={};self.rejections=[]

    def search(self,query):
        hits=self.search_provider.search(query.query,self.max_results_per_query)
        for hit in hits:self._questions[hit.url]=query
        return [SearchResult(h.url,h.title,h.snippet) for h in hits]

    def open_source(self,result):
        raw=self.fetcher.fetch(result.url)
        if raw is None:raise ValueError('source unavailable or unsupported media')
        q=self._questions[result.url]
        official=q.preferred_domains[0] if q.preferred_domains else None
        source=SourceRef(raw.url,raw.title,classify_source(raw.url,official),source_type='scraped_web',
                         retrieved_at=raw.retrieved_at,content_sha256=raw.content_sha256)
        sid=hashlib.sha256((raw.url+raw.content_sha256+str(source.tier)).encode()).hexdigest()
        return RuntimeDocument(sid,source,raw.text,raw.retrieved_at)

    def extract_claims(self,document,questions):
        q=questions[0]
        raw=SourceDocument(document.source.url,document.source.title,document.text,
                            document.observed_at,document.source.content_sha256)
        candidates=[EvidenceCandidate(hashlib.sha256((q.question_id+excerpt).encode()).hexdigest(),
            q.question_id,q.target_fields,document.source,excerpt,score,q.negative_query)
            for excerpt,score in relevant_excerpts(raw,q,self.excerpts_per_document)]
        proposed=self.extractor.extract(q,candidates,{'subject_id':q.subject_id,
            'accepted_claims':q.context_claims,'official_domain':q.preferred_domains[0] if q.preferred_domains else None})
        self.last_extraction_notes = proposed.notes
        valid,rejected=self.validator.validate(proposed,document,q.context_claims)
        self.rejections.extend(rejected)
        self._entities[document.source_id]=valid.discovered_entities
        # Pass rejected proposals back to the central intake as well, so the full run trace records
        # every rejection rather than concealing adapter filtering.
        rejected_ids={r['claim_id'] for r in rejected}
        return valid.claims+[replace(c,source_id=document.source_id) for c in proposed.claims if c.claim_id in rejected_ids]

    def discover_entities(self,document,claims,context):
        accepted_ids={c.claim_id for c in claims}
        return [e for e in self._entities.get(document.source_id,[]) if set(e.evidence_claim_ids)<=accepted_ids]

def build_default_web_executor(extractor=None):
    return ScrapingResearchExecutor(extractor=extractor)
