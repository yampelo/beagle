import pytest
from beagle.backends.networkx import NetworkX
from beagle.analyzers.statements.base_statement import NodeByProps, EdgeByProps
from beagle.analyzers.statements.lookups import Contains, EndsWith, StartsWith, Exact
from beagle.nodes.process import Process, File


@pytest.fixture
def G1():
    # A basic graph, with two nodes an an edge
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    other_proc = Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")

    proc.launched[other_proc].append(timestamp=1)

    backend = NetworkX(consolidate_edges=True, nodes=[proc, other_proc])

    return backend.graph()


@pytest.fixture
def G2():
    # A basic graph, with two nodes an an edge
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    f = File(file_name="foo", file_path="bar")

    proc.wrote[f].append(contents="foo")

    backend = NetworkX(consolidate_edges=True, nodes=[proc, f])

    return backend.graph()


@pytest.fixture
def G3():
    # *no consolidating*
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    f = File(file_name="foo", file_path="bar")

    proc.wrote[f].append(contents="foo")
    proc.wrote[f].append(contents="bar")

    backend = NetworkX(consolidate_edges=False, nodes=[proc, f])

    return backend.graph()


def test_one_node_prop_test(G1):
    statement = NodeByProps(node_type=Process, props={"command_line": Contains("test.exe")})

    # Should match on `proc` from G1
    nodes = statement.execute_networkx(G1).nodes(data=True)
    assert len(nodes) == 1
    assert Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar") in [
        n["data"] for _, n in nodes
    ]

    # should mathc on other proc
    statement = NodeByProps(node_type=Process, props={"command_line": EndsWith("123456")})
    assert [n["data"] for _, n in statement.execute_networkx(G1).nodes(data=True)] == [
        Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")
    ]

    # should match on both
    statement = NodeByProps(node_type=Process, props={"process_image": EndsWith("exe")})
    assert [n["data"] for _, n in statement.execute_networkx(G1).nodes(data=True)] == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
        Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456"),
    ]

    # should match neither
    statement = NodeByProps(node_type=Process, props={"process_image": StartsWith("exe")})
    assert [n["data"] for _, n in statement.execute_networkx(G1).nodes(data=True)] == []


def test_multiple_node_prop_test(G1):
    statement = NodeByProps(
        node_type=Process,
        props={"command_line": Contains("foobar"), "process_image": StartsWith("test")},
    )

    # Should match on `proc` from G1
    assert [n["data"] for _, n in statement.execute_networkx(G1).nodes(data=True)] == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    ]


def test_node_conditional(G1):
    statement = NodeByProps(
        node_type=Process,
        props={"command_line": Contains("foobar"), "process_image": StartsWith("test")},
    )

    # Should match on `proc` from G1
    assert [n["data"] for _, n in statement.execute_networkx(G1).nodes(data=True)] == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    ]


def test_one_edge_prop_test(G2, G3):
    statement = EdgeByProps(edge_type="Wrote", props={"contents": Exact("foo")})

    assert [n["data"] for _, n in statement.execute_networkx(G2).nodes(data=True)] == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
        File(file_name="foo", file_path="bar"),
    ]

    # Should work on the non-conslidating graph too.
    assert [n["data"] for _, n in statement.execute_networkx(G3).nodes(data=True)] == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
        File(file_name="foo", file_path="bar"),
    ]

    statement = EdgeByProps(edge_type="Launched", props={"contents": Exact("bar")})

    # Should match on `proc` from G1
    assert [n["data"] for _, n in statement.execute_networkx(G2).nodes(data=True)] == []
