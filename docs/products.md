# Products and Buyers

The event produces one behavioral substrate. Four products sell off it.

| Customer | What they buy |
|---|---|
| Sponsors | Access to high-value activations and challenges |
| Product teams | Structured research + experiments |
| Employers | Permissioned, evidence-based recruiting |
| VCs | Opted-in builder and team discovery |
| Innovation teams | Prototypes and R&D challenges |
| Developer platforms | Adoption and developer research |
| Brands | Activation + behavioral campaign measurement |

## 1. Sponsor research

Covered in [research-framework.md](research-framework.md). The anchor product.

## 2. Recruiting — work evidence, not résumés

> ⚠️ **Read [recruiting-legal.md](recruiting-legal.md) before building this.** FCRA restricts the
> candidate artifact to first-hand observation of your own event — no GitHub history, no Club OS
> longitudinal data, no third-party evidence. And it must never emit a score or ranking.

Instead of *"here's a résumé book of 200 elite students,"* a permissioned work-evidence pool:

```
CANDIDATE A

Role interest
  Software engineering

Evidence
  • built backend for a 3-person product
  • shipped working deployment in 22 hours
  • owned auth integration
  • resolved two production blockers
  • artifact available
  • teammates collaborated through completion

Project outcome
  working product

Recruiting visibility
  opted in
```

Against *"CS student, 3.8 GPA, Python."*

The employer still makes the hiring decision. We supply evidence of actual work, not a score
and not a ranking. That distinction matters legally as well as ethically — the moment the
platform outputs a ranked employability number, it is an assessment tool and inherits a
regulatory surface (NYC LL 144, Illinois AI Video Interview Act, EU AI Act's employment tier)
that evidence presentation does not. Keep it descriptive.

### Challenge-specific recruiting

A sponsor that wants infrastructure engineers doesn't buy a generic prize. They define the
challenge:

> Build an observability tool using real streaming data.

Now the work itself is the relevant evidence:

```
Employer requirement:   Infrastructure + Debugging + SystemsThinking
maps to:                ChallengeBehavior + Artifact + Outcome
```

Far stronger than keyword matching, and the participants are self-selected into the domain.

## 3. VC — team discovery

A VC doesn't want everyone who ticked "entrepreneur." They want to know **who actually builds.**

```
TEAM X

3 students · MIT / Cornell / Berkeley
Built:            AI developer infrastructure
Hackathon:        MVP shipped
After 30 days:    continued
After 90 days:    1,800 users
Team history:     2 members previously collaborated
Artifacts:        available
```

Opt-in only. This is early startup discovery with a behavioral track record attached — prior
collaboration history is a signal almost nothing else in the market has.

## 4. R&D — paid follow-on work

The interaction shouldn't end when a sponsor spots an interesting team.

```
Hackathon → PaidFollowOnProject
```

- $10K–$50K for a student team to continue building or testing something
- a 6-week design partnership
- prototype a new API integration
- test a beta product

This turns the network into outsourced student R&D, and gives participants a genuine upside
that makes the front-end offer stronger. It also introduces employment/IP questions — who owns
what a team builds in a paid follow-on, and whether these are contractor relationships — that
should be settled in the participant agreement before the first one happens.

## 5. The experimentation marketplace

The end state. A company submits a question:

> Will developers use feature X?

The system selects ~50 relevant student developers, designs the experiment, runs the
challenge/testing environment, captures behavior + feedback + outcome, and returns a
recommendation.

At that point the hackathon is just one format alongside 2-week sprints, beta groups, startup
challenges, recruiting challenges, and semester R&D programs.

## Packaging

Pricing should follow what is actually bought, not a flat sponsor tier sheet:

```
Basic sponsorship        →  event visibility + activation
Research sponsorship     →  custom experiment + report
Recruiting sponsorship   →  challenge + opt-in talent evidence
R&D partnership          →  custom prototypes / teams
Annual network partner   →  continuous experiments across events
```

Contracts can be materially larger than ordinary hackathon sponsorship because the problem being
solved is materially more valuable. Any specific numbers discussed so far are illustrative, not
validated pricing.

## Why ~200 elite builders

Not prestige. The selection creates a commercially useful experimental panel — a population
disproportionately containing future engineers, future founders, technical early adopters,
high-value recruiting candidates, and developer-tool users.

And it stratifies:

```
TechnicalBuilder · Founder · Product · Designer · BusinessBuilder
```

The tradeoff to stay honest about: this panel is deliberately unrepresentative. Findings
generalize to elite student builders and early adopters — a genuinely important segment for
developer tools, and the wrong panel for questions about the median developer. Sell it as what
it is; sponsors who need general-population data will find out either way.
