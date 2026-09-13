# Tests actually run

Validation for this revision:

- `python3 -m pytest -q`: **59 passed**, including 22 subprocess cases that execute every historical
  test script and 37 direct tests. This count describes pytest cases, not an invented count of
  assertions inside the historical scripts.
- `PYTHONPYCACHEPREFIX=/private/tmp/hackathon-refactor-pycache python3 -m compileall -q engine`: passed.
- Offline CLI smoke check: exit 2, RESEARCH_BACKEND_REQUIRED, recommendation UNKNOWN, no discovered
  entities or atomic claims, six traced backend-required attempts.
- `git diff --check`: passed.

The initial unmodified suite could not finish pytest collection because a legacy test script raised
SystemExit at import. Historical scripts now run in isolated subprocesses; return codes and printed
failure counters are checked. Only the explicitly listed historical files are excluded from normal
collection, so future pytest tests are not silently ignored. Stale tests expecting seeded pricing,
costs or RESOLVED packets were changed to assert the new honest behavior.

Tests exercise state/rollup/Defer/Evidence bypasses, facts without opened sources/excerpts, inference
support closure, source-tier spoofing and independent-source groups, company missing-field contracts,
negative searches for each field, multi-round research, discovery with no predefined sectors/logos,
deduplication, saturation vs budget exhaustion, dependency cycles, preserved contradictory evidence,
WTP misuse, covert/person-scoring capture, R&D constraints, shared burden and adaptive question tools,
negative burden, resume, independent red-team reopening, evidence-only synthesis and Pareto comparison.
Existing capture, consent, temporal, qualitative, live-research and R&D scripts remain in the suite.

All research fixtures are fictional. No live provider was exercised; no source classification or
semantic-extraction accuracy claim is made by these tests. A first compile attempt used macOS's
unwritable default bytecode cache; the explicit temporary cache command above passed.
