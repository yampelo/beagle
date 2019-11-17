from beagle.analyzers.queries.process import FindProcess
from beagle.nodes import Process, File
from beagle.analyzers.queries.lookups import EndsWith


def test_get_by_command_line_no_lookup(G5, graph_nodes_match):

    # Should return all nodes reachable from A
    query = FindProcess.with_command_line("A")

    assert graph_nodes_match(
        query.execute_networkx(G5),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )


def test_get_by_command_line_with_lookup(G5, graph_nodes_match):

    # Should return all nodes reachable from A Or G, (so all nodes)
    query = FindProcess.with_command_line(EndsWith("A") | EndsWith("G"))

    assert graph_nodes_match(
        query.execute_networkx(G5),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
            Process(process_id=10, process_image="E", command_line="E"),
            Process(process_id=12, process_image="F", command_line="F"),
            Process(process_id=12, process_image="G", command_line="G"),
            Process(process_id=12, process_image="H", command_line="H"),
        ],
    )


def test_get_process_name_no_lookup(G2, graph_nodes_match):

    # No match, since defaults to exact.
    query = FindProcess.with_process_name("exe")
    assert graph_nodes_match(query.execute_networkx(G2), [])

    query = FindProcess.with_process_name("test.exe")
    assert graph_nodes_match(
        query.execute_networkx(G2),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )


def test_get_process_name_lookup(G2, graph_nodes_match):

    # Should return test.exe because it ends with exe
    query = FindProcess.with_process_name(EndsWith("exe"))

    assert graph_nodes_match(
        query.execute_networkx(G2),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )


def test_get_process_user(G6, graph_nodes_match):

    # Should return test.exe because it ends with exe
    query = FindProcess.with_user("omer")

    assert graph_nodes_match(
        query.execute_networkx(G6),
        [
            Process(
                process_id=1, process_image_path="d:\\", process_image="parent.exe", user="omer"
            ),
            Process(
                process_id=2, process_image_path="d:\\users", process_image="child.exe", user="omer"
            ),
        ],
    )


def test_get_process_image_path(G6, graph_nodes_match):

    # Should return test.exe because it ends with exe
    query = FindProcess.with_process_image_path("d:\\")

    assert graph_nodes_match(
        query.execute_networkx(G6),
        [
            Process(
                process_id=1, process_image_path="d:\\", process_image="parent.exe", user="omer"
            ),
            Process(
                process_id=2, process_image_path="d:\\users", process_image="child.exe", user="omer"
            ),
        ],
    )
