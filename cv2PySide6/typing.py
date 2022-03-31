from numpy.typing import NDArray
from PySide6.QtCore import Signal
from PySide6.QtMultimedia import QMediaPlayer
from typing import Protocol, Callable, Any

__all__ = [
    'ArrayProcessorProtocol',
    'VideoPlayerProtocol',
]


class ArrayProcessorProtocol(Protocol):
    """
    Type annotation for array processor protocol.

    New image array is passed down from upstream pipeline to
    ``setArray`` slot. ``arrayChanged`` emits processed array.
    """
    arrayChanged: Signal
    setArray: Callable[['ArrayProcessorProtocol', NDArray], Any]


class VideoPlayerProtocol(Protocol):
    arrayChanged: Signal
    positionChanged: Signal
    durationChanged: Signal
    playbackStateChanged: Signal
    setPosition: Callable[['VideoPlayerProtocol', int], Any]
    play: Callable[['VideoPlayerProtocol'], Any]
    pause: Callable[['VideoPlayerProtocol'], Any]
    stop: Callable[['VideoPlayerProtocol'], Any]
    playbackState: QMediaPlayer.PlaybackState
