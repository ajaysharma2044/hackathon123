# How Real Hackathons Are Run — the evidence base

What the operational design in [`docs/event-ops/`](.) is grounded in. This is a **sourced** survey
of how elite and well-run hackathons actually organize, staff, judge, and run — separated honestly
into what is **KNOWN** (sourced from organizer guides and real events) and what is **our design
choice** for a Cornell-only premium fly-in. It follows the repo's discipline: evidence is not the
same as a decision ([STATE.md](../STATE.md)), and comparables are a starting point, not a template
([event-comps.md](../event-comps.md)).

## The canonical sources

| Source | What it is | What we take |
|---|---|---|
| **MLH Hackathon Organizer Guide** (guide.mlh.com) | the de-facto standard playbook, used by hundreds of collegiate events | committee structure; the science-fair **judging formula**; mentorship dispatch; logistics checklists |
| **hackathon.guide** | a widely-cited independent organizer guide | budget per-person, venue/wifi/power specifics, volunteer roles, run-of-show, safety |
| **Devpost** docs + judging guides | the dominant submission/judging platform | rubric criteria; submission flow; science-fair vs panel |
| **HackMIT** (organizer accounts) | elite, student-run via the TechX group | a ~20-person student org; one lead owns sponsorship |
| **Hack the North** (Canada's largest) | elite, functional-team org | team taxonomy: logistics, dev, design, internal ops, sponsorship, marketing |
| **TreeHacks** (Stanford) · **Cal Hacks** (Berkeley) | the premium fly-in model closest to Event 1 | funded, **admission-blind** travel; selective admission; scale + prize norms |

> Citations are to the organizations' public organizer guides and event/organizer write-ups as of
> 2026. Numbers are theirs; where we adapt them we say so.

## KNOWN — sourced operational facts

### Organization & committee structure
- **MLH model:** a single **Lead Organizer** over functional teams — **Logistics** (venue, schedule,
  swag, prizes, food), **Finance/Sponsorship** (sponsor $$, vendor payment, budget), **Marketing**
  (promotion, website, social), and **Operations** (the hacker experience). Extended committees add
  **Tech/AV, Design, Participant Experience, Judging & Awards, Mentorship, Safety**. *(MLH guide,
  "Build Your Leadership Team")*
- **HackMIT:** run by the student group **TechX**, with an organizing team of **~20** members, a
  single lead owning sponsorship. *(HackMIT organizer account)*
- **Hack the North:** roles in **Logistics, Frontend/Backend Dev, Graphic/Product Design, Internal
  Operations, Sponsorship, Marketing.** *(Hack the North)*
- One person is made accountable per team; work is tracked in a PM tool (Trello/Notion/Asana).

### Mentors
- Three models: **vertical** (1+ mentor assigned per team), **horizontal** (a shared pool any team
  can pull from), and **mixed.** Newcomer mentoring groups run roughly **1:2 to 1:6.** *(MediaWiki
  hackathon handbook; MLH mentorship)*
- Dispatch is usually **chat-based**: a `#mentorship` channel + an `@mentor` role so hackers know
  where to ask and mentors where to look; mentors get **shift slots** but are encouraged to be
  present throughout; **office hours** for group Q&A. Recruit from **TAs/tutors, alumni, industry,
  professors.** *(MLH mentorship)*
- Mentor role types: **product**, **project-manager**, **presentation** mentors. *(nonprofit-hackathon practice)*

### Judging
- **Science-fair format is the MLH recommendation:** hackers stay at assigned **tables/stations**,
  judges **rotate** through projects; run it **in person** to reduce chaos. *(MLH judging plan)*
- **Judge-count formula:** `J = ⌈(P × n × t) / T⌉` — projects × rounds × minutes-per-project ÷
  judging-window. **MLH defaults: n = 3 rounds, t = 4 min** (2 demo + 1 Q + 1 travel). Worked
  reference: **175 projects in a 2-hour window → 18 judges.** *(MLH judging plan)*
- **Stack ranking, not absolute scores:** each judge ranks their **top 3 → 3/2/1 points**, summed
  across judges, to normalize strict vs lenient judges. *(MLH judging plan)*
- Total judging **2–3 hours**; **finals ≈ 7 min/team** (3–5 min pitch + ~2 setup). One **diverse
  panel** judges all eligible projects on the same criteria; **category/sponsor prizes** are judged
  by subject-matter experts over only the tagged projects. *(MLH; Devpost)*
- Common **rubric criteria** (published in advance): technical complexity, creativity/originality,
  potential impact, execution/UX, presentation. *(Devpost)*

### Logistics & budget
- **Budget:** professional venue **$10–30/person** in a major city; **food $7–15/person**; order
  catering **3+ days ahead**; vegetarian/dairy-free **mandatory**, vegan/gluten-free considered.
  *(hackathon.guide)*
- **Venue:** **one power strip per table**; WiFi load-tested for all participants and **not blocking
  ports**; projector + mic; hacking at **~10-seat tables**, classroom setup for workshops;
  **gender-neutral single-occupancy bathrooms** preferred; AC for after-hours; **30 min
  setup/teardown**. *(hackathon.guide)*
- **Registration:** free community events see ~**65% show-up**, so cap registration at **~150% of
  capacity**. (For a premium fly-in this inverts — see below.) *(hackathon.guide)*
- **Team size 2–5**; workshop helper ratio **1 per 10–20** participants; ~**25% of stated goals** is
  a realistic accomplishment; environments should set up in **<20 min**. *(hackathon.guide)*
- **Volunteers:** registration/check-in, front-door (rotating shifts), floaters/runners,
  photography/social, workshop support, documentation; identify **~10 days prior**. *(hackathon.guide)*
- **Safety:** a **public Code of Conduct** (MLH has a standard one), an **emergency plan**, and
  **accessibility** are table stakes. *(MLH policies; hackathon.guide)*

### The premium fly-in model (closest to Event 1)
- **TreeHacks:** **flies in** top builders, reimburses travel for **every** competitor; **~7%**
  acceptance of **>15,000** applicants; **1,000+** competitors on **378** teams; **$500K+** prizes;
  marquee keynotes. *(TreeHacks)*
- **Cal Hacks:** **regional travel-stipend caps**; the stipend is an **optional** application
  question and is **admission-blind** — applying for it does **not** affect acceptance. *(Cal Hacks
  travel page)*

## Our design choices for a Cornell-only premium event (NOT sourced — decisions)

Where we deliberately diverge from the comps, and why:

| Dimension | Comp norm | Event 1 choice | Why |
|---|---|---|---|
| Scale | TreeHacks ~1,000; MLH events 150–1,500 | **~150–200** | research power + cost + experience optimum ([event1-design.md](../event1-design.md)) |
| Admission | selective (TreeHacks ~7%) | **curated, Cornell-only**, stratified | a clean, reachable, same-campus cohort ([measurement.md](../measurement.md)) |
| Travel | fly-in nationally | **mostly regional**, funded, **admission-blind** | Cornell-only keeps travel cheap; admission-blind is the Cal Hacks rule, enforced in schema |
| Organizers | all-student (HackMIT ~20) | **two orgs**: event + **research** | the research instrument is the differentiator; it needs its own director + steward |
| Judging | science-fair + finals | **same**, + the artifact feeds research | adopt the proven format wholesale; it doubles as artifact capture |
| Mentors | sponsor volunteers, 1:2–1:6 | **mixed model, ~1:10 elite**, logged in ≤20s | help-first, but the log is a disclosed friction signal ([../research-ops/mentor-system.md](../research-ops/mentor-system.md)) |
| Registration | 150% cap (65% show) | **~100% + waitlist** | a funded fly-in inverts the no-show math: accepted ≈ attend |
| Data | most events collect little beyond Devpost | the **Live Research OS** | the whole thesis ([../research-ops/live-research-os.md](../research-ops/live-research-os.md)) |

## What the comps do NOT tell us (the honest gaps)
- **Exact staff-to-hacker ratios at the 150–200 premium tier** are not published; our
  [`staffing_model.py`](../../engine/staffing_model.py) ratios are reasoned from the pieces above
  (mentor 1:10, volunteer 1:20, field-researcher 1:28, the judge formula), not lifted from one source.
- **How a research instrument interleaves with operations** has no comparable — no elite hackathon
  runs a live, consented research OS underneath. That interlock ([role-correlations.md](role-correlations.md))
  is the novel part, and therefore the part with the least external precedent and the most to learn
  by running Event 1.

## Sources

- [MLH Hackathon Organizer Guide — Build Your Leadership Team](https://guide.mlh.com/general-information/build-your-leadership-team)
- [MLH Hackathon Organizer Guide — Judging Plan](https://guide.mlh.com/general-information/judging-and-submissions/judging-plan)
- [MLH Hackathon Organizer Guide — Mentorship](https://guide.mlh.io/general-information/mentorship)
- [hackathon.guide](https://hackathon.guide/)
- [Devpost — Understanding submission and judging criteria](https://info.devpost.com/blog/understanding-hackathon-submission-and-judging-criteria)
- [What is it like to organize HackMIT? (Katie Siegel)](https://medium.com/hackmit-2014/what-is-it-like-to-organize-hackmit-96467ee9a9b8)
- [Hack the North](https://ca.linkedin.com/company/hack-the-north)
- [What does it take to attend the best hackathon in the world? (TreeHacks)](https://medium.com/@hackwithtrees/what-does-it-take-to-attend-the-best-hackathon-in-the-world-f400041d68d3)
- [Cal Hacks Travel Stipends](https://apply.calhacks.io/travel)
- [MediaWiki Hackathons Handbook — Mentoring program](https://www.mediawiki.org/wiki/Hackathons/Handbook/Mentoring_program)
