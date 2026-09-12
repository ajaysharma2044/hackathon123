# Concept

## 1. What participants actually experience

Students arrive, get access to sponsor APIs/products/tools, choose or are exposed to challenge
tracks, form teams, build, talk to engineers and founders and recruiters, test ideas, submit,
pitch, and potentially keep working afterward.

To them it is an elite builder weekend. That framing is not marketing — it is a design
constraint. The research layer runs underneath with explicit opt-in and clear consent, and the
event has to survive a participant fully understanding that layer and still wanting to come.

**Failure mode to design against:** an event that feels like a research study masquerading as a
hackathon. Selected builders have options; the moment the instrumentation is the point rather
than a byproduct, the panel self-selects down to people who did not have better offers, and the
commercial value of the population evaporates.

## 2. The sponsor model

### What sponsors normally buy

Logo placement, booth space, résumé book, API prize, workshop, recruiting access.

### What they buy here

We start from the business decision. Examples of real sponsor questions:

| Sponsor type | Question |
|---|---|
| AI lab | Why do strong student developers choose our model over competitors, and what stops more developers building on our API? |
| Payments | Where is the onboarding friction for student founders? |
| Cloud | Which services do students actually choose when completely unconstrained? |
| Design tooling | How do technical founders use collaborative design tools when building fast? |
| Fintech/ops | Which product features resonate most with student founders? |

Each becomes an experiment design.

### The exposure/choice structure

Forcing everyone to use a sponsor product for the whole event destroys the experiment — you
measure compliance, not preference. Instead:

```
REQUIRED EXPOSURE
Every relevant participant completes a real task with Product A
        ↓
FREE CHOICE
Participant may use any tool for the rest of the event
        ↓
OBSERVE
Who keeps using A? Who switches? When? Why?
        ↓
FOLLOW-UP
Do they use it again after the hackathon?
```

This is what separates `Exposure` from `Preference` from `Retention`. Required exposure must be
disclosed as part of the challenge terms — an undisclosed forced-use condition is both bad
research and bad faith with the participant.

## 3. Dynamic tracks

Tracks are not a permanent fixture list. They are a function of who is sponsoring and what they
need to learn:

```
Tracks(t) = f( Sponsors(t), ResearchQuestions(t) )
```

One event: AI developer tools, fintech infrastructure, health, consumer, climate.
Another: robotics, defense, enterprise, education, biotech.

Sponsors can shape prompts and can require particular products where that is part of the
disclosed challenge — but enough unconstrained surface has to remain that real builder
preference is still observable. If every track is constrained, there is no control condition
anywhere in the event.

## 4. Post-event is the product

A normal hackathon: `Event → End`.

This system: `Event → Behavior → Continuation → Outcome`.

With explicit permission, measured at 7 / 30 / 90 days:

- Did they keep using the API?
- Did the project continue?
- Did the team stay together?
- Did the prototype become a startup?
- Did a recruiter reach out? Did they interview?
- Did the sponsor product remain in the stack?

This is the single biggest differentiator from every other hackathon organizer, and also the
part with the most demanding consent requirements — see
[data-model.md](data-model.md#consent-is-load-bearing).

## 5. Selection becomes data

If ~3,000 students apply for ~200 seats, the application itself is an instrument: past
projects, work samples, interests, skills, track preference, team preference.

Compare application evidence against observed hackathon performance and you can eventually
learn *which application evidence actually predicts good builders* — outcome validation of the
selection rubric, not aptitude scoring. Over several events this makes selection measurably
better rather than vibes-based.

## 6. The behavioral loop

For each participant:

```
State(t) → Opportunity(t) → Action(t) → Outcome(t+h) → ModelUpdate
```

Concretely:

```
sponsor tool offered
      ↓
student tries it
      ↓
hits friction
      ↓
switches product
      ↓
finishes project elsewhere
      ↓
explains why
      ↓
30 days later still uses the replacement
```

That sequence is the asset. A static "which tool do you prefer?" survey is not.

## 7. The Club OS connection

Club OS supplies the persistent longitudinal layer on both sides of the event.

```
CLUB OS
knows ongoing campus activity
        ↓
HACKATHON
creates intense high-information episodes
        ↓
CLUB OS
observes continuation and outcomes
```

`Before + During + After` is a far richer record than a 48-hour window. Campus context —
academic timing, recruiting pressure, major, opportunity exposure, club history, project
history — lets performance be interpreted in context instead of naively. A student who shipped
less during finals week is not the same signal as a student who shipped less in a free week.

## 8. Where this ends up

The hackathon is one format. The network also supports 2-week sprints, product beta groups,
startup challenges, recruiting challenges, and semester-long R&D programs. At that point the
company is a **distributed human product-experimentation network**, and the weekend event is
simply its highest-density acquisition and measurement surface.
