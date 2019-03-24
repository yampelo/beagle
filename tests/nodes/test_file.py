from beagle.nodes import File, Process


def testCreate():
    file_node = File(file_path="c:/windows", file_name="test.exe", extension=".exe")
    assert type(file_node) == File


def testEquals():
    file_node = File(file_path="c:/windows", file_name="test.exe", extension=".exe")

    file_node2 = File(file_path="c:/windows", file_name="test.exe", extension=".exe")

    assert file_node == file_node2
    assert hash(file_node) == hash(file_node2)


def testSetExtension():
    file_node = File(file_path="c:/windows", file_name="test.exe")

    file_node.set_extension()

    assert file_node.extension == "exe"


def testSetFilePath():
    file_node = File(file_path="c:\\windows", file_name="test.exe")

    assert file_node.full_path == "c:\\windows\\test.exe"


def testFileOf():
    file_node = File(file_path="c:/windows", file_name="test.exe", extension=".exe")
    proc = Process(process_id=0, process_image="test.exe", process_image_path="c:/windows/test.exe")

    file_node.file_of[proc]

    assert proc in file_node.file_of


def testNotFileOf():
    file_node = File(file_path="c:/windows", file_name="test.exe", extension=".exe")
    proc = Process(process_id=0, process_image="best.exe", process_image_path="c:/windows/best.exe")

    assert proc not in file_node.file_of

