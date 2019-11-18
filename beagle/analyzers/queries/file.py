from typing import Union

from beagle.nodes import File

from . import FactoryMixin, make_edge_query
from .base_query import PropsDict
from .lookups import FieldLookup
from .node import NodeByPropsReachable


class FindFile(FactoryMixin):
    """Executes queries relevant to a File"""

    @staticmethod
    def with_full_path(full_path: Union[str, FieldLookup]) -> NodeByPropsReachable:
        return NodeByPropsReachable(node_type=File, props={"full_path": full_path})

    @staticmethod
    def with_file_path(file_path: Union[str, FieldLookup]) -> NodeByPropsReachable:
        return NodeByPropsReachable(node_type=File, props={"file_path": file_path})

    @staticmethod
    def with_file_name(file_name: Union[str, FieldLookup]) -> NodeByPropsReachable:
        return NodeByPropsReachable(node_type=File, props={"file_name": file_name})

    @staticmethod
    def with_extension(
        extension: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=File, props={"extension": extension})

    @staticmethod
    def with_timestamp(
        timestamp: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=File, props={"timestamp": timestamp})

    @staticmethod
    def with_hashes(hashes: Union[str, FieldLookup]) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=File, props={"hashes": hashes})

    @staticmethod
    def with_props(props: PropsDict) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=File, props=props)

    @staticmethod
    def that_was_written(descendants=True, ancestors=False, reachable=False):
        return make_edge_query(
            edge_type="Wrote", descendants=descendants, ancestors=ancestors, reachable=reachable
        )

    @staticmethod
    def that_was_copied(descendants=True, ancestors=False, reachable=False):
        return make_edge_query(
            edge_type="Copied To", descendants=descendants, ancestors=ancestors, reachable=reachable
        )
