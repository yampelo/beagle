from typing import Union, Type

from beagle.nodes import Process

from .base_statement import NodeByPropsReachable, FactoryMixin
from .lookups import FieldLookup


class FindProcess(FactoryMixin, NodeByPropsReachable):
    """Executes statements relevant to a Process"""

    @classmethod
    def with_command_line(
        cls: Type["FindProcess"], command_line: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"command_line": command_line})

    @classmethod
    def with_process_name(
        cls: Type["FindProcess"], process_image: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"process_image": process_image})

    @classmethod
    def with_process_path(
        cls: Type["FindProcess"], process_path: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(node_type=Process, props={"process_path": process_path})

    @classmethod
    def with_process_image_path(
        cls: Type["FindProcess"], process_image_path: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover

        return NodeByPropsReachable(
            node_type=Process, props={"process_image_path": process_image_path}
        )

    @classmethod
    def with_user(cls: Type["FindProcess"], user: Union[str, FieldLookup]) -> NodeByPropsReachable:
        return NodeByPropsReachable(node_type=Process, props={"user": user})

    @classmethod
    def with_md5_hash(
        cls: Type["FindProcess"], md5hash: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=Process, props={"hashes": {"md5": md5hash}})

    @classmethod
    def with_sha256_hash(
        cls: Type["FindProcess"], md5hash: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=Process, props={"hashes": {"sha256": md5hash}})

    @classmethod
    def with_sha1_hash(
        cls: Type["FindProcess"], md5hash: Union[str, FieldLookup]
    ) -> NodeByPropsReachable:  # pragma: no cover
        return NodeByPropsReachable(node_type=Process, props={"hashes": {"sha1": md5hash}})
