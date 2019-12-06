from typing import Any, Type, cast

import networkx as nx

from beagle.backends import Backend, NetworkX
from beagle.common import logger

from .queries.base_query import Query
from .queries.summary import SummaryQuery


class Analyzer(object):
    def __init__(self, name: str, query: Query, description: str = None, score: int = None):
        self.name = name
        self.description = description
        self.score = score

        # Make sure we get the start.
        while query.upstream_query is not None:
            query = query.upstream_query

        self.query: Query = query

    def run(self, backend: Type[Backend]) -> Any:

        if isinstance(backend, NetworkX):
            backend = cast(NetworkX, backend)
            return self.run_networkx(backend.G)

    def run_networkx(self, G: nx.Graph) -> nx.Graph:
        logger.info(f"Running analyzer {self.name}")

        # H is a copy of our original graph.
        H = G.copy()

        current_query = self.query

        while current_query is not None:
            # Run the query.
            if isinstance(current_query, SummaryQuery):
                # SummaryQueries get the original graph.
                H = current_query.execute_networkx(G.copy())
            else:
                H = current_query.execute_networkx(H)

            # Get the next query, and execute
            current_query = current_query.downstream_query

        if len(H.nodes()) > 0:
            logger.info(f"Analyzer query returned a matching subgraph.")

        return H
