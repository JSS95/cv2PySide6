"""
General utilities
=================

"""

import cv2PySide6
import os


__all__ = [
    "get_data_path",
]


def get_data_path(*paths: str) -> str:
    """
    Get the absolute path to the directory where the sample data are stored.

    Parameters
    ==========

    paths
        Subpaths under ``cv2PySide6/data/`` directory.

    Returns
    =======

    path
        Absolute path to the sample depending on the user's system.

    Examples
    ========

    >>> from cv2PySide6 import get_data_path
    >>> get_data_path() # doctest: +SKIP
    'path/cv2PySide6/data'
    >>> get_data_path('hello.mp4') # doctest: +SKIP
    'path/cv2PySide6/data/hello.mp4'

    """
    module_path = os.path.abspath(cv2PySide6.__file__)
    module_path = os.path.split(module_path)[0]
    sample_dir = os.path.join(module_path, "data")
    sample_dir = os.path.normpath(sample_dir)
    sample_dir = os.path.normcase(sample_dir)

    path = os.path.join(sample_dir, *paths)
    return path
