from research_contracts import AtomicClaim,CompletionGate,EpistemicStatus,EvidenceAnchor,GateRequirement,ResearchCoverage,SourceRef,SourceTier,COMPANY_COMPLETION_GATE

def src(tier=SourceTier.TIER_1_PRIMARY,domain="example.com"): return SourceRef(f"https://{domain}/source","Example source",tier)
def fact(cid,field,tier=SourceTier.TIER_1_PRIMARY,domain="example.com"):
    s=src(tier,domain); text=f"supported {field}"; return AtomicClaim(cid,field,text,EpistemicStatus.FACT,(s,),(EvidenceAnchor(s.url,text),),confidence=.9)
def test_fact_requires_source_and_anchor():
    try: AtomicClaim("c","funding","raised",EpistemicStatus.FACT); assert False
    except ValueError: pass
    s=src()
    try: AtomicClaim("c2","funding","raised",EpistemicStatus.FACT,sources=(s,)); assert False
    except ValueError: pass
def test_inference_requires_supporting_claim_ids():
    try: AtomicClaim("i","event_value_chain","x",EpistemicStatus.INFERENCE); assert False
    except ValueError: pass
def test_negative_search_can_complete_without_finding_counterevidence():
    g=CompletionGate("x",(GateRequirement("need"),),negative_search_fields=("need",)); c=ResearchCoverage(searched_fields={"need"},negative_searched_fields={"need"}); assert g.evaluate([fact("n","need")],coverage=c).complete
def test_company_gate_refuses_missing_negative_search():
    claims=[]; cov=ResearchCoverage()
    for i,r in enumerate(COMPANY_COMPLETION_GATE.requirements):
        if EpistemicStatus.FACT in r.allowed_statuses: claims.append(fact(f"c{i}",r.field)); cov.searched_fields.add(r.field)
        elif EpistemicStatus.INFERENCE in r.allowed_statuses: claims.append(AtomicClaim(f"i{i}",r.field,f"inferred {r.field}",EpistemicStatus.INFERENCE,supporting_claim_ids=("c0",)))
    out=COMPANY_COMPLETION_GATE.evaluate(claims,coverage=cov); assert not out.complete; assert "internal_capability" in out.missing_negative_search
def test_primary_validation_is_not_completion():
    g=CompletionGate("wtp",(GateRequirement("wtp"),)); out=g.evaluate([AtomicClaim("p","wtp","priced ask needed",EpistemicStatus.PRIMARY_VALIDATION_REQUIRED)]); assert not out.complete and out.primary_validation==["wtp"]
