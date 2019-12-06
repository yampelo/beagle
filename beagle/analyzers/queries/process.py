from typing import Union

from beagle.nodes import Process

from . import FactoryMixin, make_edge_query
from .base_query import PropsDict
from .lookups import FieldLookup
from .node import NodeByPropsReachable


class FindProcess(FactoryMixin):
    """Executes queries relevant to a Process"""

    @staticmethod
    def with_command_line(
        command_line: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"command_line": command_line})

    @staticmethod
    def with_process_name(
        process_image: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"process_image": process_image})

    @staticmethod
    def with_process_path(
        process_path: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"process_path": process_path})

    @staticmethod
    def with_process_image_path(
        process_image_path: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(
            node_type=Process, props={"process_image_path": process_image_path}
        )

    @staticmethod
    def with_user(user: Union[str, FieldLookup]) -> NodeByPropsReachable:

        return NodeByPropsReachable(node_type=Process, props={"user": user})

    @staticmethod
    def with_md5_hash(md5hash: Union[str, FieldLookup]) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"hashes": {"md5": md5hash}})

    @staticmethod
    def with_sha256_hash(
        sha256hash: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"hashes": {"sha256": sha256hash}})

    @staticmethod
    def with_sha1_hash(
        sha1hash: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"hashes": {"sha1": sha1hash}})

    @staticmethod
    def with_props(props: PropsDict) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=Process, props=props)

    @staticmethod
    def that_was_launched(descendants=False, ancestors=False, reachable=False):
        return make_edge_query(
            edge_type="Launched", descendants=descendants, ancestors=ancestors, reachable=reachable
        )
