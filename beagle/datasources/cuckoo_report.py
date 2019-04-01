import json
from typing import Dict, Generator

from beagle.common import split_path
from beagle.common.logging import logger
from beagle.constants import FieldNames, EventTypes
from beagle.datasources.base_datasource import DataSource
from beagle.transformers import GenericTransformer


class CuckooReport(DataSource):
    """Yields events from a cuckoo sandbox report.

    Cuckoo now provides a nice summary for each process under the "generic" summary tab::

        {
            "behavior": {
                "generic": [
                    {
                        'process_path': 'C:\\Users\\Administrator\\AppData\\Local\\Temp\\It6QworVAgY.exe',
                        'process_name': 'It6QworVAgY.exe',
                        'pid': 2548,
                        'ppid': 2460,
                        'summary': {
                            "directory_created" : [...],
                            "dll_loaded" : [...],
                            "file_opened" : [...],
                            "regkey_opened" : [...],
                            "file_moved" : [...],
                            "file_deleted" : [...],
                            "file_exists" : [...],
                            "mutex" : [...],
                            "file_failed" : [...],
                            "guid" : [...],
                            "file_read" : [...],
                            "regkey_re" : [...]
                            ...
                        },

                    }
                ]
            }
        }

    Using this, we can crawl and extract out all activity for a specific process.

    Notes
    ---------
    It's impossible to associate network traffic with a specific process.

    Parameters
    ----------
    cuckoo_report : str
        The file path to the cuckoo sandbox report.
    """

    name = "Cuckoo Sandbox Report"
    category = "Cuckoo Sandbox"  # The category this will output to.

    # The events object yields both the API calls and the prettified version.
    transformers = [GenericTransformer]

    def __init__(self, cuckoo_report: str) -> None:
        self.report = json.load(open(cuckoo_report, "r"))
        self.behavior = self.report["behavior"]

        self.processes: Dict[int, dict] = {}
        logger.info("Set up Cuckoo Sandbox")

    def metadata(self) -> dict:
        return {
            "machine": self.report["info"]["machine"]["name"],
            "package": self.report["info"]["package"],
            "score": self.report["info"]["score"],
            "report_id": self.report["info"]["id"],
            "name": self.report["target"].get("file", {"name": ""})["name"],
            "category": self.report["target"]["category"],
            "type": self.report["target"].get("file", {"type": ""})["type"],
        }

    def events(self) -> Generator[dict, None, None]:

        self.processes: Dict[int, dict] = self.identify_processes()

        # First, do process launching.
        yield from self.process_tree()

        # for each process, iterate over it's summary
        for process_summary in self.behavior["generic"]:

            # get the parent
            process = self.processes[int(process_summary["pid"])]

            # Yieled strucutred events.
            for func in [self._basic_file_events]:
                yield from func(process_summary["summary"], process)

    def identify_processes(self) -> Dict[int, dict]:
        """The `generic` tab contains an array of processes. We can iterate over it to quickly generate
        `Process` entries for later. After grabbing all processes, we can walk the "processtree" entry
        to update them with the command lines.


        Returns
        -------
        None
        """

        processes = {}

        for process in self.behavior["generic"]:

            proc_name, proc_path = split_path(process["process_path"])

            processes[int(process["pid"])] = {
                FieldNames.PROCESS_IMAGE: proc_name,
                FieldNames.PROCESS_IMAGE_PATH: proc_path,
                FieldNames.PROCESS_ID: int(process["pid"]),
            }

        return processes

    def process_tree(self) -> Generator[dict, None, None]:
        def process_single_entry(entry: dict) -> Generator[dict, None, None]:

            current_proc = self.processes[int(entry["pid"])]
            current_proc[FieldNames.COMMAND_LINE] = entry["command_line"]
            self.processes[int(entry["pid"])] = current_proc.copy()

            children = entry.get("children", [])

            # If the parent pid is not in the processes, then we need to make an artifical node.
            if entry["ppid"] not in self.processes:
                yield {
                    FieldNames.EVENT_TYPE: EventTypes.PROCESS_LAUNCHED,
                    FieldNames.TIMESTAMP: entry["first_seen"],
                    FieldNames.PARENT_PROCESS_ID: entry["ppid"],
                    FieldNames.PARENT_PROCESS_IMAGE: "Unknown",
                    FieldNames.PARENT_PROCESS_IMAGE_PATH: "\\",
                    FieldNames.PARENT_COMMAND_LINE: "",
                    **current_proc,
                }

            if len(children) > 0:

                for child in children:

                    child_proc = self.processes[int(child["pid"])]
                    child_proc[FieldNames.COMMAND_LINE] = child["command_line"]
                    self.processes[int(child["pid"])] = child_proc.copy()

                    current_as_parent = self._convert_to_parent_fields(current_proc.copy())

                    yield {
                        FieldNames.EVENT_TYPE: EventTypes.PROCESS_LAUNCHED,
                        FieldNames.TIMESTAMP: child["first_seen"],
                        **current_as_parent,
                        **child_proc,
                    }

                    yield from process_single_entry(child)

        for entry in self.behavior.get("processtree", []):
            yield from process_single_entry(entry)

    def _basic_file_events(
        self, process_summary: dict, process: dict
    ) -> Generator[dict, None, None]:

        event_type_mappings = {
            "file_deleted": EventTypes.FILE_DELETED,
            "file_opened": EventTypes.FILE_OPENED,
            "file_failed": EventTypes.FILE_OPENED,
            "file_read": EventTypes.FILE_OPENED,
            "file_written": EventTypes.FILE_WRITTEN,
            "dll_loaded": EventTypes.LOADED_MODULE,
            "file_attribute_changed": EventTypes.FILE_OPENED,
        }

        for entry_key, event_type in event_type_mappings.items():

            for file_path in process_summary.get(entry_key, []):

                # Ignore directorys
                if file_path.endswith("\\"):
                    continue

                file_name, file_path = split_path(file_path)

                yield {
                    FieldNames.FILE_NAME: file_name,
                    FieldNames.FILE_PATH: file_path,
                    FieldNames.EVENT_TYPE: event_type,
                    **process,
                }
