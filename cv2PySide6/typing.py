from PySide6.QtCore import Signal
from typing import Protocol, Callable, Any

__all__ = [
    "CameraProtocol",
    "NDArrayMediaCaptureSessionProtocol",
]


class CameraProtocol(Protocol):
    """Type annotation for camera protocol."""

    @property
    def start(self):
        ...

    @property
    def stop(self):
        ...


class NDArrayMediaCaptureSessionProtocol(Protocol):
    """
    Type annotation for media capture session protocol which emits
    frames from camera as arrays.
    """

    arrayChanged: Signal
    setCamera: Callable[["NDArrayMediaCaptureSessionProtocol", CameraProtocol], Any]
    camera: Callable[["NDArrayMediaCaptureSessionProtocol"], CameraProtocol]
