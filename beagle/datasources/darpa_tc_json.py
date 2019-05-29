# Datasource to support the "Transparent Computing Engagement" dataset
# https://github.com/darpa-i2o/Transparent-Computing
import os
from typing import Generator

from beagle.datasources.base_datasource import JSONDataSource
from beagle.transformers import DRAPATCTransformer


class DARPATCJson(JSONDataSource):
    name = "Darpa TC3 JSON"
    transformers = [DRAPATCTransformer]
    category = "Darpa TC3"

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        super().__init__(self.file_path, new_line_seperated=True)

    def metadata(self) -> dict:
        return {"filename": os.path.basename(self.file_path)}

    def events(self) -> Generator[dict, None, None]:
        """Events are in the format:

        "datum": {
            "com.bbn.tc.schema.avro.cdm18.Subject": {
             ...
        }

        This pops out the relevant info under the first key.
        """
        i = 0
        for event in super().events():
            event = event["datum"]

            for key, data in event.items():
                if "com.bbn.tc.schema.avro.cdm18." in key:
                    data["event_type"] = key.split("com.bbn.tc.schema.avro.cdm18.")[-1].lower()
                    yield data
                    break
            i += 1
            if i > 20000:
                break
