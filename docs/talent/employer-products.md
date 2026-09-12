# Employer Product Catalog (Part LII) + Buyer-Role Value (Part LIV)

The seven employer-facing products the talent market supports, and which hiring role each serves.
Every product sits on the same substrate — opt-in, decomposed, score-free work-evidence — and differs
only in packaging. Pricing entries are **comparables cited from repo docs, not observed WTP**. WTP for
every product below is **UNKNOWN** until a signed check (`docs/STATE.md`).

Vocabulary: **Evidence ≠ Claim ≠ Hypothesis ≠ Decision**; **KNOWN / LIKELY / UNKNOWN / CONTRADICTED**;
⚠️ unverified/secondary. Missing ≠ bad.

## Constraints every product inherits

From `docs/recruiting-legal.md`, the eight design rules apply to all seven products:

1. **Sell access, not outcomes** — subscription/sponsorship, not per-hire. Mirrored in
   `opportunity_market.MONETIZATION`: `TALENT_ACCESS_SUBSCRIPTION` is **ALLOWED** ("the safer
   structure"); `RECRUITING_PARTNERSHIP` and `PLACEMENT_SUCCESS_FEE` are **NEEDS_LEGAL**.
2. **Never charge a student** — the employment-agency trigger in CA (§1812.501), MA (c.140 §46A), NY
   (GBL §171).
3. **First-hand event observation only** — FCRA §1681a(d)(2)(A)(i) safe harbor. No GitHub/longitudinal
   data in the candidate artifact.
4. **Never a score, ranking, tier, or classification** — keeps you outside NYC LL144's "simplified
   output," EU AI Act "evaluation of candidates," and UGESP's "selection procedure." Enforced by
   `compliance.FORBIDDEN_SCORES` and the absence of any `overall_score` in `talent_matching`.
5. **The employer makes and documents every hiring decision.**
6. **Never put a candidate on payroll** (the line into staffing).
7. **Assume Title VII employment-agency status** (42 U.S.C. §2000e(c)) regardless of fee.
8. Any success fee: flat $5K–$20K, employer-paid, licensed in placement states — or accept it may be
   unenforceable.

---

## 1. Event Talent Partner

- **Buyer:** a sponsor who wants first look at the event's opted-in talent pool.
- **Alternative today:** hackathon sponsorship whose top "data" benefit is a mailing list —
  `docs/research-pricing.md` notes even KubeCon Diamond ($235,000) delivers only an opt-in attendee
  registration list, not structured evidence.
- **Deliverable:** access to the opted-in work-evidence pool for the event (`talent_matching.retrieve`
  over participants with `opted("EMPLOYER")`), plus the participant hub surfacing
  (`opportunity_market.participant_opportunity_hub` → `EmployerInterest`).
- **Participant benefit:** exposure only if they opt in; the hub always includes `ParticipantValue`
  and states "The participant chooses which opportunities to pursue; nothing is auto-shared."
- **Pricing comparable (cited):** student-access packages cluster $5K–$27K — CMU Student Career
  Sponsor **$10,000/two semesters**; ⚠️ Stanford Computer Forum **$27,000/yr** (secondary,
  JS-rendered, unverified — `docs/research-pricing.md`). Do not anchor above this band on access alone.
- **Legal constraints:** rules 1, 2, 3, 4 (`recruiting-legal.md`). Access framing, employer-paid.
- **Capacity:** one event's opted-in pool (~200 participants, of whom an **UNKNOWN** fraction opt in).
- **WTP:** **UNKNOWN.**

## 2. Role-Specific Search

- **Buyer:** a recruiter filling a specific req.
- **Alternative today:** RippleMatch, Handshake, Symplicity — student sourcing platforms.
- **Deliverable:** structured `JobRequirement` (`job_requirements.py`) → `talent_matching.retrieve`
  returns a **decomposed** match per opted-in participant across `MATCH_DIMS`, each with a `why` list
  and honest `unknowns`. **No `overall_score`** (rule 4). The `JobRequirement.__post_init__` runs
  `compliance.assert_no_sensitive` over every capability/domain/technology/family — sensitive
  attributes cannot enter the search at all.
- **Participant benefit:** only opted-in participants are returned (`retrieve` gates on
  `pv.opted("EMPLOYER")`); the participant can also run the search in reverse for themselves
  (`participant_side_matches`).
- **Pricing comparable (cited):** RippleMatch **$68,622 avg** ($40K–$132,600) — "the single most
  relevant comp"; Handshake TES ~$29,835; Untapped $24,150 (`recruiting-legal.md`). Published seat
  pricing: Handshake Pro $450/mo, Symplicity $55/post/school.
- **Legal constraints:** rule 4 above all — retrieval, not ranking; rules 1, 3.
- **Capacity:** unbounded queries against the opted-in pool.
- **WTP:** **UNKNOWN.**

## 3. Work Evidence Access

- **Buyer:** a hiring manager who wants to *see the work*, not a resume.
- **Alternative today:** a resume book (`docs/products.md` contrasts "here's a résumé book of 200
  elite students" against a permissioned work-evidence pool), plus coding-assessment scores.
- **Deliverable:** the work-evidence graph for opted-in participants — `evidence_for_scope(evidence,
  "EMPLOYER")` returns only Level-C, employer-opted evidence, rendered via `render_claim` as
  provenance statements. This is the packet in `evidence-packets.md`.
- **Participant benefit:** per-scope control; missing evidence never held against them
  (`neutral_when_missing`, `missing = None`).
- **Pricing comparable (cited):** the assessment vendors it displaces — Karat **$175,695**,
  CodeSignal $24,394, HackerRank $13,099 (`recruiting-legal.md`). Those sell a score; this sells
  observed work instead, so the comps bound the budget, not the deliverable.
- **Legal constraints:** rule 3 (first-hand only — the FCRA firewall the A/B/C levels enforce) and
  rule 4 (no score). This is the product `recruiting-legal.md` was written to protect ("Read this
  before building the work-evidence product").
- **Capacity:** the opted-in pool.
- **WTP:** **UNKNOWN.** (Recruiting has the more quantified adjacent WTP — ~$35K cost-to-hire,
  hackathon hiring ~$5–10K/hire, `docs/STATE.md` — but the check is unsigned.)

## 4. Hiring Challenge

- **Buyer:** a sponsor/hiring manager who defines the work the role actually needs.
- **Alternative today:** generic take-home + keyword screen. `docs/products.md`: "A sponsor that
  wants infrastructure engineers doesn't buy a generic prize. They define the challenge… Now the work
  itself is the relevant evidence."
- **Deliverable:** a challenge whose `job_capability_requirement` rows (SQL) map to the challenge, so
  participants self-select into the domain and their build *is* the evidence; matched via the same
  decomposed `talent_matching.match` (`domain_relevance`, `artifact_relevance`, `capability_coverage`).
- **Participant benefit:** self-selected into a domain they chose; opt-in still gates disclosure.
- **Pricing comparable (cited):** sits between research-challenge sponsorship and recruiting — anchor
  against the recruiting comps in rows 2–3 rather than the $5–27K access band, because a defined
  challenge is a deliverable, not a room.
- **Legal constraints:** rules 3, 4, 5 — the challenge produces artifacts and narrative, never a
  ranked tier of applicants (that would be a UGESP "selection procedure," `recruiting-legal.md`).
- **Capacity:** per-challenge cohort (the self-selected subset).
- **WTP:** **UNKNOWN.**

## 5. Paid Project Marketplace

- **Buyer:** a company wanting outsourced, scoped student R&D. `docs/products.md`: "$10K–$50K for a
  student team to continue building or testing something."
- **Alternative today:** contractor marketplaces, in-house prototyping.
- **Deliverable:** a `paid_project` record (SQL: `scope_of_work`, `duration_weeks`, `ip_terms`,
  `compensation_note`) reached through `PAID_PROJECT` opt-in scope and the `PaidProjectOpportunities`
  hub category. Any resulting evidence carries `source_kind = PAID_CONTINUATION`.
- **Participant benefit:** genuine paid upside; `compensation_note` "clarified before continuation"
  (SQL comment, Part LXI).
- **Pricing comparable (cited):** $10K–$50K per team-continuation (`docs/products.md`, explicitly
  "illustrative, not validated pricing").
- **Legal constraints:** `opportunity_market.MONETIZATION["PAID_PROJECT_FACILITATION"]` is
  **NEEDS_LEGAL** — "clarify IP + worker classification before facilitating paid work." Rule 6 (never
  put the candidate on payroll — the staffing line). IP and contractor-classification questions must
  be settled in the participant agreement first (`docs/products.md`).
- **Capacity:** limited by teams willing to continue; **UNKNOWN**.
- **WTP:** **UNKNOWN.**

## 6. Design-Partner-to-Hire

- **Buyer:** a company that wants a working relationship (design partnership) that can convert.
- **Alternative today:** cold recruiting; ad-hoc trials.
- **Deliverable:** the `DESIGN_PARTNER` visibility scope (`compliance.VISIBILITY_SCOPES`) — a
  distinct opt-in, independent of `EMPLOYER` — plus `DesignPartnerInterest` in the hub. An intro flows
  through the same `mutual_intro` mutual-opt-in gate; conversion to hire is a downstream, participant-
  reported `employment_outcome`.
- **Participant benefit:** a lower-commitment path with real work; still fully opt-in and revocable.
- **Pricing comparable (cited):** a 6-week design partnership (`docs/products.md`); price against the
  paid-project band ($10K–$50K) plus recruiting comps if it converts.
- **Legal constraints:** rules 1, 5, 6, 8. If conversion carries any success fee,
  `MONETIZATION["PLACEMENT_SUCCESS_FEE"]` is **NEEDS_LEGAL** — "legal but commercially weak and
  regulated." Flat $5K–$20K, employer-paid, licensed in placement states if unavoidable.
- **Capacity:** small (design partnerships are high-touch).
- **WTP:** **UNKNOWN.**

## 7. Annual Access

- **Buyer:** a company wanting continuous access across events (a network partner).
- **Alternative today:** annual research/recruiting subscriptions.
- **Deliverable:** subscription to opted-in discovery across events — the `TALENT_ACCESS_SUBSCRIPTION`
  monetization kind, the one `opportunity_market.assert_monetization_allowed` returns **ALLOWED** as
  "access/subscription, not per-hire — the safer structure."
- **Participant benefit:** recurring, opt-in exposure; participant hub control unchanged.
- **Pricing comparable (cited):** RedMonk **$7,500–$20,000+/yr**, Wynter Pro/Elite
  **$20,000–$40,000/yr** (`docs/research-pricing.md`) as annual-partner analogs; RippleMatch's
  $68,622 average annual contract as the recruiting-side anchor (`recruiting-legal.md`).
- **Legal constraints:** the cleanest structure — sell access, not outcomes (rule 1). Still rules 3, 4.
- **Capacity:** recurring across the event calendar.
- **WTP:** **UNKNOWN.**

---

## Buyer-role value (Part LIV)

Which of the three hiring roles values these products, and how strongly.

| Role | What they value | Best-fit products | Status |
|---|---|---|---|
| **Recruiter** | Top-of-funnel sourcing at volume; a filled req | Role-Specific Search, Event Talent Partner, Annual Access | **LIKELY** as a fit; WTP **UNKNOWN** |
| **Hiring manager** | Seeing the actual work; a defined challenge in their domain | Work Evidence Access, Hiring Challenge, Design-Partner-to-Hire, Paid Project | **LIKELY** the strongest fit — they defined the challenge and want the evidence; WTP **UNKNOWN** |
| **University recruiting** | Campus pipeline, brand, early-career funnel | Event Talent Partner, Annual Access | **CONTRADICTED** as a funder — `docs/STATE.md`: "Will a University Recruiting Lead fund this? CONTRADICTED (NACE: ~$2,850/school median budget)." |

The hiring manager is the most natural buyer of the differentiated products (Work Evidence Access,
Hiring Challenge) because they are the one who wants the *work*, not a filtered list — and, having
defined the challenge, they map their own requirement onto `ChallengeBehavior + Artifact + Outcome`
(`docs/products.md`). The recruiter buys the sourcing layer. University recruiting is a poor funder on
the published budget evidence and should not be the anchor buyer.

Across all three roles, one thing is constant: **the product is evidence, never a decision.** Every
match `explain()` ends "This is evidence-based retrieval, not a hiring recommendation," and the
employer "makes and documents every hiring decision" (rule 5).
