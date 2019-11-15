from typing import Dict, Type, List

from beagle.backends import Backend, NetworkX
from beagle.nodes import Node

from .lookups import FieldLookup


class Statement(object):
    def execute(self, backend: Type[Backend]):
        if isinstance(backend, NetworkX):
            return self.execute_networkx(backend)

    def execute_networkx(self, backend: NetworkX):  # pragma: no cover
        raise NotImplementedError(f"NetworkX not supported for {self.__class__.__name__}")


class NodeByProps(Statement):
    def __init__(self, node_type: Type[Node], props: Dict[str, FieldLookup]):
        self.node_type = node_type
        self.props = props

    def execute_networkx(self, backend: NetworkX) -> List[Node]:
        result = []
        for node_id, data in backend.G.nodes(data=True):
            node = data["data"]

            if isinstance(node, self.node_type):
                if all([lookup.test(getattr(node, prop)) for prop, lookup in self.props.items()]):
                    result.append(node)
        return result
