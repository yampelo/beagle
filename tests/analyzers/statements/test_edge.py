from beagle.analyzers.statements.edge import EdgeByProps
from beagle.analyzers.statements.lookups import Exact
from beagle.nodes import File, Process


def test_one_edge_prop_test(G2, G3, graph_nodes_match):

    # String should get mapped to Exact("foo")
    statement = EdgeByProps(edge_type="Wrote", props={"contents": "foo"})

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
