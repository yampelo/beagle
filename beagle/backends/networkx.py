from collections import defaultdict
from typing import Optional

import networkx as nx

from beagle.backends.base_backend import Backend
from beagle.common import logger
from beagle.nodes import Node


class NetworkX(Backend):
    """NetworkX based backend. Other backends can subclass this backend in order to have access
    to the underlying NetworkX object.

    While inserting the Nodes into the graph, the NetworkX object does the following:

    1. If the ID of this node (calculated via `Node.__hash__`) is already in the graph, the node is
    updated with any properties which are in the new node but not the existing node.

    2. If we are inserting the an edge type that already exists between two
    nodes `u` and `v`, the edge data is combined.

    Notes
    ---------
    In `networkx`, adding the same node twice keeps the latest version of the node. Since
    a node that represents the same thing may appear twice in a log (for example, the same
    process might appear in a process creation event and a file write event).
    It's easier to simply update the nodes as you iterate over the `nodes` attribute.

    Parameters
    ----------
    metadata : dict, optional
        The metadata from the datasource.
    consolidate_edges: boolean, optional
        Controls if edges are consolidated. That is, if the edge of type q from u to v happens N times,
        should there be one edge from u to v with type q, or should there be N edges.

    Notes
    -------
    Putting
    """

    def __init__(
        self, metadata: dict = {}, consolidate_edges: bool = False, *args, **kwargs
    ) -> None:

        self.metadata = metadata
        self.consolidate_edges = consolidate_edges
        self.G = nx.MultiDiGraph(metadata=metadata)
        super().__init__(*args, **kwargs)

        logger.info("Initialized NetworkX Backend")

    def is_empty(self) -> bool:
        return len(self.G.nodes()) == 0

    @logger.catch
    def graph(self) -> nx.MultiDiGraph:
        """Generates the MultiDiGraph.

        Places the nodes in the Graph.

        Returns
        -------
        nx.MultiDiGraph
            The generated NetworkX object.
        """

        logger.info("Beginning graph generation.")

        for node in self.nodes:
            node_id = hash(node)
            self.insert_node(node, node_id)

        logger.info("Completed graph generation.")
        logger.info(f"Graph contains {len(self.G.nodes())} nodes and {len(self.G.edges())} edges.")

        return self.G

    def insert_node(self, node: Node, node_id: int) -> None:
        """Inserts a node into the graph, as well as all edges outbound from it.

        If a node with `node_id` already exists, the node data is updated using
        :py:meth:`update_node`.

        Parameters
        ----------
        node : Node
            Node object to insert
        no`de_id : int
            The ID of the node (`hash(node)`)
        """

        if node_id not in self.G.nodes:
            self.G.add_node(node_id, data=node)
        else:
            self.update_node(node, node_id)

        for edge_dict in node.edges:
            for dest_node, edge_data in edge_dict.items():

                edge_name = edge_data.__name__

                # If there's no data on the edges, insert at least one to represent
                # the edge exists
                if len(edge_data._events) == 0:
                    self.insert_edge(
                        u=node,  # Source node
                        v=dest_node,  # Dest Node
                        edge_name=edge_data.__name__,  # Edge name
                        data=None,
                    )
                else:
                    # Otherwise, insert all the edge instances.
                    for entry in getattr(edge_data, "_events", [None]):
                        if entry and "edge_name" in entry:
                            edge_name = entry.pop("edge_name")

                        self.insert_edge(
                            u=node,  # Source node
                            v=dest_node,  # Dest Node
                            edge_name=edge_name,  # Edge name
                            data=entry,
                        )

    def insert_edge(self, u: Node, v: Node, edge_name: str, data: Optional[dict]) -> None:
        """Insert an edge from `u` to `v` with type `edge_name` that contains data
        `data`.

        If the edge already exists, the data entry is appended to the existing data
        array.

        This results in a single edge between `u` and `v` per `edge_name`. And each
        occurence of that edge is represented by an entry in the `data` list.

        Parameters
        ----------
        u : Node
            Source Node object
        v : Node
            Destination Node object
        edge_name : str
            Edge Name
        data : dict
            Data entry to place on this edge.
        """
        logger.debug(f"Adding edge ({u})-[{edge_name}]->({v})")

        u_id = hash(u)
        v_id = hash(v)

        if v_id in self.G.nodes:
            self.update_node(node=v, node_id=v_id)
        else:
            # First time, make an array.
            self.G.add_node(v_id, data=v)

        # If we consolidate edges, the key is the edge name, and we update the data.
        if self.consolidate_edges:
            curr = self.G.get_edge_data(u=u_id, v=v_id, key=edge_name, default=None)
            if curr is None:
                self.G.add_edge(
                    u_for_edge=u_id,
                    v_for_edge=v_id,
                    key=edge_name,
                    data=([data] if data else []),
                    edge_name=edge_name,
                )
            elif data:
                curr = curr["data"]
                curr.append(data)
                nx.set_edge_attributes(
                    self.G, {(u_id, v_id, edge_name): {"data": curr, "edge_name": edge_name}}
                )

        # Otherwise, they key is assigned from NetworkX, and we add the edge type as a label:
        else:
            self.G.add_edge(
                u_for_edge=u_id, v_for_edge=v_id, data=([data] if data else []), edge_name=edge_name
            )

    def update_node(self, node: Node, node_id: int) -> None:
        """Update the attributes of a node. Since we may see the same Node in multiple events,
        we want to have the largest coverage of its attributes.
        * See :class:`beagle.nodes.node.Node` for how we determine two nodes are the same.

        This method updates the node already in the graph with the newest attributes
        from the passed in parameter `Node`

        Parameters
        ----------
        node : Node
            The Node object to use to update the node already in the graph
        node_id : int
            The hash of the Node. see :py:meth:`beagle.nodes.node.__hash__`

        """

        current_data = self.G.nodes[node_id]["data"]

        for key, value in node.__dict__.items():

            # NOTE: Skips edge combination because edge data is
            # added anyway in self.insert_node()
            if isinstance(value, defaultdict):
                continue

            # Always use the latest value.
            if value:
                setattr(current_data, key, value)

        nx.set_node_attributes(self.G, {node_id: {"data": current_data}})

    @classmethod
    def graph_to_json(cls, graph: nx.MultiDiGraph) -> dict:
        backend = cls(nodes=[])
        backend.G = graph
        return backend.to_json()

    def to_json(self) -> dict:
        """Convert the graph to JSON, which can later be used be read in using
        networkx::

        >>> backend = NetworkX(nodes=nodes)
        >>> G = backend.graph()
        >>> data = G.to_json()
        >>> parsed = networkx.readwrite.json_graph.node_link_graph(data)

        Returns
        -------
        dict
            node_link compatible version of the graph.
        """

        def node_to_json(node_id: int, node: Node) -> dict:
            return {
                "id": node_id,
                "properties": node.to_dict(),
                "_node_type": node.__name__,
                "_display": node._display,
                "_color": node.__color__,
            }

        def edge_to_json(edge_id: int, u: int, v: int, edge_key: str, edge_props: dict) -> dict:
            return {
                "id": edge_id,
                "source": u,
                "target": v,
                "type": edge_props["edge_name"],
                "properties": {"data": edge_props["data"]},
            }

        relationships = [
            edge_to_json(
                index + 1,  # Unique ID based on index.
                edge[0],  # Source node (u)
                edge[1],  # Destination node (v)
                edge[2],  # Edge type (e.g "wrote")
                edge[3],  # Edge data
            )
            for index, edge in enumerate(self.G.edges(data=True, keys=True))
        ]

        nodes = [
            node_to_json(node, node_data["data"]) for node, node_data in self.G.nodes(data=True)
        ]

        return {
            "directed": self.G.is_directed(),
            "multigraph": self.G.is_multigraph(),
            "nodes": nodes,
            "links": relationships,
        }
