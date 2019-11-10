from abc import ABCMeta, abstractmethod
from typing import List, Any, Union

from beagle.nodes import Node


class Backend(object, metaclass=ABCMeta):
    """Abstract Backend Class. All Backends must implement the
    `graph()` method in order to properly function.

    When creating a new backend, you should really subclass the NetworkX class instead,
    and work on translating the NetworkX object to the other datasource.

    See :class:`beagle.backends.networkx.NetworkX`

    Parameters
    ----------
    nodes : List[Node]
        Nodes produced by the transformer.

    Example
    ----------
    >>> nodes = FireEyeHXTransformer(datasource=HXTriage('test.mans'))
    >>> backend = BackEndClass(nodes=nodes)
    >>> backend.graph()
    """

    def __init__(self, nodes: List[Node]) -> None:
        self.nodes = nodes

    @abstractmethod
    def graph(self) -> Union[str, Any]:
        """When this method is called, the backend should take in the
        passed in `Node` array and produce a graph.
        """

        raise NotImplementedError("Backend.graph() is not implemented!")

    def add_nodes(self, nodes: List[Node]):
        """This function should allow (or raise an error if not possible to) a user to add additional
        nodes to an already existing graph.

        Parameters
        ----------
        nodes : List[Node]
            The new nodes to add to the graph.
        """

        raise NotImplementedError("Backend.add_nodes() is not imeplemnted")

    def to_json(self) -> dict:
        raise NotImplementedError("Backend.to_json() is not implemented!")

    @abstractmethod
    def is_empty(self) -> bool:
        """Returns true if there wasn't a graph created.
        """
        raise NotImplementedError()
