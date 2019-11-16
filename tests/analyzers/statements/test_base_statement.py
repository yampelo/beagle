import pytest
from beagle.analyzers.statements.base_statement import FactoryMixin
from beagle.analyzers.statements.node import NodeByPropsReachable, NodeByProps
from beagle.analyzers.statements.lookups import Exact
from beagle.nodes import Process


def test_factory_mixin():
    class MyFactory(FactoryMixin):
        pass

    with pytest.raises(UserWarning):
        obj = MyFactory()
        obj.execute_networkx(None)


def test_chained_statement(G5, graph_nodes_match):
    # Both paths should show up because we use a chained statement that returns both.

    Bstatement = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("B")})
    Gstatement = NodeByPropsReachable(node_type=Process, props={"process_image": Exact("G")})

    chained = Bstatement | Gstatement

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


def test_multiple_chained_statement(G5, graph_nodes_match):
    # Should properly execute all three.

    Bstatement = NodeByProps(node_type=Process, props={"process_image": Exact("B")})
    Gstatement = NodeByProps(node_type=Process, props={"process_image": Exact("G")})
    Astatement = NodeByProps(node_type=Process, props={"process_image": Exact("A")})

    chained = Bstatement | Gstatement | Astatement

    assert graph_nodes_match(
        chained.execute_networkx(G5),
        [
            Process(process_id=12, process_image="B", command_line="B"),
            Process(process_id=12, process_image="G", command_line="G"),
            Process(process_id=10, process_image="A", command_line="A"),
        ],
    )
