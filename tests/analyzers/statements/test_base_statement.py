import pytest
from beagle.backends.networkx import NetworkX
from beagle.analyzers.statements.base_statement import NodeByProps
from beagle.analyzers.statements.lookups import Contains, EndsWith, StartsWith
from beagle.nodes.process import Process


@pytest.fixture
def G1():
    # A basic graph, with two nodes an an edge
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    other_proc = Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")

    proc.launched[other_proc].append(timestamp=1)

    backend = NetworkX(consolidate_edges=True, nodes=[proc, other_proc])

    backend.graph()

    return backend


def test_one_prop_test(G1):
    statement = NodeByProps(node_type=Process, props={"command_line": Contains("test.exe")})

    # Should match on `proc` from G1
    assert statement.execute(G1) == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    ]

    # should mathc on other proc
    statement = NodeByProps(node_type=Process, props={"command_line": EndsWith("123456")})
    assert statement.execute(G1) == [
        Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")
    ]

    # should match on both
    statement = NodeByProps(node_type=Process, props={"process_image": EndsWith("exe")})
    assert statement.execute(G1) == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
        Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456"),
    ]

    # should match neither
    statement = NodeByProps(node_type=Process, props={"process_image": StartsWith("exe")})
    assert statement.execute(G1) == []


def test_multiple_prop_test(G1):
    statement = NodeByProps(
        node_type=Process,
        props={"command_line": Contains("foobar"), "process_image": StartsWith("test")},
    )

    # Should match on `proc` from G1
    assert statement.execute(G1) == [
        Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    ]
