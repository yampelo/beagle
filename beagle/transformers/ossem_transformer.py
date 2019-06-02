from typing import List, Optional, Tuple

from beagle.nodes import Process, File

from beagle.common import logger
from beagle.transformers.base_transformer import Transformer


class OSSEMTransformer(Transformer):
    """Transformer based on the formats defined here:
    https://github.com/Cyb3rWard0g/OSSEM/tree/master/common_information_model

    Parameters
    ----------
    Transformer : [type]
        [description]
    """

    name = "OSSEM"

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        logger.info("Created OSSEM Transformer.")

    def transform(self, event: dict) -> Optional[Tuple]:

        relationship = event["event_type"]

        if relationship == "created":
            return self.created(event)

        return tuple()

    def created(self, event: dict) -> Tuple[Process, File, Process, File]:

        proc = Process(
            process_id=event.get("process_id"),
            process_image=event.get("process_name"),
            process_image_path=event.get("process_path"),
            command_line=event.get("process_command_line"),
        )

        parent = Process(
            process_id=event.get("process_parent_id"),
            process_image=event.get("process_parent_path"),
            process_image_path=event.get("process_path"),
            command_line=event.get("process_parent_command_line"),
        )

        parent_file = parent.get_file_node()
        proc_file = proc.get_file_node()

        parent_file.file_of[parent]
        proc_file.file_of[proc]

        parent.launched[proc].append(timestamp=event["time"])

        return (proc, proc_file, parent, parent_file)
