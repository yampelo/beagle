import email
from typing import Optional, Tuple, Union

from beagle.common import split_path
from beagle.constants import HashAlgos
from beagle.nodes import URI, Domain, File, IPAddress, Process
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
            elif event["mode"] == "http_request":
                return self.http_requests(event)
        elif event_type == "file":
            return self.file_events(event)
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

    def http_requests(
        self, event: dict
    ) -> Union[
        Tuple[Process, File, IPAddress, URI, Domain],
        Tuple[Process, File, IPAddress, URI],
        Tuple[Process, File, IPAddress],
    ]:
        """Transforms a single `http_request` network event. A typical event looks like::

            {
                "mode": "http_request",
                "protocol_type": "tcp",
                "ipaddress": "199.168.199.1",
                "destination_port": 80,
                "processinfo": {
                    "imagepath": "c:\\Windows\\System32\\svchost.exe",
                    "tainted": false,
                    "md5sum": "1234",
                    "pid": 1292
                },
                "http_request": "GET /some_route.crl HTTP/1.1~~Cache-Control: max-age = 900~~User-Agent: Microsoft-CryptoAPI/10.0~~Host: crl.microsoft.com~~~~",
                "timestamp": 433750
            }


        Parameters
        ----------
        event : dict
            The source `network` event with mode `http_request`

        Returns
        -------
        Tuple[Node]
            [description]
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
            timestamp=event["timestamp"],
            protocol=event["protocol_type"],
            port=event["destination_port"],
        )

        try:
            url, header = event["http_request"].split("~~", 1)

            method, uri_path, _ = url.split(" ")

            uri = URI(uri_path)

            headers = dict(email.message_from_string(header.replace("~~", "\n")).items())

            proc.http_request_to[uri].append(timestamp=event["timestamp"], method=method)

            if "Host" in headers:
                domain = Domain(headers["Host"])  # type: ignore

                domain.resolves_to[addr].append(timestamp=event["timestamp"])
                uri.uri_of[domain]

                return (proc, proc_file, addr, uri, domain)
            else:
                return (proc, proc_file, addr, uri)

        except (ValueError, KeyError):
            return (proc, proc_file, addr)

    def file_events(self, event: dict) -> Tuple[Process, File, File]:
        """Transforms a file event

        Example file event::

            {
                "mode": "created",
                "fid": { "ads": "", "content": 2533274790555891 },
                "processinfo": {
                    "imagepath": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                    "md5sum": "eb32c070e658937aa9fa9f3ae629b2b8",
                    "pid": 2956
                },
                "ntstatus": "0x0",
                "value": "C:\\Users\\admin\\AppData\\Local\\Temp\\sy24ttkc.k25.ps1",
                "CreateOptions": "0x400064",
                "timestamp": 9494
            }

        Parameters
        ----------
        event : dict
            The source event

        Returns
        -------
        Tuple[Process, File, File]
            The process, the process' image, and the file written.
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

        file_name, file_path = split_path(event["value"])
        file_node = File(file_name=file_name, file_path=file_path)

        if event["mode"] == "created":
            proc.wrote[file_node].append(timestamp=event["timestamp"])
        elif event["mode"] == "deleted":
            proc.deleted[file_node].append(timestamp=event["timestamp"])
        else:
            proc.accessed[file_node].append(timestamp=event["timestamp"])

        return (proc, proc_file, file_node)