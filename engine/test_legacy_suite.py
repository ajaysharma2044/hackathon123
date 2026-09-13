"""Every historical test script still runs; subprocess exit/F counters are asserted."""
from pathlib import Path
import subprocess
import sys
import pytest
ENGINE=Path(__file__).resolve().parent
SCRIPTS=[ENGINE/name for name in ['test_adaptive_questions.py', 'test_agent_os.py', 'test_arms_race.py', 'test_beliefs_mc.py', 'test_capture.py', 'test_company_matcher.py', 'test_cornell_products.py', 'test_discovery_engine.py', 'test_environment_economy.py', 'test_event_ops.py', 'test_event_optimizer.py', 'test_grounding.py', 'test_guardrails.py', 'test_live_research_os.py', 'test_multi_sided.py', 'test_research_triggers.py', 'test_run2_core.py', 'test_score.py', 'test_talent_venture.py', 'test_temporal.py', 'test_value_engines.py', 'test_voi_portfolio_calib.py']]
@pytest.mark.parametrize('script',SCRIPTS,ids=lambda p:p.stem)
def test_historical_script(script):
    result=subprocess.run([sys.executable,str(script)],cwd=ENGINE,text=True,capture_output=True,timeout=180)
    assert result.returncode==0,result.stdout+'\n'+result.stderr
    # Several older scripts print assertions rather than raising them.
    import re
    assert not re.search(r'(?m)^\s*FAIL(?:\s|:)|\b[1-9]\d* failed\b',result.stdout),result.stdout
