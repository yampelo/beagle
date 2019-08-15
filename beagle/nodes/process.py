from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional

from beagle.nodes.domain import URI, Domain
from beagle.nodes.edge import Edge
from beagle.nodes.file import File
from beagle.nodes.ip_address import IPAddress
from beagle.nodes.node import Node
from beagle.nodes.registry import RegistryKey


class Launched(Edge):
    __name__ = "Launched"

    timestamp: int  # Array of process launch times

    def __init__(self) -> None:
        super().__init__()


class Wrote(Edge):
    __name__ = "Wrote"

    contents: Optional[str]  # Array of contents of writes
    timestamp: int  # Array of timestamps of writes

    def __init__(self) -> None:
        super().__init__()


class Accessed(Edge):
    __name__ = "Accessed"

    timestamp: int

    def __init__(self) -> None:
        super().__init__()


class Deleted(Edge):
    __name__ = "Deleted"

    timestamp: int

    def __init__(self) -> None:
        super().__init__()


class Copied(Edge):
    __name__ = "Copied"

    timestamp: int

    def __init__(self) -> None:
        super().__init__()


class Loaded(Edge):
    __name__ = "Loaded"

    timestamp: int

    def __init__(self) -> None:
        super().__init__()


class ConnectedTo(Edge):
    __name__ = "Connected To"

    port: int
    protocol: Optional[str]
    timestamp: int
    payload: Optional[str]

    def __init__(self) -> None:
        super().__init__()


class HTTPRequestTo(Edge):
    __name__ = "HTTP Request To"

    user_agent: Optional[str]
    method: Optional[str]
    header: Optional[str]
    timestamp: int

    def __init__(self) -> None:
        super().__init__()

    @property
    def _display(self):
        return self.method or super()._display()


class DNSQueryFor(Edge):
    __name__ = "DNS Query For"

    timestamp: int
    record_type: Optional[str]

    def __init__(self) -> None:
        super().__init__()


class ChangedValue(Edge):
    __name__ = "Changed Value"

    value: Optional[str]
    timestamp: int

    def __init__(self) -> None:
        super().__init__()


class CreatedKey(Edge):
    __name__ = "Created Key"

    timestamp: int
    value: Optional[str]

    def __init__(self) -> None:
        super().__init__()


class ReadKey(Edge):
    __name__ = "Read Key"

    timestamp: int
    value: Optional[str]

    def __init__(self) -> None:
        super().__init__()


class DeletedValue(Edge):
    __name__ = "Deleted Value"

    timestamp: int
    value: Optional[str]

    def __init__(self) -> None:
        super().__init__()


class DeletedKey(Edge):
    __name__ = "Deleted Key"

    timestamp: int
    value: Optional[str]

    def __init__(self) -> None:
        super().__init__()


class Process(Node):
    __name__ = "Process"
    __color__ = "#FF0000"
    key_fields: List[str] = ["host", "process_id", "process_image"]

    host: Optional[str]
    user: Optional[str]
    process_id: Optional[int]
    process_path: Optional[str]
    process_image: Optional[str]
    process_image_path: Optional[str]
    command_line: Optional[str]
    hashes: Optional[Dict[str, str]] = {}

    # Process edges
    launched: DefaultDict["Process", Launched]  # List of launched processes

    # File edges
    wrote: DefaultDict[File, Wrote]  # List of files written
    accessed: DefaultDict[File, Accessed]  # List of files Access.
    loaded: DefaultDict[File, Loaded]  # List of files loaded (e.g DLLs)
    deleted: DefaultDict[File, Deleted]  # List of files deleted

    # List of copied files. NOTE: There'll be an edge from the file to the
    # dest file. Process -[Copied] -> File - [Copied To] -> File
    copied: DefaultDict[File, Copied]

    # Network edges
    connected_to: DefaultDict[IPAddress, ConnectedTo]  # List of Network Connections
    http_request_to: DefaultDict[URI, HTTPRequestTo]  # List of HTTP Requests
    dns_query_for: DefaultDict[Domain, DNSQueryFor]  # List of DNS Lookups

    # Registry edges
    changed_value: DefaultDict[RegistryKey, ChangedValue]
    created_key: DefaultDict[RegistryKey, CreatedKey]
    deleted_value: DefaultDict[RegistryKey, DeletedValue]
    deleted_key: DefaultDict[RegistryKey, DeletedKey]
    read_key: DefaultDict[RegistryKey, ReadKey]

    def __init__(
        self,
        host: str = None,
        process_id: int = None,
        user: str = None,
        process_image: str = None,
        process_image_path: str = None,
        command_line: str = None,
        hashes: Dict[str, str] = {},
    ) -> None:
        self.host = host
        self.process_id = process_id
        self.user = user
        self.process_image = process_image
        self.process_image_path = process_image_path
        self.command_line = command_line
        self.hashes = hashes

        if process_image_path and process_image:
            if process_image_path[-1] == "\\":
                self.process_path = f"{process_image_path}{process_image}"
            else:
                self.process_path = f"{process_image_path}\\{process_image}"

        # Edge dicts
        self.wrote = defaultdict(Wrote)
        self.accessed = defaultdict(Accessed)
        self.copied = defaultdict(Copied)
        self.launched = defaultdict(Launched)
        self.deleted = defaultdict(Deleted)
        self.connected_to = defaultdict(ConnectedTo)
        self.http_request_to = defaultdict(HTTPRequestTo)
        self.dns_query_for = defaultdict(DNSQueryFor)
        self.loaded = defaultdict(Loaded)
        self.changed_value = defaultdict(ChangedValue)
        self.created_key = defaultdict(CreatedKey)
        self.deleted_value = defaultdict(DeletedValue)
        self.read_key = defaultdict(ReadKey)
        self.deleted_key = defaultdict(DeletedKey)

    def get_file_node(self) -> File:
        return File(
            host=self.host,
            file_path=self.process_image_path,
            file_name=self.process_image,
            hashes=self.hashes,
        )

    @property
    def edges(self) -> List[DefaultDict]:
        return [
            self.wrote,
            self.accessed,
            self.copied,
            self.launched,
            self.deleted,
            self.connected_to,
            self.http_request_to,
            self.dns_query_for,
            self.loaded,
            self.changed_value,
            self.created_key,
            self.deleted_value,
            self.deleted_key,
            self.read_key,
        ]

    @property
    def _display(self) -> str:
        return self.process_image or super()._display
