from typing import Dict, Type

from beagle.nodes import Node

from .lookups import FieldLookup
import networkx as nx


class Statement(object):
    def execute_networkx(self, G: nx.Graph):  # pragma: no cover
        raise NotImplementedError(f"NetworkX not supported for {self.__class__.__name__}")


class NodeByProps(Statement):
    def __init__(self, node_type: Type[Node], props: Dict[str, FieldLookup]):
        """Searches the graph for a node of type `node_type` with properties matching `props`

        Parameters
        ----------
        node_type : Type[Node]
            The type of node to look for. e.g. Process
        props : Dict[str, FieldLookup]
            The set of props to filter the resulting nodes by.

        Examples
        ----------
        Filter for Process nodes, with command lines that contain `text.exe`
        >>> NodeByProps(node_type=Process, props={"command_line": Contains("test.exe")})

        """
        self.node_type = node_type
        self.props = props

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
                if all([lookup.test(getattr(node, prop)) for prop, lookup in self.props.items()]):
                    subgraph_nodes.append(node_id)

        return G.subgraph(subgraph_nodes)


class EdgeByProps(Statement):
    def __init__(self, edge_type: str, props: Dict[str, FieldLookup]):
        """Searches the graph for an edge of type `edge_type` with properties matching `props`

        Parameters
        ----------
        edge_type : str
            The type of edge to look for. e.g. Wrote
        props : Dict[str, FieldLookup]
            The set of props to filter the resulting edges by.

        Examples
        ----------
        Filter for TCP edges, with contents that match ".pdf"
        >>> EdgeByProps(edge_type="TCP", props={"payload": Contains(".pdf")})

        """
        self.edge_type = edge_type
        self.props = props

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        """Searches a `nx.Graph` object for edges that match type `edge_type` and contains
        props matching `props`. This is O(E).

        Returns a subgraph with all nodes contained in match edges
        """
        subgraph_edges = []

        # For each edge
        for u, v, k, e_data in G.edges(data=True, keys=True):

            # pull out the data field from NX
            data = e_data["data"]  # edge data
            e_type = e_data["edge_name"]  # edge type

            # If edge matches the desired instance.
            if e_type == self.edge_type:

                # Test the edge
                if not isinstance(data, list):
                    data = [data]

                for entry in data:
                    if any([lookup.test(entry.get(prop)) for prop, lookup in self.props.items()]):
                        subgraph_edges.append((u, v, k))
                        # can stop on first match
                        break

        return G.edge_subgraph(subgraph_edges)
