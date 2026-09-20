# Tests actually run

Validation for this revision:

- `python3 -m pytest -q`: **86 passed**, including 21 subprocess cases that execute every historical
  test script and 65 direct tests. This count describes pytest cases, not an invented count of
  assertions inside the historical scripts.
- `PYTHONPYCACHEPREFIX=/private/tmp/hackathon-refactor-pycache python3 -m compileall -q engine`: passed.
- Offline CLI smoke check: exit 2, RESEARCH_BACKEND_REQUIRED, recommendation UNKNOWN, a user-seeded company dossier with no atomic claims and an honest backend-required trace.
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

All deterministic research fixtures are fictional. Fifteen live-path tests cover the actual CLI,
semantic adapter, company/objective execution, exports, interruption persistence, budgets and provenance.
The real DuckDuckGo smoke was blocked by a bot challenge (reported explicitly); a direct fetch of
https://www.cornell.edu/ succeeded. Paid search and semantic API credentials were unavailable, so no
paid provider or semantic accuracy success is claimed. A first compile attempt used macOS's
unwritable default bytecode cache; the explicit temporary cache command above passed.

Concurrent upstream lifecycle/scraper/governor tests are included. Scraper cases verify exact
anchors/digests, rejection of invented excerpts, and private DNS/redirect rejection. CI retains the upstream workflow unchanged, including its numpy/scipy dependencies and
legacy-script runner. The local unified pytest wrapper also runs all historical scripts.

The later concurrent conversion of test_agent_os.py is preserved as seven collected pytest tests.
Governor approval/report aliases and run_cornell(ctx=...) compatibility are retained.
