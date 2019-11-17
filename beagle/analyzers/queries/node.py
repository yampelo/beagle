from typing import Dict, Set, Type, Union

import networkx as nx

from beagle.nodes import Node

from .base_query import Query, _str_to_exact
from .lookups import FieldLookup


class NodeByProps(Query):
    def __init__(self, node_type: Type[Node], props: Dict[str, Union[str, FieldLookup, Dict]] = {}):
        """Searches the graph for a node of type `node_type` with properties matching `props`

        Parameters
        ----------
        node_type : Type[Node]
            The type of node to look for. e.g. Process
        props : Dict[str, Union[str, FieldLookup, Dict]]
            The set of props to filter the resulting nodes by. Any string is transformed to `Exact` lookups.

        Examples
        ----------
        Filter for Process nodes, with command lines that contain `text.exe`
        >>> NodeByProps(node_type=Process, props={"command_line": Contains("test.exe")})

        This may also be a nested dict.
        >>> NodeByProps(node_type=Process, props={"hashes": {"md5": Contains("test.exe")}})

        """
        self.node_type = node_type

        self.props: Dict[str, Union[FieldLookup, Dict]] = _str_to_exact(props)

        # Cast and assign.
        super().__init__()

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        """Searches a `nx.Graph` object for nodes that match type `node_type` and contains
        props matching `props`. This is O(V).
        """
        subgraph_nodes = []

        # For each node
        for node_id, data in G.nodes(data=True):
            node = data["data"]

            # If node matches the desired instance.
            if isinstance(node, self.node_type):
                # Test the node
                if self._test_values_with_lookups(node, self.props):
                    subgraph_nodes.append(node_id)
                    self.result_nodes |= {node_id}

        return G.subgraph(subgraph_nodes)


class NodeByPropsDescendents(NodeByProps):
    """Executes a `NodeByProps` query, and returns all descendants of the matching nodes.
    see py:meth:`NodeByProps`"""

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:

        # Get the next graph
        next_graph = super().execute_networkx(G)

        subgraph_nodes: Set[int] = set()

        # For every node that matched `NodeByProps`
        for node_id in next_graph.nodes():
            # Get the nodes descendants in the original graph, and add make a subgraph from those.
            subgraph_nodes |= nx.descendants(G, node_id) | {node_id}

            self.result_nodes |= {node_id}

        return G.subgraph(subgraph_nodes)


class NodeByPropsAncestors(NodeByProps):
    """Executes a `NodeByProps` query, and returns all ascendants of the matching nodes.
    see py:meth:`NodeByProps`"""

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:

        # Get the next graph
        next_graph = super().execute_networkx(G)

        subgraph_nodes: Set[int] = set()

        # For every node that matched `NodeByProps`
        for node_id in next_graph.nodes():
            # Get the nodes ancestors in the original graph, and add make a subgraph from those.
            subgraph_nodes |= nx.ancestors(G, node_id) | {node_id}
            self.result_nodes |= {node_id}

        return G.subgraph(subgraph_nodes)


class NodeByPropsReachable(NodeByProps):
    """Executes a `NodeByProps` query, and returns all ancestors and descendants of the matching nodes.
    see py:meth:`NodeByProps`"""

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:

        # Get the next graph
        next_graph = super().execute_networkx(G)

        subgraph_nodes: Set[int] = set()

        # For every node that matched `NodeByProps`
        for node_id in next_graph.nodes():
            subgraph_nodes |= nx.ancestors(G, node_id) | nx.descendants(G, node_id) | {node_id}
            self.result_nodes |= {node_id}

        return G.subgraph(subgraph_nodes)
