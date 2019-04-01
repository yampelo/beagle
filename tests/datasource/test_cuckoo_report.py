import json
from beagle.datasources.cuckoo_report import CuckooReport


def make_tmp_file(data: dict, tmpdir):
    p = tmpdir.mkdir("cuckoo").join("data.json")
    p.write(json.dumps(data))
    return p


def test_metadata(tmpdir):
    f = make_tmp_file(
        data={
            "info": {
                "added": 1553807600.200415,
                "started": 1553810186.098672,
                "duration": 325,
                "ended": 1553810511.668111,
                "owner": "",
                "score": 10.4,
                "id": 1003314,
                "category": "file",
                "git": {
                    "head": "03731c4c136532389e93239ac6c3ad38441f81a7",
                    "fetch_head": "03731c4c136532389e93239ac6c3ad38441f81a7",
                },
                "monitor": "22c39cbb35f4d916477b47453673bc50bcd0df09",
                "package": "exe",
                "route": "internet",
                "custom": "",
                "machine": {
                    "status": "stopped",
                    "name": "win7x6415",
                    "label": "win7x6415",
                    "manager": "VirtualBox",
                    "started_on": "2019-03-28 21:56:26",
                    "shutdown_on": "2019-03-28 22:01:47",
                },
                "platform": "windows",
                "version": "2.0.6",
                "options": "procmemdump=yes",
            },
            "target": {
                "category": "file",
                "file": {
                    "sha1": "8338f79279b7126791e0937d1c3933f259e5d658",
                    "name": "It6QworVAgY.exe",
                    "type": "PE32 executable (GUI) Intel 80386, for MS Windows",
                    "sha256": "c1db4b2578729a1faede84d2735eb8463bfd2c6b15d2fdf2de7a89f1954d0dfb",
                    "urls": ["http://ocsp.usertrust.com0"],
                    "crc32": "660E35BC",
                    "path": "/srv/cuckoo/cwd/storage/binaries/c1db4b2578729a1faede84d2735eb8463bfd2c6b15d2fdf2de7a89f1954d0dfb",
                    "ssdeep": "3072:RNkhoRdoQbxSTcbrh82bQZfR3pKHJL1cx0W5yOpIX:RNgo3oInbQZp5MJL1cs7",
                    "size": 206088,
                    "sha512": "8f705313d7c240e72967ac3dfc0d9e3d72090e39e51dd05e803a439a78430946945f87aa596112461aedee68a472a7880a25bb6d5e019615162fa6c35a8108b2",
                    "md5": "44b696079356579d250f716a37ca9b17",
                },
            },
        },
        tmpdir=tmpdir,
    )
    assert CuckooReport(f).metadata() == {
        "machine": "win7x6415",
        "package": "exe",
        "score": 10.4,
        "report_id": 1003314,
        "category": "file",
        "name": "It6QworVAgY.exe",
        "type": "PE32 executable (GUI) Intel 80386, for MS Windows",
    }
