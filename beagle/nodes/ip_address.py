from typing import List, Optional

from beagle.nodes import Node


class IPAddress(Node):

    __name__ = "IP Address"
    __color__ = "#87CEEB"

    ip_address: Optional[str]

    key_fields: List[str] = ["ip_address"]

    def __init__(self, ip_address: str = None):
        self.ip_address = ip_address

    @property
    def _display(self) -> str:
        return self.ip_address or super()._display
