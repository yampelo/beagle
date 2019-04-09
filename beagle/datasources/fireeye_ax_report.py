import datetime
import json
from typing import Generator

from beagle.common.logging import logger
from beagle.datasources.base_datasource import DataSource
from beagle.transformers.fireeye_ax_transformer import FireEyeAXTransformer


class FireEyeAXReport(DataSource):
    """Yields events one by one from a FireEyeAX Report and sends them
    to the generic transformer.

    The JSON report should look something like this::

        {
            "alert": [
                {
                    "explanation": {
                        "malwareDetected": {
                            ...
                        },
                        "cncServices": {
                            "cncService": [
                                ...
                        },
                        "osChanges": [
                            {
                                "process": [...],
                                "registry": [...],
                                ...
                        }
                    }
                }
            ]
        }

    Beagle looks at the *first* `alert` in the `alerts` array.

    Parameters
    ----------
    ax_report : str
        File path to the JSON AX Report, see class description for expected format.
    """

    name = "FireEye AX Report"
    category = "FireEye AX"
    transformers = [FireEyeAXTransformer]

    def __init__(self, ax_report: str):

        data = json.load(open(ax_report, "r"))

        self.appliance = data.get("appliance", "Unknown")

        if "alert" not in data or len(data["alert"]) == 0:
            self.alert = {}  # type: ignore
        else:
            self.alert = data["alert"][0]
            self.base_timestamp = int(
                datetime.datetime.strptime(
                    self.alert["occurred"], "%Y-%m-%d %H:%M:%S +0000"
                ).strftime("%s")
            )

        logger.info("Set up FireEyeAX Report")

    def metadata(self) -> dict:
        base_meta = {
            "hostname": self.appliance,
            "analyzed_on": self.alert["occurred"],
            "severity": self.alert["severity"],
            "alert_url": self.alert["alertUrl"],
            "alert": self.alert["explanation"]["malwareDetected"]["malware"][0]["name"]
            if self.alert != {}
            else "",
        }

        return base_meta

    def events(self) -> Generator[dict, None, None]:

        os_changes = self.alert.get("explanation", {}).get("osChanges", [{}])

        if (len(os_changes)) == 0:
            return
        else:
            for change_type, events in os_changes[0].items():

                if not isinstance(events, list):
                    events = [events]

                for event in events:

                    if not isinstance(event, dict):
                        continue

                    event["event_type"] = change_type
                    if "timestamp" in event:
                        event["timestamp"] = float(event["timestamp"] + self.base_timestamp)

                    yield event
