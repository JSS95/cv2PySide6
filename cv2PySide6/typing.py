from numpy.typing import NDArray
from PySide6.QtCore import Signal
from PySide6.QtMultimedia import QMediaPlayer
from typing import Protocol, Callable, Any

__all__ = [
    "ArrayProcessorProtocol",
    "NDArrayVideoPlayerProtocol",
    "CameraProtocol",
    "NDArrayMediaCaptureSessionProtocol",
]


class ArrayProcessorProtocol(Protocol):
    """
    Type annotation for array processor protocol.

    New image array is passed down from upstream pipeline to
    ``setArray`` slot. ``arrayChanged`` emits processed array.
    """

    arrayChanged: Signal
    setArray: Callable[["ArrayProcessorProtocol", NDArray], Any]


class NDArrayVideoPlayerProtocol(Protocol):
    """
    Type annotation for video player protocol which emits frames from
    video file as arrays.
    """

    arrayChanged: Signal
    positionChanged: Signal
    durationChanged: Signal
    playbackStateChanged: Signal
    setPosition: Callable[["NDArrayVideoPlayerProtocol", int], Any]
    setSource: Callable[["NDArrayVideoPlayerProtocol", Any], Any]
    play: Callable[["NDArrayVideoPlayerProtocol"], Any]
    pause: Callable[["NDArrayVideoPlayerProtocol"], Any]
    stop: Callable[["NDArrayVideoPlayerProtocol"], Any]
    playbackState: Callable[["NDArrayVideoPlayerProtocol"], QMediaPlayer.PlaybackState]


class CameraProtocol(Protocol):
    """
    Type annotation for camera protocol.
    """

    start: Callable[["CameraProtocol"], Any]
    stop: Callable[["CameraProtocol"], Any]


class NDArrayMediaCaptureSessionProtocol(Protocol):
    """
    Type annotation for media capture session protocol which emits
    frames from camera as arrays.
    """

    arrayChanged: Signal
    setCamera: Callable[["NDArrayMediaCaptureSessionProtocol", CameraProtocol], Any]
    camera: Callable[["NDArrayMediaCaptureSessionProtocol"], CameraProtocol]
