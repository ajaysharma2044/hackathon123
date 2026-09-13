# GridCompute — Commercial Ecosystem and Portfolio

## Rule: economically connected, not logo count

An organization belongs only if (1) it cares economically about the underlying compute/power problem, (2) the event naturally creates a relevant artifact/usage signal, (3) that can affect a meaningful decision near a real budget, and (4) we do not manufacture participant behavior to create the value.

## Ecosystem layers

### Problem owners / operators
- hyperscale cloud and AI infrastructure operators;
- neocloud/GPU-cloud operators;
- data-center/colocation operators;
- utilities serving large data-center loads;
- RTOs/ISOs managing system reliability and large-load integration.

### Solution / infrastructure vendors
- GPU/accelerator and server vendors;
- networking vendors;
- power distribution, UPS and switchgear;
- liquid cooling/CDUs;
- DCIM/BMS/EPMS;
- storage/microgrid controls;
- grid planning / power-flow / market software;
- optimization solvers;
- observability/security.

### Complements / capital / services
- engineering and data-center design firms;
- energy suppliers/developers;
- infrastructure investors;
- research consortia;
- recruiting/talent buyers;
- CVC/VC focused on AI infrastructure/energy.

## 25-account priority map

**Status discipline:** `SOURCED CONNECTION` means this Run 2 verified a direct current connection. `CANDIDATE — VERIFY` means the organization is logically in the stack but this pass did not deep-verify the specific business unit/initiative. **Observed WTP = UNKNOWN for every account.**

| # | Account | Layer | Why economically connected | Likely internal owner (HYPOTHESIS unless sourced) | Best natural offer | Research status |
|---:|---|---|---|---|---|---|
| 1 | PJM Interconnection | Grid operator | 2026 large-load integration + 4,000 MW computational-load disconnect event | System Operations / Planning / Large Load | scenario partner + benchmark/R&D challenge | **SOURCED CONNECTION** |
| 2 | NVIDIA | GPU / control | DCGM exposes GPU-group power limits/workload power profiles | Data Center Platform / DCGM / Developer Relations | power-aware workload benchmark + developer integration evidence | **SOURCED CONNECTION** |
| 3 | Schneider Electric | Power/cooling/control | 2026 AI reference designs integrate EPMS/BMS, cooling and AI workload management | Secure Power / Data Center Systems / Innovation | simulator/control module + R&D benchmark + in-kind hardware/software | **SOURCED CONNECTION** |
| 4 | Microsoft | Cloud + grid R&D | GridFM is explicitly aimed at fast grid evaluation under datacenter-driven volatility | Azure Infrastructure / Microsoft Research energy/grid | research challenge + compute + benchmark | **SOURCED CONNECTION** |
| 5 | U.S. DOE Office of Electricity | Grid R&D/data | 2026 transmission study + large-data-center dynamic-load work | Grid Controls / Transmission Planning | public scenario/data partner + research collaborator | **SOURCED CONNECTION** |
| 6 | FERC | Regulation / market rules | Ordered all six regional operators to address large-load integration | Office of Energy Market Regulation / technical staff | policy/scenario input; **not assumed commercial payer** | **SOURCED CONNECTION** |
| 7 | Amazon Web Services | Cloud / AI infra | AI compute operator exposed to power/capacity constraints | Infrastructure / Sustainability / HPC | compute credits + workload track + R&D | CANDIDATE — VERIFY |
| 8 | Google Cloud | Cloud / AI infra | AI compute/operator + energy-aware infrastructure decisions | Data Center / Cloud Infrastructure | benchmark + compute + research | CANDIDATE — VERIFY |
| 9 | Meta | Hyperscale AI infra | massive AI clusters + data-center physical constraints | Infrastructure / Data Center Engineering | benchmark/R&D | CANDIDATE — VERIFY |
| 10 | CoreWeave | Neocloud | GPU-dense AI infrastructure depends on speed-to-power | Infrastructure / Capacity / Data Center | benchmark + design-partner scenarios | CANDIDATE — VERIFY |
| 11 | Oracle Cloud Infrastructure | Cloud / AI infra | GPU capacity/data-center operator | OCI Infrastructure | compute + workload optimization challenge | CANDIDATE — VERIFY |
| 12 | Equinix | Colocation | customer density/power/cooling/operations | Data Center Operations / xScale | facility/siting/control R&D | CANDIDATE — VERIFY |
| 13 | Digital Realty | Colocation | hyperscale/AI data-center power availability | Data Center Operations / Energy | siting/power benchmark | CANDIDATE — VERIFY |
| 14 | QTS Data Centers | Data-center operator | hyperscale campuses + utility/grid interface | Development / Operations / Energy | speed-to-power / campus digital twin | CANDIDATE — VERIFY |
| 15 | Vantage Data Centers | Data-center operator | hyperscale development and power/cooling constraints | Engineering / Energy / Operations | facility optimization challenge | CANDIDATE — VERIFY |
| 16 | Vertiv | Power/cooling | UPS, power, thermal infrastructure for high-density AI | Technology / Product / Data Centers | hardware/control challenge + product research | CANDIDATE — VERIFY |
| 17 | Eaton | Power management | electrical distribution/UPS/microgrid layer | Data Center / Digital / Innovation | power-control/simulation module | CANDIDATE — VERIFY |
| 18 | Siemens | Grid + building systems | grid planning/electrification/building control stack | Grid Software / Electrification | grid-control tools + benchmark | CANDIDATE — VERIFY |
| 19 | ABB | Electrification | data-center power distribution/control | Data Centers / Electrification | power-system integration track | CANDIDATE — VERIFY |
| 20 | GE Vernova | Grid software/equipment | grid planning/control + large-load reliability | Electrification Software / Grid Solutions | power-flow/scenario challenge | CANDIDATE — VERIFY |
| 21 | Hitachi Energy | Grid systems | transmission/grid software and equipment | Grid Automation / Digital | grid scenario/simulator partner | CANDIDATE — VERIFY |
| 22 | AMD | Accelerators | AI GPU performance-per-watt and power profiles | Data Center GPU / Developer | alternative accelerator track + benchmark | CANDIDATE — VERIFY |
| 23 | Broadcom | Networking | AI fabric power/performance bottlenecks | Data Center Networking | network-aware workload challenge | CANDIDATE — VERIFY |
| 24 | Arista Networks | Networking | AI cluster fabrics + telemetry | AI Networking / Engineering | network/power observability integration | CANDIDATE — VERIFY |
| 25 | Dominion Energy | Utility | utility in a major data-center region; large-load planning is economically material | Transmission / Distribution Planning / Key Accounts | realistic large-load scenario + R&D | CANDIDATE — VERIFY |

## Why the run stops at 25 priority accounts instead of fabricating 150

The brief's 100–300 organization target is useful only after economic connection is verified. This pass verified six current anchor connections and built a 25-account priority queue. Expanding to 150 names before validating whether the anchor product is decision-relevant would create low-value logo inventory. The next expansion should be conditional on primary buyer feedback and should recurse from the product graph, not from Fortune 500 lists.

## Offer architecture

### A. Design-partner pilot
**Deliverable:** one realistic scenario pack + benchmark spec + small pre-event solver sprint/sample report.

- Observed WTP: **UNKNOWN**.
- Recommended initial ask: **$15K–$25K — DECISION HYPOTHESIS**, chosen as a low-friction falsification instrument, not as a market fact.
- Kill signal: no qualified buyer will pay/sign a priced LOI for even this small version.

### B. Anchor R&D challenge / benchmark
**Deliverable:** simulator + 30–50 independent solution attempts + hidden stress tests + architecture/failure report + continuation shortlist.

- Observed WTP: **UNKNOWN**.
- Comparable context: repo's standing research comps span roughly $25K–$250K, but they are not observed WTP for GridCompute.
- Recommended full-event ask: **$75K–$150K — DECISION HYPOTHESIS** only after a design partner validates scenario relevance.

### C. Infrastructure partner
**Deliverable:** optional useful tooling/compute/hardware, integration support, aggregate product-friction report.

- Cash ask: **$25K–$50K — HYPOTHESIS**.
- Credits/hardware: track **face value separately from actual cost avoided**.
- Reject forced exclusivity if it destroys neutral tool choice.

### D. Paid continuation
**Deliverable:** 4–8 week scoped work with selected teams on one validated problem.

- Price: scope-dependent **HYPOTHESIS**; no observed WTP.
- Stronger economic logic than selling extra on-site branding because the buyer gets additional work output.

## Commercial portfolio — recommended Pareto shape

- **1–2 problem-owner / R&D anchors** that supply real scenarios and buy the benchmark/solution portfolio.
- **2–3 non-exclusive infrastructure partners** (compute, accelerator, solver, observability/data).
- **1 power/cooling systems partner** if its tooling materially improves the challenge.
- **1 independent research/methodology partner** to protect benchmark credibility.
- **Optional recruiting** via participant-controlled artifact sharing only.

Do **not** maximize sponsor count. Every added module consumes mentor capacity, participant attention, legal/data-rights bandwidth and research validity.

## Conflict graph

Reject or restructure modules with these conflicts:

- cloud/GPU exclusivity ↔ neutral product-choice research;
- proprietary sponsor dataset ↔ public demo/repo;
- participant IP assignment ↔ student ownership/open source;
- mandatory tool ↔ natural adoption evidence;
- sponsor-funded comparative study ↔ independence claim;
- opaque talent scoring ↔ consent/privacy;
- too many tracks ↔ coherent event/open build;
- category exclusivity ↔ multiple economically useful infrastructure partners.
