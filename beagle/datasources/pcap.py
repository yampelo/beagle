from typing import Dict, Generator, cast


from beagle.common import logger
from beagle.datasources.base_datasource import DataSource
from beagle.transformers.generic_transformer import GenericTransformer


class PCAP(DataSource):
    """Yields events from a PCAP file.

    Parameters
    ----------
    pcap_file : str
        path to a PCAP file.
    """

    name = "PCAP File"
    transformers = [GenericTransformer]
    category = "PCAP"

    def __init__(self, pcap_file: str) -> None:

        self.pcap_file = pcap_file
        self._imported_scapy = False

    def metadata(self) -> dict:
        return {}

    def _get_rdpcap(self):

        if not self._imported_scapy:
            logger.info("Loading Scapy")
            from scapy.all import rdpcap

            logger.info("Scapy Loaded")

            self._imported_scapy = True

        return rdpcap

    def events(self):  # -> Generator[dict, None, None]:
        reader = self._get_rdpcap()

        from scapy.all import Ether, IP, TCP
        from scapy.layers.http import HTTPRequest

        logger.info("Reading PCAP File")

        pcap = reader(self.pcap_file)

        layers_data = {
            Ether: {
                "src_mac": lambda layer: layer.fields["src"],
                "dst_mac": lambda layer: layer.fields["dst"],
            },
            IP: {
                "src_ip": lambda layer: layer.fields["src"],
                "dst_ip": lambda layer: layer.fields["dst"],
                # returns protocol as a human readable string.
                "protocol": lambda layer: layer.get_field("proto").i2s[layer.fields["proto"]],
            },
            TCP: {
                "sport": lambda layer: layer.fields["sport"],
                "dport": lambda layer: layer.fields["dport"],
            },
            HTTPRequest: {
                "http_method": lambda layer: layer.fields["Method"],
                "uri": lambda layer: layer.fields["Path"],
                "http_dest": lambda layer: layer.fields.get("Host"),
            },
        }

        packet_type = "Ether"
        for packet in pcap:

            packet_data = {}
            for layer_name, config in layers_data.items():

                if not packet.haslayer(layer_name):
                    continue

                packet_type = layer_name.__name__

                layer = packet[layer_name]

                for name, processor in config.items():
                    packet_data[name] = processor(layer)

            packet_data["event_type"] = packet_type
            yield packet_data
