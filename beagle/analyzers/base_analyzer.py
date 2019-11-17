from typing import Type, cast

import networkx as nx

from beagle.analyzers.statements.base_statement import Statement
from beagle.backends import Backend, NetworkX


class Analyzer(object):
    def __init__(self, name: str, description: str, score: int, statement: Statement):
        self.name = name
        self.description = description
        self.score = score

        # Make sure we get the start.
        while statement.upstream_statement is not None:
            statement = statement.upstream_statement

        self.statement: Statement = statement

    def run(self, backend: Type[Backend]):
        if isinstance(backend, NetworkX):
            backend = cast(NetworkX, backend)
            self.run_networkx(backend.G)

    def run_networkx(self, G: nx.Graph) -> nx.Graph:

        # H is a copy of our original graph.
        H = G.copy()

        current_statement = self.statement

        while current_statement is not None:
            # Run the statement.
            H = current_statement.execute_networkx(H)

            # Get the next statement, and execute
            current_statement = current_statement.downstream_statement

        return H
