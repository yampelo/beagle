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


def split_reg_path(reg_path: str) -> Tuple[str, str, str]:
    """Splits a full registry path into hive, path, and key.

    Examples
    ----------

        >>> split_reg_path(\\REGISTRY\\MACHINE\\SYSTEM\\ControlSet001\\Control\\ComputerName)
        (REGISTRY, MACHINE\\SYSTEM\\ControlSet001\\Control, ComputerName)


    Parameters
    ----------
    regpath : str
        The full registry key

    Returns
    -------
    Tuple[str, str, str]
        Hive, registry key, and registry key path
    """
    # RegistryKey Node Creation
    hive = reg_path.split("\\")[0]
    reg_key_path = "\\".join(reg_path.split("\\")[1:-1])
    reg_key = reg_path.split("\\")[-1]

    return (hive, reg_key, reg_key_path)
