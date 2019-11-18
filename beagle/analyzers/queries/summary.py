from typing import List, Set, Type

import networkx as nx

from beagle.analyzers.queries import Query
from beagle.nodes import Node


class SummaryQuery(Query):
    # Nothing special, just a type for detecting when we reach a summary operator.
    pass


class CollectDetectedNodes(SummaryQuery):
    def __init__(self, node_types: List[Type[Node]] = []):
        self.node_types = tuple(node_types)
        super().__init__()

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:

        all_resulting_nodes: Set[int] = set()

        # Get the upstream nodes.
        upstream_query = self.upstream_query
        while upstream_query is not None:
            all_resulting_nodes |= upstream_query.result_nodes
            upstream_query = upstream_query.upstream_query

        if self.node_types:
            node_attrs = nx.get_node_attributes(G, "data")
            all_resulting_nodes = filter(
                lambda node: isinstance(node_attrs[node], self.node_types), all_resulting_nodes
            )

        return G.subgraph(all_resulting_nodes)
