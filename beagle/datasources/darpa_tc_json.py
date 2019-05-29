# Datasource to support the "Transparent Computing Engagement" dataset
# https://github.com/darpa-i2o/Transparent-Computing
import os

from beagle.datasources.base_datasource import JSONDataSource
from beagle.transformers import DRAPATCTransformer


class DARPATCJson(JSONDataSource):
    name = "Darpa TC3 JSON"
    transformers = [DRAPATCTransformer]
    category = "Darpa TC3"

    def metadata(self) -> dict:
        return {"filename": os.path.basename(self.file_path)}
