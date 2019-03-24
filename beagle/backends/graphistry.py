import os

import graphistry
from beagle.backends.networkx import NetworkX
from beagle.common import logger
from beagle.config import Config


class Graphistry(NetworkX):
    def __init__(self, anonymize: bool = False, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        logger.info("Initialized Graphistry Backend")

        self.key = self._get_key()
        if self.key is None:
            raise RuntimeError(
                f"Please set the graphistry API key in either the GRAPHISTRY_API_KEY"
                + " or BEAGLE__GRAPHISTRY__API_KEY enviroment variables"
            )

    def _get_key(self) -> str:
        """Gets the graphistry API key from the enviroment variables or config.

        Returns
        -------
        str
            [description]
        """

        if "GRAPHISTRY_API_KEY" in os.environ:
            return os.environ["GRAPHISTRY_API_KEY"]
        else:
            return Config.get("graphistry", "api_key")

    def graph(self, render: bool = False):
        """Return the Graphistry URL for the graph, or an IPython Widget

        Parameters
        ----------
        render : bool, optional
            Should the result be a IPython widget? (default value is False, which returns the URL).
        Returns
        -------
        Union[str, IPython.core.display.HTML]
            str with URL to graphistry object when render if False, otherwise HTML widget for IPython.

        """

        G = super().graph()

        graphistry.register(self.key)

        return graphistry.bind(
            source="src", destination="dst", point_label="_display", edge_label="type"
        ).plot(G, render=render)

