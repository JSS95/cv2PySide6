from numpy.typing import NDArray
from PySide6.QtCore import Signal
from PySide6.QtMultimedia import QMediaPlayer
from typing import Protocol, Callable, Any

__all__ = [
    'ArrayProcessorProtocol',
    'VideoSeekControllerProtocol',
    'VideoPlayerProtocol',
]


class ArrayProcessorProtocol(Protocol):
    """
    Type annotation for array processor protocol.

    New image array is passed down from upstream pipeline to
    ``setArray`` slot. ``arrayChanged`` emits processed array.
    """
    setArray: Callable[['ArrayProcessorProtocol', NDArray], Any]
    arrayChanged: Signal


class VideoSeekControllerProtocol(Protocol):
    """
    Type annotation for video seeking controller protocol.

    ``setPosition`` is a ``Slot`` which controls the position
    of video. When video position changes, ``positionChanged`` signal
    emits integer value.

    When total duration of the video changes (i.e. new video is loaded),
    ``durationChanged`` signal emits integer value.
    """
    setPosition: Callable[['VideoSeekControllerProtocol', int], Any]
    positionChanged: Signal
    durationChanged: Signal


class VideoPlayerProtocol(Protocol):
    """
    Type annotation for video player protocol.

    ``play``, ``pause``, and ``stop`` are ``Slot`` to control the
    playback state of video. When playback state changes,
    ``playbackStateChanged`` signal emits new playback state as
    ``QMediaPlayer.PlaybackState`` enums.
    """
    play: Callable[['VideoPlayerProtocol'], Any]
    pause: Callable[['VideoPlayerProtocol'], Any]
    stop: Callable[['VideoPlayerProtocol'], Any]
    playbackStateChanged: Signal
    playbackState: Callable[
        ['VideoPlayerProtocol'], QMediaPlayer.PlaybackState
    ]
