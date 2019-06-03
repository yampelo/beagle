from beagle.constants import EventTypes, FieldNames, Protocols


def test_missing_params(client):
    resp = client.post("/api/new", data={})
    assert resp.status_code == 400


def test_non_real_datasource(client):
    resp = client.post(
        "/api/new",
        data={"datasource": "foobar", "transformer": "GenericTrasnformer", "comment": "test"},
    )
    assert resp.status_code == 400
    assert "is invalid" in resp.json["message"]


def test_misisng_params(client):
    resp = client.post(
        "/api/new",
        data={"datasource": "HXTriage", "transformer": "GenericTransformer", "comment": "test"},
    )
    assert resp.status_code == 400
    assert "Missing" in resp.json["message"]


def test_adhoc_single_event(client):
    event = {
        FieldNames.PARENT_PROCESS_IMAGE: "<PATH_SAMPLE.EXE>",
        FieldNames.PARENT_PROCESS_IMAGE_PATH: "\\",
        FieldNames.PARENT_PROCESS_ID: "3420",
        FieldNames.PARENT_COMMAND_LINE: "",
        FieldNames.PROCESS_IMAGE: "cmd.exe",
        FieldNames.PROCESS_IMAGE_PATH: "<SYSTEM32>",
        FieldNames.COMMAND_LINE: "",
        FieldNames.PROCESS_ID: "3712",
        FieldNames.TIMESTAMP: 5,
        FieldNames.EVENT_TYPE: EventTypes.PROCESS_LAUNCHED,
    }

    resp = client.post("/api/adhoc", json={"data": [event]}).json["data"]

    assert len(resp["nodes"]) > 0
    assert len(resp["links"]) > 0


def test_adhoc_array(client):
    events = [
        {
            FieldNames.PARENT_PROCESS_IMAGE: "<PATH_SAMPLE.EXE>",
            FieldNames.PARENT_PROCESS_IMAGE_PATH: "\\",
            FieldNames.PARENT_PROCESS_ID: "3420",
            FieldNames.PARENT_COMMAND_LINE: "",
            FieldNames.PROCESS_IMAGE: "cmd.exe",
            FieldNames.PROCESS_IMAGE_PATH: "<SYSTEM32>",
            FieldNames.COMMAND_LINE: "",
            FieldNames.PROCESS_ID: "3712",
            FieldNames.TIMESTAMP: 5,
            FieldNames.EVENT_TYPE: EventTypes.PROCESS_LAUNCHED,
        },
        {
            FieldNames.IP_ADDRESS: "24.151.31.150",
            FieldNames.PROTOCOL: Protocols.TCP,
            FieldNames.PORT: 465,
            FieldNames.PROCESS_IMAGE: "<PATH_SAMPLE.EXE>",
            FieldNames.PROCESS_IMAGE_PATH: "\\",
            FieldNames.PROCESS_ID: "1748",
            FieldNames.COMMAND_LINE: "",
            FieldNames.EVENT_TYPE: EventTypes.CONNECTION,
        },
    ]

    resp = client.post("/api/adhoc", json={"data": events}).json["data"]

    assert len(resp["nodes"]) > 0

    all_types = [l["type"] for l in resp["links"]]
    assert "Connected To" in all_types
