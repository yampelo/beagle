from typing import Any, Dict, List, Set, Tuple, Union

import networkx as nx

from beagle.nodes import Node

from .lookups import Exact, FieldLookup


PropsDict = Dict[str, Union[str, FieldLookup, Dict, None]]


def _str_to_exact(props: dict) -> Dict[str, Union[FieldLookup, Dict]]:
    # Ensures strings become Exact, Works on nested dicts
    for k, v in props.items():
        if isinstance(v, str):
            props[k] = Exact(v)
        elif isinstance(v, dict):
            props[k] = _str_to_exact(v)
        elif v is None:
            del props[k]

    return props


class Query(object):
    def __init__(self):
        """A query takes as input a graph, executes, and returns the next graph.

        >>> G2 = query.execute_networkx(G)

        Attributes
        ----------
        result_nodes: Set[int]:
            The set of node IDs which create the subgraph returned by the query.
        result_edges: Set[Tuple[int, int, int]]:
            The set of (u, v, k) tuples representing the edges which created the subgraph.
        """
        # The resulting node IDs
        self.result_nodes: Set[int] = set()

        # The resulting edge IDs
        self.result_edges: Set[Tuple[int, int, int]] = set()

        # Set of queries that came before or after it.
        self.downstream_query: Query = None
        self.upstream_query: Query = None

        self.upstream_nodes: Set[int] = set()
        self.upstream_edges: Set[Tuple[int, int, int]] = set()

    def get_upstream_results(self) -> Tuple[Set[int], Set[Tuple[int, int, int]]]:
        return self.upstream_query.result_nodes, self.upstream_query.result_edges

    def set_upstream_nodes(self):  # pragma: no cover
        self.upstream_nodes |= self.upstream_query.result_nodes
        self.upstream_edges |= self.upstream_query.result_edges

    def _test_values_with_lookups(
        self,
        value_to_test: Union[Node, Dict[str, Any]],
        lookup_tests: Dict[str, Union[FieldLookup, Dict]],
    ) -> bool:
        """Tests a node or dictionary against a configuration of lookup_tests.

        Parameters
        ----------
        value_to_test : Union[Node, Dict[str, Any]]
            The node or dict to test.
        lookup_tests : Dict[str, FieldLookup]
            The set of lookup_tests to test.

        Returns
        -------
        bool
            Did all of the tests pass?
        """

        # Auto pass if no tests.s
        if not lookup_tests:
            return True

        # Auto fail on empty value (given we have tests)
        if not value_to_test:
            return False

        results: List[bool] = []

        for attr_name, lookup in lookup_tests.items():
            if isinstance(lookup, dict):
                # recursivly check props against nested entrys (e.g is hashes dict in Process)
                if isinstance(value_to_test, Node):  # pragma: no cover
                    results.append(
                        self._test_values_with_lookups(
                            value_to_test=getattr(value_to_test, attr_name), lookup_tests=lookup
                        )
                    )
                else:
                    results.append(
                        self._test_values_with_lookups(
                            value_to_test=value_to_test.get(attr_name, {}), lookup_tests=lookup
                        )
                    )
            else:
                if isinstance(value_to_test, Node):
                    results.append(lookup.test(getattr(value_to_test, attr_name)))
                else:
                    results.append(lookup.test(value_to_test.get(attr_name)))

        return any(results)

    def execute_networkx(self, G: nx.Graph):  # pragma: no cover
        """Execute a query against a `networkx` graph."""
        raise NotImplementedError(f"NetworkX not supported for {self.__class__.__name__}")

    def __rshift__(self, other: "Query") -> "Query":
        """Implements Self >> Other == self.downstream_query = other

        Parameters
        ----------
        other : Query
            The other query to add.
        """
        self.downstream_query = other
        other.upstream_query = self
        return other

    def __lshift__(self, other: "Query") -> "Query":
        """Implements Self << Other == self.upstream_query = other

        Parameters
        ----------
        other : Query
            The other query to add.
        """
        other.downstream_query = self
        self.upstream_query = other
        return other

    def __or__(self, other: "Query") -> "ChainedQuery":
        """Allows queries to be combined through the `|` operator.
        The result of execution is the union of both subqueries.

        >>> query1 = Query(...)
        >>> query2 = Query(...)
        >>> chained = query1 | query2


        Parameters
        ----------
        other: Query
            The query to chain with.

        Returns
        -------
        ChainedQuery
            A chained query compromised of all three.
        """
        return ChainedQuery(self, other)


class ChainedQuery(Query):
    def __init__(self, *args: Query):
        """Executes multiple Querys, combining their outputs.

        Parameters
        ----------
        args: Query
            One ore more queries
        """
        self.queries = args
        super().__init__()

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        """Executes multiple queries against a `nx.Graph` object, combining their outputs into one subgraph.

        Parameters
        ----------
        G : nx.Graph
            Graph to execute queries against

        Returns
        -------
        nx.Graph
            Graph composed from the output graphs of the executed queries.
        """
        # Get the subgraphs

        subgraphs = []
        for query in self.queries:
            # Get the subgraphs
            subgraphs.append(query.execute_networkx(G))

            # add the reuslt_nodes, result_edges.
            self.result_edges |= query.result_edges
            self.result_nodes |= query.result_nodes

        # Compose the subgraphs
        H = subgraphs[0]
        for subgraph in subgraphs[1:]:
            H = nx.compose(H, subgraph)

        return H
