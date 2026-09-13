"""Deprecated entrypoint. Use python -m engine.research_run --objective ... ."""
from governor import build_research_graph, Governor

def build_discovery_graph(objective='Determine the optimal first Cornell technical event'):
    return build_research_graph(objective)

def run_discovery(findings_path=None, *, objective='Determine the optimal first Cornell technical event', executor=None):
    if findings_path:
        raise ValueError('Answer packets are not live research. Configure a ResearchExecutor; retain packets as archival data.')
    gov = Governor(build_discovery_graph(objective),ctx={'research_executor':executor,'objective':objective})
    return gov,gov.run()

if __name__ == '__main__':
    from research_run import main
    main()
