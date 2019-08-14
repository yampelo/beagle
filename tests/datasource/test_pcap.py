from io import BytesIO
from scapy.all import Ether, PcapWriter, Packet
from typing import List
from beagle.datasources.pcap import PCAP


def packets_to_datasource_events(packets: List[Packet]) -> PCAP:
    f = BytesIO()
    PcapWriter(f).write(packets)
    f.seek(0)
    return PCAP(f)  # type: ignore


def test_single_ether_packet():

    packets = [Ether(src="ab:ab:ab:ab:ab:ab", dst="12:12:12:12:12:12")]

    events = list(packets_to_datasource_events(packets).events())
    assert len(events) == 1

    assert events[0]["src_mac"] == "ab:ab:ab:ab:ab:ab"
    assert events[0]["dst_mac"] == "12:12:12:12:12:12"
