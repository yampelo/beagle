from typing import Union, Type

from beagle.nodes import Process

from .base_statement import NodeByPropsReachable
from .lookups import Exact, FieldLookup


class FindProcess(NodeByPropsReachable):
    """Finds statements relevant to a Process

    Parameters
    ----------
    NodeByPropsReachable : [type]
        [description]
    """

    @classmethod
    def with_command_line(
        cls: Type["FindProcess"], command_line: Union[str, FieldLookup]
    ) -> "FindProcess":

        if isinstance(command_line, str):
            command_line = Exact(command_line)
        return cls(node_type=Process, props={"command_line": command_line})

    @classmethod
    def with_process_name(
        cls: Type["FindProcess"], process_image: Union[str, FieldLookup]
    ) -> "FindProcess":

        if isinstance(process_image, str):
            process_image = Exact(process_image)
        return cls(node_type=Process, props={"process_image": process_image})
