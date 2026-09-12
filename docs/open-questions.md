# Open Questions

Decisions that block building. Not a backlog — these change what gets built.

## Sequencing

**1. What is event #1, concretely?**
Date, city, venue, headcount. Everything else — sponsor pitch, application build, budget — keys
off this.

**2. Does the platform exist for event #1, or does event #1 run on spreadsheets and forms?**
Strong argument for the latter: run one event manually, instrument it crudely, and let the real
friction dictate the schema. Building the full event-stream platform before ever running an
event risks modeling a process nobody has performed yet.

**3. What is the minimum sponsor deliverable that is still honest at n≈70?**
The findings-report format is the product. Its first version has to be defensible on one event's
data or the second sponsor won't renew.

## Economics

**4. What does a 200-person flown-in, housed, fed event actually cost?**
Travel + housing + venue + food + prizes for 200 people is the dominant number in the whole
model. Everything about pricing depends on it.

**5. How many sponsors at what contract size clear that number?**
And which sponsor type is the realistic first yes — research buyer, recruiting buyer, or plain
activation buyer? They have different sales cycles and different budget owners.

**6. Who is the first sponsor conversation with, and what is their actual decision?**
The pitch only works if it opens with their unknown, not with our event.

## Product and method

**7. What counts as `activation` and `meaningful action`?**
Must be written before event #1. See
[research-framework.md](research-framework.md#behavioral-funnel).

**8. How is `tool_switched` actually captured?**
The highest-signal event is the hardest to observe. Self-report? Periodic check-ins? Sponsor-side
telemetry? Repo inspection with consent? This is a real design problem, not a schema detail.

**9. How much of the event stays unconstrained?**
If sponsors buy required exposure across every track, there is no control condition anywhere and
the research product collapses. Needs a stated floor.

## Consent, legal, trust

**10. Legal review before event #1.**
Student population, post-event tracking, likely international participants, possible university
affiliation. FERPA-adjacent, GDPR, state privacy regimes. Cheap now; expensive after 200 people
have longitudinal records. See [data-model.md](data-model.md#consent-is-load-bearing).

**11. What does revocation do to already-delivered evidence?**
Define before the first recruiting deliverable ships.

**12. Minimum cell size for sponsor-facing segment cuts.**
Enforces the aggregate-only promise instead of just asserting it.

**13. Participant agreement: IP and paid follow-on work.**
Who owns what a team builds? What is the status of a $10K–$50K follow-on engagement? Settle
before the first one happens.

## Platform

**14. Relationship to Club OS — shared codebase, shared data layer, or separate systems with a
linkage?**
Affects everything about the architecture. Club OS is described as already having relevant
architecture; whether this is a module of it or a sibling is undecided.

**15. Build vs. buy for the event stream.**
An off-the-shelf analytics pipeline covers a lot of this early. The custom part is the
experiment record, the consent scoping, and the bitemporal handling.

## Naming

**16. The repo is currently `hackathon123`.**
The thesis is explicitly that this is not a hackathon company. Worth renaming once there's a
real name.
