import time
import ssl
import urllib
from typing import Generator

from beagle.common.logging import logger
from beagle.config import Config
from beagle.datasources.base_datasource import ExternalDataSource
from beagle.transformers.generic_transformer import GenericTransformer


def request(url, message, **kwargs):
    method = message["method"].lower()
    data = message.get("body", "") if method == "post" else None

    if isinstance(data, str):
        data = data.encode("utf-8")

    headers = dict(message.get("headers", []))

    req = urllib.request.Request(url, data, headers)
    try:
        response = urllib.request.urlopen(req, context=ssl._create_unverified_context())
    except urllib.error.HTTPError as response:
        return {
            "status": response.code,
            "reason": response.msg,
            "headers": dict(response.info()),
            "body": response,
        }

    return {
        "status": response.code,
        "reason": response.msg,
        "headers": dict(response.info()),
        "body": response,
    }


def handler():
    return request


class SplunkSPLSearch(ExternalDataSource):
    """Datasource which allows transforming the results of a Splunk search into a
    graph.

    Parameters
    ----------
    spl : str
        The splunk search to transform

    Raises
    ------
    RuntimeError
        If there are no Splunk credentials configured.
    """

    name = "Splunk SPL Search"
    transformers = [GenericTransformer]
    category = "Splunk"

    def __init__(self, spl: str, *args, **kwargs):

        self.spl = spl
        self.client = self.setup_session()

    def setup_session(self):
        import splunklib.client as client

        client_kwargs = {
            "host": Config.get("splunk", "host"),
            "username": Config.get("splunk", "username"),
            "password": Config.get("splunk", "password"),
            "port": int(Config.get("splunk", "port")),
        }

        return client.connect(sharing="global", **client_kwargs, handler=handler())

    def events(self) -> Generator[dict, None, None]:
        from splunklib.client import Job

        job: Job = self.create_search(self.spl, query_kwargs={"exec_mode": "normal"})

        self.sid = job.sid

        while not job.is_done():
            time.sleep(5)

        for result in self.get_results(job, count=100000000):
            yield result

    def metadata(self) -> dict:
        return {"sid": self.sid, "spl": self.spl[:45]}

    def create_search(self, query: str, query_kwargs: dict):
        """Creates a splunk search with `query` and `query_kwargs` using `splunk_client`

        Returns
        -------
        Job
            A splunk Job object.
        """

        return self.client.jobs.create(query, **query_kwargs)

    def get_results(self, job, count: int) -> list:  # pragma: no cover
        """Return events from a finished Job as an array of dictionaries.

        Parameters
        ----------
        job : Job
            Job object to pull results from.

        Returns
        -------
        list
            The results of the search.
        """
        import splunklib.results as results

        out = [result for result in results.ResultsReader(job.results(count=count))]
        job.cancel()
        return out
