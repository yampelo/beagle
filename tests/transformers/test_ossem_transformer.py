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
