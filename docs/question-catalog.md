# Question Catalog — First Cut

The highest-Value-of-Information questions a hackathon economy can answer unusually well, scored
by [engine/score.py](../engine/score.py). This is a **first, evidence-grounded cut** built from the
buyer evidence already in the repo ([buyer-needs.md](buyer-needs.md), [who-pays-for-research.md](who-pays-for-research.md),
[asset-monetization.md](asset-monetization.md)) — **not** a new company sweep. Broadening to
100–300 companies is the deliberate scale-up.

**Every WTP below is a rational *ceiling* derived from decision value — an estimate, never an
observed price. WTP stays UNKNOWN until the pre-sell test returns a signed number.**

Scores are ordinal HIGH/MED/LOW/NONE. `HackathonAdvantage = min(Naturalness, BlindSpot)` is the
kill gate: if it's below MED, the question is answerable without us and is **killed regardless of
budget.** The killed list at the bottom is as important as the pursue list — it is the filter
working.

---

## PURSUE

### Q1 — Do developer startup credits create *retained* usage, or subsidize *temporary* activation?
> The single strongest question found. It is the user's own headline example, and the evidence backs it.

- **Decision owner:** Head of Startup Program / Growth (AWS Activate, Google Cloud for Startups,
  Datadog for Startups, Anthropic/OpenAI startup programs, MongoDB for Startups).
- **Economic worth:** credit programs run to tens of millions — AWS up to $200K/startup, Google up
  to $350K, Microsoft up to $150K, Datadog up to $100K. The *allocation* decision across thousands
  of startups is the multi-million-dollar call. `[asset-monetization.md]`
- **How they answer it now:** their own telemetry on credited accounts. They cannot isolate the
  counterfactual or see past the program window.
- **Why their data fails:** selection bias (they only see who took credits), no counterfactual
  (would these builders have used it without the credit?), and no post-credit horizon.
- **What hackathon activity answers it:** vary credit amount as an incentive arm across otherwise
  comparable builders; observe activation vs 30/90-day retention *after the artificial incentive
  disappears*; capture the unconstrained baseline (who uses it with no credit at all).
- **Experiment/observation required:** randomize credit tier where ethical (a genuine RCT arm);
  `ChoiceSet` + `economic_transaction` record incentive→activation; follow-up separates prize-driven
  from genuine use.
- **Follow-up:** 30/90-day is the entire point — the finding lives in the post-incentive gap.
- **Rational WTP ceiling (estimate, not price):** high — it can rationally change a $10–350K/startup
  × N allocation. **WTP: UNKNOWN.**
- **Scores:** EconDecision HIGH · Uncertainty HIGH · ResearchSpend HIGH · **BlindSpot HIGH** ·
  **Naturalness HIGH** · Observability HIGH · Feasibility MED · Longitudinal HIGH · Repeat HIGH ·
  Authority HIGH → **PURSUE.** HackathonAdvantage HIGH.

### Q2 — What do strong builders reach for when unconstrained — and why us vs competitor X?
- **Owner:** PMM / Product Research / DevRel leadership (any devtool with real competitors).
- **Worth:** positioning + roadmap + competitive-response decisions.
- **Now:** telemetry sees their own users; Vercel observed 60% switched providers in six months
  with no recorded why; Datadog states in print its data can't see non-adopters.
- **Why it fails:** the counterfactual chooser — the developer who picked a competitor — is
  structurally invisible to first-party telemetry.
- **Hackathon activity:** greenfield teams choosing among simultaneously-available tools; the
  `ChoiceSet` primitive records the alternatives so choice ≠ preference is resolvable.
- **Required:** observational (self-selected) → L1/L2; a `ChoiceSet`-conditioned choice model.
- **Follow-up:** 30-day for whether the choice stuck.
- **WTP ceiling:** high. **UNKNOWN.**
- **Scores:** all HIGH except Feasibility MED (observational) → **PURSUE.** HackathonAdvantage HIGH —
  nobody can observe non-choosers naturally.

### Q3 — Does our AI coding/workflow product actually increase output, vs self-report?
- **Owner:** AI-lab platform research / Product Research.
- **Worth:** product + positioning; a category-wide open question nobody can self-answer.
- **Now:** self-report surveys — which METR showed are wrong (devs 19% *slower* while feeling 20%
  faster); own telemetry can't isolate output causally.
- **Why it fails:** no vendor can credibly publish that its own tool slows people; self-report is
  invalidated by the METR result; Anthropic ("can't measure real-world outcomes") and Cognition
  ("unsolved problem in our field") say so publicly. `[buyer-needs.md]`
- **Hackathon activity:** randomize an AI-workflow condition on a *narrow* sub-task; measure
  artifact/task-completion/time with matched effort; blinded outcome coding.
- **Required:** the rare L3 (occasionally L4) — the one place our environment reaches quasi-causal.
- **WTP ceiling:** high; the **neutral-party** advantage is the moat — no competitor can run this
  credibly on itself. **UNKNOWN.**
- **Scores:** EconDecision HIGH · Feasibility MED-HIGH (rare randomizable) · Naturalness MED-HIGH →
  **PURSUE.**

### Q4 — Where does sandbox/test → working prototype break for our API, and why?
- **Owner:** Growth / Product (Stripe, Modern Treasury, Plaid, Checkout.com).
- **Worth:** activation drives revenue; Stripe publishes the 20% of Atlas startups who charged in
  30 days and nothing about the other 80%; Modern Treasury names KYB latency as a deal-killer but
  can't size it. `[buyer-needs.md]`
- **Why their data fails:** telemetry stops at their edge; the abandonment *mechanism* is unseen.
- **Hackathon activity:** observe the full integration attempt through to a working prototype;
  brokered test-vs-prod distinction; post-error micro-prompts at the freshest moment.
- **⚠️ Honest caveat:** hackathon "production" is a working prototype, not true production — the
  finding is about the *integration funnel to shipping*, and the report must say so.
- **Follow-up:** 7/30-day for continuation.
- **Scores:** EconDecision HIGH · BlindSpot HIGH · Naturalness HIGH · Observability HIGH →
  **PURSUE**, caveated.

### Q5 — Which stack do greenfield technical teams choose from zero, before procurement constrains them?
- **Owner:** data/cloud/infra PMM + startup program (Snowflake, Databricks, MongoDB, Supabase, Neon, Confluent).
- **Worth:** early greenfield adoption becomes later enterprise spend; the choice happens *before*
  procurement — exactly the window their enterprise-sales data can't see.
- **Hackathon activity:** teams form greenfield and select a stack under a recorded `ChoiceSet`;
  dependency manifests are the honest record of what was actually wired in.
- **Follow-up:** 30/90-day for whether the greenfield stack persisted.
- **Scores:** → **PURSUE.** HackathonAdvantage HIGH — greenfield-from-zero is literally what happens.

---

## CANDIDATE (real, not flagship)

### Q6 — What triggers a switch away from us mid-build, and what makes adoption stick?
Owner: PMM/Growth. Compressed timeline + multiple tools make `TOOL_SWITCHED` (triangulated) + a
post-switch prompt observable in a way normal usage isn't. L1/L2. Retention direction from 30/90d.
**CANDIDATE → PURSUE** if paired with Q2.

### Q7 — What is the real, decomposed ROI of developer-event and startup-credit spend?
Owner: DevRel leadership / Growth / startup-program lead — the people the evidence shows are told to
"define and defend" these metrics (Databricks) and produce "not vanity metrics" (Sentry). The
`sponsor_economics` decomposition (inputs → activated → meaningful → retained 30/90) *is* the
answer. **CANDIDATE**, and the highest-`Repeatability` question — it recurs every event and is the
meta-product that could seed the year-round panel.

### Q8 — When an agent (not a human) is the API user, how does that change infra selection?
Owner: AI-infra product (Render, Neon, Supabase, Modal). Exploratory (L1 only — no baseline exists
anywhere). High uncertainty, emerging, genuinely unanswerable elsewhere, but low feasibility today.
**CANDIDATE**, flagged exploratory.

---

## KILL — answerable without a hackathon (the filter working)

These score high on budget or decision size but **fail HackathonAdvantage** — a panel, telemetry,
or Gartner answers them as well or better. Pursuing them would be selling a research product we
don't have.

| Question | Why killed |
|---|---|
| "What does the *median* developer think of X?" | Elite cohort ≠ median; a representative panel (Harris/Censuswide) does this better and cheaper. Naturalness LOW. |
| "What is tool X's industry market share?" | SlashData/telemetry already measure this at 12,500+ dev scale. BlindSpot LOW. |
| "Which vendor will enterprise *procurement* standardize on?" | Wrong population entirely — procurement doesn't happen at a hackathon; the builders aren't the enterprise buyer. Naturalness NONE. |
| "Long-run brand awareness / perception" | A brand tracker is cheaper and better-powered. Naturalness LOW. |
| "Enterprise pricing willingness for $100K+ contracts" | Wrong population; students don't hold enterprise budget. Naturalness NONE. |
| "Find security vulnerabilities in our product at scale" | A real bug-bounty program does this better and cheaper — it's an activation, not a research question. Reframe, don't sell as research. |

---

## What this first cut suggests about the ICP

The PURSUE set clusters, and the cluster *is* the ICP — discovered from the questions, not assumed:

> **A developer-facing company that spends real money to acquire early-stage builders (credits,
> startup program, free tier) and is making an allocation or product decision about that spend,
> where the deciding behavior — unconstrained choice, post-incentive retention, greenfield stack
> selection, integration-to-shipping — happens before or outside its own telemetry.**

That points less at "the biggest AI lab" and more at **companies running credit/startup programs
who cannot prove those programs work** (Q1 + Q7), and at **competed devtools who cannot see their
non-choosers** (Q2 + Q5). Both are exactly the blind spots a compressed builder economy is built to
illuminate — and both are testable with the same instrument, which is what makes the multi-client
economics real.

**Next:** score 100–300 companies against these question templates to find which specific buyers own
these decisions right now (trigger-dated), then take the sharpest one into the pre-sell test.
