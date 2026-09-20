# Research Framework

Every sponsor study follows the same architecture. That sameness is the point — it is what makes
this a platform instead of a series of bespoke consulting engagements.

```
Goal → Decision → Unknowns → Hypotheses → Experiment → Evidence → Model → Recommendation
```

## Experiment record

Stored per experiment, versioned:

| Field | |
|---|---|
| `sponsor_objective` | What they want to be true |
| `business_question` | The decision this informs |
| `hypothesis` | Stated before the event, not after |
| `population` | Which participants are in scope |
| `treatment` | The exposure condition |
| `control` | Comparison group where one is possible |
| `features` | Covariates captured |
| `outcome_variables` | What counts as success |
| `experiment_version` | Designs change between events |
| `decision_time` | When the sponsor needs the answer |
| `results` · `confidence` · `recommendation` | Output |
| `limitations` | Stated, not buried |

Pre-registering the hypothesis matters more than it sounds. Without it, every study finds
something, and sponsors eventually notice that the findings are unfalsifiable.

## Behavioral funnel

The reporting unit. Not vanity metrics.

```
Exposure → Activation → UsefulAction → RepeatedUse → VoluntaryReuse → Retention
```

Illustrative shape:

```
150  exposure
117  activated
 92  completed a meaningful action
 71  used it again during the event
 48  voluntarily used it after the event
 31  still active at 30 days
```

Each step needs a written, event-backed definition before the event runs — "meaningful action"
is a decision, not an observation, and it must be fixed in advance or it becomes a dial that
gets turned until the report looks good.

## Model specifications

Start simple: logistic regression, Bayesian models, gradient boosting. Not a large neural
network — n is in the hundreds per event, the covariates are interpretable, and sponsors are
buying explanation rather than prediction.

**Adoption**
```
P(Adopt) = f( Product, Participant, Experience, Track, Friction, Team, Context )
```

**Retention**
```
P(Retain_30d) = f( Activation, EarlyBehavior, FeatureUsage, ProjectType, Friction, InitialValue )
```

**Recruiting**
```
P(Interview) = f( WorkEvidence, RoleFit, Artifacts, TeamExecution, RecruiterInterest )
```

Sample-size honesty: a single event yields tens of participants per experiment arm, not
thousands. Early reports should lead with effect direction, friction diagnosis, and qualitative
mechanism, and be explicit that precise effect sizes need several events. Overclaiming
statistical confidence on n=72 is the fastest way to lose a sophisticated sponsor.

## Qualitative layer

Telemetry says *they switched after 24 minutes.* It does not say *why.*

Pair behavior with post-task surveys, short interviews, optional voice responses, team
retrospectives, sponsor interviews, and project reviews.

Then code free text into structured friction records:

```
"I couldn't figure out how auth worked"
"I got stuck setting up permissions"
"The docs were confusing"

        ↓

friction_type: authentication_setup
severity:      high
stage:         onboarding
```

Which lets qualitative themes enter the quantitative model:

```
AuthenticationFriction → ActivationProbability ↓ 28%     (illustrative)
```

The coding step is where an AI layer earns its place — consistent thematic extraction across
hundreds of open responses, with human review of the codebook.

## Sponsor deliverable

Not photos. A findings report:

```
SPONSOR: Company X

QUESTION
Why aren't elite student developers retaining Product X?

EXPERIMENT
187 participants · 72 relevant builders
required onboarding, then free tool choice

FINDINGS
Activation           81%
Meaningful usage     59%
Voluntary reuse      43%
30-day retention     21%

MAIN FRICTION
1. onboarding   2. docs   3. auth   4. pricing uncertainty

SEGMENT DIFFERENCES
AI founders          higher adoption
backend engineers    higher retention
first-time founders  lower activation

RECOMMENDATION
Simplify first-project flow + improve auth documentation + target segment X first
```

Underneath: projects built, interviews, representative quotes, telemetry, statistical
confidence, and methodological limitations.

## Category intelligence

Across many events, longitudinal data products emerge:

```
ToolChoice(category, t)
AdoptionTrend(category, t)
SwitchingMatrix
DeveloperPreference
```

This answers questions no single sponsor can ask alone — which cloud provider student startups
choose unconstrained, what causes A→B switching, which models technical founders actually use.
Sold as aggregate intelligence, never as identifiable student histories.
