from typing import List, Optional, Tuple, Union

from beagle.common import logger
from beagle.nodes import Process
from beagle.transformers.base_transformer import Transformer


# Custom Node classes to use the UUID in TC
class TCProcess(Process):
    key_fields: List[str] = ["uuid"]
    uuid: Optional[str]

    def __init__(self, uuid: str = None, *args, **kwargs) -> None:
        self.uuid = uuid
        super().__init__(*args, **kwargs)


class DRAPATCTransformer(Transformer):

    name = "DARPA TC"

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        logger.info("Created Darpa Transperant Computing Transformer.")

    def transform(self, event: dict) -> Optional[Tuple]:
        event_type = event["event_type"]

        if event_type == "subject" and event["type"] == "SUBJECT_PROCESS":
            return self.make_subject(event)

        return tuple()

    def make_subject(self, event: dict) -> Union[Tuple[TCProcess], Tuple[TCProcess, TCProcess]]:

        if event.get("cmdLine"):
            proc_cmdline = event["cmdLine"]["string"]
        else:
            proc_cmdline = None

        proc = TCProcess(uuid=event["uuid"], process_image=proc_cmdline, command_line=proc_cmdline)
        if event.get("parentSubject"):

            parent = TCProcess(uuid=event["parentSubject"]["com.bbn.tc.schema.avro.cdm18.UUID"])

            parent.launched[proc]

            return (proc, parent)
        else:
            return (proc,)
