from beagle.common import logger
from beagle.transformers.base_transformer import Transformer


class DRAPATCTransformer(Transformer):

    name = "DARPA TC"

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        logger.info("Created Windows EVTX Transformer.")
