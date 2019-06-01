import pytest

from beagle.transformers import DRAPATCTransformer
from beagle.transformers.darpa_tc_transformer import TCFile, TCProcess, TCRegistryKey


@pytest.fixture
def transformer() -> DRAPATCTransformer:
    return DRAPATCTransformer(datasource=None)  # type: ignore


def test_make_process(transformer):
    test_event = {
        "event_type": "subject",
        "uuid": "B80F3806-0000-0000-0000-000000000020",
        "type": "SUBJECT_PROCESS",
        "cid": 4024,
        "parentSubject": {
            "com.bbn.tc.schema.avro.cdm18.UUID": "52071700-0000-0000-0000-000000000020"
        },
        "hostId": "0A00063C-5254-00F0-0D60-000000000070",
        "localPrincipal": "EC000000-0000-0000-0000-000000000060",
        "startTimestampNanos": 1522943310819901200,
        "unitId": None,
        "iteration": None,
        "count": None,
        "cmdLine": {"string": "/usr/bin/firefox"},
        "privilegeLevel": None,
        "importedLibraries": None,
        "exportedLibraries": None,
        "properties": {
            "map": {"tgid": "3934", "path": "/home/admin/Downloads/firefox/firefox", "ppid": "1874"}
        },
    }

    nodes = transformer.transform(test_event)

    proc: TCProcess = nodes[0]
    parent: TCProcess = nodes[1]
    assert proc.uuid == "B80F3806-0000-0000-0000-000000000020"
    assert proc.command_line == "/usr/bin/firefox"
    assert proc.process_image == "firefox"
    assert parent.uuid == "52071700-0000-0000-0000-000000000020"


def test_make_process_no_properties(transformer):
    test_event = {
        "event_type": "subject",
        "uuid": "B80F3806-0000-0000-0000-000000000020",
        "type": "SUBJECT_PROCESS",
        "cid": 4024,
        "parentSubject": {
            "com.bbn.tc.schema.avro.cdm18.UUID": "52071700-0000-0000-0000-000000000020"
        },
        "hostId": "0A00063C-5254-00F0-0D60-000000000070",
        "localPrincipal": "EC000000-0000-0000-0000-000000000060",
        "startTimestampNanos": 1522943310819901200,
        "unitId": None,
        "iteration": None,
        "count": None,
        "cmdLine": {"string": "/usr/bin/firefox"},
        "privilegeLevel": None,
        "importedLibraries": None,
        "exportedLibraries": None,
        "properties": None,
    }

    nodes = transformer.transform(test_event)

    proc: TCProcess = nodes[0]
    parent: TCProcess = nodes[1]
    assert proc.uuid == "B80F3806-0000-0000-0000-000000000020"
    assert proc.command_line == "/usr/bin/firefox"
    assert proc.process_image == "/usr/bin/firefox"
    assert parent.uuid == "52071700-0000-0000-0000-000000000020"


def test_make_process_no_parent(transformer):
    test_event = {
        "event_type": "subject",
        "uuid": "B80F3806-0000-0000-0000-000000000020",
        "type": "SUBJECT_PROCESS",
        "cid": 4024,
        "parentSubject": None,
        "hostId": "0A00063C-5254-00F0-0D60-000000000070",
        "localPrincipal": "EC000000-0000-0000-0000-000000000060",
        "startTimestampNanos": 1522943310819901200,
        "unitId": None,
        "iteration": None,
        "count": None,
        "cmdLine": {"string": "/usr/bin/firefox"},
        "privilegeLevel": None,
        "importedLibraries": None,
        "exportedLibraries": None,
        "properties": None,
    }

    nodes = transformer.transform(test_event)
    assert len(nodes) == 1


def test_make_file(transformer):
    test_event = {
        "uuid": "0100D00F-1400-2E00-0000-00004FA79C38",
        "event_type": "fileobject",
        "baseObject": {
            "hostId": "0A00063C-5254-00F0-0D60-000000000070",
            "permission": None,
            "epoch": None,
            "properties": {
                "map": {
                    "dev": "265289729",
                    "inode": "3014676",
                    "filename": "/home/admin/.cache/mozilla/firefox/pe11scpa.default/thumbnails/31017840be38acf6baf0e8f850d5c94b.png",
                }
            },
        },
        "type": "FILE_OBJECT_BLOCK",
        "fileDescriptor": None,
        "localPrincipal": {
            "com.bbn.tc.schema.avro.cdm18.UUID": "EC000000-0000-0000-0000-000000000060"
        },
        "size": None,
        "peInfo": None,
        "hashes": None,
    }
    nodes = transformer.transform(test_event)
    assert len(nodes) == 1

    fnode: TCFile = nodes[0]
    assert fnode.uuid == "0100D00F-1400-2E00-0000-00004FA79C38"
    assert fnode.host == "0A00063C-5254-00F0-0D60-000000000070"
    assert (
        fnode.full_path
        == "\\home\\admin\\.cache\\mozilla\\firefox\\pe11scpa.default\\thumbnails\\31017840be38acf6baf0e8f850d5c94b.png"
    )
    assert fnode.file_name == "31017840be38acf6baf0e8f850d5c94b.png"
    assert (
        fnode.file_path == "\\home\\admin\\.cache\\mozilla\\firefox\\pe11scpa.default\\thumbnails"
    )


def test_make_file_no_properties(transformer):
    test_event = {
        "uuid": "0100D00F-1400-2E00-0000-00004FA79C38",
        "event_type": "fileobject",
        "baseObject": {
            "hostId": "0A00063C-5254-00F0-0D60-000000000070",
            "permission": None,
            "epoch": None,
            "properties": None,
        },
        "type": "FILE_OBJECT_BLOCK",
        "fileDescriptor": None,
        "localPrincipal": {
            "com.bbn.tc.schema.avro.cdm18.UUID": "EC000000-0000-0000-0000-000000000060"
        },
        "size": None,
        "peInfo": None,
        "hashes": None,
    }
    nodes = transformer.transform(test_event)
    assert len(nodes) == 1

    fnode: TCFile = nodes[0]
    assert fnode.uuid == "0100D00F-1400-2E00-0000-00004FA79C38"
    assert fnode.host == "0A00063C-5254-00F0-0D60-000000000070"
    assert fnode.full_path == ""
    assert fnode.file_name is None
    assert fnode.file_path is None


def test_make_registry(transformer):
    test_event = {
        "event_type": "registrykeyobject",
        "uuid": "736F96AB-F043-4ED4-A456-D6F6DC3365FC",
        "baseObject": {
            "hostId": "47923ED7-29D4-4E65-ABA2-F70A4E74DCCD",
            "permission": None,
            "epoch": None,
            "properties": None,
        },
        "key": "\\REGISTRY\\USER\\S-1-5-21-231540947-922634896-4161786520-1001\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager\\Subscriptions\\280810",
        "value": {
            "com.bbn.tc.schema.avro.cdm18.Value": {
                "size": -1,
                "type": "VALUE_TYPE_SRC",
                "valueDataType": "VALUE_DATA_TYPE_LONG",
                "isNone": False,
                "name": {"string": "AccelerateCacheRefreshLastDetected"},
                "runtimeDataType": None,
                "valueBytes": {"bytes": "0000000000000000"},
                "provenance": None,
                "tag": None,
                "components": None,
            }
        },
        "size": None,
    }

    nodes = transformer.transform(test_event)
    assert len(nodes) == 1
    reg: TCRegistryKey = nodes[0]
    assert reg.uuid == "736F96AB-F043-4ED4-A456-D6F6DC3365FC"
    assert reg.key == "280810"
    assert reg.hive == "REGISTRY"
