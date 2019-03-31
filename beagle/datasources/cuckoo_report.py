import json
from typing import Generator

from beagle.common.logging import logger
from beagle.datasources.base_datasource import DataSource


class CuckooReport(DataSource):
    name = "Cuckoo Sandbox Report"
    category = "Cuckoo Sandbox"  # The category this will output to.

    transformers = []  # type: ignore

    def __init__(self, cuckoo_report: str) -> None:
        self.report = json.load(open(cuckoo_report, "r"))

        logger.info("Set up Cuckoo Sandbox")

    def metadata(self) -> dict:
        return {}

    def events(self) -> Generator[dict, None, None]:
        yield {}
