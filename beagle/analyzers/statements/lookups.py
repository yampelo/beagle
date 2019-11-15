import re
from typing import Pattern, Union, cast
from abc import ABCMeta, abstractmethod
import functools


def not_null(f):
    @functools.wraps(f)
    def wrapper(prop, *args, **kwargs):
        if prop is None:
            return False
        else:
            return f(prop, *args, **kwargs)

    return wrapper


class FieldLookup(object, metaclass=ABCMeta):
    def __init__(self, value):
        self.value = value

    @abstractmethod
    def test(self, prop) -> bool:
        pass


class Contains(FieldLookup):
    """Case sensitve contains"""

    @not_null
    def test(self, prop: str):
        return self.value in prop


class IContains(FieldLookup):
    """Case insensitve Contains"""

    @not_null
    def test(self, prop: str):
        return str(self.value).lower() in str(prop).lower()


class Exact(FieldLookup):
    """Exact match"""

    @not_null
    def test(self, prop: str):
        return self.value == prop


class IExact(FieldLookup):
    """Insensitive Exact match"""

    @not_null
    def test(self, prop: str):
        return str(self.value).lower() == str(prop).lower()


class StartsWith(FieldLookup):
    """Property begins with"""

    @not_null
    def test(self, prop: str):
        return prop.startswith(self.value)


class EndsWith(FieldLookup):
    """Property begins endswith"""

    @not_null
    def test(self, prop: str):
        return prop.endswith(self.value)


class Regex(FieldLookup):
    def __init__(self, value: Union[str, Pattern]):
        if isinstance(value, str):
            self.value: Pattern = re.compile(value)
        else:
            self.value = value

    @not_null
    def test(self, prop: str):
        return self.value.search(prop) is not None
