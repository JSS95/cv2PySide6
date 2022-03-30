from numpy.typing import NDArray
from PySide6.QtCore import Signal
from typing import Protocol, Callable, Any

__all__ = [
    'VideoSeekerProtocol',
]


class ArrayProcessorProtocol(Protocol):
    """
    Type annotation for array processor protocol.

    New image array is passed down from upstream pipeline to
    :attr:`setArray` slot. :attr:`arrayChanged` emits processed array.
    """
    setArray: Callable[['ArrayProcessorProtocol', NDArray], Any]
    arrayChanged: Signal


class VideoSeekerProtocol(Protocol):
    """
    Type annotation for video seeker protocol.

    :attr:`setPosition` is a ``Slot`` which controls the position
    of video. When video position changes, `positionChanged` signal
    emits integer value.

    When total duration of the video changes (i.e. new video is loaded),
    `durationChanged` signal emits integer value.
    """
    setPosition: Callable[['VideoSeekerProtocol', int], Any]
    positionChanged: Signal
    durationChanged: Signal
