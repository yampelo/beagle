import pytest
from beagle.analyzers.queries.base_query import FactoryMixin, _str_to_exact
from beagle.analyzers.queries.node import NodeByPropsReachable, NodeByProps
from beagle.analyzers.queries.lookups import Exact
from beagle.nodes import Process


def test_factory_mixin():
    class MyFactory(FactoryMixin):
        pass

    with pytest.raises(UserWarning):
        obj = MyFactory()
        obj.execute_networkx(None)


@pytest.mark.parametrize(
    "props,expected",
    [
        ({"process_image": "A"}, {"process_image": Exact("A")}),
        ({"hashes": {"md5": "A"}}, {"hashes": {"md5": Exact("A")}}),
        ({"hashes": {"md5": "A", "baz": {"foo": "bar"}}}, {"hashes": {"md5": Exact("A"), "baz": {"foo": Exact("bar")}}}),
    ],
)
def test_str_to_exact(props, expected):
    assert _str_to_exact(props) == expected


def test_chained_query(G5, graph_nodes_match):
    # Both paths should show up because we use a chained query that returns both.

    Bquery = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("B")})
    Gquery = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("G")})

    chained = Bquery | Gquery

    assert graph_nodes_match(
        chained.execute_networkx(G5),
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


def test_multiple_chained_query(G5, graph_nodes_match):
    # Should properly execute all three.

    Bquery = NodeByProps(node_type=Process, props={"process_image": Exact("B")})
    Gquery = NodeByProps(node_type=Process, props={"process_image": Exact("G")})
    Aquery = NodeByProps(node_type=Process, props={"process_image": Exact("A")})

    chained = Bquery | Gquery | Aquery

    assert graph_nodes_match(
        chained.execute_networkx(G5),
        [
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="G", command_line="G"),
            Process(process_id=10, process_image="A", command_line="A"),
        ],
    )


def test_shift_operators():
    Bquery = NodeByProps(node_type=Process, props={"process_image": Exact("B")})
    Gquery = NodeByProps(node_type=Process, props={"process_image": Exact("G")})

    Bquery >> Gquery

    assert Bquery.downstream_query == Gquery

    Bquery = NodeByProps(node_type=Process, props={"process_image": Exact("B")})
    Gquery = NodeByProps(node_type=Process, props={"process_image": Exact("G")})

    Bquery << Gquery

    assert Gquery.downstream_query == Bquery
