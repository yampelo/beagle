from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Tuple

from beagle.common import logger
from beagle.nodes import URI, Domain, IPAddress, Node
from beagle.nodes.process import ConnectedTo, DNSQueryFor, HTTPRequestTo
from beagle.transformers.base_transformer import Transformer


class Host(IPAddress):
    __name__ = "Host"
    __color__ = "#E69500"

    mac: Optional[str]
    ip_address: Optional[str]

    key_fields: List[str] = ["ip_address", "mac"]
    connected_to: DefaultDict["Host", ConnectedTo]
    http_request_to: DefaultDict[URI, HTTPRequestTo]
    dns_query_for: DefaultDict[Domain, DNSQueryFor]  # List of DNS Lookups

    def __init__(self, mac: str, ip_address: str) -> None:
        self.mac = mac
        self.ip_address = ip_address

        self.connected_to = defaultdict(ConnectedTo)

        self.http_request_to = defaultdict(HTTPRequestTo)
        self.dns_query_for = defaultdict(DNSQueryFor)


class PCAPTransformer(Transformer):
    name = "PCAP"

    def __init__(self, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        logger.info("Created PCAP Transformer")

    def transform(self, event: Dict) -> Optional[Tuple[Node, ...]]:

        event_type = event["event_type"]

        # Skip all ether events, no src/dst IP
        if event_type in ["Ether", "IP"] or "src_ip" not in event or "dst_ip" not in event:
            return None

        src = Host(ip_address=event["src_ip"], mac=event["src_mac"])
        dst = Host(ip_address=event["dst_ip"], mac=event["dst_mac"])

        src.connected_to[dst].append(
            port=event["dport"],
            protocol=event["protocol"],
            payload=event["payload"],
            timestamp=event["timestamp"],
        )

        if event_type == "HTTPRequest":
            dom = Domain(event["http_dest"])
            uri = URI(event["uri"])
            src.http_request_to[uri].append(
                method=event["http_method"], timestamp=event["timestamp"]
            )

            dom.resolves_to[dst]

            uri.uri_of[dom]
            return (src, dst, dom, uri)

        if event_type == "DNS":
            if event["qname"][-1] == ".":
                event["qname"] = event["qname"][:-1]
            dom = Domain(event["qname"])

            src.dns_query_for[dom].append(record_type=event["qtype"], timestamp=event["timestamp"])
            if "qanswer" in event:
                ip = IPAddress(event["qanswer"])
                dom.resolves_to[ip].append(timestamp=event["timestamp"])
                return (src, dom, ip, dst)

            return (src, dom, dst)

        return (src, dst)
