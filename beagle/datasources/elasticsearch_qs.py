import time
import ssl
import urllib
from typing import Generator

from beagle.common.logging import logger
from beagle.config import Config
from beagle.datasources.base_datasource import ExternalDataSource
from beagle.transformers.generic_transformer import GenericTransformer

class ElasticSearchQSSerach(ExternalDataSource):
    """Datasource which allows transforming the results of a Elasticsearch Query String search into a
    graph.

    Parameters
    ----------
    index : str
        Elasticsearch index, by default "logs-*"
    query : str
        Elasticsearch query string, by default "*"
    earilest : str, optional
            The earliest time modifier, by default "-7d"
    latest : str, optional
            The latest time modifier, by default "now"
    Raises
    ------
    RuntimeError
        If there are no Elasticsearch credentials configured.
    """

    name = "Elasticsearch Query String"
    transformers = [GenericTransformer]
    category = "Elasticsearch"
    def __init__(self, index: str = "logs-*", query: str = "*",  earliest: str = "-7d", latest: str = "now"):
        """Creates a splunk query to pull data from

        Parameters
        ----------
        index : str
            Elasticsearch index, by default "logs-*"
        query : str
            Elasticsearch query string, by default "*"
        earilest : str, optional
            The earliest time modifier, by default "-7d"
        latest : str, optional
            The latest time modifier, by default "now"
        """

        self.earliest = earliest
        self.latest = latest
        self.index = index
        self.query = query
        self.client = self.setup_session()

    def setup_session(self):  # pragma: no cover
        from elasticsearch import Elasticsearch
        logger.info("CONFIG:")
        logger.info(Config.get("elasticsearch", "host"))
        logger.info(Config.get("elasticsearch", "scheme"))
        logger.info(Config.get("elasticsearch", "username"))    
        logger.info(Config.get("elasticsearch", "password"))
        logger.info(int(Config.get("elasticsearch", "port", fallback=9200)))


        client_kwargs = {
            "host": Config.get("elasticsearch", "host"),
            "scheme": Config.get("elasticsearch", "scheme"), 
            "port": int(Config.get("elasticsearch", "port", fallback=9200)),
        }
        if Config.get("elasticsearch", "username") and Config.get("elasticsearch", "password"):
            client_kwargs["http_auth"] = (
                Config.get("elasticsearch", "username"),             
                Config.get("elasticsearch", "password"),
            )
        logger.info(client_kwargs)

        logger.info(f"Creating Elasticsearch client for host={client_kwargs['host']}")
        return Elasticsearch(**client_kwargs)

    def events(self) -> Generator[dict, None, None]:
        query = {
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                                    "query": self.query
                        }
                    },                   
                    "filter": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": "now" + self.earliest,
                                    "lte": "now"
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        data = self.client.search(index=self.index, body=query, scroll='2m', size=100)

        # Get the scroll ID
        sid = data['_scroll_id']
        scroll_size = len(data['hits']['hits'])

        while scroll_size > 0:
            # Before scroll, process current batch of hits
            for item in data['hits']['hits']:
                source = item['_source']
                source['_id'] = item["_id"]
                yield source
            data = self.client.scroll(scroll_id=sid, scroll='2m')

            # Update the scroll ID
            sid = data['_scroll_id']

            # Get the number of results that returned in the last scroll
            scroll_size = len(data['hits']['hits'])

    def metadata(self) -> dict:  # pragma: no cover
        return {
            "index": self.index,
            "query": self.query,
            "earliest": self.earliest,
            "latest": self.latest,
        }
