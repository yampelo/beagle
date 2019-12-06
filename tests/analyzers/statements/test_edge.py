from beagle.analyzers.queries.edge import EdgeByProps
from beagle.analyzers.queries.lookups import Exact
from beagle.analyzers.queries.process import FindProcess
from beagle.nodes import File, Process


def test_one_edge_prop_test(G2, G3, graph_nodes_match):

    # String should get mapped to Exact("foo")
    query = EdgeByProps(edge_type="Wrote", props={"contents": "foo"})

    assert graph_nodes_match(
        query.execute_networkx(G2),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )

    # Should work on the non-conslidating graph too.
    assert graph_nodes_match(
        query.execute_networkx(G3),
        [
            Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar"),
            File(file_name="foo", file_path="bar"),
        ],
    )

    query = EdgeByProps(edge_type="Launched", props={"contents": Exact("bar")})

    # Should match on `proc` from G1
    assert graph_nodes_match(query.execute_networkx(G2), [])


def test_intermediate_edge_by_props(G5, graph_nodes_match):

    # Run the first query.
    query1 = FindProcess.with_command_line("B")
    query2 = EdgeByProps(edge_type="Launched")

    query1 >> query2

    # get the subgraph.
    G_s = query1.execute_networkx(G5)

    # running query two should only give us B->C
    assert graph_nodes_match(
        query2.execute_networkx(G_s),
        [
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="C", command_line="C"),
        ],
    )
