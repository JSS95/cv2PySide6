from PySide6.QtCore import Signal
from typing import Protocol, Callable

__all__ = [
    'VideoSeekerProtocol',
]


class VideoSeekerProtocol(Protocol):
    setPosition: Callable
    positionChanged: Signal
    durationChanged: Signal
