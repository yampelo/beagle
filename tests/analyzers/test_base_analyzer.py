from beagle.analyzers.base_analyzer import Analyzer
from beagle.analyzers.statements.edge import IntermediateEdgeByProps

from beagle.analyzers.statements.process import FindProcess
from beagle.nodes import Process


def test_analyzer_two_statements(G5, graph_nodes_match):

    analyzer = Analyzer(
        name="test_analyzer_two_statements",
        description="test_analyzer_two_statements",
        score=0,
        statement=FindProcess.with_command_line("B") >> FindProcess.that_was_launched(),
    )

    G = analyzer.run_networkx(G5)

    assert graph_nodes_match(
        G,
        [
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
        ],
    )
