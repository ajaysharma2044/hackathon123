"""Run historical executable checks in subprocesses, not during pytest collection."""
from pathlib import Path
LEGACY = {'test_live_research_os.py', 'test_research_triggers.py', 'test_grounding.py', 'test_value_engines.py', 'test_capture.py', 'test_multi_sided.py', 'test_arms_race.py', 'test_company_matcher.py', 'test_score.py', 'test_discovery_engine.py', 'test_event_optimizer.py', 'test_event_ops.py', 'test_talent_venture.py', 'test_adaptive_questions.py', 'test_temporal.py', 'test_guardrails.py', 'test_beliefs_mc.py', 'test_cornell_products.py', 'test_voi_portfolio_calib.py', 'test_run2_core.py', 'test_environment_economy.py'}
def pytest_ignore_collect(collection_path, config):
    p=Path(str(collection_path))
    return p.parent.name=='engine' and p.name in LEGACY
