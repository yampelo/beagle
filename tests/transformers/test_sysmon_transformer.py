import pytest

from beagle.nodes import File, Process, Domain
from beagle.transformers.sysmon_transformer import SysmonTransformer


@pytest.fixture
def transformer() -> SysmonTransformer:
    return SysmonTransformer(None)


def test_dns_event(transformer):
    event = {
        "Provider_Name": "Microsoft-Windows-Sysmon",
        "Provider_Guid": "{5770385f-c22a-43e0-bf4c-06f5698ffbd9}",
        "Provider": None,
        "EventID_Qualifiers": "",
        "EventID": "22",
        "Version": "5",
        "Level": "4",
        "Task": "22",
        "Opcode": "0",
        "Keywords": "0x8000000000000000",
        "TimeCreated_SystemTime": "2019-08-03 14:31:49.660530",
        "TimeCreated": None,
        "EventRecordID": "295",
        "Correlation_ActivityID": "",
        "Correlation_RelatedActivityID": "",
        "Correlation": None,
        "Execution_ProcessID": "7176",
        "Execution_ThreadID": "4604",
        "Execution": None,
        "Channel": "Microsoft-Windows-Sysmon/Operational",
        "Computer": "DESKTOP-3KI19E0",
        "Security_UserID": "S-1-5-18",
        "Security": None,
        "EventData_RuleName": None,
        "EventData_UtcTime": 1564857108,
        "EventData_ProcessGuid": "{8eb9d026-9ad2-5d45-0000-0010b7760001}",
        "EventData_ProcessId": "4776",
        "EventData_QueryName": "share.microsoft.com",
        "EventData_QueryStatus": "0",
        "EventData_QueryResults": "type:  5 share.microsoft.com.edgekey.net;type:  5 e11095.dscd.akamaiedge.net;::ffff:23.32.80.227;",
        "EventData_Image": "C:\\Windows\\System32\\AppHostRegistrationVerifier.exe",
    }

    nodes = transformer.transform(event)
    assert len(nodes) == 3
    proc: Process = nodes[0]
    proc_file: File = nodes[1]
    domain: Domain = nodes[2]

    assert domain in proc.dns_query_for
    assert domain.domain == "share.microsoft.com"
    assert proc in proc_file.file_of
