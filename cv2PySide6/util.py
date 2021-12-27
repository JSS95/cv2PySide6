import cv2PySide6
import os


__all__ = [
    "get_samples_path",
]


def get_samples_path(*paths: str) -> str:
    r"""
    Get the absolute path to the directory where the sample data are
    stored.

    Parameters
    ==========

    paths
        Subpaths under ``cv2PySide6/samples/`` directory.

    Returns
    =======

    path
        Absolute path to the sample depending on the user's system.

    Examples
    ========

    >>> from cv2PySide6 import get_samples_path
    >>> get_samples_path() # doctest: +SKIP
    'path/cv2PySide6/samples'
    >>> get_samples_path("hello.mp4") # doctest: +SKIP
    'path/cv2PySide6/samples/hello.mp4'

    """
    module_path = os.path.abspath(cv2PySide6.__file__)
    module_path = os.path.split(module_path)[0]
    sample_dir = os.path.join(module_path, "samples")
    sample_dir = os.path.normpath(sample_dir)
    sample_dir = os.path.normcase(sample_dir)

    path = os.path.join(sample_dir, *paths)
    return path
