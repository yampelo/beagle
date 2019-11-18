from typing import Dict, Union, Set

import networkx as nx

from .base_query import Query, _str_to_exact, PropsDict
from .lookups import FieldLookup


class EdgeByProps(Query):
    def __init__(self, edge_type: str, props: PropsDict = {}, *args, **kwargs):
        """Searches the graph for an edge of type `edge_type` with properties matching `props`

        Parameters
        ----------
        edge_type : str
            The type of edge to look for. e.g. Wrote
        props : Dict[str, Union[str, FieldLookup]]
            The set of props to filter the resulting edges by. Any string is transformed to `Exact` lookups.

        Examples
        ----------
        Filter for TCP edges, with contents that match ".pdf"
        >>> EdgeByProps(edge_type="TCP", props={"payload": Contains(".pdf")})

        """
        self.edge_type = edge_type

        self.props: Dict[str, Union[FieldLookup, Dict]] = _str_to_exact(props)

        super().__init__()

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        """Searches a `nx.Graph` object for edges that match type `edge_type` and contains
        props matching `props`. This is O(E).

        Returns a subgraph with all nodes contained in match edges
        """
        subgraph_edges = []

        if self.upstream_query is not None:
            upstream_nodes, _ = self.get_upstream_results()
            edges = G.edges(upstream_nodes, data=True, keys=True)
        else:
            edges = G.edges(data=True, keys=True)

        # For each edge
        for u, v, k, e_data in edges:

            # pull out the data field from NX
            data = e_data["data"]  # edge data
            e_type = e_data["edge_name"]  # edge type

            # If edge matches the desired instance.
            if e_type == self.edge_type:

                # Test the edge
                if not isinstance(data, list):
                    data = [data]

                for entry in data:
                    if self._test_values_with_lookups(entry, self.props):
                        subgraph_edges.append((u, v, k))
                        # can stop on first match
                        self.result_edges |= {(u, v, k)}
                        self.result_nodes |= {v}
                        break

        return G.edge_subgraph(subgraph_edges)


class EdgeByPropsDescendants(EdgeByProps):
    """Perform a `EdgeByProps` query, expanding the descendants of the found edges."""

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        next_graph = super().execute_networkx(G)

        # get the nodes from the previous graph.
        subgraph_nodes: Set[int] = {node_id for node_id in next_graph.nodes()}

        # For every node that matched `in EdgeByProps`
        for _, v, _ in self.result_edges:
            subgraph_nodes |= nx.descendants(G, v) | {v}

        self.result_nodes |= subgraph_nodes

        return G.subgraph(subgraph_nodes)


class EdgeByPropsAncestors(EdgeByProps):
    """Perform a `EdgeByProps` query, expanding the ancestors of the found edges."""

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        next_graph = super().execute_networkx(G)

        # get the nodes from the previous graph.
        subgraph_nodes: Set[int] = {node_id for node_id in next_graph.nodes()}

        # For every node that matched `in EdgeByProps`
        for _, v, _ in self.result_edges:
            subgraph_nodes |= nx.ancestors(G, v) | {v}

        self.result_nodes |= subgraph_nodes

        return G.subgraph(subgraph_nodes)


class EdgeByPropsReachable(EdgeByProps):
    """Perform a `EdgeByProps` query, including all reachable nodes."""

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        next_graph = super().execute_networkx(G)

        # get the nodes from the previous graph.
        subgraph_nodes: Set[int] = {node_id for node_id in next_graph.nodes()}

        # For every node that matched `in EdgeByProps`
        for _, v, _ in self.result_edges:
            subgraph_nodes |= nx.ancestors(G, v) | nx.descendants(G, v) | {v}

        self.result_nodes |= subgraph_nodes

        return G.subgraph(subgraph_nodes)
