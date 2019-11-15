from typing import List
import networkx as nx

from beagle.analyzers.statements.base_statement import (
    NodeByProps,
    EdgeByProps,
    NodeByPropsDescendents,
    NodeByPropsAncestors,
    NodeByPropsReachable,
)
from beagle.analyzers.statements.lookups import Contains, EndsWith, StartsWith, Exact

from beagle.nodes import Node, File, Process


def graph_nodes_match(graph: nx.Graph, nodes: List[Node]) -> bool:
    return [n["data"] for _, n in graph.nodes(data=True)] == nodes


def test_one_node_prop_test(G1):
    statement = NodeByProps(node_type=Process, props={"command_line": Contains("test.exe")})

    assert graph_nodes_match(
        statement.execute_networkx(G1),
        [Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")],
    )

    # should mathc on other proc
    statement = NodeByProps(node_type=Process, props={"command_line": EndsWith("123456")})

    assert graph_nodes_match(
        statement.execute_networkx(G1),
        [Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")],
    )

    # should match on both
    statement = NodeByProps(node_type=Process, props={"process_image": EndsWith("exe")})

    assert graph_nodes_match(
        statement.execute_networkx(G1),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456"),
        ],
    )
    statement = NodeByProps(node_type=Process, props={"process_image": StartsWith("exe")})

    assert graph_nodes_match(statement.execute_networkx(G1), [])


def test_multiple_node_prop_test(G1):
    statement = NodeByProps(
        node_type=Process,
        props={"command_line": Contains("foobar"), "process_image": StartsWith("test")},
    )

    # Should match on `proc` from G1
    assert graph_nodes_match(
        statement.execute_networkx(G1),
        [Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")],
    )


def test_node_conditional(G1):
    statement = NodeByProps(
        node_type=Process,
        props={"command_line": Contains("foobar"), "process_image": StartsWith("test")},
    )

    assert graph_nodes_match(
        statement.execute_networkx(G1),
        [Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")],
    )


def test_one_edge_prop_test(G2, G3):
    statement = EdgeByProps(edge_type="Wrote", props={"contents": Exact("foo")})

    assert graph_nodes_match(
        statement.execute_networkx(G2),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )

    # Should work on the non-conslidating graph too.
    assert graph_nodes_match(
        statement.execute_networkx(G3),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )

    statement = EdgeByProps(edge_type="Launched", props={"contents": Exact("bar")})

    # Should match on `proc` from G1
    assert graph_nodes_match(statement.execute_networkx(G2), [])


def test_node_with_descendants(G4):

    # A should return A->B->C->D
    statement = NodeByPropsDescendents(node_type=Process, props={"process_image": Exact("A")})
    assert graph_nodes_match(
        statement.execute_networkx(G4),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )

    # B should return B->C->D
    statement = NodeByPropsDescendents(node_type=Process, props={"process_image": Exact("B")})
    assert graph_nodes_match(
        statement.execute_networkx(G4),
        [
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )


def test_node_with_ancestors(G4):

    # A should return A
    statement = NodeByPropsAncestors(node_type=Process, props={"process_image": Exact("A")})
    assert graph_nodes_match(
        statement.execute_networkx(G4),
        [Process(process_id=10, process_image="A", command_line="A")],
    )

    # B should return A->B
    statement = NodeByPropsAncestors(node_type=Process, props={"process_image": Exact("B")})
    assert graph_nodes_match(
        statement.execute_networkx(G4),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
        ],
    )

    # D should return A->B->C->D
    statement = NodeByPropsAncestors(node_type=Process, props={"process_image": Exact("D")})
    assert graph_nodes_match(
        statement.execute_networkx(G4),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )


def test_nodes_reachable(G5):

    # All queries will return the full path.
    # They should only return the path this process touches, A should return A->B->C->D and not E->F->G->H

    statement = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("B")})
    assert graph_nodes_match(
        statement.execute_networkx(G5),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )

    statement = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("G")})
    assert graph_nodes_match(
        statement.execute_networkx(G5),
        [
            Process(process_id=10, process_image="E", command_line="E"),
            Process(process_id=12, process_image="F", command_line="F"),
            Process(process_id=12, process_image="G", command_line="G"),
            Process(process_id=12, process_image="H", command_line="H"),
        ],
    )
