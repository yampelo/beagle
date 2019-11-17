from beagle.analyzers.base_analyzer import Analyzer
from beagle.analyzers.queries.process import FindProcess
from beagle.nodes import Process


def test_analyzer_two_queries(G5, graph_nodes_match):

    analyzer = Analyzer(
        name="test_analyzer_two_queries",
        description="test_analyzer_two_queries",
        score=0,
        query=FindProcess.with_command_line("B") >> FindProcess.that_was_launched(),
    )

    G = analyzer.run_networkx(G5)

    assert graph_nodes_match(
        G,
        [
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
        ],
    )


def test_analyzer_or_query_queries(G5, graph_nodes_match):

    query = (
        FindProcess.with_command_line("B") | FindProcess.with_command_line("A")
    ) >> FindProcess.that_was_launched()

    analyzer = Analyzer(
        name="test_analyzer_two_queries",
        description="test_analyzer_two_queries",
        score=0,
        query=query,
    )

    G = analyzer.run_networkx(G5)

    assert graph_nodes_match(
        G,
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
        ],
    )
