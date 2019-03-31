import json
from beagle.datasources.cuckoo_report import CuckooReport


def make_tmp_file(data: dict, tmpdir):
    p = tmpdir.mkdir("cuckoo").join("data.json")
    p.write(json.dumps(data))
    return p
