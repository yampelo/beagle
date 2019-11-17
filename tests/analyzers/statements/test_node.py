from beagle.analyzers.queries.base_query import Query
from beagle.analyzers.queries.lookups import Contains, EndsWith, Exact, StartsWith
from beagle.analyzers.queries.node import (
    NodeByProps,
    NodeByPropsAncestors,
    NodeByPropsDescendents,
    NodeByPropsReachable,
)
from beagle.nodes import Process


def test_test_props_nested_dict():
    s = Query()

    assert (
        s._test_values_with_lookups(
            value_to_test={"hashes": {"md5": "1234"}},
            lookup_tests={"hashes": {"md5": Exact("1234")}},
        )
        is True
    )

    assert (
        s._test_values_with_lookups(
            value_to_test={"hashes": {}}, lookup_tests={"hashes": {"md5": Exact("1234")}}
        )
        is False
    )

    assert (
        s._test_values_with_lookups(
            value_to_test={"hashes": None}, lookup_tests={"hashes": {"md5": Exact("1234")}}
        )
        is False
    )


def test_one_node_prop_test(G1, graph_nodes_match):
    query = NodeByProps(node_type=Process, props={"command_line": Contains("test.exe")})

    assert graph_nodes_match(
        query.execute_networkx(G1),
        [Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")],
    )

    # should mathc on other proc
    query = NodeByProps(node_type=Process, props={"command_line": EndsWith("123456")})

    assert graph_nodes_match(
        query.execute_networkx(G1),
        [Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")],
    )

    # should match on both
    query = NodeByProps(node_type=Process, props={"process_image": EndsWith("exe")})

    assert graph_nodes_match(
        query.execute_networkx(G1),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456"),
        ],
    )
    query = NodeByProps(node_type=Process, props={"process_image": StartsWith("exe")})

    assert graph_nodes_match(query.execute_networkx(G1), [])


def test_multiple_node_prop_test(G1, graph_nodes_match):
    query = NodeByProps(
        node_type=Process,
        props={"command_line": Contains("foobar"), "process_image": StartsWith("test")},
    )

    # Should match on `proc` from G1
    assert graph_nodes_match(
        query.execute_networkx(G1),
        [Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")],
    )


def test_node_conditional(G1, graph_nodes_match):
    query = NodeByProps(
        node_type=Process,
        props={"command_line": Contains("foobar"), "process_image": StartsWith("test")},
    )

    assert graph_nodes_match(
        query.execute_networkx(G1),
        [Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")],
    )


def test_node_with_descendants(G4, graph_nodes_match):

    # A should return A->B->C->D
    query = NodeByPropsDescendents(node_type=Process, props={"process_image": Exact("A")})
    assert graph_nodes_match(
        query.execute_networkx(G4),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )

    # B should return B->C->D
    query = NodeByPropsDescendents(node_type=Process, props={"process_image": Exact("B")})
    assert graph_nodes_match(
        query.execute_networkx(G4),
        [
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )


def test_node_with_ancestors(G4, graph_nodes_match):

    # A should return A
    query = NodeByPropsAncestors(node_type=Process, props={"process_image": Exact("A")})
    assert graph_nodes_match(
        query.execute_networkx(G4), [Process(process_id=10, process_image="A", command_line="A")]
    )

    # B should return A->B
    query = NodeByPropsAncestors(node_type=Process, props={"process_image": Exact("B")})
    assert graph_nodes_match(
        query.execute_networkx(G4),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
        ],
    )

    # D should return A->B->C->D
    query = NodeByPropsAncestors(node_type=Process, props={"process_image": Exact("D")})
    assert graph_nodes_match(
        query.execute_networkx(G4),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )


def test_nodes_reachable(G5, graph_nodes_match):

    # All queries will return the full path.
    # They should only return the path this process touches, A should return A->B->C->D and not E->F->G->H

    query = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("B")})
    assert graph_nodes_match(
        query.execute_networkx(G5),
        [
            Process(process_id=10, process_image="A", command_line="A"),
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
            Process(process_id=12, process_image="D", command_line="D"),
        ],
    )

    query = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("G")})
    assert graph_nodes_match(
        query.execute_networkx(G5),
        [
            Process(process_id=10, process_image="E", command_line="E"),
            Process(process_id=12, process_image="F", command_line="F"),
            Process(process_id=12, process_image="G", command_line="G"),
            Process(process_id=12, process_image="H", command_line="H"),
        ],
    )
