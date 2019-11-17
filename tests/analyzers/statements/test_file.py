from beagle.analyzers.base_analyzer import Analyzer
from beagle.analyzers.queries.file import FindFile
from beagle.nodes import File, Process


def test_file_with_name(G3, graph_nodes_match):
    analyzer = Analyzer(name="test_file_with_name", query=FindFile.with_file_name("foo"))

    G = analyzer.run_networkx(G3)

    assert graph_nodes_match(
        G,
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )


def test_file_with_path(G3, graph_nodes_match):
    analyzer = Analyzer(name="test_file_with_path", query=FindFile.with_file_path("bar"))

    G = analyzer.run_networkx(G3)

    assert graph_nodes_match(
        G,
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )


def test_file_with_full_path(G3, graph_nodes_match):
    analyzer = Analyzer(name="test_file_with_full_path", query=FindFile.with_full_path("bar\\foo"))

    G = analyzer.run_networkx(G3)

    assert graph_nodes_match(
        G,
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )


def test_file_that_was_written(G3, graph_nodes_match):
    analyzer = Analyzer(name="test_file_that_was_written", query=FindFile.that_was_written())

    G = analyzer.run_networkx(G3)

    assert graph_nodes_match(G, [File(file_name="foo", file_path="bar")])
