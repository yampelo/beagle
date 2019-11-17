from typing import Union

from beagle.nodes import File

from .base_query import FactoryMixin, PropsDict
from .edge import IntermediateEdgeByProps, IntermediateEdgeByPropsDescendants
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
    def that_was_written(descendants: bool = False):
        if descendants:
            return IntermediateEdgeByPropsDescendants(edge_type="Wrote")
        else:
            return IntermediateEdgeByProps(edge_type="Wrote")

    @staticmethod
    def that_was_copied(descendants: bool = False):
        if descendants:
            return IntermediateEdgeByPropsDescendants(edge_type="Copied To")
        else:
            return IntermediateEdgeByProps(edge_type="Copied To")
