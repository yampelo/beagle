from typing import Callable

import networkx
import pytest

from beagle.backends.networkx import NetworkX
from beagle.nodes import Process


@pytest.fixture()
def nx() -> Callable[..., NetworkX]:
    def _backend(*args, **kwargs) -> networkx.Graph:
        return NetworkX(*args, consolidate_edges=True, **kwargs).graph()

    return _backend


def test_one_node(nx):

    node = Process("1", "1", "1", "1", "1", "1")
    G = nx(nodes=[node])
    assert len(G.nodes()) == 1


def test_one_edge(nx):
    proc = Process(process_id=10, process_image="test.exe", command_line="test.exe /c foobar")
    other_proc = Process(process_id=12, process_image="best.exe", command_line="best.exe /c 123456")

    proc.launched[other_proc].append(timestamp=1)

    G = nx(nodes=[proc, other_proc])

    assert len(G.nodes()) == 2
    assert len(G.edges()) == 1

    u = hash(proc)
    v = hash(other_proc)

    assert networkx.has_path(G, u, v)
    assert "Launched" in G[u][v]
    assert {"timestamp": 1} == G[u][v]["Launched"]["data"][0]


def test_node_updated(nx):
    """After pushing in the first process, the second process which has the
    same hash should cause the command line attribute to update"""
    proc = Process(process_id=10, process_image="test.exe", command_line=None)
    next_proc = Process(process_id=10, process_image="test.exe", command_line="best.exe /c 123456")
    G = nx(nodes=[proc, next_proc])

    in_graph_proc = G.nodes(data=True)[hash(proc)]["data"]

    assert in_graph_proc.command_line == "best.exe /c 123456"
    assert in_graph_proc.process_id == 10
    assert in_graph_proc.process_image == "test.exe"

    # Should only have one node, since both nodes inserted are equal
    assert len(G.nodes()) == 1
