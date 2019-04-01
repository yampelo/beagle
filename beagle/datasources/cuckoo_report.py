import json
from typing import Generator

from beagle.common.logging import logger
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
        yield {}
