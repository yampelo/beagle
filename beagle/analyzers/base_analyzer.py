from typing import Type, cast

import networkx as nx

from beagle.analyzers.queries.base_query import Query
from beagle.backends import Backend, NetworkX


class Analyzer(object):
    def __init__(self, name: str, query: Query, description: str = None, score: int = None):
        self.name = name
        self.description = description
        self.score = score

        # Make sure we get the start.
        while query.upstream_query is not None:
            query = query.upstream_query

        self.query: Query = query

    def run(self, backend: Type[Backend]):
        if isinstance(backend, NetworkX):
            backend = cast(NetworkX, backend)
            self.run_networkx(backend.G)

    def run_networkx(self, G: nx.Graph) -> nx.Graph:

        # H is a copy of our original graph.
        H = G.copy()

        current_query = self.query

        while current_query is not None:
            # Run the query.
            H = current_query.execute_networkx(H)

            # Get the next query, and execute
            current_query = current_query.downstream_query

        return H
