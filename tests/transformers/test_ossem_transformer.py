import pytest

from beagle.nodes import Process, File
from beagle.transformers import OSSEMTransformer


@pytest.fixture
def transformer() -> OSSEMTransformer:
    return OSSEMTransformer(datasource=None)  # type: ignore


def test_unknown_event(transformer):
    assert transformer.transform({"event_type": "foooo"}) == ()


def test_make_process(transformer):
    test_event = {
        "event_creation_time": "1",
        "event_type": "launched",
        "process_id": "4756",
        "process_name": "conhost.exe",
        "process_path": "C:\\Windows\\System32\\conhost.exe",
        "process_command_line": "??\\C:\\WINDOWS\\system32\\conhost.exe 0xffffffff -ForceV1",
        "process_integrity_level": "Medium",
        "process_parent_guid": "A98268C1-9C2E-5ACD-0000-00100266AB00}",
        "process_parent_id": "240",
        "process_parent_name": "cmd.exe",
        "process_parent_path": "C:\\Windows\\System32\\cmd.exe",
        "process_parent_command_line": "C:\\WINDOWS\\system32\\cmd.exe",
    }

    nodes = transformer.transform(test_event)

    assert len(nodes) == 4

    proc: Process = nodes[0]
    proc_file: File = nodes[1]
    parent_proc: Process = nodes[2]
    parent_proc_file: File = nodes[3]

    assert {"timestamp": "1"} in parent_proc.launched[proc]
    assert proc in proc_file.file_of
    assert parent_proc in parent_proc_file.file_of

    assert proc.process_id == "4756"
    assert proc.process_image == "conhost.exe"
    assert proc.process_image_path == "C:\\Windows\\System32"
    assert proc.command_line == "??\\C:\\WINDOWS\\system32\\conhost.exe 0xffffffff -ForceV1"

    assert parent_proc.process_id == "240"
    assert parent_proc.process_image == "cmd.exe"
    assert parent_proc.process_image_path == "C:\\Windows\\System32"
    assert parent_proc.command_line == "C:\\WINDOWS\\system32\\cmd.exe"


@pytest.mark.parametrize(
    "eventtype,attribute",
    [("loaded", "loaded"), ("created", "wrote"), ("modified", "wrote"), ("downloaded", "wrote")],
)
def test_file_operations(transformer, eventtype, attribute):
    test_event = {
        "event_creation_time": "1",
        "event_type": eventtype,
        "process_id": "4756",
        "process_name": "conhost.exe",
        "process_path": "C:\\Windows\\System32\\conhost.exe",
        "process_command_line": "??\\C:\\WINDOWS\\system32\\conhost.exe 0xffffffff -ForceV1",
        "file_name": "cmd.exe",
        "file_path": "C:\\Windows\\System32\\cmd.exe",
    }
    nodes = transformer.transform(test_event)

    assert len(nodes) == 3

    proc: Process = nodes[0]
    proc_file: File = nodes[1]
    dest_file: File = nodes[2]

    assert proc in proc_file.file_of

    assert proc.process_id == "4756"
    assert proc.process_image == "conhost.exe"
    assert proc.process_image_path == "C:\\Windows\\System32"
    assert proc.command_line == "??\\C:\\WINDOWS\\system32\\conhost.exe 0xffffffff -ForceV1"

    assert dest_file.file_name == "cmd.exe"
    assert dest_file.file_path == "C:\\Windows\\System32"

    assert {"timestamp": "1"} in getattr(proc, attribute)[dest_file]
