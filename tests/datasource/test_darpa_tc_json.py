from beagle.datasources import DARPATCJson


def test_init():
    d = DARPATCJson("data/tc3/ta1-cadets-e3-official.json")
    assert d.file_path == "data/tc3/ta1-cadets-e3-official.json"


def test_metadata():
    d = DARPATCJson("data/tc3/ta1-cadets-e3-official.json")
    assert d.metadata() == {"filename": "ta1-cadets-e3-official.json"}
