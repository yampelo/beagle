from typing import Optional, Tuple, Union

from beagle.common import split_path
from beagle.constants import HashAlgos
from beagle.nodes import Domain, File, Process
from beagle.nodes.ip_address import IPAddress
from beagle.transformers.base_transformer import Transformer


class FireEyeAXTransformer(Transformer):
    name = "FireEye AX"

    def transform(self, event: dict) -> Optional[Tuple]:
        """Transformers the various events from the AX Report class.

        The only edge case is the network type, AX has multiple Nodes under
        one type when it comes to the network type. For example the following
        is a DNS event::


            {
                "mode": "dns_query",
                "protocol_type": "udp",
                "hostname": "foobar",
                "qtype": "Host Address",
                "processinfo": {
                    "imagepath": "C:\\ProgramData\\bloop\\some_proc.exe",
                    "tainted": true,
                    "md5sum": "....",
                    "pid": 3020
                },
                "timestamp": 27648
            }

        While the following is a TCP connection::

            {
                "mode": "connect",
                "protocol_type": "tcp",
                "ipaddress": "192.168.199.123",
                "destination_port": 3333,
                "processinfo": {
                    "imagepath": "C:\\ProgramData\\bloop\\some_proc.exe",
                    "tainted": true,
                    "md5sum": "...",
                    "pid": 3020
                },
                "timestamp": 28029
            }

        Both have the "network" event_type when coming from :py:class:`FireEyeAXReport`

        Parameters
        ----------
        event : dict
            The current event to transform.

        Returns
        -------
        Optional[Tuple]
            Tuple of nodes extracted from the event.
        """

        event_type = event.get("event_type")
        if event_type == "process":
            return self.process_events(event)
        elif event_type == "network":
            if event["mode"] in ["dns_query_answer", "dns_query"]:
                return self.dns_events(event)
            elif event["mode"] == "connect":
                return self.conn_events(event)

        return None

    def process_events(self, event: dict) -> Optional[Tuple[Process, File, Process, File]]:
        """Transformers events from the `process` entry.

        A single process entry looks like::

            {
                "mode": string,
                "fid": dict,
                "parentname": string,
                "cmdline": string,
                "sha1sum": "string,
                "md5sum": string,
                "sha256sum": string,
                "pid": int,
                "filesize": int,
                "value": string,
                "timestamp": int,
                "ppid": int
            },

        Parameters
        ----------
        event : dict
            The input event.

        Returns
        -------
        Optional[Tuple[Process, File, Process, File]]
            Parent and child processes, and the file nodes that represent their binaries.
        """

        if event.get("mode") != "started":
            return None

        process_image, process_image_path = split_path(event["value"])
        parent_image, parent_image_path = split_path(event["parentname"])

        proc = Process(
            process_image=process_image,
            process_image_path=process_image_path,
            command_line=event["cmdline"],
            process_id=int(event["pid"]),
            hashes={
                HashAlgos.MD5: event["md5sum"],
                HashAlgos.SHA1: event["sha1sum"],
                HashAlgos.SHA256: event["sha256sum"],
            },
        )

        proc_file = proc.get_file_node()

        proc_file.file_of[proc]

        parent = Process(
            process_image=parent_image,
            process_image_path=parent_image_path,
            process_id=int(event["ppid"]),
        )

        parent_file = parent.get_file_node()

        parent_file.file_of[parent]

        parent.launched[proc].append(timestamp=int(event["timestamp"]))

        return (proc, proc_file, parent, parent_file)

    def dns_events(
        self, event: dict
    ) -> Union[Tuple[Process, File, Domain], Tuple[Process, File, Domain, IPAddress]]:
        """Transforms a single DNS event

        Example event::

            {
                "mode": "dns_query",
                "protocol_type": "udp",
                "hostname": "foobar",
                "qtype": "Host Address",
                "processinfo": {
                    "imagepath": "C:\\ProgramData\\bloop\\some_proc.exe",
                    "tainted": true,
                    "md5sum": "....",
                    "pid": 3020
                },
                "timestamp": 27648
            }

        Optionally, if the event is "dns_query_answer", we can also extract the response.

        Parameters
        ----------
        event : dict
            source dns_query event

        Returns
        -------
        Tuple[Process, File, Domain]
            Process and its image, and the domain looked up
        """
        proc_info = event["processinfo"]
        process_image, process_image_path = split_path(proc_info["imagepath"])

        proc = Process(
            process_id=int(proc_info["pid"]),
            process_image=process_image,
            process_image_path=process_image_path,
        )

        proc_file = proc.get_file_node()
        proc_file.file_of[proc]

        domain = Domain(event["hostname"])

        proc.dns_query_for[domain].append(timestamp=int(event["timestamp"]))

        if "ipaddress" in event:
            addr = IPAddress(event["ipaddress"])
            domain.resolves_to[addr].append(timestamp=int(event["timestamp"]))
            return (proc, proc_file, domain, addr)
        else:
            return (proc, proc_file, domain)

    def conn_events(self, event: dict) -> Tuple[Process, File, IPAddress]:
        """Transforms a single connection event

        Example event::

            {
                "mode": "connect",
                "protocol_type": "tcp",
                "ipaddress": "199.168.199.123",
                "destination_port": 3333,
                "processinfo": {
                    "imagepath": "C:\\ProgramData\\bloop\\some_proc.exe",
                    "tainted": true,
                    "md5sum": "....",
                    "pid": 3020
                },
                "timestamp": 27648
            }

        Parameters
        ----------
        event : dict
            source dns_query event

        Returns
        -------
        Tuple[Process, File, IPAddress]
            Process and its image, and the destination address
        """
        proc_info = event["processinfo"]
        process_image, process_image_path = split_path(proc_info["imagepath"])

        proc = Process(
            process_id=int(proc_info["pid"]),
            process_image=process_image,
            process_image_path=process_image_path,
        )

        proc_file = proc.get_file_node()
        proc_file.file_of[proc]

        addr = IPAddress(event["ipaddress"])

        proc.connected_to[addr].append(
            protocol=event["protocol_type"],
            timestamp=event["timestamp"],
            port=int(event["destination_port"]),
        )

        return (proc, proc_file, addr)
