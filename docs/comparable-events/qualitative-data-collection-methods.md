---
title: "Hackathon123 -- Qualitative-Data Collection Methods (Sourced Benchmarks)"
type: reference
created: 2026-09-14
tags: [hackathon123, research, qualitative-methods, survey-benchmarks, measurement]
ai-first: true
status: research
confidence: mixed
related-notes:
  - "[[hackathon123 MOC]]"
  - "[[comparable-events-dataset]]"
  - "[[hackathon-benchmarks-trends]]"
sources:
  - "surveymonkey.com -- 2025 response-rate benchmarks"
  - "survicate.com -- 2025 response-rate benchmarks (n=1,025 surveys / 130 companies)"
  - "userinterviews.com, dscout.com, respondent.io -- panel incentive pricing"
  - "Nolte et al. 2025 -- hackathon post-survey template (hackathon-planning-kit.org)"
  - "Imam Mahmoud et al. 2022 -- Empirical Software Engineering 27(7):167"
  - "arXiv:2103.04429 -- programmer self-report validity"
  - "PMC9844858 -- 46-RCT incentive meta-analysis; Gallup 2025; NORC 2025"
---

**Related:** [[hackathon123 MOC]] · [[comparable-events-dataset]] · [[hackathon-benchmarks-trends]]

# Hackathon123 -- Qualitative-Data Collection Methods (Sourced Benchmarks)

## For future Claude

Sourced menu of how comparable programs actually collect qualitative data -- survey channels, paid research panels, in-event/observational methods, longitudinal follow-up, and incentive design -- with real response-rate and cost benchmarks so hackathon123's capture design rests on evidence, not guesses. Every figure carries a retrieved source URL + as-of date + confidence tag; unverifiable items are marked UNKNOWN. This is a secondary research note from the 2026-09-14 comparable-events run; the quantitative event dataset lives in [[comparable-events-dataset]] and the cross-cluster synthesis in [[hackathon-benchmarks-trends]].

> [!important] Sourcing standard
> Confidence tags: **stated** = published by the source org itself · **high** = reputable/peer-reviewed, corroborated · **medium** = single secondary / vendor-blog synthesis · **speculation** = inference, no direct measurement. Undisclosed values are UNKNOWN, never invented. Most survey-channel benchmarks are vendor platform aggregates (general audiences, not developer-specific) -- flagged where it matters.

---

## The one hackathon-specific number that should drive the design

A cold, non-incentivized email survey sent to past hackathon participants after the event returned a **9.86% raw response rate (1,479 of ~11,746 deliverable invites) and only 2.77% usable/complete (416 responses)** -- Imam Mahmoud, Dey, Nolte, Mockus & Herbsleb (2022), *Empirical Software Engineering* 27(7):167, https://pmc.ncbi.nlm.nih.gov/articles/PMC9489595/ (as of 2022-09-20, **high** -- peer-reviewed primary data). This is the single most directly comparable data point found, and it is the core argument for capturing qualitative signal **live and in-platform** rather than by post-hoc outreach.

---

## A. Digital surveys / micro-surveys (low burden)

- **Post-event email survey (opted-in list, single send)** -- satisfaction / NPS / open text. **49.17% avg for opted-in email; 38.81% avg for the "post-event" survey type.** SurveyMonkey 2025 platform aggregate, https://www.surveymonkey.com/learn/survey-best-practices/survey-response-rate-benchmarks/ (**stated**; platform-wide, not developer-specific).
- **Conference/event post-event survey (industry rule of thumb)** -- **10-20% for conferences/corporate events, 12-15% trade shows; 20-30%+ is strong** for engaged audiences. Explori, https://explori.com/blog/what-is-a-good-post-event-survey-response-rate (as of 2021, **stated** but dated -- pre-hybrid-event shift, may be stale).
- **In-app / mobile SDK micro-survey (contextual, in-product)** -- in-the-moment feedback. **34.37% avg (SurveyMonkey 2025 mobile SDK); 18.69% median "Mobile" (Survicate 2025).** https://www.surveymonkey.com/learn/survey-best-practices/survey-response-rate-benchmarks/ + https://survicate.com/reports/survey-response-rate-benchmarks/ (**stated**; two independent vendors converge -- strongest non-panel digital channel).
- **Micro-survey length effect** -- **2-3 question surveys median 15.97% vs 6.87% for 7+ questions.** Survicate 2025 (n=1,025 surveys / 130 companies), https://survicate.com/reports/survey-response-rate-benchmarks/ (**stated**).
- **Passive intercept (popup / widget / in-chat)** -- weakest digital channels. **3.65% avg popup (SurveyMonkey); 7.64% median widget / 5.41% in-conversation (Survicate), 2025.** Same two sources (**stated**). Use only for high-volume passive pulse, not a 200-person cohort where completion matters.
- **SMS/text micro-survey** -- **18.54% avg (SurveyMonkey 2025)**, up to ~50% on transactional prompts per one vendor synthesis (https://frill.co/blog/how-often-to-send-nps, **medium**). Needs opt-in phone numbers; heavier setup for a one-off event.
- **Transactional NPS (within hours of a discrete interaction)** -- **25-40% RR, ~8-12 pts higher than relational.** Zonka, https://www.zonkafeedback.com/blog/nps-survey-response-rates (2026, **medium** -- blog synthesis of CustomerGauge/SurveySparrow claims).
- **Reminder cadence** -- 1st reminder (day 3-5) adds the most; 2nd (~day 7) diminishing; >2 counterproductive. Quackback, https://quackback.io/blog/improve-survey-response-rates (2026, **medium**).

## B. Paid research panels / moderated interviews (medium-high burden, real cost)

- **Moderated remote developer interview (User Interviews)** -- **$100/hr baseline; developers in the $100-150/hr mid-tier; ~70-80% fill, 6-9% no-show at $100/hr.** https://www.userinterviews.com/blog/the-ultimate-guide-to-user-research-incentives (as of 2025-01-02, **stated**, n=25,000+ sessions). All-in cost estimated **$149-298 per completed session** by third-party UserCall (**medium**, not first-party): https://www.usercall.co/post/user-interviews-pricing-in-2025-plus-faster-more-affordable-alternatives
- **Niche technical-specialist panel (dscout / Respondent.io)** -- **dscout: $150-600 for 15-30 min** with a specialist tier; **Respondent.io tech tiers: SWE/Security Admin $100 remote/$200 in-person; UX/Web/Sys Admin $125/$250; Data Analyst/Software Dev $150/$300; Cyber Security Analyst $175/$350** (incentive only; add ~$80-90/recruit sourcing + 3% processing). https://help.dscout.com/usability-tests/what-are-usability-tests-in-dscout/how-much-should-a-usability-test-pay + https://help.respondent.io/en/articles/5471087-what-is-the-correct-incentive-amount-for-my-research-project (2026, **stated**).
- **Unmoderated diary / usability study (dscout)** -- **$10-50 typical incentive**; scales ~$8/task-question + $5 per 3 open-ended. Same dscout source (2026, **stated**). Multi-day diaries raise effective burden.
- **Data-quality risk if sponsors recruit "developers" via open crowds** -- **42% of self-reported programmers on Clickworker failed a validated skill screener.** arXiv:2103.04429 (2021-03-07, **high**, peer-reviewed). Direct argument for hackathon123's pre-vetted panel vs generic panels.

## C. In-event / observational / near-free channels

- **Hackathon judging rubric as structured data (highest-leverage free channel)** -- every project already gets scored. **MLH: ~3 judges, ~3-4 min/project, stack-ranked top-3 = 3/2/1 pts; criteria Technology/Design/Completion/Learning weighted equally.** https://guide.mlh.com/general-information/judging-and-submissions/judging-plan (2026, **stated**). **Devpost: equally-weighted star criteria by default.** https://help.devpost.com/article/64-judging-public-voting (**stated**). Adding one required judge free-text field ("most interesting technical decision," "biggest blocker") yields ~100% submission coverage at zero added participant burden.
- **Contextual inquiry / ethnographic observation (roaming mentors/organizers)** -- captures unspoken workflow vs self-report; **no response-rate or $ benchmark exists** (evaluated on richness/time-cost). NN/G: ~1 hr to several days per session; small-n, researcher-intensive. https://www.nngroup.com/articles/contextual-inquiry/ (2020, **stated** methodological claim). Best as a supplement, not the primary instrument for ~200 people.
- **Validated academic post-hackathon survey (free, reusable)** -- Nolte et al. multi-construct instrument (motivation, team process, satisfaction, continuance intent, belonging, 2 open prompts), reused across 10+ published hackathon studies; authors recommend trimming to relevant sub-scales. https://hackathon-planning-kit.org/files/Nolte-Zenodo-2025.pdf (2025, **stated**). Using it makes results externally comparable to the literature.
- **Mentor office-hours logs** -- team blockers / sponsor-tech usage in real time; **no quantified adoption or signal-quality benchmark found** (Eventornado blog asserts mentored teams submit more but cites no data -- **speculation**). Genuine evidence gap; pilot and measure.
- **Structured exit interview (staffed 1:1 at demo/checkout)** -- rich reaction at peak engagement; **no hackathon-specific participation benchmark found** (UNKNOWN). A captive, staffed ~200-person venue is structurally more favorable than any remote benchmark, but that is inference, not measurement.

## D. Longitudinal follow-up (the 7/30/90-day question)

- **No study directly benchmarks day-7 vs day-30 vs day-90 decay for one population.** Closest proxy: Prolific multi-wave retention on paid online panels -- **weekly-interval waves retained ~1.6x monthly (80% vs 50%); 90% across 30 daily waves (n=300); 82% across 4 weekly waves (n=2,500)**; recommend >=90-day gap before re-surveying absent a new touchpoint. https://www.prolific.com/resources/how-to-maximise-retention-in-longitudinal-studies-reducing-attrition-and-dropout-across-multi-wave-studies (2026-05-13, **stated** for Prolific's own panels -- NOT hackathon alumni, directional only).

## E. Incentive design (cross-cutting lever)

- **Guaranteed small cash beats larger-EV lotteries/vouchers -- three independent sources agree:**
  - 46-RCT meta-analysis: **money RR=1.25 vs control, voucher RR=1.19, lottery RR=1.12.** https://pmc.ncbi.nlm.nih.gov/articles/PMC9844858/ (~2023, **high**; exact date uncertain).
  - Gallup field experiment: **$0 -> 11.8%, $1 -> 26.3%** response (also $1->16.8%, $2->17.4%, $5->21.4% in a separate arm). https://news.gallup.com/opinion/methodology/658832/cash-incentives-affect-survey-response-rates-cost.aspx (2025-04-02, **high**).
  - NORC: **prepaid $5 beat prepaid $2 (14.8% vs 12.5%).** https://www.norc.org/content/dam/norc-org/pdf2025/Research%20Science%20Brief%20Incentive%20Amounts.pdf (2025, **high**).
  - Actionable: a small guaranteed reward (gift card / swag-tier unlock) for completing an exit micro-survey should outperform one big raffle.

---

## Recommendations for hackathon123

1. **Capture live and in-platform, not by post-hoc email.** Cold post-event outreach measured 2.77% usable ([Imam Mahmoud 2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9489595/)); in-app/mobile during an active session runs 18-34% ([SurveyMonkey](https://www.surveymonkey.com/learn/survey-best-practices/survey-response-rate-benchmarks/) / [Survicate](https://survicate.com/reports/survey-response-rate-benchmarks/) 2025). Build feedback into the submission and judging flow.
2. **Make the judging rubric your primary near-free structured channel.** Judging already happens ([MLH](https://guide.mlh.com/general-information/judging-and-submissions/judging-plan), [Devpost](https://help.devpost.com/article/64-judging-public-voting)); one required judge free-text field per project = ~100% coverage at zero added participant burden.
3. **Use the pre-vetted panel as the sponsor-research edge over cold panels.** dscout/Respondent.io charge $150-600 per specialist session and still risk contamination (42% failed a skill screen, [arXiv:2103.04429](https://arxiv.org/abs/2103.04429)). Use captive downtime (lunch, judging queue) for sponsor conversations at swag/raffle-tier cost.
4. **Short, multi-checkpoint micro-surveys over one long form.** 2-3 questions ~16% vs 7+ questions ~7% ([Survicate 2025](https://survicate.com/reports/survey-response-rate-benchmarks/)); deliver in-app/QR (18-34%), not popups/widgets (4-8%).
5. **Design incentives guaranteed-small, not raffle-large** (RR 1.25 cash vs 1.12 lottery; $1 doubled Gallup's response). A small guaranteed reward for the exit micro-survey beats a single big prize.
6. **Adopt the free, peer-validated Nolte et al. template** rather than building from scratch -- comparable to the academic hackathon literature, with a built-in open-ended pair as the richest raw qualitative signal.

---

## Gaps and low-confidence flags

- No single study benchmarks day-7/30/90 decay for one population; Prolific proxy is paid panelists, not hackathon alumni -- treat any 7/30/90 framing as directional.
- Zonka transactional-vs-relational NPS (25-40% vs 15-25%) is a marketing-blog synthesis, not verified primary research.
- Mentor-log and exit-interview participation/completion rates specific to hackathons: no quantified benchmark found anywhere -- must be piloted and measured at our own event.
- Explori conference benchmark (10-20%) is dated 2021 (pre-hybrid shift).
- Typeform's own response-rate page had an inconsistent publish/modified date and conflates response vs completion -- its ~47% figures treated as self-serving vendor claim (medium).
- The 42% programmer-screening-failure stat is one 2021 study of one platform (Clickworker); may not generalize to 2026's AI-assisted survey-fraud landscape.
- The $149-298 all-in User Interviews cost is a third-party estimate (UserCall), not first-party.
- No evidence quantifies burden-vs-signal specifically for developer audiences; general-UX findings applied to elite students is inference.
- The 46-RCT meta-analysis exact publication date is uncertain (PMC index ~2023); the RR findings themselves are high-confidence.
