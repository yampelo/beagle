from typing import Dict, Type

from beagle.nodes import Node

from .lookups import FieldLookup
import networkx as nx


class Statement(object):
    def execute_networkx(self, G: nx.Graph):  # pragma: no cover
        raise NotImplementedError(f"NetworkX not supported for {self.__class__.__name__}")


class NodeByProps(Statement):
    def __init__(self, node_type: Type[Node], props: Dict[str, FieldLookup]):
        self.node_type = node_type
        self.props = props

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        subgraph_nodes = []

        # For each node
        for node_id, data in G.nodes(data=True):
            node = data["data"]

            # If node matches the desired instance.
            if isinstance(node, self.node_type):
                # Test the node
                if all([lookup.test(getattr(node, prop)) for prop, lookup in self.props.items()]):
                    subgraph_nodes.append(node_id)

        return G.subgraph(subgraph_nodes)
