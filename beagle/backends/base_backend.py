from abc import ABCMeta, abstractmethod
from typing import List

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
    def graph(self) -> None:
        """When this method is called, the backend should take in the
        passed in `Node` array and produce a graph.
        """

        raise NotImplementedError("Backend.graph() is not implemented!")

    def to_json(self) -> dict:
        raise NotImplementedError("Backend.to_json() is not implemented!")
