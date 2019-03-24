from __future__ import absolute_import

from typing import Tuple

from beagle.common.logging import logger  # noqa:F401


def split_path(path: str) -> Tuple[str, str]:
    """Parse a full file path into a file name + extension, and directory
    at once.
    For example::

        >>> split_path('c:\\ProgramData\\app.exe')
        (app.exe', 'c:\\ProgramData')

    By default, if it can't split, it'll return \\ as the directory, and None
    as the image.

    Parameters
    ----------
    path : str
        The path to parse

    Returns
    -------
    Tuple[str, str]
        A tuple of file name + extension, and directory at once.
    """
    image_only = path.split("\\")[-1]
    directory = "\\".join(path.split("\\")[:-1])

    if directory == "":
        directory = "\\"
    if image_only == "":
        image_only = "None"

    return image_only, directory

