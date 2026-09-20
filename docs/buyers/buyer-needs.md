# What Buyers Actually Need

The material for opening a sponsor conversation with *their* unknown instead of your event. Every
quote below was pulled from a live job posting or published report — verified at source, not
paraphrased.

## The thesis, now proven twice

Every developer survey in this market samples the sponsor's own audience:

- **Stack Overflow** recruits "primarily through channels owned by Stack Overflow"
- **Vercel**'s was "sourced from the Vercel community"
- **Retool** surveyed "1,128 Retool builders"
- **Grafana** through "outreach to our community"
- **GitHub** Octoverse warns its numbers are "observational signals rather than causal claims"
- **Datadog**, in print: *"the data comes from our customer base, a large but imperfect sample of
  the entire global market... they skew toward adoption of cloud platforms more than the general
  population."*

> **The entire industry makes competitive decisions from data that structurally cannot see the
> developer who chose someone else.**

A category leader (Datadog) states the exact limitation you sell into. That is the syndicated
study, and it is now empirically grounded rather than asserted.

## The budget is not the objection — it points the wrong way

These companies already commission research. **Harris Poll alone is retained by Stripe, Plaid,
Modern Treasury, Alloy, and Unit.** The problem is *who they survey*:

| Company | Their developer-facing product | Who they actually survey |
|---|---|---|
| Marqeta | card-issuing API | **5,000 consumers** |
| Mercury | banking API for founders | 1,500 founders about *money* |
| Confluent | data streaming | 4,625 IT leaders at 500+ employee firms |
| Stripe | payments API | **Developer Coefficient — last refreshed 2018** |

**Stripe commissioned the definitive developer-economics study and hasn't updated it in eight
years** (`stripe.com/reports` now 404s). Not one instrument in the category surveys the
developers and technical founders who actually wire up the product.

## The metric is named. The explanation is missing.

Live job postings, verbatim — each names a first-value metric the team is accountable for:

| Company | The metric, in their words |
|---|---|
| Modern Treasury | "reduce **time-to-first-payment**" |
| Ramp | "**time to first successful spend**" |
| Alloy | "from **first API call to production**" |
| MongoDB | "**time to first successful integration**" |
| Adyen | "contract signature to their **first transaction**" |
| Stripe | "**first successful use of Stripe** as quickly as possible" |
| Brex | "**predict drop-off**" |
| LangChain | "**time to first trace, first evaluation, and production run**" |
| Supabase | "**time to a developer's first migration**" |

They all measure where the funnel *ends up*. None can see why the ones who dropped, dropped —
because their telemetry starts the moment someone already chose them.

## Postings that read as unfunded research briefs

**Anthropic — UX Researcher, Platform ($305,000–$385,000):**
> "User research's job here is to give them a deeper and more systematic understanding of those
> users than they can get on their own." Preferred: "researching **pricing, packaging, or how
> customers decide what a product is worth**, especially for usage-based or developer products."

**Anthropic — Data Scientist, Developer Productivity:**
> "the playbook doesn't exist yet: AI-assisted development is reshaping how engineers work
> **faster than anyone can measure**" — from "is Claude making engineers faster?" to "**what does
> 'faster' even mean here?**"

**Vercel — DevRel Engineer, Agentic Infrastructure ($168–252k):**
> "**Bring the outside in: track how developers across the ecosystem are building agents, where
> they get stuck, and what they're reaching for that doesn't exist yet.**"

**Sentry — Startups Marketing Lead** (the single best find):
> "**Founders and early engineers don't read whitepapers.** Figure out what they do read, watch,
> and share, then put Sentry in front of them." + "Define KPIs that connect startup program
> activity to revenue outcomes – **not vanity metrics.**"

**Databricks — Sr Industry Marketing Manager, Startups:**
> Needs knowledge of "**triggers that accelerate or stop infrastructure and AI platform
> decisions**" and to "improve the conversion of startup evaluations into committed production
> spend."

**Cursor — Product Education Engineer:**
> "**The gap between what Cursor can do and what developers know how to build with it grows with
> every release.**" ⚠️ Cursor was acquired by SpaceX Aug 14 2026 — budget authority likely moved.

**Mercury — Strategic Partnerships Manager, AI/API:**
> "it's not a Developer Relationships role either... this is a category Mercury is still early in
> ... Developers and technical founders see you as **one of them, not as a vendor.**"

## They admit their own instruments are failing

- **Anthropic** (postmortem): telemetry issues were "challenging to distinguish from normal
  variation in user feedback." And: "**we cannot measure real-world outcomes, like whether code
  written in a session is actually used or discarded.**"
- **Cognition**, the same day it launched an "AI Productivity Guarantee": measuring dollar impact
  is "still an **unsolved problem in our field.**"
- **METR RCT**: developers were **19% slower** with AI while estimating they were **20% faster.**
  This single result invalidates self-reported productivity — which is what nearly every vendor
  survey collects.
- **Replit's CEO** defends retention with anecdote: "net retention is incredibly high — 300% in
  some cases." A claim that size defended by anecdote is exactly where independent data sells.

## The newest unknown nobody can measure: the agent as the user

- **Render — Staff Designer, Agent Experience:** "we design for two users at once — developers
  and the agents working on their behalf. **We treat the agent as a first-class customer.**"
- **Neon:** "Agents can create and manage databases without a user ever logging into Neon. No UI,
  no OAuth, no friction."
- **Pinecone** (observed agents using its own SDK): "An agent re-chooses the API on every task...
  A person squints at the rejected-key message. **An agent can't squint.**"
- **Postman:** 89% of developers use AI, but **only 24% design APIs for AI agents**; 70% know MCP,
  **only 10% use it regularly.**

Every one of Render, Neon, Supabase, Modal, and Railway is investing against a hypothesis none of
them can measure.

## Compliance kills fintech projects before launch — and nobody sizes the loss

- **Modern Treasury** BSA/AML Officer: "**KYB slows down onboarding. Transaction monitoring adds
  latency.** Manual KYB review queues don't get faster as volume grows — they get slower."
- **Modern Treasury** Head of Risk req: reach the risk decision "**fast enough that it isn't the
  reason a customer picks someone else.**"
- **Stripe** publishes that "20% of Atlas startups charged their first customer within 30 days, up
  from 8% in 2020." **They publish the 20%. They publish nothing about the other 80%.**

## The syndicated study questions

Recurring across nearly every company, each publicly gestured at, none answerable from their own
telemetry because it only sees the developers who stayed:

1. **What does a developer reach for when unconstrained — and why?** (Four vendor datasets give
   four different answers; all miss intent.)
2. **What actually triggers a switch, and what makes it stick?** (Vercel: 60% switched providers
   in six months, with no explanation.)
3. **How do developers judge model quality in practice — since every vendor now says benchmarks
   don't?** (Cursor, Sourcegraph, Anthropic, Google, Together have all publicly conceded this.)
4. **Where exactly does trust in AI-generated code break, and what restores it?** (46% distrust
   vs 33% trust per SO; everyone has the number, nobody has the mechanism.)
5. **Does pricing or capability drive model choice?** (Published data flatly contradicts itself.)
6. **What does agentic adoption look like in real projects vs. demos?** (52% don't use agents;
   the narrative/practice gap is the category's largest.)
7. **When an agent signs up, who is the customer and how do you count them?**
8. **Why did the builders who didn't choose us not choose us?** (Every dataset begins after
   selection.)
9. **Is our DevRel / startup-program / credits spend working — what's the counterfactual?**
   (Databricks: "define and *defend*" DevRel metrics to executives. Sentry: "not vanity metrics."
   Snowflake: "quantify the business impact." All three want an external baseline they lack.)

## Who to pitch — it is not DevRel

Across full board censuses, **Stripe (634 postings), Block (207), Checkout.com, Marqeta, Airbyte
have zero open DevRel/DX roles.** Pitching "DevRel" pitches a cost centre that may not exist.

The real buyers:

| Door | Evidence |
|---|---|
| **Research Ops / UX Research** | Stripe's Research Ops PM "sources and evaluates third-party vendors... manages SOWs, business terms, and budgets." The literal procurement door. Anthropic Platform UXR. GitHub Customer Research. |
| **Startup-program owners** | Often better funded than DevRel and sits in ventures/growth. MongoDB's runs under **VP, Ventures & Corporate Development**. Stripe Head of Startups. Datadog for Startups. |
| **Growth** | Brex Director of Organic Growth: "We carry a number... own the roadmap, OKRs, and budget." Modal files DevRel under GTM/Growth. LangChain built a 0→1 Growth team. |
| **Product Marketing** | Stripe Head of Market Intelligence; a Stripe PMM req wants "incorporating third-party research (Gartner, Forrester, IDC) into go-to-market." |

## The unclaimed channel

**MLH sells exactly this product** — "access product feedback and insights," reaching "1 in 3 CS
Grads in the US" — and its sponsor list is Google Cloud, Meta, GitHub, Microsoft, MongoDB. **Not
one payments, banking, or fintech-infrastructure company appears.** MongoDB proves the channel
works; the fintech budget exists and the channel is unclaimed.

**DORA (Google Cloud) publicly states: "Sponsorship opportunities are available for upcoming DORA
reports."** A live, named door into the most credible developer study in the world.

## Outreach ranking

1. **Stripe** — open with their own number: *"you publish that 20% of Atlas startups charge within
   30 days; you don't publish why the other 80% didn't."* Research Ops procures vendors; the
   Developer Coefficient is 8 years stale.
2. **Sentry** — the job posting *is* the brief; Head of DevEx seat open now, Startups Marketing
   budget being created.
3. **Adyen** — three DevX director reqs open at once (new org, fresh budget); DevRel charter
   promises "friction with evidence" and has no evidence source.
4. **Databricks / Snowflake** — startup-segment roles already measured on evaluation→production
   conversion; Snowflake writes students and hackathons into DevRel reqs.
5. **Mercury / Brex** — dedicated startup-ecosystem headcount, live event budgets, self-admitted
   blindness to the developer channel.

⚠️ Two name-collision traps for prospecting: `jobs.ashbyhq.com/neon` is a game-monetization
company, not Neon Postgres; `jobs.lever.co/alloy` is Alloy.ai (retail analytics), not the
identity/fraud Alloy at alloy.com.

## Sources

All quotes verified at source via Greenhouse/Ashby ATS APIs and published reports. Key:
[Anthropic UXR Platform](https://job-boards.greenhouse.io/anthropic/jobs/5392007008) ·
[Vercel DevRel Agentic](https://job-boards.greenhouse.io/vercel/jobs/6122437004) ·
[Sentry Startups Marketing](https://jobs.ashbyhq.com/sentry/1b63fc5e-ee6e-42b4-924c-a48836722cba) ·
[Databricks Startups Marketing](https://databricks.com/company/careers/open-positions/job?gh_jid=8638650002) ·
[Datadog State of Serverless](https://www.datadoghq.com/state-of-serverless/) ·
[Stripe Developer Coefficient](https://stripe.com/files/reports/the-developer-coefficient.pdf) ·
[Stripe 2025 update](https://stripe.com/newsroom/news/stripe-2025-update) ·
[Plaid — next 1,000 developers](https://plaid.com/blog/building-for-the-next-thousand-developers/) ·
[MLH sponsor page](https://sponsor.mlh.com/) ·
[DORA](https://dora.dev/) ·
[METR RCT](https://metr.org/) ·
[Stack Overflow 2025 survey](https://survey.stackoverflow.co/2025/)
