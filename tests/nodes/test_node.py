from collections import defaultdict
from typing import List

import pytest

from beagle.nodes import Node


def testNoKeyFields():
    """A class without the key_fields annotation should raise a RuntimeError"""

    with pytest.raises(RuntimeError):

        class AnnotatedNode(Node):
            x: str
            y: int

            def __init__(self, x: str, y: int):
                self.x = x
                self.y = y

            @property
            def _display(self) -> str:
                return self.x


def testEquals():
    class AnnotatedNode(Node):

        x: str
        y: int
        key_fields: List[str] = ["x", "y"]

        def __init__(self, x: str, y: int):
            self.x = x
            self.y = y

        @property
        def _display(self) -> str:
            return self.x

    n1 = AnnotatedNode("1", 1)
    n2 = AnnotatedNode("1", 1)

    assert n1 == n2


def test_tojson():
    class AnnotatedNode(Node):
        x: str
        y: int
        key_fields: List[str] = ["x", "y"]
        foo = defaultdict(str)

        def __init__(self, x: str, y: int):
            self.x = x
            self.y = y

        @property
        def _display(self) -> str:
            return self.x

    n1 = AnnotatedNode("1", 1)
    assert n1.to_dict() == {"x": "1", "y": 1}


def testNotEquals():
    class AnnotatedNode(Node):
        x: str
        y: int
        key_fields: List[str] = ["x", "y"]

        def __init__(self, x: str, y: int):
            self.x = x
            self.y = y

        @property
        def _display(self) -> str:
            return self.x

    n1 = AnnotatedNode("1", 1)
    n2 = AnnotatedNode("1", 2)

    assert n1 != n2


def testNotEqualsTwoClasses():
    class AnnotatedNode(Node):
        x: str
        y: int
        key_fields: List[str] = ["x", "y"]

        def __init__(self, x: str, y: int):
            self.x = x
            self.y = y

        @property
        def _display(self) -> str:
            return self.x

    class OtherAnnotatedNode(Node):
        x: str
        y: int
        key_fields: List[str] = ["x", "y"]

        def __init__(self, x: str, y: int):
            self.x = x
            self.y = y

        @property
        def _display(self) -> str:
            return self.x

    n1 = AnnotatedNode("1", 1)
    n2 = OtherAnnotatedNode("1", 1)

    assert n1 != n2


def testHash():
    class AnnotatedNode(Node):
        x: str
        y: int
        key_fields: List[str] = ["x", "y"]

        def __init__(self, x: str, y: int):
            self.x = x
            self.y = y

        @property
        def _display(self) -> str:
            return self.x

    n1 = AnnotatedNode("1", 1)
    n2 = AnnotatedNode("1", 1)

    assert hash(n1) == hash(n2)

    n3 = AnnotatedNode("1", 21)
    assert hash(n1) != hash(n3)
