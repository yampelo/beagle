import json

import pytest

from beagle.datasources.fireeye_ax_report import FireEyeAXReport


@pytest.fixture
def datasource(tmpdir) -> FireEyeAXReport:
    return FireEyeAXReport(make_default_file(tmpdir))


def make_tmp_file(data: dict, tmpdir):
    p = tmpdir.mkdir("ax").join("data.json")
    p.write(json.dumps(data))
    return p


def make_default_file(tmpdir):
    p = tmpdir.mkdir("ax").join("data.json")
    p.write(json.dumps({"alert": [{"explanation": {"osChanges": [{}]}}]}))
    return p


def test_no_data(tmpdir):

    f = make_tmp_file(data={"test": "fest"}, tmpdir=tmpdir)
    FireEyeAXReport(f)


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"alert": []},
        {"alert": [{"occurred": "2018-03-31 13:40:01 +0000", "foo": []}]},
        {"alert": [{"occurred": "2018-03-31 13:40:01 +0000", "explanation": {}}]},
        {"alert": [{"occurred": "2018-03-31 13:40:01 +0000", "explanation": {"osChanges": []}}]},
    ],
)
def test_no_events(data, tmpdir):
    f = make_tmp_file(data=data, tmpdir=tmpdir)
    assert len(list(FireEyeAXReport(f).events())) == 0


def test_get_metadata(tmpdir):
    f = make_tmp_file(
        data={
            "alert": [
                {
                    "src": {},
                    "alertUrl": "https://foo",
                    "action": "notified",
                    "occurred": "2018-03-31 13:40:01 +0000",
                    "dst": {},
                    "id": 1234,
                    "name": "MALWARE_OBJECT",
                    "severity": "MAJR",
                    "product": "MAS",
                }
            ],
            "appliance": "my_appliance",
        },
        tmpdir=tmpdir,
    )

    assert FireEyeAXReport(f).metadata() == {
        "hostname": "my_appliance",
        "analyzed_on": "2018-03-31 13:40:01 +0000",
        "severity": "MAJR",
        "alert_url": "https://foo",
    }

