import pytest

from beagle.constants import EventTypes, FieldNames, Protocols
from beagle.web.api.models import Graph
from beagle.web.api.views import _validate_params


def test_no_params(client):
    resp = client.post("/api/new", data={})
    assert resp.status_code == 400


def test_non_real_datasource(client):
    resp = client.post(
        "/api/new",
        data={"datasource": "foobar", "transformer": "GenericTrasnformer", "comment": "test"},
    )
    assert resp.status_code == 400
    assert "is invalid" in resp.json["message"]


def test_missing_params(client):
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


def test_adhoc_invalid_cim_format(client):
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

    resp = client.post("/api/adhoc", json={"data": [event], "cim": "test"}).json["message"]
    assert "cim_format must be in" in resp


def test_events_forced_to_be_list(client):
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

    resp = client.post("/api/adhoc", json={"data": event}).json["data"]

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
    assert Protocols.TCP in all_types


def test_get_graph_metadata(session, client):
    g = Graph(
        sha256="1234",
        meta={"foo": "bar"},
        category="test_cat",
        comment="foo",
        file_path="foo_Bar_/",
    )
    session.add(g)
    session.commit()

    resp = client.get(f"/api/metadata/{g.id}").json
    assert resp == {"foo": "bar"}


def test_get_graph_metadata_graph_not_found(session, client):
    g = Graph(
        sha256="1234",
        meta={"foo": "bar"},
        category="test_cat",
        comment="foo",
        file_path="foo_Bar_/",
    )
    session.add(g)
    session.commit()

    resp = client.get(f"/api/metadata/{g.id + 2}")
    assert resp.status_code == 404
    assert resp.json["message"] == "Graph not found"


def test_get_categories_only_uploaded(session, client):
    """Should only return the fireeye_hx category"""
    g = Graph(
        sha256="1234",
        meta={"foo": "bar"},
        category="fireeye_hx",
        comment="foo",
        file_path="foo_Bar_/",
    )
    session.add(g)
    session.commit()

    resp = client.get(f"/api/categories?uploaded=true")
    assert resp.json[0]["id"] == "fireeye_hx"
    assert len(resp.json) == 1


@pytest.mark.parametrize(
    "form_input,file_input,success",
    [
        # Missing one of datasource/comment/transformer
        ({"datasource": "HXTriage", "comment": "hello"}, {}, False),
        ({"datasource": "HXTriage", "transformer": "FireEyeHXTransformer"}, {}, False),
        ({"transformer": "HXTriage", "comment": "hello"}, {}, False),
        # No triage parameter
        (
            {"transformer": "FireEyeHXTransformer", "datasource": "HXTriage", "comment": "hello"},
            {},
            False,
        ),
        # Triage should be in files, not form
        (
            {
                "transformer": "FireEyeHXTransformer",
                "datasource": "HXTriage",
                "comment": "hello",
                "triage": "foo",
            },
            {},
            False,
        ),
        # Fake datasource
        (
            {"transformer": "FireEyeHXTransformer", "datasource": "Boop", "comment": "hello"},
            {},
            False,
        ),
        # should work
        (
            {"datasource": "HXTriage", "transformer": "FireEyeHXTransformer", "comment": "hello"},
            {"triage": {"name": "1234"}},
            True,
        ),
        (
            # Latest won't be required.
            {
                "datasource": "SplunkSPLSearch",
                "transformer": "GenericTransformer",
                "comment": "hello",
                "spl": "1234",
            },
            {},
            True,
        ),
        (
            # External datasource, required params not in form.
            {
                "datasource": "SplunkSPLSearch",
                "transformer": "GenericTransformer",
                "comment": "hello",
            },
            {},
            False,
        ),
    ],
)
def test_validate_params(form_input, file_input, success):
    resp, res = _validate_params(form_input, file_input)
    assert res == success, resp
