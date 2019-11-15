from typing import List

import networkx as nx
import pytest

from beagle.backends.networkx import NetworkX
from beagle.nodes import File, Node, Process


@pytest.fixture
def graph_nodes_match():
    def validate_nodes_match(graph: nx.Graph, nodes: List[Node]) -> bool:
        return [n["data"] for _, n in graph.nodes(data=True)] == nodes

    return validate_nodes_match


@pytest.fixture
def G1():
    # A basic graph, with two nodes an an edge
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    other_proc = Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")

    proc.launched[other_proc].append(timestamp=1)

    backend = NetworkX(consolidate_edges=True, nodes=[proc, other_proc])

    return backend.graph()


@pytest.fixture
def G2():
    # A basic graph, with two nodes an an edge
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    f = File(file_name="foo", file_path="bar")

    proc.wrote[f].append(contents="foo")

    backend = NetworkX(consolidate_edges=True, nodes=[proc, f])

    return backend.graph()


@pytest.fixture
def G3():
    # *no consolidating*
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    f = File(file_name="foo", file_path="bar")

    proc.wrote[f].append(contents="foo")
    proc.wrote[f].append(contents="bar")

    backend = NetworkX(consolidate_edges=False, nodes=[proc, f])

    return backend.graph()


@pytest.fixture
def G4():
    # A graph with a four process tree:
    # A -> B -> C -> D
    A = Process(process_id=10, process_image="A", command_line="A")
    B = Process(process_id=12, process_image="B", command_line="B")
    C = Process(process_id=12, process_image="C", command_line="C")
    D = Process(process_id=12, process_image="D", command_line="D")

    A.launched[B]
    B.launched[C]
    C.launched[D]

    backend = NetworkX(consolidate_edges=True, nodes=[A, B, B, C])

    return backend.graph()


@pytest.fixture
def G5():
    # A graph with two, *disconnected* four process tree:
    # A -> B -> C -> D
    # E -> F -> G -> H
    A = Process(process_id=10, process_image="A", command_line="A")
    B = Process(process_id=12, process_image="B", command_line="B")
    C = Process(process_id=12, process_image="C", command_line="C")
    D = Process(process_id=12, process_image="D", command_line="D")

    E = Process(process_id=10, process_image="E", command_line="E")
    F = Process(process_id=12, process_image="F", command_line="F")
    G = Process(process_id=12, process_image="G", command_line="G")
    H = Process(process_id=12, process_image="H", command_line="H")

    A.launched[B]
    B.launched[C]
    C.launched[D]

    E.launched[F]
    F.launched[G]
    G.launched[H]

    backend = NetworkX(consolidate_edges=True, nodes=[A, B, B, C, E, F, G, H])

    return backend.graph()


@pytest.fixture
def G6():
    parent = Process(
        process_id=1, process_image_path="d:\\", process_image="parent.exe", user="omer"
    )
    child = Process(
        process_id=2, process_image_path="d:\\users", process_image="child.exe", user="omer"
    )

    parent2 = Process(
        process_id=4, process_image_path="c:\\", process_image="parent.exe", user="admin"
    )
    child2 = Process(
        process_id=3, process_image_path="c:\\users", process_image="child.exe", user="admin"
    )

    parent.launched[child].append(timestamp=12456)

    parent2.launched[child2].append(timestamp=2)

    backend = NetworkX(consolidate_edges=True, nodes=[parent, parent2, child, child2])

    return backend.graph()
