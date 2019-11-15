from typing import Any, Dict, List, Set, Tuple, Type, Union, cast

import networkx as nx

from beagle.nodes import Node

from .lookups import Exact, FieldLookup


def _str_to_exact(props: dict) -> Dict[str, Union[FieldLookup, Dict]]:
    # Ensures strings become Exact, Works on nested dicts
    for k, v in props.items():
        if isinstance(v, str):
            props[k] = Exact(v)
        elif isinstance(v, dict):
            props[k] = _str_to_exact(v)

    return props


class Statement(object):
    def __init__(self):
        """A statement is the base building block of a query. A statement takes as input a graph, executes,
        and returns the next graph.

        >>> G2 = statement.execute_networkx(G)

        Attributes
        ----------
        result_nodes: Set[int]:
            The set of node IDs which create the subgraph returned by the statement.
        result_edges: Set[Tuple[int, int, int]]:
            The set of (u, v, k) tuples representing the edges which created the subgraph.
        """
        # The resulting node IDs
        self.result_nodes: Set[int] = set()

        # The resulting edge IDs
        self.result_edges: Set[Tuple[int, int, int]] = set()

    def __or__(self, other: "Statement") -> "ChainedStatement":
        """Allows statements to be combined through the `|` operator.
        The result of execution is the union of both substatements.

        >>> statement1 = Statement(...)
        >>> statement2 = Statement(...)
        >>> chained = statement1 | statement2


        Parameters
        ----------
        other: Statement
            The statement to chain with.

        Returns
        -------
        ChainedStatement
            A chained statement compromised of all three.
        """
        return ChainedStatement(self, other)

    def execute_networkx(self, G: nx.Graph):  # pragma: no cover
        """Execute a statement against a `networkx` graph."""
        raise NotImplementedError(f"NetworkX not supported for {self.__class__.__name__}")

    def _test_values_with_lookups(
        self,
        value_to_test: Union[Node, Dict[str, Any]],
        lookup_tests: Dict[str, Union[FieldLookup, Dict]],
    ) -> bool:
        """Tests a node or dictionay against a configuration of lookup_tests.

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

        if not value_to_test:
            return False

        results: List[bool] = []

        for attr_name, lookup in lookup_tests.items():
            if isinstance(lookup, dict):
                # recursivly check props against nested entrys (e.g is hashes dict in Process)
                if isinstance(value_to_test, Node):
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


class FactoryMixin(object):
    """Mixin to prevent Statement Factories from calling execute methods.
    """

    def execute_networkx(self, G: nx.graph):
        raise UserWarning("Statement factories cannot be called directly")


class ChainedStatement(Statement):
    def __init__(self, *args: Statement):
        """Executes multiple Statements, combining their outputs.

        Parameters
        ----------
        args: Statement
            One ore more statements
        """
        self.statements = args
        super().__init__()

    def execute_networkx(self, G: nx.Graph) -> nx.Graph:
        """Executes multiple statements against a `nx.Graph` object, combining their outputs into one subgraph.

        Parameters
        ----------
        G : nx.Graph
            Graph to execute statements against

        Returns
        -------
        nx.Graph
            Graph composed from the output graphs of the executed statements.
        """
        # Get the subgraphs

        subgraphs = []
        for statement in self.statements:
            # Get the subgraphs
            subgraphs.append(statement.execute_networkx(G))

            # add the reuslt_nodes, result_edges.
            self.result_edges |= statement.result_edges
            self.result_nodes |= statement.result_nodes

        # Compose the subgraphs
        H = subgraphs[0]
        for subgraph in subgraphs[1:]:
            H = nx.compose(H, subgraph)

        return H


class NodeByProps(Statement):
    def __init__(self, node_type: Type[Node], props: Dict[str, Union[str, FieldLookup, Dict]]):
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

        self.result_nodes = set(subgraph_nodes)
        return G.subgraph(subgraph_nodes)


class EdgeByProps(Statement):
    def __init__(self, edge_type: str, props: Dict[str, Union[str, FieldLookup]]):
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
                    if self._test_values_with_lookups(entry, self.props):
                        subgraph_edges.append((u, v, k))
                        # can stop on first match
                        break

        self.result_edges = set(subgraph_edges)
        return G.edge_subgraph(subgraph_edges)


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

        self.result_nodes = set(subgraph_nodes)
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

        self.result_nodes = set(subgraph_nodes)
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

        self.result_nodes = set(subgraph_nodes)
        return G.subgraph(subgraph_nodes)
