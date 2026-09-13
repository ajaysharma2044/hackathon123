from research_contracts import (
    AtomicClaim, CompletionGate, EpistemicStatus, GateRequirement,
    SourceRef, SourceTier, COMPANY_COMPLETION_GATE,
)


def src(tier=SourceTier.TIER_1_PRIMARY):
    return SourceRef("https://example.com/source", "Example source", tier)


def fact(cid, field, tier=SourceTier.TIER_1_PRIMARY, contradictions=()):
    return AtomicClaim(
        claim_id=cid,
        field=field,
        statement=f"supported {field}",
        status=EpistemicStatus.FACT,
        sources=(src(tier),),
        confidence=0.9,
        contradictory_claim_ids=tuple(contradictions),
    )


def test_fact_requires_source():
    try:
        AtomicClaim("c", "funding", "raised money", EpistemicStatus.FACT)
        assert False, "FACT without source must fail"
    except ValueError:
        pass


def test_discovery_only_source_does_not_satisfy_strong_gate():
    gate = CompletionGate(
        "x", (GateRequirement("funding", max_source_tier=SourceTier.TIER_2_REPUTABLE),),
        require_counterevidence=False,
    )
    out = gate.evaluate([fact("c", "funding", SourceTier.TIER_4_DISCOVERY)])
    assert not out.complete
    assert "funding" in out.weak


def test_company_gate_refuses_incomplete_dossier():
    out = COMPANY_COMPLETION_GATE.evaluate([
        fact("identity", "identity"),
        fact("money", "financial_capacity"),
    ])
    assert not out.complete
    assert "buyer_function" in out.missing
    assert "counterevidence" in out.missing


def test_company_gate_accepts_full_sourced_dossier_with_counterevidence():
    claims = []
    for i, req in enumerate(COMPANY_COMPLETION_GATE.requirements):
        claims.append(fact(f"c{i}", req.field, SourceTier.TIER_2_REPUTABLE))
    claims.append(fact("counter", "counterevidence", SourceTier.TIER_2_REPUTABLE))
    out = COMPANY_COMPLETION_GATE.evaluate(claims)
    assert out.complete


def test_primary_validation_is_not_completion():
    gate = CompletionGate(
        "wtp", (GateRequirement("wtp"),), require_counterevidence=False
    )
    out = gate.evaluate([
        AtomicClaim(
            "wtp_unknown", "wtp", "requires a priced buyer ask",
            EpistemicStatus.PRIMARY_VALIDATION_REQUIRED,
        )
    ])
    assert not out.complete
    assert out.primary_validation == ["wtp"]
